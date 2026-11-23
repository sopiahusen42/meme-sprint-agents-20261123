#!/usr/bin/env python3
"""Ship the finished meme: validate entry.png, copy it to /output/entry.png.

The grader runs this exactly once from the repository root. It is deliberately
boring and dependency-free:

  * entry.png must be a PNG (RFC 2083 signature), exactly 1024x1024 pixels as
    declared in the IHDR chunk, and at most 1,048,576 bytes -- the bounty gate;
  * /output is created if absent, and entry.png is copied there byte for byte;
  * nothing is printed on success, and the exit status is 0.

Failure is a single line on stderr and exit status 1, so a rejected entry never
pretends to have loaded. Standard library only: no network, no Pillow, no numpy
and no clock reads, so every run reproduces identical bytes.
"""

import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
DEST_DIR = "/output"
DEST = os.path.join(DEST_DIR, "entry.png")

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
EXPECTED_SIZE = (1024, 1024)
MAX_BYTES = 1_048_576  # 1 MiB
IHDR_OFFSET = 16  # width and height start here: 8 signature + 4 length + 4 type
IHDR_LEN = 24


def check_png(path):
    """Read the file at path and return its bytes, or raise ValueError.

    Checks, in the order the gate applies them: PNG signature, readable IHDR,
    1024x1024 dimensions, and the 1 MiB size ceiling.
    """
    with open(path, "rb") as fh:
        raw = fh.read()

    if raw[:8] != PNG_SIGNATURE:
        raise ValueError("the file does not start with a PNG signature")

    if len(raw) < IHDR_LEN:
        raise ValueError(f"the file is only {len(raw)} bytes, so it has no header")

    width, height = struct.unpack(">II", raw[IHDR_OFFSET:IHDR_LEN])
    if (width, height) != EXPECTED_SIZE:
        raise ValueError(f"the image is {width}x{height}, not 1024x1024")

    if len(raw) > MAX_BYTES:
        raise ValueError(
            f"the file is {len(raw)} bytes, over the 1048576 byte limit by "
            f"{len(raw) - MAX_BYTES}"
        )

    return raw


def main():
    try:
        check_png(SRC)
    except OSError as exc:
        print(f"cannot read entry.png: {exc.strerror or exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"entry.png fails the gate: {exc}", file=sys.stderr)
        return 1

    os.makedirs(DEST_DIR, exist_ok=True)
    shutil.copyfile(SRC, DEST)
    return 0


if __name__ == "__main__":
    sys.exit(main())
