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
Rudimentarily converts the PDB file to mmCIF format.

Will convert only the coordinate section.

Usage:
    python pdb_tocif.py <pdb file>

Example:
    python pdb_tocif.py 1CTF.pdb

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


def pad_line(line):
    """Helper function to pad line to 80 characters in case it is shorter"""
    size_of_line = len(line)
    if size_of_line < 80:
        padding = 80 - size_of_line + 1
        line = line.strip('\n') + ' ' * padding + '\n'
    return line[:81]  # 80 + newline character


def convert_to_mmcif(fhandle):
    """Converts a structure in PDB format to mmCIF format.
    """

    _pad_line = pad_line

    # The spacing here is just aesthetic purposes when printing the file
    _a = '{:<6s} {:5d} {:2s} {:6s} {:1s} {:3s} {:3s} {:1s} {:5s} {:1s} '
    _a += '{:10.3f} {:10.3f} {:10.3f} {:10.3f} {:10.3f} {:1s} '
    _a += '{:5s} {:3s} {:1s} {:4s} {:1d}\n'

    yield '# Converted to mmCIF by pdb-tools\n'
    yield '#\n'

    # Headers
    fname, _ = os.path.splitext(os.path.basename(fhandle.name))
    if fname == '<stdin>':
        fname = 'cell'
    yield 'data_{}\n'.format(fname)

    yield '#\n'
    yield 'loop_\n'
    yield '_atom_site.group_PDB\n'
    yield '_atom_site.id\n'
    yield '_atom_site.type_symbol\n'
    yield '_atom_site.label_atom_id\n'
    yield '_atom_site.label_alt_id\n'
    yield '_atom_site.label_comp_id\n'
    yield '_atom_site.label_asym_id\n'
    yield '_atom_site.label_entity_id\n'
    yield '_atom_site.label_seq_id\n'
    yield '_atom_site.pdbx_PDB_ins_code\n'
    yield '_atom_site.Cartn_x\n'
    yield '_atom_site.Cartn_y\n'
    yield '_atom_site.Cartn_z\n'
    yield '_atom_site.occupancy\n'
    yield '_atom_site.B_iso_or_equiv\n'
    yield '_atom_site.pdbx_formal_charge\n'
    yield '_atom_site.auth_seq_id\n'
    yield '_atom_site.auth_comp_id\n'
    yield '_atom_site.auth_asym_id\n'
    yield '_atom_site.auth_atom_id\n'
    yield '_atom_site.pdbx_PDB_model_num\n'

    # Coordinate data
    model_no = 1
    serial = 0

    records = (('ATOM', 'HETATM'))
    for line in fhandle:
        if line.startswith(records):
            line = _pad_line(line)

            record = line[0:6].strip()
            serial += 1

            element = line[76:78].strip()
            if not element:
                element = '?'

            atname = line[12:16].strip()
            atname = atname.replace('"', "'")
            if "'" in atname:
                atname = '"{}"'.format(atname)

            altloc = line[16]
            if altloc == ' ':
                altloc = '?'

            resname = line[17:20]
            chainid = line[21]
            if chainid == ' ':
                chainid = '?'

            resnum = line[22:26].strip()
            icode = line[26]
            if icode == ' ':
                icode = '?'

            x = float(line[30:38])
            y = float(line[38:46])
            z = float(line[46:54])

            occ = float(line[54:60])
            bfac = float(line[60:66])

            charge = line[78:80].strip()
            if charge == '':
                charge = '?'

            yield _a.format(record, serial, element, atname, altloc,
                            resname, chainid, '?', resnum, icode, x, y, z, occ,
                            bfac, charge, resnum, resname, chainid, atname,
                            model_no)

        elif line.startswith('ENDMDL'):
            model_no += 1
        else:
            continue

    yield '#'  # close block


def main():
    # Check Input
    pdbfh = check_input(sys.argv[1:])

    # Do the job
    new_cif = convert_to_mmcif(pdbfh)

    try:
        _buffer = []
        _buffer_size = 5000  # write N lines at a time
        for lineno, line in enumerate(new_cif):
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
