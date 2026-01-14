# 🤖 MPTB_vshell

**MPTB_vshell** is a robust and modular Telegram bot framework designed to integrate the power of **OpenAI (ChatGPT)** with advanced media management capabilities. Its flexible architecture allows for easy extension and customization.

## 🚀 Key Features

- **🤖 Deep Telegram Integration**: Built on `python-telegram-bot` for fluid and reactive interaction.
- **🧠 Artificial Intelligence**: Native support for **OpenAI (ChatGPT)**, enabling natural conversations and language processing.
- **📂 Advanced Media Management**: Download and upload large files with `Pyrogram` efficiency.
- **🎬 Media Compression**: Built-in video compression capabilities leveraging **FFmpeg** (H.265/HEVC).
- **🌐 Web Interface**: Integrated Flask-based web dashboard for file management (`web/app.py`).
- **🐳 Docker Ready**: Includes a configured `Dockerfile` with all dependencies and optimizations (jemalloc).
- **👤 User & Role System**: Complete management of users, states, and permissions (Admin, User, Banned, etc.).
- **🧩 Modular Architecture**: Code organized into independent modules (`brain`, `core`, `downup`, `compress`, etc.) for easy maintenance and scalability.
- **💾 Data Persistence**: Simple yet effective database system to maintain state.

## 📋 Requirements

- 🐍 **Python 3.8** or higher.
- 🎬 **FFmpeg** (Required for media processing).
- 📱 A **Telegram** account and a **Bot Token** (obtained from @BotFather).
- 🔑 **Telegram API ID** & **API Hash** (for Pyrogram, get it from my.telegram.org).
- 🤖 **OpenAI API Key** (optional, for AI features).

## 🛠️ Installation

### Option A: Local Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd MPTB_vshell
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Linux/Mac
   # .venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *Note: Ensure `ffmpeg` is installed on your system if you plan to use media features.*

### Option B: Docker (Recommended)

1. **Build the image:**
   ```bash
   docker build -t mptb_vshell .
   ```

2. **Run the container:**
   ```bash
   docker run -d --env-file .env --name mptb_vshell mptb_vshell
   ```

## ⚙️ Configuration

The bot uses environment variables for configuration. You can set them in your system, create a `.env` file, or pass them to Docker.

Required variables:

| Variable | Description |
|----------|-------------|
| `TOKEN` | Telegram Bot Token. |
| `API_ID` | Telegram Application ID. |
| `API_HASH` | Telegram API Hash. |
| `OPEN_AI` | OpenAI API Key. |
| `ADMIN` | Numerical ID of the main administrator. |
| `HTTP_PROXY` | (Optional) HTTP Proxy. |
| `HTTPS_PROXY` | (Optional) HTTPS Proxy. |

## ▶️ Usage

Once configured, start the bot with the following command:

```bash
python bot.py
```

## 📂 Project Structure

```text
MPTB_vshell/
├── bot.py                  # 🚀 Main bot entry point
├── clean.sh                # 🧹 Script to clean temporary files
├── database.csv            # 💾 Simple database (CSV)
├── Dockerfile              # 🐳 Docker configuration
├── requirements.txt        # 📦 Dependency list
├── modules/                # 🧩 Modular bot logic
│   ├── brain.py            # 🧠 Brain: Message processing
│   ├── chatgpt.py          # 🤖 AI: OpenAI integration
│   ├── database.py         # 🗄️ DB: Database handling
│   ├── gvar.py             # ⚙️ Config: Global variables & env
│   ├── utils.py            # 🛠️ Utils: Various tools
│   ├── compress/           # 🎬 Compress: Video compression logic
│   ├── core/               # ⚡ Core: Commands, queues, and workers
│   ├── downup/             # 📥📤 DownUp: Media download & upload
│   ├── entity/             # 👤 Entity: Object definitions (User, etc.)
│   └── fuse/               # 🔌 Fuse: Additional/experimental modules
└── web/                    # 🌐 Web: Administration web interface
    ├── app.py              # 🌐 Flask application
    ├── static/             # 🎨 Static assets
    └── templates/          # 📄 HTML templates
```
