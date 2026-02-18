import os
import psutil
import shutil
from flask import Flask, request, redirect, url_for, send_from_directory, jsonify, make_response, session, flash, render_template
from modules.compress.video import *
from functools import wraps

app = Flask(import_name=__name__, static_folder='static', template_folder='templates')
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'env'
app.config['UPLOAD_FOLDER'] = os.path.realpath(UPLOAD_FOLDER)
TOTAL = 0
PART  = 0
OK    = True

GLOBAL_BASE_DIR = app.config['UPLOAD_FOLDER']
os.makedirs(GLOBAL_BASE_DIR, exist_ok=True)

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
    return GLOBAL_BASE_DIR # Fallback or for public if intended, but we will protect routes

def get_safe_path(req_path):
    base_dir = get_base_dir()
    # Normalizar y asegurar que el path esté dentro de BASE_DIR
    if not req_path:
        req_path = ''
    # Eliminar barras iniciales para evitar que se interprete como root absoluto
    req_path = req_path.lstrip('/')
    abs_path = os.path.abspath(os.path.join(base_dir, req_path))
    # print(abs_path)
    if not abs_path.startswith(base_dir):
        return base_dir, ''
    return abs_path, req_path

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
    return render_template('index.html', username=session.get('user'))

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
                files.append(item)
    except PermissionError:
        return jsonify({'error': 'Permission denied', 'files': [], 'folders': [], 'current_path': rel_path}), 403

    folders.sort()
    files.sort()
    
    return jsonify({
        'files': files,
        'folders': folders,
        'current_path': rel_path
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

@login_required
@app.route('/download')
def download_file():
    req_path = request.args.get('path', '')
    filename = request.args.get('filename')
    
    if not filename:
        return make_response("Filename required", 400)
        
    abs_path, _ = get_safe_path(req_path)
    return send_from_directory(abs_path, filename, as_attachment=True)

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