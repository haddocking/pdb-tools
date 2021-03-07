---
layout: default
---

* Removing hydrogens, renaming `HIP` to `HIS`, and renumbering atoms, for all PDBs from a folder to a new folder:

  ```bash
  mkdir folder_new
  for i in folder/*pdb; do pdb_delelem -H $i | pdb_rplresname -HIP:HIS | pdb_reatom -1 | pdb_tidy > folder_new/$(basename $i); done
  ```
