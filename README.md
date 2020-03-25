# AMBER-Membrane_protein_tutorial

Tutorial on the setup and simulation of a membrane protein with AMBER Lipid20 and PACKMOL-Memgen

![Alt text](/figures/m2_setup.png =250x250 "M2_IXO")

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
> mv ~/Downloads/4mqs.pdb 4mqs_OPM.pdb  

The OPM database provides GPCR structures such that they are pre-aligned for membrane-embedding, and show dummy coordinates as to where the membrane starts and ends.

This structure of the M2 receptor has chain A, the receptor, and chain B, a G-protein mimetic camelid antibody fragment. It also has the agonist ligand iperoxo. In this case, we will simulation just the M2 receptor (no G-protein or mimetic) with the agonist iperoxo.

Get the raw receptor and ligand pdb files:
> grep '  A  ' 4mqs_OPM.pdb > m2_only.pdb  
> grep 'IXO' 4mqs_OPM.pdb > ixo_ligand.pdb 

This gives us the un-prepared receptor and ligand coordinates.

# Step 2: Receptor and ligand preparation

We are still in the "system_pdb" directory:

> cd ./files_clean/system_pdb 

We need to prepare the M2 receptor for molecular dynamics with AMBER. You may have your own workflow / preferences here. I am typically using CCG MOE protein preparation wizard to achieve the following: 

* Fill missing atoms
* Cap termini
* Define disulfide bridges
* Set protonation states at pH 7.4, including sampling of side chain rotomers

I will not go further on the preparation here - needless to say, you need a prepared receptor for further simulation steps. The output from MOE is provided as "m2_prep.pdb". Side-chain protonation states are set to their dominate form at pH 7.4, except ASP69 inside the helical bundle, which is charge neutral ("ASH" residue name, as AMBER convention). ASP69 is protonated during the entire photocycle in rhodopsin (https://www.pnas.org/content/90/21/10206.long).

Now we need to prepare the ixperoxo agonist.

> cd ../ligand_params

Again, I am using MOE to add hydrogens to the initial ligand coordinates, set charge state, correct bond orders. The output is "ixo_ligand.mol2". You will need to do similar, using a method of your choice.

We then determine partial charges and atom types for GAFF2 using antechamber:

> antechamber -i ixo_ligand.mol2 -fi mol2 -o IXO.mol2 -fo mol2 -c bcc -s 2 -nc 1 -rn IXO -at gaff2  
> parmchk2 -i IXO.mol2 -f mol2 -o missing_gaff2.frcmod -at gaff2

As a personal preference, I typically generate a "clean" ligand PDB file and AMBER .off file containing force field parameters:

> antechamber -i IXO.mol2 -fi mol2 -o IXO.pdb -fo pdb  
> tleap -f convert.leap  # this step simply converts the IXO.mol2 to IXO.off file

Finally, an important part of system preparation is placement of initial water molecules. Again, you may have your own method here. Typically, I follow this workflow for 3D-RISM placement of waters:

* 3D-RISM: http://dansindhikara.com/Tutorials/Entries/2012/1/1_Using_3D-RISM_and_PLACEVENT.html

A more recent tutorial is also available:

* 3D-RISM and MOFT: http://ambermd.org/tutorials/advanced/tutorial34/index.html

You will have to remove waters that are placed in the membrane region. Prepared waters are provided in "./system_pdb/m2_rism_sele.pdb".

# Step 3: Building the membrane

Now that we have prepared files for the M2 receptor, agonist iperoxo and initial water placement, we need to build the membrane simulation box.

> cd ../membrane_build

We run PACKMOL-Memgen using the "m2_prep.pdb" file as input:

> packmol-memgen --pdb ../system_pdb/m2_prep.pdb --lipids POPC:CHL1 --ratio 9:1 --preoriented --salt --salt_c Na+ --saltcon 0.15 --dist 10 --dist_wat 15 --notprotonate --nottrim

Take care to understand each of the flags. Here we ask for a mixed POPC/CHOL membrane, but you may want plain POPC, or a different lipid composition. You can run packmol-memgen --help to find out about each flag. Briefly:

* "--pdb ../system_pdb/m2_prep.pdb": input receptor PDB
* "--lipids POPC:CHL1": build a mixed POPC/CHOL membrane
* "--ratio 9:1": POPC/CHOL ratio of 9:1 
* "--preoriented": the OPM coordinates are already orientated along the z-axis, for membrane building
* "--salt --salt_c Na+ --saltcon 0.15": Add 0.15 M of NaCl salt to the water layer
* "--dist 10": minimum maxmin value for x, y, z to box boundary 
* "--dist_wat 15": water layer thickness of 15 A
* "--notprotonate --nottrim": do not process input receptor PDB file (since we have already prepared this)

PACKMOL-Memgen should output a "bilayer_m2_prep.pdb" file, which contains our receptor and the prepared membrane & water box.

This final step is personal preference: PACKMOL-Memgen often slightly shifts the coordinates of the overall system versus the input receptor. Typically, I prefer to have the initial prepared receptor, ligand coordinates and separately, the membrane box PDB.

So, we need to extract just the membrane & water from "bilayer_m2_prep.pdb" and reset the coordinates to match those of "../system_pdb/m2_prep.pdb". You can use the "shift_membrane.py" script for this:

> ./shift_membrane.py -i ../system_pdb/m2_prep.pdb -m bilayer_m2_prep.pdb -o POPC_CHL_amber.pdb

The flags here are:

* "-i ../start_pdb/m2_prep.pdb": our original receptor PDB
* "-m bilayer_m2_prep.pdb": output membrane system from PACKMOL-Memgen
* "-o POPC_CHL_amber.pdb": name of the output file for final shifted membrane box

This will output:

> Original protein 1 COM: 0.655 -0.017 -3.809  
>  
> Shifted protein 2 COM: -6.487 5.690 -3.809  
>  
> Writing POPC_CHL_amber.pdb membrane, shifted by  7.142 -5.707 0.000  
>  
> Box X, Y, Z: 85.266 85.285 94.169  

Here, the final line gives us the box dimensions of the water layer (the box dimensions may differ with separate PACKMOL-Memgen runs).

One note: since our iperoxo ligand has a +1 charge, we need to delete a single Na+ ion from the "POPC_CHL_amber.pdb" PDB file. You can use a text editor to simply remove the first Na+.

# Step 4: Build the AMBER parameter and topology file with leap

Now, we have all the files needed to build the parameter and topology file with tleap:

> cd ../../files_clean

The "build.leap" file is included. You will see that we have put the box dimensions from the previous step in here:

> set system box {85.266 85.285 94.169 }

Take care to understand each line. It is similar to building other systems with AMBER. Now, run tleap:

> tleap -f build.leap

This should output "m2_IXO.prmtop" and "m2_IXO.inpcrd".

**Important:** The "m2_prep.pdb" contains lines defining disulfide bridges: 

LINK         SG  CYX A  96                 SG  CYX A 176     1555   1555  2.03  
LINK         SG  CYX A 413                 SG  CYX A 416     1555   1555  2.03  

If you prepared your receptor in a different way, you will have to add lines into the tleap command to define these bonds.

A few steps with Parmed, again as personal preference. Since AMBER resets the residue numbering, it will not correspond to the original PDB information. You can add PDB information to a topology with Parmed, so that output PDBs saved from the simulation have residue numbering matching the initial PDB file:

> parmed -i parmed_resi.in

We also create a prmtop ready for hydrogen mass repartitioning simulations, allowing a 4 fs timestep (https://pubs.acs.org/doi/10.1021/ct5010406):

> parmed -i hmass_parmed.in

With this, we are ready for the MD simulation step.

# Step 5: GPCR molecular dynamics simulation and analysis

Go into the "MD_simulation" directory:

> cd ./MD_simulation

This folder contains input files and a bash script ("run_MD.sh") for the each step on a single GPU with pmemd.cuda. You may need to modify for your own machine / cluster.

The simulation steps are as follows:

* 01_Min.in : very short minimization on CPU with pmemd. This is advised for membrane systems, which often have bad clashes of lipid chains to resolve. The CPU code is more robust in dealing with these than the GPU
* 02_Min2.in : longer minimization on GPU
* 03_Heat.in, 04_Heat2.in : heating to 303 K, with restraints on M2 receptor, iperoxo, membrane lipids
* 05_Back.in : run 1 ns NPT with restraints on receptor backbone atoms, iperoxo
* 06_Calpha.in : run 1 ns NPT with restraints on receptor carbon-alpha atoms, iperoxo
* 07_Prod.in : run 100 ns NPT equilibration, all restraints removed
* 08_Long.in : run 0.5 us NPT production, with Monte Carlo barostat and hydrogen mass repartitioning

Once simulations are complete, we can do some simple analysis of the M2 receptor RMSD and iperoxo ligand RMSD.

> cpptraj m2_IXO.prmtop<image.trajin  
> cpptraj m2_IXO.prmtop<prot_rmsd.trajin  
> cpptraj m2_IXO.prmtop<lig_rmsd.trajin  

This creates an imaged trajectory from the 07_Prod and 08_Long steps, then determines the protein RMSD and ligand RMSD over the course of these simulation steps. We can plot the results as shown:


