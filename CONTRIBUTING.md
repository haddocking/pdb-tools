# Contributing to pdb-tools

First off, thank you for taking the time to contribute! The tone of the following
'guidelines' might seem a bit harsh (a lot of *do nots*) but it will make 
everyone's life easier. Make sure you read through this at least once before
issuing a pull request or opening an issue.

## What should I know before getting started?
The crux of any tool of `pdb-tools` is simplicity. Simplicity both for the
end-user but also for developers. You will find that the tools often repeat a
lot of code, for example the `check_input` functions. While this might look ugly
from a development point of view, it makes scripts simpler (fancy options will
very quickly turn ugly), faster (no imports) and more understandable for old and
new developers. This is also why we do not make use of `argparse`.

A corolary of this simplicity is that every tool should do **one and one job
only**. The only exception to this is `pdb_tidy` and it will very likely remain
so. Even then, its job is to 'produce a valid PDB', despite doing multiple tasks
under the hood. The tools are meant to be chained together, so if you want to
have two tasks accomplished, write two tools and have them talk.

Finally. **Dependencies are strictly not allowed**. Take this as an exercise to
work on your Python Standard Library skills.

## How do I write an issue?
If you found a problem with one of the tools, if it does not behave as expected,
if you think it should do something different or something more, or if you think
that there should be a tool do to something new, please do open an issue.

If a tool is not working, let us know exactly what you did and what the outcome
was. Whatever you tell us that helps us reproduce your workflow will make our
job much easier to answer your question and provide a fix if necessary.

&nbsp;&nbsp; **Bad issue reporter**

    pdb_reatom.py does not work. Please fix.  # believe it or not people do write this.

&nbsp;&nbsp; **Good issue reporter**

    I tried using pdb_reatom.py on a PDB file and it did not renumber nitrogen
    atoms. Here is an example:
    
    $ cat 1abc.pdb
    ATOM      9  N   ASN A   1      22.066  40.557   1.420  1.00  1.00              
    ATOM      2  N   ASN A   2      43.123  76.234   0.123  1.00  1.00              
    END
    $ pdb_reatom 1abc.pdb
    ATOM      9  N   ASN A   1      22.066  40.557   1.420  1.00  1.00              
    ATOM      2  N   ASN A   2      43.123  76.234   0.123  1.00  1.00              
    END
    
    I was expecting the two atoms to be consecutively renumbered from 1. I am 
    using pdb-tools version 2.0.0:
    
    $ pip show pdb-tools
    Name: pdb-tools
    Version: 2.0.0
    Location: /path/to/virtualenv/lib/python3.7/site-packages

## How do I contribute code?
We welcome and will gladly review any pull request. If you have never used git
or GitHub before, have a look at the [guides](https://guides.github.com/) page.

To contribute to `pdb-tools`, use the *Fork* button to create your own copy of
the `pdb-tools` repository. Then, download `git` on your laptop/desktop computer
and proceed like the snippet below, where we pretend to add a new tool:

```bash
# Clone your own fork of pdb-tools
git clone https://github.com/yourusername/pdb-tools.git
cd pdb-tools

# Add our repository as 'upstream' to make sure you are using the latest
# version of the code.
git remote add upstream https://github.com/haddocking/pdb-tools.git

# Pull our master to update your local version
# If there are changes, you should push them to the 'master' of your fork.
# IMPORTANT, start the commit message title of the merging step (`git pull`)
# with the tag `[SKIP]` to avoid trigering our GitHub actions in your own fork.
git pull upstream master
git push origin master  # Update your fork if necessary

# Create a feature branch to start working on your new tool.
# Name the new branch clearly and concisely after the change you are proposing
#
# We use feature branches to avoid conflicts in the master branch. Updating
# should always be smooth and you can deal with merge conflicts in your branches
git checkout -b pdb_newtool

# Work on your new tool!
# Include hours of work here and make sure to read the conventions below.
# Also, try to add a test case too under tests/
# We can help you fleshing it out if you need it.
...

# If you are making changes to an existing tool, run the test suite before
# committing your changes.
python setup.py test

# When you have committed all your changes, run flake8 to make sure there are
# no style issues.
pip install flake8  # Optional obviously
flake8 --ignore E501,E731 --statistics bin/

# When there are no issues left, push to your fork on github
git push origin pdb_newtool

# And then, online, create a pull request.
# That is it.
```

## Conventions
In an effort to try and make all tools look the same, stick to these conventions
when writing a new one or modifying an existing one:

### Coding conventions
Every pull request will be checked for style using Flake8. We ignore line length
warnings and the use of lambdas. Do not abuse the first one though. We always try
to stick to 80 characters, unless it's stupid to do so.

* Do not use camelCase. Stick to snake_case.
* Write docstrings and comment your code, specially if it is not obvious!
* Name your variables properly, we don't charge you for a few extra lines.

### Tool design conventions

* Every tool should have the same structure: `check_input`, `do_task`, `main`.
Do **not** deviate from this, unless you absolutely need to.
* User interfaces must follow the `pdb_tool [-option] <file>` paradigm. Do not
try and make it `pdb_tool -opt1 -opt2 -opt3`. See `pdb_rplchain` and `pdb_wc`
for good examples of how to handle multiple options.
* Avoid reading the entire file in memory unless you have to. This makes it nice
for people processing very large files.
* Following the previous item, make use of generators (`yield`) to output the
results of your tool.

## Merging Pull Requests
If you are tasked with merging a pull request yourself, you should know that there
is an automated job running every time a push is made to the master branch. This job
will trigger a version bump and automatically publish the new package to PyPi. By default,
only the patch (x.x.Y) number is incremented. If you want to trigger a minor version (x.Y.x)
update, start your commit with `[FEATURE]`. Note that since we use merge commits, this means
you have to edit the title of the merge commit. It is your responsibility to handle this as
a package maintainer! Finally, if your last commit message starts with `[SKIP]`, the automated
job does not run, so use this flag if your commits are for documentation, README, etc.
