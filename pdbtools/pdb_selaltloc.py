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
Selects altloc labels for the entire PDB file.

By default, selects the label with the highest occupancy value for each atom,
but the user can define a specific altloc label to select.

Selecting by highest occupancy removes all altloc labels for all atoms. If the
user provides an option (e.g. -A), only atoms with conformers with an altloc A
are processed by the script. If you select -A and an atom has conformers with
altlocs B and C, both B and C will be kept in the output.

Usage:
    python pdb_selaltloc.py [-<option>] <pdb file>

Example:
    python pdb_selaltloc.py 1CTF.pdb  # picks locations with highest occupancy
    python pdb_selaltloc.py -A 1CTF.pdb  # picks alternate locations labelled 'A'

This program is part of the `pdb-tools` suite of utilities and should not be
distributed isolatedly. The `pdb-tools` were created to quickly manipulate PDB
files using the terminal, and can be used sequentially, with one tool streaming
data to another. They are based on old FORTRAN77 code that was taking too much
effort to maintain and compile. RIP.
"""
from pprint import pprint
import operator
import os
import sys

__author__ = "Joao Rodrigues"
__email__ = "j.p.g.l.m.rodrigues@gmail.com"


def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options.
    """

    # Defaults
    option = None
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
    if option and len(option) > 1:
        emsg = 'ERROR!! Alternate location identifiers must be single '
        emsg += 'characters: \'{}\''
        sys.stderr.write(emsg.format(option))
        sys.exit(1)

    return (fh, option)


def select_by_occupancy(fhandle):
    return select_by_altloc(fhandle, selloc=None, byocc=True)


def select_by_altloc(fhandle, selloc):
    return select_altloc(fhandle, selloc, byocc=False)


def select_altloc(fhandle, selloc=None, byocc=False):
    """
    Pick one altloc when atoms have more than one.

    If the specified altloc (selloc) is not present for this particular
    atom, outputs all altlocs. For instance, if atom X has altlocs A and
    B but the user picked C, we return A and B anyway. If atom Y has
    altlocs A, B, and C, then we only return C.

    This function is a generator.

    Parameters
    ----------
    fhandle : an iterable giving the PDB file line-by-line.

    Yields
    ------
    str (line-by-line)
        The PDB file with altlocs according to selection.
    """
    if selloc is None and not byocc:
        raise ValueError('Provide either `selloc` or `byocc`.')

    residue_loc = {}  # dict to capture the lines from a altloc group
    prev_altloc = ''
    prev_resname = ''
    prev_resnum = ''

    flush_func = flush_resloc_occ if byocc else flush_resloc

    records = ('ATOM', 'HETATM', 'ANISOU')
    terminators = ('TER', 'END')

    for line in fhandle:

        if line.startswith(records):
            # captures the relevant parameters
            altloc = line[16]
            resname = line[17:20]
            resnum = line[22:26].strip()

            if is_another_altloc_group(
                    altloc, prev_altloc, resnum, prev_resnum,
                    resname, prev_resname, residue_loc):

                if residue_loc: # flushes only of there is something in the dict
                    # flush altloc dictionary from previous lines.
                    # avoiding using "yield from" for backwards compatibility
                    # hence we need this for-loop
                    for __line in flush_func(selloc, residue_loc):
                        yield __line

                if altloc != ' ':
                    # this case correct for two consecutive altloc groups
                    current_loc = residue_loc.setdefault(altloc, [])
                    current_loc.append(line)
                else:
                    yield line

            else:
                # this line belongs to the same altloc group as the previous line
                current_loc = residue_loc.setdefault(altloc, [])
                current_loc.append(line)

            # registers the parameters for the next line
            prev_altloc = altloc
            prev_resnum = resnum
            prev_resname = resname

        elif line.startswith(terminators):
            for __line in flush_func(selloc, residue_loc):
                yield __line

            yield line  # the terminator line

        else:
            yield line

    # end of for loop
    # flush altloc residues in case the last residue was an altloc
    for __line in flush_func(selloc, residue_loc):
        yield __line


def is_another_altloc_group(
        altloc,
        prev_altloc,
        resnum,
        prev_resnum,
        resname,
        prev_resname,
        residue_loc):
    """
    Detect if current line because to another altloc group.

    True if:
        * altloc is a blank-char it is always a new group
          a.k.a. ignore
        * altloc equals and either the resnum or resname changes
        * altloc differs and altloc already in altloc group dict
        * altloc equals and renum and resname differs and altloc in
          altloc group dict

    False otherwise.
    """
    is_another = \
        altloc == ' ' \
        or altloc == prev_altloc and (resnum != prev_resnum or resname != prev_resname) \
        or altloc != prev_altloc and altloc in residue_loc \
        or altloc == prev_altloc and resnum != prev_resnum and resname != prev_resname and altloc in residue_loc

    return is_another


def flush_resloc(selloc, residue_loc):
    """Flush the captured altloc lines."""
    # only the selected altloc is yieled
    if selloc in residue_loc:
        for line2flush in residue_loc[selloc]:
            yield line2flush[:16] + ' ' + line2flush[17:]
    # the altloc group does not contain the selected altloc
    # therefore, all members should be yielded
    else:
        for key, lines2flush in residue_loc.items():
            for line2flush in lines2flush:
                yield line2flush

    # clears the altloc group dictionary. Ready for the next one!
    residue_loc.clear()


def flush_resloc_occ(selloc, residue_loc):
    """Flush the captured altloc lines."""
    # only the selected altloc is yieled
    highest = 0.00
    altloc = None
    for key, lines2flush in residue_loc.items():
        # all atoms in a altloc location (should) have the same occupancy
        if float(lines2flush[0][54:60]) > highest:
            altloc = key

    for line2flush in residue_loc[altloc]:
        yield line2flush[:16] + ' ' + line2flush[17:]

    # clears the altloc group dictionary. Ready for the next one!
    residue_loc.clear()


def run(fhandle, option=None):
    """
    Selects altloc labels for the entire PDB file.

    Parameters
    ----------
    fhandle : an iterable giving PDB file line-by-line.

    Returns
    -------
    generator
        If option is None, return `select_by_occupancy` generator.
        If option is given, return `select_by_altloc` generator.
        See `pdb_selaltloc.select_by_occupancy` and
        `pdb_selaltloc.select_by_altloc` for more details.
    """
    if option is None:
        return select_by_occupancy(fhandle)

    else:
        return select_by_altloc(fhandle, option)


def main():
    # Check Input
    pdbfh, option = check_input(sys.argv[1:])

    # Do the job
    new_pdb = run(pdbfh, option)

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
