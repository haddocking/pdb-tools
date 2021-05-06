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
"""
Main client to organize pdb-tools as subcommands.

Usage:
    pdbtools <TOOL> <OPTION>

Example:
    pdbtools fetch 12as
    pdbtools fetch 12as | pdbtools selchain -B > 12AS_B.pdb
"""
import importlib
import os
import sys
from pathlib import Path


def exit_with_error(options):
    """Exit run with error."""
    list_scripts = "* " + "\n* ".join(options) + "\n"
    fmt = (
        "# Welcome to pdb-tools\n"
        "# List of available scripts: \n {}"
        "List of avaiable tools above."
        )
    print(fmt.format(list_scripts))
    sys.exit()


def main():
    """Client for subcommands."""
    pdbtools_folder = Path(__file__).parent
    pdbtools_scripts = sorted(pdbtools_folder.glob('pdb_*.py'))
    options = [f.stem.split('_')[1] for f in pdbtools_scripts]

    if len(sys.argv) == 1:
        exit_with_error(options)

    execs = {
        name: importlib.import_module('pdbtools.' + os.fspath(module.stem)).main
        for name, module in zip(options, pdbtools_scripts)
        }

    sys.argv.pop(0)
    subcommand = sys.argv[0]
    try:
        execs[subcommand]()
    except KeyError:
        exit_with_error(options)
    return


if __name__ == '__main__':
    main()
