# Packaging pdb-tools
This guide describes (roughly) how to package `pdb-tools` into something `pip`
can handle.

## Versioning
`pdb-tools` uses semantic versioning: MAJOR.MINOR.PATCH (e.g. 2.0.0). It works
more or less like this:

* For every new release fixing bugs, increment the PATCH counter (e.g. 2.0.1).
* For every release adding minor features to tools or new tools that do not
impact any of the existing ones, increment MINOR (e.g. 2.1.0).
* For major changes that will most likely impact the usage of existing tools,
increment MAJOR (e.g. 3.0.0).

## Packaging
This is a rough guide to building a distributable package:

### (1) Ensure all tests pass:
```bash
python setup.py test
```

2. Ensure there are no warnings from flake8:
```bash
flake8 --ignore=E501,E731
```

3. Build the distributable package:
```bash
python setup.py sdist bdist_wheel

# Upload to PyPI: testing repo for now.
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```
