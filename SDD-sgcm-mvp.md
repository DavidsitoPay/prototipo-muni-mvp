# Especificación (SDD) — Sistema de Gestión de Ciberseguridad Municipal (SGCM)
**Tipo de documento:** Spec-Driven Development — Especificación funcional y técnica
**Fase:** MVP / Prototipo local
**Contexto institucional:** Módulo administrativo de apoyo, inspirado visualmente en el portal público [muniguate.com](https://www.muniguate.com/)
**Estado:** Borrador para revisión — contiene preguntas abiertas señaladas con 🟡

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

🟡 **Pregunta abierta:** ¿El MVP necesita login real con estos tres roles, o basta con un selector de rol simulado (sin autenticación) para acelerar la demo? Se recomienda lo segundo para el prototipo y dejar auth real para la siguiente fase.

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

🟡 **Pregunta abierta:** ¿Se dispone de una API key (Anthropic/OpenAI) para esta fase, o el MVP debe funcionar completamente offline con el motor de reglas? Recomendación: construir el motor de reglas primero (siempre funciona) y dejar el LLM como mejora opcional detrás de un feature flag.

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

🟡 **Pregunta abierta:** ¿de acuerdo con este enfoque (multas como ejemplo de activo crítico, no como módulo de negocio independiente), o se prefiere algo distinto?

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

## 7. Arquitectura técnica propuesta (prototipo local con Docker)

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

🟡 **Preguntas abiertas de infraestructura (para definir antes de pasar a Claude Code):**
1. **Stack de backend:** ¿Node.js/Express o Python/FastAPI? (FastAPI facilita mucho la parte de "motor de reglas" y cálculos; Node es más uniforme si el frontend ya es React/Next).
2. **Generación de PDF:** ¿Puppeteer (HTML→PDF, más flexible visualmente) o una librería nativa (ej. ReportLab/WeasyPrint en Python, o pdf-lib en Node)?
3. **Autenticación:** ¿selector de rol simulado (sin login) para el MVP, o login real con JWT desde el inicio?
4. **LLM:** ¿se cuenta con API key para fase 2, o el MVP se queda 100% con motor de reglas?
5. **Identidad visual:** se recomienda tomar del sitio real el logo, la paleta de colores institucional (azul/dorado del escudo municipal) y la tipografía del theme actual. ¿Se puede compartir el logo oficial en formato SVG/PNG y, si existe, una guía de marca? Si no, se replicará de forma aproximada a partir de lo visible en muniguate.com.
6. **Nombre del proyecto/repositorio:** ¿"SGCM" está bien, o hay un nombre institucional ya definido?

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

### Resumen de decisiones pendientes antes de iniciar en Claude Code
- [ ] Autenticación: simulada vs. real
- [ ] Stack backend: Node/Express vs. Python/FastAPI
- [ ] Librería de generación de PDF
- [ ] Uso de LLM real (¿hay API key?) vs. solo motor de reglas
- [ ] Assets de marca oficiales (logo, colores exactos, tipografía)
- [ ] Confirmar enfoque del panel de "multas" como activo de ejemplo (sección 5.2)
