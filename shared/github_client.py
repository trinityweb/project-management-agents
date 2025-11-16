"""Cliente para interactuar con la API de GitHub."""

import os
from typing import List, Dict, Any, Optional
from github import Github
from github.GithubException import GithubException


class GitHubClient:
    """Cliente para interactuar con la API de GitHub."""
    
    def __init__(self, token: str):
        """
        Inicializa el cliente de GitHub.
        
        Args:
            token: Personal Access Token de GitHub
        """
        self.github = Github(token)
        self.token = token
    
    def get_organization_repos(self, org_name: str) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de repositorios de una organización.
        
        Args:
            org_name: Nombre de la organización
            
        Returns:
            Lista de diccionarios con información de los repositorios
        """
        try:
            org = self.github.get_organization(org_name)
            repos = []
            for repo in org.get_repos():
                repos.append({
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "url": repo.html_url,
                    "clone_url": repo.clone_url,
                    "default_branch": repo.default_branch,
                    "private": repo.private,
                    "description": repo.description,
                })
            return repos
        except GithubException as e:
            raise Exception(f"Error al obtener repositorios de {org_name}: {e}")
    
    def get_repo_info(self, repo_name: str, org_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene información de un repositorio específico.
        
        Args:
            repo_name: Nombre del repositorio (puede incluir org/repo)
            org_name: Nombre de la organización (si repo_name no incluye org)
            
        Returns:
            Diccionario con información del repositorio
        """
        try:
            if "/" in repo_name:
                repo = self.github.get_repo(repo_name)
            elif org_name:
                repo = self.github.get_repo(f"{org_name}/{repo_name}")
            else:
                raise ValueError("Debe proporcionar org_name o usar formato org/repo")
            
            return {
                "name": repo.name,
                "full_name": repo.full_name,
                "url": repo.html_url,
                "clone_url": repo.clone_url,
                "default_branch": repo.default_branch,
                "private": repo.private,
                "description": repo.description,
                "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
            }
        except GithubException as e:
            raise Exception(f"Error al obtener información del repositorio {repo_name}: {e}")
    
    def create_repo(self, name: str, org_name: Optional[str] = None, 
                   description: str = "", private: bool = False) -> Dict[str, Any]:
        """
        Crea un nuevo repositorio.
        
        Args:
            name: Nombre del repositorio
            org_name: Nombre de la organización (si se crea en una org)
            description: Descripción del repositorio
            private: Si el repositorio es privado
            
        Returns:
            Diccionario con información del repositorio creado
        """
        try:
            if org_name:
                org = self.github.get_organization(org_name)
                repo = org.create_repo(
                    name=name,
                    description=description,
                    private=private,
                    auto_init=False
                )
            else:
                user = self.github.get_user()
                repo = user.create_repo(
                    name=name,
                    description=description,
                    private=private,
                    auto_init=False
                )
            
            return {
                "name": repo.name,
                "full_name": repo.full_name,
                "url": repo.html_url,
                "clone_url": repo.clone_url,
            }
        except GithubException as e:
            raise Exception(f"Error al crear repositorio {name}: {e}")

