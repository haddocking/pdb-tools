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
"""The pdb-tools library.

A swiss army knife for manipulating and editing PDB files.

You can use pdb-tools as a library or as a series of covenient
command-line applications. The complete documentation is available at:

http://www.bonvinlab.org/pdb-tools/

Examples at the command-line
----------------------------

$ pdb_fetch 1brs > 1brs.pdb
$ pdb_reres -1 1ctf.pdb > 1ctf_renumbered.pdb
$ pdb_selchain -A,D 1brs.pdb | pdb_delhetatm | pdb_tidy > 1brs_AD_noHET.pdb


Examples using pdb-tools as library
-----------------------------------

You can use one of the following according to your needs:

>>> import pdbtools
>>> from pdbtools import *
>>> from pdbtools import PACKAGE

The list of PACKAGEs is specified bellow.

All packages have three functions: `check_input`, `main`, and `run`.
The latter executes the logic of each package. `check_input`, checks and
prepares potential input to run in case your are not sure the received
input is correct. You can chain both functions:

>>> PACKAGE.run(**PACKAGE.check_input(*args, **kwargs))

If you control the input parameters use `run` directly. In general,
`run` are generators yielding the modified PDB data line-by-line.

All PACKAGEs and `run` functions provide comprehensive docstrings:

>>> help(PACKAGE)
>>> help(PACKAGE.run)
"""

__all__ = [
    'pdb_b',
    'pdb_chainbows',
    'pdb_chain',
    'pdb_chainxseg',
    'pdb_chkensemble',
    'pdb_delchain',
    'pdb_delelem',
    'pdb_delhetatm',
    'pdb_delinsertion',
    'pdb_delresname',
    'pdb_delres',
    'pdb_element',
    'pdb_fetch',
    'pdb_fixinsert',
    'pdb_fromcif',
    'pdb_gap',
    'pdb_head',
    'pdb_intersect',
    'pdb_keepcoord',
    'pdb_merge',
    'pdb_mkensemble',
    'pdb_occ',
    'pdb_reatom',
    'pdb_reres',
    'pdb_rplchain',
    'pdb_rplresname',
    'pdb_seg',
    'pdb_segxchain',
    'pdb_selaltloc',
    'pdb_selatom',
    'pdb_selchain',
    'pdb_selelem',
    'pdb_selhetatm',
    'pdb_selresname',
    'pdb_selres',
    'pdb_selseg',
    'pdb_shiftres',
    'pdb_sort',
    'pdb_splitchain',
    'pdb_splitmodel',
    'pdb_splitseg',
    'pdb_tidy',
    'pdb_tocif',
    'pdb_tofasta',
    'pdb_uniqname',
    'pdb_validate',
    'pdb_wc',
    ]
