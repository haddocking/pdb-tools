#!/usr/bin/env python

"""
Fetches a PDB file (optionally the biological unit) from the RCSB database.

usage: python pdb_fetch.py [-biounit] <pdb id>
example: python pdb_fetch.py 1CTF

Author: {0} ({1})

This program is part of the PDB tools distributed with HADDOCK
or with the HADDOCK tutorial. The utilities in this package
can be used to quickly manipulate PDB files, with the benefit
of 'piping' several different commands. This is a rewrite of old
FORTRAN77 code that was taking too much effort to compile. RIP.
"""

from __future__ import print_function

import gzip
import os
import re
import sys
import cStringIO
import urllib2

__author__ = "Joao Rodrigues"
__email__ = "j.p.g.l.m.rodrigues@gmail.com"

USAGE = __doc__.format(__author__, __email__)

def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options."""

    if len(args) == 1:
        if not re.match('[0-9a-zA-Z]{4}$', args[0]):
            sys.stderr.write('Invalid PDB code: ' + args[0] + '\n')
            sys.stderr.write(USAGE)
            sys.exit(1)
        pdb_id = args[0]
        biounit = False
    elif len(args) == 2:
        # Chain & File
        if not re.match('\-biounit$', args[0]):
            sys.stderr.write('Invalid option: ' + args[0] + '\n')
            sys.stderr.write(USAGE)
            sys.exit(1)
        if not re.match('[0-9a-zA-Z]{4}$', args[1]):
            sys.stderr.write('Invalid PDB code: ' + args[1] + '\n')
            sys.stderr.write(USAGE)
            sys.exit(1)
        biounit = True
        pdb_id = args[1]
    else:
        sys.stderr.write(USAGE)
        sys.exit(1)

    return (pdb_id, biounit)

def _fetch_structure(pdbid, biounit=False):
    """Enclosing logic in a function"""

    base_url = 'http://www.rcsb.org/pdb/files/'
    pdb_type = '.pdb1' if biounit else '.pdb'
    pdb_url = base_url + pdbid.lower() + pdb_type + '.gz'

    try:
        request = urllib2.Request(pdb_url)
        opener = urllib2.build_opener()
        url_data = opener.open(request).read()
    except urllib2.HTTPError as e:
        print('[!] Error fetching structure: ({0}) {1}'.format(e.code, e.msg), file=sys.stderr)
        return
    else:
        try:
            buf = cStringIO.StringIO(url_data)
            gz_handle = gzip.GzipFile(fileobj=buf, mode='rb')
            for line in gz_handle:
                yield line
        except IOError as e:
            print('[!] Error fetching structure: {0}'.format(e.msg), file=sys.stderr)
            return
        finally:
            gz_handle.close()

if __name__ == '__main__':

    # Check Input
    pdb_id, biounit = check_input(sys.argv[1:])

    # Do the job
    pdb_structure = _fetch_structure(pdb_id, biounit)
    if not pdb_structure:
        sys.exit(1)

    try:
        sys.stdout.write(''.join(pdb_structure))
        sys.stdout.flush()
    except IOError:
        # This is here to catch Broken Pipes
        # for example to use 'head' or 'tail' without
        # the error message showing up
        pass

    # last line of the script
    # We can close it even if it is sys.stdin
    sys.exit(0)
