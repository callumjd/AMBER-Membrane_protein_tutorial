# AMBER-Membrane_protein_tutorial

Tutorial on the setup and simulation of a membrane protein with AMBER Lipid20 and packmol-memgen

*Disclaimer: I hope this tutorial will be useful to others wishing to run molecular dynamics simulations of membrane proteins with AMBER. However, it is as much for my own reference as a guide to others. There are a number of ways to construct such systems for AMBER, including but not limited to: AMBAT, charmm-gui, DABBLE. In this case, we use the recently released PACKMOL-Memgen: https://pubs.acs.org/doi/10.1021/acs.jcim.9b00269*

# Requirements

* AMBER20
* Python 3.6 (https://www.continuum.io/downloads)
* I use the CCG MOE GUI for protein preparation (add hydrogens, cap termini, set protonation states). You may have access to MOE or a similar GUI/tool to achieve the same task. PACKMOL-Memgen also has prep options.

# Files
You can download this tutorial from github, the resulting zip file will not have any trajectories from the MD simulations described below due to file size limits. You may have to give the scripts executable permissions with chmod. Or runs scripts as:
* bash bash_script.sh  
* python python_script.py  

The scripts have been downloaded and tested on a linux machine. If you are using a Mac you may need to correct line endings within the scripts.

There are two versions of the files: "clean" and "complete". The clean version provides just the input files to complete the tutorial and is recommended. The complete version also has all output files, so that you can check you are getting the correct outputs.

# Introduction
This tutorial describes how to construct and simulate a GPCR membrane protein system using AMBER. In this case, we will setup and simulate the agonist bound, active state of the M2 muscarinic receptor, the structure of which was solved in 2013 ([10.1038/nature12735](https://www.nature.com/articles/nature12735)). The PDB code is 4MQS - active human M2 muscarinic acetylcholine receptor bound to the agonist iperoxo.

# Step 1: Starting PDBs

Start by downloading the coordinates from the Orientations of Proteins in Membranes (OPM) database:

> cd ./files_clean/system_pdb 

> Download OPM file 4MQS: https://opm.phar.umich.edu/proteins/2304 

> mv ~./Downloads/4mqs.pdb 4mqs_OPM.pdb


This database provides GPCR structures such that they are pre-aligned for membrane-embedding, and show dummy coordinates as to where the membrane starts and ends.

This structure of the M2 receptor has chain A, the receptor, and chain B, a G-protein mimetic camelid antibody fragment. It also has the agonist ligand iperoxo. In this case, we will simulation just the M2 receptor (no G-protein or mimetic) with the agonist iperoxo.

Get the raw receptor and ligand pdb files:
> grep '  A  ' 4mqs_OPM.pdb > m2_only.pdb  
> grep 'IXO' 4mqs_OPM.pdb > ixo_ligand.pdb 

This gives us the un-prepared receptor and ligand coordinates.

# Step 2: Receptor and ligand preparation

We are still in the "system_pdb" directory:

> cd ./files_clean/system_pdb 

We need to prepare the protein for molecular dynamics with AMBER. You may have your own workflow / preferences here. I am typically using CCG MOE protein preparation wizard to achieve the following: 

* Fill missing atoms
* Cap termini
* Define disulfide bridges
* Set protonation states at pH 7.4, including sampling of side chain rotomers

I will not go further on the preparation here - needless to say, you need a prepared receptor for further simulation steps. The output from MOE is provided as "m2_prep.pdb". Side-chain protonation states are set to their dominate form at pH 7.4, except ASP69 inside the helical bundle, which is charge neutral ("ASH" residue name, as AMBER convention). ASP69 is protonated during the entire photocycle in rhodopsin (https://www.pnas.org/content/90/21/10206.long).

 
