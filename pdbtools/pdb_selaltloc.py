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
import os
import sys

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


def select_by_occupancy(fhandle):
    return select_altloc(fhandle, selloc=None, byocc=True)


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

    altloc_lines = dict()  # dict to capture the lines from a altloc group
    res_per_loc = dict()  # dict to capture the residues per altloc group

    prev_altloc = ''
    prev_resname = ''
    prev_resnum = ''

    # uses the same function names in the loop below. However, depending
    # on the input options, the functions used are different. One is
    # specific for byocc=True, and other specific for occ char selection
    flush_func_multi_residues = flush_resloc_occ if byocc else flush_resloc

    flush_func_single_residues = \
        flush_resloc_occ_same_residue if byocc else flush_resloc_id_same_residue

    # defines records and terminators
    records = ('ATOM', 'HETATM', 'ANISOU')
    terminators = ('TER', 'END', 'CONECT', 'END', 'ENDMDL')

    for line in fhandle:

        if line.startswith(records):
            # captures the relevant parameters
            altloc = line[16]
            resname = line[17:20]
            resnum = line[22:26].strip()

            if is_another_altloc_group(
                    altloc, prev_altloc, resnum, prev_resnum,
                    resname, prev_resname, altloc_lines, res_per_loc):
                # if we see the altloc group has changed, we should flush
                # the lines observed for the previous altloc group

                # uses "for loop" instead of "yield from" to maintain
                # compatibility with older python version
                if partial_altloc(altloc_lines):
                    flush_func = flush_func_single_residues
                else:
                    flush_func = flush_func_multi_residues

                for __line in flush_func(selloc=selloc, altloc_lines=altloc_lines):
                    yield __line

                altloc_lines = dict()
                res_per_loc = dict()

            # saves the line per altloc identifier
            current_loc = altloc_lines.setdefault(altloc, [])
            current_loc.append(line)

            # registers which residues are seen for each identifier
            rploc = res_per_loc.setdefault(altloc, set())
            rploc.add((resname, resnum))

            prev_altloc = altloc
            prev_resnum = resnum
            prev_resname = resname

        elif line.startswith(terminators):
            # before flushing the terminator line
            # we should flush the previous altloc group
            if altloc_lines:
                if partial_altloc(altloc_lines):
                    flush_func = flush_func_single_residues
                else:
                    flush_func = flush_func_multi_residues
                for __line in flush_func(selloc=selloc, altloc_lines=altloc_lines):
                    yield __line

                altloc_lines = dict()
                res_per_loc = dict()

            prev_altloc = ''
            prev_resname = ''
            prev_resnum = ''

            yield line  # the terminator line

        else:
            prev_altloc = ''
            prev_resname = ''
            prev_resnum = ''
            yield line

    # end of for loop
    # flush altloc residues in case the last residue was an altloc
    if altloc_lines:

        if partial_altloc(altloc_lines):
            flush_func = flush_func_single_residues
        else:
            flush_func = flush_func_multi_residues

        for __line in flush_func(selloc=selloc, altloc_lines=altloc_lines):
            yield __line

        altloc_lines = []
        res_per_loc = dict()


def is_another_altloc_group(
        altloc,
        prev_altloc,
        resnum,
        prev_resnum,
        resname,
        prev_resname,
        altloc_lines,
        rploc
):
    """Detect if current line belongs to a new altloc group."""
    a0 = prev_altloc
    a1 = altloc
    ra0 = prev_resname
    ra1 = resname
    ru0 = prev_resnum
    ru1 = resnum
    rl = altloc_lines
    rv = list(rploc.values())

    is_another = (
        all((a0, ra0, ru0)) and (
            (a0 != a1 and a1 == ' ' and ru1 > ru0)
            or (a0 == ' ' and a1 != ' ' and ru1 > ru0)
            or (a0 == ' ' and a1 == ' ' and (ru1 != ru0 or ra1 != ra0))
            or (
                a0 == a1
                and a0 != ' '
                and a1 in rl
                and ru1 > ru0
                and len(rl) > 1
                and all(len(v) == len(rv[0]) for v in rv[1:])
            )
        )
    )

    return is_another


def flush_resloc(selloc, altloc_lines):
    """Flush the captured altloc lines."""
    # only the selected altloc is yieled
    if selloc in altloc_lines:
        for line2flush in altloc_lines[selloc]:
            yield line2flush[:16] + ' ' + line2flush[17:]

    # the altloc group does not contain the selected altloc
    # therefore, all members should be yielded
    else:
        for key, lines2flush in altloc_lines.items():
            for line2flush in lines2flush:
                yield line2flush


def flush_resloc_occ(altloc_lines, **kw):
    """Flush the captured altloc lines by highest occupancy."""
    # only the selected altloc is yieled
    highest = 0.00
    altloc = ' '

    # detects which altloc identifier has the highest occupancy
    for key, lines2flush in altloc_lines.items():
        # we check only the first line because all atoms in one identifier
        # should have the same occupancy value
        occ = float(lines2flush[0][54:60])
        if occ > highest:
            altloc = key
            highest = occ

    for line2flush in altloc_lines[altloc]:
        yield line2flush[:16] + ' ' + line2flush[17:]


def flush_resloc_id_same_residue(selloc, altloc_lines):
    """Flush altloc if altloc are atoms in the same residue - by ID."""
    # places all lines in a single list
    sorted_atoms = _get_sort_atoms(altloc_lines)

    for atom, linet in sorted_atoms:
        to_yield = []
        # remember linet is a tuple, where the first item is the atom number
        lines = linet[1]

        # here we don't need to care about anisou lines as in
        # `flush_resloc_occ_same_residue` because ATOM/HETATM and ANISOU
        # are already sorted by definition and lines are yieled from the
        # altloc record
        for line in lines:
            if line[16] == selloc:
                to_yield.append(line)

        if to_yield:
            for line in to_yield:
                yield line[:16] + ' ' + line[17:]
        else:
            for line in lines:
                yield line


def flush_resloc_occ_same_residue(altloc_lines, **kw):
    """Flush altloc if altloc are atoms in the same residue - by occ."""
    sorted_atoms = _get_sort_atoms(altloc_lines)

    for atom, linest in sorted_atoms:
        lines = linest[1]

        atom_lines = [ln for ln in lines if ln.startswith(("ATOM", "HETATM"))]
        anisou_lines = [ln for ln in lines if ln.startswith(("ANISOU"))]

        if anisou_lines:
            new = []

            if len(atom_lines) != len(anisou_lines):
                emsg = (
                    "There is an error with this PDB. "
                    "We expect one ANISOU line per ATOM/HETATM lines. "
                    "But the number of ATOM/HETATM and ANISOU lines differ."
                )
                raise ValueError(emsg)

            for _a, _b in zip(atom_lines, anisou_lines):
                new.append((_a, _b))

            new.sort(key=lambda x: float(x[0][54:60]), reverse=True)

            # ATOM/HETATM
            yield new[0][0][:16] + ' ' + new[0][0][17:]
            # ANISOU
            yield new[0][1][:16] + ' ' + new[0][1][17:]

        else:
            atom_lines.sort(key=lambda x: float(x[54:60]), reverse=True)
            yield atom_lines[0][:16] + ' ' + atom_lines[0][17:]


def _get_sort_atoms(altloc_lines):
    # this function is used by both:
    # flush_resloc_occ_same_residue
    # flush_resloc_id_same_residue
    all_lines = []
    for altloc, lines in altloc_lines.items():
        all_lines.extend(lines)

    # organize by atoms
    atoms = dict()
    # key in the dictionary are unique identifiers of the same residue
    for line in all_lines:
        res_number = int(line[22:26])
        res_name = line[17:20].strip()
        atom_name = line[12:16]
        atom_number = int(line[6:11])
        chain_id = line[21]
        key = (res_number, res_name, atom_name, chain_id)
        # the atom number is saved so that the original order can be kept
        alist = atoms.setdefault(key, (atom_number, []))
        alist[1].append(line)

    # entries at this point are not sorted. Sorts entries by residue
    # number followed by atom number
    sorted_atoms = sorted(list(atoms.items()), key=lambda x: (x[0][0], x[1][0]))
    return sorted_atoms


def all_same_residue(altloc_lines):
    """Assert all lines are from same residue."""
    residues = set()
    for key, val in altloc_lines.items():
        for line in val:
            resname = line[17:20]
            resnum = line[22:26].strip()
            residues.add((resname, resnum))

    return len(residues) == 1


def partial_altloc(altloc_lines):
    """Detect if the altloc positions are atoms in a single residue."""
    return ' ' in altloc_lines and all_same_residue(altloc_lines)


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
