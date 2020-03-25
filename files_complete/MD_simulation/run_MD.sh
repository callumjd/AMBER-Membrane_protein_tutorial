#!/bin/bash

export CUDA_VISIBLE_DEVICES="0"

# SYSTEM
export prmtop=m2_IXO.prmtop
export name=m2_IXO
export hmass=m2_IXO.hmass.prmtop

## Minimise ##
$AMBERHOME/bin/pmemd \
-O \
-i 01_Min.in \
-o 01_Min.out \
-p $prmtop \
-c ${name}.inpcrd \
-r 01_Min.rst 

$AMBERHOME/bin/pmemd.cuda \
-O \
-i 02_Min2.in \
-o 02_Min2.out \
-p $prmtop \
-c 01_Min.rst \
-r 02_Min2.rst 

### Equilibration ##
$AMBERHOME/bin/pmemd.cuda \
-O \
-i 03_Heat.in \
-o 03_Heat.out \
-p $prmtop \
-c 02_Min2.rst \
-r 03_Heat.rst \
-x 03_Heat.nc \
-ref 02_Min2.rst

$AMBERHOME/bin/pmemd.cuda \
-O \
-i 04_Heat2.in \
-o 04_Heat2.out \
-p $prmtop \
-c 03_Heat.rst \
-r 04_Heat2.rst \
-x 04_Heat2.nc \
-ref 03_Heat.rst

## Peptide backbone restrained
$AMBERHOME/bin/pmemd.cuda \
-O \
-i 05_Back.in \
-o 05_Back.out \
-p $prmtop \
-c 04_Heat2.rst \
-r 05_Back.rst \
-x 05_Back.nc \
-ref 04_Heat2.rst \
-inf 05_Back.mdinfo

## Peptide C-alpha atoms only restrained
$AMBERHOME/bin/pmemd.cuda \
-O \
-i 06_Calpha.in \
-o 06_Calpha.out \
-p $prmtop \
-c 05_Back.rst \
-r 06_Calpha.rst \
-x 06_Calpha.nc \
-ref 05_Back.rst \
-inf 06_Calpha.mdinfo

## 100ns NPT run ##
$AMBERHOME/bin/pmemd.cuda \
-O \
-i 07_Prod.in \
-o 07_Prod_$name.out \
-p $prmtop \
-c 06_Calpha.rst \
-r 07_Prod_$name.rst \
-x 07_Prod_$name.nc \
-inf 07_Prod_$name.mdinfo

## 500ns HMASS ##
$AMBERHOME/bin/pmemd.cuda \
-O \
-i 08_Long.in \
-o 08_Long_$name.out \
-p $hmass \
-c 07_Prod_$name.rst \
-r 08_Long_$name.rst \
-x 08_Long_$name.nc \
-inf 08_Long_$name.mdinfo \

