# This module contains a number of function that accept the URI of an IIIF manifest of a manuscript or book and return data, 
# both on the manuscript or book as a whole (book_properties) and on the individual canvases(canvas_properties). 
# Because much information in the manifests is not standardised, there has to be a separate function for each library. 

import urllib.request
import json
import re
import requests
from lxml import etree
from classes import *

def Canvas_parsing(canvas_list):
    # Most on the information about the individual canvases is standardised, so there can be a module used to extract it from all. 
    # Only the label of the canvas can hold different kinds of information and hence has to be dissected individually later. 
    images = []
    i = 0
    for canvas in canvas_list:
        
        i = i+1
        im = Image()
        im.index = i
        im.label_raw = canvas["label"]
        im.baseurl = canvas["images"][0]["resource"]["service"]["@id"]
        im.width = canvas["images"][0]["resource"]["width"]
        im.height = canvas["images"][0]["resource"]["height"]
        images.append(im)
    return images
    
        


def BSB_parsing(URI_entered):
    #f=open(r'C:\Users\berth\Documents\Warburg\Experimente - Python\iconobase\manifest.json', 'r', encoding='utf-8')
    url = urllib.request.urlopen(URI_entered)
    manifest = json.load(url)
    #Step 1: Extracting relevant fields from the general section of the Manifest
    metadata=manifest["metadata"]
    m = Metadata()
    m.manifest =  url.read()
    location = ""
    #repository = ""
    #shelfmark = ""
    bibliographic_id = []
    bibliographic_id_url = ""
    bibliographic_id_name = ""
    bibliographic_id_number = ""
    for step1 in metadata:
        label = step1["label"]
        for step2 in label:
            label_content = step2
            if label_content["@value"] == "Standort":
                location = step1["value"]
            if label_content["@value"] == "Identifikator" and ("gesamtkatalog" in step1["value"] or "VD1" in step1["value"]):
                bibliographic_id_single = step1["value"]
                bibliographic_id.append(bibliographic_id_single)
    if not location:    
        print("Location not found")
    if not bibliographic_id:       
        print("Bibliographic ID not found")
    if "license" in manifest:
        m.license = manifest["license"][0]
        

    #Step 2: Transforming the extracted fields into database format
    location_pattern = r'(.*)(--)(.*)'
    bibliographic_id_pattern = r'(.*\')(.*)(\'>)([A-Za-z0-9]*)( )(.*)(</a.*)'
    bibliographic_id_pattern_reduced = r'([A-Za-z0-9]*)( )(.*)'
    if location:
        location_divided = re.match(location_pattern, location)
        m.repository = location_divided.groups()[0]
        m.shelfmark = location_divided.groups()[2].lstrip()
        print(m.repository)
        print(m.shelfmark)
    if bibliographic_id:
        
        for step3 in bibliographic_id:
            bibliographic_id_individual = step3
            # Sometimes, a link to a bibliographic record is given, with the bibliographic ID being the 'friendly text' in the link; sometimes there is only a
            # string with the bibliographic ID; and in other cases a string with a provisional and essentially useless bibliographic ID that needs to be ignored
            bid = Bibliographic_id()
            if "https" in bibliographic_id_individual: #if there is a link
                bibliographic_id_divided = re.match(bibliographic_id_pattern, bibliographic_id_individual)
                bid.uri = bibliographic_id_divided.groups()[1]
                bid.name = bibliographic_id_divided.groups()[3]
                bid.id = bibliographic_id_divided.groups()[5]
            else: #if there is no link
                bibliographic_id_divided = re.match(bibliographic_id_pattern_reduced, bibliographic_id_individual)                
                bid.name = bibliographic_id_divided.groups()[0]
                bid.id = bibliographic_id_divided.groups()[2]              
#            bibliographic_id_together = (bibliographic_id_url, bibliographic_id_name, bibliographic_id_number)
            if bibliographic_id_number[-4:-2] != "-0": #If there is a hyphen in the bibliographical number, the number is not relevant 
                m.bibliographic_id.append(bid)
    print(m.license)
    print(m.repository)
    print(m.shelfmark)
    
    
    #book_properties = (repository, shelfmark, bibliographic_id_transformed, license)
 
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    canvas_label_pattern = r'(.*?)([(].*)'
    roman_numerals = {"M", "m", "D", "d", "C", "c", "X", "x", "V", "v", "I", "i", "J", "j"}    
    canvas_list = (((manifest["sequences"])[0])["canvases"])
    ###from here onward new function
    images = Canvas_parsing(canvas_list)
    #for the label (page-number) of the canvas
    m.numberOfImages = len(images)
    for im in images:
        canvas_label_divided = re.match(canvas_label_pattern, im.label_raw)         
        im.label_page = canvas_label_divided.groups()[0].strip()
        #if the canvas_label is a figure or Roman numerals only, it probably is a page number, and hence "p. " is added. If it is a figure or Roman numerals 
        #but has as last character "r" or "v", it is probably a folio number. 
        if im.label_page and (im.label_page.isnumeric() or all(characters in roman_numerals for characters in im.label_page)): 
            im.label_prefix = "p. "
        elif im.label_page and (im.label_page[0:-1].isnumeric() or all(characters in roman_numerals for characters in im.label_page[0:-1])) and (im.label_page[-1] in {"r", "v"}):
            im.label_prefix = "fol. "
        else:
            im.label_prefix = ""
    m.images = images
    
   
    return m


def Halle_parsing(URI_entered):
    #f=open(r'C:\Users\berth\Documents\Warburg\Experimente - Python\iconobase\manifest.json', 'r', encoding='utf-8')
    url = urllib.request.urlopen(URI_entered)
    manifest = json.load(url)
    #Step 1: Extracting relevant fields from the general section of the Manifest
    metadata=manifest["metadata"]
    m = Metadata()
    m.manifest = url.read()
    location = ""
    bibliographic_id = []
    bibliographic_id_number = ""
    canvas_label = ""
    for step1 in metadata:
        label = step1["label"]
        for step2 in label:
            label_content = step2
            if "@value" in label_content:
                if label_content["@value"] == "Vorlage der Digitalisierung":
                    location = step1["value"]
                    print(location)
                if label_content["@value"] == "VD-Nummer" and ("gesamtkatalog" in step1["value"] or "vd1" in step1["value"]):
                    bibliographic_id_single = step1["value"]
                    bibliographic_id.append(bibliographic_id_single)
                    print(bibliographic_id_single)
    if not location:    
        print("Location not found")
    if not bibliographic_id:       
        print("Bibliographic ID not found")
    if "license" in manifest:
        m.license = manifest["license"]
    else:     
        print("License not found")

    #Step 2: Transforming the extracted fields into database format
    location_pattern = r'([^,]*)(, )(.*)'
    bibliographic_id_pattern = r'(.*\')(.*)(\'>)([A-Za-z0-9]*)( )(.*)(</a.*)'
    bibliographic_id_pattern_reduced = r'([A-Za-z0-9]*)( )(.*)'
    if location:
        location_divided = re.match(location_pattern, location)
        m.repository = location_divided.groups()[0]
        m.shelfmark = location_divided.groups()[2]
    
    if bibliographic_id:    
        for step3 in bibliographic_id:
            bibliographic_id_individual = step3
            bid = Bibliographic_id()
            # Sometimes, a link to a bibliographic record is given, with the bibliographic ID being the 'friendly text' in the link; sometimes there is only a
            # string with the bibliographic ID; and in other cases a string with a provisional and essentially useless bibliographic ID that needs to be ignored
            if "https" in bibliographic_id_individual: #if there is a link
                bibliographic_id_divided = re.match(bibliographic_id_pattern, bibliographic_id_individual)
                bid.uri = bibliographic_id_divided.groups()[1]
                bid.name = bibliographic_id_divided.groups()[3]
                bid.id = bibliographic_id_divided.groups()[5]
            else: #if there is no link
                bibliographic_id_divided = re.match(bibliographic_id_pattern_reduced, bibliographic_id_individual)                
                bid.name = bibliographic_id_divided.groups()[0]
                bid.id = bibliographic_id_divided.groups()[2]              
            if bibliographic_id_number[-4:-2] != "-0": #If there is a hyphen in the bibliographical number, the number is not relevant 
                m.bibliographic_id.append(bid)

    
    #book_properties = (repository, shelfmark, bibliographic_id_transformed, license)
 
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    canvas_id_pattern = r'(.*)(canvas/)(.*)'
    #canvas_label_pattern = r'(.*?)([(].*)'
    #roman_numerals = {"M", "m", "D", "d", "C", "c", "X", "x", "V", "v", "I", "i", "J", "j"}
    canvas_properties = []
    canvas_list = (((manifest["sequences"])[0])["canvases"])
    images = Canvas_parsing(canvas_list)
    #for the label (page-number) of the canvas
    m.numberOfImages = len(images)

    for im in images:
        #for the label (page-number) of the canvas
        canvas_label = re.sub(r"\[.*\]", "", im.label_raw)
        if canvas_label[0:6] == "Seite ":
            im.label_prefix = "p. "
            #print(canvas_prefix + "   " + canvas_label)
            im.label_page = canvas_label[6:]
        if canvas_label[0:6] == "Blatt ":
            im.label_prefix = "fol. "
            im.label_number = canvas_label[6:]

    m.images = images
   
    return m

def Berlin_parsing(URI_entered):
    url = urllib.request.urlopen(URI_entered)
    manifest = json.load(url)
    #Step 1: Extracting relevant fields from the general section of the Manifest
    metadata=manifest["metadata"]
    m = Metadata()
    m.manifest = url.read()
    bibliographic_id = []
    for step1 in metadata:
        label = step1["label"]
        if label == "PhysicalLocation":         
            m.repository = step1["value"]
            if m.repository == "DE-1":
                m.repository = "Staatsbibliothek zu Berlin - Preußischer Kulturbesitz, Berlin, Germany"
            
        if label == "Signatur" :
            m.shelfmark = step1["value"]
        if label == "BibliographicReference":
            if type(step1["value"]) == str:                
                bibliographic_id_single = step1["value"]
            else:
                for step2 in step1["value"]:
                    value_content = step2
                    if "GW" in value_content["@value"] or "VD" in value_content["@value"] or "vd" in value_content["@value"]:
                        bibliographic_id_single = value_content["@value"]                  
            bibliographic_id.append(bibliographic_id_single)
    if not bibliographic_id:       
        print("Bibliographic ID not found")
    

    #Step 2: Transforming the extracted fields into database format
    bibliographic_id_pattern = r'(.*\')(.*)(\'>)([A-Za-z0-9]*)( )(.*)(</a.*)'
    bibliographic_id_pattern_reduced = r'([A-Za-z0-9]*)( )(.*)'
    if bibliographic_id:      
        for step3 in bibliographic_id:
            bid = Bibliographic_id()
            bibliographic_id_individual = step3
            # Sometimes, a link to a bibliographic record is given, with the bibliographic ID being the 'friendly text' in the link; sometimes there is only a
            # string with the bibliographic ID; and in other cases a string with a provisional and essentially useless bibliographic ID that needs to be ignored
            if "https" in bibliographic_id_individual: #if there is a link
                bibliographic_id_divided = re.match(bibliographic_id_pattern, bibliographic_id_individual)
                bid.uri = bibliographic_id_divided.groups()[1]
                bid.name = bibliographic_id_divided.groups()[3]
                bid.id = bibliographic_id_divided.groups()[5]
            else: #if there is no link
                bibliographic_id_divided = re.match(bibliographic_id_pattern_reduced, bibliographic_id_individual)                
                bid.name = bibliographic_id_divided.groups()[0]
                bid.id = bibliographic_id_divided.groups()[2]              
            #bibliographic_id_together = (bibliographic_id_url, bibliographic_id_name, bibliographic_id_number)
            if bid.id[-4:-2] != "-0": #If there is a hyphen in the bibliographical number, the number is not relevant 
                print(bid)
                m.bibliographic_id.append(bid)

    m.license = "https://creativecommons.org/publicdomain/mark/1.0/" #There is no license information in the manifest. I assume that this is what Berlin has for all historical digital material.
    #book_properties = (repository, shelfmark, bibliographic_id_transformed, license)
    #print("Book properties: ")
    #print(book_properties)
    
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format

    canvas_label_pattern = r'(.*?)(\[.*)'
    roman_numerals = {"M", "m", "D", "d", "C", "c", "X", "x", "V", "v", "I", "i", "J", "j"}
    canvas_list = (((manifest["sequences"])[0])["canvases"])
    images = Canvas_parsing(canvas_list)
    #for the label (page-number) of the canvas
    m.numberOfImages = len(images)

    for im in images:
        
        #for the label (page-number) of the canvas
        
        canvas_label_long_divided = re.match(canvas_label_pattern, im.label_raw)
        im.label_page = canvas_label_long_divided.groups()[0].strip()
        #if the canvas_label is a figure or Roman numerlas only, it probably is a page number, and hence "p. " is added. If it is a figure or Roman numerals 
        #but has as last character "r" or "v", it is probably a folio number. 
        if im.label_page and (im.label_page.isnumeric() or all(characters in roman_numerals for characters in im.label_page)): 
            im.label_prefix = "p. "
        elif im.label_page and (im.label_page[0:-1].isnumeric() or all(characters in roman_numerals for characters in im.label_page[0:-1])) and (im.label_page[-1] in {"r", "v"}):
            im.label_prefix = "fol. "
        else:
            im.label_prefix = ""        
        #for the URI of the image file
        
        m.images = images
   
    return m


def Cambridge_Trinity_parsing(URI_entered):
    url = urllib.request.urlopen(URI_entered)
    manifest = json.load(url)
    #Step 1: Extracting relevant fields from the general section of the Manifest
    #Step 2: Transforming the extracted fields into database format (here done together with step 1 because it is very little to do)
    metadata=manifest["metadata"]
    m = Metadata()
    m.manifest = url.read()
    repository = ""
    shelfmark = ""

    bibliographic_id_transformed = []
    bibliographic_id_name = ""
    bibliographic_id_number = ""
    catalogue_address_pattern = r"(<a href=')([^<]*)('>View Record</a>)"
    canvas_prefix = ""
    canvas_label = ""
    for step1 in metadata:
        label = step1["label"]
        if label == "Catalogue":
            catalogue_address_long = step1["value"]
            catalogue_address_divided = re.match(catalogue_address_pattern, catalogue_address_long)
            catalogue_address = catalogue_address_divided[2]
#            print(catalogue_address)
            catalogue_entry = urllib.request.urlopen(catalogue_address)
            catalogue_raw = catalogue_entry.read()
            tree = etree.HTML(catalogue_raw)
            try: 
                catalogue_text = etree.tostring(tree,encoding=str)
            except TypeError:
              return
            bibliography_pattern_list = (r'ESTC, .*?<', r'ISTC, .*?<')
            bibliography_pattern_single = r'([\w]*)(, )([\w]*)(<)'
            for bibliographic_reference in bibliography_pattern_list:
                bibliography_found = re.findall(bibliographic_reference, catalogue_text)
                for single_bibliography in bibliography_found:
                    bid = Bibliographic_id()
                    bibliographic_id_divided = re.match(bibliography_pattern_single, single_bibliography)
                    bid.name = bibliographic_id_divided[1]
                    bid.id = bibliographic_id_divided[3]
                   
                    m.bibliographic_id.append(bid)               
    m.repository = manifest["attribution"]
    m.shelfmark = manifest["label"]
    m.license = manifest["license"]
    #book_properties = (repository, shelfmark, bibliographic_id_transformed, license)
     
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    #canvas_id_pattern1 = r'([^%].*)(%)(.*)'
    #canvas_id_pattern2 = r'(https://mss-cat.trin.cam.ac.uk/manuscripts/)(.*)'
    canvas_properties = []
    canvas_list = (((manifest["sequences"])[0])["canvases"])
    images = Canvas_parsing(canvas_list)    
    m.numberOfImages = len(images)
    for im in images:      
        #for the ID number of the canvas
        #for the label (page-number) of the canvas
        canvas_label = im.label_raw
        if canvas_label[0] == "f":
            im.label_prefix = "fol."
            im.label_page = (canvas_label[1:]).strip("0")
        if canvas_label[0] == "p":
            im.label_prefix = "p."
            im.labe_page = (canvas_label[1:]).istc("0")
    
    m.images = images

    return m

    
    


def ThULB_parsing(URI_entered):
    # This function is for all JSON-manifests produced by the Jena library, this includes manifests from Erfurt and Gotha. 

    url = urllib.request.urlopen(URI_entered)
    manifest = json.load(url)
    m = Metadata()
    m.manifest = url.read()
    #Step 1/2: Extracting relevant fields from the general section of the Manifest and bringing them to database format
    # The manifest contains hardly any data. Each individual canvas, however, has its own URN that is part of the label field
    # One can extract this URN, remove the two last groups of digits, send it to the URN-resolver of the DNB, and receive
    # the HTML of a catalogue page. 
    # Attention: the canvas_ID apparently does not give a sequential number (canvasses with 0000 in the number can be at the start or the end)

   
    canvas_label_pattern = r'([\w].*?)?( - )?(urn[\w:-].*)(-[\d]{1,8}-[\d]{1,4})'
    shelfmark1_long_pattern = r'>[^<>]*?\(Zitierform\)<'
    shelfmark2_pattern = r'(Signatur\(en\):<[^<>]*?>\n<[^<>]*?">\n<[^<>]*?>)(.*?)(<)'
    #repertory_long_pattern = r'Standort:<[^<>]*?>\n<[^<>]*?>\n<[^<>]*?>[^<>]*?<[^<>]*?>'
    #repository_pattern = r'(Standort:<[^<>]*?>\n<[^<>]*?>\n<[^<>]*?>)([^<>]*?)(<[^<>]*?>)'
    repository_pattern = r'(besitzende Institution:<[^<>]*?>\n<[^<>]*?>\n<[^<>]*?>\n<[^<>]*?>\n<[^<>]*?>)([^<>]*?)(<[^<>]*?>)'
    licence_pattern = r'"https://creativecommons[^"]*?"'
    bibliographic_reference_pattern = r'(GW-Nummer|VD16|VD17|VD18)(:<[^<>]*?>\n<[^<>]*?>)([^<>]*?)<'
    canvas_label_long = ((((manifest["sequences"])[0])["canvases"])[0])["label"]
    urn = re.match(canvas_label_pattern, canvas_label_long)[3]    
    urn_full = r"http://nbn-resolving.org/" + urn
    catalogue_page = requests.get(urn_full)  
    catalogue_text = catalogue_page.text
    repository_divided = re.findall(repository_pattern, catalogue_text, re.MULTILINE)[0]
    repository = repository_divided[1]


    if "Zitierform" in catalogue_text: #Sometimes, two versions of the shelf mark are given, then the one marked 'Zitierform' is to be used. 
        shelfmark_long = re.findall(shelfmark1_long_pattern, catalogue_text)
        m.shelfmark = (shelfmark_long[0])[1:-1]
    else:        
        shelfmark_divided = re.findall(shelfmark2_pattern, catalogue_text, re.MULTILINE)[0]
        m.shelfmark = shelfmark_divided[1]
    if m.shelfmark[0:11] == "UB Erfurt, ": #This is added because, for mysterious versions, Erfurt University Library repeats its name at this place
        m.shelfmark = m.shelfmark[11:]
    m.license = (re.findall(licence_pattern, catalogue_text)[0])[1:-1]


    if "GW-Nummer:" in catalogue_text or "VD16:" in catalogue_text or "VD17:" in catalogue_text or "VD18:" in catalogue_text:
    #are there ever multiple IDs? If so, one would need a loop
        bid = Bibliographic_id()
        bibliography_long = re.findall(bibliographic_reference_pattern, catalogue_text, re.MULTILINE)[0]
        print(bibliography_long)
        bid.name = bibliography_long[0]
        bid.id = bibliography_long[2]
        if bid.id[0:3] == "VD1": #Sometimes, the 'VD17' or something similar is repeated before the number
            bid.id = bid.id[5:]
    #bibliographic_id_together = ("", bibliographic_id_name, bibliographic_id_number)
    #m.bibliographic_id.append(bid)
    #book_properties = (repository, shelfmark, bibliographic_id_transformed, license)
    #print(book_properties)
        m.bibliographic_id.append(bid)

    
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    #Apparently, canvasses standing for bindings do not have an ID field consisting of a number, but two fields, the first being "0000", the second a number.
    #canvas_id_pattern1 = r'(.*?)_(0000_[\d]{2,5}.*).tif'
    #canvas_id_pattern2 = r'(.*)_([\d]{2,5}).tif'

    roman_numerals = {"M", "m", "D", "d", "C", "c", "X", "x", "V", "v", "I", "i", "J", "j"}
   
    canvas_list = (((manifest["sequences"])[0])["canvases"])
    images = Canvas_parsing(canvas_list)    
    m.numberOfImages = len(images)
    for im in images:
         #for the label (page-number) of the canvas
        canvas_label_long = im.label_raw
        canvas_label_long_divided = re.match(canvas_label_pattern, canvas_label_long)
        if canvas_label_long_divided[1]:
            im.label_page = canvas_label_long_divided[1].strip()
        #if the canvas_label is a figure or Roman numerlas only, it probably is a page number, and hence "p. " is added. If it is a figure or Roman numerals 
        #but has as last character "r" or "v", it is probably a folio number. 
        if im.label_page and (im.label_page.isnumeric() or all(characters in roman_numerals for characters in im.label_page)): 
            im.label_prefix = "p. "
        elif im.label_page and (im.label_page[0:-1].isnumeric() or all(characters in roman_numerals for characters in im.label_page[0:-1])) and (im.label_page[-1] in {"r", "v"}):
            im.label_prefix = "fol. "
        else:
            im.label_prefix = ""        
        #for the URI of the image file
    m.images = images
   
    return m

def SLUB_parsing(URI_entered):
    #f=open(r'C:\Users\berth\Documents\Warburg\Experimente - Python\iconobase\manifest.json', 'r', encoding='utf-8')
    url = urllib.request.urlopen(URI_entered)
    manifest = json.load(url)
    #Step 1/2: Extracting relevant fields from the general section of the Manifest and parsing them
    metadata=manifest["metadata"]
    m = Metadata()
    m.manifest = url.read()
    licence_pattern = r'(<[^<>].*>)(.*?)(<[^<>].*><[^<>].*>)'
    repository_pattern = r'(<[^<>]*><[^<>]*><[^<>]*><[^<>]*>)(.*?)(<.*)'

    for step1 in metadata:
        bid = Bibliographic_id()
        label = step1["label"]
        if label == "Signatur":
            m.shelfmark = step1["value"]
        if label == "Rechteinformationen":
            licence_long = step1["value"]
            m.license = re.match(licence_pattern, licence_long)[2]
            #print(licence)
        # Bei den wenigen digitalisierten Inkunabeln fehlen anscheinend die GW-Nummern. 
        if label == "VD16-Nummer":
            bid.name = "VD16"
            bid.id = step1["value"]
            if bid.id[0:4] == "VD16":
                bid.id = bid.id[5:]
            m.bibliographic_id.append(bid)
        if label == "VD17-Nummer":
            bid.name = "VD17"
            bid.id = step1["value"]
            if bid.id[0:4] == "VD17":
                bid.id = bid.id[5:]
            m.bibliographic_id.append(bid)
        if label == "VD18-Nummer":
            bid.name = "VD18"
            bid.id = step1["value"]
            if bid.id[0:4] == "VD18":
                bid.id = bid.id[5:]
            m.bibliographic_id.append(bid)
        
    
    attribution = manifest["attribution"]
    m.repository = re.match(repository_pattern, attribution)[2]

    
 
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    canvas_id_pattern = r'(.*)(canvas/)(.*)'
    canvas_label_pattern = r'(.*?)([(].*)'
    roman_numerals = {"M", "m", "D", "d", "C", "c", "X", "x", "V", "v", "I", "i", "J", "j"}
    canvas_properties = []
    canvas_list = (((manifest["sequences"])[0])["canvases"])
    images = Canvas_parsing(canvas_list)    
    m.numberOfImages = len(images)
    
    for im in images:
        #for the label (page-number) of the canvas
        canvas_label_long = im.label_raw
        if canvas_label_long == "Seite  - ": #this is the default if no pagination is given
            im.label_page = ""
        if canvas_label_long[0:6] == "Seite ":
            im.label_page = canvas_label_long[6:]
        
        #if the canvas_label is a figure or Roman numerlas only, it probably is a page number, and hence "p. " is added. If it is a figure or Roman numerals 
        #but has as last character "r" or "v", it is probably a folio number. 
        if im.label_page and (im.label_page.isnumeric() or all(characters in roman_numerals for characters in im.label_page)): 
            im.label_prefix = "p. "
        elif im.label_page and (im.label_page[0:-1].isnumeric() or all(characters in roman_numerals for characters in im.label_page[0:-1])) and (canvas_label[-1] in {"r", "v"}):
            im.label_prefix = "fol. "
    m.images = images

   
    return m

def Cambridge_Corpus_parsing(URI_entered):
    # Since currently no printed books from Corpus have been digitised on this platform, this function deals with manuscripts only. 
    url = urllib.request.urlopen(URI_entered)
    manifest = json.load(url)
    m = Metadata()
    m.manifest = url.read()
    #Step 1: Extracting relevant fields from the general section of the Manifest
    

    repository = ""
    shelfmark = ""
    canvas_prefix = ""
    canvas_label = ""
    
    label = (manifest["label"])[38:] #cutting out the name of the library
    if 'license' in manifest:
        m.license = manifest["license"]
    else:
        m.license = "https://creativecommons.org/licenses/by-nc/4.0/" 
        #I assume this is the default license for the Parker MSS, but it is not always indicated in the correct field
    

    #Step 2: Transforming the extracted fields into database format
    m.repository = "Corpus Christi College Cambridge, Parker Library"
    label_pattern = r'(.*)(:)(.*)'
    label_divided = re.match(label_pattern, label)
    m.shelfmark = "MS " + (label_divided[1]).lstrip("0")
    
 
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    

    canvas_properties = []
    canvas_list = (((manifest["sequences"])[0])["canvases"])
    images = Canvas_parsing(canvas_list)    
    m.numberOfImages = len(images)
    for im in images:
        #for the label (page-number) of the canvas
        canvas_label = im.label_raw
        if canvas_label[0] == "f":
            im.label_prefix = "fol."
            im.label_page = (canvas_label[2:]).lstrip("0")
        if canvas_label[0] == "p":
            im.label_prefix = "p."
            im.label_page = (canvas_label[2:]).lstrip("0")
    m.images = images
     
        
   
    return m


def Leipzig_parsing(URI_entered):
    url = urllib.request.urlopen(URI_entered)
    manifest = json.load(url)
    #Step 1/2: Extracting relevant fields from the general section of the Manifest and parsing them
    metadata=manifest["metadata"]
    m = Metadata()
    m.manifest = url.read()

    for step1 in metadata:
        label = step1["label"]
        bid = Bibliographic_id()
        if label == "Call number": #sometimes, a German, sometimes an English term isused
            m.shelfmark = step1["value"]
        if label == "Signatur":
            m.shelfmark = step1["value"]
        if label == "Owner":
            m.repository = step1["value"]
        # Bei den wenigen digitalisierten Inkunabeln fehlen anscheinend die GW-Nummern. 
        if label == "VD16":
            bid.name = "VD16"
            bid.id = step1["value"]
            if bid.id[0:4] == "VD16":
                bid.id = bid.id[5:]
            m.bibliographic_id.append(bid)
        if label == "VD17":
            bid.name = "VD17"
            bid.id = step1["value"]
            if bid.id[0:4] == "VD17":
                bid.id = bid.id[5:]
            m.bibliographic_id.append(bid)
        if label == "VD18":
            bid.name = "VD18"
            bid.id = step1["value"]
            if bid.id[0:4] == "VD18":
                bid.id = bid.id[5:]
            m.bibliographic_id.append(bid)
        m.license = manifest["license"]
        # The field 'owner' is not used for manuscripts. Since apparently all digitised manuscripts in the system are from Leipzig,
        # one can simply doublecheck that the name of the library appears in the 'label' and then use it. 
        # Should at some point manuscripts from other collections be described here, one would have to change that. 
        if m.repository == "" and manifest["label"][0:40] == "Leipzig, Universitätsbibliothek Leipzig,":
            m.repository = "Universitätsbibliothek Leipzig"

 
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    canvas_id_pattern = r'(.*)(canvas/)(.*)'
    roman_numerals = {"M", "m", "D", "d", "C", "c", "X", "x", "V", "v", "I", "i", "J", "j"}
    canvas_properties = []
    canvas_list = (((manifest["sequences"])[0])["canvases"])
    images = Canvas_parsing(canvas_list)    
    m.numberOfImages = len(images)

    for im in images:
        #for the label (page-number) of the canvas
        canvas_label_long = im.label_raw
        if canvas_label_long == "-": #this is the default if no pagination is given
            pass
        else:
            im.label_page = canvas_label_long
        #if the canvas_label is a figure or Roman numerlas only, it probably is a page number, and hence "p. " is added. If it is a figure or Roman numerals 
        #but has as last character "r" or "v", it is probably a folio number. 
        if im.label_page and (im.label_page.isnumeric() or all(characters in roman_numerals for characters in im.label_page)): 
            im.label_prefix = "p. "
        elif im.label_page and (im.label_page[0:-1].isnumeric() or all(characters in roman_numerals for characters in im.label_page[0:-1])) and (im.label_page[-1] in {"r", "v"}):
            im.label_prefix = "fol. "
    m.images = images
    return m
