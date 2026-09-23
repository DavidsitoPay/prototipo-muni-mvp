# Muniguate — Sistema de Gestión de Ciberseguridad Municipal (SGCM)

MVP/prototipo. Ver [`SDD-sgcm-mvp.md`](./SDD-sgcm-mvp.md) para la especificación funcional completa.

Arquitectura de despliegue: **frontend en Vercel**, **backend en Azure Functions** (Consumption, plan gratuito indefinido), **base de datos en Neon** (Postgres serverless). Sin Docker.

## Requisitos

- Python 3.12 + Node 20+
- Una cuenta [Neon](https://neon.tech) (gratis) con un proyecto creado
- Para desplegar: cuenta de Vercel + cuenta de Azure con [Azure Functions Core Tools](https://learn.microsoft.com/azure/azure-functions/functions-run-local)

## Desarrollo local

### Backend

```bash
cd backend
python -m venv .venv && .venv/Scripts/activate   # o source .venv/bin/activate en Linux/Mac
pip install -r requirements.txt
cp .env.example .env   # completar DATABASE_URL con tu branch de Neon (endpoint directo, sin "-pooler")
alembic upgrade head
python -m seed.seed_data   # una sola vez; es idempotente por tabla
uvicorn app.main:app --reload
```

- Backend API: http://localhost:8000/api (health check en `/api/health`)

Antes de desplegar, conviene validar también el wrapper de Azure Functions localmente con `func start` (usa `backend/local.settings.json`, no versionado — copiar los mismos valores de `.env`).

### Frontend

```bash
cd frontend
cp .env.example .env   # VITE_API_BASE_URL=http://localhost:8000/api para desarrollo local
npm install
npm run dev
```

- Frontend: http://localhost:3000

## Despliegue

- **Neon**: crear un proyecto y (recomendado) una branch `development` separada de `production`. Usar el endpoint directo (no el pooled) en `DATABASE_URL`; correr `alembic upgrade head` y el seed una sola vez contra la branch de producción antes del primer despliegue.
- **Backend (Azure Functions)**: `func azure functionapp publish <nombre-function-app>` desde `backend/`. Configurar `DATABASE_URL`, `JWT_SECRET`, `JWT_EXPIRE_MINUTES`, `LLM_ENABLED`, `OLLAMA_HOST`, `CORS_ORIGINS` como Application Settings de la Function App (nunca en el repo).
- **Frontend (Vercel)**: importar el repo, root directory `frontend/`, y setear `VITE_API_BASE_URL` apuntando a la URL pública de la Function App + `/api`. `frontend/vercel.json` ya incluye el rewrite SPA para React Router.
- `CORS_ORIGINS` en el backend debe incluir el dominio de producción de Vercel. Los preview deployments de Vercel (URLs dinámicas por rama) no van a pasar CORS a menos que se agreguen explícitamente.

## Roles y permisos

| Rol | Puede |
|---|---|
| Administrador TI | Todo: CRUD de activos, gestionar vulnerabilidades, cuestionario NIST, dashboard, reportes |
| Analista de Riesgo | Registrar vulnerabilidades, completar NIST, ver dashboard/reportes (no crea/edita/elimina activos) |
| Directivo / Lectura | Solo Dashboard y Reportes (sin edición; el menú oculta Activos/Riesgos/NIST para este rol) |

## Credenciales de demo (autenticación simulada)

> ⚠️ "Simulada" se refiere a **quiénes** son los usuarios, no a **cómo** se autentican: no hay proveedor de identidad externo (SSO/LDAP/OAuth) ni registro de usuarios nuevos — solo 3 cuentas fijas sembradas en la base de datos. El mecanismo de login sí es real: contraseñas con hash `bcrypt` (`passlib`) y sesión vía JWT firmado (`python-jose`, `JWT_SECRET`/`JWT_EXPIRE_MINUTES`).

Las credenciales de las 3 cuentas demo (`admin.ti`, `analista.riesgo`, `directivo`) están en `CREDENTIALS.md` (no versionado — ver `.gitignore`), no en este README ni en la UI de login, para no exponerlas en el repo público ni en el despliegue real.

## Motor de recomendaciones

El motor de reglas (catálogo local, sin dependencias externas) está siempre activo. El enriquecimiento opcional vía LLM local (Ollama) está apagado por defecto; para habilitarlo, correr Ollama localmente y setear `LLM_ENABLED=true` en `backend/.env` (no aplica en el despliegue serverless de Azure Functions, pensado solo para desarrollo local).

## Identidad visual

Paleta institucional real de Muniguate (azul marino + verde, tomados del escudo municipal) en `frontend/src/theme/tokens.css`, y el escudo oficial en `frontend/public/logo.webp` (usado en header, login y favicon).
