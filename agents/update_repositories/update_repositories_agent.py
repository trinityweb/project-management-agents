#!/usr/bin/env python3
"""Agente para actualizar repositorios Git."""

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from git import Repo, GitCommandError
    from git.exc import InvalidGitRepositoryError
except ImportError:
    print("Error: gitpython no está instalado. Ejecuta: pip install gitpython")
    sys.exit(1)

# Agregar el directorio shared al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.config_loader import ConfigLoader
from shared.github_client import GitHubClient
from shared.utils import setup_logging


class UpdateRepositoriesAgent:
    """Agente que actualiza repositorios Git."""
    
    def __init__(self):
        """Inicializa el agente."""
        self.logger = setup_logging()
        self.config = ConfigLoader()
        self.project_root = self.config.get_project_root()
        
        # GitHub client es opcional - solo se usa para detectar repos desde la API
        # Las operaciones Git (pull/push) usan la configuración local de Git
        self.github_client = None
        try:
            github_token = self.config.get_github_token()
            self.github_client = GitHubClient(github_token)
            self.logger.debug("GitHub token configurado - detección automática de repos habilitada")
        except ValueError:
            self.logger.info("GitHub token no configurado - usando solo configuración local de Git")
        
        try:
            self.github_config = self.config.load_github_config()
        except FileNotFoundError:
            self.logger.info("Configuración de GitHub no encontrada - usando detección desde repositorios locales")
            self.github_config = None
    
    def get_repositories_list(self) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de repositorios a actualizar.
        Prioriza configuración local, luego archivo de config, luego detección automática.
        
        Returns:
            Lista de diccionarios con información de repositorios
        """
        repos = []
        
        # 1. Prioridad: Usar configuración de archivo si existe
        if self.github_config:
            org_name = self.github_config.get("organization", "trinityweb")
            repo_names = self.github_config.get("repositories", [])
            local_paths = self.github_config.get("local_paths", {})
            
            for repo_name in repo_names:
                local_path = local_paths.get(repo_name)
                if not local_path:
                    # Intentar detectar automáticamente en subdirectorios comunes
                    for base_path in [self.project_root.parent, self.project_root]:
                        potential_paths = [
                            base_path / repo_name,
                            base_path / "services" / repo_name,
                            base_path / "mcp" / repo_name,
                        ]
                        for potential_path in potential_paths:
                            if potential_path.exists() and (potential_path / ".git").exists():
                                local_path = potential_path
                                break
                        if local_path:
                            break
                
                if local_path:
                    repos.append({
                        "name": repo_name,
                        "org": org_name,
                        "local_path": Path(local_path) if isinstance(local_path, str) else local_path
                    })
        
        # 2. Si no hay config o está vacía, detectar repositorios Git locales
        if not repos:
            self.logger.info("Detectando repositorios Git locales...")
            repos = self._detect_local_git_repos()
        
        # 3. Agregar el repositorio agents/project-management-agents si existe
        agents_repo_path = self.project_root / "agents" / "project-management-agents"
        if (agents_repo_path / ".git").exists():
            # Verificar que no esté ya en la lista
            if not any(r["local_path"] == agents_repo_path for r in repos):
                try:
                    repo = Repo(agents_repo_path)
                    repo_name = "project-management-agents"
                    
                    # Intentar obtener nombre del remoto si existe
                    if repo.remotes:
                        try:
                            remote_url = repo.remotes.origin.url
                            if "github.com" in remote_url:
                                parts = remote_url.replace(".git", "").split("/")
                                if len(parts) >= 2:
                                    repo_name = parts[-1]
                        except Exception:
                            pass
                    
                    repos.append({
                        "name": repo_name,
                        "org": "trinityweb",
                        "local_path": agents_repo_path
                    })
                    self.logger.info(f"Repositorio agents agregado: {repo_name}")
                except Exception as e:
                    self.logger.debug(f"No se pudo agregar repositorio agents: {e}")
        
        # 3. Si hay GitHub client, intentar complementar con repos de la organización
        if self.github_client and not repos:
            try:
                org_name = "trinityweb"
                github_repos = self.github_client.get_organization_repos(org_name)
                for repo_info in github_repos:
                    # Buscar el repositorio local
                    local_path = None
                    for base_path in [self.project_root.parent, self.project_root]:
                        potential_paths = [
                            base_path / repo_info["name"],
                            base_path / "services" / repo_info["name"],
                            base_path / "mcp" / repo_info["name"],
                        ]
                        for potential_path in potential_paths:
                            if potential_path.exists() and (potential_path / ".git").exists():
                                local_path = potential_path
                                break
                        if local_path:
                            break
                    
                    if local_path:
                        repos.append({
                            "name": repo_info["name"],
                            "org": org_name,
                            "local_path": local_path
                        })
            except Exception as e:
                self.logger.debug(f"No se pudieron obtener repositorios de GitHub API: {e}")
        
        return repos
    
    def _detect_local_git_repos(self) -> List[Dict[str, Any]]:
        """
        Detecta repositorios Git locales buscando directorios con .git.
        Solo busca en services/, mcp/ y agents/ dentro del proyecto.
        
        Returns:
            Lista de diccionarios con información de repositorios detectados
        """
        repos = []
        
        # Buscar SOLO en directorios específicos dentro del proyecto
        search_dirs = [
            self.project_root / "services",
            self.project_root / "mcp",
            self.project_root / "agents",
        ]
        
        for search_dir in search_dirs:
            if not search_dir.exists():
                self.logger.debug(f"Directorio no existe: {search_dir}")
                continue
            
            self.logger.debug(f"Buscando repositorios en: {search_dir}")
            
            # Buscar directorios con .git
            for item in search_dir.iterdir():
                if not item.is_dir() or item.name.startswith('.'):
                    continue
                
                git_dir = item / ".git"
                if git_dir.exists():
                    # Intentar obtener información del remoto
                    try:
                        repo = Repo(item)
                        if repo.remotes:
                            remote_url = repo.remotes.origin.url
                            # Extraer nombre del repo desde la URL
                            repo_name = item.name
                            if "github.com" in remote_url:
                                # Intentar extraer org/repo de la URL
                                parts = remote_url.replace(".git", "").split("/")
                                if len(parts) >= 2:
                                    repo_name = parts[-1]
                            
                            repos.append({
                                "name": repo_name,
                                "org": "trinityweb",  # Asumimos por defecto
                                "local_path": item
                            })
                            self.logger.info(f"Repositorio detectado: {repo_name} en {item}")
                    except Exception as e:
                        self.logger.debug(f"No se pudo leer info de {item}: {e}")
        
        return repos
    
    def get_repo_status(self, repo_path: Path) -> Dict[str, Any]:
        """
        Obtiene el estado de un repositorio Git.
        
        Args:
            repo_path: Path al repositorio local
            
        Returns:
            Diccionario con el estado del repositorio
        """
        try:
            repo = Repo(repo_path)
        except InvalidGitRepositoryError:
            return {
                "valid": False,
                "error": "No es un repositorio Git válido"
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
        
        # Verificar si el repositorio está sucio de forma segura
        is_dirty = False
        untracked_count = 0
        try:
            is_dirty = repo.is_dirty()
            untracked_count = len(repo.untracked_files)
        except Exception as e:
            # Si hay un error (por ejemplo, alias de Git que no soporta --cached)
            # Intentar método alternativo
            self.logger.debug(f"Error al verificar estado con is_dirty: {e}")
            try:
                # Usar git status directamente
                status_output = repo.git.status("--porcelain")
                is_dirty = len(status_output.strip()) > 0
                untracked_count = len([line for line in status_output.split('\n') if line.startswith('??')])
            except Exception as e2:
                self.logger.warning(f"No se pudo determinar estado del repositorio: {e2}")
        
        try:
            branch_name = repo.active_branch.name
        except Exception as e:
            self.logger.warning(f"No se pudo obtener branch activo: {e}")
            branch_name = "unknown"
        
        status = {
            "valid": True,
            "path": str(repo_path),
            "branch": branch_name,
            "is_dirty": is_dirty,
            "untracked_files": untracked_count,
            "ahead": 0,
            "behind": 0,
            "has_conflicts": False
        }
        
        try:
            # Obtener información de commits ahead/behind
            if repo.remotes:
                remote = repo.remotes.origin
                try:
                    remote.fetch()
                except Exception as e:
                    self.logger.debug(f"Error al hacer fetch: {e}")
                
                try:
                    # Verificar si el branch remoto existe
                    remote_branch = f"origin/{status['branch']}"
                    # Commits locales que no están en remoto (ahead)
                    commits_ahead = list(repo.iter_commits(f"{remote_branch}..{status['branch']}"))
                    # Commits remotos que no están en local (behind)
                    commits_behind = list(repo.iter_commits(f"{status['branch']}..{remote_branch}"))
                    status["ahead"] = len(commits_ahead)
                    status["behind"] = len(commits_behind)
                except Exception as e:
                    self.logger.debug(f"Error al calcular ahead/behind: {e}")
        except Exception as e:
            self.logger.debug(f"Error al obtener información de remotes: {e}")
        
        # Verificar conflictos de forma segura
        if is_dirty:
            try:
                for item in repo.index.diff(None):
                    if '<<<<<<<' in str(item) or '>>>>>>>' in str(item):
                        status["has_conflicts"] = True
                        break
            except Exception as e:
                self.logger.debug(f"Error al verificar conflictos: {e}")
        
        return status
    
    def commit_changes(self, repo_path: Path, dry_run: bool = False, message: str = None) -> bool:
        """
        Hace commit de cambios locales en un repositorio.
        
        Args:
            repo_path: Path al repositorio local
            dry_run: Si es True, solo simula la operación
            message: Mensaje de commit (si es None, usa mensaje por defecto)
            
        Returns:
            True si se hizo commit correctamente, False en caso contrario
        """
        try:
            repo = Repo(repo_path)
        except InvalidGitRepositoryError:
            self.logger.error(f"{repo_path.name}: No es un repositorio Git válido")
            return False
        
        # Verificar si hay cambios para commitear
        try:
            # Obtener archivos modificados y sin seguimiento
            modified_files = [item.a_path for item in repo.index.diff(None)]
            untracked_files = repo.untracked_files
            
            if not modified_files and not untracked_files:
                self.logger.info(f"{repo_path.name}: No hay cambios para commitear")
                return True
        except Exception as e:
            self.logger.debug(f"Error al verificar cambios: {e}")
            # Intentar método alternativo
            try:
                status_output = repo.git.status("--porcelain")
                if not status_output.strip():
                    self.logger.info(f"{repo_path.name}: No hay cambios para commitear")
                    return True
            except Exception as e2:
                self.logger.error(f"{repo_path.name}: Error al verificar cambios: {e2}")
                return False
        
        if dry_run:
            self.logger.info(f"{repo_path.name}: [DRY RUN] Hacer commit de cambios locales")
            return True
        
        try:
            # Agregar todos los cambios (Git respetará automáticamente .gitignore)
            self.logger.info(f"{repo_path.name}: Agregando cambios al staging...")
            repo.git.add(A=True)
            
            # Verificar que hay algo para commitear después de agregar
            # Si es el primer commit, no habrá HEAD
            try:
                has_staged = len(repo.index.diff("HEAD")) > 0 if repo.heads else True
                has_untracked = len(repo.untracked_files) > 0
                if not has_staged and not has_untracked:
                    self.logger.info(f"{repo_path.name}: No hay cambios para commitear (todos ignorados por .gitignore)")
                    return True
            except Exception:
                # Si no hay HEAD (primer commit), verificar staged directamente
                try:
                    staged_files = repo.git.diff("--cached", "--name-only")
                    if not staged_files.strip() and not repo.untracked_files:
                        self.logger.info(f"{repo_path.name}: No hay cambios para commitear")
                        return True
                except Exception:
                    # Si falla, intentar commit de todas formas
                    pass
            
            # Crear mensaje de commit
            if not message:
                message = f"chore: Actualización automática de archivos\n\nActualizado por agente de gestión de proyecto"
            
            # Hacer commit
            self.logger.info(f"{repo_path.name}: Haciendo commit...")
            repo.index.commit(message)
            self.logger.info(f"{repo_path.name}: Commit completado")
            return True
        
        except GitCommandError as e:
            self.logger.error(f"{repo_path.name}: Error al hacer commit: {e}")
            return False
        except Exception as e:
            self.logger.error(f"{repo_path.name}: Error inesperado al hacer commit: {e}")
            return False
    
    def initialize_repo(self, repo_path: Path, remote_url: str = None, dry_run: bool = False) -> bool:
        """
        Inicializa un repositorio Git si no existe.
        
        Args:
            repo_path: Path al directorio
            remote_url: URL del repositorio remoto (opcional)
            dry_run: Si es True, solo simula la operación
            
        Returns:
            True si se inicializó correctamente, False en caso contrario
        """
        git_dir = repo_path / ".git"
        if git_dir.exists():
            self.logger.debug(f"{repo_path.name}: Ya es un repositorio Git")
            return True
        
        if dry_run:
            self.logger.info(f"{repo_path.name}: [DRY RUN] Inicializar repositorio Git")
            return True
        
        try:
            self.logger.info(f"{repo_path.name}: Inicializando repositorio Git...")
            repo = Repo.init(repo_path)
            
            # Configurar remoto si se proporciona
            if remote_url:
                try:
                    repo.create_remote('origin', remote_url)
                    self.logger.info(f"{repo_path.name}: Remoto 'origin' configurado: {remote_url}")
                except Exception as e:
                    self.logger.warning(f"{repo_path.name}: No se pudo configurar remoto: {e}")
            
            self.logger.info(f"{repo_path.name}: Repositorio Git inicializado")
            return True
        
        except Exception as e:
            self.logger.error(f"{repo_path.name}: Error al inicializar repositorio: {e}")
            return False
    
    def create_github_repo_with_gh_cli(self, repo_name: str, org_name: str = "trinityweb",
                                       description: str = "", private: bool = False,
                                       dry_run: bool = False) -> Dict[str, Any]:
        """
        Crea un repositorio en GitHub usando GitHub CLI (gh) que usa la misma autenticación que Git.
        
        Args:
            repo_name: Nombre del repositorio
            org_name: Nombre de la organización
            description: Descripción del repositorio
            private: Si el repositorio es privado
            dry_run: Si es True, solo simula la operación
            
        Returns:
            Diccionario con información del repositorio creado o None si falla
        """
        if dry_run:
            self.logger.info(f"[DRY RUN] Crear repositorio {org_name}/{repo_name} con gh CLI")
            return {
                "name": repo_name,
                "full_name": f"{org_name}/{repo_name}",
                "url": f"https://github.com/{org_name}/{repo_name}",
                "clone_url": f"https://github.com/{org_name}/{repo_name}.git"
            }
        
        try:
            # Verificar si gh está instalado
            from shared.utils import run_command
            returncode, _, _ = run_command(["gh", "--version"], check=False, capture_output=True)
            if returncode != 0:
                self.logger.debug("GitHub CLI (gh) no está instalado")
                return None
            
            # Verificar si el repositorio ya existe
            returncode, stdout, stderr = run_command(
                ["gh", "repo", "view", f"{org_name}/{repo_name}"],
                check=False,
                capture_output=True
            )
            if returncode == 0:
                # El repositorio ya existe
                self.logger.info(f"Repositorio {repo_name} ya existe en GitHub")
                return {
                    "name": repo_name,
                    "full_name": f"{org_name}/{repo_name}",
                    "url": f"https://github.com/{org_name}/{repo_name}",
                    "clone_url": f"https://github.com/{org_name}/{repo_name}.git"
                }
            
            # Crear el repositorio
            # Necesitamos ejecutar desde el directorio del repositorio
            agents_dir = self.project_root / "agents" / "project-management-agents"
            if not agents_dir.exists():
                self.logger.debug(f"Directorio del repositorio no existe: {agents_dir}")
                return None
            
            self.logger.info(f"Creando repositorio {repo_name} en GitHub usando gh CLI...")
            # Usar --public o --private según la versión de gh
            visibility_flag = "--private" if private else "--public"
            cmd = [
                "gh", "repo", "create", f"{org_name}/{repo_name}",
                "--description", description or f"Repositorio {repo_name}",
                visibility_flag,
                "--source", ".",
                "--remote", "origin",  # Configurar como remoto origin
                "--push"  # Hacer push del contenido
            ]
            
            # Ejecutar desde el directorio del repositorio
            returncode, stdout, stderr = run_command(
                cmd, 
                cwd=str(agents_dir),  # Convertir Path a string
                check=False, 
                capture_output=True
            )
            if returncode == 0:
                self.logger.info(f"✅ Repositorio {repo_name} creado en GitHub y contenido subido")
                return {
                    "name": repo_name,
                    "full_name": f"{org_name}/{repo_name}",
                    "url": f"https://github.com/{org_name}/{repo_name}",
                    "clone_url": f"https://github.com/{org_name}/{repo_name}.git"
                }
            else:
                # Si falla con --push, intentar sin push
                self.logger.debug(f"Error al crear con push (código {returncode}): {stderr}")
                cmd_no_push = [
                    "gh", "repo", "create", f"{org_name}/{repo_name}",
                    "--description", description or f"Repositorio {repo_name}",
                    visibility_flag,
                    "--source", ".",
                    "--remote", "origin"
                ]
                returncode2, stdout2, stderr2 = run_command(
                    cmd_no_push,
                    cwd=str(agents_dir),
                    check=False,
                    capture_output=True
                )
                if returncode2 == 0:
                    self.logger.info(f"✅ Repositorio {repo_name} creado en GitHub (sin push inicial)")
                    return {
                        "name": repo_name,
                        "full_name": f"{org_name}/{repo_name}",
                        "url": f"https://github.com/{org_name}/{repo_name}",
                        "clone_url": f"https://github.com/{org_name}/{repo_name}.git"
                    }
                else:
                    self.logger.warning(f"Error al crear con gh CLI (código {returncode2}): {stderr2}")
                    return None
        
        except Exception as e:
            self.logger.debug(f"Error al usar gh CLI: {e}")
            import traceback
            self.logger.debug(traceback.format_exc())
            return None
    
    def create_github_repo(self, repo_name: str, org_name: str = "trinityweb", 
                          description: str = "", private: bool = False,
                          dry_run: bool = False) -> Dict[str, Any]:
        """
        Crea un repositorio en GitHub si no existe.
        Intenta usar GitHub CLI primero (usa la misma autenticación que Git),
        luego intenta con la API si hay token configurado.
        
        Args:
            repo_name: Nombre del repositorio
            org_name: Nombre de la organización
            description: Descripción del repositorio
            private: Si el repositorio es privado
            dry_run: Si es True, solo simula la operación
            
        Returns:
            Diccionario con información del repositorio creado o None si falla
        """
        # 1. Intentar con GitHub CLI (usa la misma autenticación que Git)
        repo_info = self.create_github_repo_with_gh_cli(
            repo_name=repo_name,
            org_name=org_name,
            description=description,
            private=private,
            dry_run=dry_run
        )
        if repo_info:
            return repo_info
        
        # 2. Si gh CLI no está disponible, intentar con API (requiere token)
        if not self.github_client:
            self.logger.info("GitHub CLI no disponible y GitHub client no configurado")
            self.logger.info("El repositorio local se puede usar normalmente, solo no estará en GitHub")
            self.logger.info("Para crear en GitHub:")
            self.logger.info("  - Instala GitHub CLI: brew install gh (macOS) o https://cli.github.com/")
            self.logger.info("  - O configura GITHUB_TOKEN en .env")
            return None
        
        try:
            # Verificar si el repositorio ya existe
            try:
                repo_info = self.github_client.get_repo_info(repo_name, org_name)
                self.logger.info(f"Repositorio {repo_name} ya existe en GitHub: {repo_info['url']}")
                return repo_info
            except Exception as e:
                # El repositorio no existe, intentar crearlo
                self.logger.debug(f"Repositorio no encontrado en GitHub: {e}")
            
            if dry_run:
                self.logger.info(f"[DRY RUN] Crear repositorio {org_name}/{repo_name} con GitHub API")
                return {
                    "name": repo_name,
                    "full_name": f"{org_name}/{repo_name}",
                    "url": f"https://github.com/{org_name}/{repo_name}",
                    "clone_url": f"https://github.com/{org_name}/{repo_name}.git"
                }
            
            self.logger.info(f"Creando repositorio {repo_name} en GitHub usando API...")
            repo_info = self.github_client.create_repo(
                name=repo_name,
                org_name=org_name,
                description=description,
                private=private
            )
            self.logger.info(f"✅ Repositorio {repo_name} creado en GitHub: {repo_info['url']}")
            return repo_info
        
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "Bad credentials" in error_msg:
                self.logger.warning(f"⚠️  No se pudo crear repositorio en GitHub: Token inválido o no configurado")
                self.logger.info("   El repositorio local funciona normalmente. Para crear en GitHub:")
                self.logger.info("   1. Instala GitHub CLI: brew install gh (usa tu autenticación Git)")
                self.logger.info("   2. O configura GITHUB_TOKEN en .env")
            elif "403" in error_msg or "Forbidden" in error_msg:
                self.logger.warning(f"⚠️  No se pudo crear repositorio en GitHub: Permisos insuficientes")
                self.logger.info("   Verifica que el token tenga permisos 'repo' y 'write:org'")
            else:
                self.logger.warning(f"⚠️  Error al crear repositorio en GitHub: {error_msg}")
            return None
    
    def pull_repository(self, repo_path: Path, dry_run: bool = False) -> bool:
        """
        Hace pull de un repositorio.
        
        Args:
            repo_path: Path al repositorio local
            dry_run: Si es True, solo simula la operación
            
        Returns:
            True si se hizo pull correctamente, False en caso contrario
        """
        try:
            repo = Repo(repo_path)
        except InvalidGitRepositoryError:
            self.logger.error(f"{repo_path.name}: No es un repositorio Git válido")
            return False
        
        if dry_run:
            self.logger.info(f"{repo_path.name}: [DRY RUN] Hacer pull")
            return True
        
        try:
            # Verificar si hay cambios locales sin commit
            if repo.is_dirty():
                self.logger.warning(f"{repo_path.name}: Hay cambios locales sin commit")
                return False
            
            # Hacer pull
            self.logger.info(f"{repo_path.name}: Haciendo pull...")
            origin = repo.remotes.origin
            origin.pull()
            self.logger.info(f"{repo_path.name}: Pull completado")
            return True
        
        except GitCommandError as e:
            if "conflict" in str(e).lower() or "merge" in str(e).lower():
                self.logger.error(f"{repo_path.name}: Conflicto de merge detectado")
                return False
            self.logger.error(f"{repo_path.name}: Error al hacer pull: {e}")
            return False
        except Exception as e:
            self.logger.error(f"{repo_path.name}: Error inesperado: {e}")
            return False
    
    def push_repository(self, repo_path: Path, dry_run: bool = False) -> bool:
        """
        Hace push de un repositorio.
        
        Args:
            repo_path: Path al repositorio local
            dry_run: Si es True, solo simula la operación
            
        Returns:
            True si se hizo push correctamente, False en caso contrario
        """
        try:
            repo = Repo(repo_path)
        except InvalidGitRepositoryError:
            self.logger.error(f"{repo_path.name}: No es un repositorio Git válido")
            return False
        
        status = self.get_repo_status(repo_path)
        if status["ahead"] == 0:
            self.logger.info(f"{repo_path.name}: No hay commits para hacer push")
            return True
        
        if dry_run:
            self.logger.info(f"{repo_path.name}: [DRY RUN] Hacer push ({status['ahead']} commits)")
            return True
        
        try:
            self.logger.info(f"{repo_path.name}: Haciendo push ({status['ahead']} commits)...")
            origin = repo.remotes.origin
            origin.push()
            self.logger.info(f"{repo_path.name}: Push completado")
            return True
        
        except GitCommandError as e:
            self.logger.error(f"{repo_path.name}: Error al hacer push: {e}")
            return False
        except Exception as e:
            self.logger.error(f"{repo_path.name}: Error inesperado: {e}")
            return False
    
    def handle_conflicts(self, repo_path: Path) -> bool:
        """
        Detecta y reporta conflictos en un repositorio.
        
        Args:
            repo_path: Path al repositorio local
            
        Returns:
            True si no hay conflictos, False si hay conflictos que requieren resolución manual
        """
        status = self.get_repo_status(repo_path)
        
        if status.get("has_conflicts"):
            self.logger.error(f"{repo_path.name}: CONFLICTOS DETECTADOS - Requiere resolución manual")
            self.logger.error(f"  Path: {status['path']}")
            self.logger.error(f"  Branch: {status['branch']}")
            return False
        
        return True
    
    def update_repository(self, repo_info: Dict[str, Any], auto_commit: bool = False,
                         dry_run: bool = False) -> Dict[str, Any]:
        """
        Actualiza un repositorio (pull y push).
        
        Args:
            repo_info: Información del repositorio
            auto_commit: Si es True, hace commit automático de cambios locales
            dry_run: Si es True, solo simula las operaciones
            
        Returns:
            Diccionario con el resultado de la actualización
        """
        repo_name = repo_info["name"]
        repo_path = repo_info["local_path"]
        
        result = {
            "name": repo_name,
            "path": str(repo_path),
            "success": False,
            "pulled": False,
            "pushed": False,
            "committed": False,
            "has_conflicts": False,
            "errors": []
        }
        
        if not repo_path.exists():
            result["errors"].append(f"Directorio no existe: {repo_path}")
            self.logger.warning(f"{repo_name}: Directorio no existe: {repo_path}")
            return result
        
        # Verificar estado
        try:
            status = self.get_repo_status(repo_path)
        except Exception as e:
            result["errors"].append(f"Error al obtener estado: {e}")
            self.logger.error(f"{repo_name}: Error al obtener estado: {e}")
            return result
        
        if not status.get("valid"):
            result["errors"].append(status.get("error", "Repositorio inválido"))
            return result
        
        # Verificar conflictos
        if not self.handle_conflicts(repo_path):
            result["has_conflicts"] = True
            result["errors"].append("Conflictos detectados - requiere resolución manual")
            return result
        
        # Hacer commit de cambios locales si está habilitado
        if auto_commit:
            # Verificar cambios de forma más robusta
            try:
                repo = Repo(repo_path)
                status_output = repo.git.status("--porcelain")
                has_changes = len(status_output.strip()) > 0
            except Exception as e:
                self.logger.debug(f"Error al verificar cambios: {e}")
                has_changes = status.get("is_dirty", False) or status.get("untracked_files", 0) > 0
            
            if has_changes:
                self.logger.info(f"{repo_name}: Haciendo commit automático de cambios locales...")
                if self.commit_changes(repo_path, dry_run=dry_run):
                    result["committed"] = True
                    # Actualizar estado después del commit
                    status = self.get_repo_status(repo_path)
                else:
                    result["errors"].append("Error al hacer commit automático")
                    # Continuar aunque falle el commit
            else:
                self.logger.debug(f"{repo_name}: No hay cambios para commitear")
        
        # Hacer pull si hay cambios remotos
        behind = status.get("behind", 0)
        if behind > 0:
            self.logger.info(f"{repo_name}: {behind} commits detrás del remoto - haciendo pull...")
            if self.pull_repository(repo_path, dry_run=dry_run):
                result["pulled"] = True
                self.logger.info(f"{repo_name}: Pull completado")
            else:
                result["errors"].append("Error al hacer pull")
                # Continuar aunque falle el pull
        else:
            self.logger.info(f"{repo_name}: Ya está actualizado con el remoto (0 commits detrás)")
        
        # Hacer push si hay commits locales
        ahead = status.get("ahead", 0)
        if ahead > 0:
            self.logger.info(f"{repo_name}: {ahead} commits por delante del remoto - haciendo push...")
            if self.push_repository(repo_path, dry_run=dry_run):
                result["pushed"] = True
                self.logger.info(f"{repo_name}: Push completado")
            else:
                result["errors"].append("Error al hacer push")
                # Continuar aunque falle el push
        else:
            self.logger.info(f"{repo_name}: No hay commits locales para hacer push (0 commits por delante)")
        
        # Informar sobre archivos modificados sin commit
        if status.get("is_dirty", False) and not auto_commit:
            self.logger.info(f"{repo_name}: Tiene {status.get('untracked_files', 0)} archivos sin seguimiento y cambios sin commit")
            self.logger.info(f"{repo_name}: Usa --auto-commit para hacer commit automático")
        
        # Considerar éxito si no hay errores críticos
        if not result["errors"] or (result["pulled"] or result["pushed"]):
            result["success"] = True
        
        return result
    
    def ensure_agents_repo_exists(self, dry_run: bool = False) -> bool:
        """
        Asegura que el repositorio agents/project-management-agents existe en GitHub.
        
        Args:
            dry_run: Si es True, solo simula la operación
            
        Returns:
            True si el repositorio existe o se creó, False en caso contrario
        """
        agents_dir = self.project_root / "agents" / "project-management-agents"
        repo_name = "project-management-agents"
        
        # Verificar si es un repositorio Git
        if not (agents_dir / ".git").exists():
            self.logger.info(f"Inicializando repositorio Git en {agents_dir}...")
            if not self.initialize_repo(agents_dir, dry_run=dry_run):
                return False
        
        # Verificar si el remoto ya está configurado
        repo = Repo(agents_dir)
        remote_configured = False
        org_name = "trinityweb"
        try:
            if "origin" in [r.name for r in repo.remotes]:
                origin = repo.remote("origin")
                remote_urls = list(origin.urls) if origin.urls else []
                if remote_urls:
                    remote_url = remote_urls[0]
                    # Verificar si el remoto apunta al repositorio correcto
                    if remote_url and (f"{org_name}/{repo_name}" in remote_url or repo_name in remote_url):
                        self.logger.info(f"Remoto 'origin' ya está configurado: {remote_url}")
                        remote_configured = True
                        return True  # Ya está todo configurado, no necesitamos crear nada
        except Exception as e:
            self.logger.debug(f"Error al verificar remoto: {e}")
        
        # Crear repositorio en GitHub solo si el remoto no está configurado
        if not remote_configured:
            repo_info = self.create_github_repo(
                repo_name=repo_name,
                org_name="trinityweb",
                description="Agentes de AI para gestión automatizada del proyecto SaaS Multi-Tenant",
                private=False,
                dry_run=dry_run
            )
            
            if repo_info and not dry_run:
                # Configurar remoto si no existe
                try:
                    if not repo.remotes:
                        repo.create_remote('origin', repo_info['clone_url'])
                        self.logger.info(f"✅ Remoto 'origin' configurado: {repo_info['clone_url']}")
                    elif repo.remotes.origin.url != repo_info['clone_url']:
                        self.logger.info(f"Actualizando remoto 'origin' a: {repo_info['clone_url']}")
                        repo.remotes.origin.set_url(repo_info['clone_url'])
                except Exception as e:
                    self.logger.warning(f"Error al configurar remoto: {e}")
        elif not repo_info and not dry_run:
            self.logger.info("ℹ️  El repositorio local está listo. Puedes configurarlo manualmente:")
            self.logger.info("   git remote add origin https://github.com/trinityweb/project-management-agents.git")
        
        return True
    
    def run(self, repo_name: Optional[str] = None, auto_commit: bool = False,
            dry_run: bool = False, ensure_agents_repo: bool = True) -> bool:
        """
        Ejecuta el proceso de actualización de repositorios.
        
        Args:
            repo_name: Nombre del repositorio específico a actualizar (None para todos)
            auto_commit: Si es True, hace commit automático de cambios locales
            dry_run: Si es True, solo simula las operaciones
            ensure_agents_repo: Si es True, verifica/crea el repositorio agents
            
        Returns:
            True si todo se ejecutó correctamente, False en caso contrario
        """
        self.logger.info("=" * 60)
        self.logger.info("Actualizando repositorios")
        if dry_run:
            self.logger.info("MODO DRY RUN - No se realizarán cambios")
        if auto_commit:
            self.logger.info("AUTO-COMMIT habilitado - se harán commits automáticos")
        self.logger.info("=" * 60)
        
        # Asegurar que el repositorio agents existe
        if ensure_agents_repo:
            self.logger.info("\nVerificando repositorio agents/project-management-agents...")
            self.ensure_agents_repo_exists(dry_run=dry_run)
            self.logger.info("")
        
        repos = self.get_repositories_list()
        
        if not repos:
            self.logger.warning("No se encontraron repositorios para actualizar")
            return False
        
        # Filtrar por nombre si se especificó
        if repo_name:
            repos = [r for r in repos if r["name"] == repo_name]
            if not repos:
                self.logger.error(f"Repositorio no encontrado: {repo_name}")
                return False
        
        results = []
        for repo_info in repos:
            self.logger.info(f"\nProcesando: {repo_info['name']}")
            try:
                result = self.update_repository(repo_info, auto_commit=auto_commit, dry_run=dry_run)
                results.append(result)
                
                if result["success"]:
                    actions = []
                    if result.get("committed"):
                        actions.append("commit")
                    if result.get("pulled"):
                        actions.append("pull")
                    if result.get("pushed"):
                        actions.append("push")
                    action_str = f" ({', '.join(actions)})" if actions else ""
                    self.logger.info(f"✅ {result['name']}: Actualizado correctamente{action_str}")
                else:
                    error_msg = '; '.join(result['errors']) if result['errors'] else "Sin cambios"
                    self.logger.warning(f"⚠️  {result['name']}: {error_msg}")
            except Exception as e:
                self.logger.error(f"❌ {repo_info['name']}: Error inesperado: {e}")
                results.append({
                    "name": repo_info['name'],
                    "success": False,
                    "errors": [str(e)]
                })
        
        # Resumen
        self.logger.info("\n" + "=" * 60)
        self.logger.info("Resumen:")
        successful = sum(1 for r in results if r["success"])
        conflicts = sum(1 for r in results if r["has_conflicts"])
        self.logger.info(f"  Exitosos: {successful}/{len(results)}")
        if conflicts > 0:
            self.logger.warning(f"  Con conflictos: {conflicts}")
        self.logger.info("=" * 60)
        
        return successful == len(results)


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description="Actualiza repositorios Git (pull y push)"
    )
    parser.add_argument(
        "--repo",
        type=str,
        help="Nombre del repositorio específico a actualizar"
    )
    parser.add_argument(
        "--auto-commit",
        action="store_true",
        help="Hacer commit automático de cambios locales"
    )
    parser.add_argument(
        "--no-ensure-agents-repo",
        dest="ensure_agents_repo",
        action="store_false",
        help="No verificar/crear repositorio agents/project-management-agents"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo simular operaciones, no hacer cambios reales"
    )
    
    args = parser.parse_args()
    
    agent = UpdateRepositoriesAgent()
    success = agent.run(
        repo_name=args.repo,
        auto_commit=args.auto_commit,
        dry_run=args.dry_run,
        ensure_agents_repo=getattr(args, 'ensure_agents_repo', True)
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

