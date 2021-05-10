import subprocess


def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line 
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)



def download(entry,output_direc):
    url = "empiar.pdbj.org::empiar/archive/"+str(entry)
    output_ = output_direc +"/"+ str(entry)+"/"
    
    for path in execute(["rsync", "-avz", "-P",url,output_]):
        print(path, end="")



def empiar_stub(accession_list,output_direc):
    for entry in accession_list:
        download(entry,output_direc)