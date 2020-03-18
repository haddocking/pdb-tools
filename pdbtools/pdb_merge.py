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

The contents are not sorted and no lines are deleted (e.g. END, TER
statements) so we recommend piping the results through `pdb_tidy.py`.

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


def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options.
    """

    # Defaults
    fl = []  # file list

    if len(args) >= 1:
        for fn in args:
            if not os.path.isfile(fn):
                emsg = 'ERROR!! File not found or not readable: \'{}\'\n'
                sys.stderr.write(emsg.format(fn))
                sys.stderr.write(__doc__)
                sys.exit(1)

            fh = open(fn, 'r')
            fl.append(fh)

    else:  # Whatever ...
        sys.stderr.write(__doc__)
        sys.exit(1)

    return fl


def concatenate_files(flist):
    """Iterates over a list of files and yields each line sequentially.
    """

    for fhandle in flist:
        for line in fhandle:
            yield line
        fhandle.close()


def main():
    # Check Input
    pdbfh = check_input(sys.argv[1:])

    # Do the job
    new_pdb = concatenate_files(pdbfh)

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
