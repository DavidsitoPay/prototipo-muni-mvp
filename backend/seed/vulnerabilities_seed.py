from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset
from app.models.vulnerability import Vulnerability
from app.services.recommendation_engine.service import generate_for_vulnerability
from app.services.risk_engine import compute_risk

# (nombre_activo, descripcion, probabilidad, impacto)
VULNERABILITIES_DATA = [
    ("Sistema de Remisiones/Multas", "Falta de parches de seguridad en el servidor web", 5, 5),
    ("Sistema de Remisiones/Multas", "Uso de contraseñas débiles en panel administrativo", 4, 4),
    ("Sistema de Remisiones/Multas", "Falta de rate limiting en formulario de pago", 3, 3),
    ("Sistema EMPAGUA (Agua Potable)", "Sistema operativo sin soporte del fabricante", 4, 5),
    ("Sistema EMPAGUA (Agua Potable)", "Falta de cifrado en transmisión de datos de facturación", 3, 4),
    ("Portal Web Institucional", "Vulnerabilidad XSS en formulario de contacto", 3, 3),
    ("Portal Web Institucional", "Certificado SSL próximo a expirar", 2, 2),
    ("Correo institucional", "Falta de filtro anti-phishing avanzado", 4, 3),
    ("Correo institucional", "Política de contraseñas débil", 3, 2),
    ("Red interna municipal", "Segmentación de red insuficiente entre dependencias", 3, 4),
    ("Red interna municipal", "Puntos de acceso WiFi sin autenticación fuerte", 3, 3),
    ("Servidor de Base de Datos Central", "Respaldos no verificados periódicamente", 3, 5),
    ("Servidor de Base de Datos Central", "Puertos de administración expuestos en la red interna sin restricción", 4, 4),
    ("Servidor de Archivos", "Permisos de carpetas compartidas demasiado abiertos", 2, 3),
    ("Servidor de Aplicaciones RRHH", "Falta de actualizaciones del sistema operativo", 3, 3),
    ("Sistema de Nómina", "Acceso de terceros sin monitoreo", 2, 4),
    ("Sistema de Nómina", "Falta de registro de auditoría de cambios salariales", 2, 3),
    ("Sistema de Catastro Municipal", "Inyección SQL detectada en módulo de búsqueda", 4, 5),
    ("Sistema de Catastro Municipal", "Falta de validación de entradas en formularios", 3, 3),
    ("Base de Datos Catastro", "Datos sensibles sin cifrar en reposo", 3, 4),
    ("Sistema de Tesorería", "Falta de segregación de funciones en aprobaciones de pago", 3, 5),
    ("Base de Datos Financiera", "Servidor en mantenimiento con parches pendientes de aplicar", 2, 4),
    ("Endpoints Dirección de Tránsito", "Antivirus desactualizado en varios equipos", 2, 2),
    ("Endpoints Alcaldía", "Uso de dispositivos USB sin control", 2, 2),
    ("Kiosco de Autoservicio", "Acceso físico sin bloqueo automático de sesión", 1, 2),
    ("Firewall Perimetral", "Reglas de firewall desactualizadas y sin revisión periódica", 2, 5),
    ("Sistema de Videovigilancia Municipal", "Cámaras con credenciales por defecto sin cambiar", 3, 2),
    ("Servidor Web Legacy", "Sistema operativo fuera de soporte, sin parches disponibles", 1, 1),
]


async def seed_vulnerabilities(db: AsyncSession, assets_by_name: dict[str, Asset]) -> None:
    for asset_name, description, probability, impact in VULNERABILITIES_DATA:
        asset = assets_by_name[asset_name]
        score, band = compute_risk(probability, impact)
        vulnerability = Vulnerability(
            asset_id=asset.id,
            description=description,
            probability=probability,
            impact=impact,
            risk_score=score,
            risk_band=band,
        )
        db.add(vulnerability)
        await db.flush()
        await generate_for_vulnerability(db, vulnerability, asset.type)
    await db.flush()
