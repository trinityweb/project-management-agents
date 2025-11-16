# Agente: Iniciar Proyecto

Este agente automatiza el proceso de inicio del proyecto siguiendo las instrucciones de `INICIO_RAPIDO.md`.

## Funcionalidad

1. Verifica que existe `INICIO_RAPIDO.md`
2. Verifica/inicia Docker Desktop
3. Ejecuta `make lite-start` para iniciar el backend
4. Verifica el estado con `make lite-status`
5. Opcionalmente inicia los frontends con `make frontend-all`

## Uso

```bash
# Activar entorno virtual
source venv/bin/activate

# Iniciar solo backend
python start_project_agent.py

# Iniciar backend y frontends
python start_project_agent.py --frontends
```

## Requisitos

- Docker Desktop instalado y configurado
- Make instalado
- Variables de entorno configuradas (ver `.env.example`)

