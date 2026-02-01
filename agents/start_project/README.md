# Agente: Iniciar Proyecto

Este agente automatiza el proceso de inicio del proyecto siguiendo las instrucciones de `INICIO_RAPIDO.md`.

## Funcionalidad

1. Verifica que existe `INICIO_RAPIDO.md`
2. Verifica/inicia Docker Desktop
3. Ejecuta `make lite-start` para iniciar el backend
4. Verifica el estado con `make lite-status`
5. Inicia los frontends con `make frontend-all` (por defecto)
6. Inicia la documentación con `make docs` (por defecto)

## Uso

```bash
# Activar entorno virtual
source venv/bin/activate

# Iniciar backend, frontends y documentación (por defecto)
python start_project_agent.py

# Iniciar solo backend (sin frontends ni docs)
python start_project_agent.py --no-frontends --no-docs

# Iniciar backend y frontends, pero sin documentación
python start_project_agent.py --no-docs

# Iniciar backend y documentación, pero sin frontends
python start_project_agent.py --no-frontends
```

## Requisitos

- Docker Desktop instalado y configurado
- Make instalado
- Variables de entorno configuradas (ver `.env.example`)

