import requests
import pandas as pd

accession_list = ['101d', '1jdn', 'lmao']  # 'lmao' is not a real protein, just for sanity checking
download_pdb = True
download_cif = True
output_dir = '.'

debug_on = False
download_links = True

rcsb_links = []
pdbe_links = []
pdbj_links = []

for index, accession in enumerate(accession_list):
    print("Currently downloading protein no.{}: {}".format(index + 1, accession))
    
    if download_pdb:
        print("\tDownloading pdb file for {}.".format(accession))
        
        # at first, trying to download corresponding pdb file from 'https://www.rcsb.org/'
        if debug_on:
            print("<debug> Downloading pdb file from RCSB for {}.".format(accession))
        response = requests.get("https://files.rcsb.org/download/{}.pdb.gz".format(accession), allow_redirects=True)
        
        # trying to download corresponding pdb file from 'https://www.ebi.ac.uk/pdbe/' if not available in RCSB
        if response.status_code == 404:
            if debug_on:
                print("<debug> Downloading pdb file from PDBe for {}, failed in RCSB.".format(accession))
            response = requests.get("http://ftp.ebi.ac.uk/pub/databases/rcsb/pdb-remediated/data/structures/divided/pdb/{}/pdb{}.ent.gz".format(accession[1: 3], accession), allow_redirects=True)
            
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
            print("\t\tpdb{}: Not found in RCSB, PDBe, PDBj, wwPDB.".format(accession))
    
    if download_cif:
        print("\tDownloading cif file for {}.".format(accession))
        
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
            print("\t\tcif{}: Not found in RCSB, PDBe, PDBj, wwPDB.".format(accession))

    if download_links:
        print("\tCollecting PDB sites' links for {}".format(accession))

        response = requests.get("https://www.rcsb.org/structure/{}".format(accession))
        if response.status_code == 200:
            rcsb_links.append("https://www.rcsb.org/structure/{}".format(accession))
        else:
            rcsb_links.append("no RCSB link available")
            if debug_on:
                print("<debug> No RCSB entry for {}.".format(accession))

        response = requests.get("https://www.ebi.ac.uk/pdbe/entry/pdb/{}".format(accession))
        if response.status_code == 200:
            pdbe_links.append("https://www.ebi.ac.uk/pdbe/entry/pdb/{}".format(accession))
        else:
            pdbe_links.append("no PDBe link available")
            if debug_on:
                print("<debug> No PDBe entry for {}.".format(accession))

        """
            problem: requests.get(url) responds with status code 404 even for valid PDBj protein profiles.
            solution: https://stackoverflow.com/questions/48125006/404-status-code-while-making-http-request-via-pythons-requests-library-howev
            
            But now, requests.get(url) responds with status code 200 even for invalid PDBj protein profiles.
        """
        if requests.get("https://pdbj.org/rest/downloadPDBfile?format=pdb&id={}".format(accession), allow_redirects=True).status_code == 200 or requests.get("https://pdbj.org/rest/downloadPDBfile?format=mmcif&id={}".format(accession), allow_redirects=True) == 200:
            pdbj_links.append("https://pdbj.org/mine/summary/{}".format(accession))
        else:
            pdbj_links.append("no PDBj link available")
            if debug_on:
                print("<debug> No PDBj entry for {}.".format(accession))

    print("Completed, {}/{} proteins remaining.{}".format(len(accession_list) - (index + 1), len(accession_list), '\n' if index < len(accession_list) - 1 else ''))

if download_links:
    data_frame = pd.DataFrame(columns=['PDB Entry', 'RCSB Links', 'PDBe Links', 'PDBj Links'])
    data_frame['PDB Entry'] = accession_list
    data_frame['RCSB Links'] = rcsb_links
    data_frame['PDBe Links'] = pdbe_links
    data_frame['PDBj Links'] = pdbj_links
    data_frame.to_excel("{}/proteins-links.xlsx".format(output_dir), index=False)
