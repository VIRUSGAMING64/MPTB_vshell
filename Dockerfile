FROM python
WORKDIR /app

# Instalar dependencias del sistema
# ffmpeg: necesario para las funciones de video/audio del bot
# gcc, build-essential: necesarios para compilar librerías como TgCrypto o psutil
RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    build-essential \
    libjemalloc2 \
    && rm -rf /var/lib/apt/lists/*
    
RUN pip install setuptools
# Configurar jemalloc como administrador de memoria para reducir fragmentación
ENV LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2

# Copiar archivo de requerimientos
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Optimización de memoria para Python en Linux (ayuda a mantener el consumo bajo)
ENV MALLOC_ARENA_MAX=2

COPY . .

CMD ["python", "bot.py"]
