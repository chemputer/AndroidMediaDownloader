#!/usr/bin/env bash
set -euo pipefail

echo "[+] Updating Ubuntu system packages..."
sudo apt update && sudo apt upgrade -y

echo "[+] Installing Buildozer and Android NDK dependencies..."
sudo apt install -y \
    build-essential \
    git \
    ffmpeg \
    ccache \
    path \
    zip \
    unzip \
    openjdk-17-jdk \
    python3 \
    python3-pip \
    python3-venv \
    python3-setuptools \
    libffi-dev \
    libssl-dev \
    libtinfo5 \
    libstdc++6 \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    autoconf \
    libtool \
    pkg-config \
    cmake \
    lld

echo "[+] Installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

echo "[+] Creating virtual environment using uv..."
uv venv ~/.venv/buildozer --python python3

echo "[+] Installing Cython, Buildozer, and Kivy tools..."
pip install --upgrade pip setuptools wheel
pip install "cython<3.0.0" buildozer Kivy yt-dlp RedDownloader

echo "[+] Ensuring environment variable persistence..."
if ! grep -q "buildozer/bin/activate" ~/.bashrc; then
    echo "source ~/.venv/buildozer/bin/activate" >> ~/.bashrc
fi

echo "[+] Setup complete! Run 'source ~/.bashrc' to activate your build environment."
