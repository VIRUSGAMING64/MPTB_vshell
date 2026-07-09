import os
import psutil
import shutil
import mimetypes
from flask import Flask, request, redirect, url_for, send_file, send_from_directory, jsonify, make_response, session, flash, render_template, Response, stream_with_context
from modules.compress.video import *
from modules.utils.videospliter import VideoSplitter
from functools import wraps
from pathlib import Path

app = Flask(import_name=__name__, static_folder='static', template_folder='templates')
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'env'
app.config['UPLOAD_FOLDER'] = os.path.realpath(UPLOAD_FOLDER)
TOTAL = 0
PART  = 0
OK    = True


@app.route('/libs/<path:filename>')
def serve_lib(filename):
    return send_from_directory(os.path.join(app.root_path, 'libs'), filename)

GLOBAL_BASE_DIR = app.config['UPLOAD_FOLDER']
os.makedirs(GLOBAL_BASE_DIR, exist_ok=True)

VIDEO_EXTENSIONS = {
    '.mp4', '.mkv', '.avi', '.mpg', '.mpeg', '.mov', '.webm', '.m4v', '.flv', '.wmv', '.ts', '.m2ts'
}

X265_MAX_INPUT_SIZE_MB = int(os.getenv('X265_MAX_INPUT_SIZE_MB', '250'))
SPLIT_SIZE_MB = int(os.getenv('SPLIT_SIZE_MB', '200'))

# --- Queue System ---
import threading
import time

class QueueManager:
    def __init__(self):
        self.queue = [] # List of dicts: {'path': str, 'callback': func}
        self.current_task = None
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()

    def add_task(self, file_path, callback):
        with self.lock:
            if any(item['path'] == file_path for item in self.queue):
                return False, "Ya está en la cola"
            if self.current_task and self.current_task['path'] == file_path:
                return False, "Ya se está procesando"
            
            self.queue.append({'path': file_path, 'callback': callback})
            return True, "Añadido a la cola"

    def get_status(self):
        with self.lock:
            return {
                'queue': [os.path.basename(item['path']) for item in self.queue],
                'current': os.path.basename(self.current_task['path']) if self.current_task else None,
                'is_processing': self.current_task is not None
            }

    def _worker(self):
        global OK, TOTAL, PART
        while not self.stop_event.is_set():
            task = None
            with self.lock:
                if self.queue and not self.current_task:
                    task = self.queue.pop(0)
                    self.current_task = task
            
            if task:
                TOTAL = 0
                PART = 0
                
                path = task['path']
                callback = task['callback']
                print(f"Queue Worker: Starting {path}")
                try:
                    comp = VideoCompressor(path, callback, parse_end=True)
                    comp.compress()
                except Exception as e:
                    print(f"Queue Worker Error processing {path}: {e}")
                finally:
                    with self.lock:
                        self.current_task = None
            else:
                time.sleep(1)

queue_manager = QueueManager()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_base_dir():
    if 'folder' in session:
         return os.path.join(GLOBAL_BASE_DIR, session['folder'])
    return GLOBAL_BASE_DIR 

def get_safe_path(req_path):
    base_dir = get_base_dir()
    if not req_path:
        req_path = ''
    # Eliminar barras iniciales para evitar que se interprete como root absoluto
    req_path = req_path.lstrip('/')
    abs_path = os.path.abspath(os.path.join(base_dir, req_path))
    if not abs_path.startswith(base_dir):
        return base_dir, ''
    return abs_path, req_path


def parse_byte_range(range_header, file_size):
    if not range_header:
        return None

    raw_value = range_header.strip()
    if '=' in raw_value:
        unit, raw_value = raw_value.split('=', 1)
        if unit.strip().lower() != 'bytes':
            return None

    if '-' not in raw_value:
        return None

    start_text, end_text = raw_value.split('-', 1)

    try:
        if start_text == '':
            suffix_length = int(end_text)
            if suffix_length <= 0:
                return None
            start = max(file_size - suffix_length, 0)
            end = file_size - 1
        else:
            start = int(start_text)
            end = int(end_text) if end_text else file_size - 1
    except ValueError:
        return None

    if start < 0 or end < start or start >= file_size:
        return None

    return start, min(end, file_size - 1)


def is_video_file(filename):
    _, ext = os.path.splitext(filename.lower())
    return ext in VIDEO_EXTENSIONS


def should_show_x265(filename, abs_path=None):
    lowered_name = filename.lower()

    if '.comp' in lowered_name:
        return False, 'compressed'

    if not is_video_file(filename):
        return False, 'non_video'

    if abs_path and os.path.exists(abs_path):
        size_limit_bytes = X265_MAX_INPUT_SIZE_MB * 1024 * 1024
        if os.path.getsize(abs_path) > size_limit_bytes:
            return False, 'too_large'

    return True, 'ok'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        folder_name = f"{username}-{password}"
        user_folder = os.path.join(GLOBAL_BASE_DIR, folder_name)
        
        if os.path.exists(user_folder):
             session['user'] = username
             session['folder'] = folder_name
             return redirect(url_for('index'))
        else:
             flash('Cuenta no creada aun en el bot')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('folder', None) 
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html', username=session.get('user'), folder=session.get('folder'))

@app.route('/api/list')
@login_required
def list_files():
    req_path = request.args.get('path', '')
    abs_path, rel_path = get_safe_path(req_path)
    
    if not os.path.exists(abs_path):
        return jsonify({'error': 'Path does not exist', 'files': [], 'folders': [], 'current_path': ''}), 404

    files = []
    folders = []
    
    try:
        for item in os.listdir(abs_path):
            item_path = os.path.join(abs_path, item)
            if os.path.isdir(item_path):
                folders.append(item)
            else:
                can_x265, x265_reason = should_show_x265(item, item_path)
                files.append({
                    'name': item,
                    'size': os.path.getsize(item_path) if os.path.exists(item_path) else None,
                    'is_video': is_video_file(item),
                    'has_comp_suffix': '.comp' in item.lower(),
                    'can_x265': can_x265,
                    'x265_reason': x265_reason,
                })
    except PermissionError:
        return jsonify({'error': 'Permission denied', 'files': [], 'folders': [], 'current_path': rel_path}), 403

    folders.sort()
    files.sort(key=lambda x: x['name'])
    
    return jsonify({
        'files': files,
        'folders': folders,
        'current_path': rel_path,
        'x265_max_input_size_mb': X265_MAX_INPUT_SIZE_MB,
    })

@app.route('/create_folder', methods=['POST'])
@login_required
def create_folder():
    current_path = request.form.get('current_path', '')
    folder_name = request.form.get('folder_name')
    
    if folder_name:
        abs_path, _ = get_safe_path(os.path.join(current_path, folder_name))
        try:
            os.makedirs(abs_path, exist_ok=True)
            return jsonify({'success': True, 'message': f'Carpeta {folder_name} creada'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error al crear carpeta: {str(e)}'}), 500
            
    return jsonify({'success': False, 'message': 'Nombre de carpeta requerido'}), 400

@login_required
@app.route('/delete', methods=['POST'])
def delete_item():
    current_path = request.form.get('current_path', '')
    item_name = request.form.get('item_name')
    item_type = request.form.get('item_type') # 'file' or 'folder'
    
    if item_name:
        abs_path, _ = get_safe_path(os.path.join(current_path, item_name))
        try:
            if item_type == 'folder':
                shutil.rmtree(abs_path)
                return jsonify({'success': True, 'message': f'Carpeta {item_name} eliminada'})
            else:
                os.remove(abs_path)
                return jsonify({'success': True, 'message': f'Archivo {item_name} eliminado'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error al eliminar: {str(e)}'}), 500
    return jsonify({'success': False, 'message': 'Nombre de item requerido'}), 400


@login_required
@app.route('/upload', methods=['POST'])
def upload_file():
    current_path = request.form.get('current_path', '')
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'}), 400
    
    if file:
        filename = file.filename
        abs_path, _ = get_safe_path(current_path)
        try:
            file.save(os.path.join(abs_path, filename))
            return jsonify({'success': True, 'message': f'Archivo {filename} subido'})

        except Exception as e:
            return jsonify({'success': False, 'message': f'Error al subir: {str(e)}'}), 500
        
    return jsonify({'success': False, 'message': 'Error desconocido'}), 500

@app.route('/download/<path:file_path>')
def download_file_direct(file_path):
    """Descarga un archivo sin requerir sesión.
    El file_path debe tener formato: userfolder/path/to/file
    Protección contra path traversal incluida.
    """
    base_path = Path(GLOBAL_BASE_DIR).resolve()
    abs_path = (base_path / file_path).resolve()
    
    # Protección contra path traversal: verificar que el path resuelto está dentro de GLOBAL_BASE_DIR
    try:
        abs_path.relative_to(base_path)
    except ValueError:
        return make_response("Invalid path", 403)

    if not abs_path.is_file():
        return make_response("File not found", 404)

    file_size = abs_path.stat().st_size
    range_header = request.headers.get('Range') or request.headers.get('range')
    byte_range = parse_byte_range(range_header, file_size)

    if range_header and byte_range is None:
        response = make_response('', 416)
        response.headers['Content-Range'] = f'bytes */{file_size}'
        response.headers['Accept-Ranges'] = 'bytes'
        return response

    content_type = mimetypes.guess_type(str(abs_path))[0] or 'application/octet-stream'
    download_name = abs_path.name

    if byte_range is None:
        response = send_file(str(abs_path), as_attachment=True, conditional=True, download_name=download_name)
        response.headers['Accept-Ranges'] = 'bytes'
        return response

    start, end = byte_range
    length = end - start + 1

    def file_iterator():
        with open(abs_path, 'rb') as file_handle:
            file_handle.seek(start)
            remaining = length
            while remaining > 0:
                chunk = file_handle.read(min(64 * 1024, remaining))
                if not chunk:
                    break
                remaining -= len(chunk)
                yield chunk

    response = Response(
        stream_with_context(file_iterator()),
        status=206,
        mimetype=content_type,
        direct_passthrough=True,
    )
    response.headers['Content-Length'] = str(length)
    response.headers['Content-Range'] = f'bytes {start}-{end}/{file_size}'
    response.headers['Accept-Ranges'] = 'bytes'
    response.headers['Content-Disposition'] = f'attachment; filename="{download_name}"'
    return response

def update_stat(total,part,ok):
    global TOTAL,PART,OK
    TOTAL = total
    PART = part
    OK = ok

@login_required
@app.route("/combstats",methods = ["GET"])
def combstats():
    global TOTAL,PART,OK
    if TOTAL == 0:
        TOTAL = 1
    
    status = queue_manager.get_status()
    # OK variable means "Is IDLE/Finished". So it is opposite of is_processing
    is_idle = not status['is_processing']

    return {
        "combertion":{
            "total":TOTAL,
            "part": PART,
            "percent": PART/TOTAL * 100,
            "ok": is_idle,
            "queue": status['queue'],
            "current": status['current']
        }
    }
@login_required

@app.route("/combert",methods = ['POST'])
def combert():
    
    current_path = request.form.get('current_path', '')
    item_name    = request.form.get('item_name')
    item_type    = request.form.get('item_type') # 'file' or 'folder'

    # Normalize path
    try:
        infile, _ = get_safe_path(os.path.join(current_path, item_name))
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error de ruta: {str(e)}'}), 400

    if not os.path.isfile(infile):
        return jsonify({'success': False, 'message': 'Archivo no encontrado'}), 404

    # Primero: comprobar si es video y no tiene sufijo .comp
    if '.comp' in item_name.lower():
        return jsonify({'success': False, 'message': 'Este archivo ya fue comprimido y no se puede volver a comprimir con x265 desde la web'}), 400

    if not is_video_file(item_name):
        return jsonify({'success': False, 'message': 'x265 solo está disponible para archivos de video'}), 400

    # Si el archivo supera el umbral de splitting, lanzamos un hilo para partirlo
    file_size = os.path.getsize(infile)
    if file_size > SPLIT_SIZE_MB * 1024 * 1024:
        def split_and_enqueue():
            try:
                vs = VideoSplitter(max_threads=2)
                parts = vs.split(infile, size=SPLIT_SIZE_MB, delete_original=True, verify=True)
            except Exception as e:
                print(f"Split error for {infile}: {e}")
                return

            added_count = 0
            for p in parts:
                ok, msg = queue_manager.add_task(p, update_stat)
                if ok:
                    added_count += 1

            print(f"Auto-split: {len(parts)} partes creadas, {added_count} añadidas a la cola")

        threading.Thread(target=split_and_enqueue, daemon=True).start()

        return jsonify({'success': True, 'message': f'Se inició el split en partes de {SPLIT_SIZE_MB} MB y se añadirán a la cola automáticamente.'})

    # Si no hace falta partir, aplicamos las comprobaciones normales y encolamos el archivo
    can_x265, x265_reason = should_show_x265(item_name, infile)
    if not can_x265:
        messages = {
            'compressed': 'Este archivo ya fue comprimido y no se puede volver a comprimir con x265 desde la web',
            'non_video': 'x265 solo está disponible para archivos de video',
            'too_large': f'Este archivo supera el límite seguro de {X265_MAX_INPUT_SIZE_MB} MB para x265 en este entorno',
        }
        return jsonify({'success': False, 'message': messages.get(x265_reason, 'No se puede comprimir este archivo con x265')}), 400

    # infile is absolute path
    added, msg = queue_manager.add_task(infile, update_stat)
    if added:
        return jsonify({'success': True, 'message': msg})
    else:
        return jsonify({'success': False, 'message': msg}), 400

@login_required

@app.route('/api/ffmpeg-status')
def ffmpeg_status():
    ffmpeg_running = False
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and 'ffmpeg' in proc.info['name'].lower():
                ffmpeg_running = True
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
        
    return jsonify({'running': ffmpeg_running})


try:
    app.run(host='0.0.0.0', port=80)
except:
    app.run(host='0.0.0.0', port=5000)
