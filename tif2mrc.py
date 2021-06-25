import sys,os
import subprocess
import argparse

def converttif2mrc(direc):
    '''
        description:
            Function for converting tif file to mrc file.
    
        input:
            - direc: directory containing the tif file
            
            
        output:
            - conversion flag: True for Success, False for Not

    '''
    # lst = 
    # for filename in glob.iglob(direc+"**/*.tif",recursive=True):
    #     print(filename)

    print("Starting to convert tif2mrc using IMOD")
    for folder, subs, files in os.walk(direc):
        
        for file in files:
            mrc_fl_name = file.split(".tif")[0] + ".mrc"
            in_file = folder +"/"+file 
            out_file = folder + "/" + mrc_fl_name
            try:
                subprocess.call(['tif2mrc',in_file,out_file]) 
            except:
                return False
    
    return True


def parseArguments():
    parser = argparse.ArgumentParser(prog='tif2mrc_Converter', description='Data Converter for tiff files')
    required = parser.add_argument_group('Required Arguments')
    required.add_argument('-id','--input_directory',
    	help="Input directory of the folder containing tif files",
    	required=True,
    	metavar='direc')

    args = parser.parse_args()
    # print(args)
    # args = validate_arguments(parser,args)
    
    converttif2mrc(args.direc)

def main():
	arguments = parseArguments()

if __name__ == "__main__":
	
	main()
