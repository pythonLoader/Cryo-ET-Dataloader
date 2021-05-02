import requests
import pandas as pd

# source & reference: 'https://github.com/pythonLoader/PDB-Scrapper/blob/main/scrapper.py'
from bs4 import BeautifulSoup
import time

"""
    function download_rcsb_pdbe_pdbj_links():
        description:
            Function for downloading protein profile links from RCSB, PDBe, PDBj sites.
    
        input:
            - accession_list: list of proteins' accession IDs (default=None)
            - debug_on: prints debugging message if True (default=False)
            
        output:
            - data_frame: data frame containing all the profile links for given proteins
"""
def download_rcsb_pdbe_pdbj_links(accession_list=None, debug_on=False):
    if accession_list is None:
        accession_list = []

    rcsb_links = []
    pdbe_links = []
    pdbj_links = []

    for index, accession in enumerate(accession_list):
        print("\nCurrently collecting PDB sites' links for protein no.{}: {}".format(index + 1, accession))

        # collecting link from RCSB site
        response = requests.get("https://www.rcsb.org/structure/{}".format(accession))
        if response.status_code == 200:
            rcsb_links.append("https://www.rcsb.org/structure/{}".format(accession))
        else:
            rcsb_links.append("no RCSB link available")
            if debug_on:
                print("<debug> No RCSB entry for {}.".format(accession))

        # collecting link from PDBe site
        response = requests.get("https://www.ebi.ac.uk/pdbe/entry/pdb/{}".format(accession))
        if response.status_code == 200:
            pdbe_links.append("https://www.ebi.ac.uk/pdbe/entry/pdb/{}".format(accession))
        else:
            pdbe_links.append("no PDBe link available")
            if debug_on:
                print("<debug> No PDBe entry for {}.".format(accession))

        # collecting link from PDBj site
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

        print("Completed, {}/{} proteins remaining.".format(len(accession_list) - (index + 1), len(accession_list)))

    data_frame = pd.DataFrame(columns=['PDB Entry', 'RCSB Links', 'PDBe Links', 'PDBj Links'])
    data_frame['PDB Entry'] = accession_list
    data_frame['RCSB Links'] = rcsb_links
    data_frame['PDBe Links'] = pdbe_links
    data_frame['PDBj Links'] = pdbj_links

    return data_frame


"""
    source & reference: 'https://github.com/pythonLoader/PDB-Scrapper/blob/main/scrapper.py'
    
    function get_metadata():
        description:
            Function for extracting metadata for given protein from 'https://www.rcsb.org/'.

        input:
            - accession: corresponding protein's accession ID

        output:
            - structure_title: protein's structure title
            - deposited_date: protein's deposition date
            - released_date: protein's release date
            - em_data_id: protein's electron-microscopy data bank ID (if any)
            - em_data_link: protein's electron-microscopy data bank profile link (if any)
            - paper_name: corresponding paper's title (if any)
            - paper_link: corresponding paper's DOI (if any)
            - abstract_text: abstract from corresponding paper (if any)
"""
def get_metadata(accession):
    url = 'https://www.rcsb.org/structure/' + accession
    start_time = time.time()

    response = requests.get(url)
    print("Page Fetching Time: {}".format(time.time() - start_time))

    if not response.status_code == 200:
        return 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'No abstract available'

    intermediate_time = time.time()
    soup = BeautifulSoup(response.content, 'html.parser')
    print("Beautiful Soup Parsing Time: {}".format(time.time() - intermediate_time))

    if soup.find(id='structureTitle') is None:
        structure_title = 'NA'
    else:
        structure_title = soup.find(id='structureTitle').text.strip()

    if soup.find(id='header_deposited-released-dates') is None:
        deposited_date = 'NA'
        released_date = 'NA'
    else:
        deposited_released_dates = soup.find(id='header_deposited-released-dates').text.strip().split("\xa0")
        deposited_date = deposited_released_dates[1].strip()
        released_date = deposited_released_dates[3].strip()

    if soup.find(id="header_emdb") is None:
        em_data_id = 'NA'
        em_data_link = 'NA'
    else:
        em_data_id = 'NA' if soup.find(id="header_emdb").find('a') is None else soup.find(id="header_emdb").find('a').text.strip()
        em_data_link = 'NA' if soup.find(id="header_emdb").find('a') is None else soup.find(id="header_emdb").find('a')['href']

    if soup.find(id='primarycitation') is None:
        paper_name = 'NA'
        paper_link = 'NA'
        abstract_text = 'No abstract available'
    else:
        paper_name = 'NA' if soup.find(id='primarycitation').find('h4') is None else soup.find(id='primarycitation').find('h4').text.strip()
        pubmed_doi = soup.find(id='primarycitation').find('li', id="pubmedDOI")
        if pubmed_doi:
            paper_link = pubmed_doi.find('a')['href']
        else:
            paper_link = "Not published yet"

        if soup.find(id='primarycitation').find(id='abstractFull') is None:
            abstract_text = 'No abstract available'
        else:
            abstract_text = 'No abstract available' if soup.find(id='primarycitation').find(id='abstractFull').find('p') is None else soup.find(id='primarycitation').find(id='abstractFull').find('p').text.strip()

    return structure_title, deposited_date, released_date, em_data_id, em_data_link, paper_name, paper_link, abstract_text


"""
    source & reference: 'https://github.com/pythonLoader/PDB-Scrapper/blob/main/scrapper.py'
    
    function download_rcsb_metadata():
        description:
            Function for downloading proteins' metadata from 'https://www.rcsb.org/'.

        input:
            - accession_list: list of proteins' accession IDs (default=None)

        output:
            - data_frame: data frame containing all the metadata for given proteins
"""
def download_rcsb_metadata(accession_list=None):
    if accession_list is None:
        accession_list = []

    structure_titles = []
    deposited_dates = []
    released_dates = []
    em_data_ids = []
    em_data_links = []
    paper_names = []
    paper_links = []

    for index, accession in enumerate(accession_list):
        print("\nCurrently working with protein no.{}: {}".format(index + 1, accession))

        (structure_title, deposited_date, released_date, em_data_id, em_data_link, paper_name, paper_link, abstract_text) = get_metadata(accession)
        print("\nStructure Title: {}\nDeposited Date: {}\nReleased Date: {}\nEM Data ID: {}\nEM Data Link: {}\nPaper Name: {}\nPaper Link: {}\n\nAbstract: {}\n".format(structure_title, deposited_date, released_date, em_data_id, em_data_link, paper_name, paper_link, abstract_text))
        print("-----------------------")

        structure_titles.append(structure_title)
        deposited_dates.append(deposited_date)
        released_dates.append(released_date)
        em_data_ids.append(em_data_id)
        em_data_links.append(em_data_link)
        paper_names.append(paper_name)
        paper_links.append(paper_link)

    data_frame = pd.DataFrame(columns=['PDB Entry', 'Structure Title', 'Paper DOI', 'Paper Name', 'EMDB ID', 'EMDB Link', 'Deposited Date', 'Released Date'])
    data_frame['PDB Entry'] = accession_list
    data_frame['Structure Title'] = structure_titles
    data_frame['Paper DOI'] = paper_links
    data_frame['Paper Name'] = paper_names
    data_frame['EMDB ID'] = em_data_ids
    data_frame['EMDB Link'] = em_data_links
    data_frame['Deposited Date'] = deposited_dates
    data_frame['Released Date'] = released_dates

    return data_frame


"""
    function main():
        description:
            Function serving as entry point.

        input:
            - accession_list: list of proteins' accession IDs (default=None)
            - output_dir='.'
            - download_pdb: downloads pdb files if True (default=True)
            - download_cif: downloads cif files if True (default=True)
            - debug_on: prints debugging message if True (default=False)
            - download_links: downloads protein profile links from RCSB, PDBe, PDBj sites if True (default=False)
            - download_metadata: downloads protein metadata from RCSB site if True (default=False)
"""
def main(accession_list=None, output_dir='.', download_pdb=True, download_cif=True, debug_on=False, download_links=False, download_metadata=False):
    if accession_list is None:
        accession_list = []

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

        print("Completed, {}/{} proteins remaining.{}".format(len(accession_list) - (index + 1), len(accession_list), '\n' if index < len(accession_list) - 1 else ''))

    # preparing and downloading corresponding .xlsx file containing PDB sites' links to local machine
    if download_links:
        print("\n======================================")
        download_rcsb_pdbe_pdbj_links(accession_list, debug_on).to_excel("{}/proteins-links.xlsx".format(output_dir), index=False)

    # preparing and downloading corresponding .xlsx file containing metadata from 'https://www.rcsb.org/' to local machine
    if download_metadata:
        print("\n======================================")
        download_rcsb_metadata(accession_list).to_excel("{}/proteins-metadata.xlsx".format(output_dir), index=False)


if __name__ == '__main__':
    main(accession_list=['101d', '2cme', '1jdn', '6vxx', 'lmao'])  # 'lmao' is not a real protein, just for sanity checking
