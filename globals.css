[build-system]
requires = ["setuptools>=75"]
build-backend = "setuptools.build_meta"

[project]
name = "edgeboard-api"
version = "3.0.0"
description = "Subscription-ready sports analytics API"
requires-python = ">=3.12"
dependencies = [
  "fastapi[standard]==0.116.1",
  "sqlalchemy==2.0.43",
  "psycopg[binary,pool]==3.2.9",
  "alembic==1.16.5",
  "pydantic-settings==2.10.1",
  "httpx==0.28.1",
  "PyJWT==2.10.1",
  "argon2-cffi==25.1.0",
  "email-validator==2.2.0",
  "stripe==15.3.1",
  "python-multipart==0.0.20",
  "orjson==3.11.3",
]

[project.optional-dependencies]
dev = [
  "pytest==8.4.1",
  "pytest-asyncio==1.1.0",
  "ruff==0.12.10",
]

[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
asyncio_mode = "auto"

[tool.ruff]
line-length = 110
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]

[tool.setuptools.packages.find]
where = ["."]
include = ["app*"]
