"""Decode zero-width-character steganography back to readable text."""

from typing import Optional

# Must mirror the encoder in injector/techniques/zero_width.py
_BIT0 = "​"  # Zero-Width Space      -> 0
_BIT1 = "‍"  # Zero-Width Joiner     -> 1
_SEP = "‌"   # Zero-Width Non-Joiner -> byte separator


def decode_zwc(text: str) -> Optional[str]:
    """Recover text hidden by the zero-width encoder.

    Returns the decoded string, or None if no decodable payload is present.
    """
    stego = "".join(c for c in text if c in (_BIT0, _BIT1, _SEP))
    if _SEP not in stego:
        return None

    out = bytearray()
    for chunk in stego.split(_SEP):
        if not chunk:
            continue
        if len(chunk) != 8 or any(c not in (_BIT0, _BIT1) for c in chunk):
            continue
        out.append(int("".join("1" if c == _BIT1 else "0" for c in chunk), 2))

    if not out:
        return None
    try:
        decoded = out.decode("utf-8")
    except UnicodeDecodeError:
        decoded = out.decode("utf-8", errors="replace")
    return decoded or None
