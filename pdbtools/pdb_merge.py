#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 João M. C. Teixeira
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
Merges several PDB files into one.

Use `pdb_mkensemble` if you with to make an ensemble of multiple
conformation states of the same protein.

Follows the criteria:

    * The merged PDB file will represent a single MODEL.
    * Non-coordinate lines in input PDBs will be ignored.
    * Atom numbers are restarted from 1.
    * CONECT lines are yield at the end. CONECT numbers are updated to
        the new atom numbers.
    * Missing TER and END statements are placed accordingly. Original
        TER and END statements are maintained.

Usage:
    python pdb_merge.py <pdb file> <pdb file>

Example:
    python pdb_merge.py 1ABC.pdb 1XYZ.pdb

This program is part of the `pdb-tools` suite of utilities and should not be
distributed isolatedly. The `pdb-tools` were created to quickly manipulate PDB
files using the terminal, and can be used sequentially, with one tool streaming
data to another. They are based on old FORTRAN77 code that was taking too much
effort to maintain and compile. RIP.
"""

import os
import sys

__author__ = "Joao M.C. Teixeira"
__email__ = "joaomcteixeira@gmail.com"


# Python 2.7 compatibility
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options.
    """

    # Defaults
    fl = []  # file list

    if len(args) == 1:
        sys.stderr.write('ERROR!! Please provide more than one input file.')
        sys.stderr.write(__doc__)
        sys.exit(1)

    elif len(args) >= 1:
        for fn in args:
            if not os.path.isfile(fn):
                emsg = 'ERROR!! File not found or not readable: \'{}\'\n'
                sys.stderr.write(emsg.format(fn))
                sys.stderr.write(__doc__)
                sys.exit(1)

            fl.append(fn)

    else:  # Whatever ...
        sys.stderr.write(__doc__)
        sys.exit(1)

    return fl


# TER     606      LEU A  75
_fmt_TER = "TER   {:>5d}      {:3s} {:1s}{:>4s}{:1s}" + " " * 53 + os.linesep


def make_TER(prev_line, fmt_TER=_fmt_TER):
    """Creates a TER statement based on the last ATOM/HETATM line."""
    # Add last TER statement
    serial = int(prev_line[6:11]) + 1
    rname = prev_line[17:20]
    chain = prev_line[21]
    resid = prev_line[22:26]
    icode = prev_line[26]

    return fmt_TER.format(serial, rname, chain, resid, icode)


def _get_lines_from_input(pinput, i=0):
    """Decide wheter input is file or lines."""
    try:
        return open(pinput, 'r')
    except (FileNotFoundError, TypeError):
        return pinput


def _update_atom_number(line, number, anisou=('ANISOU',)):
    if line.startswith(anisou):
        number -= 1
    return line[:6] + str(number).rjust(5) + line[11:]


def run(input_list):
    """
    Merges PDB files into a single file.

    Follows the criteria:

        * The merged PDB file will represent a single MODEL.
        * Non-coordinate lines will be ignored.
        * Atom numbers are restarted from 1.
        * CONECT lines are yield at the end. CONECT numbers are updated
          to the new atom numbers.
        * TER and END statements are placed accordingly.

    Use `pdb_mkensemble` if you with to make an ensemble of multiple
    conformation states of the same protein.

    Parameters
    ----------
    input_list : iterator of iterators
        `input_list` can be:
            * a list of file paths
            * a list of file handlers
            * a list of lists of lines, the latter representing the
                content of the different input PDB files

    Yields
    ------
    str (line-by-line)
        Lines from the merged PDB files.
    """
    records = ('ATOM', 'HETATM', 'ANISOU', 'CONECT', 'MODEL', 'ENDMDL')
    atom_anisou = ('ATOM', 'ANISOU')
    atom_hetatm = ('ATOM', 'HETATM')
    hetatm = ('HETATM',)
    conect = ('CONECT',)
    prev_chain = None
    chain = None
    prev_line = ''
    conect_lines = []

    # CONECT logic taken from pdb_preatom
    fmt_CONECT = "CONECT{:>5s}{:>5s}{:>5s}{:>5s}{:>5s}" + " " * 49 + os.linesep
    char_ranges = (
        slice(6, 11),
        slice(11, 16),
        slice(16, 21),
        slice(21, 26),
        slice(26, 31),
    )
    atom_number = 1

    for input_item in input_list:

        lines = _get_lines_from_input(input_item)

        # store for CONECT statements
        # restart at each PDB. Read docs above
        serial_equiv = {'': ''}

        for line in lines:

            if not line.startswith(records):
                continue

            chain = line[21]

            if line.startswith(atom_hetatm):
                serial_equiv[line[6:11].strip()] = atom_number

            if \
                    line.startswith(hetatm) \
                    and prev_line.startswith(atom_anisou):

                yield _update_atom_number(make_TER(prev_line), atom_number)
                atom_number += 1

            elif \
                    prev_chain is not None \
                    and chain != prev_chain \
                    and prev_line.startswith(atom_anisou):

                yield _update_atom_number(make_TER(prev_line), atom_number)
                atom_number += 1

            elif line.startswith(conect):

                # 6:11, 11:16, 16:21, 21:26, 26:31
                serials = (line[cr].strip() for cr in char_ranges)

                # If not found, return default
                new_serials = (str(serial_equiv.get(s, s)) for s in serials)
                conect_line = fmt_CONECT.format(*new_serials)

                conect_lines.append(conect_line)

                continue

            elif not line.strip(os.linesep).strip():
                continue

            yield _update_atom_number(line, atom_number)
            atom_number += 1

            prev_line = line
            prev_chain = chain

        try:
            lines.close()
        except AttributeError:
            pass

    for line in conect_lines:
        yield line

    yield 'END' + os.linesep


concatenate_files = run


def main():
    # Check Input
    pdbfh = check_input(sys.argv[1:])

    # Do the job
    new_pdb = run(pdbfh)

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

    sys.exit(0)


if __name__ == '__main__':
    main()
