import requests

accession_list = ['101d', '1jdn']
download_pdb = True
download_cif = True
output_dir = '.'

debug_on = True

for index, accession in enumerate(accession_list):
    print("Currently downloading protein no.{}: {}".format(index + 1, accession))
    
    if download_pdb:
        print("Downloading pdb file for {}.".format(accession))
        
        # at first, trying to download corresponding pdb file from 'https://www.rcsb.org/'
        if debug_on:
            print("<debug> Downloading pdb file from RCSB for {}.".format(accession))
        response = requests.get("https://files.rcsb.org/download/{}.pdb.gz".format(accession), allow_redirects=True)
        
        # trying to download corresponding pdb file from 'https://www.ebi.ac.uk/pdbe/' if not available in RCSB
        if response.status_code == 404:
            if debug_on:
                print("<debug> Downloading pdb file from PDBe for {}, failed in RCSB.".format(accession))
            response = requests.get("http://ftp.ebi.ac.uk/pub/databases/rcsb/pdb-remediated/data/structures/divided/pdb/ac/pdb{}.ent.gz".format(accession), allow_redirects=True)
            
        # trying to download corresponding pdb file from 'https://pdbj.org/' if not available in RCSB, PDBe
        if response.status_code == 404:
            if debug_on:
                print("<debug> Downloading pdb file from PDBj for {}, failed in RCSB, PDBe.".format(accession))
            response = requests.get("https://pdbj.org/rest/downloadPDBfile?format=pdb&id={}".format(accession), allow_redirects=True)
        
        # trying to download corresponding pdb file from 'http://www.wwpdb.org/ftp/pdb-ftp-sites' if not available in RCSB, PDBe, PDBj
        if response.status_code == 404:
            if debug_on:
                print("<debug> Downloading pdb file from wwPDB for {}, failed in RCSB, PDBe, PDBj.".format(accession))
            response = requests.get("https://ftp.wwpdb.org/pub/pdb/data/structures/all/pdb/pdb{}.ent.gz".format(accession), allow_redirects=True)
            
        # downloading corresponding pdb file to local machine
        if response.status_code == 200:
            with open("{}/pdb{}.ent.gz".format(output_dir, accession), 'wb') as output_file:
                output_file.write(response.content)
        elif response.status_code == 404:
            print("pdb{}: Not found in RCSB, PDBe, PDBj, wwPDB.")
    
    if download_cif:
        print("Downloading cif file for {}.".format(accession))
        
        # at first, trying to download corresponding cif file from 'https://www.rcsb.org/'
        if debug_on:
            print("<debug> Downloading cif file from RCSB for {}.".format(accession))
        response = requests.get("https://files.rcsb.org/download/{}.cif.gz".format(accession), allow_redirects=True)
        
        # trying to download corresponding cif file from 'https://www.ebi.ac.uk/pdbe/' if not available in RCSB
        if response.status_code == 404:
            if debug_on:
                print("<debug> Downloading cif file from PDBe for {}, failed in RCSB.".format(accession))
            response = requests.get("https://www.ebi.ac.uk/pdbe/entry-files/{}.cif".format(accession), allow_redirects=True)  # archive mmCIF file
            # response = requests.get("https://www.ebi.ac.uk/pdbe/static/entry/{}_updated.cif".format(accession), allow_redirects=True)  # updated mmCIF file
            
        # trying to download corresponding cif file from 'https://pdbj.org/' if not available in RCSB, PDBe
        if response.status_code == 404:
            if debug_on:
                print("<debug> Downloading cif file from PDBj for {}, failed in RCSB, PDBe.".format(accession))
            response = requests.get("https://pdbj.org/rest/downloadPDBfile?format=mmcif&id={}".format(accession), allow_redirects=True)
        
        # trying to download corresponding cif file from 'http://www.wwpdb.org/ftp/pdb-ftp-sites' if not available in RCSB, PDBe, PDBj
        if response.status_code == 404:
            if debug_on:
                print("<debug> Downloading cif file from wwPDB for {}, failed in RCSB, PDBe, PDBj.".format(accession))
            response = requests.get("https://ftp.wwpdb.org/pub/pdb/data/structures/all/mmCIF/{}.cif.gz".format(accession), allow_redirects=True)
            
        # downloading corresponding cif file to local machine
        if response.status_code == 200:
            with open("{}/{}.cif.gz".format(output_dir, accession), 'wb') as output_file:
                output_file.write(response.content)
        elif response.status_code == 404:
            print("cif{}: Not found in RCSB, PDBe, PDBj, wwPDB.")
            
    print("Completed, {}/{} proteins remaining.{}".format(len(accession_list) - (index + 1), len(accession_list), '\n' if index < len(accession_list) - 1 else ''))
