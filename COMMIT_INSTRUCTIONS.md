# Instrucciones para hacer Commit de forma segura

## ⚠️ IMPORTANTE: Verificar antes de hacer commit

Antes de hacer commit, verifica que los archivos sensibles estén excluidos:

```bash
cd agents/project-management-agents

# Verificar que .env NO se va a subir
git status --ignored | grep .env

# Verificar que config/github-config.json NO se va a subir
git status --ignored | grep github-config.json

# Verificar que venv/ NO se va a subir
git status --ignored | grep venv
```

## 📝 Pasos para hacer commit

1. **Verificar archivos a commitear**:
```bash
cd agents/project-management-agents
git status
```

2. **Agregar archivos (el .gitignore excluirá automáticamente los sensibles)**:
```bash
git add .
```

3. **Verificar qué se va a commitear** (IMPORTANTE):
```bash
git status
# Verifica que NO aparezcan:
# - .env
# - config/github-config.json
# - **/venv/
# - *.log
```

4. **Hacer commit**:
```bash
git commit -m "feat: Agregar agentes de gestión de proyecto

- Agente para iniciar proyecto
- Agente para actualizar documentación
- Agente para actualizar repositorios
- Scripts de setup y ejecución
- Documentación completa"
```

5. **Push (si el repositorio está configurado)**:
```bash
git push
```

## 🔒 Archivos que NUNCA deben subirse

- `.env` - Contiene tokens y variables sensibles
- `config/github-config.json` - Contiene configuración con datos sensibles
- `**/venv/` - Entornos virtuales (muy pesados)
- `*.log` - Logs que pueden contener información sensible

## ✅ Archivos que SÍ deben subirse

- Código fuente (`.py`)
- Documentación (`.md`)
- Configuración de ejemplo (`env.example`, `config/*.example.json`)
- Scripts (`.sh`)
- `requirements.txt`
- `.gitignore`

