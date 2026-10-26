# Punto de partida — E11 (pruebas de API) y E14 (pruebas de carga)

Este documento es solo una guía de arranque para que José no tenga que levantar todo el contexto desde cero. No se necesita tocar código de la aplicación para ninguno de los dos entregables — todo se construye con herramientas externas (Postman / JMeter) y los artefactos resultantes se commitean al repo.

## Contexto rápido

- **Backend:** FastAPI, desplegado en Azure Functions. Único ambiente vivo en la nube: producción (`https://muniguate-api.azurewebsites.net`). No hay un Function App separado para QA — el workflow de deploy solo corre con push a `main`.
- **Frontend:** `https://muniguate.vercel.app` (no hace falta para E11/E14, son pruebas contra el backend).
- **Auth:** `POST /api/auth/login` con `{"username": "...", "password": "..."}` devuelve `{"access_token": "...", "token_type": "bearer", "user": {...}}`. El resto de endpoints protegidos esperan `Authorization: Bearer <access_token>`.
- **Usuarios demo:** `admin.ti`, `analista.riesgo`, `directivo` (tres roles distintos, con permisos distintos — ver `backend/app/models/user.py` si hace falta el detalle). Las contraseñas están en `CREDENTIALS.md` (está en la raíz del repo local, gitignored — pregúntame si no la tienes a mano).

## Inventario de endpoints (para armar la colección)

Todos bajo el prefijo `/api`. Los que requieren rol específico están marcados.

| Recurso | Métodos | Rutas | Rol requerido |
|---|---|---|---|
| Auth | POST, GET | `/auth/login`, `/auth/me` | ninguno / cualquiera autenticado |
| Activos | GET, POST, PUT, DELETE | `/assets`, `/assets/{id}` | lectura: cualquiera autenticado · escritura/borrado: `admin_ti` |
| Vulnerabilidades | GET, POST, PUT, DELETE | `/assets/{asset_id}/vulnerabilities`, `/vulnerabilities`, `/vulnerabilities/{id}` | lectura: cualquiera · crear/editar: `analista_riesgo` o `admin_ti` · borrar: `admin_ti` |
| Recomendaciones | GET, POST | `/vulnerabilities/{id}/recommendations`, `/nist/{function}/recommendations`, `/recommendations/generate` | lectura: cualquiera · generar: `analista_riesgo` o `admin_ti` |
| NIST CSF | GET, PUT | `/nist/questions`, `/nist/assessment`, `/nist/summary` | lectura: cualquiera · editar assessment: `analista_riesgo` o `admin_ti` |
| Dashboard | GET | `/dashboard/summary`, `/dashboard/heatmap`, `/dashboard/nist-radar` | cualquiera autenticado |
| Métricas de negocio | GET | `/assets/{asset_id}/business-metrics` | cualquiera autenticado |
| Reportes PDF | GET | `/reports/executive`, `/reports/technical` | cualquiera autenticado |

Fuente de verdad: `backend/app/routers/*.py` (cada endpoint tiene su `response_model`/firma ahí si hace falta el detalle exacto de query params o el body esperado — los schemas Pydantic están en `backend/app/schemas/`).

## E11 — Colección de Postman

**Mínimo exigido:** 15 requests con aserciones (código de respuesta + esquema + contenido), más un flujo de negocio completo encadenado.

**Flujo de negocio sugerido** (encadena varias requests pasando datos de una a la siguiente vía variables de entorno de Postman):

1. `POST /api/auth/login` (como `admin.ti`) → guardar `access_token` en una variable de entorno.
2. `POST /api/assets` → crear un activo de prueba → guardar su `id`.
3. `POST /api/assets/{asset_id}/vulnerabilities` → crear una vulnerabilidad con probabilidad/impacto altos (ej. 5×5) sobre ese activo → guardar su `id`. Esto dispara la generación automática de una recomendación por reglas.
4. `GET /api/vulnerabilities/{vulnerability_id}/recommendations` → verificar que ya existe al menos una recomendación (la del motor de reglas).
5. `PUT /api/vulnerabilities/{vulnerability_id}` → bajar probabilidad/impacto, verificar que `risk_score`/`risk_band` cambian.
6. `GET /api/dashboard/summary` → verificar que el activo recién creado se refleja en los conteos.
7. `DELETE /api/vulnerabilities/{vulnerability_id}` y `DELETE /api/assets/{asset_id}` → limpiar lo creado (para no ensuciar los datos demo).

Aparte de ese flujo, se pueden sumar requests sueltas con aserciones (ej. `GET /api/assets` valida esquema de la lista, un `POST /api/assets` con `admin_ti` incorrecto valida 403, un login con password incorrecto valida 401, etc.) hasta llegar al mínimo de 15.

**Importante para la integración al pipeline (de esto me encargo yo después):** no hardcodees `https://muniguate-api.azurewebsites.net` en cada request — usa una variable de entorno de Postman (ej. `{{base_url}}`). En CI probablemente voy a correr esto contra un backend local levantado con la misma base de Neon `development` que ya usan los tests (así no afecta producción), así que si la colección ya usa `{{base_url}}` parametrizado, no hay que tocarla después.

**Dónde guardarlo:** una carpeta `api-tests/` en la raíz del repo, con la colección exportada (`.postman_collection.json`) y el/los environment(s) (`.postman_environment.json`, sin credenciales reales adentro — usa variables vacías que se llenan al correr).

## E14 — Pruebas de carga

**Escenario mínimo exigido:** ≥2 endpoints críticos, rampa de 0 a 50 VU sostenida 5 min, métricas de tiempo de respuesta (promedio y p95), throughput y tasa de error, y una conclusión que compare contra las RNF del E1.

**Importante — esta sí tiene que correr contra el ambiente real desplegado en la nube** (`https://muniguate-api.azurewebsites.net`), no local. Por eso te recomiendo elegir endpoints de **solo lectura (GET)** como los "críticos" a probar — además de ser los que de verdad importan para la experiencia de usuario bajo carga, evitan que la prueba te vaya creando/borrando cientos de registros de prueba en la base de datos de producción mientras corre.

**Candidatos sugeridos:**
- `GET /api/dashboard/summary` — el endpoint más pesado (agrega sobre todos los activos y vulnerabilidades), es el que carga el dashboard principal.
- `GET /api/assets` — el listado que más se usa en la navegación normal.

**RNF a comparar:** revisa el E1 (`documentos/Proyecto Fase 1 - Aseguramiento de la calidad de software.pdf`) — ahí está la RNF de concurrencia/desempeño definida originalmente (creo recordar que se definió para ~20 usuarios concurrentes, pero confirma el número y el texto exacto en el PDF antes de escribir la conclusión, no te fíes de mi memoria). La conclusión debe decir explícitamente si 50 VU sostenidos cumple o no esa RNF, con los números de la corrida como evidencia.

**Herramienta:** JMeter o Postman (Collection Runner / Postman's propio load testing) — ninguna de las dos te obliga a escribir código real, son configuración por UI. Si usas JMeter, el archivo `.jmx` se puede abrir y editar en la GUI sin tocar XML a mano.

**Dónde guardarlo:** una carpeta `load-tests/` en la raíz del repo, con el `.jmx` (o la config de Postman) y un resultado exportado (CSV/HTML del reporte de JMeter, o el summary de Postman) como evidencia de la corrida.

## Checklist rápido

- [ ] Colección Postman con ≥15 requests + aserciones (E11)
- [ ] Flujo de negocio completo encadenado dentro de esa colección (E11)
- [ ] Commit de `api-tests/` a `dev` (rama propia tipo `feat/e11-api-tests`, luego aviso para mergearla)
- [ ] Prueba de carga ejecutada contra producción, 2+ endpoints GET, rampa 0→50 VU / 5 min (E14)
- [ ] Métricas capturadas: tiempo de respuesta promedio y p95, throughput, tasa de error (E14)
- [ ] Conclusión escrita comparando contra la RNF de concurrencia del E1 (E14)
- [ ] Commit de `load-tests/` a `dev` (misma lógica de rama)

Cualquier duda sobre un endpoint específico, el detalle está en `backend/app/routers/` y `backend/app/schemas/` — o me preguntas directo.
