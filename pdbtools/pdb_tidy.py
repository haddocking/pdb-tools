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
Modifies the file to adhere (as much as possible) to the format specifications.
Expects a sorted file - REMARK/ATOM/HETATM/END - so use pdb_sort in case you are
not sure.

This includes:
    - Adding TER statements after chain breaks/changes
    - Truncating/Padding all lines to 80 characters
    - Adds END statement at the end of the file

Will remove all original TER/END statements from the file.

Usage:
    python pdb_tidy.py <pdb file>

Example:
    python pdb_tidy.py 1CTF.pdb

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


def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options.
    """

    # Defaults
    fh = sys.stdin  # file handle

    if not len(args):
        # Reading from pipe with default option
        if sys.stdin.isatty():
            sys.stderr.write(__doc__)
            sys.exit(1)

    elif len(args) == 1:
        if not os.path.isfile(args[0]):
            emsg = 'ERROR!! File not found or not readable: \'{}\'\n'
            sys.stderr.write(emsg.format(args[0]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        fh = open(args[0], 'r')

    else:  # Whatever ...
        emsg = 'ERROR!! Script takes 1 argument, not \'{}\'\n'
        sys.stderr.write(emsg.format(len(args)))
        sys.stderr.write(__doc__)
        sys.exit(1)

    return fh


def tidy_pdbfile(fhandle):
    """Adds TER/END statements and pads all lines to 80 characters.
    """

    def make_TER(prev_line):
        """Creates a TER statement based on the last ATOM/HETATM line.
        """

        # Add last TER statement
        serial = int(prev_line[6:11]) + 1
        rname = prev_line[17:20]
        chain = prev_line[21]
        resid = prev_line[22:26]
        icode = prev_line[26]

        return fmt_TER.format(serial, rname, chain, resid, icode)

    # TER     606      LEU A  75
    fmt_TER = "TER   {:>5d}      {:3s} {:1s}{:>4s}{:1s}" + " " * 53 + "\n"
    # CONECT 1179  746 1184 1195 1203
    fmt_CONECT = "CONECT{:>5s}{:>5s}{:>5s}{:>5s}{:>5s}" + " " * 49 + "\n"
    char_ranges = (slice(6, 11), slice(11, 16),
                   slice(16, 21), slice(21, 26), slice(26, 31))

    records = ('ATOM', 'HETATM')
    ignored = ('TER', 'END ', 'END\n')
    # Iterate up to the first ATOM/HETATM line
    prev_line = None
    for line in fhandle:

        if line.startswith(ignored):  # to avoid matching END _and_ ENDMDL
            continue

        line = line.strip()  # We will pad/add \n later to make uniform

        # Check line length
        line = "{:<80}\n".format(line)

        yield line

        if line.startswith(records):
            prev_line = line
            break

    # Now go through all the remaining lines
    serial_equiv = {}  # store for conect statements
    atom_section = False
    serial_offset = 0  # To offset after adding TER records
    for line in fhandle:

        if line.startswith(ignored):
            continue

        line = line.strip()

        # Treat ATOM/HETATM differently
        #   - no TER in HETATM
        if line.startswith('ATOM'):

            is_gap = (int(line[22:26]) - int(prev_line[22:26])) > 1
            if atom_section and (line[21] != prev_line[21] or is_gap):
                serial_offset += 1  # account for TER statement
                yield make_TER(prev_line)

            serial = int(line[6:11]) + serial_offset
            line = line[:6] + str(serial).rjust(5) + line[11:]
            prev_line = line
            atom_section = True

        elif line.startswith('HETATM'):
            if atom_section:
                atom_section = False
                serial_offset += 1  # account for TER statement
                yield make_TER(prev_line)

            serial = int(line[6:11]) + serial_offset
            line = line[:6] + str(serial).rjust(5) + line[11:]
            prev_line = line

        elif line.startswith('ANISOU'):
            # Fix serial based on previous atom
            # Avoids doing the offset again
            serial = prev_line[6:11]
            line = line[:6] + str(serial).rjust(5) + line[11:]

        elif line.startswith('CONECT'):
            if atom_section:
                atom_section = False
                yield make_TER(prev_line)

            # 6:11, 11:16, 16:21, 21:26, 26:31
            serials = [line[cr] for cr in char_ranges]
            # If not found, return default
            new_serials = [str(serial_equiv.get(s, s)) for s in serials]
            conect_line = fmt_CONECT.format(*new_serials)
            yield conect_line
            continue

        else:
            if atom_section:
                atom_section = False
                yield make_TER(prev_line)

            if line.startswith('MODEL'):
                serial_offset = 0

        # Check line length
        line = "{:<80}\n".format(line)

        yield line

    else:
        if atom_section:
            # Add last TER statement
            atom_section = False
            yield make_TER(prev_line)

    # Add END statement
    yield "{:<80}\n".format("END")


def main():
    # Check Input
    pdbfh = check_input(sys.argv[1:])

    # Do the job
    new_pdb = tidy_pdbfile(pdbfh)

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
