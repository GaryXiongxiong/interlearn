#!/usr/bin/env bash
# Interlearn - Universal Environment Setup Template
# Modify THEME_DEPS below based on your topic before running.
set -euo pipefail

echo "🔧 Setting up interactive learning environment..."

# --- Base Dependencies (nbformat + jupyter_client for notebook generation) ---
BASE_DEPS=(
    "jupyterlab"
    "nbformat>=5.0"
    "jupyter_client"
    "ipykernel"
    "numpy"
    "matplotlib"
    "tqdm"
)

# --- Theme Plugins (modify this for your topic) ---
THEME_DEPS=()
# Examples:
#   "Transformer / deep learning" → THEME_DEPS=(torch jieba)
#   "Django"                      → THEME_DEPS=(django)
#   "Dynamic programming"         → no extra deps needed
#   "Data analysis"               → THEME_DEPS=(pandas seaborn)
#   "Computer vision"             → THEME_DEPS=(torchvision opencv-python)
#   "NLP"                         → THEME_DEPS=(transformers spacy)
#   "Web scraping"                → THEME_DEPS=(requests beautifulsoup4 selenium)

# ─── Force uv Installation ────────────────────────────────────────
install_uv() {
    echo "📦 Installing uv (Python package manager)..."
    if command -v pipx &> /dev/null; then
        pipx install uv
    elif command -v pip3 &> /dev/null || command -v pip &> /dev/null; then
        pip3 install --user uv 2>/dev/null || pip install --user uv 2>/dev/null
    else
        echo "❌ Cannot install uv: no pip available. Please install uv manually:"
        echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
}

# Ensure uv is available, install if missing
if ! command -v uv &> /dev/null; then
    echo "⚠️  uv not found. Installing..."
    install_uv
fi

# Verify uv works
if ! uv --version &> /dev/null; then
    echo "❌ uv installation failed. Please install manually:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi
echo "✅ uv $(uv --version 2>&1) detected and ready"

# ─── Create Virtual Environment via uv ────────────────────────────
VENV_DIR=".venv-interactive"

if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment at $VENV_DIR ..."
    uv venv "$VENV_DIR"
else
    echo "✅ Virtual environment already exists at $VENV_DIR"
fi

# Activate the venv for subsequent commands
source "$VENV_DIR/bin/activate"
echo "✅ Activated: $(python3 --version)"

# ─── Write pyproject.toml (clean, no duplicates) ──────────────────
if [ ! -f pyproject.toml ]; then
    echo "📝 Writing pyproject.toml..."
    cat > pyproject.toml << 'TOML'
[project]
name = "interlearn"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = []

[dependency-groups]
dev = []
TOML
else
    echo "✅ pyproject.toml already exists, skipping"
fi

# ─── Install Dependencies via uv in the venv ──────────────────────
echo "📦 Installing base dependencies..."
uv pip install --python "$VENV_DIR/bin/python3" "${BASE_DEPS[@]}"

if [ ${#THEME_DEPS[@]} -gt 0 ]; then
    echo "📦 Installing theme plugins: ${THEME_DEPS[*]}"
    uv pip install --python "$VENV_DIR/bin/python3" "${THEME_DEPS[@]}"
fi

# ─── Register Python Kernel (using venv's python, local only) ──────
echo ""
echo "🐍 Registering Python kernel for notebook execution..."
"$VENV_DIR/bin/python3" -m ipykernel install \
    --sys-prefix \
    --name interlearn \
    --display-name "Python 3 (interlearn)"

# ─── Verify Installation ──────────────────────────────────────────
echo ""
echo "✅ Environment setup complete!"
echo ""
echo "Installed packages:"
uv pip list --python "$VENV_DIR/bin/python3" 2>/dev/null | grep -E "(nbformat|jupyter_client|ipykernel|numpy|matplotlib)" || true
echo ""
echo "Available kernels:"
"$VENV_DIR/bin/python3" -m jupyter kernelspec list
echo ""
echo "To start JupyterLab for interactive viewing:"
echo "  source ${VENV_DIR}/bin/activate && jupyter lab --no-browser"
echo ""
echo "Or with uv directly:"
echo "  cd <project-dir> && source .venv-interactive/bin/activate && jupyter lab --no-browser"
