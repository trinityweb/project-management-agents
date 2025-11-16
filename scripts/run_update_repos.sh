#!/bin/bash
# Script para ejecutar el agente update_repositories

set -e

# Obtener el directorio base del script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
AGENT_DIR="$BASE_DIR/agents/update_repositories"
VENV_DIR="$AGENT_DIR/venv"
AGENT_SCRIPT="$AGENT_DIR/update_repositories_agent.py"

# Verificar que existe el venv
if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Entorno virtual no encontrado. Ejecuta primero: ./scripts/setup.sh"
    exit 1
fi

# Activar venv y ejecutar agente
source "$VENV_DIR/bin/activate"
python "$AGENT_SCRIPT" "$@"

