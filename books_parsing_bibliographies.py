# This module contains a number of functions for extracting bibliographical information from standard bibliographies such as the VD16. 
# Eventually, this information will be added to the book_properties record from book_parsing_manifests. 
# There has to be a function for every bibliography (perhaps altogether about 10 the end)

import urllib.request
import xml.etree.ElementTree
import re
from lxml import etree
import requests
from classes import *

def VD17_parsing(url_bibliography):
    #This function can be used for parsing both the VD17 and the VD18
    print(url_bibliography)
    printing_information_pattern = r'(.*)(: )(.*)'
    bi = Bibliographic_information()
    #url_bibliography = r"http://sru.k10plus.de/vd17?version=2.0&operation=searchRetrieve&query=pica.vds=" + bibliographic_id_number + r'&maximumRecords=10&startRecord=1&recordSchema=marcxml'
    url = urllib.request.urlopen(url_bibliography)
    tree = xml.etree.ElementTree.parse(url)
    root = tree.getroot()
    record = root[1][0][2][0]
    if "a4" in record[0].text: #The first part of the record is the so-called 'leader'. It is here not constructed according to the usual rules.
        # However, it appears that it contains the signs "a4" only if it describes a series, not an individual book. In this case, the record
        # is not to be used. 
        # This needs to be changed!!
        return ""
    else:
        for step1 in record:
            field = step1            
            match field.get('tag'):
                case "024": #for the VD17 number
                    bid = Bibliographic_id()
                    for step2 in field:                                            
                        match(step2.get("code")):                        
                            case "a":                                
                                bid.id = step2.text
                                if bid.id[0:4] == "VD18":
                                    bid.id = bid.id[5:]                        
                            case "2":
                                bid.name = step2.text
                    if bid.name == "vd17":
                        bid.uri = r'https://kxp.k10plus.de/DB=1.28/CMD?ACT=SRCHA&IKT=8079&TRM=%27' + bid.id + '%27'
                    if bid.name == "vd18": 
                        bid.uri = r'https://vd18.k10plus.de/SET=2/TTL=1/CMD?ACT=SRCHA&IKT=8080&SRT=YOP&TRM=VD18' + bid.id + '&ADI_MAT=B'
                    bi.bibliographic_id.append(bid) # in the VD17, there is only one ID, this list is only introduced for the sake of consistence with incunables
#                        single_place = (place_name, place_id, place_role)
                    print("vorher: ")
                    print(bid.id)
                    print("gesamt: ")
                    print(bid)
                    
                case "100": #for the author
                    pe = Person()
                    for step2 in field:                     
                        match(step2.get("code")):
                            case "a":
                                pe.name = step2.text
                            case "0":
                                if "(DE-588)" in step2.text:                                
                                    pe.id = (step2.text)[8:] # here and elsewhere: to suppress the "(DE-588)"   
                                    pe.id_name = "GND"                             
                    pe.role = "aut"                        
                    bi.persons.append(pe)
#                    print("vorher:" + pe.name)
#                    print("nachher: " + bi.persons)
                case "245": # for title and volume number
                    for step2 in field:                                    
                        match(step2.get("code")):
                            case "a":                            
                                bi.title = step2.text                        
                            case "n":
                                bi.volume_number = step2.text
                            case "p":
                                bi.part_title = step2.text

                case "264": #for the date
                    for step2 in field:
                        match(step2.get("code")):
                            case "c":
                                bi.printing_date = step2.text
                case "500":  #for the original statement of publication (in order to manually indicate who is printer and who is publisher)                
                    for step2 in field:
                        if "Vorlageform des Erscheinungsvermerks" in step2.text:
                            printing_information_divided = re.match(printing_information_pattern, step2.text)
                            bi.printing_information = printing_information_divided[3]
                case "700": #for printers and publishers 
                    pe = Person()
                    for step2 in field:
                        match(step2.get("code")):
                            case "a":
                                pe.name = step2.text
                            case "0":
                                if "(DE-588)" in step2.text:
                                    pe.id = (step2.text)[8:]
                                    pe.id_name = "GND"
                                    #person_id_divided = re.match(gnd_pattern, field[step2].text)
                                    #person_id = person_id_divided[2]
                            case "4":
                                if step2.text == "prt":
                                    pe.role = "prt"
                                if step2.text == "pbl":
                                    pe.role = "pbl"
                                if step2.text == "rsp":
                                    pe.role = "rsp"
                                if step2.text == "aut":
                                    pe.role = "aut"
                    if pe.role != "":
#                        single_person = (person_name, person_id, person_role)                
                        bi.persons.append(pe)
                case "710":
                    org = Organisation()
                    for step2 in field:
                        match(step2.get("code")):
                            case "a":
                                org.name = step2.text
                            case "0":
                                if "(DE-588)" in step2.text:
                                    org.id = (step2.text)[8:]
                                    org.id_name = "GND"
                                    #person_id_divided = re.match(gnd_pattern, field[step2].text)
                                    #person_id = person_id_divided[2]
                            case "4":
                                if step2.text == "prt":
                                    org.role = "prt"
                                if step2.text == "pbl":
                                    org.role = "pbl"
                    if org.role != "":
#                        single_person = (person_name, person_id, person_role)                
                        bi.organisations.append(org)


                case "751": #for the places of printing and publishing
#                        place_id = ""
#                        place_role = ""
                        pl = Place()
                        for step2 in field:
                            match(step2.get("code")):
                                case "a":
                                    pl.name = step2.text                                
                                case "0":
                                    if "(DE-588)" in step2.text:
                                        pl.id = (step2.text)[8:]  
                                        pl.id_name = "GND"                                  
                                case "4":
                                    if step2.text == "pup":
                                        pl.role = "pup"
                                    if step2.text == "mfp":
                                        pl.role = "mfp"
                        #bibliographic_id_single = (bibliographic_id_name, bibliographic_id_number)
                        bi.places.append(pl)
 #       return bibliographic_id_list, person_list, place_list, title, volume_number, part_title, printing_date, printing_information
        print("bibliographic information from VD17:")
        print(bi)
        return bi

def VD16_parsing(url_bibliography):    
    url = urllib.request.urlopen(url_bibliography)
    raw = url.read()
    tree = etree.HTML(raw)
    record_structured = {}

    bi = Bibliographic_information()
    try: 
        record_text = etree.tostring(tree,encoding=str)
    except TypeError:
        return
    record_removal = r'(<var>|<strong>|<strong class="c2">|</strong>|</li>|<ul>|</p></div>)'
    record_cleaned = re.sub(record_removal, "", record_text)                         
    record_pattern = r'(.*)(Erfassungsdatum)(.*)' #cut off everything after 'Permalink'
    record_parts = re.match(record_pattern, record_cleaned, re.DOTALL)
    record_parts_standardised = record_parts[1].replace("Normnummer", "<br/>Normnummer") #The first line, 'Normummer', does not start with 'Break', 
    # I insert this so that the records can be chopped up properly
    record_divided = re.split("<br/>", record_parts_standardised) #divide record into individual lines
    record_line_pattern = r'(.*?)(\: )(.*)'
    for record_line in record_divided:        
            record_line_divided = re.match(record_line_pattern, record_line) #divide record into key-value-pairs
            if record_line_divided:
                record_structured[record_line_divided[1]]=record_line_divided[3]
    print(record_structured)

    #parsing the individual values
    bibliographic_id = record_structured["Normnummer"]
    bibliographic_id_pattern = r'(....)(\s)([A-Z]{1,2}\s[0-9]{1,5})(.*)'
    bid = Bibliographic_id()
    bid.name = re.match(bibliographic_id_pattern, bibliographic_id)[1]
    bid.id = re.match(bibliographic_id_pattern, bibliographic_id)[3]
#    bibliographic_id_single = (bibliographic_id_name, bibliographic_id_number)
    bi.bibliographic_id.append(bid)
#    bibliographic_id_list.append(bibliographic_id_single)  # in the VD16, there is only one ID, this list is only introduced for the sake of consistence with incunables

    #person_list_pattern = r'<a href.*?</a>'
    person_single_pattern = r'(<a h.*?>)(.*?)(&.*?</a>)(.*)?(DE-588)?(.*)?(: Datensatz)?(.*)?'
#    person_single_pattern = r'(<a h.*?>)(.*?)(</a>)(.*?)(DE-588)?(.*)?(: Datensatz)?(.*)?'
    ###currently, the system only reads the last author or contributor, and it does not read his bibliographic ID number. 
    if "Verfasser" in record_structured:
        pe = Person()
        author = record_structured["Verfasser"]
        print("Author found")
        print(author)
        #author_list_divided = re.findall(person_list_pattern, author_list)
        #for step1 in author_list_divided:
        author_single_divided = re.match(person_single_pattern, author)
        pe.name = author_single_divided[2]
        pe.id = author_single_divided[6] #That doesn't work!
        pe.role = "aut"
        bi.persons.append(pe)
    if "Weitere Pers." in record_structured:
        weitere_pers_list = record_structured["Weitere Pers."]
        weitere_pers_list_divided = re.findall(person_list_pattern, weitere_pers_list)
        for step4 in weitere_pers_list_divided:
            pe = Person()
            weitere_pers_single_divided = re.match(person_single_pattern, step4)
            pe.name = weitere_pers_single_divided[2]
            pe.id = weitere_pers_single_divided[4]
            if r"¬[Bearb.]¬" in pe.name:
                pe.name = pe.name[0:-11]
                pe.role = "edt"
            else:
                pe.role = "aut"
            bi.persons.append(pe)
    if "Impressum" in record_structured:
        impressum = record_structured["Impressum"]
        impressum_pattern = r'([^:]*)(: )?([^;]*)?( ; )?([^:]*)?(: )?(.*)?(, )([^,]*)'
        impressum_divided = re.match(impressum_pattern, impressum)
        pl = Place()
        pl.name = impressum_divided[1]
        pl.role = "mfp"
        bi.places.append(pl)
        if impressum_divided[5]:
            pl = Place()
            pl.name = impressum_divided[5]
            place.role = "pup"
            bi.places.append(pl)
        if not impressum_divided[5] and impressum_divided[7]: #if the printer (in section 3) and the publisher (in section 7) are in the same place, this place name 
            #is only given in section 1 and not repeated in section 5. However, it needs to entered twice into the database, as place of publishing and as place of printing.
            pl = Place()
            pl.name = impressum_divided[1]
            pl.role = "pup"
            bi.places.append(pl)           
        if impressum_divided[3]:
            impressum_single_person1 = re.split(" und ", impressum_divided[3])   #If there are several printers or several publishers,
            #they are separated by "und" (at least, if there are two, I don't know what happens with three, and this is extremely rare)
            for step2 in impressum_single_person1:
                pe = Person()
                pe.name = step2
                pe.role = "prt"
                bi.persons.append(pe)
        if impressum_divided[7]:
            impressum_single_person2 = re.split(" und ", impressum_divided[7])
            for step3 in impressum_single_person2:
                pe = Person()
                pe.name = step3
                pe.role = "pbl"
                bi.persons.append(pe)                
        if impressum_divided[9]:
            bi.printing_date = impressum_divided[9]
        bi.title=record_structured["Titel"]
        bi.printing_information = record_structured["Ausgabebezeichnung"]
        return bi




def ISTC_parsing(URL_bibliography):
    # I have two problems concerning the API I used here to download the data - if they are solved, some parts of the programme
    # should be changed
    # (1): I downloaded the "imprint" section as a unit and had to divide it into place, printer(s), and date, which works ok.
    # This should not be necessary since it should be possible to download them in separate fields, however, this did not work.
    # (2): in a small number of cases, the system gives two different "imprints" (because there is some uncertainty). 
    #: Oddly, the API only downloads the first of them and ignores all the others. If several can be downloaded, one needs a 
    # loop to parse all of them one by one. 
    bibliographic_id_list = []
    person_list = []
    place_list = []
    author = ""
    bi = Bibliographic_information()
    istc_record_raw = requests.get(URL_bibliography)    
    istc_record_full = (istc_record_raw).json()
       
    if (istc_record_full["hits"])["value"] == 0:
        print("No hits")
        return

    istc_record_short = (istc_record_full["rows"])[0]
    bid = Bibliographic_id()
    bid.id = istc_record_short["id"]
    bid.name = "ISTC"
    bid.uri = r"https://data.cerl.org/istc/"+bid.id
    bi.bibliographic_id.append(bid)
    #bibliographic_id_single_1 = ("ISTC", bibliographic_id_number_1)
    #bibliographic_id_list.append(bibliographic_id_single_1)
    for step1 in istc_record_short['references']:        
        if step1[0:3] == "GW ":            
            bid = Bibliographic_id()
            bid.id = step1[3:]
            bid.name = "GW"
#            bid.uri = This will need more work!
            bi.bibliographic_id.append(bid)
            #bibliographic_id_single_2 = ("GW", bibliographic_id_number_2)
            #bibliographic_id_list.append(bibliographic_id_single_2)


    if "author" in istc_record_short:
        pe = Person()
        pe.name = istc_record_short["author"]
        pe.role = "aut"
        #author_single = (author, "", "aut")
        bi.persons.append(pe)
        #person_list.append(author_single)

    if "imprint" in istc_record_short:
        printing_information = istc_record_short["imprint"]
        bi.printing_information = printing_information
        printing_information = printing_information.replace(r"[", "")
        printing_information = printing_information.replace(r"]", "")        
        printing_information_pattern =  r"([^:]*)(: .*)?(, [^,]*)$"
        printing_information_divided = re.match(printing_information_pattern, printing_information)
        pl = Place()
        pl.name = (printing_information_divided[1]).strip()
        pl.role = "mfp"
        bi.places.append(pl)
        #place_single = (place, "", "mfp")
        #place_list.append(place_single)
        printer_raw = (printing_information_divided[2][2:]).strip()
        if ", for " in printer_raw:
            #the 'for' means that there are a printer and a publisher. In this case, the publisher's town is not indicated
            printer_divided = re.split(", for ", printer_raw)
            printer_only = printer_divided[0]
            publisher_only = printer_divided[1]
            pl = Place()
            pl.name = (printing_information_divided[1]).strip()
            pl.role = "pup"
            bi.places.append(pl)
            #place_single = (place, "", "pup")
            #place_list.append(place_single)
            if " and " in publisher_only:
                publisher_divided = re.split(" and ", publisher_only)
                pe = Person()
                pe.name = publisher_divided[0]
                pe.role = "pbl"
                bi.persons.append(pe)
                #person_list.append(person_single)
                pe = Person()
                pe.name = publisher_divided[1]
                pe.role = "pbl"
                bi.persons.append(pe)
                #person_list.append(person_single)
            else:
                pe = Person()
                pe.name = publisher_only
                pe.role = "pbl"
                bi.persons.append(pe)
        else:
            printer_only = printer_raw
        if " and " in printer_only: 
            # in case of two printers with the same surname, the entry reads "John and Paul Smith", leading to the two printers
            # "JOhn" ad "Paul Smith". This happens very rarely and should be corrected manually. 
            printer_divided = re.split(" and ", printer_only)
            pe = Person()
            pe.name = printer_divided[0]
            pe.role = "prt"
            bi.persons.append(pe)
            #person_list.append(person_single)
            pe = Person()
            pe.name = printer_divided[1]
            pe.role = "prt"
            bi.persons.append(pe)
        else:
            pe = Person()
            pe.name = printer_only
            pe.role = "prt"
            bi.persons.append(pe)
            #person_list.append(person_single)
        bi.printing_date = (printing_information_divided[3][2:]).strip()
        if "title" in istc_record_short:
            bi.title = istc_record_short["title"] 
    return bi
    #return(bibliographic_id_list, person_list, place_list, title, "", "", printing_date, printing_information)