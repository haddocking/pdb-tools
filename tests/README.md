Writing unit tests for `pdb-tools`
================================================
If you want to write a new `pdb-tools` script, make sure to provide a test case
that verifies the script is running as it should. 


How to create a unit test
-------------------------

1. Create one file in `tests\` starting with `test_` and named after the script,
e.g. `test_pdb_b.py`.

2. If necessary, add an input file to `data\`.

3. Place the expected result, as the tool would write it, in `output` and name
it after the tool and ending with `.out`, e.g. `pdb_b.out`

4. Write the unit test in `test_pdb_b.py` and compare the output with `pdb_b.out`.