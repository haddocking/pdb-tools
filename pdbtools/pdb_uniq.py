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
Lists the (unique) names of chains or residues in the structure as
comma-separated values.

Several options are available to produce only partial lists:
    [c] - chain names
    [r] - residue names

Usage:
    python pdb_uniq.py [-<option>] <pdb file>

Example:
    python pdb_uniq.py 1BRS.pdb
    python pdb_uniq.py -c 1BRS.pdb  # will list "A, B, C, D, E, F"

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
    option = 'cr'
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
                emsg = 'ERROR!! File not found or not readable: \'{0}\'\n'
                sys.stderr.write(emsg.format(args[0]))
                sys.stderr.write(__doc__)
                sys.exit(1)

            fh = open(args[0], 'r')

    elif len(args) == 2:
        # Two options: option & File
        if not args[0].startswith('-'):
            emsg = 'ERROR! First argument is not an option: \'{0}\'\n'
            sys.stderr.write(emsg.format(args[0]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        if not os.path.isfile(args[1]):
            emsg = 'ERROR!! File not found or not readable: \'{0}\'\n'
            sys.stderr.write(emsg.format(args[1]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        option = args[0][1:]
        fh = open(args[1], 'r')

    else:  # Whatever ...
        sys.stderr.write(__doc__)
        sys.exit(1)

    # Validate option
    if option == '':
        option = 'cr'

    valid = set('cr')
    if set(option) - valid:
        diff = ''.join(set(option) - valid)
        emsg = 'ERROR!! The following options are not valid: \'{0}\'\n'
        sys.stderr.write(emsg.format(diff))
        sys.exit(1)

    return (option, fh)


def list_unique(fhandle, option):
    """Returns unique chain and residue names.
    """

    # Do not use just a set. Preserve order.
    chainid_set = set()
    resname_set = set()
    chainid_list = []
    resname_list = []

    records = ('ATOM', 'HETATM')
    for line in fhandle:
        if line.startswith(records):

            chain_name = line[21]
            if chain_name not in chainid_set:
                chainid_set.add(chain_name)
                chainid_list.append(chain_name)

            resid_name = line[17:20]
            if resid_name not in resname_set:
                resname_set.add(resid_name)
                resname_list.append(resid_name)

    if 'c' in option:
        csv_chainid = ','.join(chainid_list)
        sys.stdout.write('Chains: {0}\n'.format(csv_chainid))
    if 'r' in option:
        csv_resname = ','.join(resname_list)
        sys.stdout.write('Residues: {0}\n'.format(csv_resname))


def main():
    # Check Input
    option, pdbfh = check_input(sys.argv[1:])

    # Do the job
    list_unique(pdbfh, option)

    # last line of the script
    # We can close it even if it is sys.stdin
    pdbfh.close()
    sys.exit(0)


if __name__ == '__main__':
    main()
