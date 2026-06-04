#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 João Pedro Rodrigues
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# === HYBRID 36 FUNCTIONS TAKEN FROM CCTBX ===
# Copyright (c) 2006-2026, The Regents of the University of California,
# through Lawrence Berkeley National Laboratory. All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided the above copyright notice and
# this paragraph are included. Full license text available at
# [https://github.com/cctbx/cctbx_project/blob/releases/2023.1/LICENSE.txt].
#

"""
Modifies the file to adhere (as much as possible) to the format specifications.

Expects a sorted file - REMARK/ATOM/HETATM/END - so use pdb_sort in case you are
not sure.

This includes:
    - Adding TER statements after chain breaks/changes
    - Truncating/Padding all lines to 80 characters
    - Adds END statement at the end of the file

Will remove all original TER/END statements from the file.

Usage:
    python pdb_tidy.py [-strict] [-h36] <pdb file>

Options:
    -h36: allows for hybrid36 output format for encoding >99999 atoms in the PDB file

Example:
    python pdb_tidy.py 1CTF.pdb
    python pdb_tidy.py -strict 1CTF.pdb  # does not add TER on chain breaks
    python pdb_tidy.py -h36 1CTF.pdb  # allows for a number of atom >99999 by using hybrid_36 format

This program is part of the `pdb-tools` suite of utilities and should not be
distributed isolatedly. The `pdb-tools` were created to quickly manipulate PDB
files using the terminal, and can be used sequentially, with one tool streaming
data to another. They are based on old FORTRAN77 code that was taking too much
effort to maintain and compile. RIP.
"""

import os
import sys
import re
import textwrap

__author__ = "Joao Rodrigues"
__email__ = "j.p.g.l.m.rodrigues@gmail.com"


digits_upper = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
digits_lower = digits_upper.lower()
digits_upper_values = dict([pair for pair in zip(digits_upper, range(36))])
digits_lower_values = dict([pair for pair in zip(digits_lower, range(36))])


# Copied from CCTBX
def encode_pure(digits, value):
    "encodes value using the given digits"
    assert value >= 0
    if (value == 0):
        return digits[0]
    n = len(digits)
    result = []
    while (value != 0):
        rest = value // n
        result.append(digits[value - rest * n])
        value = rest
    result.reverse()
    return "".join(result)


# Copied from CCTBX
def hy36encode(width, value):
    "encodes value as base-10/upper-case base-36/lower-case base-36 hybrid"
    i = value
    if (i >= 1 - 10**(width - 1)):
        if (i < 10**width):
            return ("%%%dd" % width) % i
        i -= 10**width
        if (i < 26 * 36**(width - 1)):
            i += 10 * 36**(width - 1)
            return encode_pure(digits_upper, i)
        i -= 26 * 36**(width - 1)
        if (i < 26 * 36**(width - 1)):
            i += 10 * 36**(width - 1)
            return encode_pure(digits_lower, i)
    raise ValueError("value out of range.")


# Copied from CCTBX
def decode_pure(digits_values, s):
    "decodes the string s using the digit, value associations for each character"
    result = 0
    n = len(digits_values)
    for c in s:
        result *= n
        result += digits_values[c]
    return result


# Copied from CCTBX
def hy36decode(width, s):
    "decodes base-10/upper-case base-36/lower-case base-36 hybrid"
    if (len(s) == width):
        f = s[0]
        if (f == "-" or f == " " or f.isdigit()):
            try:
                return int(s)
            except ValueError:
                pass
            if (s == " " * width):
                return 0
        elif (f in digits_upper_values):
            try:
                return decode_pure(
                    digits_values=digits_upper_values, s=s) - 10 * 36**(width - 1) + 10**width
            except KeyError:
                pass
        elif (f in digits_lower_values):
            try:
                return decode_pure(
                    digits_values=digits_lower_values, s=s) + 16 * 36**(width - 1) + 10**width
            except KeyError:
                pass
    raise ValueError("invalid number literal.")


def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options.
    """

    # Defaults
    option = False
    h36option = False
    fh = sys.stdin  # file handle

    if not len(args):
        # Reading from pipe with default option
        if sys.stdin.isatty():
            sys.stderr.write(__doc__)
            sys.exit(1)

    elif len(args) == 1:
        # One of two options: option & Pipe OR file & default option
        if args[0] == '-strict':
            option = True
            if sys.stdin.isatty():  # ensure the PDB data is streamed in
                emsg = 'ERROR!! No data to process!\n'
                sys.stderr.write(emsg)
                sys.stderr.write(__doc__)
                sys.exit(1)
        elif args[0] == '-h36':
            h36option = True
            if sys.stdin.isatty():  # ensure the PDB data is streamed in
                emsg = 'ERROR!! No data to process!\n'
                sys.stderr.write(emsg)
                sys.stderr.write(__doc__)
                sys.exit(1)
        else:
            if not os.path.isfile(args[0]):
                emsg = 'ERROR!! File not found or not readable: \'{}\'\n'
                sys.stderr.write(emsg.format(args[0]))
                sys.stderr.write(__doc__)
                sys.exit(1)

            fh = open(args[0], 'r')

    elif len(args) == 2:
        # Two options: option & File or two options & Pipe
        if not args[0].startswith('-'):
            emsg = 'ERROR! First argument is not a valid option: \'{}\'\n'
            sys.stderr.write(emsg.format(args[0]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        if args[0].startswith('-') and not args[1].startswith('-'):
            if args[0] == '-strict':
                option = True
            elif args[0] == '-h36':
                h36option = True
            else:
                emsg = 'ERROR! First argument is not a valid option: \'{}\'\n'
                sys.stderr.write(emsg.format(args[0]))
                sys.stderr.write(__doc__)
                sys.exit(1)

            if not os.path.isfile(args[1]):
                emsg = 'ERROR!! File not found or not readable: \'{}\'\n'
                sys.stderr.write(emsg.format(args[1]))
                sys.stderr.write(__doc__)
                sys.exit(1)
            fh = open(args[1], 'r')

        elif args[0].startswith('-') and args[1].startswith('-'):
            if args[0] == args[1]:
                emsg = 'ERROR! The two arguments are the same: \'{}\'\n'
                sys.stderr.write(emsg.format(args[0]))
                sys.stderr.write(__doc__)
                sys.exit(1)
            else:
                if '-strict' in args[:2]:
                    option = True
                if '-h36' in args[:2]:
                    h36option = True
                if sys.stdin.isatty():  # ensure the PDB data is streamed in
                    emsg = 'ERROR!! No data to process!\n'
                    sys.stderr.write(emsg)
                    sys.stderr.write(__doc__)
                    sys.exit(1)

    elif len(args) == 3:
        # One option: two options & File
        if not args[0].startswith('-') and args[1].startwith('-'):
            emsg = 'ERROR! First two argument are not a valid option: \'{}\'\n'
            sys.stderr.write(emsg.format(args[0]))
            sys.stderr.write(__doc__)
            sys.exit(1)
        else:
            if args[0] == '-strict' and args[1] == '-h36':
                option = True
                h36option = True
            elif args[0] == '-h36' and args[1] == '-strict':
                option = True
                h36option = True
            if not os.path.isfile(args[2]):
                emsg = 'ERROR!! File not found or not readable: \'{}\'\n'
                sys.stderr.write(emsg.format(args[1]))
                sys.stderr.write(__doc__)
                sys.exit(1)
            fh = open(args[2], 'r')

    else:  # Whatever ...
        sys.stderr.write(__doc__)
        sys.exit(1)

    return (fh, option, h36option)


def run(fhandle, strict=False, h36=False):
    """
    Add TER/END statements and truncates/pads all lines to 80 characters.

    This function is a generator.

    Parameters
    ----------
    fhandle : a line-by-line iterator of the original PDB file.

    strict : bool
        If True, does not add TER statements at intra-chain breaks.

    h36 : bool
        If True, allows for hybrid_36 format enabling the encoding for >99999 atoms.

    Yields
    ------
    str (line-by-line)
        The modified (or not) PDB line.
    """
    not_strict = not strict
    not_h36 = not h36
    fhandle = iter(fhandle)

    def make_TER(prev_line):
        """Creates a TER statement based on the last ATOM/HETATM line.
        """

        # Add last TER statement
        try:
            nserial = int(prev_line[6:11])
        except ValueError:
            nserial = hy36decode(5, prev_line[6:11])

        serial = nserial + 1
        rname = prev_line[17:20]
        chain = prev_line[21]
        resid = prev_line[22:26]
        icode = prev_line[26]

        return fmt_TER.format(serial, rname, chain, resid, icode)

    # TER     606      LEU A  75
    fmt_TER = "TER  {:>6d}      {:3s} {:1s}{:>4s}{:1s}" + " " * 53 + "\n"

    records = ('ATOM', 'HETATM')
    ignored = ('TER', 'END', 'CONECT', 'MASTER', 'ENDMDL')
    # Iterate up to the first ATOM/HETATM line
    prev_line = None
    num_models = 1
    in_model = False
    for line in fhandle:

        line = line.strip()  # We will pad/add \n later to make uniform

        if line.startswith('MODEL'):
            line = "MODEL " + "    " + str(num_models).rjust(4)
            num_models += 1
            in_model = True

        if line.startswith(ignored):  # to avoid matching END _and_ ENDMDL
            continue

        # Check line length, wrapping and padding as necessary
        # preserve the line prefix for wrapping
        prefix = re.match(r"\S+\s*", line).group(0)
        content = line[len(prefix):].lstrip()

        line = "".join(
            f"{prefix}{part:<{80 - len(prefix)}}\n"
            for part in textwrap.wrap(content, width=80 - len(prefix)))

        yield line

        if line.startswith(records):
            prev_line = line
            break

    # Now go through all the remaining lines
    atom_section = False
    serial_offset = 0  # To offset after adding TER records
    for line in fhandle:

        line = line.strip()

        if line.startswith(ignored):
            continue

        # Treat ATOM/HETATM differently
        #   - no TER in HETATM
        if line.startswith('ATOM'):

            is_gap = (int(line[22:26]) - int(prev_line[22:26])) > 1
            if atom_section and (line[21] != prev_line[21] or (not_strict and is_gap)):
                serial_offset += 1  # account for TER statement
                yield make_TER(prev_line)

            try:
                nserial = int(line[6:11])
            except ValueError:
                nserial = hy36decode(5, line[6:11])

            if not_h36 and nserial > 99999:
                emsg = 'ERROR!! Structure contains more than 99.999 atoms.\n'
                sys.stderr.write(emsg)
                sys.stderr.write(__doc__)
                sys.exit(1)

            serial = nserial + serial_offset
            if serial > 99999:
                line = line[:6] + line[6:11] + line[11:]
            else:
                line = line[:6] + str(serial).rjust(5) + line[11:]
            prev_line = line
            atom_section = True

        elif line.startswith('HETATM'):
            if atom_section:
                atom_section = False
                serial_offset += 1  # account for TER statement
                yield make_TER(prev_line)

            try:
                nserial = int(line[6:11])
            except ValueError:
                nserial = hy36decode(5, line[6:11])

            serial = nserial + serial_offset
            if serial > 99999:
                line = line[:6] + line[6:11] + line[11:]
            else:
                line = line[:6] + str(serial).rjust(5) + line[11:]
            prev_line = line

        elif line.startswith('ANISOU'):
            # Fix serial based on previous atom
            # Avoids doing the offset again
            try:
                nserial = int(prev_line[6:11])
            except ValueError:
                nserial = prev_line[6:11]
            line = line[:6] + str(nserial) + line[11:]

        else:
            if atom_section:
                atom_section = False
                yield make_TER(prev_line)
            if in_model:
                yield "{:<80}\n".format("ENDMDL")
                in_model = False

            if line.startswith('MODEL'):
                line = "MODEL " + "    " + str(num_models).rjust(4)
                num_models += 1
                in_model = True
                serial_offset = 0

        # Check line length
        line = "{:<80}\n".format(line)

        yield line

    else:
        if atom_section:
            # Add last TER statement
            atom_section = False
            yield make_TER(prev_line)
        if in_model:
            yield "{:<80}\n".format("ENDMDL")
            in_model = False

    # Add END statement
    yield "{:<80}\n".format("END")


tidy_pdbfile = run


def main():
    # Check Input
    pdbfh, strict, h36 = check_input(sys.argv[1:])

    # Do the job
    new_pdb = run(pdbfh, strict, h36)

    try:
        _buffer = []
        _buffer_size = 5000  # write N lines at a time
        for lineno, line in enumerate(new_pdb):
            if not (lineno % _buffer_size):
                sys.stdout.write(''.join(_buffer))
                _buffer = []
            _buffer.append(line)

        sys.stdout.write(''.join(_buffer))
        sys.stdout.flush()
    except IOError:
        # This is here to catch Broken Pipes
        # for example to use 'head' or 'tail' without
        # the error message showing up
        pass

    # last line of the script
    # We can close it even if it is sys.stdin
    pdbfh.close()
    sys.exit(0)


if __name__ == '__main__':
    main()
