#!/usr/bin/env python

"""
Joins several conformations of the same structure in one ensemble file.

usage: python pdb_join.py <pdb file> <pdb file> ...
example: python pdb_join.py 1CTF_01.pdb 1CTF_02.pdb

Author: {0} ({1})

This program is part of the PDB tools distributed with HADDOCK
or with the HADDOCK tutorial. The utilities in this package
can be used to quickly manipulate PDB files, with the benefit
of 'piping' several different commands. This is a rewrite of old
FORTRAN77 code that was taking too much effort to compile. RIP.
"""

import os
import re
import sys

__author__ = "Joao Rodrigues"
__email__ = "j.p.g.l.m.rodrigues@gmail.com"

USAGE = __doc__.format(__author__, __email__)

def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options."""

    if len(args) < 2:
        sys.stderr.write(USAGE)
        sys.exit(1)

    for pdb_f in args:
        if not os.path.isfile(pdb_f):
            sys.stderr.write('File could not be read: ' + pdb_f + '\n')
            sys.exit(1)

    return args

def _build_atom_unique_id(atom_line):
    """Returns a unique identifying tuple from an ATOM line"""

    # unique_id: (name, altloc, resi, insert, chain, segid)
    unique_id = (atom_line[12:16], atom_line[16], int(atom_line[22:26]), atom_line[26], atom_line[21], atom_line[72:76].strip())
    return unique_id

def _join_pdb(pdb_list):
    """Enclosing logic in a function"""

    auid = _build_atom_unique_id

    coord_re = re.compile('^(ATOM|HETATM)')
    pdb_list = pdb_list
    atom_set = set()
    pdb_data, remarks = [], []
    for i_model, pdb_f in enumerate(pdb_list, start=1):
        model_auids = set()
        remarks.append('REMARK  {0}'.format(os.path.basename(pdb_f)))
        pdb_data.append('MODEL     {0:>4d}'.format(i_model))
        with open(pdb_f, 'r') as handle:
            for line in handle:
                line = line.strip()
                if coord_re.match(line):
                    pdb_data.append(line)
                    model_auids.add(auid(line))
        pdb_data.append('ENDMDL')

        if atom_set:
            diff = atom_set - model_auids
            if diff:
                emsg = 'Different atoms in model {0}\n'.format(i_model)
                sys.stderr.write(emsg)
                sys.exit(1)
        else:
            atom_set = model_auids

    pdb_data.append('END')
    pdb_data = remarks + pdb_data
    return pdb_data

if __name__ == '__main__':
    # Check Input
    pdb_list = check_input(sys.argv[1:])

    # Do the job
    ensemble = _join_pdb(pdb_list)

    try:
        sys.stdout.write('\n'.join(ensemble))
        sys.stdout.flush()
    except IOError:
        # This is here to catch Broken Pipes
        # for example to use 'head' or 'tail' without
        # the error message showing up
        pass

    # last line of the script
    # We can close it even if it is sys.stdin
    sys.exit(0)
