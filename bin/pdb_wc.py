#!/usr/bin/env python
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

Several options are available to produce only partial summaries:
    [m] - no. of models.
    [c] - no. of chains (plus per-model if multi-model file).
    [r] - no. of residues (plus per-model if multi-model file).
    [a] - no. of atoms (plus per-model if multi-model file).
    [h] - no. of HETATM (plus per-model if multi-model file).
    [o] - no. of disordered atoms (altloc) (plus per-model if multi-model file).
    [i] - no. of insertion codes (plus per-model if multi-model file).
    [g] - presence/absence of gaps (discontinuous residue numbering).

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

from __future__ import division

import os
import sys

__author__ = "Joao Rodrigues"
__email__ = "j.p.g.l.m.rodrigues@gmail.com"

USAGE = __doc__.format(__author__, __email__)


def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options.
    """

    # Defaults
    option = 'mcrahoig'
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
    if option == '':
        option = 'mcrahoig'

    valid = set('mcrahoig')
    if set(option) - valid:
        diff = ''.join(set(option) - valid)
        emsg = 'ERROR!! The following options are not valid: \'{}\'\n'
        sys.stderr.write(emsg.format(diff))
        sys.exit(1)

    return (option, fh)


def summarize_file(fhandle, option):
    """Returns a count of models, chains, residue, and atoms.
    """

    n_models, n_chains, n_residues, n_atoms = 0, 0, 0, 0
    n_hetatm, n_altloc, n_inscodes, n_rgaps = 0, 0, 0, 0

    prev_chain, prev_res = None, None
    for line in fhandle:
        if line.startswith('MODEL'):
            n_models += 1

        elif line.startswith('ATOM'):
            res_uid = line[17:26]
            if res_uid != prev_res:
                n_residues += 1
                prev_res = res_uid

            chain_uid = line[21]
            if chain_uid != prev_chain:
                n_chains += 1
                prev_chain = chain_uid

            if line[16] != ' ':
                n_altloc += 1

            if line[26] != ' ':
                n_inscodes += 1

            if (int(line[22:26]) - int(prev_res[5:])) > 1:
                n_rgaps += 1

            n_atoms += 1

        elif line.startswith('HETATM'):
            n_hetatm += 1

    if n_models == 0 and n_atoms > 0:
        n_models = 1

    # Per-model
    n_atom_pm = '{0:>6.1f}'.format(n_atoms / n_models)
    n_resi_pm = '{0:>6.1f}'.format(n_residues / n_models)
    n_chain_pm = '{0:>6.1f}'.format(n_chains / n_models)

    # Booleans
    has_gaps = bool(n_rgaps)
    has_altloc = bool(n_altloc)
    has_icode = bool(n_inscodes)

    if 'm' in option:
        print('No. models:\t{0}'.format(n_models))
    if 'c' in option:
        print('No. chains:\t{0}\t({1}/model)'.format(n_chains, n_chain_pm))
    if 'r' in option:
        print('No. residues:\t{0}\t({1}/model)'.format(n_residues, n_resi_pm))
    if 'a' in option:
        print('No. atoms:\t{0}\t({1}/model)'.format(n_atoms, n_atom_pm))
    if 'h' in option:
        print('No. HETATM:\t{0}'.format(n_hetatm))
    if 'o' in option:
        print('Multiple Occ.:\t{0}'.format(has_altloc))
    if 'i' in option:
        print('Res. Inserts:\t{0}'.format(has_icode))
    if 'g' in option:
        print('Has seq. gaps:\t{0}'.format(has_gaps))

if __name__ == '__main__':

    # Check Input
    option, pdbfh = check_input(sys.argv[1:])

    # Do the job
    summarize_file(pdbfh, option)

    # last line of the script
    # We can close it even if it is sys.stdin
    pdbfh.close()
    sys.exit(0)


# #!/usr/bin/env python

# """
# Summarizes the contents of a PDB file.

# usage: python pdb_wc.py -[acrmHgdiA] <pdb file>
# example: python pdb_wc.py 1CTF.pdb

# Author: {0} ({1})

# This program is part of the PDB tools distributed with HADDOCK
# or with the HADDOCK tutorial. The utilities in this package
# can be used to quickly manipulate PDB files, with the benefit
# of 'piping' several different commands. This is a rewrite of old
# FORTRAN77 code that was taking too much effort to compile. RIP.
# """

# from __future__ import print_function, division

# import os
# import re
# import sys

# __author__ = "Joao Rodrigues"
# __email__ = "j.p.g.l.m.rodrigues@gmail.com"

# USAGE = __doc__.format(__author__, __email__)


# def check_input(args):
#     """
#     Checks whether to read from stdin/file and validates user input/options.
#     """

#     if not len(args):
#         # No option, from pipe
#         if not sys.stdin.isatty():
#             pdbfh = sys.stdin
#             option = 'A'
#         else:
#             sys.stderr.write(USAGE)
#             sys.exit(1)
#     elif len(args) == 1:
#         # option & Pipe _or_ file
#         if re.match('\-[acrmHgdiA]', args[0]):
#             option = args[0][1]
#             if not sys.stdin.isatty():
#                 pdbfh = sys.stdin
#             else:
#                 sys.stderr.write(USAGE)
#                 sys.exit(1)
#         else:
#             if not os.path.isfile(args[0]):
#                 sys.stderr.write('File not found: ' + args[0] + '\n')
#                 sys.stderr.write(USAGE)
#                 sys.exit(1)
#             pdbfh = open(args[0], 'r')
#             option = 'A'
#     elif len(args) == 2:
#         # option & File
#         if not re.match('\-[acrmHgdiA]', args[0]):
#             sys.stderr.write('Invalid option: ' + args[0] + '\n')
#             sys.stderr.write(USAGE)
#             sys.exit(1)
#         if not os.path.isfile(args[1]):
#             sys.stderr.write('File not found: ' + args[1] + '\n')
#             sys.stderr.write(USAGE)
#             sys.exit(1)
#         option = args[0][1]
#         pdbfh = open(args[1], 'r')
#     else:
#         sys.stderr.write(USAGE)
#         sys.exit(1)

#     return (option, pdbfh)


# def _summarize(fhandle, option):
#     """Enclosing logic in a function"""

#     option = option

#     n_models = 0
#     has_hetero, has_gaps, has_double, has_insert = "No", "No", "No", "No"
#     at_list, res_list, chain_list = [], [], []
#     prev_resuid, prev_chainid = None, None

#     gap_check = True
#     for line in fhandle:
#         line = line.strip()

#         record = line[0:6]

#         if record == 'HETATM':
#             has_hetero = "Yes"

#         if record.startswith('ENDMDL'):
#             gap_check = False

#         if record.startswith('MODEL'):
#             n_models += 1

#         if record == 'ATOM  ':
#             if not n_models:
#                 n_models += 1

#             res_uid = (line[17:20], line[21], int(line[22:26]))
#             at_uid = (line[12:16],
#                       line[16],
#                       line[17:20],
#                       line[21],
#                       line[22:26])
#             chain_uid = line[21]

#             if res_uid != prev_resuid:
#                 if prev_chainid == line[21] and \
#                    prev_resuid and \
#                    res_uid[2] - 1 != prev_resuid[2]:

#                     if gap_check:
#                         has_gaps = "Yes"
#                     else:
#                         gap_check = True

#                 prev_resuid = res_uid
#                 res_list.append(res_uid)

#             if line[21] != prev_chainid:
#                 prev_chainid = line[21]
#                 chain_list.append(chain_uid)

#             altloc = line[16]
#             if altloc != ' ':
#                 has_double = "Yes"

#             resinsert = line[26]
#             if resinsert != ' ':
#                 has_insert = "Yes"

#             at_list.append(at_uid)

#     n_atm, nu_atm = len(at_list), len(set(at_list))
#     n_res, nu_res = len(res_list), len(set(res_list))
#     n_chn, nu_chn = len(chain_list), len(set(chain_list))

    if option == 'a':
        print(n_atm, nu_atm)
    elif option == 'r':
        print(n_res, nu_res)
    elif option == 'c':
        print(n_chn, nu_chn)
    elif option == 'm':
        print(n_models)
    elif option == 'H':
        print(has_hetero)
    elif option == 'g':
        print(has_gaps)
    elif option == 'd':
        print(has_double)
    elif option == 'i':
        print(has_insert)
    elif option == 'A':
        print('No. atoms:\t{0}\t({1:4.1f}/model)'.format(n_atm, nu_atm))
        print('No. residues:\t{0}\t({1:4.1f}/model)'.format(n_res, nu_res))
        print('No. chains:\t{0}\t({1:4.1f}/model)'.format(n_chn, nu_chn))
        print('No. models:\t{0}'.format(n_models))
        print('Hetero Atoms:\t{0}'.format(has_hetero))
        print('Has seq. gaps:\t{0}'.format(has_gaps))
        print('Double Occ.:\t{0}'.format(has_double))
        print('Insertions:\t{0}'.format(has_insert))


# if __name__ == '__main__':

#     # Check Input
#     option, pdbfh = check_input(sys.argv[1:])

#     # Do the job
#     _summarize(pdbfh, option)

#     # last line of the script
#     # We can close it even if it is sys.stdin
#     pdbfh.close()
#     sys.exit(0)
