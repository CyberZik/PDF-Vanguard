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


# Single-byte codes used to draw zero-width characters. A ToUnicode CMap maps
# them to the real code points so text extractors emit U+200B/U+200C/U+200D.
ZWC_CODE_MAP = {
    "​": 0x01,  # Zero-Width Space        -> bit 0
    "‍": 0x02,  # Zero-Width Joiner       -> bit 1
    "‌": 0x03,  # Zero-Width Non-Joiner   -> separator
}

ZWC_FONT_NAME = "/FZWC"


def _zwc_tounicode_cmap() -> bytes:
    entries = "\n".join(
        f"<{code:02X}> <{ord(ch):04X}>" for ch, code in sorted(ZWC_CODE_MAP.items(), key=lambda kv: kv[1])
    )
    return (
        "/CIDInit /ProcSet findresource begin\n"
        "12 dict begin\n"
        "begincmap\n"
        "/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def\n"
        "/CMapName /PDFVanguard-ZWC def\n"
        "/CMapType 2 def\n"
        "1 begincodespacerange\n<00> <FF>\nendcodespacerange\n"
        f"{len(ZWC_CODE_MAP)} beginbfchar\n{entries}\nendbfchar\n"
        "endcmap\n"
        "CMapName currentdict /CMap defineresource pop\n"
        "end\nend\n"
    ).encode("ascii")


def ensure_zwc_font_resource(pdf: pikepdf.Pdf, page) -> str:
    """Ensure a font whose ToUnicode CMap maps codes 1-3 to zero-width chars.

    Returns the resource name of the font (e.g. ``/FZWC``).
    """
    resources = page.get("/Resources", pikepdf.Dictionary())
    if "/Resources" not in page:
        page["/Resources"] = resources
    fonts = resources.get("/Font", pikepdf.Dictionary())
    if "/Font" not in resources:
        resources["/Font"] = fonts
    if ZWC_FONT_NAME not in fonts:
        fonts[ZWC_FONT_NAME] = pdf.make_indirect(pikepdf.Dictionary({
            "/Type": pikepdf.Name("/Font"),
            "/Subtype": pikepdf.Name("/Type1"),
            "/BaseFont": pikepdf.Name("/Helvetica"),
            "/FirstChar": 1,
            "/LastChar": 3,
            "/Widths": pikepdf.Array([0, 0, 0]),
            "/ToUnicode": pdf.make_indirect(pikepdf.Stream(pdf, _zwc_tounicode_cmap())),
        }))
    return ZWC_FONT_NAME
