"""Naive packing: 31 bytes per field element."""

from .base import FIELD_ELEMENTS_PER_BLOB, BYTES_PER_FIELD_ELEMENT, BLOB_SIZE


class NaivePacker:
    """Naive packing: 31 bytes per field element, 1 byte wasted.

    Each field element uses bytes [1:32], leaving byte [0] as 0x00.
    This guarantees we stay under the field modulus.
    """

    name = "naive_31"
    usable_bytes_per_element = 31
    usable_bytes_per_blob = FIELD_ELEMENTS_PER_BLOB * 31  # 126976 bytes

    def pack(self, data: bytes) -> list[bytes]:
        """Pack data into blobs using 31 bytes per field element."""
        if not data:
            return []

        blobs = []
        offset = 0
        data_len = len(data)
        chunk_size = self.usable_bytes_per_element

        while offset < data_len:
            blob = bytearray(BLOB_SIZE)

            for elem_idx in range(FIELD_ELEMENTS_PER_BLOB):
                if offset >= data_len:
                    break
                # Leave first byte as 0, pack 31 bytes into bytes 1-31
                take = min(chunk_size, data_len - offset)
                blob_offset = elem_idx * BYTES_PER_FIELD_ELEMENT
                blob[blob_offset + 1 : blob_offset + 1 + take] = data[offset : offset + take]
                offset += take

            blobs.append(bytes(blob))

        return blobs

    def unpack(self, blobs: list[bytes]) -> bytes:
        """Unpack blobs back to data."""
        result = bytearray()

        for blob in blobs:
            for i in range(FIELD_ELEMENTS_PER_BLOB):
                offset = i * BYTES_PER_FIELD_ELEMENT
                # Extract 31 bytes (skip the first byte)
                chunk = blob[offset + 1 : offset + BYTES_PER_FIELD_ELEMENT]
                result.extend(chunk)

        return bytes(result)
