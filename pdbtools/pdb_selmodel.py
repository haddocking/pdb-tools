#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 João Pedro Rodrigues
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
Extracts one or more models from a PDB file.

If the PDB file has no MODEL records, returns the entire file.

Usage:
    python pdb_selmodel.py -<model id> <pdb file>

Example:
    python pdb_selmodel.py -1 1GGR.pdb  # selects model 1
    python pdb_selmodel.py -1,3 1GGR.pdb  # selects models 1 and 3

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


def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options.
    """

    # Defaults
    option = ''
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
    option_set = set()
    for opt in option.split(','):
        opt = opt.strip()
        if not opt:
            continue
        try:
            opt = int(opt)
        except ValueError:
            emsg = 'ERROR!! Model identifier is invalid: \'{}\'\n'
            sys.stderr.write(emsg.format(opt))
            sys.stderr.write(__doc__)
            sys.exit(1)
        option_set.add(opt)

    if not option_set:
        emsg = 'ERROR!! You must provide at least one model identifier\n'
        sys.stderr.write(emsg)
        sys.stderr.write(__doc__)
        sys.exit(1)

    return (fh, option_set)


def run(fhandle, model_set):
    """
    Filter the PDB file for specific model identifiers.

    This function is a generator.

    Parameters
    ----------
    fhandle : a line-by-line iterator of the original PDB file.

    model_set : set, or list, or tuple
        The group of models to kepp.
        Example: (1, 3), keeps only atoms from models 1 and 3

    Yields
    ------
    str (line-by-line)
        The PDB lines for those matching the selected chains.
    """
    records = ('ATOM', 'HETATM', 'TER', 'ANISOU')
    ignore_model = False
    for line in fhandle:
        if line.startswith('MODEL'):
            model_id = int(line[10:14])
            if model_id not in model_set:
                ignore_model = True
                continue

        elif line.startswith('ENDMDL'):
            if ignore_model:
                ignore_model = False
                continue

        elif ignore_model and line.startswith(records):
            continue
        yield line


select_model = run


def main():
    # Check Input
    pdbfh, models = check_input(sys.argv[1:])

    # Do the job
    new_pdb = run(pdbfh, models)

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
