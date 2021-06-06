import subprocess
import glob
from pprint import pprint
import os,sys

def execute(cmd):
    '''
    Helper function for executing subprocess command
    '''
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line 
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)



def download(entry,output_direc):
    '''
        description:
            Function for downloading the empiar file
    
        input:
            - entry: EMPIAR entry or accession number
            
            
        output:
            No Output

    '''
    #Create URL Link
    url = "empiar.pdbj.org::empiar/archive/"+str(entry) 
    output_ = output_direc +"/"+ str(entry)+"/"
    
    for path in execute(["rsync", "-avz", "-P",url,output_]):
        print(path, end="")

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
            
            


def empiar_stub(accession_list,output_direc):
    '''
        Stub for downloading the EMPIAR files
    '''
    for entry in accession_list:
        download(entry,output_direc)


if __name__ == "__main__":
    direc = "/home/sawmya/Documents/CMU Internship/Dataloader/empiar/10533/data/Control h3ACs/Control.20200724"
    converttif2mrc(direc)