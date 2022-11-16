import hashlib
import logging
import random
import struct
import uuid
from typing import Sequence, Dict

id_salt = random.randbytes(16)

issued_warnings: Dict[tuple[int, int], list[str]] = {}


def gen_object_id(fig_id: Sequence[int], suffix: bytes = b'') -> str:
    # Generate UUIDs by hashing the fig GUID with a salt
    salted_id = id_salt + struct.pack('<' + 'I' * len(fig_id), *fig_id) + suffix
    uuid_bytes = bytearray(hashlib.shake_128(salted_id).digest(16))

    # Override bits to match UUIDv4
    uuid_bytes[6] = (uuid_bytes[6] & 0x0f) | 0x40
    uuid_bytes[8] = (uuid_bytes[8] & 0x3f) | 0x80

    return str(uuid.UUID(bytes=bytes(uuid_bytes))).upper()


def generate_file_ref(data: bytes) -> str:
    return hashlib.sha1(hashlib.sha1(data).digest()).hexdigest()


def get_style_table_override(fig_item):
    override_table = {0: {}}

    if 'styleOverrideTable' in fig_item:
        override_table.update({s['styleID']: s for s in fig_item['styleOverrideTable']})

    return override_table


def log_conversion_warning(warning_code: str, fig_node: dict) -> None:
    WARNING_MESSAGES = {
        "TXT001": f"is missing the glyphs property. If the text has unicode characters, it may not convert the format properly",
        "TXT002": f"has multiple text fill colors. Only the first one will be converted",
        "TXT003": f"has a non-solid text color (gradient or image) which is not supported by Sketch",
        "TXT004": f"contains a 'TITLE' transformation. Sketch does not support this text transformation, so no transformation is applied",
        "TXT005": f"contains a LIST style with list markers. This style will be ignored",

        "SHP001": f"contains a line with at least one 'Reversed triangle' end. This type of marker does not exist in Sketch. It has been converted to a 'Line' type marker",

        "STY001": f"contains a layer blur and a background blur. Only one will be converted",
        "STY002": f"contains a DIAMOND gradient, which is not supported. It is converted to a RADIAL gradient",

        "SYM001": f"references an invalid symbol. It will be converted to an empty placeholder group",

        "ART001": f"has at least one corner radius which is not supported by sketch artboards. The corner radius will be ignored",
        "ART002": f"is being converted to an artboard. However, artboard rotations are not supported. Rotation will be ignored",
        "ART003": f"has an style that is not supported by sketch artboards. It will add a background rectangle to the artboard with the frame style",

        "BSE001": f"has a layout grid enabled. This functionality is not yet implemented",

        "GRP001": f"is a nested frame, which is not supported in sketch. The frame will be converted to a group"
    }

    if fig_node['guid'] not in issued_warnings:
        issued_warnings[fig_node['guid']] = [warning_code]
    elif warning_code not in issued_warnings[fig_node['guid']]:
        issued_warnings[fig_node['guid']].append(warning_code)
    else:
        return
    logging.warning(
        f"[{warning_code}] {fig_node['type']} '{fig_node['name']}' {WARNING_MESSAGES[warning_code]}")
