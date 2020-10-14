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
Selects residues by their index, piecewise or in a range.

The range option has three components: start, end, and step. Start and end
are optional and if ommitted the range will start at the first residue or
end at the last, respectively.

Usage:
    python pdb_selres.py -[resid]:[resid]:[step] <pdb file>

Example:
    python pdb_selres.py -1,2,4,6 1CTF.pdb # Extracts residues 1, 2, 4 and 6
    python pdb_selres.py -1:10 1CTF.pdb # Extracts residues 1 to 10
    python pdb_selres.py -1:10,20:30 1CTF.pdb # Extracts residues 1 to 10 and 20 to 30
    python pdb_selres.py -1: 1CTF.pdb # Extracts residues 1 to END
    python pdb_selres.py -:5 1CTF.pdb # Extracts residues from START to 5.
    python pdb_selres.py -::5 1CTF.pdb # Extracts every 5th residue
    python pdb_selres.py -1:10:5 1CTF.pdb # Extracts every 5th residue from 1 to 10

This program is part of the `pdb-tools` suite of utilities and should not be
distributed isolatedly. The `pdb-tools` were created to quickly manipulate PDB
files using the terminal, and can be used sequentially, with one tool streaming
data to another. They are based on old FORTRAN77 code that was taking too much
effort to maintain and compile. RIP.
"""

from itertools import chain as iter_chain
import os
import sys

__author__ = "Joao Rodrigues"
__email__ = "j.p.g.l.m.rodrigues@gmail.com"


def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options.
    """

    # Options can be single numbers or ranges.
    def _validate_opt_numeric(value):
        """Returns a valid numerical option or dies trying"""
        try:
            num = int(value)
        except ValueError:
            emsg = "ERROR!! Not a valid number: '{}'\n"
            sys.stderr.write(emsg.format(value))
            sys.exit(1)
        else:
            # resid 4-char limit
            if (-999 <= num < 10000):
                return num
            else:
                emsg = "ERROR!! Residue numbers must be between -999 and 9999: '{}'\n"
                sys.stderr.write(emsg.format(value))
                sys.exit(1)

    def _validate_opt_range(value, resid_list):
        """Returns a numerical range or dies trying"""

        # Validate formatting
        if not (1 <= value.count(':') <= 2):
            emsg = "ERROR!! Residue range must be in 'a:z:s' where a and z are "
            emsg += 'optional (default to first residue and last respectively), and'
            emsg += 's is an optional step value (to return every s-th residue).\n'
            sys.stderr.write(emsg)
            sys.exit(1)

        start, end, step = None, None, 1
        slices = [_validate_opt_numeric(num)
                  if num.strip() else None for num in value.split(':')]

        if len(slices) == 3:
            start, end, step = slices
        elif len(slices) == 2:
            start, end = slices
        elif len(slices) == 1:
            if value.startswith(':'):
                end = slices[0]
            else:
                start = slices[0]

        # Upper/Lower limits, resid max 4 char
        if start is None:
            start = -1000
        if end is None:
            end = 10000

        # extra validation for step
        if step is None:
            step = 1
        else:
            if step < 1:
                emsg = "ERROR!! Step value must be a positive number: '{}'\n"
                sys.stderr.write(emsg.format(step))
                sys.exit(1)

        # validate proper order in range
        if start > end:
            emsg = 'ERROR!! Start ({}) cannot be larger than end ({})\n'
            sys.stderr.write(emsg.format(start, end))
            sys.exit(1)

        # Build range
        bounded_resid = [r for r in resid_list if start <= r <= end]
        return bounded_resid[::step]

    # Defaults
    option = '::'
    fh = sys.stdin  # file handle

    if not len(args):
        # Reading from pipe with default option
        if sys.stdin.isatty():
            sys.stderr.write(__doc__)
            sys.exit(1)

    elif len(args) == 1:
        # One of two options: option & Pipe OR file & default option
        if args[0].startswith('-'):
            option = args[0][1:]
            if sys.stdin.isatty():  # ensure the PDB data is streamed in
                emsg = 'ERROR!! No data to process!\n'
                sys.stderr.write(emsg)
                sys.stderr.write(__doc__)
                sys.exit(1)

        else:
            if not os.path.isfile(args[0]):
                emsg = 'ERROR!! File not found or not readable: \'{}\'\n'
                sys.stderr.write(emsg.format(args[0]))
                sys.stderr.write(__doc__)
                sys.exit(1)

            fh = open(args[0], 'rb')

    elif len(args) == 2:
        # Two options: option & File
        if not args[0].startswith('-'):
            emsg = 'ERROR! First argument is not an option: \'{}\'\n'
            sys.stderr.write(emsg.format(args[0]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        if not os.path.isfile(args[1]):
            emsg = 'ERROR!! File not found or not readable: \'{}\'\n'
            sys.stderr.write(emsg.format(args[1]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        option = args[0][1:]
        fh = open(args[1], 'rb')

    else:  # Whatever ...
        sys.stderr.write(__doc__)
        sys.exit(1)

    # Read file handle to extract residue numbers
    # Because sys.stdin is not seekable we store the
    # lines again in an iterator.
    buffer = iter([])
    resid_list = []

    records = ('ATOM', 'HETATM', 'TER', 'ANISOU')
    prev_res = None
    for line in fh:
        line = line
        if line.startswith(records):
            res_id = line[21:26]  # include chain ID
            if res_id != prev_res:
                prev_res = res_id
                resid_list.append(int(line[22:26]))
        buffer = iter_chain(buffer, [line])

    try:
        fh.close()  # in case we opened a file. Just to be clean.
    except AttributeError:
        pass

    fh = buffer

    residue_range = set()  # stores all the residues to write.
    for entry in option.split(','):
        if ':' in entry:
            resrange = _validate_opt_range(entry, resid_list)
            residue_range.update(resrange)
        else:
            singleres = _validate_opt_numeric(entry)
            residue_range.add(singleres)

    return (residue_range, fh)


def select_residues(fhandle, residue_range):
    """Outputs residues within a certain numbering range.
    """

    prev_res = None
    records = ('ATOM', 'HETATM', 'TER', 'ANISOU')
    for line in fhandle:
        if line.startswith(records):

            res_id = line[21:26]  # include chain ID
            if res_id != prev_res:
                prev_res = res_id

            if int(line[22:26]) not in residue_range:
                continue

        yield line


def main():
    # Check Input
    resrange, pdbfh = check_input(sys.argv[1:])

    # Do the job
    new_pdb = select_residues(pdbfh, resrange)

    try:
        _buffer = []
        _buffer_size = 5000  # write N lines at a time
        for lineno, line in enumerate(new_pdb):
            if not (lineno % _buffer_size):
                sys.stdout.write(''.join(_buffer))
                _buffer = []
            _buffer.append(line)

        sys.stdout.write(''.join(_buffer))
        sys.stdout.flush()
    except IOError:
        # This is here to catch Broken Pipes
        # for example to use 'head' or 'tail' without
        # the error message showing up
        pass

    # last line of the script
    # No need to close the file handle since we
    # build an iterator in the check_input functions
    sys.exit(0)


if __name__ == '__main__':
    main()
