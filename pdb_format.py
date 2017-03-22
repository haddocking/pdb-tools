#!/usr/bin/env python

"""
Validates each ATOM/HETATM line against the 'official' PDB format specification.

usage: python pdb_format.py <pdb file>
example: python pdb_format.py 1CTF.pdb

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

__author__ = "Joao Rodrigues"
__email__ = "j.p.g.l.m.rodrigues@gmail.com"

USAGE = __doc__.format(__author__, __email__)

def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options."""

    if not len(args):
        # Read from pipe
        if not sys.stdin.isatty():
            pdbfh = sys.stdin
        else:
            sys.stderr.write(USAGE)
            sys.exit(1)
    elif len(args) == 1:
        # File
        if not os.path.isfile(args[0]):
            sys.stderr.write('File not found: ' + args[0] + '\n')
            sys.stderr.write(USAGE)
            sys.exit(1)
        pdbfh = open(args[0], 'r')
    else:
        sys.stderr.write(USAGE)
        sys.exit(1)

    return pdbfh

def _check_pdb_format(fhandle):
    """
    Compares each ATOM/HETATM line with the format defined on the official
    PDB website.

    http://deposit.rcsb.org/adit/docs/pdb_atom_format.html
    """

    has_error = False
    _format_check = (
                      ('Atm. Num.', (slice(6,11), re.compile('[\d\s]+'))),
                      ('Alt. Loc.', (slice(11,12), re.compile('\s'))),
                      ('Atm. Nam.', (slice(12,16), re.compile('\s*[A-Z0-9]+\s*'))),
                      ('Spacer #1', (slice(16,17), re.compile('[A-Z0-9 ]{1}'))),
                      ('Res. Nam.', (slice(17,20), re.compile('\s*[A-Z0-9]+\s*'))),
                      ('Spacer #2', (slice(20, 21), re.compile('\s'))),
                      ('Chain Id.', (slice(21, 22), re.compile('[A-Za-z0-9 ]{1}'))),
                      ('Res. Num.', (slice(22,26), re.compile('\s*[\d]+\s*'))),
                      ('Ins. Code', (slice(26,27), re.compile('[A-Z0-9 ]{1}'))),
                      ('Spacer #3', (slice(27,30), re.compile('\s+'))),
                      ('Coordn. X', (slice(30,38), re.compile('\s*[\d\.\-]+\s*'))),
                      ('Coordn. Y', (slice(38,46), re.compile('\s*[\d\.\-]+\s*'))),
                      ('Coordn. Z', (slice(46,54), re.compile('\s*[\d\.\-]+\s*'))),
                      ('Occupancy', (slice(54,60), re.compile('\s*[\d\.\-]+\s*'))),
                      ('Tmp. Fac.', (slice(60,66), re.compile('\s*[\d\.\-]+\s*'))),
                      ('Spacer #4', (slice(66,72), re.compile('\s+'))),
                      ('Segm. Id.', (slice(72,76), re.compile('[\sA-Z0-9\-\+]+'))),
                      ('At. Elemt', (slice(76,78), re.compile('[\sA-Z0-9\-\+]+'))),
                      ('At. Charg', (slice(78,80), re.compile('[\sA-Z0-9\-\+]+'))),
                    )

    for iline, line in enumerate(fhandle, start=1):
        line = line.rstrip('\n').rstrip('\r') # CR/LF
        if not line:
            continue

        # Type check for ATOM/HETATM lines
        if line[0:6] in ('ATOM  ', 'HETATM'):
            s_of_line = len(line)
            if s_of_line < 80:
                print('[!] Line {0} too short: is {1} instead of 80'.format(iline, s_of_line))
                has_error = True

            elif s_of_line > 80:
                print('[!] Line {0} too long: is {1} instead of 80'.format(iline, s_of_line))
                has_error = True

            for fname, (fcol, fcheck) in _format_check:
                field = line[fcol]
                if not fcheck.match(field):
                    pointer = ''.join(['^' if c in range(fcol.start+1, fcol.stop) else ' ' for c in xrange(80)])
                    print('[!] Offending field ({0}) at line {1}'.format(fname, iline))
                    print('{0!r}'.format(line))
                    print('{0}'.format(pointer))
                    has_error = True
                    break

    if has_error:
        print('\nTo understand your errors, read the format specification:')
        print('  http://deposit.rcsb.org/adit/docs/pdb_atom_format.html')
    else:
        print('It *seems* everything is OK.')

if __name__ == '__main__':

    # Check Input
    pdbfh = check_input(sys.argv[1:])

    # Do the job

    _check_pdb_format(pdbfh)

    # last line of the script
    # We can close it even if it is sys.stdin
    pdbfh.close()
    sys.exit(0)
