from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset, AssetCriticality, AssetLocation, AssetStatus, AssetType

ASSETS_DATA = [
    dict(name="Sistema de Remisiones/Multas", type=AssetType.sistema_web_publico, department="Dirección de Tránsito", criticality=AssetCriticality.critica, location=AssetLocation.nube, owner="Dirección de Tránsito", status=AssetStatus.activo),
    dict(name="Sistema EMPAGUA (Agua Potable)", type=AssetType.aplicacion, department="EMPAGUA", criticality=AssetCriticality.critica, location=AssetLocation.on_prem, owner="EMPAGUA", status=AssetStatus.activo),
    dict(name="Portal Web Institucional", type=AssetType.sistema_web_publico, department="Comunicación Social", criticality=AssetCriticality.alta, location=AssetLocation.nube, owner="Comunicación Social", status=AssetStatus.activo),
    dict(name="Correo institucional", type=AssetType.aplicacion, department="Dirección de Informática", criticality=AssetCriticality.alta, location=AssetLocation.nube, owner="Dirección de Informática", status=AssetStatus.activo),
    dict(name="Red interna municipal", type=AssetType.red, department="Dirección de Informática", criticality=AssetCriticality.alta, location=AssetLocation.on_prem, owner="Dirección de Informática", status=AssetStatus.activo),
    dict(name="Servidor de Base de Datos Central", type=AssetType.base_datos, department="Dirección de Informática", criticality=AssetCriticality.critica, location=AssetLocation.on_prem, owner="Dirección de Informática", status=AssetStatus.activo),
    dict(name="Servidor de Archivos", type=AssetType.servidor, department="Dirección de Informática", criticality=AssetCriticality.media, location=AssetLocation.on_prem, owner="Dirección de Informática", status=AssetStatus.activo),
    dict(name="Servidor de Aplicaciones RRHH", type=AssetType.servidor, department="Recursos Humanos", criticality=AssetCriticality.alta, location=AssetLocation.on_prem, owner="Recursos Humanos", status=AssetStatus.activo),
    dict(name="Sistema de Nómina", type=AssetType.aplicacion, department="Recursos Humanos", criticality=AssetCriticality.alta, location=AssetLocation.nube, owner="Recursos Humanos", status=AssetStatus.activo),
    dict(name="Sistema de Catastro Municipal", type=AssetType.aplicacion, department="Dirección de Catastro", criticality=AssetCriticality.critica, location=AssetLocation.on_prem, owner="Dirección de Catastro", status=AssetStatus.activo),
    dict(name="Base de Datos Catastro", type=AssetType.base_datos, department="Dirección de Catastro", criticality=AssetCriticality.critica, location=AssetLocation.on_prem, owner="Dirección de Catastro", status=AssetStatus.activo),
    dict(name="Sistema de Tesorería", type=AssetType.aplicacion, department="Dirección Financiera", criticality=AssetCriticality.critica, location=AssetLocation.on_prem, owner="Dirección Financiera", status=AssetStatus.activo),
    dict(name="Base de Datos Financiera", type=AssetType.base_datos, department="Dirección Financiera", criticality=AssetCriticality.critica, location=AssetLocation.on_prem, owner="Dirección Financiera", status=AssetStatus.mantenimiento),
    dict(name="Endpoints Dirección de Tránsito", type=AssetType.endpoint, department="Dirección de Tránsito", criticality=AssetCriticality.media, location=AssetLocation.fisico, owner="Dirección de Tránsito", status=AssetStatus.activo),
    dict(name="Endpoints Alcaldía", type=AssetType.endpoint, department="Alcaldía", criticality=AssetCriticality.media, location=AssetLocation.fisico, owner="Alcaldía", status=AssetStatus.activo),
    dict(name="Kiosco de Autoservicio", type=AssetType.endpoint, department="Atención al Ciudadano", criticality=AssetCriticality.baja, location=AssetLocation.fisico, owner="Atención al Ciudadano", status=AssetStatus.activo),
    dict(name="Firewall Perimetral", type=AssetType.red, department="Dirección de Informática", criticality=AssetCriticality.critica, location=AssetLocation.on_prem, owner="Dirección de Informática", status=AssetStatus.activo),
    dict(name="Sistema de Videovigilancia Municipal", type=AssetType.aplicacion, department="Dirección de Seguridad", criticality=AssetCriticality.media, location=AssetLocation.nube, owner="Dirección de Seguridad", status=AssetStatus.activo),
    dict(name="Servidor Web Legacy", type=AssetType.servidor, department="Dirección de Informática", criticality=AssetCriticality.baja, location=AssetLocation.on_prem, owner="Dirección de Informática", status=AssetStatus.dado_de_baja),
]


async def seed_assets(db: AsyncSession) -> dict[str, Asset]:
    assets_by_name: dict[str, Asset] = {}
    for data in ASSETS_DATA:
        asset = Asset(**data)
        db.add(asset)
        assets_by_name[data["name"]] = asset
    await db.flush()
    return assets_by_name
