#!/usr/bin/env python

"""
Compares two PDB files.

Takes as input two PDB files: a reference and a target.

Outputs two PDB files:
  the reference file without atoms not present in the target
  the target file without atoms not present in the reference

(e.g. use this before RMSD calculations)

usage: python {0} refe.pdb target.pdb
"""

from __future__ import print_function

import os
import sys

def _build_atom_unique_id(atom_line):
    """Returns a unique identifying tuple from an ATOM line"""

    # unique_id: (name, altloc, resi, insert, chain, segid)
    unique_id = (atom_line[12:16], atom_line[16], int(atom_line[22:26]), atom_line[26], atom_line[21], atom_line[72:76].strip())
    return unique_id

def build_atom_set(pdbfile):
    """Builds a set with a unique entry for each atom."""

    atom_set = set()
    with open(pdbfile) as handle:
        for line in handle:
            if not line.startswith('ATOM'):
                continue
            unique_id = _build_atom_unique_id(line)
            atom_set.add(unique_id)

    return atom_set

def remove_mismatching_atoms(pdbfile, mismatching_set):
    """Outputs atoms lines that do not match the mismatching set"""

    with open(pdbfile) as handle:
        for line in handle:
            line = line.strip()
            if line.startswith('ATOM'):
                unique_id = _build_atom_unique_id(line)
                if unique_id in mismatching_set:
                    continue
            yield line + '\n'

def write_pdb_file(pdbdata, filename):
    """Writes a PDB file data to disk"""
    if os.path.isfile(filename):
        sys.stderr.write('Failed. Output file exists: {0}\n'.format(filename))
        return

    with open(filename, 'w') as ohandle:
        ohandle.write(''.join(pdbdata))

    return

if __name__ == '__main__':

    cmd_args = sys.argv[1:]
    if not cmd_args or len(cmd_args) != 2:
        print(__doc__.format(sys.argv[0]))
        sys.exit(1)

    reference_pdb, target_pdb = map(os.path.abspath, cmd_args)

    reference_set = build_atom_set(reference_pdb)
    target_set = build_atom_set(target_pdb)
    mismatching = reference_set ^ target_set

    harmonized_reference = remove_mismatching_atoms(reference_pdb, mismatching)
    harmonized_target = remove_mismatching_atoms(target_pdb, mismatching)

    write_pdb_file(harmonized_reference, reference_pdb[:-4]+'-harmonized.pdb')
    write_pdb_file(harmonized_target, target_pdb[:-4]+'-harmonized.pdb')
