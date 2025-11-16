#!/bin/bash
# Script para ejecutar el agente start_project

set -e

# Obtener el directorio base del script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
AGENT_DIR="$BASE_DIR/agents/start_project"
VENV_DIR="$AGENT_DIR/venv"
AGENT_SCRIPT="$AGENT_DIR/start_project_agent.py"

# Verificar que existe el venv
if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Entorno virtual no encontrado. Ejecuta primero: ./scripts/setup.sh"
    exit 1
fi

# Activar venv y ejecutar agente
source "$VENV_DIR/bin/activate"
python "$AGENT_SCRIPT" "$@"

