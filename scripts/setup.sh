#!/bin/bash
# Script de setup para crear entornos virtuales e instalar dependencias

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Obtener el directorio base del script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${GREEN}=== Setup de Agentes de Gestión de Proyecto ===${NC}"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 no está instalado${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}Python encontrado: ${PYTHON_VERSION}${NC}"
echo ""

# Función para crear venv e instalar dependencias
setup_agent() {
    local AGENT_NAME=$1
    local AGENT_DIR="$BASE_DIR/agents/$AGENT_NAME"
    local VENV_DIR="$AGENT_DIR/venv"
    local REQUIREMENTS="$AGENT_DIR/requirements.txt"
    
    echo -e "${YELLOW}Configurando agente: $AGENT_NAME${NC}"
    
    if [ ! -d "$AGENT_DIR" ]; then
        echo -e "${RED}Error: Directorio no encontrado: $AGENT_DIR${NC}"
        return 1
    fi
    
    # Crear venv si no existe
    if [ ! -d "$VENV_DIR" ]; then
        echo "  Creando entorno virtual..."
        python3 -m venv "$VENV_DIR"
        echo -e "${GREEN}  ✓ Entorno virtual creado${NC}"
    else
        echo "  Entorno virtual ya existe"
    fi
    
    # Instalar dependencias
    if [ -f "$REQUIREMENTS" ]; then
        echo "  Instalando dependencias..."
        if "$VENV_DIR/bin/pip" install --upgrade pip > /dev/null 2>&1; then
            if "$VENV_DIR/bin/pip" install -r "$REQUIREMENTS" > /dev/null 2>&1; then
                echo -e "${GREEN}  ✓ Dependencias instaladas${NC}"
            else
                echo -e "${RED}  ✗ Error al instalar dependencias${NC}"
                return 1
            fi
        else
            echo -e "${RED}  ✗ Error al actualizar pip${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}  ⚠ No se encontró requirements.txt${NC}"
    fi
    
    echo ""
}

# Instalar dependencias compartidas primero
echo -e "${YELLOW}Instalando dependencias compartidas...${NC}"
if [ -f "$BASE_DIR/requirements.txt" ]; then
    if python3 -m pip install --user -r "$BASE_DIR/requirements.txt" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Dependencias compartidas instaladas${NC}"
    else
        echo -e "${YELLOW}⚠ Advertencia: Error al instalar dependencias compartidas (continuando...)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ No se encontró requirements.txt compartido${NC}"
fi
echo ""

# Configurar cada agente
echo -e "${YELLOW}Configurando agentes...${NC}"
setup_agent "start_project" || echo -e "${RED}Error configurando start_project${NC}"
setup_agent "update_documentation" || echo -e "${RED}Error configurando update_documentation${NC}"
setup_agent "update_repositories" || echo -e "${RED}Error configurando update_repositories${NC}"
echo ""

# Verificar configuración
echo -e "${YELLOW}Verificando configuración...${NC}"

# Verificar .env
if [ ! -f "$BASE_DIR/.env" ]; then
    if [ -f "$BASE_DIR/env.example" ]; then
        echo -e "${YELLOW}  ⚠ Archivo .env no encontrado${NC}"
        echo -e "${YELLOW}  Copia env.example a .env y configura tus valores:${NC}"
        echo -e "    cp $BASE_DIR/env.example $BASE_DIR/.env"
    fi
else
    echo -e "${GREEN}  ✓ Archivo .env encontrado${NC}"
fi

# Verificar github-config.json
if [ ! -f "$BASE_DIR/config/github-config.json" ]; then
    if [ -f "$BASE_DIR/config/github-config.example.json" ]; then
        echo -e "${YELLOW}  ⚠ Archivo github-config.json no encontrado${NC}"
        echo -e "${YELLOW}  Copia github-config.example.json a github-config.json:${NC}"
        echo -e "    cp $BASE_DIR/config/github-config.example.json $BASE_DIR/config/github-config.json"
    fi
else
    echo -e "${GREEN}  ✓ Archivo github-config.json encontrado${NC}"
fi

echo ""
echo -e "${GREEN}=== Setup completado ===${NC}"
echo ""
echo "Para ejecutar los agentes, usa los scripts en scripts/:"
echo "  ./scripts/run_start_project.sh"
echo "  ./scripts/run_update_docs.sh"
echo "  ./scripts/run_update_repos.sh"

