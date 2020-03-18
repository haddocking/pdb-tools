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
Rudimentarily converts a mmCIF file to the PDB format. 

Will not convert if the file does not 'fit' in PDB format, e.g. too many
chains, residues, or atoms. Will convert only the coordinate section.

Usage:
    python pdb_fromcif.py <pdb file>

Example:
    python pdb_fromcif.py 1CTF.pdb

This program is part of the `pdb-tools` suite of utilities and should not be
distributed isolatedly. The `pdb-tools` were created to quickly manipulate PDB
files using the terminal, and can be used sequentially, with one tool streaming
data to another. They are based on old FORTRAN77 code that was taking too much
effort to maintain and compile. RIP.
"""

import os
import re
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


def convert_to_pdb(fhandle):
    """Converts a structure in mmCIF format to PDB format.
    """

    _a = "{:6s}{:5d} {:<4s}{:1s}{:3s} {:1s}{:4d}{:1s}   {:8.3f}{:8.3f}{:8.3f}"
    _a += "{:6.2f}{:6.2f}      {:<4s}{:<2s}{:2s}\n"

    in_section, read_atom = False, False

    label_pos = 0
    labels = {}
    empty = set(('.', '?'))

    prev_model = None
    atom_num = 0
    serial = 0  # do not read serial numbers from mmCIF. Wrong in multi-models.

    model_data = []  # store atom data to account for multi-model files
    for line in fhandle:
        if line.startswith('loop_'):  # start of section
            in_section = True

        elif line.startswith('#'):  # end of section
            in_section = False
            read_atom = False

        elif in_section and line.startswith('_atom_site.'):  # ATOM/HETATM
            read_atom = True
            labels[line.strip()] = label_pos
            label_pos += 1

        elif read_atom and line.startswith(('ATOM', 'HETATM')):  # convert
            fields = re.findall(r'[^"\s]\S*|".+?"', line)  # find enclosed ''

            # Pick fields, giving preference to auth to match PDBs
            # http://mmcif.wwpdb.org/docs/pdb_to_pdbx_correspondences.html
            model_no = fields[labels.get('_atom_site.pdbx_PDB_model_num')]
            if prev_model != model_no:  # first line will trigger
                prev_model = model_no
                model_data.append([])
                serial = 0

            record = fields[labels.get('_atom_site.group_PDB')]

            # serial = int(fields[labels.get('_atom_site.id')])
            serial += 1

            fid = labels.get('_atom_site.auth_atom_id')
            if fid is None:
                fid = labels.get('_atom_site.label_atom_id')
            atname = fields[fid]

            element = fields[labels.get('_atom_site.type_symbol')]
            if element in empty:
                element = ' '

            # handle atom name
            if atname[0] == '"' and atname[-1] == '"':
                atname = atname[1:-1]

            if len(atname) < 4 and atname[0].isalpha() and len(element) < 2:
                atname = ' ' + atname  # pad

            altloc = fields[labels.get('_atom_site.label_alt_id')]
            if altloc in empty:
                altloc = ' '

            fid = labels.get('_atom_site.auth_comp_id')
            if fid is None:
                fid = labels.get('_atom_site.label_comp_id')
            resname = fields[fid]

            fid = labels.get('_atom_site.auth_asym_id')
            if fid is None:
                fid = labels.get('_atom_site.label_asym_id')
            chainid = fields[fid]

            fid = labels.get('_atom_site.auth_seq_id')
            if fid is None:
                fid = labels.get('_atom_site.label_seq_id')
            resnum = int(fields[fid])

            icode = fields[labels.get('_atom_site.pdbx_PDB_ins_code')]
            if icode in empty:
                icode = ' '

            x = float(fields[labels.get('_atom_site.Cartn_x')])
            y = float(fields[labels.get('_atom_site.Cartn_y')])
            z = float(fields[labels.get('_atom_site.Cartn_z')])
            occ = float(fields[labels.get('_atom_site.occupancy')])
            bfactor = float(fields[labels.get('_atom_site.B_iso_or_equiv')])

            charge = fields[labels.get('_atom_site.pdbx_formal_charge')]
            try:
                charge = charge
            except ValueError:
                charge = '  '

            segid = chainid

            atom_line = _a.format(record, serial, atname, altloc, resname,
                                  chainid, resnum, icode, x, y, z, occ, bfactor,
                                  segid, element, charge)

            atom_num += 1

            # Check if structure is too large
            if atom_num > 99999:
                emsg = 'ERROR!! Number of atoms exceeds PDB format limit: \'{}\'\n'
                sys.stderr.write(emsg.format(atom_num))
                sys.stderr.write(__doc__)
                sys.exit(1)
            elif len(chainid) > 1:
                emsg = 'ERROR!! Chain IDs is too large: \'{}\'\n'
                sys.stderr.write(emsg.format(chainid))
                sys.stderr.write(__doc__)
                sys.exit(1)
            elif resnum > 9999:
                emsg = 'ERROR!! Too many residues (\'{}\') in chain \'{}\' \n'
                sys.stderr.write(emsg.format(resnum, chainid))
                sys.stderr.write(__doc__)
                sys.exit(1)

            model_data[-1].append(atom_line)

    # Check if multi-model
    is_ensemble = len(model_data) > 1
    if is_ensemble:
        for model_no, model in enumerate(model_data, start=1):
            yield "MODEL {:>5d}\n".format(model_no)
            for line in model:
                yield line
            yield 'ENDMDL\n'
    else:
        for line in model_data[0]:
            yield line

    yield "{:<80s}\n".format("END")


def main():
    # Check Input
    pdbfh = check_input(sys.argv[1:])

    # Do the job
    new_pdb = convert_to_pdb(pdbfh)

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
