# Agentes de Gestión de Proyecto

Repositorio con agentes de AI para automatizar tareas de gestión del proyecto SaaS Multi-Tenant "Tienda Vecina".

## 📋 Agentes Disponibles

### 1. Iniciar Proyecto (`start_project`)
Automatiza el proceso de inicio del proyecto siguiendo `INICIO_RAPIDO.md`:
- Verifica/inicia Docker Desktop
- Ejecuta `make lite-start` para iniciar el backend
- Verifica el estado de los servicios
- Inicia los frontends (por defecto)
- Inicia la documentación (por defecto)

**Ver ayuda:** `./scripts/run_start_project.sh --help`

### 2. Actualizar Documentación (`update_documentation`)
Mantiene la documentación del proyecto actualizada:
- Actualiza collections de Postman combinadas
- Valida documentación de repositorios
- Sincroniza frontend de documentación

**Ver ayuda:** `./scripts/run_update_docs.sh --help`

### 3. Actualizar Repositorios (`update_repositories`)
Gestiona actualizaciones de repositorios Git:
- Hace pull de cambios remotos
- Hace push de commits locales
- Detecta y reporta conflictos

**Ver ayuda:** `./scripts/run_update_repos.sh --help`

---

## 🆘 Ayuda Rápida

**Todos los agentes tienen ayuda integrada:**
```bash
./scripts/run_start_project.sh --help
./scripts/run_update_docs.sh --help
./scripts/run_update_repos.sh --help
```

**Ver guía completa de ayuda:** [HELP.md](HELP.md)

## 🚀 Instalación

### Requisitos Previos

- Python 3.8 o superior
- Git instalado
- Docker Desktop (para el agente start_project)
- Make (para el agente start_project)

### Configuración Inicial

1. **Clonar o navegar al repositorio**:
```bash
cd agents/project-management-agents
```

2. **Ejecutar script de setup**:
```bash
./scripts/setup.sh
```

Este script:
- Crea entornos virtuales para cada agente
- Instala dependencias de cada agente
- Verifica la configuración

3. **Configurar variables de entorno**:
```bash
# Copiar archivo de ejemplo
cp env.example .env

# Editar .env con tus valores
# PROJECT_ROOT=/ruta/al/proyecto/saas-mt
# GITHUB_TOKEN=tu_personal_access_token  # OPCIONAL - solo para detección automática desde API
```

**Nota**: El token de GitHub es **opcional**. El agente `update_repositories` usa tu configuración local de Git (SSH o credenciales guardadas) para hacer pull/push. El token solo se usa si quieres detectar repositorios automáticamente desde la API de GitHub.

4. **Configurar GitHub (opcional, para update_repositories)**:
```bash
# Copiar archivo de ejemplo
cp config/github-config.example.json config/github-config.json

# Editar config/github-config.json con tus repositorios
# O dejar vacío para detección automática desde repositorios locales
```

### Obtener GitHub Personal Access Token (Opcional)

Solo necesario si quieres detectar repositorios automáticamente desde la API de GitHub:

1. Ve a https://github.com/settings/tokens
2. Click en "Generate new token (classic)"
3. Selecciona los permisos:
   - `repo` (acceso completo a repositorios)
   - `read:org` (lectura de organizaciones)
4. Copia el token y agrégalo a `.env`

## 📖 Uso

### Agente: Iniciar Proyecto

```bash
# Iniciar solo backend
./scripts/run_start_project.sh

# Iniciar backend y frontends
./scripts/run_start_project.sh --frontends
```

O directamente:
```bash
cd agents/start_project
source venv/bin/activate
python start_project_agent.py [--frontends]
```

### Agente: Actualizar Documentación

```bash
# Actualizar todo
./scripts/run_update_docs.sh

# Solo validar (no actualizar)
./scripts/run_update_docs.sh --validate-only

# Actualizar solo Postman
./scripts/run_update_docs.sh --update-postman --no-update-docs --no-sync-frontend

# Validar solo documentación
./scripts/run_update_docs.sh --no-update-postman --update-docs --no-sync-frontend
```

O directamente:
```bash
cd agents/update_documentation
source venv/bin/activate
python update_documentation_agent.py [opciones]
```

### Agente: Actualizar Repositorios

```bash
# Actualizar todos los repositorios
./scripts/run_update_repos.sh

# Actualizar un repositorio específico
./scripts/run_update_repos.sh --repo saas-mt-marketplace-admin

# Modo dry-run (solo simular)
./scripts/run_update_repos.sh --dry-run
```

O directamente:
```bash
cd agents/update_repositories
source venv/bin/activate
python update_repositories_agent.py [opciones]
```

## 📁 Estructura del Proyecto

```
agents/project-management-agents/
├── README.md                          # Este archivo
├── .gitignore                         # Archivos a ignorar
├── requirements.txt                   # Dependencias compartidas
├── env.example                        # Template de variables de entorno
├── config/
│   ├── github-config.example.json    # Template de configuración GitHub
│   └── github-config.json            # Configuración real (no commitear)
├── agents/
│   ├── start_project/                # Agente: Iniciar Proyecto
│   │   ├── start_project_agent.py
│   │   ├── requirements.txt
│   │   ├── README.md
│   │   └── venv/                     # Entorno virtual (generado)
│   ├── update_documentation/         # Agente: Actualizar Documentación
│   │   ├── update_documentation_agent.py
│   │   ├── requirements.txt
│   │   ├── README.md
│   │   └── venv/                     # Entorno virtual (generado)
│   └── update_repositories/          # Agente: Actualizar Repositorios
│       ├── update_repositories_agent.py
│       ├── requirements.txt
│       ├── README.md
│       └── venv/                     # Entorno virtual (generado)
├── shared/                            # Módulos compartidos
│   ├── config_loader.py              # Cargador de configuración
│   ├── github_client.py              # Cliente GitHub API
│   └── utils.py                      # Utilidades compartidas
├── scripts/
│   ├── setup.sh                      # Script de setup inicial
│   ├── run_start_project.sh          # Ejecutar agente start_project
│   ├── run_update_docs.sh            # Ejecutar agente update_documentation
│   └── run_update_repos.sh           # Ejecutar agente update_repositories
└── tests/                            # Tests (futuro)
    └── __init__.py
```

## 🔧 Configuración Avanzada

### Variables de Entorno

Archivo `.env`:
```bash
# GitHub Personal Access Token
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# Ruta raíz del proyecto saas-mt
PROJECT_ROOT=/Users/hornosg/MyProjects/saas-mt
```

### Configuración de GitHub

Archivo `config/github-config.json`:
```json
{
  "organization": "trinityweb",
  "repositories": [
    "saas-mt-marketplace-admin",
    "saas-mt-marketplace-frontend",
    "mcp-go-generator-node",
    "mcp-trello-tracking",
    "documentation"
  ],
  "local_paths": {
    "saas-mt-marketplace-admin": "../marketplace-admin",
    "saas-mt-marketplace-frontend": "../marketplace-frontend"
  }
}
```

## 🐛 Troubleshooting

### Error: "Entorno virtual no encontrado"
```bash
# Ejecutar setup nuevamente
./scripts/setup.sh
```

### Error: "Variable de entorno GITHUB_TOKEN no encontrada"
```bash
# Verificar que existe .env
ls -la .env

# Si no existe, copiar desde ejemplo
cp env.example .env
# Editar .env y agregar tu token
```

### Error: "Docker no está corriendo"
```bash
# Iniciar Docker Desktop manualmente
open -a Docker  # macOS
# O esperar a que el agente lo inicie automáticamente
```

### Error: "GitHub API rate limit exceeded"
- Espera unos minutos y vuelve a intentar
- O usa un token con más permisos

## 📝 Desarrollo

### Agregar un Nuevo Agente

1. Crear directorio en `agents/nuevo_agente/`
2. Crear `nuevo_agente_agent.py` con la clase del agente
3. Crear `requirements.txt` con dependencias
4. Agregar script de ejecución en `scripts/run_nuevo_agente.sh`
5. Actualizar `scripts/setup.sh` para incluir el nuevo agente

### Ejecutar Tests

```bash
# (Futuro: cuando se implementen tests)
pytest tests/
```

## 📄 Licencia

Este proyecto es parte del ecosistema SaaS Multi-Tenant "Tienda Vecina".

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## 📞 Soporte

Para problemas o preguntas:
- Abre un issue en el repositorio
- Revisa la documentación de cada agente en `agents/*/README.md`

---

**¡Disfruta automatizando tu flujo de trabajo!** 🚀

