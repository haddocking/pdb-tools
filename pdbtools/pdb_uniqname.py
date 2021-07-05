#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2020 João Pedro Rodrigues
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
Renames atoms sequentially (C1, C2, O1, ...) for each HETATM residue.

Relies on an element column being present (see pdb_element).

Usage:
    python pdb_uniqname.py <pdb file>

Example:
    python pdb_uniqname.py 1CTF.pdb

This program is part of the `pdb-tools` suite of utilities and should not be
distributed isolatedly. The `pdb-tools` were created to quickly manipulate PDB
files using the terminal, and can be used sequentially, with one tool streaming
data to another. They are based on old FORTRAN77 code that was taking too much
effort to maintain and compile. RIP.
"""

import collections
import os
import sys

__author__ = ["Joao Rodrigues"]
__email__ = ["j.p.g.l.m.rodrigues@gmail.com"]


def check_input(args):
    """Checks whether to read from stdin/file.
    """

    # Defaults
    fh = sys.stdin  # file handle

    if not len(args):
        # Reading from pipe
        if sys.stdin.isatty():
            sys.stderr.write(__doc__)
            sys.exit(1)

    elif len(args) == 1:
        # Input File
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


def run(fhandle):
    """
    Rename HETATM atoms on each residue based on their element.

    This function is a generator.

    Parameters
    ----------
    fhandle : a line-by-line iterator of the original PDB file.

    Yields
    ------
    str (line-by-line)
        The modified (or not) PDB line.
    """
    prev_res = None
    for line_idx, line in enumerate(fhandle):
        if line.startswith('HETATM'):

            element = line[76:78].strip()

            if not element:
                emsg = 'ERROR!! No element found in line {}'.format(line_idx)
                sys.stderr.write(emsg)
                sys.exit(1)

            resuid = line[17:27]

            if prev_res != resuid:
                prev_res = resuid
                element_idx = collections.defaultdict(lambda: 1)  # i.e. a counter

            spacer = ' ' if len(element) == 1 else ''
            name = (spacer + element + str(element_idx[element])).ljust(4)
            line = line[:12] + name + line[16:]

            element_idx[element] += 1

        yield line


rename_atoms = run


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

    # last line of the script
    # We can close it even if it is sys.stdin
    pdbfh.close()
    sys.exit(0)


if __name__ == '__main__':
    main()
