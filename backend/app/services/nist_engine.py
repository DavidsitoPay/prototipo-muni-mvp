from app.models.nist_assessment import NistFunction

QUESTION_CATALOG: list[dict[str, str]] = [
    # Identificar
    {"code": "ID-1", "function": NistFunction.identify, "text": "¿Existe un inventario formal y actualizado de los activos tecnológicos?"},
    {"code": "ID-2", "function": NistFunction.identify, "text": "¿Se ha clasificado cada activo según su criticidad para la operación municipal?"},
    {"code": "ID-3", "function": NistFunction.identify, "text": "¿Se identifican y documentan los riesgos de ciberseguridad de forma periódica?"},
    {"code": "ID-4", "function": NistFunction.identify, "text": "¿Existe un responsable asignado por cada activo o sistema crítico?"},
    {"code": "ID-5", "function": NistFunction.identify, "text": "¿Se conocen las dependencias entre sistemas internos y proveedores externos?"},
    # Proteger
    {"code": "PR-1", "function": NistFunction.protect, "text": "¿Se aplica autenticación multifactor en accesos administrativos o críticos?"},
    {"code": "PR-2", "function": NistFunction.protect, "text": "¿Existen políticas de control de acceso basadas en roles?"},
    {"code": "PR-3", "function": NistFunction.protect, "text": "¿El personal recibe capacitación periódica en ciberseguridad?"},
    {"code": "PR-4", "function": NistFunction.protect, "text": "¿Se gestionan parches y actualizaciones de seguridad de forma regular?"},
    {"code": "PR-5", "function": NistFunction.protect, "text": "¿Existen controles de cifrado para datos sensibles en tránsito y reposo?"},
    # Detectar
    {"code": "DE-1", "function": NistFunction.detect, "text": "¿Se cuenta con monitoreo centralizado de logs o eventos de seguridad?"},
    {"code": "DE-2", "function": NistFunction.detect, "text": "¿Existen alertas automáticas ante actividad anómala en sistemas críticos?"},
    {"code": "DE-3", "function": NistFunction.detect, "text": "¿Se revisan periódicamente los registros de acceso a sistemas sensibles?"},
    {"code": "DE-4", "function": NistFunction.detect, "text": "¿Se realizan escaneos de vulnerabilidades de forma periódica?"},
    {"code": "DE-5", "function": NistFunction.detect, "text": "¿Existe un proceso para detectar accesos no autorizados?"},
    # Responder
    {"code": "RS-1", "function": NistFunction.respond, "text": "¿Existe un plan documentado de respuesta a incidentes de ciberseguridad?"},
    {"code": "RS-2", "function": NistFunction.respond, "text": "¿Se han definido roles y responsables para la respuesta a incidentes?"},
    {"code": "RS-3", "function": NistFunction.respond, "text": "¿Se han realizado simulacros o pruebas del plan de respuesta?"},
    {"code": "RS-4", "function": NistFunction.respond, "text": "¿Existe un canal definido para reportar incidentes internamente?"},
    {"code": "RS-5", "function": NistFunction.respond, "text": "¿Se documentan las lecciones aprendidas tras un incidente?"},
    # Recuperar
    {"code": "RC-1", "function": NistFunction.recover, "text": "¿Existen respaldos periódicos y probados de los sistemas críticos?"},
    {"code": "RC-2", "function": NistFunction.recover, "text": "¿Se han definido objetivos de tiempo de recuperación (RTO/RPO)?"},
    {"code": "RC-3", "function": NistFunction.recover, "text": "¿Existe un plan de continuidad operativa ante fallas mayores?"},
    {"code": "RC-4", "function": NistFunction.recover, "text": "¿Se ha probado la restauración de sistemas desde respaldo en el último año?"},
    {"code": "RC-5", "function": NistFunction.recover, "text": "¿Se comunican a los interesados los planes de recuperación tras un incidente?"},
]

QUESTIONS_BY_CODE = {q["code"]: q for q in QUESTION_CATALOG}


def average_score(scores: list[int]) -> float | None:
    if not scores:
        return None
    return sum(scores) / len(scores)


def maturity_percent(scores: list[int]) -> float | None:
    """Convierte escala 1-5 a porcentaje. Preguntas sin responder (None) se
    excluyen del calculo, no cuentan como 0."""
    if not scores:
        return None
    avg = sum(scores) / len(scores)
    return round((avg / 5) * 100, 1)
