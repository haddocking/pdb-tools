# pdb-tools

[![PyPI version](https://badge.fury.io/py/pdb-tools.svg)](https://pypi.python.org/pypi/pdb-tools)
[![PyPi Downloads](https://img.shields.io/pypi/dm/pdb-tools.svg)](https://pypi.python.org/pypi/pdb-tools)
[![ci](https://github.com/haddocking/pdb-tools/actions/workflows/ci.yml/badge.svg)](https://github.com/haddocking/pdb-tools/actions/workflows/ci.yml)
[![DOI](https://zenodo.org/badge/27217350.svg)](https://doi.org/10.12688/f1000research.17456.1)

A swiss army knife for manipulating and editing PDB files.


## Looking for the _other_ pdb-tools?
The Harms lab maintains a set of tools also called `pdbtools`, which perform a
slightly different set of functions. You can find them [here](https://github.com/harmslab/pdbtools).


## About
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


## Installation Instructions
`pdb-tools` are available on PyPi and can be installed though `pip`. This is the
recommended way as it makes updating/uninstalling rather simple:
```bash
pip install pdb-tools
```

Because we use semantic versioning in the development of `pdb-tools`, every bugfix
or new feature results in a new version of the software that is automatically published
on PyPI. As such, there is no difference between the code on github and the latest version
you can install with `pip`. To update your installation to the latest version of the code
run:
```bash
pip install --upgrade pdb-tools
```

## What can I do with them?
The names of the tools should be self-explanatory. Their command-line interface
is also pretty consistent. Therefore, here is a couple of examples to get you
started:

* Downloading a structure
   ```bash
   pdb_fetch 1brs > 1brs.pdb  # 6 chains
   pdb_fetch -biounit 1brs > 1brs.pdb  # 2 chains
   ```

* Renumbering a structure
   ```bash
   pdb_reres -1 1ctf.pdb > 1ctf_renumbered.pdb
   ```

* Selecting chain(s)
   ```bash
   pdb_selchain -A 1brs.pdb > 1brs_A.pdb
   pdb_selchain -A,D 1brs.pdb > 1brs_AD.pdb
   ```

* Deleting hydrogens
   ```bash
   pdb_delelem -H 1brs.pdb > 1brs_noH.pdb
   ```

* Selecting backbone atoms
   ```bash
   pdb_selatom -CA,C,N,O 1brs.pdb > 1brs_bb.pdb
   ```

* Selecting chains, removing HETATM, and producing a valid PDB file
  ```bash
  pdb_selchain -A,D 1brs.pdb | pdb_delhetatm | pdb_tidy > 1brs_AD_noHET.pdb
  ```

*Note: On Windows the tools will have the `.exe` extension.*


## What _can't_ I do with them?
Operations that involve coordinates or numerical calculations are usually not in
the scope of `pdb-tools`. Use a proper library for that, it will be much faster
and scalable. Also, although we provide mmCIF<->PDB converters, we do not support
large mmCIF files with more than 99999 atoms, or 9999 residues in a single chain.
Our tools will complain if you try using them on such a molecule. 


## Citation
We finally decided to write up a small publication describing the tools. If you
used them in a project that is going to be published, please cite us:

```
Rodrigues JPGLM, Teixeira JMC, Trellet M and Bonvin AMJJ.
pdb-tools: a swiss army knife for molecular structures. 
F1000Research 2018, 7:1961 (https://doi.org/10.12688/f1000research.17456.1) 
```

If you use a reference manager that supports BibTex, use this record:
```
@Article{ 10.12688/f1000research.17456.1,
AUTHOR = { Rodrigues, JPGLM and Teixeira, JMC and Trellet, M and Bonvin, AMJJ},
TITLE = {pdb-tools: a swiss army knife for molecular structures [version 1; peer review: 2 approved]
},
JOURNAL = {F1000Research},
VOLUME = {7},
YEAR = {2018},
NUMBER = {1961},
DOI = {10.12688/f1000research.17456.1}
}
```

## Requirements
`pdb-tools` should run on Python 2.7+ and Python 3.x. We test on Python 2.7, 3.6,
and 3.7. There are no dependencies.


## Installing from Source
Download the zip archive or clone the repository with git. We recommend the `git`
approach since it makes updating the tools extremely simple.

```bash
# To download
git clone https://github.com/haddocking/pdb-tools
cd pdb-tools

# To update
git pull origin master

# To install
python setup.py install
```

## Contributing
If you want to contribute to the development of `pdb-tools`, provide a bug fix,
or a new tools, read our `CONTRIBUTING` instructions [here](https://github.com/haddocking/pdb-tools/blob/master/CONTRIBUTING.md).

## License
`pdb-tools` are open-source and licensed under the Apache License, version 2.0.
For details, see the LICENSE file.
