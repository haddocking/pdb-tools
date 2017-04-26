pdb-tools
================================================
Set of utility scripts in python to manipulate PDB files as streams. Given the generic name, there
was already another set of scripts named 'pdb-tools', which perform a very different variety of
operations on PDB files. You can find them [here](https://github.com/harmslab/pdbtools).

About
---------

Manipulating PDB files is a pain. Extracting chains, renumbering residues, splitting or merging
models or chains, modifying b-factors and occupancies, or extracting the sequence of a PDB file, are
examples of operations that can be done using any decent parsing library but it takes 1) scripting
knowledge, 2) time, and 3) almost surely a set of external dependencies installed.

The scripts in this repository simplify most of these tasks. They are the descendant of a set of old
FORTRAN77 programs in use in our lab at Utrecht that had the particular advantage of working with
streams, i.e. the output of one script could be piped into another. Since FORTRAN77 is a pain too, I
rewrote the scripts in Python and added a few more.

Requests for new scripts will be taken into consideration, depending on the effort and general
usability of the script.

Citation
------------
There is no publication (yet?) for pdb-tools, but there is a citable [DOI](http://dx.doi.org/10.5281/zenodo.31158) item. Please consider citing it in your publication if these tools were in anyway helpful.

[![DOI](https://zenodo.org/badge/18453/haddocking/pdb-tools.svg)](https://zenodo.org/badge/latestdoi/18453/haddocking/pdb-tools)

Features
------------
* Simple: one script, one job.
* Written using Python (stdlib): no compilation, cross-platform, no external dependencies
* Read data from file, or from the output of another script.

Requirements
------------
* Python 2.7 (might work on earlier versions, not really tested.)

Installation
------------
Download the zip archive or clone the repository with git. This last is the recommended option as it
is then extremely simple to get updates.

```bash
# To download
git clone https://github.com/JoaoRodrigues/pdb-tools

# To update
cd pdb-tools && git pull origin master
```

Usage
------------
All the scripts have a short description of their purpose and their usage. Just run them without any
arguments:
```bash
$ ./pdb_selchain.py

Extracts a chain from a PDB file.

usage: python pdb_selchain.py -<chain> <pdb file>
example: python pdb_selchain.py -A 1CTF.pdb

Author: Joao Rodrigues (j.p.g.l.m.rodrigues@gmail.com)

This program is part of the PDB tools distributed with HADDOCK
or with the HADDOCK tutorial. The utilities in this package
can be used to quickly manipulate PDB files, with the benefit
of 'piping' several different commands. This is a rewrite of old
FORTRAN77 code that was taking too much effort to compile. RIP.
```

Examples
------------

* Downloading a structure
   ```bash
   ./pdb_fetch.py 1ctf > 1ctf.pdb
   ./pdb_fetch.py -biounit 1brs > 1brs_biounit.pdb
   ```

* Renumbering a structure
   ```bash
   ./pdb_reres.py -1 1ctf.pdb > 1ctf_renumbered.pdb
   ```

* Extracting a particular chain
   ```bash
   ./pdb_selchain.py -A 1brs_biounit.pdb > 1brs_A.pdb
   ```

* Downloading, extracting a chain, and extracting its aa sequence
  ```bash
  ./pdb_fetch.py 1brs | ./pdb_selchain.py -A | ./pdb_toseq.py > 1brs_A.fasta
  ```

* Getting general information on a PDB file
   ```bash
   $ ./pdb_fetch.py 1brs | ./pdb_wc.py
   No. atoms:	4640	(4640.0 per model)
   No. residues:	588	(588.0 per model)
   No. chains:	6	( 6.0 per model)
   No. models:	1
   Hetero Atoms:	Yes
   Has seq. gaps:	Yes
   Double Occ.:	Yes
   Insertions:	No

   $ ./pdb_fetch.py -biounit 1brs | ./pdb_wc.py
   No. atoms:	1559	(1559.0 per model)
   No. residues:	195	(195.0 per model)
   No. chains:	2	( 2.0 per model)
   No. models:	2
   Hetero Atoms:	Yes
   Has seq. gaps:	Yes
   Double Occ.:	Yes
   Insertions:	No
   ```

* Finding gaps in a PDB file
   ```bash
   $ ./pdb_fetch.py -biounit 1brs | ./pdb_gap.py
   D:THR63 <    4.88A > D:GLY66
   ```

License
---------
Apache2. See LICENSE file.
