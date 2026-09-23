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

URLs de producción:

- Frontend: <https://muniguate.vercel.app>
- Backend API: <https://muniguate-api.azurewebsites.net/api>

Los despliegues a `main` son automáticos:

- **Frontend (Vercel)**: proyecto conectado vía Git integration (Root Directory `frontend/`, rama de producción `main`). Un push a `main` que toque `frontend/` hace build y deploy solo.
- **Backend (Azure Functions)**: workflow de GitHub Actions [`.github/workflows/main_muniguate-api.yml`](./.github/workflows/main_muniguate-api.yml). Un push a `main` que toque `backend/` corre `alembic upgrade head` contra Neon producción y luego despliega la Function App. También se puede disparar a mano desde GitHub → pestaña Actions → "Run workflow". Requiere dos secrets configurados en el repo (Settings → Secrets and variables → Actions):
  - `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`: perfil de publicación de la Function App (`az functionapp deployment list-publishing-profiles --name muniguate-api --resource-group rg-muniguate --xml`). Si el deploy falla con `401 Unauthorized` en `ValidateAzureResource`, revisar que "Basic Auth Publishing Credentials (SCM)" esté habilitado en la Function App y regenerar este secret (el password rota cuando se cambia esa política).
  - `NEON_DATABASE_URL`: endpoint directo (no pooled) de la branch `production` de Neon.

### Setup inicial de infraestructura (ya hecho para este proyecto; referencia si hay que recrear algo)

- **Neon**: proyecto `muniguate` con branches `production` y `development` (endpoint directo, no pooled, en `DATABASE_URL`).
- **Azure**: resource group `rg-muniguate` (eastus2 — la región depende de qué regiones permita la suscripción), storage account, Function App `muniguate-api` (Python 3.12, Linux, plan Consumption — **no usar 3.13**, el host de Functions falla en arrancar con esa versión). `host.json` tiene `"routePrefix": ""` porque cada ruta de FastAPI ya trae su propio `/api`; sin esto el host de Azure Functions duplica el prefijo y no levanta. El CORS de Azure Functions es una config de plataforma **separada** de la de FastAPI — hay que configurar los dos (`az functionapp cors add` además de `CORS_ORIGINS`).
- **Vercel**: proyecto con Root Directory `frontend/`, `VITE_API_BASE_URL` apuntando a la Function App + `/api`, dominio corto asignado vía `vercel alias set`.

### Calidad de código

SonarCloud analiza cada PR (`sonarcloud.io/project/issues?id=DavidsitoPay_prototipo-muni-mvp`). Los hallazgos de estilo puro en `backend/seed/` y componentes React (props read-only, `response_model` redundante) quedaron pendientes deliberadamente — bajo impacto para un MVP universitario.

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

El motor de reglas (catálogo local, sin dependencias externas) está siempre activo y es la única fuente garantizada de recomendación. El enriquecimiento opcional vía LLM en la nube (**Google Gemini, capa gratuita**) está **habilitado en producción**: cada vulnerabilidad o función NIST que dispara una recomendación de regla genera **además** una segunda fila `Recommendation` con `source=llm` — un párrafo más natural, redactado para un directivo no técnico — sin reemplazar nunca la de reglas. Si Gemini no responde, tarda más de 12s, o no hay `GEMINI_API_KEY` configurado, se degrada en silencio y solo queda la de reglas.

En el frontend, la recomendación de IA aparece marcada con **"(enriquecido por IA)"** junto al texto (ver "Ver recomendaciones" en cada vulnerabilidad).

Para habilitarlo (o probarlo local): obtener un API key gratis en <https://aistudio.google.com/apikey> (no pide tarjeta), y setear `LLM_ENABLED=true` + `GEMINI_API_KEY=...` en `backend/.env` (local) o como Application Settings de la Function App (producción). El modelo (`GEMINI_MODEL`, default `gemini-3.6-flash`) corre con `thinkingBudget: 0` para no gastar cuota gratis en modo de razonamiento — esto es solo una reescritura de texto, no necesita "pensar".

## Identidad visual

Paleta institucional real de Muniguate (azul marino + verde, tomados del escudo municipal) en `frontend/src/theme/tokens.css`, y el escudo oficial en `frontend/public/logo.webp` (usado en header, login y favicon).
