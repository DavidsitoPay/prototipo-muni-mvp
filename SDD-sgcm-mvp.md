# Especificación (SDD) — Sistema de Gestión de Ciberseguridad Municipal (SGCM)
**Tipo de documento:** Spec-Driven Development — Especificación funcional y técnica
**Fase:** MVP / Prototipo local
**Contexto institucional:** Módulo administrativo de apoyo, inspirado visualmente en el portal público [muniguate.com](https://www.muniguate.com/)
**Estado:** Implementado. Todas las preguntas abiertas (🟡) quedaron resueltas y se anota la decisión final junto a cada una; ver [`README.md`](./README.md) para el estado operativo (setup local, despliegue, credenciales).

---

## 1. Visión y problema a resolver

La municipalidad no cuenta con un inventario formal de sus activos tecnológicos ni con un mecanismo estructurado para evaluar riesgos de ciberseguridad. Se requiere un prototipo funcional (MVP) que demuestre el flujo completo:

`Registrar activo → Identificar vulnerabilidad → Calcular riesgo → Evaluar cumplimiento NIST → Visualizar en dashboard → Exportar reporte → Recibir recomendación de mitigación`

El prototipo debe sentirse como una extensión natural del ecosistema Muniguate (mismo lenguaje visual), aunque técnicamente sea una aplicación independiente.

## 2. Alcance del MVP

Incluye:
1. Registro de Activos (CRUD + clasificación)
2. Evaluación de Riesgos (motor impacto × probabilidad)
3. Dashboard centralizado
4. Reportes PDF descargables
5. Cuestionario de madurez NIST CSF (Identificar, Proteger, Detectar, Responder, Recuperar)
6. Motor de recomendaciones (basado en reglas, con posibilidad de conectar a un LLM)

Fuera de alcance en esta fase (a definir en iteraciones futuras):
- Autenticación federada / SSO con sistemas municipales existentes
- Integración real con sistemas de terceros (ej. escaneo automático de vulnerabilidades, CMDB real)
- Notificaciones por correo/SMS
- Multi-tenant (varias dependencias municipales con datos aislados)
- Auditoría legal / cumplimiento normativo formal (esto es un prototipo demostrativo, no un sistema certificable)

## 3. Roles de usuario (MVP)

| Rol | Permisos |
|---|---|
| **Administrador TI** | Alta/edición de activos, ejecuta evaluaciones, ve dashboard completo, genera reportes |
| **Analista de Riesgo** | Registra vulnerabilidades, completa cuestionario NIST, ve recomendaciones |
| **Directivo / Lectura** | Solo visualiza dashboard y reportes (sin edición) |

🟡 **Pregunta abierta (resuelta):** ¿login real o selector de rol simulado? Se implementó un punto intermedio: **login real** (JWT + bcrypt) contra **3 cuentas fijas sembradas** ("simulada" se refiere a quiénes son los usuarios — sin SSO/registro — no a cómo se autentican). Detalle en el README, credenciales en `CREDENTIALS.md` (no versionado).

## 4. Requisitos funcionales por módulo

### 4.1 Registro de Activos
- Alta, edición, baja (soft delete) y listado de activos tecnológicos.
- Campos sugeridos: nombre, tipo (servidor, aplicación, base de datos, red, endpoint, sistema web público), dependencia/dirección responsable, criticidad para el negocio (baja/media/alta/crítica), fecha de alta, propietario/responsable, ubicación (físico/nube/on-prem), estado (activo/en mantenimiento/dado de baja).
- Clasificación y filtrado por tipo, criticidad y dependencia responsable.
- Búsqueda por nombre.
- **Criterio de aceptación:** un usuario puede registrar un activo, verlo en el listado filtrable, y editarlo sin recargar toda la vista.

### 4.2 Evaluación de Riesgos
- Cada activo puede tener 0..N vulnerabilidades asociadas.
- Cada vulnerabilidad tiene: descripción, **probabilidad** (1-5) y **impacto** (1-5).
- El motor calcula `riesgo = probabilidad × impacto`, clasificado en bandas:
  - 1-4: Bajo · 5-9: Medio · 10-15: Alto · 16-25: Crítico
- El riesgo del activo = el riesgo más alto entre sus vulnerabilidades asociadas (regla simple para el MVP).
- Vista tipo matriz de calor (5×5) probabilidad vs. impacto.
- **Criterio de aceptación:** al registrar una vulnerabilidad, el sistema calcula y muestra el nivel de riesgo automáticamente, sin cálculo manual del usuario.

### 4.3 Dashboard
Ver sección 5 (se detalla aparte por su importancia para la demo).

### 4.4 Reportes PDF
- Reporte **ejecutivo**: resumen visual (1-2 páginas) con KPIs de riesgo, top 5 activos críticos, % de madurez NIST.
- Reporte **técnico**: listado completo de activos + vulnerabilidades + recomendaciones asociadas.
- Exportación bajo demanda desde el dashboard o desde el listado de activos.
- **Criterio de aceptación:** el botón "Exportar PDF" genera un archivo descargable coherente con los datos filtrados en pantalla.

### 4.5 Evaluación NIST CSF
- Cuestionario dividido en las 5 funciones del marco: Identificar, Proteger, Detectar, Responder, Recuperar.
- Cada función contiene un set corto de preguntas (sugerido: 4-6 por función para el MVP) con escala de madurez 1-5 (Inexistente → Optimizado).
- Cálculo de % de cumplimiento por función y global.
- **Criterio de aceptación:** al completar el cuestionario, el dashboard refleja el % de madurez actualizado.

### 4.6 IA para Recomendaciones
- Al registrar una vulnerabilidad o completar el cuestionario NIST, el sistema sugiere un plan de mitigación.
- **MVP recomendado:** motor de reglas (mapea tipo de activo + nivel de riesgo + función NIST débil → recomendación predefinida de un catálogo). Esto funciona 100% local, sin dependencias externas ni costos de API.
- **Opcional/fase 2:** conectar a un LLM (ej. API de Anthropic) para generar recomendaciones más específicas en lenguaje natural, con el motor de reglas como respaldo si no hay conexión.
- **Criterio de aceptación:** toda vulnerabilidad de riesgo Alto o Crítico muestra al menos una recomendación de mitigación.

🟡 **Pregunta abierta (resuelta):** el motor de reglas es el único camino garantizado, siempre activo. El enriquecimiento opcional detrás del feature flag `LLM_ENABLED` primero se implementó contra Ollama local (solo desarrollo, no llegaba a producción por ser Azure Functions serverless); se migró después a **Google Gemini API (capa gratuita, sin tarjeta)** vía REST, lo que sí permite tenerlo activo en producción sin costo. Nunca reemplaza la recomendación de reglas — se agrega como una segunda fila `Recommendation` con `source=llm`.

## 5. Dashboard — diseño y justificación

El dashboard tiene dos secciones, para que el prototipo se sienta relevante tanto a nivel de ciberseguridad como a nivel de gestión municipal:

### 5.1 Panel de Riesgo de Ciberseguridad (núcleo del sistema)
- Total de activos registrados, desglosados por criticidad.
- Vulnerabilidades por nivel de riesgo (Bajo/Medio/Alto/Crítico) — gráfico de barras o dona.
- Matriz de calor probabilidad × impacto.
- % de madurez NIST global y por función (radar o barras).
- Top 5 activos con mayor riesgo.

### 5.2 Panel de ejemplo administrativo (dato de negocio simulado)
Se evaluó la sugerencia de usar "multas" como referencia, y tiene sentido usarla **no como reemplazo del dashboard de riesgo, sino como un activo de ejemplo dentro del inventario**: el "Sistema de Remisiones/Multas" (existe realmente en muniguate.com) se registra como un activo tecnológico crítico, y se le agregan métricas de negocio simuladas para ilustrar por qué ese activo es crítico:
- Total de multas del mes (cantidad y monto)
- Monto pagado del mes
- Monto pendiente de pago del mes

Esto conecta el riesgo técnico con el impacto real ("si este sistema falla o es vulnerado, esto es lo que está en juego"), y hace la demo más tangible para una audiencia no técnica (directivos municipales) sin desviar el propósito del sistema, que sigue siendo ciberseguridad.

**Datos de ejemplo (seed):** todo el contenido de multas será data simulada/estática para el prototipo, no una integración real con el sistema de remisiones.

🟡 **Pregunta abierta (resuelta):** confirmado tal cual — el "Sistema de Remisiones/Multas" se sembró como activo crítico con métricas de negocio simuladas asociadas (`DemoBusinessMetric`), sin convertirlo en módulo aparte.

## 6. Modelo de datos (entidades principales)

```
Asset (Activo)
├─ id, name, type, department, criticality, status, owner, location, created_at

Vulnerability (Vulnerabilidad)
├─ id, asset_id (FK), description, probability (1-5), impact (1-5),
│  risk_score (calculado), status (abierta/mitigada), created_at

Recommendation (Recomendación)
├─ id, vulnerability_id (FK) [nullable], nist_function [nullable],
│  source (regla|llm), text, created_at

NistAssessment (Evaluación NIST)
├─ id, function (identify|protect|detect|respond|recover),
│  question, score (1-5), evaluated_at

DemoBusinessMetric (Métrica de negocio simulada)
├─ id, asset_id (FK), label, value, period (mes), unit

User (si se implementa auth)
├─ id, name, role, email
```

## 7. Arquitectura técnica (histórico y estado actual)

### 7.1 Propuesta original (prototipo local con Docker)

```
docker-compose.yml
├─ frontend   → React/Next.js (SPA), puerto 3000
├─ backend    → API REST (Node/Express o Python/FastAPI), puerto 8000
├─ db         → PostgreSQL 16, puerto 5432
├─ pdf-worker → generación de PDF (puppeteer o WeasyPrint) — puede ir dentro del backend, no necesariamente un servicio aparte
└─ (opcional) redis → cache de cálculos de riesgo si se requiere
```

- Toda la infraestructura corre con `docker compose up`, sin dependencias de nube para el prototipo.
- La base de datos se inicializa con un script de seed (activos, vulnerabilidades y multas de ejemplo).
- El motor de recomendaciones vive como módulo dentro del backend (no como microservicio aparte, para simplicidad del MVP).

Esta fue la arquitectura del MVP inicial (fase local). Se abandonó Docker en una fase posterior para desplegar el prototipo de verdad — ver §7.2.

🟡 **Preguntas abiertas de infraestructura (resueltas):**
1. **Stack de backend:** Python/FastAPI.
2. **Generación de PDF:** WeasyPrint (HTML/CSS → PDF) en el MVP local con Docker; reemplazado por **xhtml2pdf** al migrar a Azure Functions, porque WeasyPrint requiere librerías nativas del sistema (pango/cairo/gdk-pixbuf) incompatibles con el runtime serverless.
3. **Autenticación:** login real (JWT) contra usuarios fijos sembrados — ver §3.
4. **LLM:** motor de reglas + enriquecimiento opcional vía Google Gemini (capa gratuita) — ver §4.6.
5. **Identidad visual:** se obtuvo el escudo oficial y la paleta real (azul marino + verde) directamente del usuario; implementados en `frontend/src/theme/tokens.css` y `frontend/public/logo.webp`.
6. **Nombre del proyecto:** "Muniguate" (no "SGCM" como marca de cara al usuario; SGCM queda como nombre técnico/histórico del repo).

### 7.2 Arquitectura de despliegue real (sin Docker)

El MVP se re-desplegó con presupuesto cero, sin Docker, en tres servicios administrados:

```
Vercel (frontend)          Azure Functions (backend)         Neon (Postgres)
React/Vite SPA       →     FastAPI vía AsgiFunctionApp   →   branches production/development
Git integration             (Consumption, plan gratuito       (endpoint directo, sin pooling)
push a main = deploy         indefinido)
                             push a main = GitHub Actions
                             (alembic upgrade head + deploy)
```

Decisiones clave de esta migración (detalle operativo completo en el README):
- **Por qué Azure Functions y no AWS EC2/App Service:** se validó que el free tier clásico de EC2 (12 meses) ya había expirado en la cuenta AWS disponible; Azure Functions Consumption es "siempre gratis" (no depende de crédito), usando una cuenta de Azure for Students.
- **Por qué no Docker:** ninguno de los tres servicios (Vercel, Azure Functions Consumption, Neon) lo requiere ni lo soporta de forma nativa para este caso de uso; simplifica el setup local a un venv + npm.
- **Azure Functions Python V2 (`AsgiFunctionApp`)** envuelve la app FastAPI existente sin reescribir routers. Requiere `"routePrefix": ""` en `host.json` (cada ruta de FastAPI ya trae su propio `/api`; sin esto el host de Azure duplica el prefijo y no arranca) y Python 3.12 específicamente (3.13 falla al iniciar el host en Linux Consumption).
- **CI/CD:** GitHub Actions (`.github/workflows/main_muniguate-api.yml`) corre `alembic upgrade head` contra Neon producción y despliega en cada push a `main` que toque `backend/`; Vercel tiene su propio Git integration para el frontend.

## 8. Lineamientos de diseño (consistencia con muniguate.com)

- **Header:** logo institucional a la izquierda, navegación horizontal simple (a diferencia del mega-menú del sitio público, aquí un menú corto: Dashboard, Activos, Riesgos, NIST, Reportes).
- **Paleta:** azul institucional como color primario, blanco como fondo dominante, un color de acento (dorado/amarillo, presente en el sitio público) reservado para alertas o CTAs, y la escala semántica de riesgo (verde/amarillo/naranja/rojo) solo para los indicadores de riesgo, sin mezclarla con la marca.
- **Tipografía:** sans-serif institucional (la misma familia tipográfica del sitio público, o una alternativa muy cercana si no está disponible como recurso libre).
- **Componentes:** tarjetas (cards) con bordes suaves y sombra ligera para KPIs, igual que los bloques de "servicios en línea" del sitio actual; tablas limpias para listados de activos.
- **Tono:** institucional, sobrio, orientado a lectura rápida por parte de directivos no técnicos.

## 9. Datos de ejemplo (seed) sugeridos

- 15-20 activos representativos (servidores, portal web, sistema de remisiones/multas, sistema de agua EMPAGUA, red interna, correo institucional, etc.)
- 20-30 vulnerabilidades distribuidas en distintos niveles de riesgo (para que el dashboard no se vea vacío ni artificialmente perfecto).
- Respuestas NIST parcialmente completadas (para mostrar tanto áreas fuertes como débiles).
- Métricas de multas del mes (ej. Total: Q450,000 · Pagadas: Q310,000 · Por pagar: Q140,000) — cifras ilustrativas, no reales.

## 10. Plan de entrega sugerido (spec-driven)

1. **Spec (este documento)** → validar con stakeholder antes de pasar a implementación.
2. **Plan técnico** → Claude Code detalla estructura de carpetas, contratos de API y esquema de base de datos a partir de esta spec.
3. **Tareas** → desglose en tickets pequeños (uno por módulo del punto 4).
4. **Implementación incremental** → Activos → Riesgos → NIST → Dashboard → PDF → Recomendaciones (motor de reglas) → (opcional) LLM.
5. **Demo con datos seed.**

---

### Resumen de decisiones (todas resueltas)
- [x] Autenticación: login real (JWT/bcrypt) contra 3 cuentas fijas sembradas
- [x] Stack backend: Python/FastAPI
- [x] Librería de generación de PDF: WeasyPrint → xhtml2pdf (al migrar a Azure Functions serverless)
- [x] LLM: motor de reglas siempre activo + enriquecimiento opcional vía Google Gemini (capa gratuita) detrás de feature flag, habilitado en producción
- [x] Assets de marca oficiales: escudo y paleta reales de Muniguate implementados
- [x] Enfoque del panel de "multas" confirmado tal cual (sección 5.2)
- [x] Infraestructura de despliegue: Vercel + Azure Functions + Neon, sin Docker (sección 7.2)
