#!/usr/bin/env python3
"""Agente para iniciar el proyecto siguiendo INICIO_RAPIDO.md"""

import argparse
import sys
from pathlib import Path

# Agregar el directorio shared al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.config_loader import ConfigLoader
from shared.utils import setup_logging, run_command, check_docker_running


class StartProjectAgent:
    """Agente que inicia el proyecto siguiendo INICIO_RAPIDO.md"""
    
    def __init__(self):
        """Inicializa el agente."""
        self.logger = setup_logging()
        self.config = ConfigLoader()
        self.project_root = self.config.get_project_root()
        self.inicio_rapido_path = self.project_root / "INICIO_RAPIDO.md"
    
    def verify_inicio_rapido_exists(self) -> bool:
        """
        Verifica que existe el archivo INICIO_RAPIDO.md.
        
        Returns:
            True si existe, False en caso contrario
        """
        if not self.inicio_rapido_path.exists():
            self.logger.error(f"Archivo INICIO_RAPIDO.md no encontrado en {self.inicio_rapido_path}")
            return False
        self.logger.info(f"Archivo INICIO_RAPIDO.md encontrado: {self.inicio_rapido_path}")
        return True
    
    def start_docker(self) -> bool:
        """
        Inicia Docker Desktop si no está corriendo.
        
        Returns:
            True si Docker está corriendo, False en caso contrario
        """
        if check_docker_running():
            return True
        
        self.logger.info("Intentando iniciar Docker Desktop...")
        try:
            # En macOS
            import platform
            if platform.system() == "Darwin":
                returncode, _, _ = run_command(
                    ["open", "-a", "Docker"],
                    check=False
                )
                if returncode == 0:
                    self.logger.info("Docker Desktop iniciado. Esperando que esté listo...")
                    # Esperar hasta 60 segundos
                    import time
                    for i in range(30):
                        time.sleep(2)
                        if check_docker_running():
                            self.logger.info("Docker está listo")
                            return True
                        self.logger.debug(f"Esperando Docker... ({i*2} segundos)")
                    self.logger.warning("Docker no respondió en 60 segundos")
                    return False
            else:
                self.logger.warning("Inicio automático de Docker no soportado en este sistema")
                return False
        except Exception as e:
            self.logger.error(f"Error al iniciar Docker: {e}")
            return False
    
    def start_backend(self) -> bool:
        """
        Inicia el backend con make lite-start.
        
        Returns:
            True si se inició correctamente, False en caso contrario
        """
        self.logger.info("Iniciando backend con 'make lite-start'...")
        returncode, stdout, stderr = run_command(
            ["make", "lite-start"],
            cwd=self.project_root,
            check=False,
            capture_output=True
        )
        
        if returncode == 0:
            self.logger.info("Backend iniciado correctamente")
            if stdout:
                self.logger.debug(stdout)
            return True
        else:
            self.logger.error(f"Error al iniciar backend: {stderr}")
            return False
    
    def check_status(self) -> bool:
        """
        Verifica el estado de los servicios con make lite-status.
        
        Returns:
            True si los servicios están funcionando, False en caso contrario
        """
        self.logger.info("Verificando estado de servicios...")
        returncode, stdout, stderr = run_command(
            ["make", "lite-status"],
            cwd=self.project_root,
            check=False,
            capture_output=True
        )
        
        if returncode == 0:
            self.logger.info("Estado de servicios:")
            if stdout:
                # Mostrar solo las líneas importantes
                for line in stdout.split('\n'):
                    if '✅' in line or '❌' in line or 'Status' in line:
                        self.logger.info(line)
            return True
        else:
            self.logger.warning(f"Error al verificar estado: {stderr}")
            return False
    
    def start_frontends(self) -> bool:
        """
        Inicia los frontends con make frontend-all.
        
        Returns:
            True si se inició correctamente, False en caso contrario
        """
        self.logger.info("Iniciando frontends con 'make frontend-all'...")
        returncode, stdout, stderr = run_command(
            ["make", "frontend-all"],
            cwd=self.project_root,
            check=False,
            capture_output=True
        )
        
        if returncode == 0:
            self.logger.info("Frontends iniciados correctamente")
            if stdout:
                self.logger.debug(stdout)
            return True
        else:
            self.logger.warning(f"Error al iniciar frontends: {stderr}")
            return False
    
    def run(self, start_frontends: bool = False) -> bool:
        """
        Ejecuta la secuencia completa de inicio del proyecto.
        
        Args:
            start_frontends: Si es True, también inicia los frontends
            
        Returns:
            True si todo se ejecutó correctamente, False en caso contrario
        """
        self.logger.info("=" * 60)
        self.logger.info("Iniciando proyecto siguiendo INICIO_RAPIDO.md")
        self.logger.info("=" * 60)
        
        # 1. Verificar que existe INICIO_RAPIDO.md
        if not self.verify_inicio_rapido_exists():
            return False
        
        # 2. Verificar/iniciar Docker
        if not self.start_docker():
            self.logger.error("Docker no está disponible. Por favor, inicia Docker Desktop manualmente.")
            return False
        
        # 3. Iniciar backend
        if not self.start_backend():
            return False
        
        # 4. Verificar estado
        if not self.check_status():
            self.logger.warning("Algunos servicios pueden no estar funcionando correctamente")
        
        # 5. Opcionalmente iniciar frontends
        if start_frontends:
            if not self.start_frontends():
                self.logger.warning("Error al iniciar frontends, pero el backend está funcionando")
        
        self.logger.info("=" * 60)
        self.logger.info("Proceso de inicio completado")
        self.logger.info("=" * 60)
        
        return True


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description="Inicia el proyecto siguiendo INICIO_RAPIDO.md"
    )
    parser.add_argument(
        "--frontends",
        action="store_true",
        help="También inicia los frontends"
    )
    
    args = parser.parse_args()
    
    agent = StartProjectAgent()
    success = agent.run(start_frontends=args.frontends)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

