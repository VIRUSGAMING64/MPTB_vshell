from ast import parse
import os
import psutil
from pickle import FALSE
import shutil
from flask import Flask, request, redirect, url_for, send_from_directory, jsonify, make_response
from modules.compress.video import *

app = Flask(import_name=__name__, static_folder='static', template_folder='templates')
# app.secret_key = 'supersecretkey' # No longer needed without flash
UPLOAD_FOLDER = 'env'
app.config['UPLOAD_FOLDER'] = os.path.realpath(UPLOAD_FOLDER)
TOTAL = 0
PART  = 0
OK    = True

# Asegurarse de que la carpeta de subidas existe
BASE_DIR =  app.config['UPLOAD_FOLDER']
os.makedirs(BASE_DIR, exist_ok=True)

def get_safe_path(req_path):
    # Normalizar y asegurar que el path esté dentro de BASE_DIR
    if not req_path:
        req_path = ''
    # Eliminar barras iniciales para evitar que se interprete como root absoluto
    req_path = req_path.lstrip('/')
    abs_path = os.path.abspath(os.path.join(BASE_DIR, req_path))
    print(abs_path)
    if not abs_path.startswith(BASE_DIR):
        return BASE_DIR, ''
    return abs_path, req_path

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

@app.route('/api/list')
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

@app.route("/combstats",methods = ["GET"])
def combstats():
    global TOTAL,PART,OK
    if TOTAL == 0:
        TOTAL = 1
    return {
        "combertion":{
            "total":TOTAL,
            "part": PART,
            "percent": PART/TOTAL * 100,
            "ok": OK
        }
    }

@app.route("/combert",methods = ['POST'])
def combert():
    
    current_path = request.form.get('current_path', '')
    item_name    = request.form.get('item_name')
    item_type    = request.form.get('item_type') # 'file' or 'folder'

    if OK == False:
         return jsonify({'success': False, 'message': 'Conversion en progreso'}), 400
    
    infile, _    = get_safe_path(os.path.join(current_path, item_name))
    comp         = VideoCompressor(infile, update_stat,parse_end=True)
    
    Thread(target=comp.compress,daemon=True).start()
    return jsonify({'success': True, 'message': 'Conversion iniciada'})

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