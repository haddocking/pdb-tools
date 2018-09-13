#!/usr/bin/env python

"""
Concatenates PDB files ordering chains according to input.

Residue names are maintained and HETATMS are written at the end
keeping information on the chain they belong.

usage: python pdb_concat.py <pdb files> 
example:
    python pdb_concat.py 1.pdb 2.pdb 3.pdb > new.pdb
    python pdb_concat *.pdb > new.pdb

Author: {0} ({1})

This program is part of the PDB tools distributed with HADDOCK
or with the HADDOCK tutorial. The utilities in this package
can be used to quickly manipulate PDB files, with the benefit
of 'piping' several different commands. This is a rewrite of old
FORTRAN77 code that was taking too much effort to compile. RIP.
"""

import os
import sys
import re
import string
import itertools as it

__author__ = "Joao M.C. Teixeira"
__email__ = "joaomcteixeira@gmail.com"

USAGE = __doc__.format(__author__, __email__)

def check_input(args):
    """
    Checks whether to read from stdin/file and validates user input/options.
    """
    
    if not len(args):
        sys.stderr.write(USAGE)
        sys.exit(1)
    elif len(args) >= 1:
        for file_name in args:
            if not os.path.isfile(file_name):
                sys.stderr.write('File not found: ' + file_name + '\n')
                sys.stderr.write(USAGE)
                sys.exit(1)
    else:
        sys.stderr.write(USAGE)
        sys.exit(1)
    
    return args

def _concatenate_pdbs(pdbfnlh):
    """
    Concatenates PDBs in a single PDB file.
    
    PDBs with multiple chains are also read.
    
    Parameters:
        - pdbfnlh (list of str): list of file names to process.
    """
    # reads only ATOM and HETATOM lines
    coord_re = re.compile('^(ATOM|HETATM)')
    
    for file_name in pdbfnlh:
        
        with open(file_name, 'rU') as handle:
            for line in handle:
                if coord_re.match(line):
                    yield line

if __name__ == '__main__':

    # Check Input
    # PDB file list handler
    pdbfnlh = check_input(sys.argv[1:])

    # Do the job
    new_pdb = _concatenate_pdbs(pdbfnlh)

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
    sys.exit(0)

