#!/usr/bin/env python

"""
Scrapes tool headers for documentation.
"""

import importlib
from pathlib import Path

with open('index.md', 'w') as handle:

    with open('index.md.template') as template:
        print(template.read(), file=handle)

    import pdbtools
    modfile = Path(pdbtools.__file__)
    for f in sorted(list(modfile.parent.iterdir())):
        # ignore __init__.py and others.
        if f.stem.startswith('_') or f.suffix != '.py':
            continue

        # Dynamically import tool to get __doc__
        name = f.stem
        try:
            tool = importlib.import_module(f'pdbtools.{name}')
        except ModuleNotFoundError:
            print(f'Could not import module: {name}')
            continue

        # Parse documentation from docstrings
        # Preserve white-space as best as possible.
        # First non-empty line is always short description.
        # Last lines are always licensing disclaimer
        summary = None
        long_description = []

        doctext = tool.__doc__.replace('<', '&lt;').replace('>', '&gt;')
        for line in doctext.split('\n'):
            if summary is None and not line.strip():
                continue
            if line.startswith('This program is part of the'):
                break
            elif summary is None:
                summary = line
            else:
                long_description.append(line)

        long_description = '\n'.join(long_description)
        print('<div style="margin-bottom: 1em;">', file=handle)
        print('<details>', file=handle)
        print(f"<summary><b>{name}</b><p>{summary}</p></summary>", file=handle)
        print(
            f'<span style="font-family: monospace; white-space: pre;">{long_description}</span>',
            file=handle
        )
        print('</details>', file=handle)
        print('</div>', file=handle)
