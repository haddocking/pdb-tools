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
Changes residue names in the PDB file, replacing one name by another.

Usage:
    python pdb_resrename.py -<from> -<to> <pdb file>

Example:
    python pdb_resrename.py -HIP -HIS 1CTF.pdb  # changes all HIP residues to HIS

This program is part of the `pdb-tools` suite of utilities and should not be
distributed isolatedly. The `pdb-tools` were created to quickly manipulate PDB
files using the terminal, and can be used sequentially, with one tool streaming
data to another. They are based on old FORTRAN77 code that was taking too much
effort to maintain and compile. RIP.
"""

import os
import sys

__author__ = ["Joao Rodrigues", "Joao M.C. Teixeira"]
__email__ = ["j.p.g.l.m.rodrigues@gmail.com", "joaomcteixeira@gmail.com"]


def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options.
    """

    # Defaults
    name_to, name_from = None, None
    fh = sys.stdin  # file handle

    if len(args) == 2:
        # -to and -from and read file from stdin
        if args[0].startswith('-'):
            name_to = args[0][1:]
        else:
            emsg = 'ERROR! First argument is not an option: \'{}\'\n'
            sys.stderr.write(emsg.format(args[0]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        if args[1].startswith('-'):
            name_from = args[1][1:]
        else:
            emsg = 'ERROR! Second argument is not an option: \'{}\'\n'
            sys.stderr.write(emsg.format(args[1]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        if sys.stdin.isatty():  # ensure the PDB data is streamed in
            emsg = 'ERROR!! No data to process!\n'
            sys.stderr.write(emsg)
            sys.stderr.write(__doc__)
            sys.exit(1)

    elif len(args) == 3:
        # -to and -from and filename
        if args[0].startswith('-'):
            name_from = args[0][1:]
        else:
            emsg = 'ERROR! First argument is not an option: \'{}\'\n'
            sys.stderr.write(emsg.format(args[0]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        if args[1].startswith('-'):
            name_to = args[1][1:]
        else:
            emsg = 'ERROR! Second argument is not an option: \'{}\'\n'
            sys.stderr.write(emsg.format(args[0]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        if not os.path.isfile(args[2]):
            emsg = 'ERROR!! File not found or not readable: \'{}\'\n'
            sys.stderr.write(emsg.format(args[0]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        fh = open(args[2], 'r')

    else:  # Whatever ...
        sys.stderr.write(__doc__)
        sys.exit(1)

    # Validate options
    if len(name_from) > 3:
        emsg = 'ERROR!! Residue name must be at most three characters: \'{}\'\n'
        sys.stderr.write(emsg.format(name_from))
        sys.exit(1)

    if len(name_to) > 3:
        emsg = 'ERROR!! Residue name must be at most three characters: \'{}\'\n'
        sys.stderr.write(emsg.format(name_to))
        sys.exit(1)

    return (name_from, name_to, fh)


def rename_residues(fhandle, name_from, name_to):
    """Changes the residue name of residues matching a pattern to another.
    """

    records = ('ATOM', 'HETATM', 'TER', 'ANISOU')
    for line in fhandle:
        if line.startswith(records):
            line_resname = line[17:20]
            if line_resname == name_from:
                yield line[:17] + name_to.rjust(3) + line[20:]
                continue
        yield line


if __name__ == '__main__':

    # Check Input
    name_from, name_to, pdbfh = check_input(sys.argv[1:])

    # Do the job
    new_pdb = rename_residues(pdbfh, name_from, name_to)

    # Output results
    try:
        sys.stdout.write(''.join(new_pdb))
        sys.stdout.flush()
    except IOError:
        # This is here to catch Broken Pipes
        # for example to use 'head' or 'tail' without
        # the error message showing up
        pass

    # last line of the script
    # Close file handle even if it is sys.stdin, no problem here.
    pdbfh.close()
    sys.exit(0)
