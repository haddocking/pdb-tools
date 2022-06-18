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
Checks all models in a multi-model PDB file have the same composition.

Composition is defined as same atoms/residues/chains.

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
        if sys.stdin.closed or sys.stdin.isatty():
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
    Check if the ensemble is valid.

    - Same atoms in each model
    - Paired MODEL/ENDMDL tags

    Parameters
    ----------
    fhandle : a line-by-line iterator of the original PDB file.

    Returns
    -------
    int
        1 if an error was found. 0 if no errors are found.
    """
    model_open = False
    model_no = None
    model_data = {}  # list of sets
    records = ('ATOM', 'HETATM', 'ANISOU', 'TER')
    for lineno, line in enumerate(fhandle):
        if line.startswith('MODEL'):
            if model_open:
                emsg = 'ERROR!! MODEL record found before ENDMDL at line \'{}\'\n'
                sys.stderr.write(emsg.format(lineno))
                return 1

            model_open = True
            model_no = int(line[10:14])
            model_data[model_no] = set()

        elif line.startswith('ENDMDL'):
            if not model_open:
                emsg = 'ERROR!! ENDMDL record found before MODEL at line \'{}\'\n'
                sys.stderr.write(emsg.format(lineno))
                return 1

            model_open = False
            model_no = None  # will fail to add lines if a new model is not open

        elif line.startswith(records):
            if not model_open:
                emsg = 'ERROR!! MODEL record missing before ATOM at line \'{}\'\n'
                sys.stderr.write(emsg.format(lineno))
                return 1

            atom_uid = line[6:27]
            model_data[model_no].add(atom_uid)
        else:
            if model_open:  # Missing last ENDMDL
                emsg = 'ERROR!! ENDMDL record missing at line \'{}\'\n'
                sys.stderr.write(emsg.format(lineno))
                return 1

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
        return 0

    return 1


check_ensemble = run


def main():
    # Check Input
    pdbfh = check_input(sys.argv[1:])

    # Do the job
    status_code = check_ensemble(pdbfh)

    pdbfh.close()
    sys.exit(status_code)


if __name__ == '__main__':
    main()
