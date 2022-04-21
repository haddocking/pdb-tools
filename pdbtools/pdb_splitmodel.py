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
Splits a PDB file into several, each containing one MODEL.

Usage:
    python pdb_splitmodel.py <pdb file>

Example:
    python pdb_splitmodel.py 1CTF.pdb

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

USAGE = __doc__.format(__author__, __email__)


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


def run(fhandle, outname=None):
    """
    Split PDB into MODELS.

    Each MODELS is saved to a different file. Non-records lines are
    ignored.

    Parameters
    ----------
    fhandle : a line-by-line iterator of the original PDB file.

    outname : str
        The base name of the output files. If None is given, tries to
        extract a name from the `.name` attribute of `fhandler`. If
        `fhandler` has no attribute name, assigns `splitmodels`.
    """
    _defname = 'splitmodels'
    if outname is None:
        try:
            fn = fhandle.name
            outname = fn[:-4] if fn != '<stdin>' else _defname
        except AttributeError:
            outname = _defname

    basename = os.path.basename(outname)

    model_lines = []
    records = ('ATOM', 'HETATM', 'ANISOU', 'TER')
    for line in fhandle:
        if line.startswith('MODEL'):
            model_no = line[10:14].strip()
            fh = open(basename + '_' + model_no + '.pdb', 'w')
            model_lines = []

        elif line.startswith('ENDMDL'):
            fh.write(''.join(model_lines))
            fh.close()

        elif line.startswith(records):
            model_lines.append(line)


split_model = run


def main():
    # Check Input
    pdbfh = check_input(sys.argv[1:])

    # Do the job
    run(pdbfh)

    # last line of the script
    # We can close it even if it is sys.stdin
    pdbfh.close()
    sys.exit(0)


if __name__ == '__main__':
    main()
