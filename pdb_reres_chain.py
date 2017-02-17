#!/usr/bin/env python

"""
Renumbers residues in a PDB file starting from a given number and
for a specific chain.

usage: python pdb_reres_chain.py -<resi> -<chain> <pdb file>
example: python pdb_reres.py -1 1CTF.pdb

Author: {0} ({1})
Initial work: Joao Rodrigues (j.p.g.l.m.rodrigues@gmail.com)

This program is part of the PDB tools distributed with HADDOCK
or with the HADDOCK tutorial. The utilities in this package
can be used to quickly manipulate PDB files, with the benefit
of 'piping' several different commands. 
"""

import os
import re
import sys

__author__ = "Mikael Trellet"
__email__ = "mikael.trellet@gmail.com"

USAGE = __doc__.format(__author__, __email__)

def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options."""

    if len(args) < 2:
        # No reres or chain, from pipe
        if not sys.stdin.isatty():
            pdbfh = sys.stdin
            reres = 1
        else:
            sys.stderr.write(USAGE)
            sys.exit(1)
    elif len(args) == 2:
        # Resi & Chain & Pipe _OR_ file & no reres
        if re.match('\-[\-0-9]+', args[0]) and re.match('\-[A-Za-z0-9]+', args[1]):
            reres = int(args[0][1:])
            chain = args[1][1:]
            if not sys.stdin.isatty():
                pdbfh = sys.stdin
            else:
                sys.stderr.write(USAGE)
                sys.exit(1)
        else:
            sys.stderr.write(USAGE)
            sys.exit(1)
    elif len(args) == 3:
        # Resid & Chain & File
        if not re.match('\-[\-0-9]+', args[0]):
            sys.stderr.write('Invalid residue number: ' + args[0] + '\n')
            sys.stderr.write(USAGE)
            sys.exit(1)
        if not re.match('\-[A-Za-z0-9]+', args[1]):
            sys.stderr.write('Invalid chain ID: ' + args[1] + '\n')
            sys.stderr.write(USAGE)
            sys.exit(1)
        if not os.path.isfile(args[2]):
            sys.stderr.write('File not found: ' + args[2] + '\n')
            sys.stderr.write(USAGE)
            sys.exit(1)
        reres = int(args[0][1:])
        chain = args[1][1:]
        pdbfh = open(args[2], 'r')
    else:
        sys.stderr.write(USAGE)
        sys.exit(1)

    return (reres, chain, pdbfh)


def _renumber_chain_residue(fhandle, sresid, chain_id):
    """Enclosing logic in a function to speed up a bit"""

    resi = sresid - 1
    prev_resi = None
    coord_re = re.compile('^(ATOM|HETATM)')
    fhandle = fhandle
    chain_id = set(chain_id)

    for line in fhandle:
        if coord_re.match(line) and line[21] in chain_id:
            if line[22:26] != prev_resi:
                prev_resi = line[22:26]
                resi += 1
            yield line[:22] + str(resi).rjust(4) + line[26:]
        else:
            yield line


if __name__ == '__main__':
    # Check Input
    reres, chain, pdbfh = check_input(sys.argv[1:])
    
    # Do the job
    new_pdb = _renumber_chain_residue(pdbfh, reres, chain)

    try:
        sys.stdout.write(''.join(new_pdb))
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