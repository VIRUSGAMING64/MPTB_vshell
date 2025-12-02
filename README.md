# 🚀 MPTB_vshell

![Python Version](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Telegram Bot API](https://img.shields.io/badge/Telegram-Bot%20API-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT-412991?style=for-the-badge&logo=openai&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**MPTB_vshell** redefine la interacción con bots de Telegram. No es solo un bot, es un **sistema operativo virtual** en tu chat. Diseñado con una arquitectura modular y asíncrona, combina la potencia de una shell de comandos, gestión de archivos en la nube y la inteligencia artificial de OpenAI para ofrecer una experiencia de usuario sin precedentes.

---

## ✨ Características Destacadas

### 🧠 Inteligencia Artificial Integrada
Conversa de manera natural, obtén ayuda con código o genera contenido creativo gracias a la integración nativa con **OpenAI (ChatGPT)**. El bot mantiene el contexto y ofrece respuestas precisas.

### 📂 Sistema de Archivos Virtual (VFS)
Gestiona tus archivos como si estuvieras en una terminal Linux.
*   **Navegación:** Crea carpetas (`mkdir`), lista contenidos (`ls`) y organiza tu espacio.
*   **Gestión:** Elimina (`rm`), renombra y verifica tamaños (`size`) de archivos fácilmente.
*   **Nube Personal:** Sube y descarga archivos a tu "nube" privada gestionada por el bot.

### ⚡ Rendimiento y Concurrencia
Olvídate de los bots lentos. **MPTB_vshell** utiliza:
*   **Colas de Mensajes (`MessageQueue`):** Para un procesamiento ordenado y eficiente.
*   **Multithreading & Asyncio:** Maneja múltiples descargas, subidas y consultas a la IA simultáneamente sin bloquearse.

### 🛡️ Administración Robusta
*   Sistema completo de gestión de usuarios y permisos.
*   Base de datos personalizada para persistencia de estados.
*   Herramientas de moderación y control administrativo (`ban`, `promote`).

---

## 🛠️ Instalación y Configuración

### 1. Requisitos Previos
*   Python 3.8 o superior.
*   Cuenta de Telegram y Token del bot (@BotFather).
*   (Opcional) API Key de OpenAI.
*   (Opcional) API ID y Hash de Telegram (para funcionalidades de cliente de usuario/Pyrogram).

### 2. Clonar el Repositorio
```bash
git clone https://github.com/VIRUSGAMING64/MPTB_vshell.git
cd MPTB_vshell
```

### 3. Configurar Entorno Virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# .\venv\Scripts\activate # Windows
```

### 4. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 5. Configuración de Variables
Crea un archivo `.env` en la raíz o exporta las siguientes variables de entorno:

| Variable | Descripción | Requerido |
| :--- | :--- | :--- |
| `TOKEN` | El token de tu bot obtenido de @BotFather. | ✅ Sí |
| `ADMIN` | Tu ID de usuario de Telegram (para permisos de root). | ✅ Sí |
| `OPEN_AI` | Tu API Key de OpenAI (para funciones de IA). | ❌ No |
| `API_ID` | Tu App ID de my.telegram.org. | ❌ No |
| `API_HASH` | Tu App Hash de my.telegram.org. | ❌ No |

---

## 🎮 Guía de Uso

Inicia el bot con:
```bash
python bot.py
```

### Comandos Principales

#### 🐚 Shell y Archivos
*   `/ls` - Lista los archivos y directorios en tu ruta actual.
*   `/mkdir <nombre>` - Crea una nueva carpeta.
*   `/rm <nombre|índice>` - Elimina un archivo o carpeta.
*   `/size <nombre|índice>` - Muestra el tamaño de un archivo o directorio.

#### 🤖 Utilidades
*   `/start` - Inicia el bot y verifica el estado.
*   `/getid` - Muestra tu ID de Telegram (útil para configurar `ADMIN`).
*   `/help` - Muestra el mensaje de ayuda.

#### 👑 Administración (Solo Admin)
*   `/kill` - Apaga el bot remotamente.
*   `/su_state` - Cambia permisos de usuarios.
*   `/banuser` - Restringe acceso a usuarios.

---

## 📂 Estructura del Código

El proyecto sigue una estructura limpia y modular para facilitar la contribución:

```text
MPTB_vshell/
├── bot.py              # 🚀 Entry point: Inicialización y polling
├── modules/            # 📦 Núcleo del sistema
│   ├── core/           # Comandos base, colas y handlers
│   ├── downup/         # Motores de descarga y subida
│   ├── entity/         # Modelos de datos (User, File)
│   ├── brain.py        # Lógica de procesamiento central
│   ├── chatgpt.py      # Cliente de OpenAI
│   └── database.py     # Motor de base de datos JSON/Pickle
├── web/                # 🌐 Interfaz Web (Dashboard/Status)
├── tests/              # 🧪 Tests unitarios
└── requirements.txt    # Dependencias del proyecto
```

---

## 🤝 Contribución

¡Tu ayuda es bienvenida! Si tienes ideas para mejorar **MPTB_vshell**:
1.  Haz un Fork del proyecto.
2.  Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`).
3.  Haz Commit de tus cambios (`git commit -m 'Add some AmazingFeature'`).
4.  Haz Push a la rama (`git push origin feature/AmazingFeature`).
5.  Abre un Pull Request.

---

## 📄 Licencia

Distribuido bajo la licencia **MIT**. Ver `LICENSE` para más información.

---
<div align="center">
  <sub>Desarrollado con ❤️ por <a href="https://github.com/VIRUSGAMING64">VIRUSGAMING64</a></sub>
</div>
