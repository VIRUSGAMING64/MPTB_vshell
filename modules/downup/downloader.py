from threading import Thread
import os
import requests as rq

class downloader:
    def __init__(self,progress =  None,args = [],threads = 2):
        self.threads = threads
        if progress == None:
            progress = self.__call
        self.call = progress
        self.args = args

    def __call(self):
        pass

    def getdata(self,url,l,r) -> bytes:
        data = b""
        headers = {"Range":f"bytes={l}-{r}"}
        resp = rq.get(url,headers=headers,stream=True)
        for chunk in resp.iter_content(chunk_size=8192):    
            data += chunk

        return data
    

    def add(self,data,file,mode = "ab"):
        try:
            file2 = open(file,mode)
            file2.write(data)
            file2.close()
        except Exception as e:
            print(f"error writing file [{e}]")

    def _download(self,url, l, r, filename, single = False):
        headers = {"Range": f"bytes={l}-{r}"}
        try:
            resp = rq.get(url, headers=headers, stream=True)
            resp.raise_for_status()
            written = 0
            with open(filename, "r+b") as f:
                f.seek(l)
                for chunk in resp.iter_content(chunk_size=1024*64):
                    if not chunk:
                        continue
                    f.write(chunk)
                    written += len(chunk)
                    if single:
                        self.call(min(l + written, r + 1), r + 1, *self.args)
        except Exception as e:
            print(f"download chunk error [{e}]")


    def getlenght(self,url) -> int:
        heads = rq.head(url).headers
        length = heads.get("Content-Length")
        if length is None:
            length = rq.get(url, stream=True).headers.get("Content-Length", 0)
        return int(length)


    def getname(self,url) -> str:
        if not "/" in url:
            return "unnamed.file" 
        url = url.rsplit("/",1)[1]
        return url


    def multithread(self,url, total_len, filename) -> bool:
        accept_ranges = rq.get(url, stream=True).headers.get("accept-ranges", "").lower()
        if accept_ranges != "bytes":
            return False
        # Asegurar carpeta y archivo del tamaño correcto
        dirn = os.path.dirname(filename)
        if dirn:
            os.makedirs(dirn, exist_ok=True)
        with open(filename, "wb") as f:
            f.truncate(total_len)
        # Calcular rangos uniformes y lanzar hilos
        threads = []
        threads_count = max(1, int(self.threads))
        for i in range(threads_count):
            start = (total_len * i) // threads_count
            end = (total_len * (i + 1)) // threads_count - 1
            if start > end:
                continue
            th = Thread(target=self._download, args=(url, start, end, filename, False))
            th.start()
            threads.append(th)
        for th in threads:
            th.join()
        return True
    

    def _download_single(self, url: str, total_len: int, filename: str):
        try:
            dirn = os.path.dirname(filename)
            if dirn:
                os.makedirs(dirn, exist_ok=True)
            with open(filename, "wb") as f:
                with rq.get(url, stream=True) as resp:
                    resp.raise_for_status()
                    downloaded = 0
                    for chunk in resp.iter_content(chunk_size=1024*64):
                        if not chunk:
                            continue
                        f.write(chunk)
                        downloaded += len(chunk)
                        self.call(downloaded, total_len, *self.args)
        except Exception as e:
            print(f"download single error [{e}]")

    def download(self, url:str, save_folder:str = "") -> bool: 
        total_len = self.getlenght(url)
        base_name = self.getname(url)
        name = os.path.join(save_folder, base_name) if save_folder else base_name
        try:    
            if self.multithread(url, total_len, name):
                return True
            else:
                self._download_single(url, total_len, name)
                return True
        except Exception as e:
            print("download error " + str(e))
            return False