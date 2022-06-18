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
Renames chain identifiers sequentially, based on TER records.

Since HETATM records are not separated by TER records and usually come together
at the end of the PDB file, this script will attempt to reassign their chain
identifiers based on the changes it made to ATOM lines. This might lead to bad
output in certain corner cases.

Usage:
    python pdb_chainbows.py <pdb file>

Example:
    python pdb_chainbows.py 1CTF.pdb

This program is part of the `pdb-tools` suite of utilities and should not be
distributed isolatedly. The `pdb-tools` were created to quickly manipulate PDB
files using the terminal, and can be used sequentially, with one tool streaming
data to another. They are based on old FORTRAN77 code that was taking too much
effort to maintain and compile. RIP.
"""

import os
import string
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


def run(fhandle):
    """
    Set chains sequentially based on existing TER records.

    Follow sequence [ABC...abc...012...].

    This function is a generator.

    Parameters
    ----------
    fhandle : an iterable giving the PDB file line-by-line

    Yields
    ------
    str (line-by-line)
        The modified (or not) PDB line.
    """
    chainlist = list(
        string.digits[::-1] + string.ascii_lowercase[::-1] + string.ascii_uppercase[::-1]
    )  # 987...zyx...cbaZYX...BCA.
    max_chains = len(chainlist)

    chain_map = {}  # for HETATM.

    curchain = chainlist.pop()
    records = ('ATOM', 'TER', 'ANISOU')
    for line in fhandle:
        if line.startswith(records):
            chain_map[line[21]] = curchain
            line = line[:21] + curchain + line[22:]

            if line.startswith('TER'):
                try:
                    curchain = chainlist.pop()
                except IndexError:
                    emsg = 'ERROR!! Structure contains more than {} TER records.\n'
                    sys.stderr.write(emsg.format(max_chains))
                    sys.stderr.write(__doc__)
                    sys.exit(1)

        elif line.startswith('HETATM'):
            hetchain = chain_map[line[21]]
            line = line[:21] + hetchain + line[22:]

        yield line


set_chain_sequence = run


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
