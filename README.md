# Muniguate — Sistema de Gestión de Ciberseguridad Municipal (SGCM)

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

> ⚠️ "Simulada" se refiere a **quiénes** son los usuarios, no a **cómo** se autentican: no hay proveedor de identidad externo (SSO/LDAP/OAuth) ni registro de usuarios nuevos — solo 3 cuentas fijas sembradas en la base de datos. El mecanismo de login sí es real: contraseñas con hash `bcrypt` (`passlib`) y sesión vía JWT firmado (`python-jose`, `JWT_SECRET`/`JWT_EXPIRE_MINUTES`). No usar estas credenciales ni este `JWT_SECRET` de ejemplo en producción.

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

Paleta institucional real de Muniguate (azul marino + verde, tomados del escudo municipal) en `frontend/src/theme/tokens.css`, y el escudo oficial en `frontend/public/logo.webp` (usado en header, login y favicon).
