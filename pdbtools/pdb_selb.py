#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2024 João Pedro Rodrigues
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
Selects residues according to the B-factor values.

Valid Operations:
    [g] - greater than
    [l] - less than
    [e] - equal to
    [n] - not equal to

Valid B-Factor Filtering Modes:
    [mean] - Filter by the mean of the B-factors of all atoms in a residue
    [min] - Filter by the atom with the minimum B-factor in a residue
    [max] - Filter by the atom with the maximum B-factor in a residue

Usage:
    python pdb_selb.py -<filtering_mode>:<operators> -treshold  <pdb file>

Example:
    python pdb_selb.py -mean:g -10  1CTF.pdb  # selects residues with a mean B-factor greater than 10
    python pdb_selb.py -min:g -10  1CTF.pdb  # selects residues where the atom with the minimum B-factor has a B-factor greater than 10
    python pdb_selb.py -max:g -10  1CTF.pdb  # selects residues where the atom with the maximum B-factor has a B-factor greater than 10

    python pdb_selb.py -mean:l -10 1CTF.pdb # selects residues with a mean B-factor less than 10
    python pdb_selb.py -min:ge -10 1CTF.pdb # selects residues where the atom with the minimum B-factor has a B-factor greater than or equal to 10
    python pdb_selb.py -max:le -10 1CTF.pdb # selects residues where the atom with the maximum B-factor has a B-factor less than or equal to 10
    python pdb_selb.py -mean:e -10 1CTF.pdb # selects residues with a mean B-factor equal to 10
    python pdb_selb.py -mean:n -10 1CTF.pdb # selects residues with a mean B-factor not equal to 10

This program is part of the `pdb-tools` suite of utilities and should not be
distributed isolatedly. The `pdb-tools` were created to quickly manipulate PDB
files using the terminal, and can be used sequentially, with one tool streaming
data to another. They are based on old FORTRAN77 code that was taking too much
effort to maintain and compile. RIP.
"""
import os
import sys
import statistics

__author__ = "Ahmed Selim Üzüm"
__email__ = "ahmedselimuzum@gmail.com"


def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options."""

    # Defaults
    filtering_modes = {"min", "max", "mean"}
    operators = {"g", "l", "e", "n"}
    option = ""
    operator_treshold = None
    fh = sys.stdin  # file handle

    if len(args) <= 1:
        # Reading from pipe with default option
        if sys.stdin.isatty():
            sys.stderr.write(__doc__)
            sys.exit(1)

    elif len(args) == 2:
        # Two options: Options & Pipe
        if args[0].startswith("-"):
            option = args[0][1:]
            if args[1].startswith("-"):
                operator_treshold = args[1][1:]
                if sys.stdin.isatty():  # ensure the PDB data is streamed in
                    emsg = "ERROR!! No data to process!\n"
                    sys.stderr.write(emsg)
                    sys.stderr.write(__doc__)
                    sys.exit(1)

    elif len(args) == 3:
        # Three options: options & File
        if not args[0].startswith("-"):
            emsg = "ERROR! First argument is not an option: '{}'\n"
            sys.stderr.write(emsg.format(args[0]))
            sys.stderr.write(__doc__)
            sys.exit(1)
        elif not args[1].startswith("-"):
            emsg = "ERROR! Second argument is not an option: '{}'\n"
            sys.stderr.write(emsg.format(args[0]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        if not os.path.isfile(args[2]):
            emsg = "ERROR!! File not found or not readable: '{}'\n"
            sys.stderr.write(emsg.format(args[1]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        option = args[0][1:]
        operator_treshold = args[1][1:]
        fh = open(args[2], "r")

    else:  # Whatever ...
        sys.stderr.write(__doc__)
        sys.exit(1)

    # Validate options
    try:
        filtering_mode, operator = option.split(":")
    except ValueError:
        emsg = "ERROR!! You have provided filtering mode and operator in an invalid format: '{}'"
        sys.stderr.write(emsg.format(option))
        sys.exit(1)

    if filtering_mode == '':
        emsg = "ERROR!! You did not provided a filtering_mode."
        sys.stderr.write(emsg.format())
        sys.exit(1)
    elif filtering_mode not in filtering_modes:
        emsg = "ERROR!! You provided an invalid filtering_mode: '{}'"
        sys.stderr.write(emsg.format(filtering_mode))
        sys.exit(1)

    if operator == '':
        emsg = "ERROR!! You did not provided an operator."
        sys.stderr.write(emsg.format())
        sys.exit(1)
    elif not set(operator).issubset(operators):
        emsg = "ERROR!! You provided an invalid operator: '{}'"
        sys.stderr.write(emsg.format(operator))
        sys.exit(1)

    try:
        if operator_treshold is None:
            emsg = "ERROR!! You did not provided an operator treshold."
            sys.stderr.write(emsg.format())
            sys.exit(1)
        operator_treshold = float(operator_treshold)
    except ValueError:
        emsg = "ERROR!! You provided an invalid b-factor treshold value: '{}'"
        sys.stderr.write(emsg.format(operator_treshold))
        sys.exit(1)

    return (fh, filtering_mode, operator, operator_treshold)


def pad_line(line):
    """Pad line to 80 characters in case it is shorter."""
    size_of_line = len(line)
    if size_of_line < 80:
        padding = 80 - size_of_line + 1
        line = line.strip("\n") + " " * padding + "\n"
    return line[:81]  # 80 + newline character


def run(fhandle, filtering_mode, operator, operator_treshold):
    """
    Filter according to the bfactor value using the given operator and operator
    treshold.

    This function is a generator.

    Parameters
    ----------
    fhandle : a line-by-line iterator of the original PDB file.

    filtering_mode: string
        The desired filtering mode that should be used to select in which
        conditions a residue should be filtered.
        Filtering mode values:
            "mean": Filter by the mean of the B-factors of all atoms in a residue
            "min": Filter by the atom with the minimum B-factor in a residue
            "max": Filter by the atom with the maximum B-factor in a residue


    operator : string
        The desired operator that should be used to filter by bafctor. The
        combination of multiple operator values such as "ge" can also be used.
        Operator values:
            "g": greater than operator
            "l": less than operator
            "e": equal to operator
            "n": not equal to operator

    operator_treshold : float
        The treshold bfactor value that should be used to filter by bfactor.

    Yields
    ------
    str (line-by-line)
        The modified (or not) PDB line.
    """
    _pad_line = pad_line
    records = ("ATOM", "HETATM")
    res_lines = []
    prev_res_id = None
    for line in fhandle:
        if line.startswith(records):
            line = _pad_line(line)

            res_id = int(line[23:26])

            if prev_res_id == res_id or prev_res_id is None:
                res_lines.append(line)
            else:
                bfactors = [float(rl[60:66]) for rl in res_lines]

                selected_bfactor = None
                if filtering_mode == "mean":
                    selected_bfactor = statistics.fmean(bfactors)
                elif filtering_mode == "min":
                    selected_bfactor = min(bfactors)
                elif filtering_mode == "max":
                    selected_bfactor = max(bfactors)

                for o in operator:
                    if o == "g":
                        if selected_bfactor > operator_treshold:
                            yield from res_lines
                            continue
                    elif o == "l":
                        if selected_bfactor < operator_treshold:
                            yield from res_lines
                            continue
                    elif o == "e":
                        if selected_bfactor == operator_treshold:
                            yield from res_lines
                            continue
                    elif o == "n":
                        if selected_bfactor != operator_treshold:
                            yield from res_lines
                            continue
                res_lines = []

            prev_res_id = res_id

        else:
            yield line


alter_bfactor = run


def main():

    # Check Input
    pdbfh, filtering_mode, operator, operator_treshold = check_input(
        sys.argv[1:])

    # Do the job
    new_pdb = run(pdbfh, filtering_mode, operator, operator_treshold)

    # Output results
    try:
        _buffer = []
        _buffer_size = 5000  # write N lines at a time
        for lineno, line in enumerate(new_pdb):
            if not (lineno % _buffer_size):
                sys.stdout.write("".join(_buffer))
                _buffer = []
            _buffer.append(line)

        sys.stdout.write("".join(_buffer))
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


if __name__ == "__main__":
    main()
