#!/usr/bin/env python3
"""
Convert a tokenized MSX BASIC .bas file into a 16 KB ROM
for openMSX (mapper type 'page2').

Always appends a dummy line 65000 so the program is cleanly terminated.

Usage:
    python bas2rom.py input.bas output.rom
"""

import sys
import struct

ROM_SIZE = 0x4000
TEXT_ADDR = 0x8010
FIRST_LINE_ADDR = 0x8011

def bas_to_rom(bas_path: str, rom_path: str) -> None:
    with open(bas_path, "rb") as f:
        data = f.read()

    if not data or data[0] != 0xFF:
        raise ValueError("Not a tokenized BASIC file (must start with 0xFF)")

    src = data[1:]
    lines = []
    pos = 0

    while pos + 4 <= len(src):
        next_ptr = struct.unpack_from("<H", src, pos)[0]
        if next_ptr == 0:
            break

        line_num_bytes = src[pos + 2 : pos + 4]
        line_num = struct.unpack("<H", line_num_bytes)[0]

        if line_num > 65000:
            break

        eol = pos + 4
        while eol < len(src) and src[eol] != 0:
            eol += 1
        if eol >= len(src):
            body = src[pos + 4 :] + b"\x00"
            lines.append((line_num_bytes, body))
            break

        body = src[pos + 4 : eol + 1]
        lines.append((line_num_bytes, body))
        pos = eol + 1

    if not lines:
        raise ValueError("No BASIC lines found")

    print(f"Extracted {len(lines)} lines from source")

    # Force a clean dummy line at the end
    dummy_num = struct.pack("<H", 65000)
    dummy_body = b"\x8F\xE6 program converted from bas to rom\x00"
    lines.append((dummy_num, dummy_body))

    # Rebuild with correct absolute addresses
    rebuilt = bytearray()
    addr = FIRST_LINE_ADDR

    for i, (line_num_bytes, body) in enumerate(lines):
        line_len = 4 + len(body)
        next_addr = 0 if i == len(lines) - 1 else addr + line_len

        rebuilt.extend(struct.pack("<H", next_addr))
        rebuilt.extend(line_num_bytes)
        rebuilt.extend(body)
        addr += line_len

    rebuilt.extend(b"\x00\x00")

    # Zero-filled ROM
    rom = bytearray(ROM_SIZE)
    rom[0:2] = b"AB"
    rom[8:10] = struct.pack("<H", TEXT_ADDR)
    rom[0x10] = 0x00

    end = 0x11 + len(rebuilt)
    if end > ROM_SIZE:
        raise ValueError(f"Program too large ({len(rebuilt)} bytes)")
    rom[0x11:end] = rebuilt

    with open(rom_path, "wb") as f:
        f.write(rom)

    print(f"Wrote {rom_path} (with dummy line 65000)")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python bas2rom.py input.bas output.rom")
        sys.exit(1)
    try:
        bas_to_rom(sys.argv[1], sys.argv[2])
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
