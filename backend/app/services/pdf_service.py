from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=select_autoescape(["html"]))


def render_pdf(template_name: str, context: dict) -> bytes:
    template = _env.get_template(template_name)
    html_content = template.render(**context, generated_at=datetime.now(timezone.utc))
    return HTML(string=html_content, base_url=str(TEMPLATES_DIR)).write_pdf()
