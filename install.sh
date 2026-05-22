#!/usr/bin/env bash

# Self-contained Bash Installer for Delphi for Python Wizard Skill
# Usage:
#   curl -sSL https://raw.githubusercontent.com/gaitolini/delphi-for-python-wizard/main/install.sh | bash

REPO_URL="https://github.com/gaitolini/delphi-for-python-wizard.git"
SKILL_FOLDER_NAME="delphi-for-python-wizard"

echo "============================================================"
echo "  Delphi for Python Wizard - AI Skill & Workspace Installer"
echo "============================================================"

# 1. Determine Source Directory (Clone if run remotely)
CURRENT_DIR="$(pwd)"
TEMP_DIR=""
SOURCE_SKILL_PATH="${CURRENT_DIR}/${SKILL_FOLDER_NAME}"

if [ ! -f "${SOURCE_SKILL_PATH}/SKILL.md" ]; then
    echo "[Info] Executando fora de um repositório clonado localmente."
    echo "[Info] Clonando o repositório temporariamente a partir de ${REPO_URL}..."
    
    TEMP_DIR="/tmp/delphi-for-python-wizard-temp"
    rm -rf "${TEMP_DIR}" 2>/dev/null
    
    if git clone "${REPO_URL}" "${TEMP_DIR}"; then
        SOURCE_SKILL_PATH="${TEMP_DIR}/${SKILL_FOLDER_NAME}"
    else
        echo "[Erro] Falha ao clonar o repositório. Certifique-se de que o Git está instalado no PATH."
        exit 1
    fi
fi

# 2. Detect Target Folders (.agent or Global Antigravity)
INSTALL_PATHS=()

# Check local workspace for .agent / .agent/skills
LOCAL_AGENT_DIR="${CURRENT_DIR}/.agent"
if [ -d "${LOCAL_AGENT_DIR}" ]; then
    echo "[Info] Diretório do agente local (.agent) detectado na pasta atual."
    LOCAL_SKILLS_DIR="${LOCAL_AGENT_DIR}/skills"
    mkdir -p "${LOCAL_SKILLS_DIR}"
    INSTALL_PATHS+=("${LOCAL_SKILLS_DIR}/${SKILL_FOLDER_NAME}")
fi

# Check global Antigravity path (Windows user profile or Unix home)
if [ -n "$USERPROFILE" ]; then
    GLOBAL_SKILLS_DIR="${USERPROFILE}/.gemini/antigravity/skills"
else
    GLOBAL_SKILLS_DIR="${HOME}/.gemini/antigravity/skills"
fi

if [ -d "${GLOBAL_SKILLS_DIR}" ]; then
    INSTALL_PATHS+=("${GLOBAL_SKILLS_DIR}/${SKILL_FOLDER_NAME}")
else
    # If parent gemini dir exists, we can create skills folder
    GLOBAL_BASE=$(dirname "${GLOBAL_SKILLS_DIR}")
    if [ -d "${GLOBAL_BASE}" ]; then
        mkdir -p "${GLOBAL_SKILLS_DIR}"
        INSTALL_PATHS+=("${GLOBAL_SKILLS_DIR}/${SKILL_FOLDER_NAME}")
    fi
fi

# Default Fallback if none found
if [ ${#INSTALL_PATHS[@]} -eq 0 ]; then
    DEFAULT_LOCAL_DIR="${CURRENT_DIR}/.agent/skills"
    mkdir -p "${DEFAULT_LOCAL_DIR}"
    INSTALL_PATHS+=("${DEFAULT_LOCAL_DIR}/${SKILL_FOLDER_NAME}")
fi

# 3. Copy Skill Files to Targets
for TARGET in "${INSTALL_PATHS[@]}"; do
    echo "[Info] Instalando Skill em: ${TARGET}"
    rm -rf "${TARGET}" 2>/dev/null
    mkdir -p "${TARGET}"
    cp -r "${SOURCE_SKILL_PATH}"/* "${TARGET}/"
    echo "[Sucesso] Arquivos copiados com sucesso!"
done

# 4. Automate Virtual Environment (.venv) Creation
VENV_PATH="${CURRENT_DIR}/.venv"
if [ ! -d "${VENV_PATH}" ]; then
    echo "[Info] Nenhum ambiente virtual (.venv) encontrado na pasta de destino."
    echo "[Info] Verificando versões de Python compatíveis instaladas..."
    
    PYTHON_EXE=""
    TARGET_VERSIONS=("python3.13" "python3.12" "python3.11" "python3.10" "python3.9" "python3.8" "python3" "python")
    
    for cmd in "${TARGET_VERSIONS[@]}"; do
        if command -v "$cmd" &>/dev/null; then
            # Verify version compatibility
            major=$("$cmd" -c "import sys; print(sys.version_info.major)")
            minor=$("$cmd" -c "import sys; print(sys.version_info.minor)")
            if [ "$major" -eq 3 ] && [ "$minor" -ge 8 ] && [ "$minor" -le 13 ]; then
                PYTHON_EXE="$cmd"
                break
            fi
        fi
    done
    
    if [ -z "${PYTHON_EXE}" ]; then
        echo "[Aviso] Nenhuma versão estável recomendada (Python 3.8 a 3.13) foi encontrada."
        echo "Por favor, instale o Python 3.12 ou 3.13 para obter a melhor compatibilidade."
    else
        echo "[Info] Criando ambiente virtual (.venv) usando ${PYTHON_EXE}..."
        "${PYTHON_EXE}" -m venv "${VENV_PATH}"
        
        # Configure local dependencies
        if [ -f "${VENV_PATH}/bin/python" ]; then
            VENV_PYTHON="${VENV_PATH}/bin/python"
        elif [ -f "${VENV_PATH}/Scripts/python.exe" ]; then
            VENV_PYTHON="${VENV_PATH}/Scripts/python.exe"
        fi
        
        if [ -n "${VENV_PYTHON}" ] && [ -f "${VENV_PYTHON}" ]; then
            echo "[Info] Atualizando o pip no ambiente virtual..."
            "${VENV_PYTHON}" -m pip install --upgrade pip &>/dev/null
            echo "[Info] Instalando delphivcl no ambiente virtual (.venv)..."
            "${VENV_PYTHON}" -m pip install delphivcl &>/dev/null
            echo "[Sucesso] Ambiente virtual (.venv) criado e configurado!"
        fi
    fi
else
    echo "[Info] Ambiente virtual (.venv) já existe. Ignorando criação."
fi

# 5. Cleanup Temp Directory
if [ -n "${TEMP_DIR}" ] && [ -d "${TEMP_DIR}" ]; then
    rm -rf "${TEMP_DIR}"
fi

echo "============================================================"
echo "  Instalação concluída com sucesso! Nova Skill ativa."
echo "============================================================"
