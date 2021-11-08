#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2021 João MC Teixeira
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
Renames hydrogen according to the communitie's conversion tables.

Available conversions:
    - bmrb/iupac/pdbv3/xplor
    - pdb old format
    - ucsf

Usage:
    python pdb_selatom.py -<option> <pdb file>

Example:
    python pdb_renameatom.py -xplor 2M9Y.pdb

This program is part of the `pdb-tools` suite of utilities and should not be
distributed isolatedly. The `pdb-tools` were created to quickly manipulate PDB
files using the terminal, and can be used sequentially, with one tool streaming
data to another. They are based on old FORTRAN77 code that was taking too much
effort to maintain and compile. RIP.
"""
import sys
import os


bmrb = {
    'ALA': ['N', 'CA', 'C', 'O', 'CB', 'H', 'H1', 'H2', 'H3', 'HA', 'HB1', 'HB2', 'HB3'],
    'ARG': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD', 'NE', 'CZ', 'NH1', 'NH2', 'H', 'H1', 'H2', 'H3', 'HA', 'HB2', 'HB3', 'HG2', 'HG3', 'HD2', 'HD3', 'HE', 'HH11', 'HH12', 'HH21', 'HH22'],
    'ASN': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'OD1', 'ND2', 'H', 'H1', 'H2', 'H3', 'HA', 'HB2', 'HB3', 'HD21', 'HD22'],
    'ASP': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'OD1', 'OD2', 'H', 'H1', 'H2', 'H3', 'HA', 'HB2', 'HB3', 'HD2'],
    'CYS': ['N', 'CA', 'C', 'O', 'CB', 'SG', 'H', 'H1', 'H2', 'H3', 'HA', 'HB2', 'HB3', 'HG'],
    'GLN': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD', 'OE1', 'NE2', 'H', 'H1', 'H2', 'H3', 'HA', 'HB2', 'HB3', 'HG2', 'HG3', 'HE21', 'HE22'],
    'GLU': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD', 'OE1', 'OE2', 'H', 'H1', 'H2', 'H3', 'HA', 'HB2', 'HB3', 'HG2', 'HG3', 'HE2'],
    'GLY': ['N', 'CA', 'C', 'O', 'H', 'H1', 'H2', 'H3', 'HA2', 'HA3'],
    'HIS': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'ND1', 'CD2', 'CE1', 'NE2', 'H', 'H1', 'H2', 'H3', 'HA', 'HB2', 'HB3', 'HD1', 'HD2', 'HE1', 'HE2'],
    'ILE': ['N', 'CA', 'C', 'O', 'CB', 'CG1', 'CG2', 'CD1', 'H', 'H1', 'H2', 'H3', 'HA', 'HB', 'HG12', 'HG13', 'HG21', 'HG22', 'HG23', 'HD11', 'HD12', 'HD13'],
    'LEU': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD1', 'CD2', 'H', 'H1', 'H2', 'H3', 'HA', 'HB2', 'HB3', 'HG', 'HD11', 'HD12', 'HD13', 'HD21', 'HD22', 'HD23'],
    'LYS': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD', 'CE', 'NZ', 'H', 'H1', 'H2', 'H3', 'HA', 'HB2', 'HB3', 'HG2', 'HG3', 'HD2', 'HD3', 'HE2', 'HE3', 'HZ1', 'HZ2', 'HZ3'],
    'MET': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'SD', 'CE', 'H', 'H1', 'H2', 'H3', 'HA', 'HB2', 'HB3', 'HG2', 'HG3', 'HE1', 'HE2', 'HE3'],
    'PHE': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD1', 'CD2', 'CE1', 'CE2', 'CZ', 'H', 'H1', 'H2', 'H3', 'HA', 'HB2', 'HB3', 'HD1', 'HD2', 'HE1', 'HE2', 'HZ'],
    'PRO': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD', 'H2', 'H3', 'HA', 'HB2', 'HB3', 'HG2', 'HG3', 'HD2', 'HD3'],
    'SER': ['N', 'CA', 'C', 'O', 'CB', 'OG', 'H', 'H1', 'H2', 'H3', 'HA', 'HB2', 'HB3', 'HG'],
    'THR': ['N', 'CA', 'C', 'O', 'CB', 'OG1', 'CG2', 'H', 'H1', 'H2', 'H3', 'HA', 'HB', 'HG1', 'HG21', 'HG22', 'HG23'],
    'TRP': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD1', 'CD2', 'NE1', 'CE2', 'CE3', 'CZ2', 'CZ3', 'CH2', 'H', 'H1', 'H2', 'H3', 'HA', 'HB2', 'HB3', 'HD1', 'HE1', 'HE3', 'HZ2', 'HZ3', 'HH2'],
    'TYR': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD1', 'CD2', 'CE1', 'CE2', 'CZ', 'OH', 'H', 'H1', 'H2', 'H3', 'HA', 'HB2', 'HB3', 'HD1', 'HD2', 'HE1', 'HE2', 'HH'],
    'VAL': ['N', 'CA', 'C', 'O', 'CB', 'CG1', 'CG2', 'H', 'H1', 'H2', 'H3', 'HA', 'HB', 'HG11', 'HG12', 'HG13', 'HG21', 'HG22', 'HG23'],
    }

diana = {
    'ALA': ['N', 'CA', 'C', 'O', 'CB', 'HN', 'H1', 'H2', 'H3', 'HA', 'HB1', 'HB2', 'HB3'],
    'ARG': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD', 'NE', 'CZ', 'NH1', 'NH2', 'HN', 'H1', 'H2', 'H3', 'HA', 'HB2', 'HB3', 'HG2', 'HG3', 'HD2', 'HD3', 'HE', 'HH11', 'HH12', 'HH21', 'HH22'],
    'ASN': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'OD1', 'ND2', 'HN', 'H1', 'H2', 'H3', 'HA', 'HB2', 'HB3', 'HD21', 'HD22'],
    'ASP': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'OD1', 'OD2', 'HN', 'H1', 'H2', 'H3', 'HA', 'HB2', 'HB3', 'HD2'],
    'CYS': ['N', 'CA', 'C', 'O', 'CB', 'SG', 'HN', 'H1', 'H2', 'H3', 'HA', 'HB2', 'HB3', 'HG'],
    'GLN': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD', 'OE1', 'NE2', 'HN', 'H1', 'H2', 'H3', 'HA', 'HB2', 'HB3', 'HG2', 'HG3', 'HE21', 'HE22'],
    'GLU': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD', 'OE1', 'OE2', 'HN', 'H1', 'H2', 'H3', 'HA', 'HB2', 'HB3', 'HG2', 'HG3', 'HE2'],
    'GLY': ['N', 'CA', 'C', 'O', 'HN', 'H1', 'H2', 'H3', 'HA2', 'HA3'],
    'HIS': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'ND1', 'CD2', 'CE1', 'NE2', 'HN', 'H1', 'H2', 'H3', 'HA', 'HB2', 'HB3', 'HD1', 'HD2', 'HE1', 'HE2'],
    'ILE': ['N', 'CA', 'C', 'O', 'CB', 'CG1', 'CG2', 'CD1', 'HN', 'H1', 'H2', 'H3', 'HA', 'HB', 'HG12', 'HG13', 'HG21', 'HG22', 'HG23', 'HD11', 'HD12', 'HD13'],
    'LEU': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD1', 'CD2', 'HN', 'H1', 'H2', 'H3', 'HA', 'HB2', 'HB3', 'HG', 'HD11', 'HD12', 'HD13', 'HD21', 'HD22', 'HD23'],
    'LYS': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD', 'CE', 'NZ', 'HN', 'H1', 'H2', 'H3', 'HA', 'HB2', 'HB3', 'HG2', 'HG3', 'HD2', 'HD3', 'HE2', 'HE3', 'HZ1', 'HZ2', 'HZ3'],
    'MET': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'SD', 'CE', 'HN', 'H1', 'H2', 'H3', 'HA', 'HB2', 'HB3', 'HG2', 'HG3', 'HE1', 'HE2', 'HE3'],
    'PHE': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD1', 'CD2', 'CE1', 'CE2', 'CZ', 'HN', 'H1', 'H2', 'H3', 'HA', 'HB2', 'HB3', 'HD1', 'HD2', 'HE1', 'HE2', 'HZ'],
    'PRO': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD', 'H2', 'H3', 'HA', 'HB2', 'HB3', 'HG2', 'HG3', 'HD2', 'HD3'],
    'SER': ['N', 'CA', 'C', 'O', 'CB', 'OG', 'HN', 'H1', 'H2', 'H3', 'HA', 'HB2', 'HB3', 'HG'],
    'THR': ['N', 'CA', 'C', 'O', 'CB', 'OG1', 'CG2', 'HN', 'H1', 'H2', 'H3', 'HA', 'HB', 'HG1', 'HG21', 'HG22', 'HG23'],
    'TRP': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD1', 'CD2', 'NE1', 'CE2', 'CE3', 'CZ2', 'CZ3', 'CH2', 'HN', 'H1', 'H2', 'H3', 'HA', 'HB2', 'HB3', 'HD1', 'HE1', 'HE3', 'HZ2', 'HZ3', 'HH2'],
    'TYR': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD1', 'CD2', 'CE1', 'CE2', 'CZ', 'OH', 'HN', 'H1', 'H2', 'H3', 'HA', 'HB2', 'HB3', 'HD1', 'HD2', 'HE1', 'HE2', 'HH'],
    'VAL': ['N', 'CA', 'C', 'O', 'CB', 'CG1', 'CG2', 'HN', 'H1', 'H2', 'H3', 'HA', 'HB', 'HG11', 'HG12', 'HG13', 'HG21', 'HG22', 'HG23'],
    }

ucsf = {
    'ALA': ['N', 'CA', 'C', 'O', 'CB', 'HN', 'HN1', 'HN2', 'HN3', 'HA', 'HB1', 'HB2', 'HB3'],
    'ARG': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD', 'NE', 'CZ', 'NH1', 'NH2', 'HN', 'HN1', 'HN2', 'HN3', 'HA', 'HB1', 'HB2', 'HG1', 'HG2', 'HD1', 'HD2', 'HNE', 'HN11', 'HN12', 'HN21', 'HN22'],
    'ASN': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'OD1', 'ND2', 'HN', 'HN1', 'HN2', 'HN3', 'HA', 'HB1', 'HB2', 'HN21', 'HN22'],
    'ASP': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'OD1', 'OD2', 'HN', 'HN1', 'HN2', 'HN3', 'HA', 'HB1', 'HB2', 'HOG'],
    'CYS': ['N', 'CA', 'C', 'O', 'CB', 'SG', 'HN', 'HN1', 'HN2', 'HN3', 'HA', 'HB1', 'HB2', 'HSG'],
    'GLN': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD', 'OE1', 'NE2', 'HN', 'HN1', 'HN2', 'HN3', 'HA', 'HB1', 'HB2', 'HG1', 'HG2', 'HN21', 'HN22'],
    'GLU': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD', 'OE1', 'OE2', 'HN', 'HN1', 'HN2', 'HN3', 'HA', 'HB1', 'HB2', 'HG1', 'HG2', 'HOE'],
    'GLY': ['N', 'CA', 'C', 'O', 'HN', 'HN1', 'HN2', 'HN3', 'HA1', 'HA2'],
    'HIS': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'ND1', 'CD2', 'CE1', 'NE2', 'HN', 'HN1', 'HN2', 'HN3', 'HA', 'HB1', 'HB2', 'HND1', 'HD2', 'HE1', 'HNE2'],
    'ILE': ['N', 'CA', 'C', 'O', 'CB', 'CG1', 'CG2', 'CD1', 'HN', 'HN1', 'HN2', 'HN3', 'HA', 'HB', 'HG11', 'HG12', 'HG21', 'HG22', 'HG23', 'HD11', 'HD12', 'HD13'],
    'LEU': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD1', 'CD2', 'HN', 'HN1', 'HN2', 'HN3', 'HA', 'HB1', 'HB2', 'HG', 'HD11', 'HD12', 'HD13', 'HD21', 'HD22', 'HD23'],
    'LYS': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD', 'CE', 'NZ', 'HN', 'HN1', 'HN2', 'HN3', 'HA', 'HB1', 'HB2', 'HG1', 'HG2', 'HD1', 'HD2', 'HE1', 'HE2', 'HNZ1', 'HNZ2', 'HNZ3'],
    'MET': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'SD', 'CE', 'HN', 'HN1', 'HN2', 'HN3', 'HA', 'HB1', 'HB2', 'HG1', 'HG2', 'HE1', 'HE2', 'HE3'],
    'PHE': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD1', 'CD2', 'CE1', 'CE2', 'CZ', 'HN', 'HN1', 'HN2', 'HN3', 'HA', 'HB1', 'HB2', 'HD1', 'HD2', 'HE1', 'HE2', 'HZ'],
    'PRO': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD', 'HN2', 'HN3', 'HA', 'HB1', 'HB2', 'HG1', 'HG2', 'HD2', 'HD1'],
    'SER': ['N', 'CA', 'C', 'O', 'CB', 'OG', 'HN', 'HN1', 'HN2', 'HN3', 'HA', 'HB1', 'HB2', 'HOG'],
    'THR': ['N', 'CA', 'C', 'O', 'CB', 'OG1', 'CG2', 'HN', 'HN1', 'HN2', 'HN3', 'HA', 'HB', 'HOG1', 'HG21', 'HG22', 'HG23'],
    'TRP': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD1', 'CD2', 'NE1', 'CE2', 'CE3', 'CZ2', 'CZ3', 'CH2', 'HN', 'HN1', 'HN2', 'HN3', 'HA', 'HB1', 'HB2', 'HD1', 'HNE1', 'HE3', 'HZ2', 'HZ3', 'HH2'],
    'TYR': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD1', 'CD2', 'CE1', 'CE2', 'CZ', 'OH', 'HN', 'HN1', 'HN2', 'HN3', 'HA', 'HB1', 'HB2', 'HD1', 'HD2', 'HE1', 'HE2', 'HOH'],
    'VAL': ['N', 'CA', 'C', 'O', 'CB', 'CG1', 'CG2', 'HN', 'HN1', 'HN2', 'HN3', 'HA', 'HB', 'HG11', 'HG12', 'HG13', 'HG21', 'HG22', 'HG23'],
    }

old_pdb = {
    'ALA': ['N', 'CA', 'C', 'O', 'CB', 'H', '1H', '2H', '3H', 'HA', '1HB', '2HB', '3HB'],
    'ARG': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD', 'NE', 'CZ', 'NH1', 'NH2', 'H', '1H', '2H', '3H', 'HA', '1HB', '2HB', '1HG', '2HG', '1HD', '2HD', 'HE', '1HH1', '2HH1', '1HH2', '2HH2'],
    'ASN': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'OD1', 'ND2', 'H', '1H', '2H', '3H', 'HA', '1HB', '2HB', '1HD2', '2HD2'],
    'ASP': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'OD1', 'OD2', 'H', '1H', '2H', '3H', 'HA', '1HB', '2HB', '1HD'],
    'CYS': ['N', 'CA', 'C', 'O', 'CB', 'SG', 'H', '1H', '2H', '3H', 'HA', '1HB', '2HB', 'HG'],
    'GLN': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD', 'OE1', 'NE2', 'H', '1H', '2H', '3H', 'HA', '1HB', '2HB', '1HG', '2HG', '1HE2', '2HE2'],
    'GLU': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD', 'OE1', 'OE2', 'H', '1H', '2H', '3H', 'HA', '1HB', '2HB', '1HG', '2HG', '1HE'],
    'GLY': ['N', 'CA', 'C', 'O', 'H', '1H', '2H', '3H', '1HA', '2HA'],
    'HIS': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'ND1', 'CD2', 'CE1', 'NE2', 'H', '1H', '2H', '3H', 'HA', '1HB', '2HB', 'HD1', 'HD2', 'HE1', 'HE2'],
    'ILE': ['N', 'CA', 'C', 'O', 'CB', 'CG1', 'CG2', 'CD1', 'H', '1H', '2H', '3H', 'HA', 'HB', '1HG1', '2HG1', '1HG2', '2HG2', '3HG2', '1HD1', '2HD1', '3HD1'],
    'LEU': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD1', 'CD2', 'H', '1H', '2H', '3H', 'HA', '1HB', '2HB', 'HG', '1HD1', '2HD1', '3HD1', '1HD2', '2HD2', '3HD2'],
    'LYS': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD', 'CE', 'NZ', 'H', '1H', '2H', '3H', 'HA', '1HB', '2HB', '1HG', '2HG', '1HD', '2HD', '1HE', '2HE', '1HZ', '2HZ', '3HZ'],
    'MET': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'SD', 'CE', 'H', '1H', '2H', '3H', 'HA', '1HB', '2HB', '1HG', '2HG', '1HE', '2HE', '3HE'],
    'PHE': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD1', 'CD2', 'CE1', 'CE2', 'CZ', 'H', '1H', '2H', '3H', 'HA', '1HB', '2HB', 'HD1', 'HD2', 'HE1', 'HE2', 'HZ'],
    'PRO': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD', 'HA', 'H2', 'H1', '1HB', '2HB', '1HG', '2HG', '1HD', '2HD'],
    'SER': ['N', 'CA', 'C', 'O', 'CB', 'OG', 'H', '1H', '2H', '3H', 'HA', '1HB', '2HB', 'HG'],
    'THR': ['N', 'CA', 'C', 'O', 'CB', 'OG1', 'CG2', 'H', '1H', '2H', '3H', 'HA', 'HB', 'HG1', '1HG2', '2HG2', '3HG2'],
    'TRP': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD1', 'CD2', 'NE1', 'CE2', 'CE3', 'CZ2', 'CZ3', 'CH2', 'H', '1H', '2H', '3H', 'HA', '1HB', '2HB', 'HD1', 'HE1', 'HE3', 'HZ2', 'HZ3', 'HH2'],
    'TYR': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD1', 'CD2', 'CE1', 'CE2', 'CZ', 'OH', 'H', '1H', '2H', '3H', 'HA', '1HB', '2HB', 'HD1', 'HD2', 'HE1', 'HE2', 'HH'],
    'VAL': ['N', 'CA', 'C', 'O', 'CB', 'CG1', 'CG2', 'H', '1H', '2H', '3H', 'HA', 'HB', '1HG1', '2HG1', '3HG1', '1HG2', '2HG2', '3HG2'],
    }

xplor = {
    'ALA': ['N', 'CA', 'C', 'O', 'CB', 'HN', 'HT1', 'HT2', 'HT3', 'HA', '1HB', '2HB', '3HB'],
    'ARG': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD', 'NE', 'CZ', 'NH1', 'NH2', 'HN', 'HT1', 'HT2', 'HT3', 'HA', 'HB2', 'HB1', 'HG2', 'HG1', 'HD2', 'HD1', 'HE', 'HH11', 'HH12', 'HH21', 'HH22'],
    'ASN': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'OD1', 'ND2', 'HN', 'HT1', 'HT2', 'HT3', 'HA', 'HB2', 'HB1', 'HD21', 'HD22'],
    'ASP': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'OD1', 'OD2', 'HN', 'HT1', 'HT2', 'HT3', 'HA', 'HB2', 'HB1', 'HD1'],
    'CYS': ['N', 'CA', 'C', 'O', 'CB', 'SG', 'HN', 'HT1', 'HT2', 'HT3', 'HA', 'HB2', 'HB1', 'HG'],
    'GLN': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD', 'OE1', 'NE2', 'HN', 'HT1', 'HT2', 'HT3', 'HA', 'HB2', 'HB1', 'HG2', 'HG1', 'HE21', 'HE22'],
    'GLU': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD', 'OE1', 'OE2', 'HN', 'HT1', 'HT2', 'HT3', 'HA', '1HB', '2HB', '1HG', '2HG', '1HE'],
    'GLY': ['N', 'CA', 'C', 'O', 'HN', 'HT1', 'HT2', 'HT3', 'HA2', 'HA1'],
    'HIS': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'ND1', 'CD2', 'CE1', 'NE2', 'HN', 'HT1', 'HT2', 'HT3', 'HA', 'HB2', 'HB1', 'HD1', 'HD2', 'HE1', 'HE2'],
    'ILE': ['N', 'CA', 'C', 'O', 'CB', 'CG1', 'CG2', 'CD1', 'HN', 'HT1', 'HT2', 'HT3', 'HA', 'HB', 'HG12', 'HG11', 'HG21', 'HG22', 'HG23', 'HD11', 'HD12', 'HD13'],
    'LEU': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD1', 'CD2', 'HN', 'HT1', 'HT2', 'HT3', 'HA', 'HB2', 'HB1', 'HG', 'HD11', 'HD12', 'HD13', 'HD21', 'HD22', 'HD23'],
    'LYS': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD', 'CE', 'NZ', 'HN', 'HT1', 'HT2', 'HT3', 'HA', 'HB2', 'HB1', 'HG2', 'HG1', 'HD2', 'HD1', 'HE2', 'HE1', 'HZ1', 'HZ2', 'HZ3'],
    'MET': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'SD', 'CE', 'HN', 'HT1', 'HT2', 'HT3', 'HA', 'HB2', 'HB1', 'HG2', 'HG1', 'HE1', 'HE2', 'HE3'],
    'PHE': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD1', 'CD2', 'CE1', 'CE2', 'CZ', 'HN', 'HT1', 'HT2', 'HT3', 'HA', 'HB2', 'HB1', 'HD1', 'HD2', 'HE1', 'HE2', 'HZ'],
    'PRO': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD', 'HA', 'HT2', 'HT1', 'HB2', 'HB1', 'HG2', 'HG1', 'HD2', 'HD1'],
    'SER': ['N', 'CA', 'C', 'O', 'CB', 'OG', 'HN', 'HT1', 'HT2', 'HT3', 'HA', 'HB2', 'HB1', 'HG'],
    'THR': ['N', 'CA', 'C', 'O', 'CB', 'OG1', 'CG2', 'HN', 'HT1', 'HT2', 'HT3', 'HA', 'HB', 'HG1', 'HG21', 'HG22', 'HG23'],
    'TRP': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD1', 'CD2', 'NE1', 'CE2', 'CE3', 'CZ2', 'CZ3', 'CH2', 'HN', 'HT1', 'HT2', 'HT3', 'HA', 'HB2', 'HB1', 'HD1', 'HE1', 'HE3', 'HZ2', 'HZ3', 'HH2'],
    'TYR': ['N', 'CA', 'C', 'O', 'CB', 'CG', 'CD1', 'CD2', 'CE1', 'CE2', 'CZ', 'OH', 'HN', 'HT1', 'HT2', 'HT3', 'HA', 'HB2', 'HB1', 'HD1', 'HD2', 'HE1', 'HE2', 'HH'],
    'VAL': ['N', 'CA', 'C', 'O', 'CB', 'CG1', 'CG2', 'HN', 'HT1', 'HT2', 'HT3', 'HA', 'HB', 'HG11', 'HG12', 'HG13', 'HG21', 'HG22', 'HG23'],
    }


convert_table = {
    'bmrb': bmrb,
    'amber': bmrb,
    'pdbv3': bmrb,
    'oldpdb': old_pdb,
    'xplor': xplor,
    'ucsf': ucsf,
    }


for key in bmrb.keys():
    assert len(bmrb[key]) == len(xplor[key]) == len(old_pdb[key]) == len(ucsf[key]), key


def check_input(args):
    """Checks whether to read from stdin/file and validates user input/options.
    """
    if not args:
        emsg = 'ERROR! No input provided{}'
        sys.stderr.write(emsg.format(os.linesep))
        sys.stderr.write(__doc__)
        sys.exit(1)

    if len(args) > 2:
        emsg = 'ERROR! Too many arguments.'
        sys.stderr.write(emsg)
        sys.stderr.write(__doc__)
        sys.exit(1)

    # The first argument is mandatory, you always need to select an atom
    if not args[0].startswith('-'):
        emsg = 'ERROR! First argument is not an option: \'{}\'{}'
        sys.stderr.write(emsg.format(args[0], os.linesep))
        sys.stderr.write(__doc__)
        sys.exit(1)

    # atom names have at most 4 characters
    option = args[0][1:]
    if option not in convert_table.keys():
        emsg = 'ERROR! The option provided {!r} is not within the possible options: {}. {}'
        sys.stderr.write(emsg.format(option, list(convert_table.keys()), os.linesep))
        sys.stderr.write(__doc__)
        sys.exit(1)

    # Pipe or file
    if sys.stdin.isatty():  # ensure the PDB data is streamed in
        if len(args) == 1:
            emsg = 'ERROR!! No file provided.'
            sys.stderr.write(emsg)
            sys.stderr.write(__doc__)
            sys.exit(1)

        if not os.path.isfile(args[1]):
            emsg = 'ERROR!! File not found or not readable: \'{}\'{}'
            emsg = emsg.format(args[1], os.linesep)
            sys.stderr.write(emsg)
            sys.stderr.write(__doc__)
            sys.exit(1)

        fh = open(args[1], 'r')

    else:  # input comes from pipe
        fh = sys.stdin

    return fh, option


def run(fhandle, option):
    """
    Renames hydrogen according to the communitie's conversion tables.

    Available conversions:
        - bmrb/iupac/pdbv3
        - xplor
        - pdb old format
        - ucsf

    This function is a generator.

    Parameters
    ----------
    fhandle : a line-by-line iterator of the original PDB file.

    option : a conversion option.

    Yields
    ------
    str (line-by-line)
        All non-RECORD lines and RECORD lines within the new atom names.
    """
    records = ('ATOM', 'HETATM', 'ANISOU')
    for line in fhandle:
        if line.startswith(records):
            atom_source = line[12:16].strip()
            residue = line[17:20].strip().upper()

            for convention in convert_table.values():
                try:
                    idx = convention[residue].index(atom_source)
                except ValueError:
                    continue

            new_atom = convert_table[option][residue][idx]

            if 1 <= len(new_atom) <= 3:
                new_atom = ' {:<3s}'.format(new_atom)
            elif len(new_atom) == 4:
                new_atom  = '{:<4s}'.format(new_atom)
            else:
                raise ValueError('Something went very badly')

            line = line[:12] + new_atom + line[16:]

        yield line


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
