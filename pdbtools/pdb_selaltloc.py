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

Despite not an official format, many times alternative locations are identified
by a blank character ' ' (space), and a character, for example ('A'). In these
cases, to select the alternative location identified by a blank character,
define blank in the command line, see below.

Usage:
    python pdb_selaltloc.py [-<option>] <pdb file>

Example:
    python pdb_selaltloc.py 1CTF.pdb  # picks locations with highest occupancy
    python pdb_selaltloc.py -A 1CTF.pdb  # picks alternate locations labelled 'A'
    python pdb_selaltloc.py -' ' 1CTF.pdb  # picks alternate locations labelled blank ' '

This program is part of the `pdb-tools` suite of utilities and should not be
distributed isolatedly. The `pdb-tools` were created to quickly manipulate PDB
files using the terminal, and can be used sequentially, with one tool streaming
data to another. They are based on old FORTRAN77 code that was taking too much
effort to maintain and compile. RIP.
"""
import os
import sys
from pprint import pprint

if sys.version[0] == '2':
    from collections import OrderedDict as dict


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


def run(fhandle, option=None):
    """
    Selects altloc labels for the entire PDB file.

    Parameters
    ----------
    fhandle : an iterable giving the PDB file line-by-line.

    option : str or `None`.
        The alternative location identifier to select. By default
        (`None`) selects the alternative location with highest
        occupancy. In this case, if the different alternative locations
        have the same occupancy, selects the one that comes first.
        Selecting by highest occupancy removes all altloc labels for all
        atoms. Provide an option (e.g. 'A') to select only atoms with
        altloc label `A`. If you select `A` and an atom has conformers
        with altlocs `B` and `C`, both B and C will be kept in the
        output. Despite not an official format, many times alternative
        locations are identified by a blank character ' ' (space), and a
        [A-Z] character.  In these cases, to select the alternative
        location identified by a blank character give `option=' '`.

    Returns
    -------
    generator
        A generator object. To exhaust the generator, that is, to
        process the PDB file (or PDB lines), convert it to a list.

        >>> from pdbtools.pdb_selaltloc import run
        >>> with('input.pdb', 'r') as fin:
        >>>     processed_lines = list(run(fin))

        For more example see:

        >>> import pdbtools
        >>> help(pdbtools)
    """
    records = ('ATOM', 'HETATM', 'ANISOU')
    terminators = ('TER', 'END', 'CONECT', 'END', 'ENDMDL', 'MODEL')

    # register atom information
    register = dict()

    # register comment lines
    others = []

    # register current chain
    chain = None
    prev_chain = None

    # keep record of the line number. This will be used to sort lines
    # after selecting the desired alternative location
    nline = 0

    # the loop will collect information on the different atoms
    # throughout the PDB file until a new chain or any terminal line is
    # found. At that point, the collected information is flushed because
    # all altlocs for that block have been defined.
    for line in fhandle:
        nline += 1

        if line.startswith(records):

            # here resnum + insertion code are taken to identify
            # different residues
            resnum = line[22:27].strip()
            atomname = line[12:16]
            altloc = line[16]
            chain = line[21:22]

            # flush lines because we enter a new chain
            if chain != prev_chain:
                # the "yield from" statement is avoided to keep
                # compatibility with Python 2.7
                for _line in _flush(register, option, others):
                    yield _line
                # Python 2.7 compatibility. Do not use .clear() method

                # restart help variables
                del register, others
                register, others = dict(), []

            # organizes information hierarchically
            resnum_d = register.setdefault(resnum, {})
            atomname_d = resnum_d.setdefault(atomname, {})
            altloc_d = atomname_d.setdefault(altloc, [])

            # adds info to dictionary
            altloc_d.append((nline, line))

        # flush information because we reached the end of a block
        elif line.startswith(terminators):
            for _line in _flush(register, option, others):
                yield _line

            del register, others
            register, others = dict(), []

            yield line  # yield the current line after flush

        else:
            # append comments to flush list
            # The reason to add comments to a list instead of yielding
            # them directly is to cover the possibility of having
            # comments in the middle of the PDB file. Obviously is this
            # extremely unlikely. But just in case...
            others.append((nline, line))

        prev_chain = chain

    # at the end of the PDB, flush the remaining lines
    for _line in _flush(register, option, others):
        yield _line


def _flush(register, option, others):
    """
    Processes the collected atoms according to the selaltloc option.
    """
    lines_to_yield = []
    select_by_occupancy = option is None

    atom_lines = ('ATOM', 'HETATM')

    # anisou lines are treated specially
    anisou_lines = ('ANISOU',)

    for resnum, atomnames in register.items():

        for atomname, altlocs in atomnames.items():

            if select_by_occupancy:

                # gathers all alternative locations for the atom
                all_lines = []
                for altloc, lines in altlocs.items():
                    all_lines.extend(lines)

                # identifies the highest occupancy combining dictionary
                # and sorting
                new = {}
                for line_number, line in all_lines:
                    if line.startswith(atom_lines):
                        occupancy_number = line[54:60]
                        list_ = new.setdefault(occupancy_number, [])
                        list_.append((line_number, line))

                    # assumes ANISOU succeed the respective ATOM line
                    elif line.startswith(anisou_lines):
                        list_.append((line_number, line))

                # sort keys by occupancy
                keys_ = sorted(new.keys(), key=lambda x: float(x.strip()), reverse=True)

                these_atom_lines = new[keys_[0]]
                if len(keys_) == 1 and len(these_atom_lines) > 1:
                    # address "take first if occ is the same"
                    # see: https://github.com/haddocking/pdb-tools/issues/153#issuecomment-1488627668
                    lines_to_yield.extend(_remove_altloc(these_atom_lines[0:1]))

                    # if there's ANISOU, add it
                    if these_atom_lines[1][1].startswith(anisou_lines):
                        lines_to_yield.extend(_remove_altloc(these_atom_lines[1:2]))

                # this should run when there are more than one key or
                # the key has only one atom line. Keys are the occ
                # value.
                else:
                    # when occs are different, select the highest one
                    lines_to_yield.extend(_remove_altloc(these_atom_lines))

                del all_lines, new

            # selected by option:
            else:
                if option in altlocs:
                    # selects the option, that's it
                    lines_to_yield.extend(_remove_altloc(altlocs[option]))

                else:
                    # if the option does not exist, add all altlocs
                    for altloc, lines in altlocs.items():
                        lines_to_yield.extend(lines)

    # add comments
    lines_to_yield.extend(others)

    # lines are sorted to the line number so that the output is sorted
    # the same way as in the input PDB
    lines_to_yield.sort(key=lambda x: x[0])

    # the line number is ignored, only the line is yield
    for line_number, line in lines_to_yield:
        yield line


def _remove_altloc(lines):
    # the altloc ID is removed in processed altloc lines
    for line_num, line in lines:
        yield (line_num, line[:16] + ' ' + line[17:])


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
