#!/bin/bash
# ==============================================================================
# Universal Video & Audio Downloader - Launcher para macOS
# Utiliza os binários e bibliotecas globais (Homebrew / Miniforge / Global Python)
# evitando duplicação de ambientes ou downloads redundantes.
# ==============================================================================

# Entrar no diretório do projeto
cd "$(dirname "$0")" || exit 1

# Carregar ambiente Homebrew (garante ffmpeg e ferramentas de sistema no PATH)
if [ -x "/opt/homebrew/bin/brew" ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# Garantir ferramentas no PATH prioritário
export PATH="/opt/homebrew/Caskroom/miniforge/base/bin:/opt/homebrew/bin:$HOME/.local/bin:$PATH"

# Selecionar o executável Python global que possui as dependências
if [ -x "/opt/homebrew/Caskroom/miniforge/base/bin/python3" ]; then
    PYTHON_BIN="/opt/homebrew/Caskroom/miniforge/base/bin/python3"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python3)"
else
    echo "❌ Erro: Python 3 não foi encontrado no sistema."
    read -p "Pressione Enter para sair..."
    exit 1
fi

echo "========================================================"
echo "  ⚡ Universal Video Downloader • Terminal Edition"
echo "========================================================"
echo "  Python : $($PYTHON_BIN --version 2>&1)"
echo "  FFmpeg : $(command -v ffmpeg || echo 'Não encontrado')"
echo "  Diretório: $(pwd)"
echo "========================================================"
echo "Iniciando aplicação..."

# Executa o app com o Python global
"$PYTHON_BIN" app.py

EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "⚠️ O aplicativo encerrou com código $EXIT_CODE."
    echo "Pressione [Enter] para fechar esta janela..."
    read -r
fi
