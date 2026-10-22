from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset, AssetCriticality, AssetLocation, AssetStatus, AssetType

DEPT_TRANSITO = "Dirección de Tránsito"
DEPT_INFORMATICA = "Dirección de Informática"
DEPT_RRHH = "Recursos Humanos"
DEPT_CATASTRO = "Dirección de Catastro"
DEPT_FINANCIERA = "Dirección Financiera"

ASSETS_DATA = [
    {"name": "Sistema de Remisiones/Multas", "type": AssetType.sistema_web_publico, "department": DEPT_TRANSITO, "criticality": AssetCriticality.critica, "location": AssetLocation.nube, "owner": DEPT_TRANSITO, "status": AssetStatus.activo},
    {"name": "Sistema EMPAGUA (Agua Potable)", "type": AssetType.aplicacion, "department": "EMPAGUA", "criticality": AssetCriticality.critica, "location": AssetLocation.on_prem, "owner": "EMPAGUA", "status": AssetStatus.activo},
    {"name": "Portal Web Institucional", "type": AssetType.sistema_web_publico, "department": "Comunicación Social", "criticality": AssetCriticality.alta, "location": AssetLocation.nube, "owner": "Comunicación Social", "status": AssetStatus.activo},
    {"name": "Correo institucional", "type": AssetType.aplicacion, "department": DEPT_INFORMATICA, "criticality": AssetCriticality.alta, "location": AssetLocation.nube, "owner": DEPT_INFORMATICA, "status": AssetStatus.activo},
    {"name": "Red interna municipal", "type": AssetType.red, "department": DEPT_INFORMATICA, "criticality": AssetCriticality.alta, "location": AssetLocation.on_prem, "owner": DEPT_INFORMATICA, "status": AssetStatus.activo},
    {"name": "Servidor de Base de Datos Central", "type": AssetType.base_datos, "department": DEPT_INFORMATICA, "criticality": AssetCriticality.critica, "location": AssetLocation.on_prem, "owner": DEPT_INFORMATICA, "status": AssetStatus.activo},
    {"name": "Servidor de Archivos", "type": AssetType.servidor, "department": DEPT_INFORMATICA, "criticality": AssetCriticality.media, "location": AssetLocation.on_prem, "owner": DEPT_INFORMATICA, "status": AssetStatus.activo},
    {"name": "Servidor de Aplicaciones RRHH", "type": AssetType.servidor, "department": DEPT_RRHH, "criticality": AssetCriticality.alta, "location": AssetLocation.on_prem, "owner": DEPT_RRHH, "status": AssetStatus.activo},
    {"name": "Sistema de Nómina", "type": AssetType.aplicacion, "department": DEPT_RRHH, "criticality": AssetCriticality.alta, "location": AssetLocation.nube, "owner": DEPT_RRHH, "status": AssetStatus.activo},
    {"name": "Sistema de Catastro Municipal", "type": AssetType.aplicacion, "department": DEPT_CATASTRO, "criticality": AssetCriticality.critica, "location": AssetLocation.on_prem, "owner": DEPT_CATASTRO, "status": AssetStatus.activo},
    {"name": "Base de Datos Catastro", "type": AssetType.base_datos, "department": DEPT_CATASTRO, "criticality": AssetCriticality.critica, "location": AssetLocation.on_prem, "owner": DEPT_CATASTRO, "status": AssetStatus.activo},
    {"name": "Sistema de Tesorería", "type": AssetType.aplicacion, "department": DEPT_FINANCIERA, "criticality": AssetCriticality.critica, "location": AssetLocation.on_prem, "owner": DEPT_FINANCIERA, "status": AssetStatus.activo},
    {"name": "Base de Datos Financiera", "type": AssetType.base_datos, "department": DEPT_FINANCIERA, "criticality": AssetCriticality.critica, "location": AssetLocation.on_prem, "owner": DEPT_FINANCIERA, "status": AssetStatus.mantenimiento},
    {"name": "Endpoints Dirección de Tránsito", "type": AssetType.endpoint, "department": DEPT_TRANSITO, "criticality": AssetCriticality.media, "location": AssetLocation.fisico, "owner": DEPT_TRANSITO, "status": AssetStatus.activo},
    {"name": "Endpoints Alcaldía", "type": AssetType.endpoint, "department": "Alcaldía", "criticality": AssetCriticality.media, "location": AssetLocation.fisico, "owner": "Alcaldía", "status": AssetStatus.activo},
    {"name": "Kiosco de Autoservicio", "type": AssetType.endpoint, "department": "Atención al Ciudadano", "criticality": AssetCriticality.baja, "location": AssetLocation.fisico, "owner": "Atención al Ciudadano", "status": AssetStatus.activo},
    {"name": "Firewall Perimetral", "type": AssetType.red, "department": DEPT_INFORMATICA, "criticality": AssetCriticality.critica, "location": AssetLocation.on_prem, "owner": DEPT_INFORMATICA, "status": AssetStatus.activo},
    {"name": "Sistema de Videovigilancia Municipal", "type": AssetType.aplicacion, "department": "Dirección de Seguridad", "criticality": AssetCriticality.media, "location": AssetLocation.nube, "owner": "Dirección de Seguridad", "status": AssetStatus.activo},
    {"name": "Servidor Web Legacy", "type": AssetType.servidor, "department": DEPT_INFORMATICA, "criticality": AssetCriticality.baja, "location": AssetLocation.on_prem, "owner": DEPT_INFORMATICA, "status": AssetStatus.dado_de_baja},
]


async def seed_assets(db: AsyncSession) -> dict[str, Asset]:
    assets_by_name: dict[str, Asset] = {}
    for data in ASSETS_DATA:
        asset = Asset(**data)
        db.add(asset)
        assets_by_name[data["name"]] = asset
    await db.flush()
    return assets_by_name
