# E4 — Matriz de Trazabilidad

## 1. Introducción

El presente documento establece la trazabilidad entre los requerimientos funcionales definidos en el entregable E1, los casos de prueba diseñados en el entregable E3 y los resultados obtenidos durante la ejecución registrada en el entregable E5. La matriz permite identificar qué requerimientos carecen de cobertura y qué defectos afectan a cada requerimiento, conforme a lo exigido por el entregable.

La información se extrae directamente del Test Plan "Muniguate - Fase 1 (E3/E4/E5)" (identificador #220) del proyecto `prototipo-muni-mvp`, alojado en `dev.azure.com/drecinosg2`, y corresponde al estado de ejecución vigente a la fecha de este documento.

## 2. Alcance y estado de la ejecución

De los 41 casos de prueba diseñados, se han ejecutado 24 (58.5 %) contra el ambiente de producción de la aplicación. Los 17 casos restantes dependen de la observación de la interfaz gráfica y se encuentran pendientes de ejecución manual. La columna "Ejecución" de la matriz refleja, para cada caso, uno de tres valores posibles: Aprobado, Fallido o Pendiente. La columna "Estado" refleja exclusivamente la condición del defecto derivado, cuando existe; los requerimientos sin defectos asociados se marcan como "Sin defectos", independientemente de si su ejecución está completa o pendiente.

## 3. Matriz de trazabilidad

| Requerimiento | Caso(s) de prueba | Ejecución | Defecto(s) | Estado |
|---|---|---|---|---|
| RF-01 | CP-01, CP-02, CP-03 | Pendiente | - | Sin defectos |
| RF-02 | CP-40, CP-41 | CP-40: Aprobado; CP-41: Pendiente | - | Sin defectos |
| RF-03 | CP-28, CP-29, CP-30, CP-31 | CP-28: Aprobado; CP-29: Pendiente; CP-30: Aprobado; CP-31: Aprobado | - | Sin defectos |
| RF-04 | CP-04, CP-05, CP-23, CP-24 | CP-04: Pendiente; CP-05: Aprobado; CP-23: Fallido; CP-24: Fallido | DEF-01, DEF-02 | Abierto |
| RF-05 | CP-37 | Pendiente | - | Sin defectos |
| RF-06 | CP-38, CP-39 | Aprobado | - | Sin defectos |
| RF-07 | CP-06, CP-07, CP-08 | Pendiente | - | Sin defectos |
| RF-08 | CP-09 | Pendiente | - | Sin defectos |
| RF-09 | CP-13, CP-14, CP-15, CP-16 | Aprobado | - | Sin defectos |
| RF-10 | CP-14, CP-15, CP-16, CP-17, CP-18, CP-19, CP-20, CP-21, CP-22 | Aprobado | - | Sin defectos |
| RF-11 | CP-34, CP-35 | Pendiente | - | Sin defectos |
| RF-12 | CP-34, CP-35, CP-36 | Pendiente | - | Sin defectos |
| RF-13 | CP-12 | Pendiente | - | Sin defectos |
| RF-14 | CP-25 | Aprobado | - | Sin defectos |
| RF-15 | CP-26 | Aprobado | - | Sin defectos |
| RF-16 | CP-15, CP-20, CP-32, CP-33, CP-36 | CP-15, CP-20, CP-32, CP-33: Aprobado; CP-36: Pendiente | - | Sin defectos |
| RF-17 | CP-27 | Aprobado | - | Sin defectos |
| RF-18 | CP-34, CP-38 | CP-34: Pendiente; CP-38: Aprobado | - | Sin defectos |
| RF-19 | CP-09 | Pendiente | - | Sin defectos |
| RF-20 | CP-10 | Pendiente | - | Sin defectos |
| RF-21 | CP-11 | Pendiente | - | Sin defectos |

## 4. Requerimientos sin cobertura

Los 21 requerimientos funcionales cuentan con al menos un caso de prueba asociado. No se identifican requerimientos sin cobertura.

## 5. Defectos derivados y requerimientos afectados

Se identificaron dos defectos durante la ejecución, ambos asociados al requerimiento RF-04 y documentados con el detalle correspondiente en el entregable E5.

| Defecto | Caso de prueba | Requerimiento afectado | Severidad | Estado |
|---|---|---|---|---|
| DEF-01 (Azure DevOps #267) | CP-23 | RF-04 | Major | Abierto |
| DEF-02 (Azure DevOps #268) | CP-24 | RF-04 | Critical | Abierto |

Ninguno de los dos defectos se ha corregido a la fecha de este documento; en consecuencia, RF-04 es el único requerimiento cuyo estado se reporta como Abierto en la sección 3.

## 6. Resumen de la ejecución

| Métrica | Valor |
|---|---|
| Casos de prueba diseñados | 41 |
| Casos ejecutados | 24 (58.5 %) |
| Casos pendientes de ejecución | 17 (41.5 %) |
| Casos aprobados | 22 |
| Casos fallidos | 2 |
| Tasa de aprobación sobre lo ejecutado | 91.7 % |
| Requerimientos sin cobertura | 0 |
| Requerimientos con defectos abiertos | 1 (RF-04) |

## 7. Trabajo pendiente

La matriz se actualizará conforme el equipo ejecute de forma manual los 17 casos de prueba pendientes, correspondientes a validaciones que requieren interacción con la interfaz gráfica. Cualquier defecto adicional que se identifique durante dicha ejecución deberá documentarse con el mismo nivel de detalle empleado para DEF-01 y DEF-02, enlazarse al requerimiento y al caso de prueba correspondientes en Azure DevOps, e incorporarse tanto a esta matriz como al reporte del entregable E5.
