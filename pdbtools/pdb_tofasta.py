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
Extracts the residue sequence in a PDB file to FASTA format.

Canonical amino acids and nucleotides are represented by their
one-letter code while all others are represented by 'X'.

The -multi option splits the different chains into different records in the
FASTA file.

Usage:
    python pdb_tofasta.py [-multi] <pdb file>

Example:
    python pdb_tofasta.py 1CTF.pdb

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
    option = None
    fh = sys.stdin  # file handle

    if not len(args):
        # Reading from pipe with default option
        if os.isatty(sys.stdin.fileno()):
            sys.stderr.write(__doc__)
            sys.exit(1)

    elif len(args) == 1:
        # One of two options: option & Pipe OR file & default option
        if args[0].startswith('-'):
            option = args[0][1:]
            if os.isatty(sys.stdin.fileno()):  # ensure the PDB data is streamed in
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
    if option is not None and option != 'multi':
        emsg = 'ERROR!! You provided an invalid option: \'{}\'\n'
        sys.stderr.write(emsg.format(option))
        sys.stderr.write(__doc__)
        sys.exit(1)

    return (fh, option)


def run(fhandle, multi):
    """
    Read residue names of ATOM/HETATM records and exports them to a FASTA
    file.

    This function is a generator.

    Parameters
    ----------
    fhandle : a line-by-line iterator of the original PDB file.

    multi : bool
        Whether to concatenate FASTA of multiple chains.

    Yields
    ------
    str
        The different FASTA contents.
    """
    res_codes = [
        # 20 canonical amino acids
        ('CYS', 'C'), ('ASP', 'D'), ('SER', 'S'), ('GLN', 'Q'),
        ('LYS', 'K'), ('ILE', 'I'), ('PRO', 'P'), ('THR', 'T'),
        ('PHE', 'F'), ('ASN', 'N'), ('GLY', 'G'), ('HIS', 'H'),
        ('LEU', 'L'), ('ARG', 'R'), ('TRP', 'W'), ('ALA', 'A'),
        ('VAL', 'V'), ('GLU', 'E'), ('TYR', 'Y'), ('MET', 'M'),
        # Non-canonical amino acids
        # ('MSE', 'M'), ('SOC', 'C'),
        # Canonical xNA
        ('  U', 'U'), ('  A', 'A'), ('  G', 'G'), ('  C', 'C'),
        ('  T', 'T'),
    ]

    three_to_one = dict(res_codes)
    records = ('ATOM', 'HETATM')

    sequence = []  # list of chain sequences
    seen = set()
    prev_chain = None
    for line in fhandle:
        if line.startswith(records):

            chain_id = line[21]
            if chain_id != prev_chain:
                sequence.append([chain_id])
                prev_chain = chain_id

            res_uid = line[17:27]
            if res_uid in seen:
                continue

            seen.add(res_uid)

            aa_resn = three_to_one.get(line[17:20], 'X')
            sequence[-1].append(aa_resn)

    # Yield fasta format
    _olw = 60
    if multi is None:
        # Remove chain labels and merge into one single sequence
        labels = sorted(set([c[0] for c in sequence]))
        sequence = [[r for c in sequence for r in c[1:]]]

        yield '>PDB|' + ''.join(labels) + '\n'

    for chain in sequence:
        if multi is not None:
            label = chain[0]
            yield '>PDB|' + label + '\n'
            chain = chain[1:]

        seq = ''.join(chain)
        fmt_seq = [seq[i:i + _olw] + '\n' for i in range(0, len(seq), _olw)]
        yield ''.join(fmt_seq)


pdb_to_fasta = run


def main():
    # Check Input
    pdbfh, multi = check_input(sys.argv[1:])

    # Do the job
    fasta = run(pdbfh, multi)

    # Output results
    try:
        sys.stdout.write(''.join(fasta))
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


if __name__ == '__main__':
    main()
