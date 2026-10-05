# PROMPT 04: Configuración de Calidad

## Objetivo
Crear archivos de configuración para linting, type checking y testing.

## Instrucciones Detalladas

### 1. pyproject.toml

```toml
[tool.poetry]
name = "restaurant-ai"
version = "1.0.0"
description = "AI Restaurant Commerce & Operations Platform"
authors = ["Your Name <your@email.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.11"

[tool.poetry.group.dev.dependencies]
ruff = "^0.8.0"
pyright = "^1.1.380"
mypy = "^1.13.0"
pytest = "^8.3.0"
pytest-cov = "^6.0.0"
pytest-asyncio = "^0.24.0"
pre-commit = "^3.8.0"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "A", "COM", "C4", "DTZ", "ISC", "ICN", "PIE", "PT", "RSE", "RET", "SLF", "SIM", "TID", "TCH", "ARG", "PTH", "ERA"]
ignore = ["E501"]

[tool.ruff.lint.isort]
known-first-party = ["api", "database", "skills", "tools"]

[tool.pyright]
pythonVersion = "3.11"
typeCheckingMode = "strict"
include = ["api", "database", "skills", "tools"]
exclude = ["__pycache__", ".venv", "node_modules"]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = "-v --cov=api --cov=database --cov=skills --cov=tools --cov-report=html"
```

### 2. pyrightconfig.json

```json
{
  "include": ["api", "database", "skills", "tools", "tests"],
  "exclude": ["__pycache__", ".venv", "node_modules", "venv"],
  "pythonVersion": "3.11",
  "typeCheckingMode": "strict",
  "reportMissingImports": true,
  "reportMissingTypeStubs": false,
  "reportUntypedFunctionDecorator": "error",
  "reportUntypedClassDecorator": "error"
}
```

### 3. .pre-commit-config.yaml

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/RobertCraiword/pyright-python
    rev: v1.1.380
    hooks:
      - id: pyright
```

## Verificación
- [ ] pyproject.toml creado con configuración ruff, pyright, pytest
- [ ] pyrightconfig.json creado
- [ ] .pre-commit-config.yaml creado
- [ ] Configuración consistente entre archivos
