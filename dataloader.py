import subprocess
import argparse
from pdb.pdb_cif_dataloader import pdb_stub
from empiar.empiar_downloader import empiar_stub
from emdb.emdb_downloader import emdb_stub
import shutil,os,sys

def validate_arguments(parser,args):
	
	if(args.singleId and args.batchFileName):
		parser.error("Cannot have both single accession and batch list together")
	if not args.singleId and not args.batchFileName:
		parser.error("Please input atleast one entry/accession or the batch entry/accession file")
	args.input_format = args.input_format.lower()
	return args

def get_accession_list(args):
	if(args.batchFileName):
		fl = open(args.batchFileName,"r")
		accession_list = fl.read().split(",")
		for idx,elems in enumerate(accession_list):
			accession_list[idx] = elems.strip()
		print(accession_list)
	elif(args.singleId):
		accession_list = [args.singleId]
	
	return accession_list

def handle_pdb_download(args,accession_list):
	if(args.links or args.metadata_pdb or args.ciff or args.pdb):
		pdb_stub(accession_list,args.output,args.pdb,args.ciff,False,args.links,args.metadata_pdb)
	else:
		pdb_stub(accession_list,args.output)


def handle_empiar_download(args,accession_list):
	
	empiar_stub(accession_list,args.output)

def handle_emdb_download(args,accession_list):
	if(args.header or args.image or args.map):
		emdb_stub(accession_list, args.output, args.map, args.header, args.image)
	else:
		emdb_stub(accession_list,args.output)

def parseArguments():
    parser = argparse.ArgumentParser(prog='dataloader', description='Data Downloader for cryo-EM/ cryo-ET and PDB files')
    required = parser.add_argument_group('Required Arguments')
    required.add_argument('-if','--input_format',
    	help="File format to be downloaded (EMDB/EMPIAR/PDB)",
    	required=True,
    	metavar='file_type')
    required.add_argument('-i',
    	'--input_id',
    	help="Single entry or accession id",
    	dest="singleId",
    	metavar="Single Entry/Accession ID")
    required.add_argument('-ib','--input_batch',
    	help="Batch entry or accession id file (IDs seperated by comma)",
    	dest="batchFileName",
    	metavar="Batch File Name")
    required.add_argument(
        "-o", "--output",
        dest="output", metavar="OUTPUT",
        default="output",
        type=str,
        help="output files with prefix OUTPUT. [default: %(default)s]")

    optional_for_pdb = parser.add_argument_group('Optional Arguments For PDB File Format')
    optional_for_pdb.add_argument('--ciff',
    	help="Download mmCIFF file format for PDB data",
    	action='store_true')
    optional_for_pdb.add_argument('--pdb',
    	help="Download pdb file format for PDB data",
    	action='store_true')
    optional_for_pdb.add_argument('--links',
    	help="Download links for the pdb entries",
    	action='store_true')
    optional_for_pdb.add_argument('--metadata_pdb',
    	help="Download metadata for the pdb entries",
    	action='store_true')
    optional_for_pdb.add_argument('--unzip_pdb',
    	help="Unzip the downloaded files",
    	action='store_true')


    optional_for_emdb = parser.add_argument_group('Optional Arguments for EMDB File Format')
    optional_for_emdb.add_argument('--unzip_emdb',
    	help="Unzip the downloaded files",
    	action='store_true')
    optional_for_emdb.add_argument('--header',
    	help="Download headers",
    	action='store_true')
    optional_for_emdb.add_argument('--image',
    	help="Download images",
    	action='store_true')
    optional_for_emdb.add_argument('--map',
    	help="Download map",
    	action='store_true')


    optional_for_empiar = parser.add_argument_group('Optional Arguments for EMPIAR File Format')
    optional_for_empiar.add_argument('--metadata_empiar',
    	help="Download metadata",
    	action='store_true')
    optional_for_empiar.add_argument('--tif2mrc',
    	help="Download metadata",
    	action='store_true')

    
    args = parser.parse_args()
    # print(args)
    args = validate_arguments(parser,args)
	
    accession_list = get_accession_list(args)

    if not os.path.exists(args.output):
    	os.mkdir(args.output)

    if(args.input_format == "pdb"):
    	handle_pdb_download(args,accession_list)
    elif(args.input_format == "empiar"):
    	handle_empiar_download(args,accession_list)
    elif(args.input_format == "emdb"):
    	handle_emdb_download(args,accession_list)
	
	


def main():
	arguments = parseArguments()

if __name__ == "__main__":
	
	main()