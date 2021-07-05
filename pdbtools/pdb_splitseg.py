#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
Splits a PDB file into several, each containing one segment.

Usage:
    python pdb_splitseg.py <pdb file>

Example:
    python pdb_splitseg.py 1CTF.pdb

This program is part of the `pdb-tools` suite of utilities and should not be
distributed isolatedly. The `pdb-tools` were created to quickly manipulate PDB
files using the terminal, and can be used sequentially, with one tool streaming
data to another. They are based on old FORTRAN77 code that was taking too much
effort to maintain and compile. RIP.
"""

import os
import sys

__author__ = "Joao Rodrigues"
__email__ = "j.p.g.l.m.rodrigues@gmail.com"

USAGE = __doc__.format(__author__, __email__)


def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options.
    """

    # Defaults
    fh = sys.stdin  # file handle

    if not len(args):
        # Reading from pipe with default option
        if sys.stdin.isatty():
            sys.stderr.write(__doc__)
            sys.exit(1)

    elif len(args) == 1:
        if not os.path.isfile(args[0]):
            emsg = 'ERROR!! File not found or not readable: \'{}\'\n'
            sys.stderr.write(emsg.format(args[0]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        fh = open(args[0], 'r')

    else:  # Whatever ...
        emsg = 'ERROR!! Script takes 1 argument, not \'{}\'\n'
        sys.stderr.write(emsg.format(len(args)))
        sys.stderr.write(__doc__)
        sys.exit(1)

    return fh


def run(fhandle):
    """
    Split PDB into segments.

    Each segment is saved to a different file. Non-records lines are
    ignored.

    Parameters
    ----------
    fhandle : a line-by-line iterator of the original PDB file.
    """
    fname_root = fhandle.name[:-4] if fhandle.name != '<stdin>' else 'output'
    basename = os.path.basename(fname_root)

    segment_data = {}  # {segment_id: lines}

    prev_segment = None
    records = ('ATOM', 'HETATM', 'ANISOU', 'TER')
    for line in fhandle:
        if line.startswith(records):
            line_segment = line[72:76].strip()
            if line_segment != prev_segment:
                if line_segment not in segment_data:
                    segment_data[line_segment] = []
                prev_segment = line_segment
            segment_data[line_segment].append(line)

    for segment_id in sorted(segment_data.keys()):
        if not segment_id:
            continue  # skip empty segment

        lines = segment_data[segment_id]
        with open(basename + '_' + segment_id + '.pdb', 'w') as fh:
            fh.write(''.join(lines))


run = split_segment


def main():
    # Check Input
    pdbfh = check_input(sys.argv[1:])

    # Do the job
    run(pdbfh)

    # last line of the script
    # We can close it even if it is sys.stdin
    pdbfh.close()
    sys.exit(0)


if __name__ == '__main__':
    main()
