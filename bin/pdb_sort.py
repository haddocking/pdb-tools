#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 João Pedro Rodrigues & João M. C. Teixeira
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
Sorts the ATOM/HETATM/ANISOU/CONECT records in a PDB file.

Atoms are always sorted by their serial number, meaning the original ordering
of the atoms within each residue are not changed. Alternate locations are sorted
by default.

Residues are sorted according to their residue sequence number and then by their
insertion code (if any).

Chains are sorted by their chain identifier.

Finally, the file is sorted by all keys, and the records are placed in the
following order:
    - ATOM/ANISOU, intercalated if the latter exist
    - HETATM
    - CONECT, sorted by the serial number of the central (first) atom

MASTER, TER, END statements are removed. Headers (HEADER, REMARK, etc) are kept
and placed first. Does NOT support multi-model files. Use pdb_splitmodel, then
pdb_sort on each model, and then pdb_mkensemble.

Usage:
    python pdb_sort.py -<option> <pdb file>

Example:
    python pdb_sort.py 1CTF.pdb  # sorts by chain and residues
    python pdb_sort.py -C 1CTF.pdb  # sorts by chain (A, B, C ...) only
    python pdb_sort.py -R 1CTF.pdb  # sorts by residue number/icode only

This program is part of the `pdb-tools` suite of utilities and should not be
distributed isolatedly. The `pdb-tools` were created to quickly manipulate PDB
files using the terminal, and can be used sequentially, with one tool streaming
data to another. They are based on old FORTRAN77 code that was taking too much
effort to maintain and compile. RIP.
"""

import os
import sys

__author__ = ["Joao Rodrigues", "Joao M.C. Teixeira"]
__email__ = ["j.p.g.l.m.rodrigues@gmail.com", "joaomcteixeira@gmail.com"]


def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options.
    """

    # Defaults
    option = 'CR'
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
    option = [o.upper() for o in option]
    valid = set('CR')
    for item in option:
        if item not in valid:
            emsg = 'ERROR!! Sorting key is not valid: \'{}\'\n'
            sys.stderr.write(emsg.format(item))
            sys.stderr.write(__doc__)
            sys.exit(1)

    return (option, fh)


def sort_file(fhandle, sorting_keys):
    """Sorts the contents of the PDB file.
    """

    # Sort keys
    chain_key = lambda x: x[21]  # chain id
    resid_key = lambda x: (int(x[22:26]), x[26])  # resid, icode
    atoms_key = lambda x: int(x[6:11])  # atom serial
    altloc_key = lambda x: x[16]
    icode_key = lambda x: x[26]

    # ignored fields
    ignored = (('END', 'MASTER', 'TER'))

    # First, separate records
    header_data = []
    atomic_data = []
    hetatm_data = []
    anisou_data = {}  # Matches a unique atom uid
    conect_data = []
    chains_list = []  # list of chain identifiers in order they were read
    for line in fhandle:
        if line.startswith('ATOM'):
            atomic_data.append(line)
            chains_list.append(line[21])
        elif line.startswith('HETATM'):
            hetatm_data.append(line)
            chains_list.append(line[21])
        elif line.startswith('ANISOU'):
            atom_uid = line[12:27]  # aname, chain, resid, resname, & alt/icode
            anisou_data[atom_uid] = line
        elif line.startswith('CONECT'):
            conect_data.append(line)
        elif line.startswith(ignored):
            continue
        elif line.startswith(('MODEL', 'ENDMDL')):
            emsg = 'ERROR!! Sorting does not support multi-model files\n'
            sys.stderr.write(emsg)
            sys.stderr.write(__doc__)
            sys.exit(1)
        elif line.strip():  # remove empty lines
            header_data.append(line)

    # Map original chain orders to integers
    # To circumvent mixed chains when sorting by residue number
    chain_order = {}
    ordinal = 0
    for chain in chains_list:
        if chain not in chain_order:
            chain_order[chain] = ordinal
            ordinal += 1
    del chains_list

    # Always sort by altloc
    atomic_data.sort(key=atoms_key)
    atomic_data.sort(key=altloc_key)
    hetatm_data.sort(key=atoms_key)
    hetatm_data.sort(key=altloc_key)

    if 'R' in sorting_keys:
        atomic_data.sort(key=icode_key)
        atomic_data.sort(key=resid_key)
        hetatm_data.sort(key=icode_key)
        hetatm_data.sort(key=resid_key)

    if 'C' in sorting_keys:
        atomic_data.sort(key=chain_key)
        hetatm_data.sort(key=chain_key)
    else:  # restore original order
        chain_key = lambda x: chain_order.get(x[21])
        atomic_data.sort(key=chain_key)
        hetatm_data.sort(key=chain_key)

    # Sort conect statements by the central atom
    # Share the same format at ATOM serial number
    conect_data.sort(key=atoms_key)

    # Now return everything in order:
    #  - ATOMs intercalated with ANISOU
    #  - HETATM
    #  - CONECT
    sorted_data = header_data + atomic_data + hetatm_data + conect_data
    for line in sorted_data:

        yield line

        atom_uid = line[12:27]
        anisou_record = anisou_data.get(atom_uid)
        if anisou_record:
            yield anisou_record


def main():
    # Check Input
    chain, pdbfh = check_input(sys.argv[1:])

    # Do the job
    new_pdb = sort_file(pdbfh, chain)

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
