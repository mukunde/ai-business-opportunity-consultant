"""Render the persisted Markdown reports into a single branded PDF.

xhtml2pdf (pisa) is pure Python, so the PDF builds identically on a Windows dev
host and inside the Linux container, with no cairo/pango system libraries. The
two stored Markdown documents are converted to HTML and laid out on their own
pages: executive summary first, detailed assessment second.
"""

from __future__ import annotations

import io

from markdown import markdown as _md_to_html
from xhtml2pdf import pisa

# Deep teal, matching the Alfred AI brand accent used in the web UI.
_BRAND = "#0e7490"

_CSS = f"""
@page {{ size: a4; margin: 2.2cm 2cm; }}
body {{ font-family: Helvetica, sans-serif; font-size: 10.5pt; color: #1c2024;
        line-height: 1.45; }}
h1 {{ font-size: 19pt; color: {_BRAND}; margin: 0 0 4pt 0; }}
h2 {{ font-size: 12pt; color: {_BRAND}; margin: 16pt 0 4pt 0;
      border-bottom: 1px solid #d4dadf; padding-bottom: 2pt; }}
p {{ margin: 4pt 0; }}
ul {{ margin: 4pt 0; }}
li {{ margin: 1pt 0; }}
strong {{ color: #11181c; }}
table {{ border-collapse: collapse; width: 100%; margin: 6pt 0; }}
th, td {{ border: 1px solid #d4dadf; padding: 4pt 6pt; text-align: left;
          font-size: 9.5pt; }}
th {{ background-color: #eef4f5; color: {_BRAND}; }}
.brandbar {{ color: #8b9398; font-size: 8pt; letter-spacing: 1pt;
             text-transform: uppercase; margin-bottom: 12pt; }}
"""

_TEMPLATE = (
    "<html><head><meta charset='utf-8'><style>{css}</style></head><body>"
    "<div class='brandbar'>Alfred AI &middot; AI use-case qualification</div>"
    "{summary}"
    "<pdf:nextpage />"
    "{assessment}"
    "</body></html>"
)

_MD_EXTENSIONS = ["tables", "sane_lists"]


def render_report_pdf(*, summary_md: str, assessment_md: str) -> bytes:
    """Convert both report documents into one PDF and return its raw bytes."""
    summary_html = _md_to_html(summary_md, extensions=_MD_EXTENSIONS)
    assessment_html = _md_to_html(assessment_md, extensions=_MD_EXTENSIONS)
    html = _TEMPLATE.format(css=_CSS, summary=summary_html, assessment=assessment_html)

    buffer = io.BytesIO()
    result = pisa.CreatePDF(src=html, dest=buffer, encoding="utf-8")
    if result.err:
        raise RuntimeError("PDF rendering failed")
    return buffer.getvalue()
