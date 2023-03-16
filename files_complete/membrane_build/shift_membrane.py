#!/usr/bin/env python
import sys
import math
import os.path
import argparse
import numpy as np

################################################################################
#
# shift_membrane. Run as:
# ./shift_membrane.py -i original_protein.pdb -m bilayer.pdb -o output_name.pdb 
#
################################################################################

# x,y,z cartesian coordinate object
class Coord(object):
	def __init__(self,x,y,z):
		self.x=x
		self.y=y
		self.z=z

# If your system has unusual atom types you may need to add the atomic
# mass into the dictionary below 
def atom_mass(str):
	weight={'C':'12.01','H':'1.008','P':'30.97','N':'14.01','O':'16.0','Cl':'35.45','F':'19.0','S':'32.065'}
	if str[0].isalpha() == True:
		if str[1].isalpha() == True:
			try:
				return weight[str[0:2]]
			except:
				return weight[str[0]]
		else:
			return weight[str[0]] 
	elif str[0].isalpha() == False:
		if str[1].isalpha() == True and str[2].isalpha() == True:
			try:
				return weight[str[1:3]]
			except:
				return weight[str[1]]
		else:
			return weight[str[1]]

def atom_length(file_in):
	length=0

	disallow=['MEMB','TIP3','SOD','POT','CLA']

	with open(file_in,'r') as f:
		for line in f:
			if line.split()[0]=='ATOM':
				if line.split()[-1] not in disallow:
					length+=1
			elif line.split()[0]=='HETATM':
				if line.split()[-1] not in disallow:
					length+=1

	return length

def get_com_pdb(file_in,length):

	output_coords=np.zeros((length,4))
	com_result=Coord(0.000,   0.000,  0.000)

	disallow=['MEMB','TIP3','SOD','POT','CLA']

	i=0
	with open(file_in,'r') as f:
		for line in f:
			if line.split()[0]=='ATOM' or line.split()[0]=='HETATM':
				if line.split()[-1] not in disallow:
					output_coords[i][0]=float(atom_mass(str(line[12:16])))
					output_coords[i][1]=str(line[30:38])
					output_coords[i][2]=str(line[38:46])
					output_coords[i][3]=str(line[46:54])
					i+=1

	total_weight=0.0
	for i in range(0,length):
		total_weight+=output_coords[i][0]

	for i in range(0,length):
		com_result.x+=output_coords[i][1]*output_coords[i][0]
		com_result.y+=output_coords[i][2]*output_coords[i][0]
		com_result.z+=output_coords[i][3]*output_coords[i][0]
	
	com_result.x=com_result.x/total_weight
	com_result.y=com_result.y/total_weight
	com_result.z=com_result.z/total_weight

	return com_result

def get_wat_size(file_in):

	wat_xyz=[]
	with open(file_in,'r') as f_in:
		for line in f_in:
			if line.split()[0]=='ATOM' or line.split()[0]=='HETATM':
				if line.split()[-1]=='TIP3':

					x=float(line.split()[-6])
					y=float(line.split()[-5])
					z=float(line.split()[-4])

					wat_xyz.append((x,y,z))

	wat_xyz_np=np.array(wat_xyz)

	box_x=abs(np.min(wat_xyz_np[:,0]))+abs(np.max(wat_xyz_np[:,0]))
	box_y=abs(np.min(wat_xyz_np[:,1]))+abs(np.max(wat_xyz_np[:,1]))
	box_z=abs(np.min(wat_xyz_np[:,2]))+abs(np.max(wat_xyz_np[:,2]))

	return Coord(box_x,box_y,box_z)

################################################################################
#### Read input from command line ####
################################################################################
prot_file=None
membrane_file=None
output_file=None

parser = argparse.ArgumentParser()
parser.add_argument("-i", type=str, help="Original input receptor PDB file",required=True)
parser.add_argument("-m",  type=str, help="Packmol-memgen generated protein+membrane PDB to shift",required=True)
parser.add_argument("-o", type=str, help="Output name of PDB",required=True)

args = parser.parse_args()

# Check command line arguments exist 
args = parser.parse_args()
if (args.i != None and args.m != None and args.o != None):
	if (os.path.isfile(args.i) and os.path.isfile(args.m)):
		prot_file=args.i
		membrane_file=args.m
		output_file=args.o
	else:
		parser.print_help()
		sys.exit()

if prot_file==None or membrane_file==None:
	print('Error: input options not set')
	sys.exit()

################################################################################
#### Get centre of mass ####
################################################################################

prot_length=atom_length(prot_file)
mem_length=atom_length(membrane_file)

prot_com=get_com_pdb(prot_file,prot_length)
mem_com=get_com_pdb(membrane_file,mem_length)

print("Original protein 1 COM: %.3f %.3f %.3f\n" % (prot_com.x,prot_com.y,prot_com.z))
print("Shifted protein 2 COM: %.3f %.3f %.3f\n" % (mem_com.x,mem_com.y,mem_com.z))

move=Coord((prot_com.x - mem_com.x), (prot_com.y - mem_com.y), (prot_com.z - mem_com.z))

#################################################################################
#### Print output file #### 
#################################################################################

print("Writing %s membrane, shifted by  %.3f %.3f %.3f\n" % (output_file,move.x,move.y,move.z))

disallow=['MEMB','TIP3','SOD','POT','CLA']
with open(output_file,'w') as f_out:
	with open(membrane_file,'r') as f_in:
		for line in f_in:
			if line.split()[0]=='ATOM' or line.split()[0]=='HETATM':
				if line.split()[-1] in disallow:
					shifted=("%s   %7.3f %7.3f %7.3f\n" % (line[0:28],float(line[30:38])+move.x,float(line[38:46])+move.y,float(line[46:54])+move.z))
					f_out.write(shifted)
			elif line.split()[0]=='TER':
				f_out.write(line)
			elif line.split()[0]=='END':
				f_out.write(line)

box_dimensions=get_wat_size(membrane_file)

print('Box X, Y, Z: %.3f %.3f %.3f\n' % (box_dimensions.x,box_dimensions.y,box_dimensions.z))

