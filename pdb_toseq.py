#!/usr/bin/env python

"""
Extracts the sequence of a PDB file in FASTA format

usage: python pdb_toseq.py <pdb file>
example: python pdb_toseq.py 1CTF.pdb

Author: {0} ({1})

This program is part of the PDB tools distributed with HADDOCK
or with the HADDOCK tutorial. The utilities in this package
can be used to quickly manipulate PDB files, with the benefit
of 'piping' several different commands. This is a rewrite of old
FORTRAN77 code that was taking too much effort to compile. RIP.
"""

import os
import sys

__author__ = "Joao Rodrigues"
__email__ = "j.p.g.l.m.rodrigues@gmail.com"

USAGE = __doc__.format(__author__, __email__)

def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options."""

    if not len(args):
        # No chain, from pipe
        if not sys.stdin.isatty():
            pdbfh = sys.stdin
            pdbfn = 'APDB'
        else:
            sys.stderr.write(USAGE)
            sys.exit(1)
    elif len(args) == 1:
        if not os.path.isfile(args[0]):
            sys.stderr.write('File not found: ' + args[0] + '\n')
            sys.stderr.write(USAGE)
            sys.exit(1)
        pdbfh = open(args[0], 'rU')
        pdbfn = os.path.basename(args[0])[:-4]
    else:
        sys.stderr.write(USAGE)
        sys.exit(1)

    return (pdbfn, pdbfh)

def _get_sequence(fhandle):
    """Enclosing logic in a function to simplify code"""

    res_codes = [
                # 20 canonical amino acids
                ('CYS', 'C'), ('ASP', 'D'), ('SER', 'S'), ('GLN', 'Q'),
               	('LYS', 'K'), ('ILE', 'I'), ('PRO', 'P'), ('THR', 'T'),
                ('PHE', 'F'), ('ASN', 'N'), ('GLY', 'G'), ('HIS', 'H'),
               	('LEU', 'L'), ('ARG', 'R'), ('TRP', 'W'), ('ALA', 'A'),
               	('VAL', 'V'), ('GLU', 'E'), ('TYR', 'Y'), ('MET', 'M'),
                # Non-canonical amino acids
               	#('MSE', 'M'), ('SOC', 'C'),
                # Canonical xNA
                ('  U', 'U'), ('  A', 'A'), ('  G', 'G'), ('  C', 'C'),
                ('  T', 'T'),
               ]

    three_to_one = dict(res_codes)
    _records = set(['ATOM  ', 'HETATM'])

    fhandle = fhandle
    sequence = {}
    read = set()
    for line in fhandle:
        line = line.strip()
        if line[0:6] in _records:

            resn = line[17:20]
            chain = line[21]
            resi = line[22:26]
            icode = line[26]
            r_uid = (resn, chain, resi, icode)
            if r_uid not in read:
                read.add(r_uid)
            else:
                continue

            aa_resn = three_to_one.get(resn, 'X')
            if chain not in sequence:
                sequence[chain] = []

            sequence[chain].append(aa_resn)

    return sequence

if __name__ == '__main__':
    # Check Input
    pdbfn, pdbfh = check_input(sys.argv[1:])

    # Do the job
    pdb_seq = _get_sequence(pdbfh)

    try:
        for chain in pdb_seq:
            seq = ''.join(pdb_seq[chain])
            fmt_seq = [seq[i:i+80]+'\n' for i in range(0, len(seq), 80)]
            msg = ">{0}_{1}\n{2}".format(pdbfn, chain, ''.join(fmt_seq))
            sys.stdout.write(msg)
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
