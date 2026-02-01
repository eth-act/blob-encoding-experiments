"""Bit-packing: 254 bits per field element."""

from bitarray import bitarray
from bitarray.util import ba2int, int2ba

from .base import FIELD_ELEMENTS_PER_BLOB, BYTES_PER_FIELD_ELEMENT, BLOB_SIZE


class BitPacker:
    """Bit-packing: use 254 bits per field element.

    The BLS12-381 scalar field modulus is ~255 bits, but to guarantee
    we stay under it, we use 254 bits per element. This gives us
    254 * 4096 = 1040384 bits = 130048 bytes per blob.
    """

    name = "bitpack_254"
    bits_per_element = 254
    usable_bytes_per_blob = (254 * FIELD_ELEMENTS_PER_BLOB) // 8  # 130048 bytes
    _data_mask = (1 << bits_per_element) - 1

    def pack(self, data: bytes) -> list[bytes]:
        """Pack data using 254 bits per field element."""
        if not data:
            return []

        blobs = []

        # Convert data to bit stream
        bits = bitarray(endian="big")
        bits.frombytes(data)
        total_bits = len(bits)
        offset = 0
        while offset < total_bits:
            blob = bytearray(BLOB_SIZE)

            for elem_idx in range(FIELD_ELEMENTS_PER_BLOB):
                if offset >= total_bits:
                    break

                # Extract 254 bits for this field element
                elem_bits = bits[offset : offset + self.bits_per_element]
                offset += len(elem_bits)

                # Pad to 254 bits if needed (pad on LSB side)
                missing = self.bits_per_element - len(elem_bits)
                if missing:
                    elem_bits.extend([0] * missing)

                # Convert 254 bits to 32 bytes (256 bits), with 2 leading zero bits.
                # The value is guaranteed < 2^254, so top 2 bits are zero.
                elem_bytes = ba2int(elem_bits).to_bytes(32, "big")

                blob_offset = elem_idx * BYTES_PER_FIELD_ELEMENT
                blob[blob_offset : blob_offset + 32] = elem_bytes

            blobs.append(bytes(blob))

        return blobs if blobs else [bytes(BLOB_SIZE)]

    def unpack(self, blobs: list[bytes]) -> bytes:
        """Unpack blobs back to data."""
        all_bits = bitarray(endian="big")

        for blob in blobs:
            for elem_idx in range(FIELD_ELEMENTS_PER_BLOB):
                offset = elem_idx * BYTES_PER_FIELD_ELEMENT
                elem_bytes = blob[offset : offset + 32]

                # Extract the 254 data bits (skip the 2 padding bits)
                value = int.from_bytes(elem_bytes, "big") & self._data_mask
                all_bits.extend(int2ba(value, length=self.bits_per_element, endian="big"))

        return all_bits.tobytes()
