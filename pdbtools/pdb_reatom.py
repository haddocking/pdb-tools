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

"""
Renumbers atom serials in the PDB file starting from a given value (default 1).

Usage:
    python pdb_reatom.py -<number> <pdb file>

    Options:
        -h36: allows for hybrid36 output format for encoding >99999 atoms in the PDB file

Example:
    python pdb_reatom.py -10 1CTF.pdb  # renumbers from 10
    python pdb_reatom.py --1 1CTF.pdb  # renumbers from -1

This program is part of the `pdb-tools` suite of utilities and should not be
distributed isolatedly. The `pdb-tools` were created to quickly manipulate PDB
files using the terminal, and can be used sequentially, with one tool streaming
data to another. They are based on old FORTRAN77 code that was taking too much
effort to maintain and compile. RIP.
"""

import os
import sys

__author__ = "Joao Rodrigues"
__email__ = "j.p.g.l.m.rodrigues@gmail.com"

digits_upper = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
digits_lower = digits_upper.lower()
digits_upper_values = dict([pair for pair in zip(digits_upper, range(36))])
digits_lower_values = dict([pair for pair in zip(digits_lower, range(36))])


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


def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options.
    """

    # Defaults
    option = 1
    h36option = False
    fh = sys.stdin  # file handle

    if not len(args):
        # Reading from pipe with default option
        if sys.stdin.isatty():
            sys.stderr.write(__doc__)
            sys.exit(1)

    elif len(args) == 1:
        # One of two options: option & Pipe OR file & default option
        if args[0].startswith('-') and args[0] != '-h36':
            option = args[0][1:]
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
        # One of three options: two options & Pipe OR one option & file
        if not args[0].startswith('-'):
            emsg = 'ERROR! First argument is not an option: \'{}\'\n'
            sys.stderr.write(emsg.format(args[0]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        if args[0].startswith('-') and args[0] != '-h36' and args[1] == '-h36':
            option = args[0][1:]
            h36option = True
            if sys.stdin.isatty():  # ensure the PDB data is streamed in
                emsg = 'ERROR!! No data to process!\n'
                sys.stderr.write(emsg)
                sys.stderr.write(__doc__)
                sys.exit(1)

        elif args[1].startswith('-') and args[1] != '-h36' and args[0] == '-h36':
            option = args[1][1:]
            h36option = True
            if sys.stdin.isatty():  # ensure the PDB data is streamed in
                emsg = 'ERROR!! No data to process!\n'
                sys.stderr.write(emsg)
                sys.stderr.write(__doc__)
                sys.exit(1)

        elif args[0] == '-h36':
            h36option = True
            if not os.path.isfile(args[1]):
                emsg = 'ERROR!! File not found or not readable: \'{}\'\n'
                sys.stderr.write(emsg.format(args[1]))
                sys.stderr.write(__doc__)
                sys.exit(1)

            fh = open(args[1], 'r')

        elif args[0].startswith('-') and args[0] != '-h36':
            option = args[0][1:]
            if not os.path.isfile(args[1]):
                emsg = 'ERROR!! File not found or not readable: \'{}\'\n'
                sys.stderr.write(emsg.format(args[1]))
                sys.stderr.write(__doc__)
                sys.exit(1)

            fh = open(args[1], 'r')

    elif len(args) == 3:
        # Two options: two option (different orders) & File
        if not args[0].startswith('-') and not args[1].startswith('-'):
            emsg = 'ERROR! First two arguments are not an option: \'{}\'\n'
            sys.stderr.write(emsg.format(args[0]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        if args[0] == args[1]:
            emsg = 'ERROR! The two arguments are the same: \'{}\'\n'
            sys.stderr.write(emsg.format(args[0]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        if args[1] == '-h36':
            h36option = True
            option = args[0][1:]

        if args[0] == '-h36':
            h36option = True
            option = args[1][1:]

        if not os.path.isfile(args[2]):
            emsg = 'ERROR!! File not found or not readable: \'{}\'\n'
            sys.stderr.write(emsg.format(args[2]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        fh = open(args[2], 'r')

    else:  # Whatever ...
        sys.stderr.write(__doc__)
        sys.exit(1)

    # Validate option
    try:
        option = int(option)
    except ValueError:
        emsg = 'ERROR!! You provided an invalid atom serial number: \'{}\''
        sys.stderr.write(emsg.format(option))
        sys.exit(1)

    return (fh, option, h36option)


def run(fhandle, starting_value, h36=False):
    """
    Reset the atom serial number column to start from a specific number.

    This function is a generator.

    Parameters
    ----------
    fhandle : a line-by-line iterator of the original PDB file.

    h36 : bool
        If True, allows for hybrid_36 format enabling the encoding for >99999 atoms.

    Yields
    ------
    str (line-by-line)
        The modified (or not) PDB line.
    """

    # CONECT 1179  746 1184 1195 1203
    fmt_CONECT = "CONECT{:>5s}{:>5s}{:>5s}{:>5s}{:>5s}" + " " * 49 + "\n"
    char_ranges = (slice(6, 11), slice(11, 16),
                   slice(16, 21), slice(21, 26), slice(26, 31))

    serial_equiv = {'': ''}  # store for conect statements

    not_h36 = not h36
    serial = starting_value
    records = ('ATOM', 'HETATM')
    for line in fhandle:
        if line.startswith(records):
            serial_equiv[line[6:11].strip()] = serial

            if serial < 100000:
                wserial = serial
                yield line[:6] + str(serial).rjust(5) + line[11:]

            else:
                if not_h36 and serial > 99999:
                    emsg = 'ERROR!! Structure contains more than 99.999 atoms.\n'
                    sys.stderr.write(emsg)
                    sys.stderr.write(__doc__)
                    sys.exit(1)
                elif h36 and serial > 99999:
                    wserial = hy36encode(5, serial)
                    yield line[:6] + str(wserial).rjust(5) + line[11:]

            serial += 1

        elif line.startswith('ANISOU'):
            # Keep atom id as previous atom
            yield line[:6] + str(wserial).rjust(5) + line[11:]

        elif line.startswith('CONECT'):
            # 6:11, 11:16, 16:21, 21:26, 26:31
            serials = [line[cr].strip() for cr in char_ranges]

            # If not found, return default
            new_serials = [str(serial_equiv.get(s, s)) for s in serials]
            conect_line = fmt_CONECT.format(*new_serials)

            yield conect_line
            continue

        elif line.startswith('MODEL'):
            serial = starting_value
            yield line

        elif line.startswith('TER'):
            yield line[:6] + str(wserial).rjust(5) + line[11:]
            serial += 1

        else:
            yield line


renumber_atom_serials = run


def main():
    # Check Input
    pdbfh, starting_resid, h36 = check_input(sys.argv[1:])

    # Do the job
    new_pdb = run(pdbfh, starting_resid, h36)

    # Output results
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
    # Close file handle even if it is sys.stdin, no problem here.
    pdbfh.close()
    sys.exit(0)


if __name__ == '__main__':
    main()
