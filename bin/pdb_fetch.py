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
Downloads a structure in PDB format from the RCSB website. Allows downloading
the (first) biological structure if selected.

Usage:
    python pdb_fetch.py [-biounit] <pdb code>

Example:
    python pdb_fetch.py 1brs  # downloads unit cell, all 6 chains
    python pdb_fetch.py -biounit 1brs  # downloads biounit, 2 chains

This program is part of the `pdb-tools` suite of utilities and should not be
distributed isolatedly. The `pdb-tools` were created to quickly manipulate PDB
files using the terminal, and can be used sequentially, with one tool streaming
data to another. They are based on old FORTRAN77 code that was taking too much
effort to maintain and compile. RIP.
"""

import gzip
import re
import sys

# Python 3 vs Python 2
if sys.version_info[0] < 3:
    from cStringIO import StringIO as IO
    from urllib2 import Request, build_opener
    from urllib2 import HTTPError
else:
    from io import BytesIO as IO
    from urllib.request import Request, build_opener
    from urllib.error import HTTPError

__author__ = "Joao Rodrigues"
__email__ = "j.p.g.l.m.rodrigues@gmail.com"


def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options.
    """

    # Defaults
    option = False

    if len(args) == 1:
        # pdb code only
        if not re.match('[0-9a-zA-Z]{4}$', args[0]):
            emsg = 'ERROR!! Invalid PDB code: \'{}\'\n'
            sys.stderr.write(emsg.format(args[0]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        pdb_code = args[0]

    elif len(args) == 2:
        # biounit & pdb code
        if not re.match('\-biounit$', args[0]):
            emsg = 'ERROR!! Invalid option: \'{}\'\n'
            sys.stderr.write(emsg.format(args[0]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        if not re.match('[0-9a-zA-Z]{4}$', args[1]):
            emsg = 'ERROR!! Invalid PDB code: \'{}\'\n'
            sys.stderr.write(emsg.format(args[0]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        option = True
        pdb_code = args[1]
    else:
        sys.stderr.write(__doc__)
        sys.exit(1)

    return (pdb_code, option)


def fetch_structure(pdbid, biounit=False):
    """Downloads the structure in PDB format from the RCSB PDB website.
    """

    base_url = 'https://files.rcsb.org/download/'
    pdb_type = '.pdb1' if biounit else '.pdb'
    pdb_url = base_url + pdbid.lower() + pdb_type + '.gz'

    try:
        request = Request(pdb_url)
        opener = build_opener()
        url_data = opener.open(request).read()

    except HTTPError as e:
        emsg = '[!] Error fetching structure: ({0}) {1}\n'
        sys.stderr.write(emsg.format(e.code, e.msg))
        return

    else:

        try:
            buf = IO(url_data)
            gz_handle = gzip.GzipFile(fileobj=buf, mode='rb')
            for line in gz_handle:
                yield line.decode('utf-8')

        except IOError as e:
            emsg = '[!] Error fetching structure: ({0}) {1}\n'
            sys.stderr.write(emsg.format(e.code, e.msg))
            return

        finally:
            gz_handle.close()


if __name__ == '__main__':
    # Check Input
    pdb_code, biounit = check_input(sys.argv[1:])

    # Do the job
    new_pdb = fetch_structure(pdb_code, biounit)

    try:
        sys.stdout.write(''.join(new_pdb))
        sys.stdout.flush()
    except IOError:
        # This is here to catch Broken Pipes
        # for example to use 'head' or 'tail' without
        # the error message showing up
        pass

    sys.exit(0)
