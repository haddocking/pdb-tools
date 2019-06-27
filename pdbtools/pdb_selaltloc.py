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
Picks one location for each atom with fractional occupancy values. By default,
picks the atom with the highest occupancy value. User can define one specific
location using an option.

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

import os
import sys

__author__ = "Joao Rodrigues"
__email__ = "j.p.g.l.m.rodrigues@gmail.com"


def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options.
    """

    # Defaults
    option = ''
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
    if len(option) > 1:
        emsg = 'ERROR!! Alternate location identifiers must be single '
        emsg += 'characters: \'{}\''
        sys.stderr.write(emsg.format(option))
        sys.exit(1)

    return (option, fh)


def select_occupancy(fhandle, option):
    """Picks one occupancy when atoms have more than one.

    By default checks the occupancy line for the atom with the highest value.
    Otherwise, the user can provide a specific label ('A', 'B', etc.)
    """

    # Filter functions
    def pick_by_altloc(line, altloc):
        """Selects atom lines based on altloc (or none, in case there is none)
        """
        if line[16] == altloc or line[16] == ' ':
            return line

    def pick_by_occupancy(data, *args):
        """Selects atom lines based on highest occupancy value.
        """
        data.sort(key=lambda l: float(l[54:60]), reverse=True)
        return data[0]

    if option == '':  # Get occupancy
        get_prop = lambda l: float(l[54:60])
        sel_prop = lambda d: sorted(d, key=lambda x: x[1], reverse=True)[0]
    else:  # get altloc
        option_set = set((option, ' '))
        get_prop = lambda l: l[16]
        sel_prop = lambda d: [l for l in d if l[1] in option_set][0]

    # We have to iterate multiple times
    atom_prop = {}  # {atom_uid: (lineno, prop)}
    atom_data = []

    # Iterate over file and store atom_uid
    records = ('ATOM', 'HETATM')
    for line in fhandle:

        atom_data.append(line)

        if line.startswith(records):
            atom_uid = (line[12:16], line[17:26])
            atom_full_uid = line[12:26]
            prop = get_prop(line)

            if atom_uid in atom_prop:
                atom_prop[atom_uid].append((atom_full_uid, prop))
            else:
                atom_prop[atom_uid] = [(atom_full_uid, prop)]

    # Filter atom_prop
    sel_atoms = set()
    for key, prop_list in atom_prop.items():
        selected = sel_prop(prop_list)
        sel_atoms.add(selected[0])  # atom_full_uid

    # Iterate again and yield the right one
    records = ('ATOM', 'HETATM', 'ANISOU')  # we can filter ANISOU too
    for lineno, line in enumerate(atom_data):
        if line.startswith(records):
            if line[12:26] in sel_atoms:
                yield line[:16] + ' ' + line[17:]  # clear altloc
            continue

        yield line


def main():
    # Check Input
    option, pdbfh = check_input(sys.argv[1:])

    # Do the job
    new_pdb = select_occupancy(pdbfh, option)

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
