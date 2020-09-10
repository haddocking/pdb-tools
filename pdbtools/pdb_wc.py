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
Summarizes the contents of a PDB file, like the wc command in UNIX.

By default, this tool produces a general summary, but you can use several
options to produce focused but more detailed summaries:
    [m] - no. of models.
    [c] - no. of chains (plus per-model if multi-model file).
    [r] - no. of residues (plus per-model if multi-model file).
    [a] - no. of atoms (plus per-model if multi-model file).
    [h] - no. of HETATM (plus per-model if multi-model file).
    [o] - no. of disordered atoms (altloc) (plus per-model if multi-model file).
    [i] - no. of insertion codes (plus per-model if multi-model file).

Usage:
    python pdb_wc.py [-<option>] <pdb file>

Example:
    python pdb_wc.py 1CTF.pdb

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
    option = ''  # empty produces overall summary
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

    if option:
        valid = set('mcrahoi')
        if set(option) - valid:
            diff = ''.join(set(option) - valid)
            emsg = 'ERROR!! The following options are not valid: \'{0}\'\n'
            sys.stderr.write(emsg.format(diff))
            sys.exit(1)

    return (option, fh)


def summarize_file(fhandle, option):
    """Returns summary of models, chains, residue, and atoms.
    """

    models = set()
    chains, resids, atoms, hetatm = set(), set(), set(), set()
    has_altloc, has_icode = False, False  # flags only

    model_id = "X   "
    for line in fhandle:
        if line.startswith('MODEL'):
            model_id = line[10:14]
            models.add(model_id.strip())

        elif line.startswith('ATOM'):

            chains.add(model_id + line[21])
            resids.add(model_id + line[17:26])
            atoms.add(model_id + line[12:27])

            if line[16] != ' ':
                has_altloc = True

            if line[26] != ' ':
                has_icode = True

        elif line.startswith('HETATM'):
            chains.add(model_id + line[21])
            hetatm.add(model_id + line[12:27])

    if not models:
        models = {None}

    # Tally counts
    n_models = len(models)
    n_chains = len(chains)
    n_resids = len(resids)
    n_atoms = len(atoms)
    n_hetatm = len(hetatm)

    # Per-model
    n_atoms_pm = '{0:>6.1f}'.format(n_atoms / n_models)
    n_resids_pm = '{0:>6.1f}'.format(n_resids / n_models)
    n_chains_pm = '{0:>6.1f}'.format(n_chains / n_models)

    if not option:
        sys.stdout.write(
            'No. models:\t{0}\n'.format(n_models)
        )
        sys.stdout.write(
            'No. chains:\t{0}\t({1}/model)\n'.format(n_chains, n_chains_pm)
        )
        sys.stdout.write(
            'No. residues:\t{0}\t({1}/model)\n'.format(n_resids, n_resids_pm)
        )
        sys.stdout.write(
            'No. atoms:\t{0}\t({1}/model)\n'.format(n_atoms, n_atoms_pm)
        )
        sys.stdout.write(
            'No. HETATM:\t{0}\n'.format(n_hetatm)
        )
        sys.stdout.write(
            'Multiple Occ.:\t{0}\n'.format(has_altloc)
        )
        sys.stdout.write(
            'Res. Inserts:\t{0}\n'.format(has_icode)
        )

        return

    if 'm' in option:
        sys.stdout.write(
            'No. models:\t{0}\n'.format(n_models)
        )
        if models != {None}:
            models_str = ','.join(sorted(models, key=int))
            sys.stdout.write(
                '\t->\t{0}\n'.format(models_str)
            )

    if 'c' in option:
        sys.stdout.write(
            'No. chains:\t{0}\t({1}/model)\n'.format(n_chains, n_chains_pm)
        )
        chains_str = ','.join(sorted((c[4:] for c in chains)))
        sys.stdout.write(
            '\t->\t{0}\n'.format(chains_str)
        )

    if 'r' in option:
        sys.stdout.write(
            'No. residues:\t{0}\t({1}/model)\n'.format(n_resids, n_resids_pm)
        )
        resnames = ','.join(sorted({f[4:7].strip() for f in resids}))
        sys.stdout.write(
            '\t->\t{0}\n'.format(resnames)
        )

    if 'a' in option:
        sys.stdout.write(
            'No. atoms:\t{0}\t({1}/model)\n'.format(n_atoms, n_atoms_pm)
        )
        atnames = ','.join(sorted({repr(f[4:8]) for f in atoms}))
        sys.stdout.write(
            '\t->\t{0}\n'.format(atnames)
        )

    if 'h' in option:
        sys.stdout.write(
            'No. HETATM:\t{0}\n'.format(n_hetatm)
        )
        hetnames = ','.join(sorted({repr(f[4:7]) for f in hetatm}))
        sys.stdout.write(
            '\t->\t{0}\n'.format(hetnames)
        )

    if 'o' in option:
        sys.stdout.write(
            'Multiple Occ.:\t{0}\n'.format(has_altloc)
        )

    if 'i' in option:
        sys.stdout.write(
            'Res. Inserts:\t{0}\n'.format(has_icode)
        )


def main():
    # Check Input
    option, pdbfh = check_input(sys.argv[1:])

    # Do the job
    summarize_file(pdbfh, option)

    # last line of the script
    # We can close it even if it is sys.stdin
    pdbfh.close()
    sys.exit(0)


if __name__ == '__main__':
    main()
