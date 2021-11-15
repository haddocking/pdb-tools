#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2021 Brian Andrews
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
Adds TER entries at locations in pdb designated by the user. Starting residue
must be specified to avoid inconsistent behavior. This program is agnostic to
residue numbers in the pdb file. The first residue of the pdb file will be
considered residue one (1) and TER entries will be entered at specified intervals
using that convention. Existing TER entries will not be affected.

Usage:
    python pdb_addter.py -[first residue]:[last residue]:[frequency] <pdb file>

Example:
    python pdb_addter.py -1:10 1CTF.pdb # Adds TER after every residue starting with the end of residue 1 to before residue 10
    python pdb_addter.py -1::3 1CTF.pdb # Adds TER after every 3th residue starting from residue 1
    python pdb_addter.py -1:10:5 1CTF.pdb # Adds TER after every 5th residue from residues 1 to 10
    python pdb_addter.py -4: 1CTF.pdb # Adds TER after every residue starting at the end of residue 4

This program is part of the `pdb-tools` suite of utilities and should not be
distributed isolatedly. The `pdb-tools` were created to quickly manipulate PDB
files using the terminal, and can be used sequentially, with one tool streaming
data to another. They are based on old FORTRAN77 code that was taking too much
effort to maintain and compile. RIP.
"""

import os
import sys

__author__ = ["Joao Rodrigues", "Brian Andrews"]
__email__ = ["j.p.g.l.m.rodrigues@gmail.com", "b9andrews@gmail.com"]


def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options.
    """

    def return_integer(string):
        try:
            return int(string)
        except:
            emsg = 'ERROR!! Range values must be integers!\n'
            sys.stderr.write(emsg.format(string))
            sys.exit(1)

    # Defaults
    option = ':::'
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

            fh = open(args[0], 'r')

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
        fh = open(args[1], 'r')

    else:  # Whatever ...
        sys.stderr.write(__doc__)
        sys.exit(1)

    # Validate option
    if not (1 <= option.count(':') <= 2):
        emsg = 'ERROR!! Residue range must be in \'a:z:s\' where a and z are '
        emsg += 'optional (default to first residue and last respectively), and '
        emsg += 's is an optional step value (to return every s-th residue).\n'
        sys.stderr.write(emsg)
        sys.exit(1)

    start, end, step = None, None, 1
    slices = [num if num.strip() else None for num in option.split(':')]
    if len(slices) == 3:
        start, end, step = slices
    elif len(slices) == 2:
        start, end = slices
    elif len(slices) == 1:
        if option.startswith(':'):
            end = slices[0]
        elif option.endswith(':'):
            start = slices[0]

    #residue range start
    if start is None:
        emsg = 'ERROR!! Please specify starting value: \'{}\'\n'
        sys.stderr.write(emsg.format(start))
        sys.exit(1)
    else:
        start = return_integer(start)

    if  start < 1:
        emsg = 'ERROR!! Starting value must be 1 or greater: \'{}\'\n'
        sys.stderr.write(emsg.format(start))
        sys.exit(1)

    #residue range end
    if end is None:
        end = 1000000  # a value that presumably will not be reached
    else:
        end = return_integer(end)

    if start >= end:
        emsg = 'ERROR!! Start ({}) cannot be larger than end ({})\n'
        sys.stderr.write(emsg.format(start, end))
        sys.exit(1)

    #residue range step
    if step is None:
        step = 1
    else:
        step = return_integer(step)

    if step <= 0:
        emsg = 'ERROR!! Step value must be a positive number: \'{}\'\n'
        sys.stderr.write(emsg.format(step))
        sys.exit(1)

    resrange = set(range(start, end + 2)) #plus 2 here is necessary
    return (fh, resrange, step)


def run(fhandle, residue_range, step):
    """
    Add TER records within the residue range at frequency identified by step.

    This function is a generator.

    Parameters
    ----------
    fhandle : a line-by-line iterator of the original PDB file.

    residue_range : set, list, or tuple
        The residues describing the range to consider.

    step : int
        The step at which to insert a TER record.

    Yields
    ------
    str (line-by-line)
        All lines with added TER lines designated by inputs.
    """

    def make_TER(prev_line):
        """Creates a TER statement based on the last ATOM/HETATM line.
        """

        # Add last TER statement
        serial = int(prev_line[6:11]) + 1
        rname = prev_line[17:20]
        chain = prev_line[21]
        resid = prev_line[22:26]
        icode = prev_line[26]

        return fmt_TER.format(serial, rname, chain, resid, icode)

    # TER     606      LEU A  75
    fmt_TER = "TER   {:>5d}      {:3s} {:1s}{:>4s}{:1s}" + " " * 53 + "\n"

    prev_line = None
    prev_res = None
    res_counter = 0
    no_more_atoms = False
    min_residue = min(residue_range)
    records = ('ATOM', 'HETATM', 'ANISOU') #added END* for cases where TER added after last residue
    ignored = ('TER')
    end = ('END', 'ENDMDL', 'CONECT')
    for line in fhandle:
        if line.startswith(records):

            res_id = line[21:26]  # include chain ID
            if res_id != prev_res:

                prev_res = res_id
                res_counter += 1
                if res_counter - min_residue != 0 \
                  and (res_counter - min_residue) % step == 0 \
                  and res_counter in residue_range \
                  and not prev_line.startswith(ignored): #does not add TER record if one exists
                    yield make_TER(prev_line)

        # sees record that indicates end of ATOMS records, checks if TER record should be
        # added based on user input only once.
        if line.startswith(end) \
          and res_counter in residue_range \
          and res_counter % step == 0 \
          and not prev_line.startswith(ignored) \
          and not no_more_atoms:
            no_more_atoms = True
            yield make_TER(prev_line)

        prev_line = line
        yield line

add_manual_ter = run

def main():
    # Check Input
    pdbfh, resrange, step = check_input(sys.argv[1:])

    # Do the job
    new_pdb = run(pdbfh, resrange, step)

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
    # We can close it even if it is sys.stdin
    pdbfh.close()
    sys.exit(0)


if __name__ == '__main__':
    main()
