# Import Python
FROM python:3.9-slim-bullseye

# Make /app dir
WORKDIR /app

# Install system dependencies
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Kolkata

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    wget \
    aria2 \
    curl \
    busybox \
    p7zip-full \

    unzip \
    mkvtoolnix \
    ffmpeg \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip3 install --upgrade pip setuptools wheel && \
    pip3 install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Permissions
RUN chmod +x extract run.sh

# Start bot
CMD ["bash", "run.sh"]
