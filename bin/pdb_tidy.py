#!/usr/bin/env python
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
Modifies the file to comply (as much as possible) with the format specifications.

This includes:
    - Adding TER statements after chain breaks/changes
    - Truncating/Padding all lines to 80 characters
    - Adds END statement at the end of the file

This will remove all original TER/END statements from the file.

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
        sys.stderr.write(__doc__)
        sys.exit(1)

    return fh


def tidy_pdbfile(fhandle):
    """Adds TER/END statements and pads all lines to 80 characters.
    """

    # TER     606      LEU A  75
    fmt_TER = "TER   {:>5d}      {:3s} {:1s}{:>4s}{:1s}" + " " * 53 + "\n"
    # CONECT 1179  746 1184 1195 1203
    fmt_CONECT = "CONECT{:>5d}{:>5d}{:>5d}{:>5d}{:>5d}" + " " * 49 + "\n"
    char_ranges = (slice(6, 11), slice(11, 16),
                   slice(16, 21), slice(21, 26), slice(26, 31))

    records = ('ATOM', 'HETATM')
    ignored = ('TER', 'END')
    conect = ('CONECT',)
    # Iterate up to the first ATOM/HETATM line
    prev_line = None
    for line in fhandle:
        if line.startswith(ignored):
            continue

        # Check line length
        line_length = len(line)
        if line_length < 80:
            num_pads = 80 - line_length + 1
            line = line + ' ' * num_pads

        yield line[:80]

        if line.startswith(records):
            prev_line = line
            break

    # Now go through all the remaining lines
    serial_equiv = {}  # store for conect statements
    coord_section = False
    serial_offset = 0  # To offset after adding TER records
    for line in fhandle:
        if line.startswith(ignored):
            continue

        elif line.startswith(records):
            coord_section = True
            is_gap = (int(line[22:26]) - int(prev_line[22:26])) > 1
            if line[21] != prev_line[21] or is_gap:
                serial = int(prev_line[6:11]) + 1
                rname = prev_line[17:20]
                chain = prev_line[21]
                resid = prev_line[22:26]
                icode = prev_line[26]

                serial_offset += 1

                ter_line = fmt_TER.format(serial, rname, chain, resid, icode)
                yield ter_line

            ori_serial = int(prev_line[6:11])
            serial = ori_serial + serial_offset

            serial_equiv[ori_serial] = serial

            line = line[:6] + str(serial).rjust(5) + line[11:]
            prev_line = line
            serial_offset = 1  # reset otherwise we have +2 ex.

        elif line.startswith(conect):
            # 6:11, 11:16, 16:21, 21:26, 26:31
            serials = [line[cr] for cr in char_ranges]
            # If not found, return default
            new_serials = [serial_equiv.get(s, s) for s in serials]
            conect_line = fmt_CONECT.format(*new_serials)
            yield conect_line
            continue

        else:
            if coord_section:
                coord_section = False
                # Add last TER statement
                serial = int(prev_line[6:11]) + 1
                rname = prev_line[17:20]
                chain = prev_line[21]
                resid = prev_line[22:26]
                icode = prev_line[26]

                ter_line = fmt_TER.format(serial, rname, chain, resid, icode)
                yield ter_line

        # Check line length
        line_length = len(line)
        if line_length < 80:
            num_pads = 80 - line_length + 1
            line = line + ' ' * num_pads

        yield line

    # Add END statement
    yield 'END' + ' ' * 77 + '\n'


if __name__ == '__main__':
    # Check Input
    pdbfh = check_input(sys.argv[1:])

    # Do the job
    new_pdb = tidy_pdbfile(pdbfh)

    try:
        sys.stdout.write(''.join(new_pdb))
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
