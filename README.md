# bas2rom.py

Convert a tokenized MSX BASIC `.bas` file into a 16 KB ROM suitable for openMSX (mapper type `page2`).

The resulting ROM is mapped to page 2 (`$8000–$BFFF`) and contains a standard MSX cartridge header so the BASIC program runs automatically when the cartridge is inserted.

## Features

- Reads a classic tokenized MSX BASIC file (must start with `0xFF`)
- Rebuilds the program with correct absolute line-link pointers inside the ROM
- Inserts a proper cartridge header (`"AB"` + TEXT pointer)
- Always appends a dummy line `65000` to guarantee a clean end-of-program marker
- Produces a 16 KB ROM filled with zeros after the program (safe for BASIC)

## Requirements

- Python 3.6 or later
- No external dependencies

## Usage

```bash
python3 bas2rom.py input.bas output.rom
```
