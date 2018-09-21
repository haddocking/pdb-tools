#!/usr/bin/env python

"""
Sorts the whole PDB file: chains -> residues -> atoms.

usage: python pdb_sort.py -[cra] <pdb file>
example:
    python pdb_sort.py 1CTF.pdb
    python pdb_sort.py -c 1CTF.pdb
    python pdb_sort.py -cr 1CTF.pdb

OPTIONS:

    : if no option if given sort applies to chains -> residues -> atoms.
    : -c, sorts only chains,
    : -r, sorts only residues, chain order is not altered,
    : -a, sorts only atoms, chain and residues are not altered.

Author: {0} ({1})

This program is part of the PDB tools distributed with HADDOCK
or with the HADDOCK tutorial. The utilities in this package
can be used to quickly manipulate PDB files, with the benefit
of 'piping' several different commands. This is a rewrite of old
FORTRAN77 code that was taking too much effort to compile. RIP.
"""

from __future__ import print_function

import os
import re
import sys

__author__ = "Joao M.C. Teixeira"
__email__ = "joaomcteixeira@gmail.com"

USAGE = __doc__.format(__author__, __email__)


def check_input(args):
    """
    Checks whether to read from stdin/file and validates user input/options.
    """

    if not len(args):
        # Read from pipe
        if not sys.stdin.isatty():
            pdbfh = sys.stdin
            option = "cra"
        else:
            sys.stderr.write(USAGE)
            sys.exit(1)
    elif len(args) == 1:
        # option & Pipe _or_ file
        if args[0].startswith('-') \
                and all(re.match('[cra]', c) for c in args[0][1:]):
            option = args[0][1:]
            if not sys.stdin.isatty():
                pdbfh = sys.stdin
            else:
                sys.stderr.write(USAGE)
                sys.exit(1)
        else:
            if not os.path.isfile(args[0]):
                sys.stderr.write('File not found: ' + args[0] + '\n')
                sys.stderr.write(USAGE)
                sys.exit(1)
            pdbfh = open(args[0], 'r')
            option = 'cra'
    elif len(args) == 2:
        # option & File
        if not (args[0].startswith('-') \
                and all(re.match('[cra]', c) for c in args[0][1:])):
            sys.stderr.write('Invalid option: ' + args[0] + '\n')
            sys.stderr.write(USAGE)
            sys.exit(1)
        if not os.path.isfile(args[1]):
            sys.stderr.write('File not found: ' + args[1] + '\n')
            sys.stderr.write(USAGE)
            sys.exit(1)
        option = args[0][1:]
        pdbfh = open(args[1])
    else:
        sys.stderr.write(USAGE)
        sys.exit(1)

    return (option, pdbfh)


def _sort_chains(fhandle, options):
    """Enclosing logic in a function"""
    
    # atom_line = df.loc[:,]
    
    # for option in options:
        
    
    
    
    # coord_re = re.compile('^(ATOM|HETATM)')
    # chain_dump = dict()
    # prev_chain = None
    
    # # stores chain info in dictionary where keys are chain ids
    # for line in fhandle:
        # if not coord_re.match(line):
            # continue
        
        # chain_id = line[21]
        
        # if chain_id != prev_chain:
            # chain_dump.setdefault(chain_id, "")
        
        # chain_dump[chain_id] += line
        
    # for chain in sorted(chain_dump.keys()):
        # yield chain_dump[chain]

if __name__ == '__main__':
    
    # Check Input
    option, pdbfh = check_input(sys.argv[1:])
    
    # Do the job
    new_pdb = _sort_chains(pdbfh, option)

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
