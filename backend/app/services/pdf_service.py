from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from xhtml2pdf import pisa

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
_BASE_CSS_PATH = TEMPLATES_DIR / "_base.css"

_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=select_autoescape(["html"]))


def render_pdf(template_name: str, context: dict) -> bytes:
    template = _env.get_template(template_name)
    html_content = template.render(
        **context,
        generated_at=datetime.now(timezone.utc),
        base_css=_BASE_CSS_PATH.read_text(encoding="utf-8"),
    )
    buffer = BytesIO()
    result = pisa.CreatePDF(html_content, dest=buffer)
    if result.err:
        raise RuntimeError(f"Error generando PDF ({template_name}): {result.err} error(es)")
    return buffer.getvalue()
