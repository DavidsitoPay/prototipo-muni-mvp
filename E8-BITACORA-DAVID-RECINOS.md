# E8 — Bitácora individual: David Edgar Recinos García (222697)

## Qué produje

Durante esta fase realicé la migración completa de la arquitectura de despliegue, desde Docker Compose local hacia un esquema sin servidor con presupuesto cero: frontend en Vercel, backend en Azure Functions (plan Consumption) y base de datos en Neon PostgreSQL, con integración continua mediante GitHub Actions para las migraciones y el despliegue del backend. Reemplacé el motor de generación de PDF (WeasyPrint por xhtml2pdf) al no ser compatible el primero con un entorno serverless. Corregí los hallazgos de seguridad y accesibilidad señalados por SonarCloud en varias iteraciones, e implementé el enriquecimiento opcional de recomendaciones mediante la API de Google Gemini, manteniendo el motor de reglas como fuente garantizada.

También detecté y corregí una exposición real de credenciales en el historial de git, lo que implicó rotar las contraseñas de los tres usuarios sembrados y, posteriormente, eliminar por completo cualquier password o hash versionado en el código fuente, sustituyéndolo por variables de entorno. Configuré Azure DevOps Test Plans con los 21 requerimientos funcionales, el plan de pruebas con los 41 casos diseñados en E3, y ejecuté de forma real 24 de esos casos contra el ambiente de producción, documentando los dos defectos encontrados con su evidencia.

## Qué dificultades enfrenté

La dificultad más significativa surgió al intentar depurar por qué la aplicación funcionaba correctamente en una URL pero no en otra: existían dos proyectos de Vercel distintos, en dos cuentas distintas, ambos conectados al mismo repositorio de GitHub. Al intentar eliminar el proyecto duplicado, resultó que el dominio de producción real dependía de ese mismo proyecto, lo que provocó una caída temporal del sitio en producción y obligó a reconstruirlo desde cero. Esta situación evidenció que había dado por buena una hipótesis (que se trataba de cuentas separadas) sin verificarla con suficiente profundidad antes de actuar.

## Qué aprendí

Aprendí que una URL funcionando no es evidencia suficiente de que un sistema esté correctamente configurado; es necesario verificar el flujo completo (variables de entorno, CORS, autenticación) de extremo a extremo antes de darlo por resuelto. Aprendí también que un secreto sigue siendo un secreto incluso convertido en hash, y que la única forma correcta de manejarlo es mantenerlo fuera del control de versiones.

## Qué haría distinto

Antes de ejecutar cualquier acción irreversible sobre un recurso de infraestructura compartido, verificaría de forma explícita todos los dominios y configuraciones asociados a ese recurso, en lugar de basarme en lo que devuelve un único listado de la herramienta disponible.
