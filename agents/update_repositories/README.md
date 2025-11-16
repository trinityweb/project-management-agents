# Agente: Actualizar Repositorios

Este agente automatiza la actualización de repositorios Git (pull y push).

## Funcionalidad

1. **Detectar repositorios**:
   - Lee configuración desde `config/github-config.json` (si existe)
   - O detecta automáticamente repositorios Git locales en `services/` y `mcp/`
   - O usa la API de GitHub si está configurado el token (opcional)

2. **Para cada repositorio**:
   - Ejecuta `git pull` si hay cambios remotos
   - Ejecuta `git push` si hay commits locales
   - Detecta y reporta conflictos

3. **Manejo de conflictos**:
   - Detecta conflictos de merge
   - Genera reporte de conflictos
   - Solicita asistencia si hay conflictos que requieren resolución manual

## Uso

```bash
# Activar entorno virtual
source venv/bin/activate

# Actualizar todos los repositorios
python update_repositories_agent.py

# Actualizar un repositorio específico
python update_repositories_agent.py --repo saas-mt-marketplace-admin

# Modo dry-run (solo simular)
python update_repositories_agent.py --dry-run
```

## Requisitos

- Git instalado y configurado (con credenciales SSH o guardadas)
- Variables de entorno configuradas (ver `.env.example`)
  - `PROJECT_ROOT` es requerido
  - `GITHUB_TOKEN` es opcional (solo para detección desde API)
- Configuración de GitHub (opcional, ver `config/github-config.example.json`)

## Notas

- **El agente usa tu configuración local de Git** para pull/push (no requiere token de GitHub)
- Si no hay configuración, detecta automáticamente repositorios Git locales en `services/` y `mcp/`
- El agente NO hace commit automático de cambios locales (por seguridad)
- Si hay conflictos, se detiene y reporta para resolución manual
- El modo `--dry-run` permite ver qué se haría sin hacer cambios reales

