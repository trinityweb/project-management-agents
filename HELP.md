# 📖 Ayuda de Agentes - Guía Rápida

## 🚀 Agente: Iniciar Proyecto

Inicia el proyecto completo siguiendo `INICIO_RAPIDO.md`.

### Uso Básico
```bash
./scripts/run_start_project.sh
```

### Opciones
```bash
./scripts/run_start_project.sh --help
```

**Opciones disponibles:**
- `--no-frontends` - NO inicia los frontends (por defecto los inicia)
- `--no-docs` - NO inicia la documentación (por defecto la inicia)

### Ejemplos
```bash
# Iniciar TODO (backend, frontends y documentación)
./scripts/run_start_project.sh

# Solo backend (sin frontends ni docs)
./scripts/run_start_project.sh --no-frontends --no-docs

# Backend y frontends, pero sin documentación
./scripts/run_start_project.sh --no-docs

# Backend y documentación, pero sin frontends
./scripts/run_start_project.sh --no-frontends
```

---

## 📚 Agente: Actualizar Documentación

Mantiene la documentación del proyecto actualizada.

### Uso Básico
```bash
./scripts/run_update_docs.sh
```

### Opciones
```bash
./scripts/run_update_docs.sh --help
```

**Opciones disponibles:**
- `--validate-only` - Solo validar, no actualizar
- `--update-postman` - Actualizar collection de Postman (por defecto: True)
- `--no-update-postman` - No actualizar collection de Postman
- `--update-docs` - Validar documentación de servicios (por defecto: True)
- `--no-update-docs` - No validar documentación de servicios
- `--sync-frontend` - Sincronizar frontend de docs (por defecto: True)
- `--no-sync-frontend` - No sincronizar frontend de docs

### Ejemplos
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

---

## 🔄 Agente: Actualizar Repositorios

Gestiona actualizaciones de repositorios Git (pull, push, commit).

### Uso Básico
```bash
./scripts/run_update_repos.sh
```

### Opciones
```bash
./scripts/run_update_repos.sh --help
```

**Opciones disponibles:**
- `--repo REPO_NAME` - Nombre del repositorio específico a actualizar
- `--auto-commit` - Hacer commit automático de cambios locales
- `--no-ensure-agents-repo` - No verificar/crear repositorio agents/project-management-agents
- `--dry-run` - Solo simular operaciones, no hacer cambios reales

### Ejemplos
```bash
# Actualizar todos los repositorios
./scripts/run_update_repos.sh

# Actualizar un repositorio específico
./scripts/run_update_repos.sh --repo saas-mt-marketplace-admin

# Modo dry-run (solo simular)
./scripts/run_update_repos.sh --dry-run

# Actualizar con commit automático
./scripts/run_update_repos.sh --auto-commit

# Actualizar un repo específico con commit automático
./scripts/run_update_repos.sh --repo saas-mt-pim-service --auto-commit
```

---

## 📋 Resumen de Comandos

### Ver ayuda de cualquier agente
```bash
./scripts/run_start_project.sh --help
./scripts/run_update_docs.sh --help
./scripts/run_update_repos.sh --help
```

### Ejecutar directamente (sin scripts)
```bash
# Activar entorno virtual
cd agents/start_project
source venv/bin/activate

# Ejecutar con ayuda
python start_project_agent.py --help
```

---

## 🆘 Solución de Problemas

### Error: "Entorno virtual no encontrado"
```bash
# Ejecutar setup primero
./scripts/setup.sh
```

### Error: "PROJECT_ROOT no encontrado"
El agente detecta automáticamente el directorio raíz del proyecto. Si falla:
1. Asegúrate de estar en el directorio correcto
2. O crea un archivo `.env` con:
   ```
   PROJECT_ROOT=/Users/hornosg/MyProjects/saas-mt
   ```

### Ver logs detallados
Los agentes usan logging. Para ver más detalles, revisa la salida de los comandos.

---

## 📝 Notas

- Todos los agentes tienen ayuda integrada con `--help`
- Los scripts en `./scripts/` son wrappers que activan el entorno virtual automáticamente
- Puedes ejecutar los agentes directamente desde sus directorios si prefieres

