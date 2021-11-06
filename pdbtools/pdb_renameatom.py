#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2021 João MC Teixeira
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
Renames all atoms matching the given name in the PDB file by a new name.

Atom names are matched *without* taking into consideration spaces, so ' CA '
(alpha carbon) and 'CA  ' (calcium) will both be renamed if -CA is passed.

Usage:
    python pdb_selatom.py -<option> <pdb file>

Example:
    python pdb_renameatom.py -1HB,HB2 1CTF.pdb  # renames '1HB' to 'HB2'

This program is part of the `pdb-tools` suite of utilities and should not be
distributed isolatedly. The `pdb-tools` were created to quickly manipulate PDB
files using the terminal, and can be used sequentially, with one tool streaming
data to another. They are based on old FORTRAN77 code that was taking too much
effort to maintain and compile. RIP.
"""
import os
import sys

__author__ = ["Joao M.C. Teixeira"]
__email__ = ["joaomcteixeira@gmail.com"]


def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options.
    """
    if not args:
        emsg = 'ERROR! No input provided{}'
        sys.stderr.write(emsg.format(os.linesep))
        sys.stderr.write(__doc__)
        sys.exit(1)

    if len(args) > 2:
        emsg = 'ERROR! Too many arguments.'
        sys.stderr.write(emsg)
        sys.stderr.write(__doc__)
        sys.exit(1)

    # The first argument is mandatory, you always need to select an atom
    if not args[0].startswith('-'):
        emsg = 'ERROR! First argument is not an option: \'{}\'{}'
        sys.stderr.write(emsg.format(args[0], os.linesep))
        sys.stderr.write(__doc__)
        sys.exit(1)

    # atom names have at most 4 characters
    option = args[0][1:].split(',')
    if len(option) != 2:
        emsg = 'ERROR! You need to provide two atom names: source and target.{}'
        sys.stderr.write(emsg.format(os.linesep))
        sys.stderr.write(__doc__)
        sys.exit(1)

    if any(len(atom_name) > 4 for atom_name in option):
        emsg = 'ERROR!! Atom names have maximum 4 characters: \'{}\'{}'
        sys.stderr.write(emsg.format(args[0], os.linesep))
        sys.stderr.write(__doc__)
        sys.exit(1)

    # Pipe or file
    if sys.stdin.isatty():  # ensure the PDB data is streamed in
        if len(args) == 1:
            emsg = 'ERROR!! No file provided.'
            sys.stderr.write(emsg)
            sys.stderr.write(__doc__)
            sys.exit(1)

        if not os.path.isfile(args[1]):
            emsg = 'ERROR!! File not found or not readable: \'{}\'{}'
            emsg = emsg.format(args[1], os.linesep)
            sys.stderr.write(emsg)
            sys.stderr.write(__doc__)
            sys.exit(1)

    fh = open(args[1], 'r')
    return fh, option


def run(fhandle, source, target):
    """
    Rename selected atoms

    This function is a generator.

    Atom names are matched *without* taking into consideration spaces,
    so ' CA ' (alpha carbon) and 'CA  ' (calcium) will both be renamed
    if -CA is passed.

    Parameters
    ----------
    fhandle : a line-by-line iterator of the original PDB file.

    source : the atom name to change.

    target : the new atom name.

    Yields
    ------
    str (line-by-line)
        All non-RECORD lines and RECORD lines within the selected atom
        names.
    """
    records = ('ATOM', 'HETATM', 'ANISOU')
    # try/catch block is added here to avoid creating it every line
    try:
        for line in fhandle:
            if line.startswith(records):
                atom_source = line[12:16].strip()
                element = line[76:78].strip()
                if atom_source == source:
                    new_name = format_atom_name(target, element)
                    line = line[:12] + new_name + line[16:]
            yield line

    except KeyError as err:
        _ = f'Could not format this atom:type -> {atom_source}:{element}'
        raise KeyError(_) from err


# string formats for atom name depending on element
_3 = ' {:<3s}'
_4 = '{:<4s}'
_atom_format_dict = {
    0: { 1: _4, 2: _4, 3: _4, 4: _4},  # uses for spaces if element not present
    1: { 1: _3, 2: _3, 3: _3, 4: _4},
    2: { 1: _4, 2: _4, 3: _4, 4: _4},
    }


def format_atom_name(atom, element, AFD=_atom_format_dict):
    """
    Format PDB Record line Atom name.

    Further Reading:

    * https://www.cgl.ucsf.edu/chimera/docs/UsersGuide/tutorials/pdbintro.html

    Parameters
    ----------
    atom : str
        The atom name.

    element : str
        The atom element code.

    Returns
    -------
    str
        Formatted atom name.
    """
    len_atm = len(atom)
    len_ele = len(element)
    return AFD[len_ele][len_atm].format(atom)


renameatom = run


def main():
    # Check Input
    pdbfh, option = check_input(sys.argv[1:])

    # Do the job
    new_pdb = run(pdbfh, *option)

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
