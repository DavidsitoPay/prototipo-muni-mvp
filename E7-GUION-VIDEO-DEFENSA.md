# E7 — Guión del Video de Defensa (máximo 10 minutos)

## Cómo usar este documento

Este es un guión literal: el texto en **negrita con nombre** es lo que cada persona debe decir, tal cual, en voz alta. El texto entre corchetes `[ASÍ]` no se lee en voz alta — es una instrucción de qué hacer en pantalla en ese momento (a qué pantalla cambiar, en qué botón hacer click, cuándo esperar). Los tiempos entre paréntesis son un estimado; sirven para no quedarse cortos ni pasarse del límite de 10 minutos, no hay que cronometrarlos al segundo.

Antes de grabar, revisar la sección 7 al final de este documento: ahí está la preparación previa necesaria (activos de prueba, sesiones abiertas, pestañas listas) para que nada de esto se tenga que improvisar en el momento.

---

## 1. Introducción conjunta (0:00–0:45)

**[PANTALLA: dashboard principal de la aplicación, ya con sesión iniciada, en `https://muniguate.vercel.app`]**

**DAVID:** "Buenas tardes. Somos David Recinos y José López, y les vamos a presentar Muniguate, un sistema de gestión de ciberseguridad municipal."

**JOSÉ:** "Muniguate permite registrar los activos tecnológicos de una municipalidad, identificar sus vulnerabilidades, calcular el riesgo de cada una, y medir la madurez de la institución frente al marco NIST Cybersecurity Framework."

**DAVID:** "La aplicación está desplegada y en funcionamiento en la nube. El frontend corre en Vercel y el backend en Azure Functions, con la base de datos en Neon. Ahora les mostramos cada uno la parte de la que fuimos responsables."

---

## 2. Componente de David (0:45–4:30)

### 2.1 Demostración del funcionamiento desplegado (0:45–1:45)

**[PANTALLA: cerrar sesión y volver a `https://muniguate.vercel.app/login`]**

**DAVID:** "Yo trabajé la arquitectura de despliegue, la seguridad y el motor de recomendaciones. Empiezo iniciando sesión con una cuenta real."

**[ACCIÓN: iniciar sesión con una de las 3 cuentas sembradas. Esperar a que cargue el Dashboard.]**

**DAVID:** "El login es real: las contraseñas están hasheadas con bcrypt y la sesión se maneja con un token JWT."

**[PANTALLA: ir a Activos → crear un activo nuevo con una vulnerabilidad]**

**DAVID:** "Ahora registro una vulnerabilidad para un activo. El sistema calcula automáticamente el riesgo, multiplicando probabilidad por impacto, y le asigna una banda."

**[ACCIÓN: guardar la vulnerabilidad y señalar en pantalla la banda de riesgo calculada]**

**[PANTALLA: cambiar a la pestaña de GitHub, sección Actions del repositorio]**

**DAVID:** "El backend se despliega automáticamente con GitHub Actions cada vez que se hace push a la rama principal. Aquí se ve una ejecución exitosa del pipeline."

### 2.2 Ejecución en vivo — caso que pasa (1:45–2:45)

**[PANTALLA: cambiar a `https://muniguate-api.azurewebsites.net/docs`]**

**DAVID:** "Ahora voy a ejecutar en vivo un caso de prueba directamente contra la API, usando la documentación interactiva que genera el backend."

**[ACCIÓN: autenticarse en Swagger UI con el token de un usuario válido]**

**DAVID:** "Este caso se llama CP-20 y prueba un valor límite: probabilidad 2, impacto 5."

**[ACCIÓN: ejecutar POST /api/assets/{asset_id}/vulnerabilities con probability=2, impact=5. Esperar la respuesta.]**

**DAVID:** "Como se ve en la respuesta, el puntaje calculado es 10 y la banda asignada es 'alto', que es exactamente lo que esperábamos. El caso pasa."

### 2.3 Ejecución en vivo — caso que falla (2:45–3:45)

**DAVID:** "Ahora les muestro un caso que sí falla, y que ya documentamos como un defecto real."

**[ACCIÓN: en Swagger UI, ejecutar POST /api/assets con name de más de 200 caracteres, resto de campos válidos. Esperar la respuesta.]**

**DAVID:** "El resultado esperado era un error 422, con un mensaje claro de que el nombre es demasiado largo. Pero lo que obtenemos es un error 500, sin ningún detalle, lo cual es un defecto real de la aplicación."

**[PANTALLA: cambiar a Azure DevOps, abrir el work item del defecto DEF-02 (#268)]**

**DAVID:** "Este defecto ya está documentado en Azure DevOps, con su severidad, los pasos para reproducirlo, y la evidencia de la respuesta que acabamos de ver."

### 2.4 Cierre del componente de David (3:45–4:30)

**[PANTALLA: panel de SonarCloud del proyecto]**

**DAVID:** "Por último, en cuanto a calidad de código, integramos SonarCloud al proyecto. Aquí se ve el estado del Quality Gate y las correcciones que aplicamos sobre los hallazgos de seguridad que se identificaron. Le paso la palabra a José."

---

## 3. Componente de José (4:30–8:15)

### 3.1 Demostración del funcionamiento desplegado (4:30–5:30)

**[PANTALLA: ir a la sección NIST de la aplicación]**

**JOSÉ:** "Yo trabajé la evaluación de madurez NIST, el dashboard, los reportes, y el control de acceso según el rol de cada usuario."

**[ACCIÓN: responder o modificar una pregunta de una de las 5 funciones del cuestionario NIST. Guardar.]**

**JOSÉ:** "El cuestionario tiene 25 preguntas, 5 por cada función del marco NIST. Cada respuesta actualiza el porcentaje de madurez de esa función."

**[PANTALLA: ir a Dashboard]**

**JOSÉ:** "Y aquí, en el dashboard, se ve reflejado ese cambio inmediatamente en el radar de madurez NIST y en la matriz de calor de riesgo."

### 3.2 Ejecución en vivo — caso que pasa (5:30–6:45)

**JOSÉ:** "Ahora ejecuto en vivo un caso de prueba de control de acceso por rol, que se llama CP-29."

**[ACCIÓN: cerrar sesión. Iniciar sesión con la cuenta del rol Directivo.]**

**JOSÉ:** "El resultado esperado es que, con este rol, el menú solo muestre Dashboard y Reportes."

**[PANTALLA: señalar el menú de navegación]**

**JOSÉ:** "Como se ve, no aparecen las opciones de Activos, Riesgos ni NIST."

**[ACCIÓN: hacer click en la barra de direcciones del navegador, escribir manualmente la URL terminada en /activos, y presionar Enter]**

**JOSÉ:** "Ahora intento entrar directamente escribiendo la dirección del inventario de activos en el navegador. El sistema no debería mostrármelo."

**[ACCIÓN: esperar a que cargue. Señalar el resultado.]**

**JOSÉ:** "Como se ve, la aplicación no muestra el inventario. El caso pasa: el control de acceso por rol funciona correctamente también cuando se intenta entrar directamente por la URL."

### 3.3 Ejecución en vivo — segundo caso (6:45–8:00)

**[ACCIÓN: cerrar sesión. Iniciar sesión de nuevo como admin.ti.]**

**JOSÉ:** "Este segundo caso se llama CP-38 y prueba que, al eliminar un activo, desaparezca en todos lados: en el listado, en el dashboard, y en los reportes."

**[PANTALLA: Dashboard. Señalar el KPI de total de activos.]**

**JOSÉ:** "Primero anoto el total de activos actual."

**[ACCIÓN: ir a Activos → crear un activo de prueba llamado "QA-DEMO-VIDEO"]**

**JOSÉ:** "Creo un activo de prueba para esta demostración."

**[ACCIÓN: en el listado, eliminar "QA-DEMO-VIDEO" y confirmar]**

**JOSÉ:** "Y ahora lo elimino."

**[PANTALLA: Dashboard]**

**JOSÉ:** "El total de activos regresa al número original."

**[PANTALLA: Reportes → exportar PDF técnico → abrir el archivo descargado]**

**JOSÉ:** "Y si exporto el reporte técnico en PDF, el activo que acabo de eliminar tampoco aparece. El caso pasa."

### 3.4 Cierre del componente de José (8:00–8:15)

**[PANTALLA: Azure DevOps, Test Plan, suites de Tabla de Decisión y Transición de Estados]**

**JOSÉ:** "Estos y el resto de los casos de mi parte quedan registrados aquí, en el Test Plan de Azure DevOps."

---

## 4. Cierre conjunto (8:15–9:30)

**[PANTALLA: matriz de trazabilidad, resaltando la fila de RF-04]**

**DAVID:** "En resumen, de los 41 casos de prueba diseñados, ejecutamos 24 hasta este momento, con una tasa de aprobación del 91.7 por ciento sobre lo ejecutado."

**[PANTALLA: tabla de métricas del entregable E5]**

**JOSÉ:** "Encontramos dos defectos reales, ambos en el módulo de registro de activos, ya documentados con su severidad y su evidencia. El resto de los casos, y cualquier defecto adicional que aparezca, se completará durante la siguiente fase del proyecto."

**DAVID:** "Con esto concluimos la defensa de Muniguate. Gracias por su atención."

---

## 5. Preparación previa a la grabación (hacer esto ANTES de grabar)

1. Confirmar la contraseña vigente de la cuenta `directivo` en `CREDENTIALS.md`, para no trabarse al iniciar sesión en la sección 3.2.
2. Tener ya creada al menos una vulnerabilidad de prueba lista para usar en la sección 2.1, sobre un activo que no sea parte del seed original.
3. Abrir de antemano todas las pestañas que se van a necesitar, en este orden, para solo alternar entre ellas durante la grabación:
   - Pestaña 1: `muniguate.vercel.app`
   - Pestaña 2: `muniguate-api.azurewebsites.net/docs` (Swagger UI), con sesión ya autenticada
   - Pestaña 3: GitHub, sección Actions del repositorio
   - Pestaña 4: Azure DevOps, con el work item DEF-02 (#268) ya abierto
   - Pestaña 5: SonarCloud, panel del proyecto
   - Pestaña 6: Azure DevOps, Test Plan "Muniguate - Fase 1 (E3/E4/E5)"
4. Hacer un ensayo completo sin grabar, una vez, para medir el tiempo real y ajustar el ritmo si hace falta.
5. Verificar que el micrófono y la grabación de pantalla capturan ambas voces con buen volumen antes de la toma final.
