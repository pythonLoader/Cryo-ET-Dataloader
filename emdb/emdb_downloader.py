# -*- coding: utf-8 -*-
"""EMDB Downloader
Downloads a Cryo-Electron Microscopy resource given the accession ID.
Written by Arpita Saha 
"""

import requests, os, subprocess, shutil
import zipfile
from bs4 import BeautifulSoup as bs

def get_header_data(accession_id, headerURL, debug):
  header_response = requests.get(headerURL)
  if header_response.status_code == 200 and debug == True:
        print("Downloading header file----")
  temp_file="/content/drive/MyDrive/EMDB_Data/New_Maps/temp.xml"
  with open(temp_file, "wb+") as file:
    file.write(header_response.content)
  with open(temp_file, "r") as file:
    # Read each line in the file, readlines() returns a list of lines
    content = file.readlines()
    # Combine the lines in the list into a string
    content = "".join(content)
    bs_content = bs(content, "lxml")
  
  structure_title = bs_content.find("title") 
  if structure_title is not None:
    structure_title = structure_title.contents[0]
  else:
    structure_title = ""

  depositiondate = bs_content.find("depositiondate")
  if depositiondate is not None:
    depositiondate = depositiondate.contents[0]
  else:
    depositiondate = ""

  headerreleasedate =  bs_content.find("headerreleasedate")
  if headerreleasedate is not None:
    headerreleasedate = headerreleasedate.contents[0]
  else:
    headerreleasedate = ""

  mapreleasedate =  bs_content.find("mapreleasedate")
  if mapreleasedate is not None:
    mapreleasedate = mapreleasedate.contents[0]
  else:
    mapreleasedate = ""

  fittedpdb = bs_content.find("fittedpdbentryidlist")
  fittedpdblist = bs_content.find_all("fittedpdbentryid")
  fitted_pdbs=""
  if fittedpdblist is not None:
    for i,fp in enumerate(fittedpdblist):
      fitted_pdbs+=fittedpdblist[i].contents[0]
      if (i<len(fittedpdblist)-1):
        fitted_pdbs+ ", "
  else:
    fitted_pdbs = ""


  articletitle = ""
  pubmed = ""
  doi = ""
  issn = ""
  published = bs_content.find("primaryreference", attrs={'published' : 'true'})
  
  if published is not None:
    articletitle= published.find("articletitle")
    if articletitle is not None:
      articletitle = articletitle.contents[0]
    else:
      articletitle = ""
    
    pubmed=published.find("externalreference", attrs={'type' : 'pubmed'})
    if pubmed is not None:
      pubmed = pubmed.contents[0]
    else:
      pubmed = ""

    doi = published.find("externalreference", attrs={'type' : 'doi'})
    if doi is not None:
      doi = doi.contents[0]
    else:
      doi = ""

    issn = published.find("externalreference", attrs={'type' : 'issn'})
    if issn is not None:
      issn = issn.contents[0]   
    else:
      issn = ""

  os.remove(temp_file)
  return structure_title, fitted_pdbs, depositiondate, headerreleasedate, mapreleasedate, articletitle, pubmed, doi, issn 

def get_header_data_String_format(structure_title, fittedpdbs, depositiondate, headerreleasedate, mapreleasedate, articletitle, pubmed, doi, issn):
  header_content = "Structure Title: {}\n".format(structure_title)
  header_content += "Fitted PDBs: {}\n".format(fittedpdbs)
  header_content += "Deposition Date: {}\n".format(depositiondate)
  header_content += "Header Release Date: {}\n".format(headerreleasedate)
  header_content += "Map Release Date: {}\n".format(mapreleasedate)
  header_content += "Article Title: {}\n".format(articletitle)
  header_content += "Pubmed ID: {}\n".format(pubmed)
  header_content += "Article Link: {}\n".format(doi)
  header_content += "ISSN: {}\n".format(issn)
  return header_content

def download_emdb(accession_id, output_directory, map=True, header=True, image=True, debug=True ):
  URL_pdbj="https://ftp.pdbj.org/pub/emdb/structures/EMD-{}/".format(accession_id)
  response = requests.get(URL_pdbj)
  #
  if not os.path.exists(output_directory):
    os.mkdir(output_directory)
  if (response.status_code == 200): #found at PDBJ
    if debug == True:
      print("Downloaading from EM Resource of PDBJ---- \n")
    if (map==True):
      map_url = URL_pdbj+"map/emd_{}.map.gz".format(accession_id)
      map_response = requests.get(map_url)
      if map_response.status_code == 200 and debug == True:
        print("Downloading .map file----")
      with open(output_directory+"/emd_{}.map.gz".format(accession_id), 'wb') as output_file:
        output_file.write(map_response.content)
    if (image == True):
      image_url = URL_pdbj + "images/emd_{}.png".format(accession_id)
      image_response = requests.get(image_url)
      if image_response.status_code == 200 and debug == True:
        print("Downloading image file----")
      with open(output_directory+"/emd_{}.png".format(accession_id), 'wb') as output_file:
        output_file.write(image_response.content)
    if header == True:
      header_url = "https://ftp.pdbj.org/pub/emdb/structures/EMD-{}/header/emd-{}.xml".format(accession_id, accession_id)
      structure_title, fittedpdbs, depositiondate, headerreleasedate, mapreleasedate, articletitle, pubmed, doi, issn = get_header_data(accession_id, header_url, debug)
      header_content = get_header_data_String_format(structure_title, fittedpdbs, depositiondate, headerreleasedate, mapreleasedate, articletitle, pubmed, doi, issn)
      with open(output_directory+"/header_emd_{}.txt".format(accession_id), 'w+') as output_file:
        output_file.write(header_content)
  elif response.status_code == 404: #Not found in PDBJ
      URL_EMDataResource = "https://www.emdataresource.org/EMD-{}".format(accession_id)
      response = requests.get(URL_EMDataResource)
      if response.status_code == 200: #downloading from EM Data Resource 
        if debug == True:
          print("Downloaading from EM Data Resource ---- \n")
        if (map==True):
          map_url = "https://ftp.wwpdb.org/pub/emdb/structures/EMD-{}/map/emd_{}.map.gz".format(accession_id, accession_id)
          map_response = requests.get(map_url)
          if map_response.status_code == 200 and debug == True:
            print("Downloading .map file----")
          with open(output_directory+"/emd_{}.map.gz".format(accession_id), 'wb') as output_file:
            output_file.write(map_response.content)
        if (image == True):
          image_url = "https://ftp.wwpdb.org/pub/emdb/structures/EMD-{}/images/emd_{}.png".format(accession_id, accession_id)
          image_response = requests.get(image_url)
          if image_response.status_code == 200 and debug == True:
            print("Downloading image file----")
          with open(output_directory+"/emd_{}.png".format(accession_id), 'wb') as output_file:
            output_file.write(image_response.content)
        if (header == True):
          header_url = "https://ftp.wwpdb.org/pub/emdb/structures/EMD-{}/header/emd-{}.xml".format(accession_id, accession_id)
          structure_title, fittedpdbs, depositiondate, headerreleasedate, mapreleasedate, articletitle, pubmed, doi, issn = get_header_data(accession_id, header_url, debug)
          header_content = get_header_data_String_format(structure_title, fittedpdbs, depositiondate, headerreleasedate, mapreleasedate, articletitle, pubmed, doi, issn)
          with open(output_directory+"/header_emd_{}.txt".format(accession_id), 'w+') as output_file:
            output_file.write(header_content)
      elif ressponse.status_code == 404: # Not found in EM Data Resource
        URL_pdbE = "https://www.ebi.ac.uk/pdbe/entry/emdb/EMD-{}".format()
        response = requests.get(URL_pdbE) # searching in pdb E
        if response.status_code == 200:
          if debug == True:
            print("Downloaading from EM Resource of PDBE---- \n")
          if map == True:
            map_url="ftp://ftp.ebi.ac.uk/pub/databases/emdb/structures/EMD-{}/map/emd_{}.map.gz".format(accession_id, accession_id)
            map_response = requests.get(map_url)
            if map_response.status_code == 200 and debug == True:
              print("Downloading .map file----")
            with open(output_directory+"/emd_{}.map.gz".format(accession_id), 'wb') as output_file:
              output_file.write(map_response.content)
          if header == True:
            header_url = "https://www.ebi.ac.uk/pdbe/entry/download/EMD-{}/xml".format(accession_id)
            structure_title, fittedpdbs, depositiondate, headerreleasedate, mapreleasedate, articletitle, pubmed, doi, issn = get_header_data(accession_id, header_url, debug)
            header_content = get_header_data_String_format(structure_title, fittedpdbs, depositiondate, headerreleasedate, mapreleasedate, articletitle, pubmed, doi, issn)
            with open(output_directory+"/header_emd_{}.txt".format(accession_id), 'w+') as output_file:
              output_file.write(header_content)
          if image == True:
            bundle_url = "https://www.ebi.ac.uk//pdbe/entry/download/EMD-{}/bundlezip".format(accession_id)
            output_ = output_directory+"/bundle.zip"
            for path in execute(["wget", "-O", output_, bundle_url]):
              print(path, end="")
            if debug == True:
              print("Downloading image file----")
            if not os.path.exists(output_directory+"/extracted_folder"):
              os.mkdir(output_directory+"/extracted_folder")
            with zipfile.ZipFile(output_, 'r') as zip_ref:
              zip_ref.extractall(output_directory+"/extracted_folder")
            image_file_path = output_directory+"/extracted_folder/EMD-{}/images/emd_{}.png".format(accession_id,accession_id)
            shutil.copy(image_file_path, output_directory)
            os.remove(output_directory+"/extracted_folder")
          else:
            print("Not found in EM Data Resource or EM Resource of PDBJ or PDBE")

def emdb_stub(accession_list, output_directory, map_=True, header=True, image=True, debug=True):
  for entry in accession_list:
    download_emdb(entry,output_directory,map_,header,image,debug)

#example
# def main(accession_id):
# 	output_directory="EMD-{}".format(accession_id)
# 	download_emdb(accession_id, output_directory)

# if __name__ == '__main__':
# 	main("11082")
