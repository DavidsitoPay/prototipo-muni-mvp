# SGCM — Sistema de Gestión de Ciberseguridad Municipal

MVP/prototipo local. Ver [`SDD-sgcm-mvp.md`](./SDD-sgcm-mvp.md) para la especificación funcional completa.

## Requisitos

- Docker + Docker Compose

## Levantar el proyecto

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api (health check en `/api/health`)
- Postgres: localhost:5432

Para bajar todo y limpiar datos: `docker compose down -v`.

El primer arranque aplica las migraciones de Alembic y siembra datos de demo automáticamente (19 activos, ~28 vulnerabilidades, cuestionario NIST parcial y métricas de multas). Es idempotente: reiniciar el stack no duplica datos.

## Roles y permisos

| Rol | Puede |
|---|---|
| Administrador TI | Todo: CRUD de activos, gestionar vulnerabilidades, cuestionario NIST, dashboard, reportes |
| Analista de Riesgo | Registrar vulnerabilidades, completar NIST, ver dashboard/reportes (no crea/edita/elimina activos) |
| Directivo / Lectura | Solo Dashboard y Reportes (sin edición; el menú oculta Activos/Riesgos/NIST para este rol) |

## Credenciales de demo (autenticación simulada)

> ⚠️ Autenticación simulada para el prototipo — usuarios y contraseñas fijos, sin proveedor de identidad real. No usar en producción.

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin.ti` | `Demo123!` | Administrador TI |
| `analista.riesgo` | `Demo123!` | Analista de Riesgo |
| `directivo` | `Demo123!` | Directivo / Lectura |

## Motor de recomendaciones

El motor de reglas (catálogo local, sin dependencias externas) está siempre activo. El enriquecimiento opcional vía LLM local (Ollama) está apagado por defecto; para habilitarlo:

```bash
docker compose --profile llm up
```

y setear `LLM_ENABLED=true` en `.env`.

## Identidad visual

La paleta de colores es una aproximación institucional (azul + dorado), ya que no fue posible obtener los assets oficiales exactos de muniguate.com durante el desarrollo (el sitio bloquea scraping). Los valores viven en `frontend/src/theme/tokens.css` y son el único lugar a tocar si se consiguen los assets reales.
