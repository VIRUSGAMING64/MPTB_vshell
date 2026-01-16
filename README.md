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

---

# 📚 Detailed Technical Documentation

This section provides a deep dive into the architecture, design patterns, and internal data flow of **MPTB_vshell**, intended for developers who wish to understand or extend the system.

## ⚙️ Architecture & Core Components

### 1. The Kernel (`bot.py`)
The `bot.py` file serves as the system's entry point and orchestrator. It manages concurrent execution using Python's `threading` module to ensure the bot remains responsive while performing heavy tasks:
- **Bot Application**: Initializes the `python-telegram-bot` application and starts the polling loop to listen for updates.
- **Database Saver**: A daemon thread that periodically (every `DB_SAVE_TIMEOUT` seconds) commits the in-memory database state to the `database.csv` file on disk, ensuring data persistence without blocking the main event loop.
- **Web Server**: Launches the Flask application (`web/app.py`) in a separate thread. This allows the admin dashboard to run side-by-side with the Telegram bot process.
- **Initialization Routine**: The `__init__` function waits for the bot's event loop to be ready and verifies that the configured administrators (`ADMINS_ID`) are properly registered in the database with the correct privileges (`ADMIN | LLM`).

### 2. The "Brain" (`modules/brain.py`)
This module acts as the central **Message Router**. When an update (Message) is received, `brain.py` analyzes its content and delegates responsibility:
- **Command Handling**: If the text starts with a slash `/` (or the configured `BOT_HANDLER`), it matches the command against the registry in `modules/core/commands.py` and executes the corresponding function.
- **Media Detection**: It scans messages for URLs from supported platforms (like YouTube, Instagram, Facebook). If a match is found, it triggers the extraction and download logic in `modules/downup`.
- **AI Processing**: If the message is not a command or media link, and the user possesses the `LLM` flag authorization, the text is forwarded to `modules/chatgpt.py` or configured LLM provider for natural language processing.

### 3. Database System (`modules/database.py`)
The project uses a lightweight, custom **CSV-based** persistence layer designed for speed and simplicity.
- **In-Memory Cache**: Upon startup, the entire CSV file is loaded into a dictionary (`self.dic`). This ensures that user lookups are typically O(1) operations, extremely fast.
- **Serialization**: The `database.py` module handles the conversion between `peer` (User) objects and their CSV string representation.
- **Thread-Safety**: While simple, the `save()` method is called from a dedicated thread, minimizing I/O blocking on the main execution path.

### 4. Roles, Permissions & Bitmasks (`modules/core/enums.py` & `entity`)
To manage permissions efficiently, the system utilizes **Bitwise Flags**. This allows for complex role combinations within a single integer field.
- **Role Flags**:
    - `ADMIN` (16): Full system control.
    - `LLM` (8): Authorized to interact with the AI models.
    - `BANNED` (1): Restricted access.
- **Message Type Flags**: Used to quickly categorize content type (VIDEO, DOCUMENT, URL, etc.) internally.
- **User State**: A user's state is simply the sum of these flags (e.g., `ADMIN | LLM` = 24). Checks are performed using bitwise AND operations (e.g., `if user.state & ADMIN:`).

### 5. Media Engine (`modules/downup`)
This module handles the heavy lifting of file operations, specifically designed to bypass standard bot API limits where possible.
- **`downloader.py`**: A custom **Multi-threaded HTTP Downloader**. It requests files in "chunks" (byte ranges) concurrently, saturating the available bandwidth for faster downloads.
- **Pyrogram Integration**: For uploading files larger than 50MB (up to 2GB or 4GB for premium), the bot leverages `Pyrogram` (a MTProto client) instead of the standard HTTP Bot API. This requires the `API_ID` and `API_HASH` credentials.

### 6. Video Compression (`modules/compress`)
Automated media optimization pipeline using **FFmpeg**.
- **HEVC/H.265**: The default encoding profile targets `libx265`, providing significant size reduction (often 50%+) compared to standard H.264 while maintaining visual quality.
- **Concurrency**: The compressor class manages FFmpeg processes, potentially running them in separate threads to avoid blocking the bot's responsiveness during long encoding tasks.

### 7. Global Variables & Configuration (`modules/gvar.py`)
The central configuration hub.
- It loads all environment variables (`os.getenv`).
- It initializes shared singletons like the OpenAI client or the Database instance.
- It defines constants used across the application to avoid magic numbers or hardcoded strings.

## 🔧 Deep Dive: Environment Variables

| Variable | Criticality | Technical Description |
| :--- | :--- | :--- |
| `TOKEN` | **Critical** | The HTTP API Token generated by BotFather. The main `python-telegram-bot` instance uses this for polling and standard API calls. |
| `API_ID` | **Critical** | The Application ID from `my.telegram.org`. Required to initialize the MTProto client (Pyrogram). |
| `API_HASH` | **Critical** | The API Hash paired with the API_ID. Essential for the MTProto handshake. |
| `OPEN_AI` | Optional | API Key for OpenAI. If absent, the `chatgpt.py` module will gracefully fail or disable AI features. |
| `ADMIN` | **Critical** | The numeric Telegram ID of the Superuser. During the boot sequence in `bot.py`, this ID is automatically granted `ADMIN` and `LLM` privileges in the database. |
| `BOT_HANDLER`| Optional | A cleaner prefix for commands (e.g., `.start` vs `/start`). Useful when multiple bots share a group chat to prevent command naming collisions. |
| `HTTP_PROXY` | Optional | Proxy URL. If set, the bot routes traffic through this proxy, useful for hosting in restricted network environments. |

