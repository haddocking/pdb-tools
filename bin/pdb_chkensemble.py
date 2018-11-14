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
Performs a basic check on a multi-model PDB file (ensemble) to ensure all models
have exactly the same atoms (as they should).

Usage:
    python pdb_chkensemble.py <pdb file>

Example:
    python pdb_chkensemble.py 1CTF.pdb

This program is part of the `pdb-tools` suite of utilities and should not be
distributed isolatedly. The `pdb-tools` were created to quickly manipulate PDB
files using the terminal, and can be used sequentially, with one tool streaming
data to another. They are based on old FORTRAN77 code that was taking too much
effort to maintain and compile. RIP.
"""

import itertools
import os
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
        sys.stderr.write(__doc__)
        sys.exit(1)

    return fh


def check_ensemble(fhandle):
    """Checks if the ensemble is valid.

    - Same atoms in each model
    - Paired MODEL/ENDMDL tags
    """

    model_open = False
    model_data = {}  # list of sets
    records = ('ATOM', 'HETATM', 'ANISOU', 'TER')
    for lineno, line in enumerate(fhandle):
        if line.startswith('MODEL'):
            if model_open:
                emsg = 'ERROR!! MODEL record found before ENDMDL at line \'{}\'\n'
                sys.stderr.write(emsg.format(lineno))
                sys.exit(1)

            model_open = True
            model_no = int(line[10:14])
            model_data[model_no] = set()

        elif line.startswith('ENDMDL'):
            if not model_open:
                emsg = 'ERROR!! ENDMDL record found before MODEL at line \'{}\'\n'
                sys.stderr.write(emsg.format(lineno))
                sys.exit(1)

            model_open = False
            model_no = None  # will fail to add lines if a new model is not open

        elif line.startswith(records):
            if model_no is None:
                emsg = 'ERROR!! MODEL record missing before ATOM at line \'{}\'\n'
                sys.stderr.write(emsg.format(lineno))
                sys.exit(1)

            atom_uid = line[6:27]
            model_data[model_no].add(atom_uid)

    # Verify all models have the same atoms
    bad_ensemble = False
    model_no_list = list(model_data.keys())
    for model_i, model_j in itertools.combinations(model_no_list, 2):
        atoms_i = model_data[model_i]
        atoms_j = model_data[model_j]

        difference_ij = atoms_i - atoms_j
        difference_ji = atoms_j - atoms_i

        if difference_ij or difference_ji:
            bad_ensemble = True
            msg = 'Models {} and {} differ:\n'
            sys.stderr.write(msg.format(model_i, model_j))

            if len(difference_ij):
                d_ij = sorted(difference_ij)
                msg = 'Atoms in model {} only:\n'
                sys.stderr.write(msg.format(model_i))
                sys.stderr.write('\n'.join(d_ij))

            if len(difference_ji):
                d_ji = sorted(difference_ji)
                msg = 'Atoms in model {} only:\n'
                sys.stderr.write(msg.format(model_j))
                sys.stderr.write('\n'.join(d_ji))

    if not bad_ensemble:
        n_models = len(model_data)
        msg = 'Ensemble of {} models *seems* OK\n'
        sys.stdout.write(msg.format(n_models))


def main():
    # Check Input
    pdbfh = check_input(sys.argv[1:])

    # Do the job
    check_ensemble(pdbfh)
    
    pdbfh.close()
    sys.exit(0)


if __name__ == '__main__':
    main()
