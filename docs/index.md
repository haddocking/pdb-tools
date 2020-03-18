---
layout: default
---

A swiss army knife for manipulating and editing PDB files.


## Installation Instructions
`pdb-tools` are available on PyPi and can be installed though `pip`. This is the
recommended way as it makes updating/uninstalling rather simple:
```bash
pip install pdb-tools
```

If you want to install the latest development version, which might give you new
features but also some bugs, see [here](#Installing-from-Source).


## What can I do with them?
The purpose of each tool should be obvious from its name. In any case, [here](#list-of-tools)
is a list of all the tools in the suite and their function. All tools share the
same command-line interface. Here is a couple of examples to get you started:

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


## About
Manipulating PDB files is often painful. Extracting a particular chain or set of
residues, renumbering residues, splitting or merging models and chains, or just
ensuring the file is conforming to the PDB specifications are examples of tasks
that can be done using any decent parsing library or graphical interface. These,
however, almost always require 1) scripting knowledge, 2) time, and 3) installing
one or more programs.

`pdb-tools` were designed to be a swiss army knife for the PDB format. The
philosophy of the scripts is simple: one script, one task. If you want to do two
things, pipe the scripts together. Requests for new scripts will be taken into
consideration - use the Issues button or write them yourself and create a Pull
Request.


## Looking for the _other_ pdb-tools?
The Harms lab maintains a set of tools also called `pdbtools`, which perform a
slightly different set of functions. You can find them [here](https://github.com/harmslab/pdbtools).


## Citation
We finally decided to write up a small publication describing the tools. If you
used them in a project that is going to be published, please cite us:

```
Rodrigues, J. P. G. L. M., Teixeira, J. M. C., Trellet, M. & Bonvin, A. M. J. J.
pdb-tools: a swiss army knife for molecular structures. bioRxiv (2018). 
doi:10.1101/483305
```

If you use a reference manager that supports BibTex, use this record:
```
@article {Rodrigues483305,
  author = {Rodrigues, Jo{\~a}o P.G.L.M. and Teixeira, Jo{\~a}o M.C. and Trellet, Mika{\"e}l and Bonvin, Alexandre M.J.J.},
  title = {pdb-tools: a swiss army knife for molecular structures},
  elocation-id = {483305},
  year = {2018},
  doi = {10.1101/483305},
  publisher = {Cold Spring Harbor Laboratory},
  abstract = {The pdb-tools are a collection of Python scripts for working with molecular structure data in the PDB format. They allow users to edit, convert, and validate PDB files, from the command-line, in a simple but efficient manner. The pdb-tools are implemented in Python, without any external dependencies, and are freely available under the open-source Apache License at https://github.com/haddocking/pdb-tools/ and on PyPI (https://pypi.org/project/pdb-tools/).},
  URL = {https://www.biorxiv.org/content/early/2018/12/04/483305},
  eprint = {https://www.biorxiv.org/content/early/2018/12/04/483305.full.pdf},
  journal = {bioRxiv}
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

## List of Tools
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_b</b> | Modifies the temperature factor column of a PDB file (default 10.0).</summary>
<span style="font-family: monospace; white-space: pre;">
Usage:
    python pdb_b.py -&lt;bfactor&gt; &lt;pdb file&gt;

Example:
    python pdb_b.py -10.0 1CTF.pdb
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_chain</b> | Modifies the chain identifier column of a PDB file (default is an empty chain).</summary>
<span style="font-family: monospace; white-space: pre;">
Usage:
    python pdb_chain.py -&lt;chain id&gt; &lt;pdb file&gt;

Example:
    python pdb_chain.py -C 1CTF.pdb
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_chainxseg</b> | Swaps the segment identifier for the chain identifier.</summary>
<span style="font-family: monospace; white-space: pre;">
Usage:
    python pdb_chainxseg.py &lt;pdb file&gt;

Example:
    python pdb_chainxseg.py 1CTF.pdb
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_chkensemble</b> | Checks all models in a multi-model PDB file have the same composition.</summary>
<span style="font-family: monospace; white-space: pre;">
Composition is defined as same atoms/residues/chains.

Usage:
    python pdb_chkensemble.py &lt;pdb file&gt;

Example:
    python pdb_chkensemble.py 1CTF.pdb
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_delchain</b> | Deletes all atoms matching specific chains in the PDB file.</summary>
<span style="font-family: monospace; white-space: pre;">
Usage:
    python pdb_delchain.py -&lt;option&gt; &lt;pdb file&gt;

Example:
    python pdb_delchain.py -A 1CTF.pdb  # removes chain A from PDB file
    python pdb_delchain.py -A,B 1CTF.pdb  # removes chains A and B from PDB file
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_delelem</b> | Deletes all atoms matching the given element in the PDB file. </summary>
<span style="font-family: monospace; white-space: pre;">
Elements are read from the element column.

Usage:
    python pdb_delelem.py -&lt;option&gt; &lt;pdb file&gt;

Example:
    python pdb_delelem.py -H 1CTF.pdb  # deletes all protons
    python pdb_delelem.py -N 1CTF.pdb  # deletes all nitrogens
    python pdb_delelem.py -H,N 1CTF.pdb  # deletes all protons and nitrogens
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_delhetatm</b> | Removes all HETATM records in the PDB file.</summary>
<span style="font-family: monospace; white-space: pre;">
Usage:
    python pdb_delhetatm.py &lt;pdb file&gt;

Example:
    python pdb_delhetatm.py 1CTF.pdb
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_delinsertion</b> | Deletes insertion codes in a PDB file.</summary>
<span style="font-family: monospace; white-space: pre;">
Deleting an insertion code shifts the residue numbering of downstream
residues. Allows for picking specific residues to delete insertion codes for.

Usage:
    python pdb_delinsertion.py [-&lt;option&gt;] &lt;pdb file&gt;

Example:
    python pdb_delinsertion.py 1CTF.pdb  # delete ALL insertion codes
    python pdb_delinsertion.py -A9,B12 1CTF.pdb  # deletes ins. codes for res
                                                 # 9 of chain A and 12 of chain B.
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_delres</b> | Deletes a range of residues from a PDB file. </summary>
<span style="font-family: monospace; white-space: pre;">
The range option has three components: start, end, and step. Start and end
are optional and if ommitted the range will start at the first residue or
end at the last, respectively. The step option can only be used if both start
and end are provided. Note that the start and end values of the range are
purely numerical, while the range actually refers to every N-th residue,
regardless of their sequence number.

Usage:
    python pdb_delres.py -[resid]:[resid]:[step] &lt;pdb file&gt;

Example:
    python pdb_delres.py -1:10 1CTF.pdb # Deletes residues 1 to 10
    python pdb_delres.py -1: 1CTF.pdb # Deletes residues 1 to END
    python pdb_delres.py -:5 1CTF.pdb # Deletes residues from START to 5.
    python pdb_delres.py -::5 1CTF.pdb # Deletes every 5th residue
    python pdb_delres.py -1:10:5 1CTF.pdb # Deletes every 5th residue from 1 to 10
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_delresname</b> | Removes all residues matching the given name in the PDB file. </summary>
<span style="font-family: monospace; white-space: pre;">
Residues names are matched *without* taking into consideration spaces.

Usage:
    python pdb_delresname.py -&lt;option&gt; &lt;pdb file&gt;

Example:
    python pdb_delresname.py -ALA 1CTF.pdb  # removes only Alanines
    python pdb_delresname.py -ASP,GLU 1CTF.pdb  # removes (-) charged residues
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_element</b> | Assigns the elements in the PDB file from atom names.</summary>
<span style="font-family: monospace; white-space: pre;">
Usage:
    python pdb_element.py &lt;pdb file&gt;

Example:
    python pdb_element.py 1CTF.pdb
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_fetch</b> | Downloads a structure in PDB format from the RCSB website. </summary>
<span style="font-family: monospace; white-space: pre;">
Allows downloading the (first) biological structure if selected.

Usage:
    python pdb_fetch.py [-biounit] &lt;pdb code&gt;

Example:
    python pdb_fetch.py 1brs  # downloads unit cell, all 6 chains
    python pdb_fetch.py -biounit 1brs  # downloads biounit, 2 chains
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_fromcif</b> | Rudimentarily converts a mmCIF file to the PDB format. </summary>
<span style="font-family: monospace; white-space: pre;">
Will not convert if the file does not 'fit' in PDB format, e.g. too many
chains, residues, or atoms. Will convert only the coordinate section.

Usage:
    python pdb_fromcif.py &lt;pdb file&gt;

Example:
    python pdb_fromcif.py 1CTF.pdb
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_gap</b> | Finds gaps between consecutive protein residues in the PDB.</summary>
<span style="font-family: monospace; white-space: pre;">
Detects gaps both by a distance criterion or discontinuous residue numbering.
Only applies to protein residues.

Usage:
    python pdb_gap.py &lt;pdb file&gt;

Example:
    python pdb_gap.py 1CTF.pdb
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_head</b> | Returns the first N coordinate (ATOM/HETATM) lines of the file.</summary>
<span style="font-family: monospace; white-space: pre;">
Usage:
    python pdb_head.py -&lt;num&gt; &lt;pdb file&gt;

Example:
    python pdb_head.py -100 1CTF.pdb  # first 100 ATOM/HETATM lines of the file
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_intersect</b> | Returns a new PDB file only with atoms in common to all input PDB files.</summary>
<span style="font-family: monospace; white-space: pre;">
Atoms are judged equal is their name, altloc, res. name, res. num, insertion
code and chain fields are the same. Coordinates are taken from the first input
file. Keeps matching TER/ANISOU records.

Usage:
    python pdb_intersect.py &lt;pdb file&gt; &lt;pdb file&gt;

Example:
    python pdb_intersect.py 1XYZ.pdb 1ABC.pdb
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_keepcoord</b> | Removes all non-coordinate records from the file.</summary>
<span style="font-family: monospace; white-space: pre;">
Keeps only MODEL, ENDMDL, END, ATOM, HETATM, and CONECT.

Usage:
    python pdb_keepcoord.py &lt;pdb file&gt;

Example:
    python pdb_keepcoord.py 1CTF.pdb
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_merge</b> | Merges several PDB files into one. </summary>
<span style="font-family: monospace; white-space: pre;">
The contents are not sorted and no lines are deleted (e.g. END, TER
statements) so we recommend piping the results through `pdb_tidy.py`.

Usage:
    python pdb_merge.py &lt;pdb file&gt; &lt;pdb file&gt;

Example:
    python pdb_merge.py 1ABC.pdb 1XYZ.pdb
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_mkensemble</b> | Merges several PDB files into one multi-model (ensemble) file.</summary>
<span style="font-family: monospace; white-space: pre;">
Strips all HEADER information and adds REMARK statements with the provenance
of each conformer.

Usage:
    python pdb_mkensemble.py &lt;pdb file&gt; &lt;pdb file&gt;

Example:
    python pdb_mkensemble.py 1ABC.pdb 1XYZ.pdb
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_occ</b> | Modifies the occupancy column of a PDB file (default 1.0).</summary>
<span style="font-family: monospace; white-space: pre;">
Usage:
    python pdb_occ.py -&lt;occupancy&gt; &lt;pdb file&gt;

Example:
    python pdb_occ.py -1.0 1CTF.pdb
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_reatom</b> | Renumbers atom serials in the PDB file starting from a given value (default 1).</summary>
<span style="font-family: monospace; white-space: pre;">
Usage:
    python pdb_reatom.py -&lt;number&gt; &lt;pdb file&gt;

Example:
    python pdb_reatom.py -10 1CTF.pdb  # renumbers from 10
    python pdb_reatom.py --1 1CTF.pdb  # renumbers from -1
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_reres</b> | Renumbers the residues of the PDB file starting from a given number (default 1).</summary>
<span style="font-family: monospace; white-space: pre;">
Usage:
    python pdb_reres.py -&lt;number&gt; &lt;pdb file&gt;

Example:
    python pdb_reres.py -10 1CTF.pdb  # renumbers from 10
    python pdb_reres.py --1 1CTF.pdb  # renumbers from -1
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_rplchain</b> | Performs in-place replacement of a chain identifier by another.</summary>
<span style="font-family: monospace; white-space: pre;">
Usage:
    python pdb_rplchain.py -&lt;from&gt;:&lt;to&gt; &lt;pdb file&gt;

Example:
    python pdb_rplchain.py -A:B 1CTF.pdb # Replaces chain A for chain B
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_rplresname</b> | Performs in-place replacement of a residue name by another.</summary>
<span style="font-family: monospace; white-space: pre;">
Affects all residues with that name.

Usage:
    python pdb_rplresname.py -&lt;from&gt;:&lt;to&gt; &lt;pdb file&gt;

Example:
    python pdb_rplresname.py -HIP:HIS 1CTF.pdb  # changes all HIP residues to HIS
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_seg</b> | Modifies the segment identifier column of a PDB file (default is an empty segment).</summary>
<span style="font-family: monospace; white-space: pre;">
Usage:
    python pdb_seg.py -&lt;segment id&gt; &lt;pdb file&gt;

Example:
    python pdb_seg.py -C 1CTF.pdb
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_segxchain</b> | Swaps the chain identifier by the segment identifier.</summary>
<span style="font-family: monospace; white-space: pre;">
If the segment identifier is longer than one character, the script will
truncate it. Does not ensure unique chain IDs.

Usage:
    python pdb_segxchain.py &lt;pdb file&gt;

Example:
    python pdb_segxchain.py 1CTF.pdb
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_selaltloc</b> | Selects altloc labels for the entire PDB file.</summary>
<span style="font-family: monospace; white-space: pre;">
By default, picks the label with the highest occupancy value for each atom, 
but the user can define a specific label. Removes all labels afterwards.

Usage:
    python pdb_selaltloc.py [-&lt;option&gt;] &lt;pdb file&gt;

Example:
    python pdb_selaltloc.py 1CTF.pdb  # picks locations with highest occupancy
    python pdb_selaltloc.py -A 1CTF.pdb  # picks alternate locations labelled 'A'
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_selatom</b> | Selects all atoms matching the given name in the PDB file.</summary>
<span style="font-family: monospace; white-space: pre;">
Atom names are matched *without* taking into consideration spaces, so ' CA '
(alpha carbon) and 'CA  ' (calcium) will both be kept if -CA is passed.

Usage:
    python pdb_selatom.py -&lt;option&gt; &lt;pdb file&gt;

Example:
    python pdb_selatom.py -CA 1CTF.pdb  # keeps only alpha-carbon atoms
    python pdb_selatom.py -CA,C,N,O 1CTF.pdb  # keeps only backbone atoms
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_selchain</b> | Extracts one or more chains from a PDB file.</summary>
<span style="font-family: monospace; white-space: pre;">
Usage:
    python pdb_selchain.py -&lt;chain id&gt; &lt;pdb file&gt;

Example:
    python pdb_selchain.py -C 1CTF.pdb  # selects chain C
    python pdb_selchain.py -A,C 1CTF.pdb  # selects chains A and C
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_selelem</b> | Selects all atoms that match the given element(s) in the PDB file.</summary>
<span style="font-family: monospace; white-space: pre;">
Elements are read from the element column.

Usage:
    python pdb_selelem.py -&lt;option&gt; &lt;pdb file&gt;

Example:
    python pdb_selelem.py -H 1CTF.pdb  # selects all protons
    python pdb_selelem.py -N 1CTF.pdb  # selects all nitrogens
    python pdb_selelem.py -H,N 1CTF.pdb  # selects all protons and nitrogens
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_selhetatm</b> | Selects all HETATM records in the PDB file.</summary>
<span style="font-family: monospace; white-space: pre;">
Usage:
    python pdb_selhetatm.py &lt;pdb file&gt;

Example:
    python pdb_selhetatm.py 1CTF.pdb
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_selres</b> | Selects residues by their index, piecewise or in a range. </summary>
<span style="font-family: monospace; white-space: pre;">
The range option has three components: start, end, and step. Start and end
are optional and if ommitted the range will start at the first residue or
end at the last, respectively.

Usage:
    python pdb_selres.py -[resid]:[resid]:[step] &lt;pdb file&gt;

Example:
    python pdb_selres.py -1,2,4,6 1CTF.pdb # Extracts residues 1, 2, 4 and 6
    python pdb_selres.py -1:10 1CTF.pdb # Extracts residues 1 to 10
    python pdb_selres.py -1:10,20:30 1CTF.pdb # Extracts residues 1 to 10 and 20 to 30
    python pdb_selres.py -1: 1CTF.pdb # Extracts residues 1 to END
    python pdb_selres.py -:5 1CTF.pdb # Extracts residues from START to 5.
    python pdb_selres.py -::5 1CTF.pdb # Extracts every 5th residue
    python pdb_selres.py -1:10:5 1CTF.pdb # Extracts every 5th residue from 1 to 10
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_selresname</b> | Selects all residues matching the given name in the PDB file.</summary>
<span style="font-family: monospace; white-space: pre;">
Residues names are matched *without* taking into consideration spaces.

Usage:
    python pdb_selresname.py -&lt;option&gt; &lt;pdb file&gt;

Example:
    python pdb_selresname.py -ALA 1CTF.pdb  # keeps only Alanines
    python pdb_selresname.py -ASP,GLU 1CTF.pdb  # keeps (-) charged residues
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_selseg</b> | Selects all atoms matching the given segment identifier.</summary>
<span style="font-family: monospace; white-space: pre;">
Usage:
    python pdb_selseg.py -&lt;segment id&gt; &lt;pdb file&gt;

Example:
    python pdb_selseg.py -C 1CTF.pdb  # selects segment C
    python pdb_selseg.py -C,D 1CTF.pdb  # selects segments C and D
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_shiftres</b> | Shifts the residue numbers in the PDB file by a constant value.</summary>
<span style="font-family: monospace; white-space: pre;">
Usage:
    python pdb_shiftres.py -&lt;number&gt; &lt;pdb file&gt;

Example:
    python pdb_shiftres.py -10 1CTF.pdb  # adds 10 to the original numbering
    python pdb_shiftres.py --5 1CTF.pdb  # subtracts 5 from the original numbering
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_sort</b> | Sorts the ATOM/HETATM/ANISOU/CONECT records in a PDB file.</summary>
<span style="font-family: monospace; white-space: pre;">
Atoms are always sorted by their serial number, meaning the original ordering
of the atoms within each residue are not changed. Alternate locations are sorted
by default.

Residues are sorted according to their residue sequence number and then by their
insertion code (if any).

Chains are sorted by their chain identifier.

Finally, the file is sorted by all keys, and the records are placed in the
following order:
    - ATOM/ANISOU, intercalated if the latter exist
    - HETATM
    - CONECT, sorted by the serial number of the central (first) atom

MASTER, TER, END statements are removed. Headers (HEADER, REMARK, etc) are kept
and placed first. Does NOT support multi-model files. Use pdb_splitmodel, then
pdb_sort on each model, and then pdb_mkensemble.

Usage:
    python pdb_sort.py -&lt;option&gt; &lt;pdb file&gt;

Example:
    python pdb_sort.py 1CTF.pdb  # sorts by chain and residues
    python pdb_sort.py -C 1CTF.pdb  # sorts by chain (A, B, C ...) only
    python pdb_sort.py -R 1CTF.pdb  # sorts by residue number/icode only
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_splitchain</b> | Splits a PDB file into several, each containing one chain.</summary>
<span style="font-family: monospace; white-space: pre;">
Usage:
    python pdb_splitchain.py &lt;pdb file&gt;

Example:
    python pdb_splitchain.py 1CTF.pdb
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_splitmodel</b> | Splits a PDB file into several, each containing one MODEL.</summary>
<span style="font-family: monospace; white-space: pre;">
Usage:
    python pdb_splitmodel.py &lt;pdb file&gt;

Example:
    python pdb_splitmodel.py 1CTF.pdb
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_splitseg</b> | Splits a PDB file into several, each containing one segment.</summary>
<span style="font-family: monospace; white-space: pre;">
Usage:
    python pdb_splitseg.py &lt;pdb file&gt;

Example:
    python pdb_splitseg.py 1CTF.pdb
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_tidy</b> | Modifies the file to adhere (as much as possible) to the format specifications.</summary>
<span style="font-family: monospace; white-space: pre;">
Expects a sorted file - REMARK/ATOM/HETATM/END - so use pdb_sort in case you are
not sure.

This includes:
    - Adding TER statements after chain breaks/changes
    - Truncating/Padding all lines to 80 characters
    - Adds END statement at the end of the file

Will remove all original TER/END statements from the file.

Usage:
    python pdb_tidy.py &lt;pdb file&gt;

Example:
    python pdb_tidy.py 1CTF.pdb
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_tocif</b> | Rudimentarily converts the PDB file to mmCIF format. </summary>
<span style="font-family: monospace; white-space: pre;">
Will convert only the coordinate section.

Usage:
    python pdb_tocif.py &lt;pdb file&gt;

Example:
    python pdb_tocif.py 1CTF.pdb
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_tofasta</b> | Extracts the residue sequence in a PDB file to FASTA format. </summary>
<span style="font-family: monospace; white-space: pre;">
Canonical amino acids and nucleotides are represented by their
one-letter code while all others are represented by 'X'.

The -multi option splits the different chains into different records in the
FASTA file.

Usage:
    python pdb_tofasta.py [-multi] &lt;pdb file&gt;

Example:
    python pdb_tofasta.py 1CTF.pdb
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_validate</b> | Validates the PDB file ATOM/HETATM lines according to the format specifications.</summary>
<span style="font-family: monospace; white-space: pre;">
Does not catch all the errors though... people are creative!

Usage:
    python pdb_validate.py &lt;pdb file&gt;

Example:
    python pdb_validate.py 1CTF.pdb
</span>
</details>
</div>
<div style="margin-bottom: 1em;">
<details>
<summary><b>pdb_wc</b> | Summarizes the contents of a PDB file, like the wc command in UNIX.</summary>
<span style="font-family: monospace; white-space: pre;">
Several options are available to produce only partial summaries:
    [m] - no. of models.
    [c] - no. of chains (plus per-model if multi-model file).
    [r] - no. of residues (plus per-model if multi-model file).
    [a] - no. of atoms (plus per-model if multi-model file).
    [h] - no. of HETATM (plus per-model if multi-model file).
    [o] - no. of disordered atoms (altloc) (plus per-model if multi-model file).
    [i] - no. of insertion codes (plus per-model if multi-model file).
    [g] - presence/absence of gaps (discontinuous residue numbering).

Usage:
    python pdb_wc.py [-&lt;option&gt;] &lt;pdb file&gt;

Example:
    python pdb_wc.py 1CTF.pdb
</span>
</details>
</div>