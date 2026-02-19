let currentPath = new URLSearchParams(window.location.search).get('path') || '';

function showMessage(message, type) {
    const container = document.getElementById('flash-messages');
    const div = document.createElement('div');
    div.className = `flash-message flash-${type}`;
    div.textContent = message;
    container.appendChild(div);
    setTimeout(() => {
        div.remove();
    }, 5000);
}

async function loadFiles() {
    try {
        const response = await fetch(`/api/list?path=${encodeURIComponent(currentPath)}`);
        const data = await response.json();

        if (!response.ok) {
            showMessage(data.error || 'Error loading files', 'error');
            return;
        }

        // Update Breadcrumb
        let breadcrumbHtml = `Ruta actual: <strong>/${data.current_path ? data.current_path : ''}</strong>`;
        if (data.current_path) {
            const parentPath = data.current_path.includes('/') ? data.current_path.substring(0, data.current_path.lastIndexOf('/')) : '';
            breadcrumbHtml += `<a href="#" onclick="navigate('${parentPath}'); return false;" class="btn btn-sm" style="float: right;">⬆️ Subir nivel</a>`;
        }
        document.getElementById('breadcrumb').innerHTML = breadcrumbHtml;

        // Update File List
        const list = document.getElementById('fileList');
        list.innerHTML = '';

        if (data.folders.length === 0 && data.files.length === 0) {
            list.innerHTML = '<li class="file-item" style="justify-content: center; color: #666;">Carpeta vacía</li>';
        }

        data.folders.forEach(folder => {
            const li = document.createElement('li');
            li.className = 'file-item';
            const newPath = data.current_path ? `${data.current_path}/${folder}` : folder;
            li.innerHTML = `
                        <div class="file-info">
                            <span class="file-icon">📁</span>
                            <a href="#" onclick="navigate('${newPath}'); return false;" class="file-name">${folder}</a>
                        </div>
                        <div class="file-actions">
                            <button onclick="deleteItem('${folder.replace(/'/g, "\\'")}', 'folder')" class="btn btn-danger btn-sm">🗑️</button>
                        </div>
                    `;
            list.appendChild(li);
        });

        data.files.forEach(file => {
            const li = document.createElement('li');
            li.className = 'file-item';
            li.innerHTML = `
                        <div class="file-info">
                            <span class="file-icon">📄</span>
                            <span class="file-name">${file}</span>
                        </div>
                        <div class="file-actions">
                            <button onclick="convertFile('${file.replace(/'/g, "\\'")}')" class="btn btn-sm">X265</button>
                            <a href="/download?path=${encodeURIComponent(data.current_path)}&filename=${encodeURIComponent(file)}" class="btn btn-sm">⬇️</a>
                            <button onclick="deleteItem('${file.replace(/'/g, "\\'")}', 'file')" class="btn btn-danger btn-sm">🗑️</button>
                        </div>
                    `;
            list.appendChild(li);
        });

    } catch (error) {
        console.error(error);
        showMessage('Error de conexión', 'error');
    }
}

function navigate(path) {
    currentPath = path;
    const url = new URL(window.location);
    if (path) {
        url.searchParams.set('path', path);
    } else {
        url.searchParams.delete('path');
    }
    window.history.pushState({}, '', url);
    loadFiles();
}

// Handle browser back/forward buttons
window.onpopstate = () => {
    currentPath = new URLSearchParams(window.location.search).get('path') || '';
    loadFiles();
};

// Upload File
document.getElementById('uploadForm').onsubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    formData.append('current_path', currentPath);

    try {
        const res = await fetch('/upload', { method: 'POST', body: formData });
        const data = await res.json();
        if (res.ok && data.success) {
            showMessage(data.message, 'success');
            e.target.reset();
            loadFiles();
        } else {
            showMessage(data.message || 'Error', 'error');
        }
    } catch (err) {
        showMessage('Error uploading file', 'error');
    }
};

// Create Folder
document.getElementById('createFolderForm').onsubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    formData.append('current_path', currentPath);

    try {
        const res = await fetch('/create_folder', { method: 'POST', body: formData });
        const data = await res.json();
        if (res.ok && data.success) {
            showMessage(data.message, 'success');
            e.target.reset();
            loadFiles();
        } else {
            showMessage(data.message || 'Error', 'error');
        }
    } catch (err) {
        showMessage('Error creating folder', 'error');
    }
};

// Delete Item
async function deleteItem(name, type) {
    if (!confirm(`¿Estás seguro de eliminar este ${type === 'folder' ? 'carpeta' : 'archivo'}?`)) return;

    const formData = new FormData();
    formData.append('current_path', currentPath);
    formData.append('item_name', name);
    formData.append('item_type', type);

    try {
        const res = await fetch('/delete', { method: 'POST', body: formData });
        const data = await res.json();
        if (res.ok && data.success) {
            showMessage(data.message, 'success');
            loadFiles();
        } else {
            showMessage(data.message || 'Error', 'error');
        }
    } catch (err) {
        showMessage('Error deleting item', 'error');
    }
}

// Convert File
async function convertFile(name) {
    const formData = new FormData();
    formData.append('current_path', currentPath);
    formData.append('item_name', name);
    formData.append('item_type', 'file');

    try {
        const res = await fetch('/combert', { method: 'POST', body: formData });
        const data = await res.json();
        if (res.ok && data.success) {
            showMessage(data.message, 'success');
        } else {
            showMessage(data.message || 'Error', 'error');
        }
    } catch (err) {
        showMessage('Error starting conversion', 'error');
    }
}

// Conversion Statistics
var t;

function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

async function initStats() {
    try {
        const res = await fetch('/combstats');
        const data = await res.json();
        const c = data.combertion;
        const total = c.total;
        const part = c.part;
        const percent = c.percent;

        document.querySelector('.progress').style.width = percent + '%';
        document.getElementById('part').innerText = formatBytes(part);
        document.getElementById('total').innerText = formatBytes(total);
        document.getElementById('percentText').innerText = percent.toFixed(1) + '%';

        // Update Queue UI
        const queueList = document.getElementById('queueList');
        if (data.combertion.queue && data.combertion.queue.length > 0) {
            queueList.innerHTML = '';
            data.combertion.queue.forEach((item, index) => {
                const div = document.createElement('div');
                div.textContent = `${index + 1}. ${item}`;
                div.style.padding = '2px 0';
                queueList.appendChild(div);
            });
        } else {
            queueList.innerHTML = '<div style="font-style: italic;">Cola vacía</div>';
        }

        // Update Current File
        const currentFileText = document.getElementById('currentFileText');
        if (data.combertion.current) {
            currentFileText.textContent = data.combertion.current;
            currentFileText.style.color = '#fff';
        } else {
            currentFileText.textContent = 'Ninguno';
            currentFileText.style.color = '#666';
        }

    } catch (e) { console.log(e); }
}

// Start
loadFiles();
t = setInterval(initStats, 4000);

// FFmpeg Status Monitor
async function updateFfmpegStatus() {
    try {
        const response = await fetch('/api/ffmpeg-status');
        if (response.ok) {
            const data = await response.json();
            const indicator = document.getElementById('ffmpeg-indicator');
            if (data.running) {
                indicator.textContent = 'FFmpeg: EJECUTANDO';
                indicator.style.backgroundColor = '#4caf50'; // Green
                indicator.style.color = '#fff';
                indicator.style.boxShadow = '0 0 5px #4caf50';
            } else {
                indicator.textContent = 'FFmpeg: DETENIDO';
                indicator.style.backgroundColor = '#424242'; // Dark gray
                indicator.style.color = '#aa';
                indicator.style.boxShadow = 'none';
            }
        }
    } catch (error) {
        console.error('Error fetching ffmpeg stats:', error);
    }
}

// Check every 3 seconds
setInterval(updateFfmpegStatus, 10000);
updateFfmpegStatus();
