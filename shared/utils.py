"""Utilidades compartidas para los agentes."""

import subprocess
import sys
import logging
from pathlib import Path
from typing import Optional, Tuple, List


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """
    Configura el logging para los agentes.
    
    Args:
        level: Nivel de logging
        
    Returns:
        Logger configurado
    """
    logger = logging.getLogger("project_management_agents")
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def run_command(command: List[str], cwd: Optional[Path] = None, 
                check: bool = True, capture_output: bool = False) -> Tuple[int, str, str]:
    """
    Ejecuta un comando en el shell.
    
    Args:
        command: Lista con el comando y sus argumentos
        cwd: Directorio de trabajo
        check: Si es True, lanza excepción si el comando falla
        capture_output: Si es True, captura stdout y stderr
        
    Returns:
        Tupla con (returncode, stdout, stderr)
        
    Raises:
        subprocess.CalledProcessError: Si check=True y el comando falla
    """
    logger = logging.getLogger("project_management_agents")
    logger.debug(f"Ejecutando comando: {' '.join(command)}")
    
    try:
        # Convertir Path a string si es necesario
        cwd_str = str(cwd) if cwd else None
        logger.debug(f"Directorio de trabajo: {cwd_str}")
        
        result = subprocess.run(
            command,
            cwd=cwd_str,
            check=check,
            capture_output=capture_output,
            text=True,
            encoding='utf-8'
        )
        
        stdout = result.stdout if capture_output else ""
        stderr = result.stderr if capture_output else ""
        
        if result.returncode != 0:
            logger.warning(f"Comando falló con código {result.returncode}")
            if stderr:
                logger.warning(f"stderr: {stderr}")
        
        return result.returncode, stdout, stderr
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al ejecutar comando: {e}")
        if check:
            raise
        return e.returncode, e.stdout if hasattr(e, 'stdout') else "", e.stderr if hasattr(e, 'stderr') else ""


def check_docker_running() -> bool:
    """
    Verifica si Docker está corriendo.
    
    Returns:
        True si Docker está corriendo, False en caso contrario
    """
    logger = logging.getLogger("project_management_agents")
    try:
        returncode, _, _ = run_command(["docker", "info"], check=False, capture_output=True)
        if returncode == 0:
            logger.info("Docker está corriendo")
            return True
        else:
            logger.warning("Docker no está corriendo")
            return False
    except FileNotFoundError:
        logger.error("Docker no está instalado o no está en el PATH")
        return False


def find_files(pattern: str, root_dir: Path, recursive: bool = True) -> List[Path]:
    """
    Busca archivos que coincidan con un patrón.
    
    Args:
        pattern: Patrón de búsqueda (ej: "*.json", "*postman*.json")
        root_dir: Directorio raíz para buscar
        recursive: Si es True, busca recursivamente
        
    Returns:
        Lista de Paths que coinciden con el patrón
    """
    if recursive:
        return list(root_dir.rglob(pattern))
    else:
        return list(root_dir.glob(pattern))


def ensure_dir(path: Path) -> Path:
    """
    Asegura que un directorio existe, creándolo si es necesario.
    
    Args:
        path: Ruta del directorio
        
    Returns:
        Path del directorio
    """
    path.mkdir(parents=True, exist_ok=True)
    return path

