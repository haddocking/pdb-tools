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
Selects altloc labels for the entire PDB file.

By default, picks the label with the highest occupancy value for each atom,
but the user can define a specific label. Removes all labels afterwards.

Usage:
    python pdb_selaltloc.py [-<option>] <pdb file>

Example:
    python pdb_selaltloc.py 1CTF.pdb  # picks locations with highest occupancy
    python pdb_selaltloc.py -A 1CTF.pdb  # picks alternate locations labelled 'A'

This program is part of the `pdb-tools` suite of utilities and should not be
distributed isolatedly. The `pdb-tools` were created to quickly manipulate PDB
files using the terminal, and can be used sequentially, with one tool streaming
data to another. They are based on old FORTRAN77 code that was taking too much
effort to maintain and compile. RIP.
"""

import collections
import operator
import os
import sys

__author__ = "Joao Rodrigues"
__email__ = "j.p.g.l.m.rodrigues@gmail.com"


def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options.
    """

    # Defaults
    option = None
    fh = sys.stdin  # file handle

    if not len(args):
        # Reading from pipe with default option
        if sys.stdin.isatty():
            sys.stderr.write(__doc__)
            sys.exit(1)

    elif len(args) == 1:
        # One of two options: option & Pipe OR file & default option
        if args[0].startswith('-'):
            option = args[0][1:]
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
        if not args[0].startswith('-'):
            emsg = 'ERROR! First argument is not an option: \'{}\'\n'
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

    # Validate option
    if option and len(option) > 1:
        emsg = 'ERROR!! Alternate location identifiers must be single '
        emsg += 'characters: \'{}\''
        sys.stderr.write(emsg.format(option))
        sys.exit(1)

    return (option, fh)


def select_by_occupancy(fhandle):
    """Picks the altloc with the highest occupancy.
    """

    atom_prop = collections.defaultdict(list)
    atom_data = []
    anisou_lines = {}  # map atom_uid to lineno
    ignored = set()

    # Iterate over file and store atom_uid
    records = ('ATOM', 'HETATM', 'ANISOU')
    for lineno, line in enumerate(fhandle):

        atom_data.append(line)

        if line.startswith(records):
            # Sometimes altlocs are used between different residue names.
            # See 3u7t (residue 22 of chain A). So we ignore the resname below.
            atom_uid = (line[12:16], line[20:26])

            # ANISOU records do not have occupancy values.
            # To keep things simple, we map ANISOU to ATOM/HETATM records
            if line.startswith('ANISOU'):
                anisou_lines[lineno - 1] = lineno
                ignored.add(lineno)  # we will fix this below
            else:
                occ = float(line[54:60])
                atom_prop[atom_uid].append((lineno, occ))

    # Iterate and pick highest occupancy for each atom.
    for atom_uid, prop_list in atom_prop.items():
        prop_list.sort(key=operator.itemgetter(1), reverse=True)

        lineno = prop_list[0][0]

        # Edit altloc field(s)
        line = atom_data[lineno]
        atom_data[lineno] = line[:16] + ' ' + line[17:]

        if lineno in anisou_lines:
            anisou_lineno = anisou_lines[lineno]
            line = atom_data[anisou_lineno]
            atom_data[anisou_lineno] = line[:16] + ' ' + line[17:]
            ignored.discard(anisou_lineno)

        ignored.update(p[0] for p in prop_list[1:])

    # Now yield
    for lineno, line in enumerate(atom_data):
        if lineno in ignored:
            continue

        yield line


def select_by_altloc(fhandle, selloc):
    """Picks one altloc when atoms have more than one.

    If the specified altloc (selloc) is not present for this particular atom,
    outputs all altlocs. For instance, if atom X has altlocs A and B but the
    user picked C, we return A and B anyway. If atom Y has altlocs A, B, and C,
    then we only return C.
    """

    # We have to iterate multiple times
    atom_prop = collections.defaultdict(list)
    atom_data = []

    # Iterate over file and store atom_uid
    records = ('ATOM', 'HETATM', 'ANISOU')
    editable = set()
    for lineno, line in enumerate(fhandle):

        atom_data.append(line)

        if line.startswith(records):
            # Sometimes altlocs are used between different residue names.
            # See 3u7t (residue 22 of chain A). So we ignore the resname below.
            atom_uid = (line[12:16], line[20:26])

            altloc = line[16]
            atom_prop[atom_uid].append((altloc, lineno))

            if altloc == selloc:  # flag as editable
                editable.add(lineno)

    # Reduce editable indexes to atom_uid entries
    editable = {
        (atom_data[i][12:16], atom_data[i][20:26]) for i in editable
    }

    # Now define lines to ignore in the output
    ignored = set()
    for atom_uid in editable:
        for altloc, lineno in atom_prop[atom_uid]:
            if altloc != selloc:
                ignored.add(lineno)
            else:
                # Edit altloc field
                line = atom_data[lineno]
                atom_data[lineno] = line[:16] + ' ' + line[17:]

    # Iterate again and yield the correct lines.
    for lineno, line in enumerate(atom_data):
        if lineno in ignored:
            continue

        yield line


def main():
    # Check Input
    option, pdbfh = check_input(sys.argv[1:])

    # Do the job
    if option is None:
        new_pdb = select_by_occupancy(pdbfh)
    else:
        new_pdb = select_by_altloc(pdbfh, option)

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
