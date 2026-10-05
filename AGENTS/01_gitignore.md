# PROMPT 01: .gitignore

## Objetivo
Crear el archivo .gitignore para el proyecto Restaurant AI Platform.

## Instrucciones Detalladas

Crear el archivo `.gitignore` en la raíz del proyecto con las siguientes exclusiones:

### Python
```
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST
```

### Virtual Environment
```
venv/
env/
ENV/
.venv/
.env
```

### IDE
```
.vscode/
.idea/
*.swp
*.swo
*~
.project
.classpath
.settings/
```

### Database
```
*.db
*.sqlite3
*.sqlite
```

### Logs
```
*.log
logs/
```

### Docker
```
docker-compose.override.yml
```

### Environment Variables
```
.env
.env.local
.env.production
```

### OS
```
.DS_Store
Thumbs.db
```

### Python Specific
```
*.pyc
*.pyo
.mypy_cache/
.pytest_cache/
.ruff_cache/
htmlcov/
.coverage
.coverage.*
coverage.xml
```

### Node.js (si se usa Next.js para frontend)
```
node_modules/
.next/
out/
.env.local
.env.development.local
.env.test.local
.env.production.local
npm-debug.log*
yarn-debug.log*
yarn-error.log*
```

### Google Calendar Credentials
```
*credentials.json
*service-account*.json
```

## Verificación
- [ ] Archivo .gitignore creado
- [ ] Excluye __pycache__
- [ ] Excluye venv/
- [ ] Excluye .env
- [ ] Excluye *.db
- [ ] Excluye node_modules/
- [ ] Excluye credenciales de Google
