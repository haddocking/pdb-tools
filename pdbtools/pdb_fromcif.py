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

    Options:
        -h36: allows for hybrid36 output format for encoding >99999 atoms in the PDB file

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


digits_upper = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
digits_lower = digits_upper.lower()
digits_upper_values = dict([pair for pair in zip(digits_upper, range(36))])
digits_lower_values = dict([pair for pair in zip(digits_lower, range(36))])

def encode_pure(digits, value):
    "encodes value using the given digits"
    assert value >= 0
    if (value == 0): return digits[0]
    n = len(digits)
    result = []
    while (value != 0):
        rest = value // n
        result.append(digits[value - rest * n])
        value = rest
    result.reverse()
    return "".join(result)

def decode_pure(digits_values, s):
    "decodes the string s using the digit, value associations for each character"
    result = 0
    n = len(digits_values)
    for c in s:
        result *= n
        result += digits_values[c]
    return result

def hy36encode(width, value):
    "encodes value as base-10/upper-case base-36/lower-case base-36 hybrid"
    i = value
    if (i >= 1-10**(width-1)):
        if (i < 10**width):
            return ("%%%dd" % width) % i
        i -= 10**width
        if (i < 26*36**(width-1)):
            i += 10*36**(width-1)
            return encode_pure(digits_upper, i)
        i -= 26*36**(width-1)
        if (i < 26*36**(width-1)):
            i += 10*36**(width-1)
            return encode_pure(digits_lower, i)
    raise ValueError("value out of range.")

def hy36decode(width, s):
    "decodes base-10/upper-case base-36/lower-case base-36 hybrid"
    if (len(s) == width):
        f = s[0]
        if (f == "-" or f == " " or f.isdigit()):
            try: return int(s)
            except ValueError: pass
            if (s == " "*width): return 0
        elif (f in digits_upper_values):
            try: return decode_pure(
                digits_values=digits_upper_values, s=s) - 10*36**(width-1) + 10**width
            except KeyError: pass
        elif (f in digits_lower_values):
            try: return decode_pure(
                digits_values=digits_lower_values, s=s) + 16*36**(width-1) + 10**width
            except KeyError: pass
    raise ValueError("invalid number literal.")

def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options.
    """

    # Defaults
    h36option = False
    fh = sys.stdin  # file handle

    if not len(args):
        # Reading from pipe with default option
        if sys.stdin.isatty():
            sys.stderr.write(__doc__)
            sys.exit(1)

    elif len(args) == 1:
        # One of two options: option & Pipe OR file & default option
        if args[0] == '-h36':
            h36option = True
            if sys.stdin.isatty():  # ensure the PDB data is streamed in
                emsg = 'ERROR!! No data to process!\n'
                sys.stderr.write(emsg)
                sys.stderr.write(__doc__)
                sys.exit(1)

        if not os.path.isfile(args[0]):
            emsg = 'ERROR!! File not found or not readable: \'{}\'\n'
            sys.stderr.write(emsg.format(args[0]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        fh = open(args[0], 'r')

    elif len(args) == 2:
        # Ome options: option & File
        if not (args[0] == '-h36'):
            emsg = 'ERROR! First argument is not a valid option: \'{}\'\n'
            sys.stderr.write(emsg.format(args[0]))
            sys.stderr.write(__doc__)
            sys.exit(1)
        else:
            h36option = True

        if not os.path.isfile(args[1]):
            emsg = 'ERROR!! File not found or not readable: \'{}\'\n'
            sys.stderr.write(emsg.format(args[1]))
            sys.stderr.write(__doc__)
            sys.exit(1)

        fh = open(args[1], 'r')

    else:  # Whatever ...
        emsg = 'ERROR!! Script takes 2 argument, not \'{}\'\n'
        sys.stderr.write(emsg.format(len(args)))
        sys.stderr.write(__doc__)
        sys.exit(1)

    return fh, h36option


def run(fhandle, h36=False):
    """
    Convert a structure in mmCIF format to PDB format.

    This function is a generator.

    Parameters
    ----------
    fhandle : a line-by-line iterator of the original PDB file.

    h36 : bool
        If True, allows for hybrid_36 format enabling the encoding for >99999 atoms.

    Yields
    ------
    str (line-by-line)
        New PDB lines.
    """
    _a = "{:6s}{:5d} {:<4s}{:1s}{:3s} {:1s}{:4d}{:1s}   {:8.3f}{:8.3f}{:8.3f}"
    _a += "{:6.2f}{:6.2f}      {:<4s}{:<2s}{:2s}\n"

    not_h36 = not h36

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

            if serial < 100000:
                wserial = serial

            else:
                if not_h36 and serial > 99999:
                    emsg = 'ERROR!! Structure contains more than 99.999 atoms.\n'
                    sys.stderr.write(emsg)
                    sys.stderr.write(__doc__)
                    sys.exit(1)
                elif h36 and serial > 99999:
                     wserial = hy36encode(5, serial)

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

            try:
                charge = fields[labels.get('_atom_site.pdbx_formal_charge')]
            except TypeError:
                charge = '  '

            segid = chainid

            atom_line = _a.format(record, wserial, atname, altloc, resname,
                                  chainid, resnum, icode, x, y, z, occ, bfactor,
                                  segid, element, charge)

            atom_num += 1

            # Check if structure is too large
            if len(chainid) > 1:
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


convert_to_pdb = run


def main():
    # Check Input
    pdbfh, h36 = check_input(sys.argv[1:])

    # Do the job
    new_pdb = run(pdbfh, h36)

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
