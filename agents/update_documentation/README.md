# Agente: Actualizar Documentación

Este agente automatiza la actualización y validación de la documentación del proyecto.

## Funcionalidad

1. **Actualizar collections de Postman**:
   - Busca todas las collections de Postman en los servicios
   - Valida su estructura JSON
   - Combina las collections en `combined-services-postman-collection.json`

2. **Validar documentación de repositorios**:
   - Verifica que cada servicio tenga README.md
   - Verifica existencia de directorios de documentación
   - Genera reporte de inconsistencias

3. **Sincronizar frontend de docs**:
   - Ejecuta el script de sincronización del frontend de documentación
   - Asegura que todos los archivos .md estén disponibles

## Uso

```bash
# Activar entorno virtual
source venv/bin/activate

# Actualizar todo
python update_documentation_agent.py

# Solo validar (no actualizar)
python update_documentation_agent.py --validate-only

# Actualizar solo Postman
python update_documentation_agent.py --update-postman --no-update-docs --no-sync-frontend

# Validar solo documentación
python update_documentation_agent.py --no-update-postman --update-docs --no-sync-frontend
```

## Requisitos

- Variables de entorno configuradas (ver `.env.example`)
- Script de sincronización en `services/saas-mt-docs/scripts/sync-docs.sh`

