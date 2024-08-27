#pylint: disable=C0301, C0303, C0116, C0325, C0103
"""
This module contains a number of function that accept the URI of an IIIF manifest of a manuscript 
or book and return data, both on the manuscript or book as a whole (book_properties) and on the 
individual canvases(canvas_properties). Because much information in the manifests is not standardised, 
there has to be a separate function for each library. 
"""

import urllib.request
import json
import re
import xml.etree.ElementTree
import requests
from lxml import etree
import classes
import parse_canvas

@classes.func_logger
def parse_manifests_bsb(manifest):
    #f=open(r'C:\Users\berth\Documents\Warburg\Experimente - Python\iconobase\manifest.json', 'r', encoding='utf-8')

    #Step 1: Extracting relevant fields from the general section of the Manifest
    metadata=manifest["metadata"]
#    print("initialising beanie")
#    c=db_actions.get_database()
    #print(metadata)
    m = classes.Metadata()
    repository = classes.Organisation()
#    m.manifest =  url.read()
 #   print("url"+uri_entered)
    location = ""
    bibliographic_id = []
#    bibliographic_id_url = ""
#    bibliographic_id_name = ""
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
        repository.name = location_divided.groups()[0]
        repository.role = "col"
        m.repository.append(repository)
        m.shelfmark = location_divided.groups()[2].lstrip()
        print(m.repository[0].name)
        print(m.shelfmark)

        
    if bibliographic_id:
        
        for step3 in bibliographic_id:
            bibliographic_id_individual = step3
            # Sometimes, a link to a bibliographic record is given, with the bibliographic ID being the 'friendly text' in the link; sometimes there is only a
            # string with the bibliographic ID; and in other cases a string with a provisional and essentially useless bibliographic ID that needs to be ignored
            bid =classes.BibliographicId()
            if "https" in bibliographic_id_individual: #if there is a link
                print(bibliographic_id_individual)
                bibliographic_id_divided = re.match(bibliographic_id_pattern, bibliographic_id_individual)
                print(bibliographic_id_divided)
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
    print(m.repository[0].name)
    print(m.shelfmark)
    
    
    #book_properties = (repository, shelfmark, bibliographic_id_transformed, license)
 
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    canvas_label_pattern = r'(.*?)([(].*)'
    roman_numerals = {"M", "m", "D", "d", "C", "c", "X", "x", "V", "v", "I", "i", "J", "j"}    
    canvas_list = (((manifest["sequences"])[0])["canvases"])
    ###from here onward new function
    images = parse_canvas.parse_canvas(canvas_list)
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

@classes.func_logger
def parse_manifest_halle(URI_entered):
    #f=open(r'C:\Users\berth\Documents\Warburg\Experimente - Python\iconobase\manifest.json', 'r', encoding='utf-8')
    url = urllib.request.urlopen(URI_entered)
    manifest = json.load(url)
    #Step 1: Extracting relevant fields from the general section of the Manifest
    metadata=manifest["metadata"]
    m = classes.Metadata()
    m.manifest = url.read()
    repository = classes.Organisation()
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
        repository.name = location_divided.groups()[0]
        repository.role = "col"
        m.repository.append(repository)
        m.shelfmark = location_divided.groups()[2]
    
    if bibliographic_id:    
        for step3 in bibliographic_id:
            bibliographic_id_individual = step3
            bid = classes.BibliographicId()
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
    images = parse_canvas.parse_canvas(canvas_list)
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

@classes.func_logger
def parse_manifest_berlin(URI_entered):
    url = urllib.request.urlopen(URI_entered)
    manifest = json.load(url)
    #Step 1: Extracting relevant fields from the general section of the Manifest
    classes.Metadata=manifest["classes.Metadata"]
    m = classes.Metadata()
    repository = classes.Organisation()
    m.manifest = url.read()
    bibliographic_id = []
    for step1 in classes.Metadata:
        label = step1["label"]
        if label == "PhysicalLocation":         
            repository.name = step1["value"]
            if repository.name == "DE-1":
                repository.name = "Staatsbibliothek zu Berlin - Preußischer Kulturbesitz, Berlin, Germany"
            repository.role = "col"
            m.repository.append(repository)
            
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
            bid = classes.BibliographicId()
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
    images =parse_canvas.parse_canvas(canvas_list)
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

@classes.func_logger
def parse_manifest_cambridge_trinity(URI_entered):
    url = urllib.request.urlopen(URI_entered)
    manifest = json.load(url)
    #Step 1: Extracting relevant fields from the general section of the Manifest
    #Step 2: Transforming the extracted fields into database format (here done together with step 1 because it is very little to do)
    classes.Metadata=manifest["classes.Metadata"]
    m = classes.Metadata()
    m.manifest = url.read()
    repository = classes.Organisation()
    shelfmark = ""

    bibliographic_id_transformed = []
    bibliographic_id_name = ""
    bibliographic_id_number = ""
    catalogue_address_pattern = r"(<a href=')([^<]*)('>View Record</a>)"
    canvas_prefix = ""
    canvas_label = ""
    for step1 in classes.Metadata:
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
                    bid = classes.BibliographicId()
                    bibliographic_id_divided = re.match(bibliography_pattern_single, single_bibliography)
                    bid.name = bibliographic_id_divided[1]
                    bid.id = bibliographic_id_divided[3]
                   
                    m.bibliographic_id.append(bid)               
    repository.name = manifest["attribution"]
    repository.role = "col"
    m.repository.append(repository)
    m.shelfmark = manifest["label"]
    m.license = manifest["license"]
    #book_properties = (repository, shelfmark, bibliographic_id_transformed, license)
     
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    #canvas_id_pattern1 = r'([^%].*)(%)(.*)'
    #canvas_id_pattern2 = r'(https://mss-cat.trin.cam.ac.uk/manuscripts/)(.*)'
    canvas_properties = []
    canvas_list = ((manifest["sequences"])[0])["canvases"]
    images = parse_canvas.parse_canvas(canvas_list)    
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

    
    

@classes.func_logger
def parse_manifest_thulb(URI_entered):
    # This function is for all JSON-manifests produced by the Jena library, this includes manifests from Erfurt and Gotha. 

    url = urllib.request.urlopen(URI_entered)
    manifest = json.load(url)
    m = classes.Metadata()
    repository = classes.Organisation()
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
    repository.name = repository_divided[1]
    repository.role = "col"
    m.repository.append(repository)


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
        bid =classes.BibliographicId()
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
   
    canvas_list = ((manifest["sequences"])[0])["canvases"]
    images = parse_canvas.parse_canvas(canvas_list)
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

@classes.func_logger
def parse_manifest_slub(uri_entered):
    """
\todo
    """
    #f=open(r'C:\Users\berth\Documents\Warburg\Experimente - Python\iconobase\manifest.json', 'r', encoding='utf-8')
    url = urllib.request.urlopen(uri_entered)
    manifest = json.load(url)
    #Step 1/2: Extracting relevant fields from the general section of the Manifest and parsing them
    classes.Metadata=manifest["classes.Metadata"]
    m = classes.Metadata()
    repository = classes.Organisation()
    m.manifest = url.read()
    licence_pattern = r'(<[^<>].*>)(.*?)(<[^<>].*><[^<>].*>)'
    repository_pattern = r'(<[^<>]*><[^<>]*><[^<>]*><[^<>]*>)(.*?)(<.*)'

    for step1 in classes.Metadata:
        bid = classes.BibliographicId()
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
    repository.name = re.match(repository_pattern, attribution)[2]
    repository.role = "col"
    m.repository.append(repository)

    
 
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    canvas_id_pattern = r'(.*)(canvas/)(.*)'
    canvas_label_pattern = r'(.*?)([(].*)'
    roman_numerals = {"M", "m", "D", "d", "C", "c", "X", "x", "V", "v", "I", "i", "J", "j"}
    canvas_properties = []
    canvas_list = ((manifest["sequences"])[0])["canvases"]
    images = parse_canvas.parse_canvas(canvas_list)    
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
        elif im.label_page and (im.label_page[0:-1].isnumeric() or all(characters in roman_numerals for characters in im.label_page[0:-1])) and (im.label_page[-1] in {"r", "v"}):
            im.label_prefix = "fol. "
    m.images = images

   
    return m

@classes.func_logger
def parse_manifest_cambridge_corpus(uri_entered):
    """
Since currently no printed books from Corpus have been digitised on this platform, this function deals with manuscripts only. 
    """
    url = urllib.request.urlopen(uri_entered)
    manifest = json.load(url)
    m = classes.Metadata()
    repository = classes.Organisation()
    m.manifest = url.read()
    #Step 1: Extracting relevant fields from the general section of the Manifest
    

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
    repository.name = "Corpus Christi College Cambridge, Parker Library"
    repository.role = "col"
    m.repository.append(repository)
    label_pattern = r'(.*)(:)(.*)'
    label_divided = re.match(label_pattern, label)
    m.shelfmark = "MS " + (label_divided[1]).lstrip("0")
    
 
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    

    canvas_properties = []
    canvas_list = ((manifest["sequences"])[0])["canvases"]
    images = parse_canvas.parse_canvas(canvas_list)
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


@classes.func_logger
def parse_manifest_leipzig(uri_entered):
    """
\todo
    """
    url = urllib.request.urlopen(uri_entered)
    manifest = json.load(url)
    #Step 1/2: Extracting relevant fields from the general section of the Manifest and parsing them
    classes.Metadata=manifest["classes.Metadata"]
    m = classes.Metadata()
    repository = classes.Organisation()
    m.manifest = url.read()

    for step1 in classes.Metadata:
        label = step1["label"]
        bid = classes.BibliographicId()
        if label == "Call number": #sometimes, a German, sometimes an English term isused
            m.shelfmark = step1["value"]
        if label == "Signatur":
            m.shelfmark = step1["value"]
        if label == "Owner":
            repository.name = step1["value"]
            repository.role = "col"
            m.repository.append(repository)
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
        if repository.name == "" and manifest["label"][0:40] == "Leipzig, Universitätsbibliothek Leipzig,":
            repository.name = "Universitätsbibliothek Leipzig"
            repository.role = "col"
            m.repository.append(repository)

 
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    canvas_id_pattern = r'(.*)(canvas/)(.*)'
    roman_numerals = {"M", "m", "D", "d", "C", "c", "X", "x", "V", "v", "I", "i", "J", "j"}
    canvas_properties = []
    canvas_list = ((manifest["sequences"])[0])["canvases"]
    images = parse_canvas.parse_canvas(canvas_list)    
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

@classes.func_logger
def parse_manifest_gallica(URI_entered):
    # This function works only on the manifests from Gallica proper, not on external manifests shown here (hence it works on the BnF, Arsenal, and very few other libraries)
    # Unfortunately, references to bibliographical reportories are not really standardised in Gallica, they can appear in at least four different places. 
    # Hence, this section is messy,a nd it probably needs a number of additions. 
    #f=open(r'C:\Users\berth\Documents\Warburg\Experimente - Python\iconobase\manifest.json', 'r', encoding='utf-8')
    url = urllib.request.urlopen(URI_entered)
    manifest = json.load(url)
    #Step 1: Extracting relevant fields from the general section of the Manifest
    classes.Metadata=manifest["classes.Metadata"]
    m = classes.Metadata()
    repository = classes.Organisation()
    m.manifest = url.read()
    licence_pattern = r'(<[^<>].*>)(.*?)(<[^<>].*><[^<>].*>)'
    shelfmark_pattern = r'([^,.]*)?[,.]?([^,.]*)?[,.]?(.*)'
    catalogue_reference = ""
    bibliographical_references = []
    format = ""
    m.license = manifest["license"]
    for step1 in classes.Metadata:
        bid = classes.BibliographicId()
        label = step1["label"]
        if label == "Shelfmark":
            shelfmark_long = step1["value"]
        if label == "Repository":
            if step1["value"]: # Oddly, this field seems to be sometimes empty, but it still has a label. 
                repository.name = step1["value"]
                repository.role = "col"
                m.repository.append(repository)
        if label == "Relation":
            print(step1["value"][0:46])
            if step1["value"][0:46] == r"Notice du catalogue : http://catalogue.bnf.fr/":
                catalogue_reference = step1["value"][46:] #only the identificator, not the start of the URN
        if label == "Format" and len(step1["value"]) == 2: # Sometimes, a bibliographical reference is added to the indication of the format - no idea, why
            # In these cases, there are 2 records linked to format. 
            format = step1["value"][0]["@value"]

# Step 2: Parsing the shelf mark and format sections
    shelfmark_divided = re.match(shelfmark_pattern, shelfmark_long)
    if shelfmark_divided[3]: # most shelfmark lines consist of three elements, but some only have two. The last first is (again) the repository, the last the shelfmark,#
        #the middle one a department of the BnF that I can ignore here. 
        m.shelfmark = shelfmark_divided[3].strip()
        if shelfmark_divided[2][0:7].strip() == "Biblio": # this is the for the Bibliothèque de l'Arsenal, which is treated as department of the BnF
            repository.name = shelfmark_divided[2].strip()
        else: 
            repository.name = shelfmark_divided[1].strip()
    elif shelfmark_divided[2]:
        m.shelfmark = shelfmark_divided[2].strip()
        repository.name = shelfmark_divided[1].strip()
    repository.role = "col"
    if len(m.repository) == 0: #This is only added if the field repository is empty
        m.repository.append(repository)

    if "(" in format:
        format_bibliography = re.search(r'\(.*\)', format).group(0)[1:-2]
        format_bibliography = format_bibliography.replace(",", "", 1) # In this case, there is a comma after the title of the reference work, in other cases not
        if "; " in format_bibliography:
            #print("format_bibliography split")
            bibliographical_references =  format_bibliography.split("; ")
        else: 
            bibliographical_references.append(format_bibliography)


    if catalogue_reference:
        record_url = r"http://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&query=(bib.persistentid%20any%20%22" + catalogue_reference + r"%22)"
        print(record_url)
        good_record = False
        url = urllib.request.urlopen(record_url)
        tree = xml.etree.ElementTree.parse(url)
        root = tree.getroot()
        record = root[3][0][2][0]
        for step1 in record:
            match step1.get('tag'):
                case "210":# In some cases, this field seems to be used for bibliographical records
                    for step2 in step1:
                        record_210 = step2.text
                        if "Hain-Copinger" in record_210:
                            bid = classes.BibliographicId()
                            hc_found = re.search(r'Hain-Copinger, \w*', record_210)
                            if hc_found:
                                bid.name = "HC"
                                bid.id = hc_found.group(0)[14:].strip()
                                m.bibliographic_id.append(bid)
                        if "Pellechet" in record_210:
                            bid = classes.BibliographicId()
                            hc_found = re.search(r'Pellechet, \w*', record_210)
                            if hc_found:
                                bid.name = "Pell Ms"
                                bid.id = hc_found.group(0)[10:].strip()
                                m.bibliographic_id.append(bid)
                            

                case "300": # This field seems to be not so commonly used for bibliographical records
                    for step2 in step1:
                        match step2.get("code"):
                            case "a":
                                record_300 = step2.text
                                if "ISTC" in record_300 or "istc" in record_300 or "GW" in record_300 or "gesamtkatalogderwiegendrucke" in record_300:                                   
                                    print("field 300: " + record_300)
                                    record_300 = record_300.replace("n°", "")
                                    record_300 = record_300.replace("  ", " ")                                    
                                    bid = classes.BibliographicId()
                                    istc_long_found = re.search(r'https\://data\.cerl\.org/istc/i\w\d{8}', record_300)
                                    if istc_long_found:
                                        print("ISTC URL found in 300")
                                        bid.name = "ISTC"
                                        bid.id = istc_long_found.group(0)[27:37]
                                        print("ISTC found in 300: "+ bid.id)
                                        good_record = True
                                        m.bibliographic_id.append(bid)
                                    gw_long_found = re.search(r'https\://www\.gesamtkatalogderwiegendrucke\.de/docs/\w*', record_300)
                                    if gw_long_found:
                                        print("GW URL found in 300")
                                        bid.name = "GW"
                                        print(gw_long_found.group(0))
                                        bid.id = gw_long_found.group(0)[49:]
                                        good_record = True
                                        m.bibliographic_id.append(bid)
                                    istc_found = re.search(r"ISTC i[a-z]\d{8}", record_300)
                                    if istc_found:
                                        bid.name = "ISTC"
                                        bid.id = istc_found.group(0)[5:]
                                        good_record = True
                                        m.bibliographic_id.append(bid)
                                    gw_found = re.search(r"GW [\w]*", record_300)
                                    if gw_found:
                                        print("GW found in 300")
                                        bid.name = "GW"
                                        bid.id = gw_found.group(0)[3:]
                                        good_record = True
                                        m.bibliographic_id.append(bid)
                                    
                case "321": # In most cases, it seems, bibliographical references are here, in a relatively ordered list
                    for step2 in step1:
                        match step2.get("code"):
                            case "a":
                                if "ISTC" in step2.text or "istc" in step2.text or "gesamtkatalogderwiegendrucke" in step2.text or "GW" in step2.text or "VD16" in step2.text:
                                    good_record = True # I need this for later - I only check for other catalogues, if good_record is false. 
                                if ". - " in step2.text:
                                    bibliographical_references =  step2.text.split(". - ")
                                elif "; " in step2.text:
                                    bibliographical_references =  step2.text.split("; ")        
                                else: 
                                    bibliographical_references.append(step2.text)
        if bibliographical_references:
            for bibref in bibliographical_references:
                bid = classes.BibliographicId()
                bibref = bibref.replace("n°", "")
                print(bibref)
                if bibref[0:4] == "ISTC":
                    bid.name = "ISTC"
                    bid.id = bibref[4:].strip()
                    m.bibliographic_id.append(bid)
                if bibref[0:2] == "GW":
                    bid.name = "GW"
                    bid.id = bibref[3:].strip()
                    m.bibliographic_id.append(bid)
                if bibref[0:4] == "VD16": 
                    bid.name = "VD16"
                    bid.id = bibref[4:].strip()              
                    m.bibliographic_id.append(bid)
                if bibref[0:4] == "VD17": 
                    bid.name = "VD17"
                    bid.id = bibref[4:].strip()
                    m.bibliographic_id.append(bid)
                if bibref[0:4] == "VD18": 
                    bid.name = "VD18"
                    bid.id = bibref[4:].strip()
                    m.bibliographic_id.append(bid)
                if bibref[0:49] == "https://www.gesamtkatalogderwiegendrucke.de/docs/":
                    bid.name = "GW"
                    bid.id = bibref[49:].strip()
                    m.bibliographic_id.append(bid)                    
                if bibref[0:27] == "https://data.cerl.org/istc/im00626000":
                    bid.name = "ISTC"
                    bid.id = bibref[27:37].strip()
                    m.bibliographic_id.append(bid)


                if good_record is False: # I check the following only, if I don't have any standard bibliographic ID
                    if bibref[0:13] == "Hain-Copinger":
                        bid.name = "HC"
                        bid.id = bibref[13:].strip()
                        m.bibliographic_id.append(bid)
                    if bibref[0:2] == "HC":
                        bid.name = "HC"
                        bid.id = bibref[2:].strip()
                        m.bibliographic_id.append(bid)
                    if bibref[0:4] == "Goff":
                        bid.name = "Goff"
                        bid.id = bibref[4:].strip().replace("-", "", 1)
                        m.bibliographic_id.append(bid)
                    if bibref[0:4] == "Pell":
                        bid.name = "Pell Ms"
                        bid.id = bibref[4:]
                        m.bibliographic_id.append(bid)
                    if bibref[0:9] == "Pellechet":
                        bid.name = "Pell Ms"
                        bid.id = bibref[9:]
                        m.bibliographic_id.append(bid)
                    if bibref[0:4] == "CIBN":
                        bid.name = "CIBN"
                        bid.id = bibref[4:]
                        m.bibliographic_id.append(bid)
                    if bibref[0:2] == "C ":
                        bid.name = "C"
                        bid.id = bibref[2:]
                        m.bibliographic_id.append(bid)
                    if bibref[0:8] == "Copinger":
                        bid.name = "C"
                        bid.id = bibref[8:]
                        m.bibliographic_id.append(bid)
            print(m.bibliographic_id)
                



    
 
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    canvas_id_pattern = r'(.*)(canvas/)(.*)'
    canvas_label_pattern = r'(.*?)([(].*)'
    roman_numerals = {"M", "m", "D", "d", "C", "c", "X", "x", "V", "v", "I", "i", "J", "j"}
    canvas_properties = []
    canvas_list = ((manifest["sequences"])[0])["canvases"]
    images = parse_canvas.parse_canvas(canvas_list)    
    m.numberOfImages = len(images)
    
    for im in images:
        #for the label (page-number) of the canvas
        canvas_label_long = im.label_raw
        if canvas_label_long == "NP": #this is the default if no pagination is given
            im.label_page = ""
        else:
            im.label_page = canvas_label_long #Since paris does not seem to give any prefixes
        
        #if the canvas_label is a figure or Roman numerlas only, it probably is a page number, and hence "p. " is added. If it is a figure or Roman numerals 
        #but has as last character "r" or "v", it is probably a folio number. 
        if im.label_page and (im.label_page.isnumeric() or all(characters in roman_numerals for characters in im.label_page)): 
            im.label_prefix = "p. "
        elif im.label_page and (im.label_page[0:-1].isnumeric() or all(characters in roman_numerals for characters in im.label_page[0:-1])) and (im.label_page[-1] in {"r", "v"}):
            im.label_prefix = "fol. "
    m.images = images
 
    return m


@classes.func_logger
def parse_manifest_ecodices(uri_entered):
    #f=open(r'C:\Users\berth\Documents\Warburg\Experimente - Python\iconobase\manifest.json', 'r', encoding='utf-8')
    url = urllib.request.urlopen(uri_entered)
    manifest = json.load(url)
    #Step 1/2: Extracting relevant fields from the general section of the Manifest and parsing them
    classes.Metadata=manifest["classes.Metadata"]
    m = classes.Metadata()
    repository = classes.Organisation()
    m.manifest = url.read()
    m.license = manifest["license"]
    for step1 in classes.Metadata:
        bid = classes.BibliographicId()
        label = step1["label"]
        if label == "Location":
            collection_place = step1["value"]
        if label == "Collection Name": 
            collection_name = step1["value"]
        if label == "Shelfmark":
            m.shelfmark = step1["value"]
        
    
    attribution = manifest["attribution"]
    repository.name = collection_name.strip() + " " + collection_place.strip()
    repository.role = "col"
    m.repository.append(repository)

    
 
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    canvas_id_pattern = r'(.*)(canvas/)(.*)'
    canvas_label_pattern = r'(.*?)([(].*)'
    roman_numerals = {"M", "m", "D", "d", "C", "c", "X", "x", "V", "v", "I", "i", "J", "j"}
    canvas_properties = []
    canvas_list = ((manifest["sequences"])[0])["canvases"]
    images = parse_canvas.parse_canvas(canvas_list)    
    m.numberOfImages = len(images)
    
    for im in images:
        #for the label (page-number) of the canvas
        im.label_page = im.label_raw
        
        #if the canvas_label is a figure or Roman numerlas only, it probably is a page number, and hence "p. " is added. If it is a figure or Roman numerals 
        #but has as last character "r" or "v", it is probably a folio number. 
        if im.label_page and (im.label_page.isnumeric() or all(characters in roman_numerals for characters in im.label_page)): 
            im.label_prefix = "p. "
        elif im.label_page and (im.label_page[0:-1].isnumeric() or all(characters in roman_numerals for characters in im.label_page[0:-1])) and (im.label_page[-1] in {"r", "v"}):
            im.label_prefix = "fol. "
    m.images = images
    return m

@classes.func_logger
def parse_manifest_erara(uri_entered):
    """
\todo
    """
    #f=open(r'C:\Users\berth\Documents\Warburg\Experimente - Python\iconobase\manifest.json', 'r', encoding='utf-8')
    url = urllib.request.urlopen(uri_entered)
    manifest = json.load(url)
    #Step 1: Extracting relevant fields from the general section of the Manifest
    classes.Metadata=manifest["classes.Metadata"]
    m = classes.Metadata()
    repository = classes.Organisation()
    bibliographic_reference_long = ""
    bibliographic_reference_divided = []
    mets_record = ""
    m.manifest = url.read()
    m.license = "Public Domain" # das ist provisorisch, die License ist hier nicht angeben
    for step1 in classes.Metadata:
        bid = classes.BibliographicId()
        label = step1["label"]
        if label == "Besitzende Institution":
            location_long = step1["value"]
        if label == "Bibliografische Referenz":
            bibliographic_reference_long = step1["value"]
   
    if  bibliographic_reference_long == "":
        see_also = manifest["seeAlso"]
        mets_record = see_also['@id']
        print("mets-URL: " + mets_record)

    if mets_record: #in a few cases the number is only here and not in the manifest. 
        mets = urllib.request.urlopen(mets_record)
        tree = xml.etree.ElementTree.parse(mets)
        root = tree.getroot()
        record = root[2][0][1][0][2][0][0][0]
        for step1 in record:
            match step1.get("type"):
                case "vda":
                    bibliographic_reference_long = step1.text
                    print("entry found: "+ bibliographic_reference_long)



    
    attribution = manifest["attribution"]
    
    # Step 2: Parsing the extracted fields
    if "," in location_long: # I assume there always is one I have to find out what it looks like if there isn't. 
        location_divided = location_long.split(",", maxsplit = 1)
        if location_divided:
            repository.name = location_divided[0]
            repository.role = "col"
            m.repository.append(repository)
            m.shelfmark = location_divided[1]
    if bibliographic_reference_long:
        if ";" in bibliographic_reference_long:
            bibliographic_reference_divided = bibliographic_reference_long.split(";")
        else:
            bibliographic_reference_divided.append(bibliographic_reference_long)
        for reference in bibliographic_reference_divided:
            bid = classes.BibliographicId()
            reference = reference.strip()
            reference = reference.replace("VD ", "VD")
            if "GW" in reference:
                bid.name = "GW"
                bid.id = reference[2:].strip()
                m.bibliographic_id.append(bid)
            if "ISTC" in reference:
                bid.name = "ISTC"
                bid.id = reference[4:].strip()
                m.bibliographic_id.append(bid)
            if "VD16" in reference:
                bid.name = "VD16"
                bid.id = reference[4:].strip()
                m.bibliographic_id.append(bid)
                print(m.bibliographic_id)
            if "VD17" in reference:
                bid.name = "VD17"
                bid.id = reference[4:].strip()                
                m.bibliographic_id.append(bid)
            if "VD18" in reference:
                bid.name = "VD18"
                bid.id = reference[4:].strip()
                m.bibliographic_id.append(bid)
            if "ESTC" in reference:
                bid.name = "ESTC"
                bid.id = reference[4:].strip()
                m.bibliographic_id.append(bid)
            if "CNCE" in reference:
                bid.name = "EDIT16 CNCE"
                bid.id = reference[4:].strip()
                m.bibliographic_id.append(bid)



   
 
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    
    canvas_label_pattern = r'(\[\d*\])(.*)?'#There is always a counting of canvases, and sometimes a page-number following it
    roman_numerals = {"M", "m", "D", "d", "C", "c", "X", "x", "V", "v", "I", "i", "J", "j"}
    canvas_properties = []
    canvas_list = ((manifest["sequences"])[0])["canvases"]
    images = parse_canvas.parse_canvas(canvas_list)    
    m.numberOfImages = len(images)
    
    for im in images:
        #for the label (page-number) of the canvas
        label_page_divided = re.match(canvas_label_pattern, im.label_raw)
        if label_page_divided:
            if label_page_divided[2]:
                im.label_page = label_page_divided[2].strip()
        
        
        #if the canvas_label is a figure or Roman numerlas only, it probably is a page number, and hence "p. " is added. If it is a figure or Roman numerals 
        #but has as last character "r" or "v", it is probably a folio number. 
        if im.label_page and (im.label_page.isnumeric() or all(characters in roman_numerals for characters in im.label_page)): 
            im.label_prefix = "p. "
        elif im.label_page and (im.label_page[0:-1].isnumeric() or all(characters in roman_numerals for characters in im.label_page[0:-1])) and (im.label_page[-1] in {"r", "v"}):
            im.label_prefix = "fol. "
    m.images = images

   
    return m


@classes.func_logger
def parse_manifest_bodleian(uri_entered):
    """
\todo
    """
    #f=open(r'C:\Users\berth\Documents\Warburg\Experimente - Python\iconobase\manifest.json', 'r', encoding='utf-8')
    url = urllib.request.urlopen(uri_entered)
    manifest = json.load(url)
    #Step 1: Extracting relevant fields from the general section of the Manifest and parsing them
    classes.Metadata=manifest["classes.Metadata"]
    m = classes.Metadata()
    repository = classes.Organisation()
    m.manifest = url.read()
    shelfmark_pattern = r'(.*?)(College|Hall|Church)(.*)'
    attribution_pattern = r'(.*?)(https://creativecommons[^>]*)'
    repository_pattern = r'(<[^<>]*><[^<>]*><[^<>]*><[^<>]*>)(.*?)(<.*)'
    bibliographic_record = ""
    for step1 in classes.Metadata:
        bid = classes.BibliographicId()
        label = step1["label"]
        if label == "Shelfmark":
            shelfmark_long = step1["value"]
        if label == "Catalogue Identifier":
            bibliographic_record = step1["value"]          
        #if label == "Other Identifier":
            #additional_bibliographic_record = step1["value"] This is a reference to the Bodleian Catalogue. However, since up to now there are hardly any non-Enlish
            #Post-1500 books digitised, I don't bother with this now. 
    attribution = manifest["attribution"]

    
    
    #Step 2: Parsing the extracted fields
    
    if "All rights reserved" in attribution or "all rights reserved" in attribution:
        m.license = "All rights reserved"
    if "https://creativecommons" in attribution:
        m.license = re.match(attribution_pattern, attribution)[2]


    if "Bodleian Library" in shelfmark_long:
        repository.name = "Bodleian Library"
        repository.role = "col"
        m.repository.append(repository)
        m.shelfmark = shelfmark_long[16:].strip()
    if "Ashmolean Museum" in shelfmark_long:
        repository.name = "Ashmolean Museum"
        repository.role = "col"
        m.repository.append(repository)
        m.shelfmark = shelfmark_long[16:].strip()
    if "Museum of Natural History OUM" in shelfmark_long:
        repository.name = "Oxford University Museum of Natural History"
        repository.role = "col"
        m.repository.append(repository)
        m.shelfmark = shelfmark_long[30:].strip()
    if "College" in shelfmark_long or "Hall" in shelfmark_long or "Church" in shelfmark_long:
        shelfmark_long_divided = re.match(shelfmark_pattern, shelfmark_long)
        repository.name = shelfmark_long_divided[1] + shelfmark_long_divided[2] + " Oxford"
        repository.role = "col"
        m.shelfmark = shelfmark_long_divided[3].strip()   
        m.repository.append(repository)

    if bibliographic_record:
        bid =classes.BibliographicId()
        if "Bod-inc." in bibliographic_record:
            bid.name = "Bod-inc"
            bid.id = bibliographic_record[9:].strip()
            m.bibliographic_id.append(bid)
        if "ESTC" in bibliographic_record:
            bid.name = "ESTC"
            bid.id = bibliographic_record[5:].strip()
            m.bibliographic_id.append(bid)



    
 
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    roman_numerals = {"M", "m", "D", "d", "C", "c", "X", "x", "V", "v", "I", "i", "J", "j"}
    canvas_properties = []
    canvas_list = ((manifest["sequences"])[0])["canvases"]
    images = parse_canvas.parse_canvas(canvas_list)    
    m.numberOfImages = len(images)
    
    for im in images:
        #for the label (page-number) of the canvas
        if im.label_raw[0:5] == "fol. ":
            im.label_prefix = "fol. "
            im.label_page = im.label_raw[5:]
        if im.label_raw[0:3] == "p. ":
            im.label_prefix = "p. "
            im.label_page = im.label_raw[3:]
    m.images = images

   
    return m

@classes.func_logger
def parse_manifest_heidelberg(uri_entered):
    url = urllib.request.urlopen(uri_entered)
    manifest = json.load(url)
    #Step 1/2: Extracting relevant fields from the general section of the Manifest and parsing them
    classes.Metadata=manifest["classes.Metadata"]
    attribution = manifest["attribution"][0]["@value"]
    m = classes.Metadata()
    repository = classes.Organisation()
    bibliographic_information = ""
    m.manifest = url.read()
    m.license = manifest["license"]
    for step1 in classes.Metadata:
        label = step1["label"]
        if label == "Shelfmark":
            shelfmark = step1["value"][0]
            if "Universitätsbibliothek Heidelberg, " in shelfmark:
                m.shelfmark = shelfmark[34:].strip()
        if label =="Bibliographic Information":
            bibliographic_information = step1["value"][0]

    
    repository.name = attribution
    repository.role = "col"
    m.repository.append(repository)

    if bibliographic_information:
        catalogue_text = requests.get(bibliographic_information).text
        record = ""
        record_raw = re.search(r'(GW|VD16|VD17|VD18) [^<]*', catalogue_text)
        if record_raw:
            record = record_raw.group(0)
        if record:
            record_divided = record.split(" ", maxsplit=1)
            bid =classes.BibliographicId()
            bid.name = record_divided[0]
            bid.id = record_divided[1]
            m.bibliographic_id.append(bid)
        
               
 
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    canvas_id_pattern = r'(.*)(canvas/)(.*)'
    roman_numerals = {"M", "m", "D", "d", "C", "c", "X", "x", "V", "v", "I", "i", "J", "j"}
    canvas_properties = []
    canvas_list = ((manifest["sequences"])[0])["canvases"]
    images = parse_canvas.parse_canvas(canvas_list)    
    m.numberOfImages = len(images)

    for im in images:
        #for the label (page-number) of the canvas
        im.label_page = im.label_raw
        #if the canvas_label is a figure or Roman numerlas only, it probably is a page number, and hence "p. " is added. If it is a figure or Roman numerals 
        #but has as last character "r" or "v", it is probably a folio number. 
        if im.label_page and (im.label_page.isnumeric() or all(characters in roman_numerals for characters in im.label_page)): 
            im.label_prefix = "p. "
        elif im.label_page and (im.label_page[0:-1].isnumeric() or all(characters in roman_numerals for characters in im.label_page[0:-1])) and (im.label_page[-1] in {"r", "v"}):
            im.label_prefix = "fol. "
    m.images = images
    return m

@classes.func_logger
def parse_manifest_vaticana(uri_entered):
    """
\todo
    """
    url = urllib.request.urlopen(uri_entered)
    manifest = json.load(url)
    #Step 1/2: Extracting relevant fields from the general section of the Manifest and parsing them
    classes.Metadata=manifest["classes.Metadata"]
    m = classes.Metadata()
    repository = classes.Organisation()
    bibliographic_information = ""
    m.manifest = url.read()
    m.license = manifest["attribution"] # There is no license field, hence I copy the attribution
    bibliographic_information = manifest["seeAlso"][0]
    print("reference to catalogue BAV")
    print(bibliographic_information)
    for step1 in classes.Metadata:
        label = step1["label"]
        if label == "Shelfmark":
            m.shelfmark = step1["value"]
        
            
        

    
    repository.name = "Biblioteca Apostolica Vaticana" # I indicate it manually since it stands nowhere. 
    repository.role = "col"
    m.repository.append(repository)

    if bibliographic_information:
        catalogue_text = requests.get(bibliographic_information).text
        if catalogue_text:
            print("BAV catalogue text found")
        record = ""
        #record_raw = re.search(r'ISTC i\w\d{8}', catalogue_text)
        record_raw = re.search(r'ISTC i\w\d{8}', catalogue_text)
        if record_raw:
            print("text found BAV")
            record = record_raw.group(0)
            print("identified bibliography: ")
            print(record)
            if record:
                bid =classes.BibliographicId()
                bid.name = "ISTC"
                bid.id = record[5:].strip()
                m.bibliographic_id.append(bid)
        else:
            record_raw = re.search(r'GW \d{1,8}', catalogue_text)
            if record_raw:
                print("text found BAV")
                record = record_raw.group(0)
                print("identified bibliography: ")
                print(record)
                if record:
                    bid =classes.BibliographicId()
                    bid.name = "GW"
                    bid.id = record[3:].strip()
                    m.bibliographic_id.append(bid)

        
               
 
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    canvas_id_pattern = r'(.*)(canvas/)(.*)'
    roman_numerals = {"M", "m", "D", "d", "C", "c", "X", "x", "V", "v", "I", "i", "J", "j"}
    canvas_properties = []
    canvas_list = ((manifest["sequences"])[0])["canvases"]
    images = parse_canvas.parse_canvas(canvas_list)    
    m.numberOfImages = len(images)

    for im in images:
        #for the label (page-number) of the canvas
        im.label_page = im.label_raw
        #if the canvas_label is a figure or Roman numerlas only, it probably is a page number, and hence "p. " is added. If it is a figure or Roman numerals 
        #but has as last character "r" or "v", it is probably a folio number. 
        if im.label_page and (im.label_page.isnumeric() or all(characters in roman_numerals for characters in im.label_page)): 
            im.label_prefix = "p. "
        elif im.label_page and (im.label_page[0:-1].isnumeric() or all(characters in roman_numerals for characters in im.label_page[0:-1])) and (im.label_page[-1] in {"r", "v"}):
            im.label_prefix = "fol. "
    m.images = images
    return m

@classes.func_logger
def parse_manifest_vienna(uri_entered):
    url = urllib.request.urlopen(uri_entered)
    manifest = json.load(url)
    
    #Step 1/2: Extracting relevant fields from the general section of the Manifest and parsing them
    m = classes.Metadata()
    m.manifest = url.read()
    
    repository = classes.Organisation()
    bibliographic_information = ""
    attribution = manifest["attribution"]
    for step1 in attribution:
        if step1["@language"] == "ger":
            repository.name = step1["@value"]
            repository.role = "col"
            m.repository.append(repository)

    classes.Metadata=manifest["classes.Metadata"]
    m.license = manifest["license"] # There is no license field, hence I copy the attribution
    for step1 in classes.Metadata:
        label = step1["label"]
        for step2 in label:
            if isinstance(step2, dict):
                if step2["@value"] == "Ort":
                    shelfmark_long = step1["value"]

        if step1["label"] == "Barcode":          
            bibliographic_information = step1["value"]

    if "href" in shelfmark_long: # I am not sure if the shelfmark always contains a link
        shelfmark_pattern = r'>[^<]*<'
        m.shelfmark = re.search(shelfmark_pattern, shelfmark_long).group(0)[1:-1]
    else:
        m.shelfmark = shelfmark_long # In fact, if such shelfmarks appear, I have to check what their syntax is
            
     

    

    if bibliographic_information:
        record_url = r'https://obv-at-oenb.alma.exlibrisgroup.com/view/sru/43ACC_ONB?version=1.2&query=alma.barcode=' + bibliographic_information + r'&startRecord=0&maximumRecords=1&operation=searchRetrieve&recordSchema=marcxml'
        # The plus-sign of the barcode has to be changed for the URL, hence I keep it here in percent code and leave it out in the barcode
        print("URL for bibliographical information: ")
        print(record_url)
        url = urllib.request.urlopen(record_url)
        tree = xml.etree.ElementTree.parse(url)
        root = tree.getroot()
        record = root[2][0][2][0]
        for step1 in record:
            match step1.get("tag"):
                # In the examples I saw, bibligraphical references for Post-1501 books are in field 24, those for incunables in field 555. I have no clue if this is consistently handled like that. 
                case "024":
                    print("field with bibliography found in catalogue")
                    bid =classes.BibliographicId()
                    for step2 in step1:
                        print("tag of subfield: ")
                        print(step2.get("code"))
                        match step2.get("code"):                            
                            case "a":
                                print("bibliographical reference from catalogue: ")
                                print(step2.text)
                                if step2.text[0:4] == "VD16":
                                    bid.name = "VD16"
                                    bid.id = step2.text[4:].strip()
                                    m.bibliographic_id.append(bid)
                                if step2.text[0:4] == "VD17":
                                    bid.name = "VD17"
                                    bid.id = step2.text[4:].strip()
                                    m.bibliographic_id.append(bid)
                                if step2.text[0:4] == "VD18":
                                    bid.name = "VD18"
                                    bid.id = step2.text[4:].strip()
                                    m.bibliographic_id.append(bid)
                                if step2.text[0:4] == "CNCE":
                                    bid.name = "EDIT16 CNCE"
                                    bid.id = step2.text[4:].strip()
                                    m.bibliographic_id.append(bid) # Vienna quotes this a lot, so I already inserted that here. 
                                    # I wonder if how to abbreviate it
                case "555": # I include this although up to now there are no IIIF manifests for incunables. 
                    bid =classes.BibliographicId()
                    for step2 in step1:
                        match step2.get("code"):
                            case "d":
                                if step2.text == "GW":
                                    bid.name = "GW"
                                    bid.id = step2.text[2:].strip()
                                    m.bibliographic_id.append(bid)                                     
                      
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    canvas_id_pattern = r'(.*)(canvas/)(.*)'
    roman_numerals = {"M", "m", "D", "d", "C", "c", "X", "x", "V", "v", "I", "i", "J", "j"}
    canvas_properties = []
    canvas_list = ((manifest["sequences"])[0])["canvases"]
    images = parse_canvas.parse_canvas(canvas_list)    
    m.numberOfImages = len(images)
    # It appears that Vienna does not give any page numbers, and that the numbers such as "page50" are merely canvas numbers. Hence, I do not do anything to parse these numbers. 
    m.images = images
    return m


@classes.func_logger
def parse_manifest_washington(uri_entered): 
    """
This section is still untested since I couldn't open the manifest
    """
    print("starting LoC")
    print(uri_entered)
    url = requests.get(uri_entered) # I have to use here this, since the usual urllib.request returns 'forbidden'. 
    manifest = url.json()
    #Step 1/2: Extracting relevant fields from the general section of the Manifest and parsing them
    m = classes.Metadata()
    repository = classes.Organisation()
    bibliographic_information = ""
    shelfmark_part1 = ""
    shelfmark_part2 = ""
    shelfmark_part3 = ""
    m.manifest = json.dumps(manifest)
    m.license = "Fair Use"
    repository.name = "Library of Congress"
    repository.role = "col"
    m.repository.append(repository)

    
    bibliographical_reference = manifest["seeAlso"]    
    for step1 in bibliographical_reference:
        if "marcxml" in step1["@id"]:
            record_url = step1["@id"] # Apparently, every digitised item has such a URL
            print("LoC record URL: ")
            print(record_url)

    url = urllib.request.urlopen(record_url)
    tree = xml.etree.ElementTree.parse(url)
    record = tree.getroot() # Much simpler than other MarcXML records!
    for step1 in record:
        match step1.get("tag"):
            case "050":
                for step2 in step1:
                    match step2.get("code"):
                        case "a":
                            shelfmark_part1 = step2.text
                        case "b":
                            shelfmark_part2 = step2.text
            case "510":
                bid =classes.BibliographicId()
                for step2 in step1:
                    match step2.get("code"):
                        case "a":
                            if "ISTC" in step2.text:
                                bid.name = "ISTC"
                            if "VD16" in step2.text:
                                bid.name = "VD16"
                            if "VD17" in step2.text:
                                bid.name = "VD17"
                            if "VD18" in step2.text:
                                bid.name = "VD18"
                            if "ESTC" in step2.text:
                                bid.name = "ESTC"
                            if "EDIT 16" in step2.text or "EDIT16" in step2.text or "CNCE" in step2.text:
                                bid.name = "EDIT16 CNCE"
                            if "Gesamtkatalog der Wiegendrucke" in step2.text:
                                bid.name = "GW"
                            if "Goff" in step2.text:
                                bid.name = "Goff"
                        case "c":
                            bid.id = step2.text
                            if bid.id[0:4] == "ISTC" or bid.id[0:4] == "VD16" or bid.id[0:4] == "VD17" or bid.id[0:4] == "VD18" or bid.id[0:4] == "ESTC" or bid.id[0:4] == "CNCE":
                                bid.id = bid.id[4:].strip()
                if bid.name:
                    m.bibliographic_id.append(bid) # Only append this if it is one of these references.                         
            case "856":
                for step2 in step1:
                    match step2.get("code"):
                        case "u":
                            shelfmark_part3_long = step2.text
                shelfmark_part3_long_pattern = r'(.*?)([^/]*$)'
                shelfmark_part3 = re.match(shelfmark_part3_long_pattern, shelfmark_part3_long)[2]
    m.shelfmark = shelfmark_part1 + shelfmark_part2 + " (" + shelfmark_part3 + ")"
    print("List of bibliographic records: ")
    for record in m.bibliographic_id:
        print(record.id)
    
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    canvas_id_pattern = r'(.*)(canvas/)(.*)'
    roman_numerals = {"M", "m", "D", "d", "C", "c", "X", "x", "V", "v", "I", "i", "J", "j"}
    canvas_properties = []
    canvas_list = (((manifest["sequences"])[0])["canvases"])
    images = parse_canvas.parse_canvas(canvas_list)    
    m.numberOfImages = len(images)
    # It appears that LoC does not give any page numbers, and that the numbers such as "page 50" are merely canvas numbers. Hence, I do not do anything to parse these numbers. 
    m.images = images
    return m


@classes.func_logger
def parse_manifest_goettingen (URI_entered): 
    url = urllib.request.urlopen(URI_entered)
    manifest = json.load(url)
    #Step 1/2: Extracting relevant fields from the general section of the Manifest and parsing them
    m = classes.Metadata()
    repository = classes.Organisation()
    record_url = ""
    m.manifest = url.read()
    bibliographical_reference_long = manifest["@id"]
    if "PPN" in bibliographical_reference_long: # This is the case for books, but apparently not always for manuscripts
        bibliographical_reference_long_pattern = r'(.*?)(PPN)(\d*$)'
        bibliographical_reference = re.match(bibliographical_reference_long_pattern, bibliographical_reference_long)[3]
        record_url = r'http://sru.k10plus.de/opac-de-627?version=1.1&operation=searchRetrieve&query=pica.ppn%3D' + bibliographical_reference + r'&maximumRecords=10&recordSchema=marcxml'
        print("URL of catalogue record: ")
        print(record_url)
    if "license" in manifest:
        m.license = manifest["license"]
    else:
        m.license = "no license information"
    repository.name = manifest["attribution"]
    repository.role = "col"
    m.repository.append(repository)
    classes.Metadata = manifest["classes.Metadata"]
    for step1 in classes.Metadata:
        if step1["label"] == "Signatur":
            m.shelfmark = step1["value"]


    # In many cases, the shelf mark is not given in the manifest, but only in the METS/MODS file connected to it. 
    if m.shelfmark == "":
        shelfmark_reference_long = manifest['seeAlso']      
        for record in shelfmark_reference_long:
            if "mets.xml" in record["@id"]:
                shelfmark_reference = record["@id"]
                print("URL of METS file: ")
                print(shelfmark_reference)
        if shelfmark_reference:
            mets = urllib.request.urlopen(shelfmark_reference)
            tree = xml.etree.ElementTree.parse(mets)
            root = tree.getroot()
            print("Root found")
            for location in root.iter(r'{http://www.loc.gov/mods/v3}shelfLocator'):
                m.shelfmark = location.text
    
    if record_url:
        url = urllib.request.urlopen(record_url)
        tree = xml.etree.ElementTree.parse(url)
        root = tree.getroot()
        if len(root[2][0]) > 1: # Some old PPNs do not have a record that can be called this way - if it is called, a useless dummy record appears. 
            record = root[2][0][2][0]
            for step1 in record:
                match step1.get("tag"):
                    case "024":
                        bid =classes.BibliographicId()
                        for step2 in step1:
                            match step2.get("code"):
                                case "2":
                                    if "GW" in step2.text:
                                        bid.name = "GW"
                                    if "VD16" in step2.text or "vd16" in step2.text:
                                        bid.name = "VD16"
                                    if "VD17" in step2.text or "vd17" in step2.text:
                                        bid.name = "VD17"
                                    if "VD18" in step2.text or "vd18" in step2.text:
                                        bid.name = "VD18"
                                    if "ESTC" in step2.text:
                                        bid.name = "ESTC"
                                    if "EDIT 16" in step2.text or "EDIT16" in step2.text or "CNCE" in step2.text:
                                        bid.name = "EDIT16 CNCE"
                                case "a":
                                    bid.id = step2.text
                                    print("bid.id uncropped: ")
                                    print(bid.id)
                                    if bid.id[0:4] == "VD16" or bid.id[0:4] == "VD17" or bid.id[0:4] == "VD18" or bid.id[0:4] == "ESTC" or bid.id[0:4] == "CNCE":
                                        bid.id = bid.id[4:].strip()
                                    if bid.id[0:2] == "GW":
                                        bid.id = bid.id[2:].strip()
                        if bid.name:
                            print(bid.name)
                            print("bid.id cropped: ")
                            print(bid.id)
                            m.bibliographic_id.append(bid) # Only append this if it is one of these references. 
                    
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    canvas_id_pattern = r'(.*)(canvas/)(.*)'
    roman_numerals = {"M", "m", "D", "d", "C", "c", "X", "x", "V", "v", "I", "i", "J", "j"}
    canvas_properties = []
    canvas_list = (((manifest["sequences"])[0])["canvases"])
    images = parse_canvas.parse_canvas(canvas_list)    
    m.numberOfImages = len(images)

    
    for im in images:
        #for the label (page-number) of the canvas
        im.label_page = im.label_raw
        #if the canvas_label is a figure or Roman numerlas only, it probably is a page number, and hence "p. " is added. If it is a figure or Roman numerals 
        #but has as last character "r" or "v", it is probably a folio number. 
        if im.label_page and (im.label_page.isnumeric() or all(characters in roman_numerals for characters in im.label_page)): 
            im.label_prefix = "p. "
        elif im.label_page and (im.label_page[0:-1].isnumeric() or all(characters in roman_numerals for characters in im.label_page[0:-1])) and (im.label_page[-1] in {"r", "v"}):
            im.label_prefix = "fol. "
    m.images = images
    return m


@classes.func_logger
def parse_manifest_princeton (URI_entered): 
    url = urllib.request.urlopen(URI_entered)
    manifest = json.load(url)
    #Step 1/2: Extracting relevant fields from the general section of the Manifest and parsing them
    m = classes.Metadata()
    repository = classes.Organisation()
    
    m.manifest = url.read()
    repository.name = "Princeton University Library"
    repository.role = "col"
    m.repository.append(repository)
    if "license" in manifest:
        m.license = manifest["license"]
    else:
        m.license = "no license information"
    classes.Metadata = manifest["classes.Metadata"]
    for step1 in classes.Metadata:
        if step1["label"] == "Location":
            m.shelfmark = step1["value"][0]
            if m.shelfmark[0:20] == "Special Collections ":
                m.shelfmark = m.shelfmark[20:]

    seeAlso = manifest["seeAlso"]
    for step1 in seeAlso:
        if step1["format"] == "text/xml":
            catalogue_address = step1["@id"]
    

    url = urllib.request.urlopen(catalogue_address)
    tree = xml.etree.ElementTree.parse(url)
    root = tree.getroot()
    for step1 in root:
        match step1.get("tag"):
            case "510":
                bid =classes.BibliographicId()
                for step2 in step1:
                    match step2.get("code"):
                        case "a":
                            if "GW" in step2.text:
                                bid.name = "GW"
                            if "Goff" in step2.text:
                                bid.name = "Goff"
                            if "ISTC" in step2.text:
                                bid.name = "ISTC"
                            if "VD16" in step2.text or "vd16" in step2.text:
                                bid.name = "VD16"
                            if "VD17" in step2.text or "vd17" in step2.text:
                                bid.name = "VD17"
                            if "VD18" in step2.text or "vd18" in step2.text:
                                bid.name = "VD18"
#                            if "ESTC" in step2.text: I remove it because I have not yet programmed it. 
#                                bid.name = "ESTC"
                            if "EDIT 16" in step2.text or "EDIT16" in step2.text or "CNCE" in step2.text:
                                bid.name = "EDIT16 CNCE"
                        case "c":
                            bid.id = step2.text
                if bid.name:
                    m.bibliographic_id.append(bid)
                    print(bid.id)
                    print(bid.name)
    


                    
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    
    canvas_list = (((manifest["sequences"])[0])["canvases"])
    images = parse_canvas.parse_canvas(canvas_list)    
    m.numberOfImages = len(images)

    
    for im in images:
        #for the label (page-number) of the canvas
        if im.label_raw[0:2] == "f.":
            im.label_prefix = "fol."
            im.label_page = im.label_raw[2:].strip()
            if im.label_page[-1] == ".":
                im.label_page = im.label_page[:-1]

        elif im.label_raw[0:2] == "p.":
            im.label_prefix = "p."
            im.label_page = im.label_raw[2:].stri()
            if im.label_page[-1] == ".":
                im.label_page = im.label_page[:-1]
        elif "board" in im.label_raw or "leaf" in im.label_raw:
            im.label_page = im.label_raw

       
    
    m.images = images
    return m

@classes.func_logger
def parse_manifest_yale (URI_entered): 
    url = urllib.request.urlopen(URI_entered)
    manifest = json.load(url)
    #Step 1/2: Extracting relevant fields from the general section of the Manifest and parsing them
    m = classes.Metadata()
    repository = classes.Organisation()
    bibliographical_references_list = []
    m.manifest = url.read()
    repository.name = manifest["requiredStatement"]["value"]["en"][0]
    repository.role = "col"
    m.repository.append(repository)
    classes.Metadata = manifest["classes.Metadata"]
    for step1 in classes.Metadata:
        if step1["label"]["en"][0] == "Call Number":
            m.shelfmark = step1["value"]["none"][0]
        if step1["label"]["en"][0] == "Rights":
            m.license = step1["value"]["none"][0]
        if step1["label"]["en"][0] == "Citation":
            for reference in step1["value"]["none"]:
                print("bibliographical reference found: " + reference)
                bibliographical_references_list.append(reference)

    for reference in bibliographical_references_list:
        bid =classes.BibliographicId()
        reference_divided = reference.split(",")
        if "Gesamtkatalog" in reference:
            bid.name = "GW"
            bid.id = reference_divided[1].strip()
            m.bibliographic_id.append(bid)
        if "Incunabula short" in reference:
            bid.name = "ISTC"
            bid.id = reference_divided[1].strip()
            m.bibliographic_id.append(bid)
        if "Goff" in reference:
            bid.name = "Goff"
            bid.id = reference[4:].strip() # this works if it is quoted Goff + number
            m.bibliographic_id.append(bid)
    


                    
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    roman_numerals = {"M", "m", "D", "d", "C", "c", "X", "x", "V", "v", "I", "i", "J", "j"}    
    canvas_list = (manifest["items"])
    images = parse_canvas.parse_canvas_yale(canvas_list)    
    m.numberOfImages = len(images)

    
    for im in images:
        im.label_page = im.label_raw
        if im.label_page and (im.label_page.isnumeric() or all(characters in roman_numerals for characters in im.label_page)): 
            im.label_prefix = "p. "
        elif im.label_page and (im.label_page[0:-1].isnumeric() or all(characters in roman_numerals for characters in im.label_page[0:-1])) and (im.label_page[-1] in {"r", "v"}):
            im.label_prefix = "fol. "
        else:
            im.label_prefix = ""


       
    
    m.images = images
    return m


@classes.func_logger
def parse_manifest_boston (URI_entered): 
    url = urllib.request.urlopen(URI_entered)
    manifest = json.load(url)
    #Step 1/2: Extracting relevant fields from the general section of the Manifest and parsing them
    m = classes.Metadata()
    repository = classes.Organisation()
    rights_list = []
    identifiers_list = []
    
    m.manifest = url.read()
    classes.Metadata = manifest["classes.Metadata"]
    for step1 in classes.Metadata:
        if step1["label"] == "Location":
            repository.name = step1["value"]
            repository.role = "col"
            m.repository.append(repository)
        if step1["label"] == "Identifier": # there are several identifiers given - I assume that the relevant one starts always with "RARE"
            for line1 in step1["value"]:
                identifiers_list.append(line1)
            for line2 in identifiers_list:
                if "RARE" in line2: 
                    m.shelfmark = line2 
        if step1["label"] == "Terms of Use":
            for line1 in step1["value"]:
                rights_list.append(line1)
            for line2 in rights_list:
                m.license = m.license + line2 + "; "
            m.license = m.license[0:-2]


    if manifest["seeAlso"]:
        bibliographical_reference = manifest["seeAlso"]
        url = requests.get(bibliographical_reference)
        record = url.text
        reference_istc = re.search(r'Incunabula short title catalogue, i\w\d{8}', record)
        if reference_istc:
            bid =classes.BibliographicId()
            bid.name = "ISTC"
            bid.id = reference_istc.group(0)[34:].strip()
            m.bibliographic_id.append(bid)
        reference_gw = re.search(r'Gesamtkatalog der Wiegendrucke, \w*<', record)
        if reference_gw:
            bid =classes.BibliographicId()
            bid.name = "GW"
            bid.id = reference_gw.group(0)[32:-1].strip()
                                 
    
                 
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    
    canvas_list = (((manifest["sequences"])[0])["canvases"])
    images = parse_canvas.parse_canvas(canvas_list)    
    m.numberOfImages = len(images)

    # Apparently, the BPL does not use page numbers
    m.images = images
    return m

@classes.func_logger
def parse_manifest_manchester (URI_entered): 
    # As of 2023, Manchester seems to have onle two digitised incunables - hence, this modules is only geared at manuscripts. 
    url = urllib.request.urlopen(URI_entered)
    manifest = json.load(url)
    #Step 1/2: Extracting relevant fields from the general section of the Manifest and parsing them
    m = classes.Metadata()
    repository = classes.Organisation()
    license_long = manifest["attribution"]   
    license_long = license_long.replace("<p>", "")
    m.license = license_long.replace("</p>", "")
    m.manifest = url.read()
    classes.Metadata = manifest["classes.Metadata"]
    for step1 in classes.Metadata:
        if step1["label"] == "Physical Location":
            repository.name = step1["value"]
            repository.role = "col"
            m.repository.append(repository)
        if step1["label"] == "Classmark": 
            m.shelfmark = step1["value"]
                               
    
                 
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    
    roman_numerals = {"M", "m", "D", "d", "C", "c", "X", "x", "V", "v", "I", "i", "J", "j"}
    canvas_list = (((manifest["sequences"])[0])["canvases"])
    images = parse_canvas.parse_canvas(canvas_list)    
    m.numberOfImages = len(images)

    
    for im in images:
        #for the label (page-number) of the canvas
        im.label_page = im.label_raw
        #if the canvas_label is a figure or Roman numerlas only, it probably is a page number, and hence "p. " is added. If it is a figure or Roman numerals 
        #but has as last character "r" or "v", it is probably a folio number. 
        if im.label_page and (im.label_page.isnumeric() or all(characters in roman_numerals for characters in im.label_page)): 
            im.label_prefix = "p. "
        elif im.label_page and (im.label_page[0:-1].isnumeric() or all(characters in roman_numerals for characters in im.label_page[0:-1])) and (im.label_page[-1] in {"r", "v"}):
            im.label_prefix = "fol. "
    m.images = images
    return m

@classes.func_logger
def parse_manifest_cambridge_ul (URI_entered): 
    # As of 2023, Cambridge has virtually only catalogued manuscripts, hence there is no function for printed books
    url = urllib.request.urlopen(URI_entered)
    manifest = json.load(url)
    #Step 1/2: Extracting relevant fields from the general section of the Manifest and parsing them
    m = classes.Metadata()
    repository = classes.Organisation()
    m.license = manifest["attribution"]   
    m.manifest = url.read()
    classes.Metadata = manifest["classes.Metadata"]
    #  Sometimes, the field 'Classmark' contains only the shelf mark, in this case one has to take the repository from 'physical location'#
    # which is sometimes a bit awkward. 
    # In other cases, the field 'Classmark' contains 'Cambridge', the collection and the shelf mark, and hence it can be divided. 
    for step1 in classes.Metadata:
        if step1["label"] == "Physical Location":
            repository_long = step1["value"]
        if step1["label"] == "Classmark":
            shelfmark_long = step1["value"]
    if "Cambridge, " in shelfmark_long and shelfmark_long.count(",") >1:
        shelfmark_long_divided = shelfmark_long.split(",", maxsplit=2)
        repository.name = shelfmark_long_divided[1].strip()
        repository.role = "col"
        m.repository.append(repository)
        m.shelfmark = shelfmark_long_divided[2].strip()
    else:
        repository.name = repository_long
        repository.role = "col"
        m.repository.append(repository)
        m.shelfmark = shelfmark_long
    
                 
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    
    roman_numerals_plus_brackets = {"M", "m", "D", "d", "C", "c", "X", "x", "V", "v", "I", "i", "J", "j", "[", ""}
    canvas_list = (((manifest["sequences"])[0])["canvases"])
    images = parse_canvas.parse_canvas(canvas_list)    
    m.numberOfImages = len(images)

    
    for im in images:
        #for the label (page-number) of the canvas
        im.label_page = im.label_raw
        #if the canvas_label is a figure or Roman numerlas only, it probably is a page number, and hence "p. " is added. If it is a figure or Roman numerals 
        #but has as last character "r" or "v", it is probably a folio number. 
        if im.label_page and (im.label_page.isnumeric() or all(characters in roman_numerals_plus_brackets for characters in im.label_page)): 
            im.label_prefix = "p. "
        elif im.label_page and (im.label_page[0:-1].isnumeric() or all(characters in roman_numerals_plus_brackets for characters in im.label_page[0:-1])) and (im.label_page[-1] in {"r", "v"}):
            im.label_prefix = "fol. "
    m.images = images
    return m



@classes.func_logger
def parse_manifests_irht (URI_entered): 
    # This repository only contains manuscripts
    url = urllib.request.urlopen(URI_entered)
    manifest = json.load(url)
    #Step 1/2: Extracting relevant fields from the general section of the Manifest and parsing them
    m = classes.Metadata()
    repository = classes.Organisation()
    m.license = manifest["license"]
    repository.name = manifest["attribution"]
    repository.role = "col"
    m.repository.append(repository)
    m.manifest = url.read()
    classes.Metadata = manifest["classes.Metadata"]
    for step1 in classes.Metadata:
        if step1["label"] == "Cote":
            shelfmark_long = step1["value"]
            shelfmark_long_divided = shelfmark_long.split(",")
            m.shelfmark = shelfmark_long_divided[-1].strip().lstrip("0")
                        

                 
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    # Here, most photos show double-pages. They will have to be separated at a later date, and then it will be necessary to sort 
    # out the labels for the individual pages. 
    roman_numerals_plus_brackets = {"M", "m", "D", "d", "C", "c", "X", "x", "V", "v", "I", "i", "J", "j", "[", ""}
    canvas_list = (((manifest["sequences"])[0])["canvases"])
    images = parse_canvas.parse_canvas(canvas_list)    
    m.numberOfImages = len(images)

    
    for im in images:
        #for the label (page-number) of the canvas
        im.label_page = im.label_raw
        if im.label_page[0:2] == "f.":
            im.label_prefix = "fol. "
            label = im.label_page[2:]
        
        elif im.label_page[0:2] == "p.": # I expect that it works like this
            im.label_prefix = "p "
            label = im.label_page[2:]

        else:
            label = im.label_page

        if " - " in label:
            label_divided = label.split(" - ")
            label_part0 = label_divided[0].strip().lstrip("0")
            label_part1 = label_divided[1].strip().lstrip("0")
            im.label_page = label_part0 + " - " + label_part1



    m.images = images
    return m



@classes.func_logger
def parse_manifest_frankfurt (URI_entered): 
    url = urllib.request.urlopen(URI_entered)
    manifest = json.load(url)
    #Step 1/2: Extracting relevant fields from the general section of the Manifest and parsing them
    m = classes.Metadata()
    repository = classes.Organisation()
    m.license = manifest["license"]
    repository.name = "Universitätsbibliothek Frankfurt"
    repository.role = "col"
    m.repository.append(repository)
    m.manifest = url.read()
    classes.Metadata = manifest["classes.Metadata"]
    for step1 in classes.Metadata:
        if step1["label"] == "Titel":
            shelfmark_long = step1["value"]
            shelfmark_long_divided = shelfmark_long.split(" - ", maxsplit = 1)
            if len(shelfmark_long_divided) > 1:
                m.shelfmark = shelfmark_long_divided[0].strip()
        if step1["label"] == "VD16":
            bid =classes.BibliographicId()
            bid.name = "Vd16"
            bid.id = step1["value"]
            m.bibliographic_id.append(bid)
        if step1["label"] == "VD17":
            bid =classes.BibliographicId()
            bid.name = "VD17"
            bid.id = step1["value"]
            m.bibliographic_id.append(bid)
# For incunables, there there are apparently no references to catalogue numbers
    if m.shelfmark == "":
        m.shelfmark = "Shelfmark not indicated"
                 
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    # Here, most photos show double-pages. They will have to be separated at a later date, and then it will be necessary to sort 
    # out the labels for the individual pages. 
    roman_numerals_plus_brackets = {"M", "m", "D", "d", "C", "c", "X", "x", "V", "v", "I", "i", "J", "j", "[", ""}
    canvas_list = (((manifest["sequences"])[0])["canvases"])
    images = parse_canvas.parse_canvas(canvas_list)    
    m.numberOfImages = len(images)

    
    for im in images:
        #for the label (page-number) of the canvas
        im.label_page = im.label_raw
        #if the canvas_label is a figure or Roman numerlas only, it probably is a page number, and hence "p. " is added. If it is a figure or Roman numerals 
        #but has as last character "r" or "v", it is probably a folio number. 
        if im.label_page and (im.label_page.isnumeric() or all(characters in roman_numerals_plus_brackets for characters in im.label_page)): 
            im.label_prefix = "p. "
        elif im.label_page and (im.label_page[0:-1].isnumeric() or all(characters in roman_numerals_plus_brackets for characters in im.label_page[0:-1])) and (im.label_page[-1] in {"r", "v"}):
            im.label_prefix = "fol. "



    m.images = images
    return m



@classes.func_logger
def parse_manifest_weimar (URI_entered): 
    url = urllib.request.urlopen(URI_entered)
    manifest = json.load(url)
    #Step 1/2: Extracting relevant fields from the general section of the Manifest and parsing them
    m = classes.Metadata()
    repository = classes.Organisation()
    m.license = manifest["license"]
    repository.name = "Herzogin Anna Amalia Bibliothek, Weimar"
    repository.role = "col"
    m.repository.append(repository)
    m.manifest = url.read()
    classes.Metadata = manifest["classes.Metadata"]
    for step1 in classes.Metadata:
        label = step1["label"]
        for step2 in label:
            if isinstance(step2, dict):
                if step2["@value"] == "Signatur":
                    m.shelfmark = step1["value"]
    seeAlso = manifest["seeAlso"]
        # In order to get bibliographical references,I first have to parse the METS/MODS file to get the catalogue number PPN
        # and then to laod the record of this catalogue number from the union catalogue kxp. 
    if seeAlso["label"] == "METS/MODS":
        mets_reference = seeAlso["@id"]
    if mets_reference:
        kxp_reference = ""
        mets = urllib.request.urlopen(mets_reference)
        tree = xml.etree.ElementTree.parse(mets)
        root = tree.getroot()
        mods = root[1][0][0][0]
        for step1 in mods:
            match step1.get('source'):
                case "gbv-ppn":
                    kxp_reference = step1.text
        if kxp_reference == "": # I don't understand how the METS records are built. There is always a ppn in 'type' and sometimes
                # on in 'source'. However, it seems that if there is one in 'source', the one in 'type' does not work.
                # Sometimes, there is no working PPN number given. 
            for step1 in mods:
                match step1.get('type'):        
                    case "gbv-ppn":
                        kxp_reference = step1.text

            
        if kxp_reference:
            kxp_url = r'http://sru.k10plus.de/opac-de-627?version=1.1&operation=searchRetrieve&query=pica.ppn%3D' + kxp_reference + r'&maximumRecords=10&recordSchema=marcxml'
            print("URL of catalogue entry" + kxp_url)
            kxp = urllib.request.urlopen(kxp_url)
            tree = xml.etree.ElementTree.parse(kxp)
            root = tree.getroot()
            for step1 in root[2][0][2][0]:
                match step1.get('tag'):
                    case "024":
                        bid =classes.BibliographicId()
                        for step2 in step1:
                            match step2.get('code'):
                                case "2":
                                    bid.name = step2.text.strip()
                                case "a":
                                    bid.id = step2.text
                                    if bid.id[0:2] == "VD":
                                        bid.id = bid.id[5:]
                                    if bid.id[0:2] == "GW": # just in case a reference to the GW also appears here
                                        bid.id = bid.id[3:]
                        print(bid.name)
                        print(bid.id)
                        if bid.name in ["GW", "ISTC", "VD16", "vd16", "VD17", "vd17", "VD18", "vd18"]:
                            print ("appended:")
                            print(bid)
                            m.bibliographic_id.append(bid)
                    case "510":
                        bid =classes.BibliographicId()
                        for step2 in step1:
                            match step2.get('code'):
                                case "a":
                                    bibliographic_reference = step2.text
                                    if bibliographic_reference[0:2] == "GW":
                                        bid.name = "GW"
                                        bid.id = bibliographic_reference[3:]
                                        m.bibliographic_id.append(bid)
                                    if bibliographic_reference[0:4] == "ISTC":
                                        bid.name = "ISTC"
                                        bid.id = bibliographic_reference[5:]
                                        m.bibliographic_id.append(bid)
                                    if bibliographic_reference[0:4] == "VD16":
                                        bid.name = "VD16"
                                        bid.id = bibliographic_reference[5:]
                                        m.bibliographic_id.append(bid)
                                    if bibliographic_reference[0:4] == "VD17":
                                        bid.name = "VD17"
                                        bid.id = bibliographic_reference[5:]
                                        m.bibliographic_id.append(bid)
                                    if bibliographic_reference[0:4] == "VD18":
                                        bid.name = "VD18"
                                        bid.id = bibliographic_reference[5:]
                                        m.bibliographic_id.append(bid)
                                    

    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    # Here, most photos show double-pages. They will have to be separated at a later date, and then it will be necessary to sort 
    # out the labels for the individual pages. 
    roman_numerals_plus_brackets = {"M", "m", "D", "d", "C", "c", "X", "x", "V", "v", "I", "i", "J", "j", "[", ""}
    canvas_list = (((manifest["sequences"])[0])["canvases"])
    images = parse_canvas.parse_canvas(canvas_list)    
    m.numberOfImages = len(images)

    
    for im in images:
        #for the label (page-number) of the canvas
        im.label_page = im.label_raw
        #if the canvas_label is a figure or Roman numerlas only, it probably is a page number, and hence "p. " is added. If it is a figure or Roman numerals 
        #but has as last character "r" or "v", it is probably a folio number. 
        if im.label_page and (im.label_page.isnumeric() or all(characters in roman_numerals_plus_brackets for characters in im.label_page)): 
            im.label_prefix = "p. "
        elif im.label_page and (im.label_page[0:-1].isnumeric() or all(characters in roman_numerals_plus_brackets for characters in im.label_page[0:-1])) and (im.label_page[-1] in {"r", "v"}):
            im.label_prefix = "fol. "



    m.images = images
    return m






@classes.func_logger
def parse_manifest_kiel (URI_entered): 
    print("Start parsing Kiel")
    url = urllib.request.urlopen(URI_entered)
    manifest = json.load(url)
    #Step 1/2: Extracting relevant fields from the general section of the Manifest and parsing them
    m = classes.Metadata()
    repository = classes.Organisation()
    bibliographical_reference = ""
    bibliographical_reference_divided = []
    m.license = manifest["license"]
    m.manifest = url.read()
    classes.Metadata = manifest["classes.Metadata"]
    for step1 in classes.Metadata:
        label = step1["label"]
       
        for step2 in label:
            if isinstance(step2, dict):
                if step2["@value"] == "Signatur":
                    m.shelfmark = step1["value"]
                if step2["@value"] == "Physikalischer Standort":
                    repository.name = step1["value"]
                    repository.role = "col"
                    m.repository.append(repository)
                    #At least in some instances, there is a separate field for "VD18 Nummer" - in other cases, the bibliography is given in the description field
                if step2["@value"] == "VD16 Nummer": 
                    bid =classes.BibliographicId()
                    bid.name = "VD16"
                    bid.id = step1["value"]
                    m.bibliographic_id.append(bid)
                if step2["@value"] == "VD17 Nummer":
                    bid =classes.BibliographicId()
                    bid.name = "VD17"
                    bid.id = step1["value"]
                    m.bibliographic_id.append(bid)
                if step2["@value"] == "VD18 Nummer":
                    bid =classes.BibliographicId()
                    bid.name = "VD18"
                    bid.id = step1["value"]
                    m.bibliographic_id.append(bid)
                if step2["@value"] == "Beschreibung":
                    bibliographical_reference = step1["value"]


    
    if bibliographical_reference[0:20] == "Bibliogr. Nachweis: ":
        bibliographical_reference = bibliographical_reference[20:]
        if ";" in bibliographical_reference:
            bibliographical_reference_divided = bibliographical_reference.split("; ")
        else:
            bibliographical_reference_divided.append(bibliographical_reference)
    for reference in bibliographical_reference_divided:
        bid =classes.BibliographicId()
        reference = reference.strip()
        if reference[0:2] == "GW":
            bid.name = "GW"
            bid.id = reference[3:]
            m.bibliographic_id.append(bid)
        if reference[0:4] == "ISTC":
            bid.name = "ISTC"
            bid.id = reference[5:]
            m.bibliographic_id.append(bid)
        if reference[0:4] == "VD16":
            bid.name = "VD16"
            bid.id = reference[5:]
            m.bibliographic_id.append(bid)
        if reference[0:4] == "VD17":
            bid.name = "VD17"
            bid.id = reference[5:]
            m.bibliographic_id.append(bid)
        if reference[0:4] == "VD18":
            bid.name = "VD18"
            bid.id = reference[5:]
            m.bibliographic_id.append(bid)

    
    
                 
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    # Here, most photos show double-pages. They will have to be separated at a later date, and then it will be necessary to sort 
    # out the labels for the individual pages. 
    roman_numerals_plus_brackets = {"M", "m", "D", "d", "C", "c", "X", "x", "V", "v", "I", "i", "J", "j", "[", ""}
    canvas_list = (((manifest["sequences"])[0])["canvases"])
    images = parse_canvas.parse_canvas(canvas_list)    
    m.numberOfImages = len(images)

    
    for im in images:
        #for the label (page-number) of the canvas
        im.label_page = im.label_raw
        #if the canvas_label is a figure or Roman numerlas only, it probably is a page number, and hence "p. " is added. If it is a figure or Roman numerals 
        #but has as last character "r" or "v", it is probably a folio number. 
        if im.label_page and (im.label_page.isnumeric() or all(characters in roman_numerals_plus_brackets for characters in im.label_page)): 
            im.label_prefix = "p. "
        elif im.label_page and (im.label_page[0:-1].isnumeric() or all(characters in roman_numerals_plus_brackets for characters in im.label_page[0:-1])) and (im.label_page[-1] in {"r", "v"}):
            im.label_prefix = "fol. "



    m.images = images
    return m



@classes.func_logger
def parse_manifest_hamburg (URI_entered): 
    url = urllib.request.urlopen(URI_entered)
    manifest = json.load(url)
    #Step 1/2: Extracting relevant fields from the general section of the Manifest and parsing them
    m = classes.Metadata()
    repository = classes.Organisation()
    shelfmark_long = ""
    bibliographical_reference = ""
    bibliographical_reference_divided = []
    ppn_original_long = ""
    ppn_original_long_pattern = r'(\([\w\-]*\))?(\d*)'
    m.license = r'https://creativecommons.org/publicdomain/mark/1.0/' #on the library's website
    m.manifest = url.read()
    classes.Metadata = manifest["classes.Metadata"]
    for step1 in classes.Metadata:
        label = step1["label"]
       
        for step2 in label:
            if isinstance(step2, dict):
                if step2["@value"] == "Signatur":
                    shelfmark_long = step1["value"]

                if step2["@value"] == "VD16 Nummer": 
                    bid =classes.BibliographicId()
                    bid.name = "VD16"
                    bid.id = step1["value"]
                    m.bibliographic_id.append(bid)
                if step2["@value"] == "VD17 Nummer":
                    bid =classes.BibliographicId()
                    bid.name = "VD17"
                    bid.id = step1["value"]
                    m.bibliographic_id.append(bid)
                if step2["@value"] == "VD18 Nummer":
                    bid =classes.BibliographicId()
                    bid.name = "VD18"
                    bid.id = step1["value"]
                    m.bibliographic_id.append(bid)
                if step2["@value"] == "Beschreibung":
                    bibliographical_reference = step1["value"]

    if "," in shelfmark_long:
        shelfmark_long_divided = shelfmark_long.split(", ", maxsplit=1)
        repository.name = shelfmark_long_divided[0]
        repository.role = "col"
        m.repository.append(repository)
        m.shelfmark = shelfmark_long_divided[1].strip()

    ppn_digitised = URI_entered[42:-9]
    url_ppn_digitised = r'http://sru.k10plus.de/opac-de-627?version=1.1&operation=searchRetrieve&query=pica.ppn%3D' + ppn_digitised + r'&maximumRecords=10&recordSchema=marcxml'    
    kxp_digitised = urllib.request.urlopen(url_ppn_digitised)
    tree = xml.etree.ElementTree.parse(kxp_digitised)
    root = tree.getroot()
    for step1 in root[2][0][2][0]:
        match step1.get('tag'):
            case "776":
                for step2 in step1:
                    match step2.get('code'):
                        case "w":
                            ppn_original_long = step2.text.strip()
                            print("ppn original found: " + ppn_original_long)
                            ppn_original_long_divided = re.match(ppn_original_long_pattern, ppn_original_long)
                            ppn_original = ppn_original_long_divided[2]
    if ppn_original:
        url_ppn_original = r'http://sru.k10plus.de/opac-de-627?version=1.1&operation=searchRetrieve&query=pica.ppn%3D' + ppn_original + r'&maximumRecords=10&recordSchema=marcxml'        
        kxp = urllib.request.urlopen(url_ppn_original)
        tree = xml.etree.ElementTree.parse(kxp)
        root = tree.getroot()
        for step1 in root[2][0][2][0]:
            match step1.get('tag'):
                case "024":
                    bid =classes.BibliographicId()
                    for step2 in step1:
                        match step2.get('code'):
                            case "2":
                                bid.name = step2.text.strip()
                            case "a":
                                bid.id = step2.text
                                if bid.id[0:2] == "VD":
                                    bid.id = bid.id[5:]
                                if bid.id[0:2] == "GW": # just in case a reference to the GW also appears here
                                    bid.id = bid.id[3:]
                    print(bid.name)
                    print(bid.id)
                    if bid.name in ["GW", "ISTC", "VD16", "vd16", "VD17", "vd17", "VD18", "vd18"]:
                        m.bibliographic_id.append(bid)
                case "510":
                    bid =classes.BibliographicId()
                    for step2 in step1:
                        match step2.get('code'):
                            case "a":
                                bibliographic_reference = step2.text
                                if bibliographic_reference[0:2] == "GW":
                                    bid.name = "GW"
                                    bid.id = bibliographic_reference[3:]
                                    m.bibliographic_id.append(bid)
                                if bibliographic_reference[0:4] == "ISTC":
                                    bid.name = "ISTC"
                                    bid.id = bibliographic_reference[5:]
                                    m.bibliographic_id.append(bid)
                                if bibliographic_reference[0:4] == "VD16":
                                    bid.name = "VD16"
                                    bid.id = bibliographic_reference[5:]
                                    m.bibliographic_id.append(bid)
                                if bibliographic_reference[0:4] == "VD17":
                                    bid.name = "VD17"
                                    bid.id = bibliographic_reference[5:]
                                    m.bibliographic_id.append(bid)
                                if bibliographic_reference[0:4] == "VD18":
                                    bid.name = "VD18"
                                    bid.id = bibliographic_reference[5:]
                                    m.bibliographic_id.append(bid)
                                
 
  


    
    
                 
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    # Here, most photos show double-pages. They will have to be separated at a later date, and then it will be necessary to sort 
    # out the labels for the individual pages. 
    roman_numerals_plus_brackets = {"M", "m", "D", "d", "C", "c", "X", "x", "V", "v", "I", "i", "J", "j", "[", ""}
    canvas_list = (((manifest["sequences"])[0])["canvases"])
    images = parse_canvas.parse_canvas(canvas_list)    
    m.numberOfImages = len(images)

    
    for im in images:
        #for the label (page-number) of the canvas
        im.label_page = im.label_raw
        #if the canvas_label is a figure or Roman numerlas only, it probably is a page number, and hence "p. " is added. If it is a figure or Roman numerals 
        #but has as last character "r" or "v", it is probably a folio number. 
        if im.label_page and (im.label_page.isnumeric() or all(characters in roman_numerals_plus_brackets for characters in im.label_page)): 
            im.label_prefix = "p. "
        elif im.label_page and (im.label_page[0:-1].isnumeric() or all(characters in roman_numerals_plus_brackets for characters in im.label_page[0:-1])) and (im.label_page[-1] in {"r", "v"}):
            im.label_prefix = "fol. "



    m.images = images
    return m


@classes.func_logger
def parse_manifest_rostock (URI_entered): 
    url = urllib.request.urlopen(URI_entered)
    manifest = json.load(url)
    #Step 1/2: Extracting relevant fields from the general section of the Manifest and parsing them
    m = classes.Metadata()
    repository = classes.Organisation()
    repository.name = "Universitätsbibliothek Rostock"
    repository.role = "col"
    m.repository.append(repository)
    shelfmark_long = ""
    shelfmark_long_pattern = r'(.*?) : (.*?)'
    bibliographical_reference = ""
    bibliographical_reference_divided = []
    ppn_original_long = ""
    ppn_original_long_pattern = r'(.*?ppn)(\d*)'
    m.license = r'https://creativecommons.org/publicdomain/mark/1.0/' #on the library's website
    m.manifest = url.read()
    classes.Metadata = manifest["classes.Metadata"]
    for step1 in classes.Metadata:
        if step1["label"] == "identifier":
            ppn_original_long = step1["value"]
        if step1["label"] == "title":
            shelfmark_long = step1["value"]

    if " : " in shelfmark_long:
        print("shelfmark_long: " + shelfmark_long)
        shelfmark_long_divided = re.match(shelfmark_long_pattern, shelfmark_long)
        m.shelfmark = shelfmark_long_divided[2].strip()

    if ppn_original_long:
        print("ppn_original_long: " + ppn_original_long)
        ppn_original_long_divided = re.match(ppn_original_long_pattern, ppn_original_long)
        if ppn_original_long_divided[2]:
            ppn_original = ppn_original_long_divided[2]
        url_ppn_original = r'http://sru.k10plus.de/opac-de-627?version=1.1&operation=searchRetrieve&query=pica.ppn%3D' + ppn_original + r'&maximumRecords=10&recordSchema=marcxml'        
        kxp = urllib.request.urlopen(url_ppn_original)
        tree = xml.etree.ElementTree.parse(kxp)
        root = tree.getroot()
        for step1 in root[2][0][2][0]:
            match step1.get('tag'):
                case "024":
                    bid =classes.BibliographicId()
                    for step2 in step1:
                        match step2.get('code'):
                            case "2":
                                bid.name = step2.text
                            case "a":
                                bid.id = step2.text
                                if bid.id[0:2] == "VD" or bid.id[0:2] == "vd" or bid.id[0:4] == "ISTC":
                                    bid.id = bid.id[4:].strip()
                                if bid.id[0:2] == "GW":
                                    bid.id = bid.id[2:].strip()
                    if bid.name.strip() in ["GW", "ISTC", "VD16", "vd16", "VD17", "vd17", "VD18", "vd18"]:
                        m.bibliographic_id.append(bid)


                case "535":
                    for step2 in step1:
                        match step2.get('code'):
                            case "3":
                                m.shelfmark = step2.text


    
    
                 
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    # Here, most photos show double-pages. They will have to be separated at a later date, and then it will be necessary to sort 
    # out the labels for the individual pages. 
    roman_numerals_plus_brackets = {"M", "m", "D", "d", "C", "c", "X", "x", "V", "v", "I", "i", "J", "j", "[", ""}
    canvas_list = (((manifest["sequences"])[0])["canvases"])
    images = parse_canvas.parse_canvas(canvas_list)    
    m.numberOfImages = len(images)

    
    for im in images:
        #for the label (page-number) of the canvas
        im.label_page = im.label_raw
        #if the canvas_label is a figure or Roman numerlas only, it probably is a page number, and hence "p. " is added. If it is a figure or Roman numerals 
        #but has as last character "r" or "v", it is probably a folio number. 
        if im.label_page and (im.label_page.isnumeric() or all(characters in roman_numerals_plus_brackets for characters in im.label_page)): 
            im.label_prefix = "p. "
        elif im.label_page and (im.label_page[0:-1].isnumeric() or all(characters in roman_numerals_plus_brackets for characters in im.label_page[0:-1])) and (im.label_page[-1] in {"r", "v"}):
            im.label_prefix = "fol. "



    m.images = images
    return m



@classes.func_logger
def parse_manifest_nuernberg_stb (URI_entered): 
    url = urllib.request.urlopen(URI_entered)
    manifest = json.load(url)
    #Step 1/2: Extracting relevant fields from the general section of the Manifest and parsing them
    m = classes.Metadata()
    repository = classes.Organisation()
    bibliographical_reference = ""
    bibliographical_reference_divided = []
    m.license = r'https://creativecommons.org/publicdomain/mark/1.0/' #on the library's website
    m.manifest = url.read()
    classes.Metadata = manifest["classes.Metadata"]
    for step1 in classes.Metadata:
        label = step1["label"]
        if isinstance(label, list):
            for step2 in label:
                if step2["@value"] == "Signatur":
                    m.shelfmark = step1["value"]
        else:
            if step1["label"] == "MD_DV_OWNER":
                repository.name = step1["value"]
                repository.role = "col"
                m.repository.append(repository)
            elif step1["label"] == "Anmerkung":
                bibliographical_reference_long = step1["value"]
    
    if bibliographical_reference_long:
        if ";" in bibliographical_reference_long:
            bibliographical_reference_list = bibliographical_reference_long.split(";")
        else:
            bibliographical_reference_list.append(bibliographical_reference_long)
        for bibliographical_reference_line in bibliographical_reference_list:
            if "GW" or "VD" in bibliographical_reference_line:
                bibliographical_reference_raw = bibliographical_reference_line
                break # There is only one such reference, normally in the first, rarely in the second line, the rest is to be ignored

    if bibliographical_reference_raw:
        if ":" in bibliographical_reference_raw:
            bibliographical_reference_divided = bibliographical_reference_raw.split(":", maxsplit=1)
            bibliographical_reference = bibliographical_reference_divided[1] # suppressing a preliminary '
        else: 
            bibliographical_reference = bibliographical_reference_raw
        bid =classes.BibliographicId()
        if bibliographical_reference[0:2] == "VD":
            bid.name = bibliographical_reference[0:4]
            bid.id = bibliographical_reference[5:].strip()
            m.bibliographic_id.append(bid)
        if bibliographical_reference[0:2] == "GW":
            bid.name = bibliographical_reference[0:2]
            bid.id = bibliographical_reference[3:].strip()
            m.bibliographic_id.append(bid)
    
                 
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    # Here, most photos show double-pages. They will have to be separated at a later date, and then it will be necessary to sort 
    # out the labels for the individual pages. 
    roman_numerals_plus_brackets = {"M", "m", "D", "d", "C", "c", "X", "x", "V", "v", "I", "i", "J", "j", "[", ""}
    canvas_list = (((manifest["sequences"])[0])["canvases"])
    images = parse_canvas.parse_canvas(canvas_list)    
    m.numberOfImages = len(images)

    
    for im in images:
        #for the label (page-number) of the canvas
        if im.label_raw != " - ": 
            im.label_page = im.label_raw
        #if the canvas_label is a figure or Roman numerlas only, it probably is a page number, and hence "p. " is added. If it is a figure or Roman numerals 
        #but has as last character "r" or "v", it is probably a folio number. 
        if im.label_page and (im.label_page.isnumeric() or all(characters in roman_numerals_plus_brackets for characters in im.label_page)): 
            im.label_prefix = "p. "
        elif im.label_page and (im.label_page[0:-1].isnumeric() or all(characters in roman_numerals_plus_brackets for characters in im.label_page[0:-1])) and (im.label_page[-1] in {"r", "v"}):
            im.label_prefix = "fol. "


    m.images = images
    return m

@classes.func_logger
def parse_manifest_manuscriptorium (URI_entered): 
    # This database seems to contain only manuscripts, hence there is no provision for printed books here
    url = urllib.request.urlopen(URI_entered)
    manifest = json.load(url)
    #Step 1/2: Extracting relevant fields from the general section of the Manifest and parsing them
    m = classes.Metadata()
    repository = classes.Organisation()
    bibliographical_reference = ""
    bibliographical_reference_divided = []
    m.license = manifest["license"]
    m.manifest = url.read()
    classes.Metadata = manifest["classes.Metadata"]
    for step1 in classes.Metadata:
        label = step1["label"]
        if step1["label"] == "Repository":
            repository.name = step1["value"]
            repository.role = "col"
            m.repository.append(repository)
        elif step1["label"] == "Shelfmark/Identifyer":
            m.shelfmark = step1["value"]
    
                 
    #Step 3: Extracting the relevant fields for the records on individual pages in the manifest and transforming them into database format
    # Here, most photos show double-pages. They will have to be separated at a later date, and then it will be necessary to sort 
    # out the labels for the individual pages. 
    roman_numerals_plus_brackets = {"M", "m", "D", "d", "C", "c", "X", "x", "V", "v", "I", "i", "J", "j", "[", ""}
    canvas_list = (((manifest["sequences"])[0])["canvases"])
    images = parse_canvas.parse_canvas(canvas_list)    
    m.numberOfImages = len(images)

    
    for im in images:
        #for the label (page-number) of the canvas
        if im.label_raw != " - ": 
            im.label_page = im.label_raw
        #if the canvas_label is a figure or Roman numerlas only, it probably is a page number, and hence "p. " is added. If it is a figure or Roman numerals 
        #but has as last character "r" or "v", it is probably a folio number. 
        if im.label_page and (im.label_page.isnumeric() or all(characters in roman_numerals_plus_brackets for characters in im.label_page)): 
            im.label_prefix = "p. "
        elif im.label_page and (im.label_page[0:-1].isnumeric() or all(characters in roman_numerals_plus_brackets for characters in im.label_page[0:-1])) and (im.label_page[-1] in {"r", "v"}):
            im.label_prefix = "fol. "


    m.images = images
    return m
