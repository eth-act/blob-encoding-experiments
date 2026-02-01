"""No compression (pass-through)."""


class NoCompression:
    """Pass-through, no compression."""

    name = "none"

    def compress(self, data: bytes) -> bytes:
        return data

    def decompress(self, data: bytes) -> bytes:
        return data
