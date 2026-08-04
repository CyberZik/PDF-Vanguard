"""Low-level PDF manipulation utilities for injection techniques."""

import pikepdf


def escape_pdf_string(text: str) -> str:
    """Escape special characters for PDF string literals."""
    return (text
            .replace("\\", "\\\\")
            .replace("(", "\\(")
            .replace(")", "\\)")
            .replace("\n", "\\n")
            .replace("\r", "\\r"))


def append_content_stream(pdf: pikepdf.Pdf, page, raw_content: str) -> None:
    """Append raw PDF content stream operators (text) to a page."""
    append_content_stream_raw(pdf, page, raw_content.encode("latin-1"))


def append_content_stream_raw(pdf: pikepdf.Pdf, page, raw_bytes: bytes) -> None:
    """Append raw bytes as a new PDF content stream to a page."""
    new_stream = pikepdf.Stream(pdf, raw_bytes)
    new_ref = pdf.make_indirect(new_stream)

    contents = page.get("/Contents")
    if contents is None:
        page["/Contents"] = new_ref
    elif isinstance(contents, pikepdf.Array):
        contents.append(new_ref)
    else:
        page["/Contents"] = pikepdf.Array([contents, new_ref])


def ensure_font_resource(page) -> None:
    """Ensure /F1 Helvetica font exists in page resources."""
    resources = page.get("/Resources", pikepdf.Dictionary())
    if "/Resources" not in page:
        page["/Resources"] = resources
    fonts = resources.get("/Font", pikepdf.Dictionary())
    if "/Font" not in resources:
        resources["/Font"] = fonts
    if "/F1" not in fonts:
        fonts["/F1"] = pikepdf.Dictionary({
            "/Type": pikepdf.Name("/Font"),
            "/Subtype": pikepdf.Name("/Type1"),
            "/BaseFont": pikepdf.Name("/Helvetica"),
        })
