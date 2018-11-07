pdb-tools
================================================
Set of Python scripts designed to be a dependency-free cross-platform 
swiss-knife for PDB files.


Looking for the _other_ pdb-tools?
----------------------------------
Given the very unoriginal name, there was bound to exist another set of scripts
with the same name. The original `pdb-tools` perform a very different variety of
operations on PDB files and can be found [here](https://github.com/harmslab/pdbtools).

What can I do with them?
------------------------
The names of the tools should be self-explanatory. Their usage is also pretty
consistent. Therefore, here is a couple of examples to get you started:

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

What _can't_ I do with them?
------------------------
mmCIF files are not supported. There might be a sister repository `mmcif-tools`
one day. Also, operations that involve coordinates or numerical calculations are
usually not in the scope of `pdb-tools`. Use a proper library for that, it will
be much faster and scalable.

About
---------
Manipulating PDB files is often painful. Extracting a particular chain or set of
residues, renumbering residues, splitting or merging models and chains, or just
ensuring the file is conforming to the PDB specifications are examples of tasks
that can be done using any decent parsing library or graphical interface. These,
however, almost always require 1) scripting knowledge, 2) time, and 3) installing
one or more programs.

`pdb-tools` were designed to be a swiss-knife for the PDB format. They have no
external dependencies, besides obviously the [Python programming language](http://www.python.org).
They are the descendant of a set of old FORTRAN77 programs that had the 
particular advantage of working with streams, i.e. the output of one script 
could be piped into another. Since FORTRAN77 is a pain too, I rewrote them in
Python and added a few more utilities. 

The philosophy of the scripts is simple: one script, one task. If you want to 
do two things, pipe the scripts together. Requests for new scripts will be taken
into consideration - use the Issues button or write them yourself and create a
Pull Request.

Citation
------------
There is no publication (yet!) for pdb-tools, but if you use them and want to
cite them use this [DOI](http://dx.doi.org/10.5281/zenodo.31158) item.

[![DOI](https://zenodo.org/badge/18453/haddocking/pdb-tools.svg)](https://zenodo.org/badge/latestdoi/18453/haddocking/pdb-tools)


Requirements
------------
* Python 2.7+ and 3.x

Installation
------------
Download the zip archive or clone the repository with git. We recommend the `git`
approach since it makes updating the tools extremely simple.

```bash
# To download
git clone https://github.com/JoaoRodrigues/pdb-tools

# To update
cd pdb-tools && git pull origin master
```

License
---------
`pdb-tools` are open-source and licensed under the Apache License, version 2.0.
For details, see the LICENSE file.