#!/usr/bin/env python
# coding=utf-8

# To support python 2.5+
from __future__ import with_statement

"""
PDBParser.py

Module to validate PDB files.
"""

__author__    = "Alexandre Bonvin"
__version__   = "2.3"
__copyright__ = "Copyright 2014, Alexandre Bonvin"
__email__     = "a.m.j.j.bonvin@uu.nl"
__credits__   = ['Alexandre Bonvin', 'João Rodrigues', 'Mikael Trellet']

import os
import logging
import re
import argparse

from Haddock.DataIO.GenericParser import GenericFileParser

# Regular expression to parse PDB ATOM/HETATM lines
# Spec: http://www.wwpdb.org/documentation/file-format-content/format33/sect9.html#ATOM
re_ATOM = re.compile("""
                     (ATOM[\s]{2}|HETATM)
                     (?P<serial>[\d\s]{4}[0-9])
                     [\s]{1}
                     (?P<atname>[\w\s\']{4})
                     (?P<altloc>[\w\s]{1})
                     (?P<resn>[\s\w]{3})
                     [\s]{1}
                     (?P<chain>[\w\s]{1})
                     (?P<resi>[\s\d]{3}[0-9])
                     (?P<icode>[\w\s]{1})
                     [\s]{3}
                     (?P<x>[\s\d\-]{4}\.[0-9]{3})
                     (?P<y>[\s\d\-]{4}\.[0-9]{3})
                     (?P<z>[\s\d\-]{4}\.[0-9]{3})
                     (?P<o>[\s\d\.\-]{3}\.[0-9]{2})
                     (?P<b>[\s\d\.\-]{3}\.[0-9]{2})
                     [\s]{6}
                     (?P<segid>[\w\s]{1})
                     [\s]{3}
                     """, re.VERBOSE)
# Taken from
# http://www.wwpdb.org/documentation/format33/v3.3.html
valid_records = set(( 'ANISOU', 'ATOM', 'AUTHOR',
                      'CAVEAT', 'CISPEP', 'COMPND',
                      'CONECT', 'CRYST', 'DBREF',
                      'ENDMDL', 'EXPDTA', 'FORMUL',
                      'HEADER', 'HELIX', 'HET',
                      'HETATM', 'HETNAM', 'HETSYN',
                      'JRNL', 'KEYWDS', 'LINK',
                      'MDLTYP', 'MODEL', 'MODRES',
                      'MTRIX', 'NUMMDL', 'OBSLTE',
                      'ORIGX', 'REVDAT', 'SCALE',
                      'SEQADV', 'SEQRES', 'SHEET',
                      'SOURCE', 'SPLIT', 'SPRSDE',
                      'SSBOND', 'TER', 'TITLE',
                      'MASTER', 'END','REMARK',
                      'SEQALI', 'SPDBVT', 'SPDBVV',
                      'SPDBVf', 'SPDBVR', 'SPDBVb'))

aa = ["ACE", "CTN", "ALA", "CFE", "CYS", "CYM", "CYF", "CSP", "ASP","GLU","PHE","GLY","HIS","NEP","ILE","LYS","ALY", "MLY", "MLZ", "M3L", "LEU","MET","ASN","PRO","GLN","ARG","SER","SEP", "THR","THP", "TOP", "VAL","TRP","TYR","PTR","TYP","TYS", "TIP", "HYP", "HEB", "HEC", "WAT", "PNS"]
bases = ["ADE", "CYT", "DOC", "GUA", "DGP", "URI", "THY", "THJ", " DG", " DC", " DT", " DA", "DG ", "DC ", "DT ", "DA ","  A", "  G", "  C", "  T", "  U"]
aa += bases
weirdbases = [" A ", " G ", " C ", " T ", " U "] #unusual one-letter bases
aa += weirdbases
knownligands = ["DFO","ADY","ACD","ACT","ACN","BDY","BEN","CHE","DME","ETA","EOL","BUT","THS","AMN","PHN","URE","IMI","MER"]
aa += knownligands

                     
class PDBParsingError(Exception):
    """
    Custom exception class to provide better error messages.
    
    Besides the standard error message, the class appends
    the full offending line together with an example valid line.
    """
    def __init__(self, user_message, line, final=False):
        # Add information to our message

        # Valid example ATOM line
        valid_ATOM = "ATOM     32  N  AARG A  -3      11.281  86.699  94.383  0.50 35.88           N  "
        full_message = '{0}\n'.format(user_message)
        # To avoid repetitive messages, only last PDBParsing exception triggers the wollowing line
        if final:
            full_message+= '{0}  <-- (Offending Line)\n{1}(Example Valid Line)'.format(line.strip(), valid_ATOM)
            full_message+= '\n\nSee http://www.wwpdb.org/documentation/file-format-content/format33/sect9.html#ATOM for more details'
        
        # Call base class constructor
        Exception.__init__(self, full_message)

class PDBParser(object):
    """
    Class to parse a PDB file coordinates
    and ATOM/HETATM identity.
    """
    
    def __init__(self, fpath=None, chain_id_check = False):
        #GenericFileParser.__init__(self, path)
        fpath = os.path.abspath(os.path.expanduser(fpath))
        self.fpath = self._check_path(fpath)
        
        # Holds tuple for each atom.
        self.atoms = []
        # Holds key (model_id, chain, resi, icode) for each residue
        # and value (aname, position in self.atoms array)
        self.residues = {}
        self._parse(fpath, chain_id_check)

    def _check_path(self, path):
        """ Verifies the existence and permissions of a file     
            Args:
                fpath (str): path to a file
        
            Returns:
                if existing and accessible, absolute path for file
        
            Raises:
                IOError: file cannot be found or read.
        """
    
        full_path = os.path.abspath(path)
        if not os.path.exists(full_path):
            raise IOError('File does not exist: {0}'.format(full_path))
        elif not os.access(full_path, os.R_OK):
            raise IOError('File cannot be read (do you have permission?): {0}',format(full_path))
    
        return full_path
        
    def _parse_atom_line(self, line, chain_id_check):
        """Extracts information from ATOM/HETATM line"""

        atom_data = re_ATOM.match(line)
        if not atom_data:
            raise PDBParsingError('ATOM/HETATM line does not meet the expected format', line)
        
        (record, serial, atname,
         altloc, resn, chain, resi,
         icode, x, y, z, o, b, segid) = atom_data.groups()

        # Check if it is a known residue
        if record.strip() == "ATOM" and resn not in aa:
        	raise PDBParsingError('Residue name ("{}") is unknown, please check the syntax or replace ATOM by HETATM'.format(resn), line)

        # This is probably redundant because of the validation done in the regex matching..
        try:
            resi = int(resi)
        except ValueError:
            raise PDBParsingError('Residue number must be an integer (is {0!r})'.format(resi), line)
        try:
            x, y, z, o, b = map(float, [x,y,z,o,b])
        except ValueError as error:
            raise PDBParsingError('X,Y,Z coordinates, occupancy, and temperature (b) factors must be decimal numbers.', line)   
        if chain_id_check and chain == " ":
            raise PDBParsingError('No chain_id found', line)
        if chain != " " and segid != " " and (chain != segid):
        	raise PDBParsingError('seg_id different from chain_id', line)
        
        # Could use a named tuple here?
        atom = (record, atname, altloc, resn, chain, resi, icode, x, y, z, o, b) 
        return atom    
        
    def _parse_model_line(self, line):
        """Extracts the model number from the line"""    
        
        try:
            model_number = int(line[11:14])
        except ValueError:
            raise PDBParsingError('Model number must be an integer (is {0!r})'.format(line[11:14]), line)
        else:
            return model_number
            
    def _parse(self, handle, chain_id_check):
        """Actual parsing function"""
        pdbf = self.fpath

        # Counter / other variables
        at_counter = 0
        model_open = False
        model_id = None
        # Warning triggered if an ATOM/HETATM line has less than 80 columns
        len_warning = False
        # Parser loop
        with open(pdbf, 'r') as pdb_handle:
            for iline, line in enumerate(pdb_handle):
                record = line[0:6].strip()
                if record in valid_records:
                    if line.startswith('MODEL'):
                        if model_open:
                            raise PDBParsingError('It seems an ENDMDL statement is missing at line {0}'.format(iline), line, True)
                        model_open = True
                        model_id = self._parse_model_line(line)

                    elif line.startswith('ENDMDL'):
                        model_open = False

                    elif line.startswith(('ATOM', 'HETATM')):
                    	if not len_warning and len(line) < 81:
                    		len_warning = True
                        try:
                            atom = self._parse_atom_line(line, chain_id_check)
                        except PDBParsingError as error:
                            raise PDBParsingError('Could not parse the PDB file at line {0}\n{1}'.format(iline + 1, error.message), line, True)
                        else:
                            # Register atoms
                            atom_uid = (model_id, ) + atom
                            self.atoms.append(atom_uid)
                            
                            # Register residue
                            _, atname, _, _, chain, \
                            resi, icode, _, _, _, _, _ = atom                            
                            res_id = (model_id, chain, resi, icode)
                            if res_id in self.residues:
                                self.residues[res_id].append( (atname, at_counter) )
                            else:
                                self.residues[res_id] = [ (atname, at_counter) ]
                                
                            at_counter += 1
                else:
                    raise PDBParsingError('Could not parse the PDB file at line {0}: record unknown ({1})'.format(iline, record), line, True)
        if len_warning:
        	print "WARNING: At least one ATOM/HETATM line consists of less than 80 columns. \nTo follow the official wwPDB guidelines, please use http://github.com/haddocking/pdb-tools/pdb_linewidth to"+\
        	"format your PDB file.\nOfficial PDB format guidelines can be found here: http://www.wwpdb.org/documentation/file-format-content/format33/sect9.html#ATOM.\n"

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="This script validates a PDB file (*.tbl).\n")
    
    parser.add_argument("pdb", help="PDB file")

    args = parser.parse_args()

    try:
        f_pdb = PDBParser(args.pdb, True)
    except PDBParsingError as e:
        print e
