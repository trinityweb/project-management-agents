"""Cargador de configuración para los agentes."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class ConfigLoader:
    """Carga y gestiona la configuración de los agentes."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Inicializa el cargador de configuración.
        
        Args:
            config_dir: Directorio donde están los archivos de configuración.
                       Si es None, usa el directorio config/ relativo a este módulo.
        """
        if config_dir is None:
            # Obtener el directorio base del proyecto
            base_dir = Path(__file__).parent.parent
            config_dir = base_dir / "config"
        
        self.config_dir = config_dir
        self.base_dir = config_dir.parent
        
        # Cargar variables de entorno
        env_file = self.base_dir / ".env"
        if not env_file.exists():
            env_file = self.base_dir / "env.example"
        
        if env_file.exists():
            load_dotenv(env_file)
    
    def load_env(self, key: str, default: Optional[str] = None) -> str:
        """
        Carga una variable de entorno.
        
        Args:
            key: Nombre de la variable de entorno
            default: Valor por defecto si no existe
            
        Returns:
            Valor de la variable de entorno
            
        Raises:
            ValueError: Si la variable no existe y no hay valor por defecto
        """
        value = os.getenv(key, default)
        if value is None:
            raise ValueError(f"Variable de entorno {key} no encontrada")
        return value
    
    def load_github_config(self) -> Dict[str, Any]:
        """
        Carga la configuración de GitHub.
        
        Returns:
            Diccionario con la configuración de GitHub
            
        Raises:
            FileNotFoundError: Si el archivo de configuración no existe
        """
        config_file = self.config_dir / "github-config.json"
        if not config_file.exists():
            example_file = self.config_dir / "github-config.example.json"
            if example_file.exists():
                raise FileNotFoundError(
                    f"Archivo de configuración no encontrado: {config_file}\n"
                    f"Copia {example_file} a {config_file} y configura tus valores."
                )
            raise FileNotFoundError(f"Archivo de configuración no encontrado: {config_file}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_project_root(self) -> Path:
        """
        Obtiene la ruta raíz del proyecto.
        
        Returns:
            Path a la raíz del proyecto
        """
        project_root = self.load_env("PROJECT_ROOT", None)
        if project_root:
            return Path(project_root)
        
        # Intentar detectar automáticamente
        current = Path(__file__).parent.parent.parent.parent
        if (current / "INICIO_RAPIDO.md").exists():
            return current
        
        raise ValueError(
            "No se pudo determinar PROJECT_ROOT. "
            "Configura la variable de entorno PROJECT_ROOT o .env"
        )
    
    def get_github_token(self) -> str:
        """
        Obtiene el token de GitHub.
        
        Returns:
            Token de GitHub
            
        Raises:
            ValueError: Si el token no está configurado
        """
        return self.load_env("GITHUB_TOKEN")

