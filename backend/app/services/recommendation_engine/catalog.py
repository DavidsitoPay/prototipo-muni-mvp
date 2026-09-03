"""Catalogo de recomendaciones deterministico (sin dependencias externas).

Claves de ASSET_RISK_CATALOG: (asset_type, risk_band) -> lista de textos.
"*" en asset_type actua como comodin para cualquier tipo de activo.

Claves de NIST_FUNCTION_CATALOG: (nist_function, score_band) -> lista de textos.
score_band en {"debil", "moderado"}; "fuerte" nunca dispara recomendacion.
"""

GENERIC_RISK_FALLBACK = [
    "Escalar el hallazgo al responsable del activo y definir un plan de remediacion con fecha compromiso.",
]

ASSET_RISK_CATALOG: dict[tuple[str, str], list[str]] = {
    ("servidor", "critico"): [
        "Aplicar de inmediato los parches de seguridad criticos pendientes y aislar el servidor de redes no confiables mientras se remedia.",
        "Habilitar monitoreo de integridad de archivos (FIM) y revisar logs de acceso privilegiado en el servidor.",
    ],
    ("servidor", "alto"): [
        "Programar ventana de mantenimiento para aplicar parches pendientes y revisar configuracion de hardening del servidor.",
    ],
    ("base_datos", "critico"): [
        "Restringir accesos privilegiados a la base de datos al minimo necesario y forzar rotacion de credenciales.",
        "Verificar cifrado en reposo y en transito de la base de datos, y validar que existan respaldos recientes probados.",
    ],
    ("base_datos", "alto"): [
        "Auditar permisos de usuarios de base de datos y revisar reglas de firewall/red que la exponen.",
    ],
    ("sistema_web_publico", "critico"): [
        "Ejecutar un escaneo de vulnerabilidades web y aplicar reglas de WAF para mitigar el vector identificado mientras se corrige de raiz.",
        "Revisar validacion de entradas y controles de autenticacion del sistema publico ante el riesgo critico detectado.",
    ],
    ("sistema_web_publico", "alto"): [
        "Priorizar la correccion del hallazgo en el proximo ciclo de despliegue y reforzar monitoreo del sistema publico.",
    ],
    ("aplicacion", "critico"): [
        "Congelar nuevos despliegues de la aplicacion hasta remediar el hallazgo critico y notificar al equipo responsable.",
    ],
    ("aplicacion", "alto"): [
        "Incluir la correccion en el backlog de la siguiente iteracion con prioridad alta y agregar prueba de regresion.",
    ],
    ("red", "critico"): [
        "Segmentar la red afectada y revisar reglas de firewall/ACLs para contener el riesgo critico identificado.",
    ],
    ("red", "alto"): [
        "Revisar configuracion de switches/routers y actualizar firmware de los equipos de red involucrados.",
    ],
    ("endpoint", "critico"): [
        "Aislar el endpoint de la red corporativa y ejecutar analisis antimalware completo antes de reincorporarlo.",
    ],
    ("endpoint", "alto"): [
        "Verificar que el endpoint cuente con antivirus/EDR actualizado y aplicar politicas de bloqueo de dispositivos externos.",
    ],
    ("*", "critico"): [
        "Escalar a un plan de respuesta a incidentes inmediato dado el nivel de riesgo critico del activo.",
    ],
    ("*", "alto"): [
        "Priorizar la remediacion de esta vulnerabilidad en las proximas dos semanas y asignar responsable.",
    ],
}

NIST_FUNCTION_CATALOG: dict[tuple[str, str], list[str]] = {
    ("identify", "debil"): [
        "Formalizar un inventario de activos tecnologicos con revision trimestral y responsables asignados por dependencia.",
    ],
    ("identify", "moderado"): [
        "Complementar el inventario de activos con clasificacion de criticidad y mapa de dependencias entre sistemas.",
    ],
    ("protect", "debil"): [
        "Implementar autenticacion multifactor en accesos administrativos y a sistemas criticos.",
    ],
    ("protect", "moderado"): [
        "Reforzar politicas de control de acceso basado en roles y revisar permisos con privilegios elevados.",
    ],
    ("detect", "debil"): [
        "Desplegar monitoreo centralizado de logs (SIEM basico) para los activos criticos identificados en el inventario.",
    ],
    ("detect", "moderado"): [
        "Definir umbrales y alertas automaticas para eventos anomalos en los sistemas mas criticos.",
    ],
    ("respond", "debil"): [
        "Documentar un plan de respuesta a incidentes basico con roles, contactos y pasos de escalamiento.",
    ],
    ("respond", "moderado"): [
        "Realizar un simulacro (tabletop exercise) del plan de respuesta a incidentes existente.",
    ],
    ("recover", "debil"): [
        "Establecer y probar un procedimiento de respaldo y restauracion para los sistemas criticos.",
    ],
    ("recover", "moderado"): [
        "Definir objetivos de tiempo de recuperacion (RTO/RPO) para los sistemas criticos y validarlos con una prueba de restauracion.",
    ],
}
