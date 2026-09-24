# E5 — Informe de Ejecución de Casos de Prueba y Reporte de Resultados

## 1. Introducción

El presente informe documenta la ejecución de los casos de prueba diseñados en el entregable E3 y consolidados en la matriz de trazabilidad del entregable E4. La ejecución se registra en Azure DevOps Test Plans, dentro del proyecto `prototipo-muni-mvp` de la organización `drecinosg2`, sobre el ambiente de producción de la aplicación Muniguate, desplegado en `https://muniguate.vercel.app` (frontend) y `https://muniguate-api.azurewebsites.net` (backend).

El informe se organiza en cinco secciones adicionales: la metodología empleada para la ejecución, los resultados obtenidos, los defectos documentados, las métricas derivadas de la ejecución, y el estado del despliegue en la nube correspondiente al entregable E6.

Al momento de la redacción de este documento, la ejecución se encuentra en un estado parcial. Esta condición se declara de forma explícita en la sección 3 y se retomará como trabajo pendiente en la sección 7, en lugar de presentarse como una ejecución completa que no corresponde con la evidencia disponible.

## 2. Metodología de ejecución

### 2.1 Herramienta y configuración

La ejecución se gestiona mediante Azure DevOps Test Plans. Se configuró un plan de pruebas denominado "Muniguate - Fase 1 (E3/E4/E5)" (identificador #220), estructurado en cuatro suites estáticas que corresponden a las cuatro técnicas de diseño aplicadas en E3: partición de equivalencia, análisis de valores límite, tabla de decisión y transición de estados. Cada uno de los 41 casos de prueba se registró como un work item de tipo Test Case, vinculado mediante la relación Tests/Tested By al requerimiento funcional (RF) que verifica.

### 2.2 Alcance de la ejecución: casos automatizables por API frente a casos dependientes de interfaz

De los 41 casos de prueba, 24 corresponden a validaciones que pueden verificarse enviando solicitudes directas a los endpoints de la API en producción, sin requerir interacción con la interfaz gráfica. Estos 24 casos se ejecutaron mediante un script que envía las solicitudes descritas en cada caso y compara la respuesta obtenida contra el resultado esperado definido en E3.

Los 17 casos restantes dependen de la observación de la interfaz de usuario (por ejemplo, el contenido visual del encabezado tras iniciar sesión, el comportamiento de un formulario de búsqueda, la ausencia de recarga completa de una vista, o la manipulación del almacenamiento local del navegador mediante herramientas de desarrollador) y requieren ejecución manual por parte de los integrantes del equipo.

## 3. Resultados de la ejecución

### 3.1 Resumen general

| Métrica | Valor |
|---|---|
| Casos de prueba diseñados (E3) | 41 |
| Casos ejecutados | 24 (58.5 %) |
| Casos pendientes de ejecución manual | 17 (41.5 %) |
| Casos aprobados | 22 |
| Casos fallidos | 2 |
| Tasa de aprobación (sobre lo ejecutado) | 91.7 % |

**[Figura 1: captura de la vista general del Test Plan "Muniguate - Fase 1 (E3/E4/E5)" en Azure DevOps, mostrando las cuatro suites y el conteo de casos en cada una.]**

### 3.2 Resultados por técnica de diseño

| Técnica | Casos | Ejecutados | Aprobados | Fallidos | Pendientes |
|---|---|---|---|---|---|
| Partición de equivalencia | 12 | 3 | 3 | 0 | 9 |
| Análisis de valores límite | 15 | 15 | 13 | 2 | 0 |
| Tabla de decisión | 6 | 5 | 5 | 0 | 1 |
| Transición de estados | 8 | 1 | 1 | 0 | 7 |

Se observa que la técnica de análisis de valores límite alcanzó una cobertura de ejecución del 100 %, dado que la mayoría de sus casos consisten en el envío de valores numéricos en los extremos de un rango, verificación que no requiere interfaz gráfica. En contraste, las técnicas de partición de equivalencia y transición de estados presentan la menor cobertura de ejecución, debido a que un número mayor de sus casos depende de la observación visual de la interfaz.

**[Figura 2: captura de la vista "Test Runs" en Azure DevOps mostrando el Run #2 (ejecución automatizada vía API) con su desglose de resultados Passed/Failed.]**

## 4. Defectos documentados

Se documentan a continuación los defectos identificados durante la ejecución. Ambos se registraron como work items de tipo Issue en Azure DevOps, enlazados al requerimiento funcional que afectan y al caso de prueba que los detectó.

### 4.1 DEF-01 (Azure DevOps #267) — Creación de activos con campos obligatorios vacíos

| Campo | Detalle |
|---|---|
| Severidad | Major |
| Prioridad | Alta |
| Módulo afectado | CRUD de activos (`backend/app/routers/assets.py`) |
| Requerimiento afectado | RF-04 |
| Caso de prueba | CP-23 |
| Pasos de reproducción | Enviar `POST /api/assets` con un token de administrador válido y el cuerpo `{"name": "", "department": "", "type": "servidor", "criticality": "media", "owner": "QA", "location": "nube"}`. |
| Resultado esperado | La API responde `422 Unprocessable Entity` y el activo no se crea. |
| Resultado obtenido | La API responde `201 Created`. El activo se crea con `name` y `department` vacíos. |
| Evidencia | Cuerpo de la respuesta real: `{"name": "", "type": "servidor", "department": "", "criticality": "media", "status": "activo", "owner": "QA", "location": "nube", "id": "7cd10f21-02b2-41cb-ac8d-23351ab9913f", "created_at": "2026-09-24T06:06:54.044833Z", "risk_band": null}` |

**[Figura 3: captura del work item DEF-01 (#267) en Azure DevOps, mostrando el estado, la severidad, la prioridad y los enlaces a RF-04 y CP-23.]**

### 4.2 DEF-02 (Azure DevOps #268) — Error no controlado ante un nombre de longitud excesiva

| Campo | Detalle |
|---|---|
| Severidad | Critical |
| Prioridad | Alta |
| Módulo afectado | CRUD de activos (`backend/app/routers/assets.py`) |
| Requerimiento afectado | RF-04 |
| Caso de prueba | CP-24 |
| Pasos de reproducción | Enviar `POST /api/assets` con un token de administrador válido y un campo `name` de 201 caracteres, con el resto de los campos válidos. |
| Resultado esperado | La API responde `422 Unprocessable Entity` con un mensaje que indique la longitud máxima permitida. |
| Resultado obtenido | La API responde `500 Internal Server Error`, con un cuerpo de respuesta vacío (`Content-Length: 0`), sin ningún detalle del error. |
| Evidencia | Encabezados de la respuesta real: `HTTP/1.1 500 Internal Server Error`, `Content-Length: 0`, `Server: Kestrel`. |

**[Figura 4: captura del work item DEF-02 (#268) en Azure DevOps, con el mismo contenido que la Figura 3 pero para este defecto.]**

### 4.3 Estado frente al mínimo requerido de defectos documentados

El presente informe documenta 2 defectos, mientras que el entregable exige un mínimo de 10. Esta diferencia se debe a que los 24 casos ejecutados hasta el momento corresponden, en su mayoría, a la lógica de cálculo de riesgo y de madurez NIST, componentes que se verificaron sin observarse defectos adicionales a los dos reportados. Los 17 casos pendientes de ejecución manual cubren áreas de la aplicación que no han sido sometidas a ninguna verificación todavía, por lo que no se descarta la aparición de defectos adicionales una vez completada su ejecución. Esta sección se actualizará conforme el equipo ejecute los casos restantes.

## 5. Métricas

### 5.1 Casos ejecutados y tasa de aprobación

De un total de 41 casos de prueba diseñados, se ejecutaron 24 (58.5 %), de los cuales 22 se aprobaron y 2 fallaron, lo que arroja una tasa de aprobación del 91.7 % sobre lo ejecutado.

### 5.2 Defectos por severidad

| Severidad | Cantidad |
|---|---|
| Blocker | 0 |
| Critical | 1 |
| Major | 1 |
| Minor | 0 |

### 5.3 Densidad de defectos por módulo

La densidad se calcula como el número de defectos encontrados dividido entre el número de casos de prueba ejecutados que cubren dicho módulo, conforme a la identificación de módulos críticos del entregable E2.

| Módulo | Casos ejecutados en el módulo | Defectos encontrados | Densidad |
|---|---|---|---|
| Motor de riesgo | 11 | 0 | 0.0 % |
| Autenticación y autorización | 4 | 0 | 0.0 % |
| Router de vulnerabilidades | 9 | 0 | 0.0 % |
| Motor NIST | 3 | 0 | 0.0 % |
| Motor de recomendaciones | 5 | 0 | 0.0 % |
| Agregaciones de dashboard y reportes | 0 | 0 | Sin ejecutar |
| CRUD de activos | 3 | 2 | 66.7 % |

El módulo de CRUD de activos concentra la totalidad de los defectos encontrados hasta el momento, con una densidad considerablemente superior al resto de los módulos evaluados. Este resultado sugiere que la validación de entrada en dicho módulo requiere revisión prioritaria, en particular en lo referente a las restricciones de longitud y de contenido mínimo de los campos de texto.

## 6. Estado del despliegue en la nube (E6)

La aplicación se encuentra desplegada y operativa. El frontend está publicado en Vercel, en la dirección `https://muniguate.vercel.app`, y el backend está publicado en Azure Functions (plan Consumption), en la dirección `https://muniguate-api.azurewebsites.net`. Ambos componentes se verificaron como accesibles durante la ejecución de los casos de prueba documentados en la sección 3.

**[Figura 5: captura de la pantalla de inicio de sesión de la aplicación en `https://muniguate.vercel.app/login`, mostrando la URL en la barra de direcciones.]**

## 7. Conclusiones y trabajo pendiente

La ejecución realizada hasta el momento cubre el 58.5 % de los casos de prueba diseñados y ha permitido identificar dos defectos reales en el módulo de CRUD de activos, ambos relacionados con la ausencia de validación de longitud y de contenido mínimo en los campos de texto del formulario de registro de activos.

Para completar el entregable, resta ejecutar de forma manual los 17 casos de prueba que dependen de la interfaz de usuario, registrar su resultado en el Test Plan de Azure DevOps, documentar cualquier defecto adicional que se identifique con el mismo nivel de detalle empleado en la sección 4, y actualizar las tablas de métricas de la sección 5 y la matriz de trazabilidad del entregable E4 con los resultados finales.
