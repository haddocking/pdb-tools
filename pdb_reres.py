#!/usr/bin/env python

"""
Renumbers residues in a PDB file.

usage: python pdb_reres.py <pdb file> [-chain <ids>][-resid <int>]
example:
    python pdb_reres.py 1CTF.pdb -resid 1 # renumbers from 1, sequentially
    python pdb_reres.py 1CTF.pdb -chain -resid 1 # renumbers each chain from 1
    python pdb_reres.py 1CTF.pdb -chain A -resid 1 # renumbers chain A from 1

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


def check_input(arg_list):
    """
    Checks whether to read from stdin/file and validates user input/options.
    """
    # Dictionary to define options and default values,
    # rules to validate input values, and handlers to parse them if needed.
    # @joaomcteixeira
    user_opts = {'resid': 1, 'chain': None}  # defaults if no opt is called

    opts_defaults = {'resid': 1, 'chain': {}}  # default if opt *is* called

    rules = {'resid': re.compile('[\-0-9]+'),  # option with numeric value
             'chain': re.compile('[A-Za-z0-9,]+'),  # options with alpha value
             }

    handlers = {'resid': lambda x: int(x),
                'chain': lambda x: set(x.split(','))}

    pdbfh = None

    # First argument is always file name
    # If it is an option (or no args), assume reading from input stream
    if not arg_list or arg_list[0][0] == '-':
        if not sys.stdin.isatty():
            pdbfh = sys.stdin
        else:
            sys.stderr.write(USAGE)
            sys.exit(1)
    else:
        if not sys.stdin.isatty():
            sys.stderr.write('Error: multiple sources of input' + '\n')
            sys.exit(1)
        pdbfh = open(arg_list[0])
        arg_list = arg_list[1:]

    # Check for any combination of arguments
    n_args, skip = len(arg_list), False
    for idx, arg in enumerate(arg_list):
        if skip:
            skip = False
            continue

        # Option
        if re.match('\-', arg):
            name = arg[1:]
            # Validate option name
            if name not in rules:
                sys.stderr.write('Unrecognized option: ' + arg + '\n')
                sys.exit(1)

            rule = rules[name]

            # Validate option value (if any)
            if idx + 1 < n_args and arg_list[idx + 1][0] != '-':
                raw_val = arg_list[idx + 1]
                val = rule.match(raw_val)
                if val:
                    user_opts[name] = handlers[name](val.group(0))
                    skip = True
                else:
                    sys.stderr.write('Bad value for \'' + arg + '\': '
                                     + raw_val +'\n')
                    sys.exit(1)
            else:  # no-value option or last option
                user_opts[name] = opts_defaults[name]
        else:
            sys.stderr.write('Unrecognized option: ' + arg + '\n')
            sys.exit(1)

    return (pdbfh, user_opts)


def _renumber_pdb_residue(fhandle, opt_dict):
    """Keeping code organized ..."""

    opts = opt_dict
    resi = opts['resid'] - 1

    # if chain is none, renumber everyone
    # if chain is not none but empty, restart at each chain
    # otherwise, renumber only chain
    on_chain = opts.get('chain') is not None

    prev_chain, prev_resi = None, None
    for line in fhandle:
        if line.startswith(('ATOM', 'HETATM', 'TER')):
            if line[21] != prev_chain:
                if on_chain:
                    resi = opts['resid'] - 1
                prev_chain = line[21]

            if line[22:26] != prev_resi:
                prev_resi = line[22:26]
                resi += 1

            if not opts.get('chain') or line[21] in opts['chain']:
                yield line[:22] + str(resi).rjust(4) + line[26:]
                continue

        yield line


if __name__ == '__main__':

    # Check Input
    pdbfh, options = check_input(sys.argv[1:])

    # Do the job
    new_pdb = _renumber_pdb_residue(pdbfh, options)

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
