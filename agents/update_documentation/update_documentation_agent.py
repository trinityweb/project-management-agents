#!/usr/bin/env python3
"""Agente para actualizar documentación del proyecto."""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Agregar el directorio shared al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.config_loader import ConfigLoader
from shared.utils import setup_logging, run_command, find_files


class UpdateDocumentationAgent:
    """Agente que actualiza la documentación del proyecto."""
    
    def __init__(self):
        """Inicializa el agente."""
        self.logger = setup_logging()
        self.config = ConfigLoader()
        self.project_root = self.config.get_project_root()
        self.services_dir = self.project_root / "services"
        self.docs_dir = self.project_root / "services" / "saas-mt-docs"
        self.combined_collection_path = self.project_root / "combined-services-postman-collection.json"
    
    def find_postman_collections(self) -> List[Path]:
        """
        Busca todas las collections de Postman en los servicios.
        
        Returns:
            Lista de paths a las collections encontradas
        """
        self.logger.info("Buscando collections de Postman...")
        collections = find_files("*postman*.json", self.services_dir)
        
        # Filtrar solo collections (no environments)
        postman_collections = [
            p for p in collections 
            if "collection" in p.name.lower() and "environment" not in p.name.lower()
        ]
        
        self.logger.info(f"Encontradas {len(postman_collections)} collections:")
        for col in postman_collections:
            self.logger.info(f"  - {col.relative_to(self.project_root)}")
        
        return postman_collections
    
    def validate_postman_collection(self, collection_path: Path) -> bool:
        """
        Valida que un archivo de collection de Postman tenga la estructura correcta.
        
        Args:
            collection_path: Path al archivo de collection
            
        Returns:
            True si es válida, False en caso contrario
        """
        try:
            with open(collection_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validar estructura básica
            if "info" not in data:
                self.logger.error(f"{collection_path.name}: Falta campo 'info'")
                return False
            
            if "item" not in data:
                self.logger.error(f"{collection_path.name}: Falta campo 'item'")
                return False
            
            self.logger.debug(f"{collection_path.name}: Estructura válida")
            return True
        
        except json.JSONDecodeError as e:
            self.logger.error(f"{collection_path.name}: Error de JSON: {e}")
            return False
        except Exception as e:
            self.logger.error(f"{collection_path.name}: Error al validar: {e}")
            return False
    
    def merge_postman_collections(self, collections: List[Path]) -> Dict[str, Any]:
        """
        Combina múltiples collections de Postman en una sola.
        
        Args:
            collections: Lista de paths a las collections
            
        Returns:
            Diccionario con la collection combinada
        """
        self.logger.info("Combinando collections de Postman...")
        
        combined = {
            "info": {
                "name": "SaaS - Microservices API Collection",
                "description": "Colección combinada de todos los endpoints de los servicios",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
                "version": "1.0.0"
            },
            "item": []
        }
        
        for collection_path in collections:
            if not self.validate_postman_collection(collection_path):
                self.logger.warning(f"Omitiendo collection inválida: {collection_path.name}")
                continue
            
            try:
                with open(collection_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                service_name = collection_path.parent.name
                service_item = {
                    "name": service_name,
                    "description": data.get("info", {}).get("description", f"Endpoints de {service_name}"),
                    "item": data.get("item", [])
                }
                
                combined["item"].append(service_item)
                self.logger.info(f"Agregada collection de {service_name}")
            
            except Exception as e:
                self.logger.error(f"Error al procesar {collection_path.name}: {e}")
        
        return combined
    
    def update_postman_collection(self) -> bool:
        """
        Actualiza la collection combinada de Postman.
        
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        self.logger.info("Actualizando collection combinada de Postman...")
        
        collections = self.find_postman_collections()
        if not collections:
            self.logger.warning("No se encontraron collections de Postman")
            return False
        
        combined = self.merge_postman_collections(collections)
        
        try:
            with open(self.combined_collection_path, 'w', encoding='utf-8') as f:
                json.dump(combined, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Collection combinada actualizada: {self.combined_collection_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error al guardar collection combinada: {e}")
            return False
    
    def validate_service_documentation(self, service_path: Path) -> Dict[str, Any]:
        """
        Valida la documentación de un servicio.
        
        Args:
            service_path: Path al directorio del servicio
            
        Returns:
            Diccionario con el resultado de la validación
        """
        service_name = service_path.name
        result = {
            "service": service_name,
            "readme_exists": False,
            "docs_dir_exists": False,
            "postman_collection_exists": False,
            "issues": []
        }
        
        # Verificar README.md
        readme_path = service_path / "README.md"
        if readme_path.exists():
            result["readme_exists"] = True
        else:
            result["issues"].append("README.md no encontrado")
        
        # Verificar directorio de documentación
        docs_dirs = ["docs", "documentation"]
        for docs_dir in docs_dirs:
            if (service_path / docs_dir).exists():
                result["docs_dir_exists"] = True
                break
        
        # Verificar collection de Postman
        postman_collections = find_files("*postman*collection*.json", service_path)
        if postman_collections:
            result["postman_collection_exists"] = True
        
        return result
    
    def validate_all_documentation(self) -> List[Dict[str, Any]]:
        """
        Valida la documentación de todos los servicios.
        
        Returns:
            Lista de resultados de validación
        """
        self.logger.info("Validando documentación de servicios...")
        
        results = []
        if not self.services_dir.exists():
            self.logger.error(f"Directorio de servicios no encontrado: {self.services_dir}")
            return results
        
        for service_path in self.services_dir.iterdir():
            if not service_path.is_dir() or service_path.name.startswith('.'):
                continue
            
            result = self.validate_service_documentation(service_path)
            results.append(result)
            
            if result["issues"]:
                self.logger.warning(f"{result['service']}: {', '.join(result['issues'])}")
            else:
                self.logger.info(f"{result['service']}: Documentación OK")
        
        return results
    
    def sync_docs_frontend(self) -> bool:
        """
        Sincroniza la documentación con el frontend de docs.
        
        Returns:
            True si se sincronizó correctamente, False en caso contrario
        """
        self.logger.info("Sincronizando documentación con frontend...")
        
        sync_script = self.docs_dir / "scripts" / "sync-docs.sh"
        if not sync_script.exists():
            self.logger.error(f"Script de sincronización no encontrado: {sync_script}")
            return False
        
        # Hacer el script ejecutable
        sync_script.chmod(0o755)
        
        returncode, stdout, stderr = run_command(
            [str(sync_script)],
            cwd=self.docs_dir,
            check=False,
            capture_output=True
        )
        
        if returncode == 0:
            self.logger.info("Documentación sincronizada correctamente")
            if stdout:
                self.logger.debug(stdout)
            return True
        else:
            self.logger.error(f"Error al sincronizar documentación: {stderr}")
            return False
    
    def run(self, validate_only: bool = False, update_postman: bool = True,
            update_docs: bool = True, sync_frontend: bool = True) -> bool:
        """
        Ejecuta el proceso de actualización de documentación.
        
        Args:
            validate_only: Solo validar, no actualizar
            update_postman: Actualizar collection de Postman
            update_docs: Validar documentación de servicios
            sync_frontend: Sincronizar frontend de docs
            
        Returns:
            True si todo se ejecutó correctamente, False en caso contrario
        """
        self.logger.info("=" * 60)
        self.logger.info("Actualizando documentación del proyecto")
        self.logger.info("=" * 60)
        
        success = True
        
        # 1. Actualizar collection de Postman
        if update_postman and not validate_only:
            if not self.update_postman_collection():
                success = False
        
        # 2. Validar documentación de servicios
        if update_docs:
            results = self.validate_all_documentation()
            issues_count = sum(len(r["issues"]) for r in results)
            if issues_count > 0:
                self.logger.warning(f"Se encontraron {issues_count} problemas en la documentación")
                if validate_only:
                    success = False
        
        # 3. Sincronizar frontend de docs
        if sync_frontend and not validate_only:
            if not self.sync_docs_frontend():
                success = False
        
        self.logger.info("=" * 60)
        self.logger.info("Proceso de actualización de documentación completado")
        self.logger.info("=" * 60)
        
        return success


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description="Actualiza la documentación del proyecto"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Solo validar, no actualizar"
    )
    parser.add_argument(
        "--update-postman",
        action="store_true",
        default=True,
        help="Actualizar collection de Postman (por defecto: True)"
    )
    parser.add_argument(
        "--no-update-postman",
        dest="update_postman",
        action="store_false",
        help="No actualizar collection de Postman"
    )
    parser.add_argument(
        "--update-docs",
        action="store_true",
        default=True,
        help="Validar documentación de servicios (por defecto: True)"
    )
    parser.add_argument(
        "--no-update-docs",
        dest="update_docs",
        action="store_false",
        help="No validar documentación de servicios"
    )
    parser.add_argument(
        "--sync-frontend",
        action="store_true",
        default=True,
        help="Sincronizar frontend de docs (por defecto: True)"
    )
    parser.add_argument(
        "--no-sync-frontend",
        dest="sync_frontend",
        action="store_false",
        help="No sincronizar frontend de docs"
    )
    
    args = parser.parse_args()
    
    agent = UpdateDocumentationAgent()
    success = agent.run(
        validate_only=args.validate_only,
        update_postman=args.update_postman,
        update_docs=args.update_docs,
        sync_frontend=args.sync_frontend
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

