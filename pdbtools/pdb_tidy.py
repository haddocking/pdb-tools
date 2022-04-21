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
    python pdb_tidy.py [-strict] <pdb file>

Example:
    python pdb_tidy.py 1CTF.pdb
    python pdb_tidy.py -strict 1CTF.pdb  # does not add TER on chain breaks

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
    option = False
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

        else:
            if not os.path.isfile(args[0]):
                emsg = 'ERROR!! File not found or not readable: \'{}\'\n'
                sys.stderr.write(emsg.format(args[0]))
                sys.stderr.write(__doc__)
                sys.exit(1)

            fh = open(args[0], 'r')

    elif len(args) == 2:
        # Two options: option & File
        if not args[0] == '-strict':
            emsg = 'ERROR! First argument is not a valid option: \'{}\'\n'
            sys.stderr.write(emsg.format(args[0]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        if not os.path.isfile(args[1]):
            emsg = 'ERROR!! File not found or not readable: \'{}\'\n'
            sys.stderr.write(emsg.format(args[1]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        option = args[0][1:]
        fh = open(args[1], 'r')

    else:  # Whatever ...
        sys.stderr.write(__doc__)
        sys.exit(1)

    return (fh, option)


def run(fhandle, strict=False):
    """
    Add TER/END statements and pads all lines to 80 characters.

    This function is a generator.

    Parameters
    ----------
    fhandle : a line-by-line iterator of the original PDB file.

    strict : bool
        If True, does not add TER statements at intra-chain breaks.

    Yields
    ------
    str (line-by-line)
        The modified (or not) PDB line.
    """
    not_strict = not strict

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

        # Check line length
        line = "{:<80}\n".format(line)

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
            serial = int(prev_line[6:11])
            line = line[:6] + str(serial).rjust(5) + line[11:]

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


        if serial > 99999:
            emsg = 'ERROR!! Structure contains more than 99.999 atoms.\n'
            sys.stderr.write(emsg)
            sys.stderr.write(__doc__)
            sys.exit(1)

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
    pdbfh, strict = check_input(sys.argv[1:])

    # Do the job
    new_pdb = run(pdbfh, strict)

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
