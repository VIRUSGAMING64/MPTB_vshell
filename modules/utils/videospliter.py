import os
import shutil
import subprocess
import math
from pathlib import Path
from typing import List, Optional, Union


class VideoSplitter:
    """
    Divide y une archivos de video grandes con mínimo consumo de RAM.
    
    Características v2:
      - split() recibe tamaño en MB
      - Verificación de integridad de cada parte con ffprobe (sin decodificar)
      - Auto-eliminación del archivo original solo si todas las partes pasan
        la verificación
    """

    MB = 1024 ** 2
    GB = 1024 ** 3

    def __init__(
        self,
        ffmpeg_path: str = "ffmpeg",
        ffprobe_path: str = "ffprobe",
        max_threads: Optional[int] = os.cpu_count(),
        temp_dir: Optional[str] = None,
    ):
        """
        Args:
            ffmpeg_path:  ruta al binario de ffmpeg
            ffprobe_path: ruta al binario de ffprobe
            max_threads: hilos de CPU (2 = bajo consumo, None = automático)
            temp_dir:    carpeta para las partes (None = junto al original)
        """
        self.ffmpeg = ffmpeg_path
        self.ffprobe = ffprobe_path
        self.max_threads = max_threads
        self.temp_dir = temp_dir
        self._check_dependencies()

    # ============================================================
    #  Utilidades internas
    # ============================================================
    def _check_dependencies(self):
        for tool in (self.ffmpeg, self.ffprobe):
            if shutil.which(tool) is None and not os.path.isfile(tool):
                raise FileNotFoundError(
                    f"No se encontró '{tool}'. Instala FFmpeg o pasa la ruta completa."
                )

    def _run(self, cmd: List[str]) -> subprocess.CompletedProcess:
        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Error ejecutando {' '.join(cmd[:3])}...\n\n{result.stderr}"
            )
        return result

    def _probe(self, file: str) -> dict:
        """Lee metadatos del video (rápido, sin decodificar, ~MB de RAM)."""
        cmd = [
            self.ffprobe, "-v", "error",
            "-show_entries", "format=duration,size,bit_rate",
            "-show_entries", "stream=index,codec_type,codec_name",
            "-of", "json", file,
        ]
        import json
        return json.loads(self._run(cmd).stdout)

    def _check_disk_space(self, file: str, required_bytes: int):
        target_dir = os.path.dirname(os.path.abspath(file)) or "."
        free = shutil.disk_usage(target_dir).free
        if free < required_bytes:
            raise IOError(
                f"Espacio insuficiente: {free/1e9:.2f} GB libres, "
                f"se necesitan ~{required_bytes/1e9:.2f} GB."
            )

    def _format_mb(self, n: float) -> str:
        return f"{n/self.MB:.2f} MB"

    # ============================================================
    #  Verificación de integridad (low RAM)
    # ============================================================
    def _verify_part(self, part: str, original_info: dict) -> tuple[bool, str]:
        """
        Verifica UNA parte sin decodificar el video.
        - Existe y tamaño > 0
        - ffprobe la puede leer
        - Codecs de video/audio coinciden con el original
        - Duración > 0

        Returns:
            (ok: bool, mensaje: str)
        """
        p = Path(part)
        if not p.is_file():
            return False, "no existe"

        size = p.stat().st_size
        if size == 0:
            return False, "archivo vacío (0 bytes)"

        if size < 1024:  # <1 KB → claramente corrupto
            return False, f"tamaño sospechosamente pequeño: {size} bytes"

        try:
            info = self._probe(part)
        except Exception as e:
            return False, f"ffprobe no pudo leerla: {e}"

        # Verificar duración
        try:
            dur = float(info["format"]["duration"])
        except (KeyError, ValueError):
            return False, "sin duración legible"

        if dur <= 0:
            return False, f"duración inválida: {dur}"

        # Verificar que los codecs coincidan con el original
        orig_streams = {s["codec_type"]: s["codec_name"]
                        for s in original_info.get("streams", [])}
        part_streams = {s["codec_type"]: s["codec_name"]
                        for s in info.get("streams", [])}

        for ctype, cname in orig_streams.items():
            if ctype not in part_streams:
                return False, f"falta stream de {ctype}"
            if part_streams[ctype] != cname:
                return False, (
                    f"codec de {ctype} no coincide: "
                    f"original={cname}, parte={part_streams[ctype]}"
                )

        return True, f"OK ({self._format_mb(size)}, {dur:.2f}s)"

    def _verify_all_parts(
        self, parts: List[str], original_info: dict, original_file: str, expected_durations: Optional[List[float]] = None
    ) -> None:
        """
        Verifica TODAS las partes. Si alguna falla, lanza excepción
        con el detalle (y NO borra el original).
        """
        print(f"[verify] Verificando {len(parts)} partes con ffprobe (low RAM)…")
        failures: List[str] = []

        # Calculamos duración total esperada
        orig_dur = float(original_info["format"]["duration"])

        sum_dur = 0.0
        for i, part in enumerate(parts, 1):
            ok, msg = self._verify_part(part, original_info)
            status = "✓" if ok else "✗"
            print(f"  {status} [{i}/{len(parts)}] {Path(part).name}: {msg}")
            if not ok:
                failures.append(f"{Path(part).name}: {msg}")
                continue

            # Acumulamos duración real para sanity check final
            part_info = self._probe(part)
            sum_dur += float(part_info["format"]["duration"])

        # Comparar con las duraciones esperadas si se proporcionaron
        if expected_durations is not None:
            expected_sum = sum(expected_durations)
            # Aquí expected_sum debería ser exactamente orig_dur por construcción
            if abs(expected_sum - orig_dur) > 1e-3:
                failures.append(
                    f"suma de duraciones esperadas {expected_sum:.3f}s != original {orig_dur:.3f}s"
                )

        # Tolerancia sobre la suma real reportada por ffprobe: aceptamos pequeños desfases
        # debido a contenedores y keyframes. Tolerancia = max(0.5s, 0.1s por parte)
        tolerance = max(0.5, len(parts) * 0.1)
        if abs(sum_dur - orig_dur) > tolerance:
            failures.append(
                f"duración total reportada {sum_dur:.2f}s != original {orig_dur:.2f}s "
                f"(tolerancia {tolerance}s)"
            )

        if failures:
            raise RuntimeError(
                "❌ Verificación FALLÓ. NO se borró el original.\n"
                "Errores:\n  - " + "\n  - ".join(failures)
            )

        print(f"[verify] ✓ Todas las partes OK "
              f"({sum_dur:.2f}s ≈ {orig_dur:.2f}s original)")

    # ============================================================
    #  API pública: split
    # ============================================================
    def split(
        self,
        file: str,
        size: Union[int, float],
        delete_original: bool = True,
        verify: bool = True,
    ) -> List[str]:
        """
        Divide 'file' en partes de ~'size' MB usando stream copy (mínima RAM).

        Args:
            file:            ruta al video de entrada
            size:            tamaño objetivo por parte, en **MB**
            delete_original: si True (default), borra el original tras verificar
            verify:          si True (default), verifica integridad de cada parte
                             antes de borrar el original

        Returns:
            Lista con las rutas de los videos generados (en orden).

        Raises:
            RuntimeError: si la verificación falla (no se borra el original).
        """
        size = float(size)
        if size <= 0:
            raise ValueError("El tamaño debe ser mayor a 0 MB.")

        path = Path(file)
        if not path.is_file():
            raise FileNotFoundError(f"No existe el archivo: {file}")

        info = self._probe(file)
        duration = float(info["format"]["duration"])
        total_bytes = int(info["format"]["size"])
        total_mb = total_bytes / self.MB

        if total_mb <= size:
            print(f"[split] El video ({total_mb:.2f} MB) ya es menor al objetivo. Nada que hacer.")
            return [str(path)]

        # Verificamos espacio: lectura 1× + escritura 1× para stream copy
        self._check_disk_space(file, int(total_bytes * 2.1))

        # Calculamos número de partes objetivo según tamaño (MB)
        n_parts = int(math.ceil(total_mb / size))
        if n_parts < 1:
            n_parts = 1

        # Distribuimos la duración original entre las n_parts de forma que la suma
        # exacta de las duraciones pedidas sea igual a la duración original.
        seconds_per_part = duration / n_parts

        out_dir = Path(self.temp_dir) if self.temp_dir else path.parent
        out_dir.mkdir(parents=True, exist_ok=True)

        print(
            f"[split] {path.name}: {total_mb:.2f} MB / {duration:.0f}s "
            f"→ {n_parts} partes de ~{size} MB ({seconds_per_part:.0f}s c/u)"
        )
        print(f"[split] RAM estimada: <100 MB | Hilos: {self.max_threads or 'auto'}")

        parts: List[str] = []
        threads_arg = ["-threads", str(self.max_threads)] if self.max_threads else []
        expected_durations: List[float] = []

        for i in range(n_parts):
            start = i * seconds_per_part
            # última parte toma el resto para evitar pérdidas por redondeo
            if i == n_parts - 1:
                part_dur = duration - start
            else:
                part_dur = seconds_per_part

            # Guardar la duración esperada para verificación exacta
            expected_durations.append(part_dur)

            out_file = out_dir / f"{path.stem}_part{i+1:03d}.mp4"

            # Usar -ss después de -i para seek preciso (más fiable en duración)
            cmd = [self.ffmpeg, "-y", "-hide_banner", "-loglevel", "error"]
            cmd += threads_arg
            cmd += ["-i", str(path)]
            if start > 0:
                cmd += ["-ss", f"{start:.6f}"]
            cmd += ["-t", f"{part_dur:.6f}"]
            cmd += ["-c", "copy", "-avoid_negative_ts", "make_zero", str(out_file)]

            self._run(cmd)
            parts.append(str(out_file))
            out_size = out_file.stat().st_size / self.MB
            print(f"  ✓ Parte {i+1}/{n_parts}: {out_file.name} ({out_size:.2f} MB)")

        # -------- Verificación + borrado --------
        if verify:
            self._verify_all_parts(parts, info, file, expected_durations=expected_durations)
        else:
            print("[verify] ⚠ Verificación omitida por el usuario.")

        if delete_original:
            size_orig = path.stat().st_size
            path.unlink()
            print(f"[delete] 🗑 Original borrado: {file} ({size_orig/self.MB:.2f} MB)")
        else:
            print(f"[delete] Original conservado (delete_original=False): {file}")

        return parts

    # ============================================================
    #  API pública: join
    # ============================================================
    def join(self, files: List[str], output: Optional[str] = None) -> str:
        """
        Une varios videos en uno solo usando concat demuxer (sin re-codificar).

        Args:
            files:  lista de rutas a videos (en orden)
            output: ruta de salida (None = auto-generada)

        Returns:
            Ruta del video resultante.

        Requisito:
            Todos los videos deben tener el mismo códec/resolución/fps.
        """
        if not files:
            raise ValueError("La lista de archivos está vacía.")
        for f in files:
            if not os.path.isfile(f):
                raise FileNotFoundError(f"No existe: {f}")

        if output is None:
            first = Path(files[0])
            base = first.stem.split("_part")[0]
            output = str(first.parent / f"joined_{base}.mp4")

        list_file = Path(output).with_suffix(".list.txt")
        with open(list_file, "w", encoding="utf-8") as fp:
            for f in files:
                safe = f.replace("'", "'\\''")
                fp.write(f"file '{safe}'\n")

        total_in = sum(os.path.getsize(f) for f in files)
        self._check_disk_space(files[0], int(total_in * 1.1))

        threads_arg = ["-threads", str(self.max_threads)] if self.max_threads else []
        cmd = [
            self.ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
            "-fflags", "+genpts",
        ]
        cmd += threads_arg
        cmd += ["-f", "concat", "-safe", "0", "-i", str(list_file),
                "-c", "copy", output]

        print(f"[join] {len(files)} partes → {output} (RAM <100 MB)")
        self._run(cmd)
        list_file.unlink(missing_ok=True)

        out_size = os.path.getsize(output) / self.MB
        print(f"  ✓ Resultado: {output} ({out_size:.2f} MB)")
        return output


# ---------- ejemplo de uso ----------
if __name__ == "__main__":
    vs = VideoSplitter(max_threads=2)               # bajo consumo
    partes = vs.split("mi_video.mp4", size=500)    # partes de 500 MB
    # auto-verifica y, si todo OK, borra mi_video.mp4
    final  = vs.join(partes)
    print(f"\n🎬 Video final: {final}")
