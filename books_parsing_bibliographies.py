#pylint: disable=C0302
"""
This module contains a number of functions for extracting bibliographical information 
from standard bibliographies such as the VD16. 
Eventually, this information will be added to the book_properties record 
from book_parsing_manifests. 
There has to be a function for every bibliography (perhaps altogether about 10 the end)
"""
import urllib.request
import xml.etree.ElementTree
import re
from lxml import etree
import requests
import classes
from parsing_helpers import convert_roman_numerals

@classes.func_logger
def parse_vd17(url_bibliography):
    """
This function can be used for parsing both the VD17 and the VD18
    """
    print(url_bibliography)
    printing_information_pattern = r'(.*)(: )(.*)'
    bi = classes.BibliographicInformation()
    #url_bibliography = r"http://sru.k10plus.de/vd17?version=2.0\
    # &operation=searchRetrieve&query=pica.vds=" + \
    # bibliographic_id_number + r'&maximumRecords=10&startRecord=1&recordSchema=marcxml'
    url = urllib.request.urlopen(url_bibliography)
    tree = xml.etree.ElementTree.parse(url)
    root = tree.getroot()
    record = root[1][0][2][0]
    if "a4" in record[0].text: #The first part of the record is the so-called 'leader'.
        #It is here not constructed according to the usual rules.
        # However, it appears that it contains the signs "a4" only if it describes a series,
        # not an individual book. In this case, the record
        # is not to be used.
        # This needs to be changed!!
        return ""
    else:
        for step1 in record:
            field = step1
            match field.get('tag'):
                case "024": #for the VD17 number
                    bid = classes.BibliographicId()
                    for step2 in field:
                        match(step2.get("code")):
                            case "a":
                                bid.id = step2.text
                                if bid.id[0:4] == "VD18":
                                    bid.id = bid.id[5:]
                            case "2":
                                bid.name = step2.text
                    if bid.name == "vd17":
                        bid.uri = r'https://kxp.k10plus.de/DB=1.28/CMD?ACT=SRCHA&IKT=8079&TRM=%27' \
                            + bid.id + '%27'
                        bi.bibliographic_id.append(bid) # in the VD17, there is only one ID,
                        #this list is only introduced for the sake of consistence with incunables
#                        single_place = (place_name, place_id, place_role)

                    if bid.name == "vd18":
                        bid.uri = r'https://vd18.k10plus.de/SET=2/TTL=1/CMD?ACT=\
                            SRCHA&IKT=8080&SRT=YOP&TRM=VD18' + bid.id + '&ADI_MAT=B'

                        bi.bibliographic_id.append(bid) # in the VD18, there is only one ID,
                        #this list is only introduced for the sake of consistence with incunables
#                        single_place = (place_name, place_id, place_role)
                    print("vorher: ")
                    print(bid.id)
                    print("gesamt: ")
                    print(bid)

                case "100": #for the author
                    pe = classes.Person()
                    for step2 in field:
                        match(step2.get("code")):
                            case "a":
                                pe.name = step2.text
                            case "0":
                                if "(DE-588)" in step2.text:
                                    pe.id = (step2.text)[8:]
                                    # here and elsewhere: to suppress the "(DE-588)"
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
                                printing_date_raw = step2.text.strip()
                case "500":  #for the original statement of publication
                    #(in order to manually indicate who is printer and who is publisher)
                    for step2 in field:
                        if "Vorlageform" in step2.text:
                            printing_information_divided = \
                                re.match(printing_information_pattern, step2.text)
                            bi.printing_information = printing_information_divided[3]
                case "700": #for printers and publishers
                    pe = classes.Person()
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
                    org = classes.Organisation()
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
                    pl = classes.Place()
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
                                elif step2.text == "mfp":
                                    pl.role = "mfp"
                                elif step2.text == "uvp":
                                    pl.role = "uvp"
                                        # I am not sure if I should not suppress 'uvp'????
                        #bibliographic_id_single = (bibliographic_id_name, bibliographic_id_number)
                        bi.places.append(pl)
 #       return bibliographic_id_list, person_list, place_list,
            # title, volume_number, part_title, printing_date, printing_information
        year_pattern_isolated = r'\d{4}'
        year_pattern_brackets = r'\[(ca. |ca.|ca |circa |um |vor |nicht vor \
            |nach |nicht nach |erschienen |erschienen ca. \
            |erschienen nach |i.e. )?(\d{4})?([MDCLXVI\.]*)?(\?|\? )?(/\d{2}|/\d{4})?\]'
        year_pattern_arabic_in_text = r'(1\d{3})[\D$]?'
        # should mean 1XXX, then a non-number or end of string
        year_pattern_roman_in_text = r'(M[DCLXVI\. ]*)'
        if printing_date_raw:
            print("Rohdatum: ")
            print(printing_date_raw)
            if re.match(year_pattern_isolated, printing_date_raw):
                # This means ca. 80% of the cases, when there is just a four-digit year
                print("Year simple number")
                bi.date_string = printing_date_raw
                start_year = int(printing_date_raw)
                end_year = int(printing_date_raw)
            elif re.search(year_pattern_brackets, printing_date_raw):
                # If there is a date given in brackets, it should be the preferred form to use
                printing_date_divided = re.search(year_pattern_brackets, printing_date_raw).groups()
                print("Year in square brackets matched")
                if printing_date_divided[1]:
                    print("year string: " + printing_date_divided[1])
                    year_string = printing_date_divided[1]
                    bi.date_string = year_string
                    start_year = int(year_string)
                    end_year = int(year_string)
                elif printing_date_divided[2]:
                    year_string = convert_roman_numerals(printing_date_divided[2])
                    bi.date_string = year_string
                    start_year = int(year_string)
                    end_year = int(year_string)
                if printing_date_divided[4]: #if there is a second year given as end of a period
                    year_end_string = printing_date_divided[4][1:]
                    print("Year_end_string found: ")
                    print(year_end_string)
                    if len(year_end_string) == 2: #if there are only two digits
                        year_end_string = "17" + year_end_string
                    year_string = year_string + " / " + year_end_string
                    bi.date_string = year_string
                    end_year = int(year_end_string)
                if printing_date_divided[0]:
                    print("Year in square brackets with Prefix")
                    match printing_date_divided[0]:
                        case "erschienen ":
                            bi.date_string = year_string
                            start_year = int(year_string)
                            end_year = int(year_string)
                        case "ca. "|"ca."|"ca "|"circa "|"um "|"erschienen ca. ":
                            bi.date_string =  "about " + year_string
                            start_year = int(year_string)- 2
                            end_year = int(year_string) + 2
                        case "vor ": # I include the year for 'before' in the string
                            #since I am not sure if it always means 'before Jan 1st'
                            bi.date_string =  "before " + year_string
                            start_year = int(year_string) - 5
                            end_year = int(year_string)
                        case "nach "|"erschienen nach ": # cf. comment on "vor "
                            bi.date_string =  "after " + year_string
                            start_year = int(year_string)
                            end_year = int(year_string) + 5
                        case "nicht vor ":
                            bi.date_string =  "not before " + year_string
                            start_year = int(year_string)
                            end_year = int(year_string) + 5
                        case "nicht nach ":
                            bi.date_string =  "not after " + year_string
                            start_year = int(year_string) - 5
                            end_year = int(year_string)
                        case "i.e. ":
                            bi.date_string = year_string + " (corrected date)"
                            start_year = int(year_string)
                            end_year = int(year_string)
                if printing_date_divided[3] == "?" or printing_date_divided[3] == "? ":
                    bi.date_string = bi.date_string + "?"
            else: # This means that there the original datestring
                #from the book that will hopefully contain a legible date
                printing_date_raw = printing_date_raw.replace("[", "")
                printing_date_raw = printing_date_raw.replace("]", "")
                #date_string = date_string.replace("M D", "MD")
                #date_string = date_string.replace("D C", "DC")

                if re.search(year_pattern_arabic_in_text, printing_date_raw):
                    #This means that if there is a four-digit date
                    # starting with '1' in the text and nothing in square brackets
                    year_string = re.search(year_pattern_arabic_in_text, \
                        printing_date_raw).groups()[0]
                    print("four arabic digits found in text")
                    bi.date_string = year_string
                    start_year = int(year_string)
                    end_year = int(year_string)
                if re.search(year_pattern_roman_in_text, printing_date_raw):
                    # This means that there is a string in Roman numerals starting with "M"
                    year_string = convert_roman_numerals(re.search(year_pattern_roman_in_text, \
                        printing_date_raw).groups()[0])
                    bi.date_string = year_string
                    print("Year in Roman numerals:")
                    print(bi.date_string)
                    start_year = int(year_string)
                    end_year = int(year_string)
                elif "18. Jh." in printing_date_raw or "18.Jh." in printing_date_raw:
                    bi.date_string = "18th century"
                    start_year = 1701
                    end_year = 1800

                else:
                    print("year not digested")
            bi.date_start = (start_year, 1, 1)
            bi.date_end = (end_year, 12, 31)
#            bi.date_start = datetime(start_year, 1, 1, 0, 0, 0, 0)
#           #There are apparently never months or days in standardised format.
#            bi.date_end = datetime(end_year, 12, 31, 23, 59, 59, 0)
#            if bi.date_string:
#                print(bi.date_string)
#                print(bi.date_start.isoformat())
#                print(bi.date_end.isoformat())
#                bi.printing_date = bi.date_string + " (" + bi.date_start.isoformat()[0:10] + \
#                " - " + bi.date_end.isoformat()[0:10] + ")"
        print("bibliographic information from VD17:")
        print(bi)
        return bi

@classes.func_logger
def parse_vd16(url_bibliography):
    """This version parses the VD16, the catalogue of German 16th-century printed books
    # NB: currently, this data is only available as HTML.
    # I built this code for the original version,
    # and it does not fully work for the current Beta version.
    # Since it is planned to make export possible as MARCXML
    # I do not want to sepnd much time making improvements here.
    # For instance, it seems to display only the last of several authors in the moment."""
    url = urllib.request.urlopen(url_bibliography)
    raw = url.read()
    tree = etree.HTML(raw)
    record_structured = {}
    printing_date_long = ""
    printing_date_divided = []

    bi = classes.BibliographicInformation()
    try:
        record_text = etree.tostring(tree,encoding=str)
    except TypeError:
        return
    record_removal = r'(<var>|<strong>|<strong class="c2">|</strong>|</li>|<ul>|</p></div>)'
    record_cleaned = re.sub(record_removal, "", record_text)
    record_pattern = r'(.*)(Erfassungsdatum)(.*)' #cut off everything after 'Permalink'
    record_parts = re.match(record_pattern, record_cleaned, re.DOTALL)
    record_parts_standardised = record_parts[1].replace("Normnummer", "<br/>Normnummer")
    #The first line, 'Normummer', does not start with 'Break',
    # I insert this so that the records can be chopped up properly
    record_divided = re.split("<br/>", record_parts_standardised)
    #divide record into individual lines
    record_line_pattern = r'(.*?)(\: )(.*)'
    for record_line in record_divided:
        record_line_divided = re.match(record_line_pattern, record_line)
        #divide record into key-value-pairs
        if record_line_divided:
            record_structured[record_line_divided[1]]=record_line_divided[3]
    print(record_structured)

    #parsing the individual values
    bibliographic_id = record_structured["Normnummer"]
    bibliographic_id_pattern = r'(....)(\s)([A-Z]{1,2}\s[0-9]{1,5})(.*)'
    bid = classes.BibliographicId()
    bid.name = re.match(bibliographic_id_pattern, bibliographic_id)[1]
    bid.id = re.match(bibliographic_id_pattern, bibliographic_id)[3]
#    bibliographic_id_single = (bibliographic_id_name, bibliographic_id_number)
    bi.bibliographic_id.append(bid)
#    bibliographic_id_list.append(bibliographic_id_single)
#   in the VD16, there is only one ID,
#   this list is only introduced for the sake of consistence with incunables

    person_list_pattern = r'<a href.*?</a>'
    person_single_pattern = r'(<a h.*?>)(.*?)(</a>|&.*?</a>)(.*)?(DE-588)?(.*)?(: Datensatz)?(.*)?'
#    person_single_pattern = r'(<a h.*?>)(.*?)(</a>)(.*?)(DE-588)?(.*)?(: Datensatz)?(.*)?'
    ###currently, the system only reads the last author or contributor,
    # and it does not read his bibliographic ID number.
    if "Verfasser" in record_structured:
        pe = classes.Person()
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
            pe = classes.Person()
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
        impressum_pattern = r'([^:]*)(: )?([^;]*)?(; )?([^:]*)?(: )?(.*)?(, )([^,]*)'
        impressum_divided = re.match(impressum_pattern, impressum)
        pl = classes.Place()
        pl.name = impressum_divided[1]
        pl.role = "mfp"
        bi.places.append(pl)
        if impressum_divided[5]:
            pl = classes.Place()
            pl.name = impressum_divided[5]
            pl.role = "pup"
            bi.places.append(pl)
        if not impressum_divided[5] and impressum_divided[7]:
            #if the printer (in section 3) and the publisher (in section 7)
            # are in the same place, this place name
            #is only given in section 1 and not repeated in section 5.
            # However, it needs to entered twice into the database,
            # as place of publishing and as place of printing.
            pl = classes.Place()
            pl.name = impressum_divided[1]
            pl.role = "pup"
            bi.places.append(pl)
        if impressum_divided[3]:
            impressum_single_person1 = re.split(" und ", impressum_divided[3])
            #If there are several printers or several publishers,
            #they are separated by "und" (at least, if there are two,
            # I don't know what happens with three, and this is extremely rare)
            for step2 in impressum_single_person1:
                pe = classes.Person()
                pe.name = step2
                pe.role = "prt"
                bi.persons.append(pe)
        if impressum_divided[7]:
            impressum_single_person2 = re.split(" und ", impressum_divided[7])
            for step3 in impressum_single_person2:
                pe = classes.Person()
                pe.name = step3
                pe.role = "pbl"
                bi.persons.append(pe)
        if impressum_divided[9]:
            printing_date_long = impressum_divided[9]
        bi.title=record_structured["Titel"]
        bi.printing_information = record_structured["Ausgabebezeichnung"]
    # Although some early 16th-century books give a day, the date field in the VD16 only contains
    #  a year, two years separated by "/" (two different years given in the book) "-"
    if printing_date_long != "":
        if "/" in printing_date_long:
            printing_date_divided = printing_date_long.split("/")
        elif "-" in printing_date_long:
            printing_date_divided = printing_date_long.split("-")
        else:
            printing_date_long = printing_date_long.strip()
            if len(printing_date_long) == 4: # If there are only four digits
                bi.date_string = printing_date_long
                start_year = int(printing_date_long)
                end_year = int(printing_date_long)


        if printing_date_divided != []:
            if len(printing_date_divided[1]) == 2:
                #If for the second year only the last two digits are given
                printing_date_divided[1] = "15" + printing_date_divided[1]
            if int(printing_date_divided[0]) < int(printing_date_divided[1]):
                #if the first figure is lower (this is not always the case)
                bi.date_string = printing_date_divided[0] + "-" + printing_date_divided[1]
                start_year = int(printing_date_divided[0])
                end_year = int(printing_date_divided[1])
            else:
                bi.date_string = printing_date_divided[1] + "-" + printing_date_divided[0]
                start_year = int(printing_date_divided[1])
                end_year = int(printing_date_divided[0])
        start_day = 1
        start_month = 1
        end_day = 31
        end_month = 12
        #bi.date_start = datetime(start_year, start_month, start_day, 0, 0, 0, 0)
        #bi.date_end = datetime(end_year, end_month, end_day, 23, 59, 59, 0)
        #bi.printing_date = bi.date_string + " (" + bi.date_start.isoformat()[0:10] +
        # " - " + bi.date_end.isoformat()[0:10] + ")"
        bi.date_start = (start_year, start_month, start_day)
        bi.date_end = (end_year, end_month, end_day)
    return bi



def istc_parsing_alt(url_bibliography):
    """Is this even in use????"""
    # I have two problems concerning the API I used here to download the data
    # - if they are solved, some parts of the programme
    # should be changed
    # (1): I downloaded the "imprint" section as a unit and had to
    # divide it into place, printer(s), and date, which works ok.
    # This should not be necessary since it should be possible
    # to download them in separate fields, however, this did not work.
    # (2): in a small number of cases, the system gives
    # two different "imprints" (because there is some uncertainty).
    # Oddly, the API only downloads the first of them and ignores all the others.
    # If several can be downloaded, one needs a loop to parse all of them one by one.
    bi = classes.BibliographicInformation()
    istc_record_raw = requests.get(url_bibliography, timeout = 10)
    istc_record_full = (istc_record_raw).json()

    if (istc_record_full["hits"])["value"] == 0:
        print("No hits")
        return

    istc_record_short = (istc_record_full["rows"])[0]
    bid = classes.BibliographicId()
    bid.id = istc_record_short["id"]
    bid.name = "ISTC"
    bid.uri = r"https://data.cerl.org/istc/"+bid.id
    bi.bibliographic_id.append(bid)
    #bibliographic_id_single_1 = ("ISTC", bibliographic_id_number_1)
    #bibliographic_id_list.append(bibliographic_id_single_1)
    for step1 in istc_record_short['references']:
        if step1[0:3] == "GW ":
            bid = classes.BibliographicId()
            bid.id = step1[3:]
            bid.name = "GW"
#            bid.uri = This will need more work!
            bi.bibliographic_id.append(bid)
            #bibliographic_id_single_2 = ("GW", bibliographic_id_number_2)
            #bibliographic_id_list.append(bibliographic_id_single_2)


    if "author" in istc_record_short:
        pe = classes.Person()
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
        pl = classes.Place()
        pl.name = (printing_information_divided[1]).strip()
        pl.role = "mfp"
        bi.places.append(pl)
        #place_single = (place, "", "mfp")
        #place_list.append(place_single)
        printer_raw = (printing_information_divided[2][2:]).strip()
        if ", for " in printer_raw:
            #the 'for' means that there are a printer and a publisher.
            # In this case, the publisher's town is not indicated
            printer_divided = re.split(", for ", printer_raw)
            printer_only = printer_divided[0]
            publisher_only = printer_divided[1]
            pl = classes.Place()
            pl.name = (printing_information_divided[1]).strip()
            pl.role = "pup"
            bi.places.append(pl)
            #place_single = (place, "", "pup")
            #place_list.append(place_single)
            if " and " in publisher_only:
                publisher_divided = re.split(" and ", publisher_only)
                pe = classes.Person()
                pe.name = publisher_divided[0]
                pe.role = "pbl"
                bi.persons.append(pe)
                #person_list.append(person_single)
                pe = classes.Person()
                pe.name = publisher_divided[1]
                pe.role = "pbl"
                bi.persons.append(pe)
                #person_list.append(person_single)
            else:
                pe = classes.Person()
                pe.name = publisher_only
                pe.role = "pbl"
                bi.persons.append(pe)
        else:
            printer_only = printer_raw
        if " and " in printer_only:
            # in case of two printers with the same surname,
            # the entry reads "John and Paul Smith", leading to the two printers
            # "JOhn" ad "Paul Smith". This happens very rarely and should be corrected manually.
            printer_divided = re.split(" and ", printer_only)
            pe = classes.Person()
            pe.name = printer_divided[0]
            pe.role = "prt"
            bi.persons.append(pe)
            #person_list.append(person_single)
            pe = classes.Person()
            pe.name = printer_divided[1]
            pe.role = "prt"
            bi.persons.append(pe)
        else:
            pe = classes.Person()
            pe.name = printer_only
            pe.role = "prt"
            bi.persons.append(pe)
            #person_list.append(person_single)
        bi.printing_date = (printing_information_divided[3][2:]).strip()
        if "title" in istc_record_short:
            bi.title = istc_record_short["title"]
    return bi
    #return(bibliographic_id_list, person_list, place_list, \
    # title, "", "", printing_date, printing_information)


@classes.func_logger
def parse_istc(url_bibliography):
    """This parses the istc records that can be downloaded in JSON. 
    Since the Imprint is normally one line only, some string processing is necessary"""
    # A small problem: if there are several imprints, I take the
    # place and printer information from all, but the date only from the last.
    date_pattern = r'(About |about |Before |before |Not before |not before |Shortly before \
        |shortly before |Between |between |After |after |Not after \
        |not after |Shortly after |shortly after )?(\d{1,2} )?\
        ([A-Za-z\.]{3,5} )?(\d{4})?(/\d{2,4}|-\d{2,4})?( and |and )?\
            (\d{1,2} )?([\w\.]{3,5} )?(\d{4})?'
    month_names = {"Jan. " : "January ", "Feb. " : "February ", "Mar. " : "March ", \
                   "Apr. ": "April", "May " : "May ", "June " : "June ", "July " : "July ", \
                    "Aug. " : "August ", "Sep. " : "September ", "Sept. " : "September ", \
                    "Oct. " : "October ", "Nov. " : "November ", "Dec. " : "December "}
    month_numbers = {"Jan. " : 1, "Feb. " : 2, "Mar. " : 3, "Apr. ": 4, "May " : 5, "June " : 6, \
                     "July " : 7, "Aug. " : 8, \
                    "Sep. " : 9, "Sept. " : 9, "Oct. " : 10, "Nov. " : 11, "Dec. " : 12}
    date_prefix = ""
    date_day = ""
    date_month = ""
    date_year = ""
    date_year_to = ""
    date_between_indicator = ""
    date_between_day = ""
    date_between_month = ""
    date_between_year = ""
    string_prefix = ""
    string_day = ""
    string_month = ""
    string_year = ""
    string_day_between = ""
    string_month_between = ""
    string_year_between = ""
    start_month = 0
    start_day = 0
    start_year = 0
    end_month = 0
    end_day = 0
    end_year = 0


    bi = classes.BibliographicInformation()
    print("URL for search in ISTC: " + url_bibliography)
    istc_record_raw = requests.get(url_bibliography, timeout = 10)
    istc_record_full = (istc_record_raw).json()
    print(istc_record_full)

    if (istc_record_full["hits"])["value"] == 0:
        print("No hits")
        return

    istc_record_short = istc_record_full["rows"][0]
    bid = classes.BibliographicId()
    bid.id = istc_record_short["id"]
    bid.name = "ISTC"
    bid.uri = r"https://data.cerl.org/istc/"+bid.id
    bi.bibliographic_id.append(bid)
    for step1 in istc_record_short['references']:
        #print("step1: " + step1)
        if step1["reference_name"] == "GW":
            bid = classes.BibliographicId()
            if isinstance(step1["reference_location_in_source"], int):
                # Sometimes, this is a mere number - a problem not occurring with ISTC,
                # VD16 and VD17, but perhaps with VD18
                bid.id = str(step1["reference_location_in_source"])
            else:
                bid.id = step1["reference_location_in_source"]
                bid.name = "GW"
    #            bid.uri = This will need more work!
                bi.bibliographic_id.append(bid)


    if "author" in istc_record_short:
        pe = classes.Person()
        pe.name = istc_record_short["author"]
        pe.role = "aut"
        bi.persons.append(pe)

    if "imprint" in istc_record_short:
        for step1 in istc_record_short["imprint"]:
            # this is iterated in case there are several imprints, I reckon
            printer_name_long = ""
            publisher_name_long = ""
            print("step1 in imprint: ")
            print(step1)
            if "imprint_name" in step1:
                imprint_name_long = step1["imprint_name"].strip("[]")
            if "imprint_place" in step1:
                pl = classes.Place()
                pl.name = step1["imprint_place"].strip("[]")
                pl.role = "mfp"
                bi.places.append(pl)
            if "imprint_date" in step1:
                #bi.printing_date = step1["imprint_date"].strip("[]")
                printing_date_raw = step1["imprint_date"].strip("[]")
                print("printing_date_raw: " + printing_date_raw)
                if "[" in printing_date_raw or "]" in printing_date_raw:
                    printing_date_raw = printing_date_raw.replace("[", "")
                    printing_date_raw = printing_date_raw.replace("]", "")
                print("printing_date_raw"+printing_date_raw)
                print( re.match(date_pattern, printing_date_raw))
                printing_date_divided = printing_date_raw
                if  re.match(date_pattern, printing_date_raw):
                    printing_date_divided = re.match(date_pattern, printing_date_raw).groups()
                    date_prefix = ""
                    if printing_date_divided[0]:
                        date_prefix = printing_date_divided[0]
                    if printing_date_divided[1]:
                        date_day = printing_date_divided[1]
                    if printing_date_divided[2]:
                        date_month = printing_date_divided[2]
                    if printing_date_divided[3]:
                        date_year = printing_date_divided[3]
                    if printing_date_divided[4]:
                        date_year_to = printing_date_divided[4]
                    if printing_date_divided[5]:
                        date_between_indicator = printing_date_divided[5]
                    # I wonder if I even need it - probably not.
                    if printing_date_divided[6]:
                        date_between_day = printing_date_divided[6]
                    if printing_date_divided[7]:
                        date_between_month = printing_date_divided[7]
                    if printing_date_divided[8]:
                        date_between_year = printing_date_divided[8]

                print("Raw date: ")
                print(printing_date_raw)
                print("Prefix: ")
                if date_prefix != "":
                    print(date_prefix) #+ "x"
                print("Day: ")
                if date_day:
                    print(date_day) #+ "x"
                print("Month: ")
                if date_month:
                    print(date_month) #+ "x"
                print("Year: ")
                if date_year:
                    print(date_year) #+ "x"
                print("Year - to: ")
                if date_year_to:
                    print(date_year_to) #+ "x"
                if date_between_day:
                    print("date_between_day: ")
                    print(date_between_day)
                if date_between_month:
                    print("date_between_month: ")
                    print(date_between_month)
                if date_between_year:
                    print("date_between_year: ")
                    print(date_between_year) #+ "x"
                if date_prefix == "" and date_year_to == "" and date_between_year == "":
                    #If there is only one date
                    print("Only one year")
                    if date_year != "":
                    #This is not the case if there is a date such as "Between Jan. and Oct. 1488"
                        string_year = date_year + " "
                        start_year = int(date_year)
                        end_year = int(date_year)
                elif date_prefix != "" and date_year_to == "" and date_between_year == "":
                    #If there is only one date, that is not exact
#                    print("only one year, but prefixes")
                    match date_prefix:
                        case "About "|"about ":
                            string_prefix = "about "
                            string_year = date_year + " "
                            start_year = int(date_year) - 1
                            end_year = int(date_year) + 1
                        case "Before " | "before ":
                            string_prefix = "before "
                            string_year = date_year + " "
                            start_year = int(date_year) - 2
                            end_year = int(date_year)
                        case "Shortly before " | "shortly before ":
                            string_prefix = "shortly before "
                            # I am not sure if I will suppress this eventually??
                            string_year = date_year + " "
                            start_year = int(date_year) - 1
                            end_year = int(date_year)
                        case "Not before " | "not before ":
                            string_prefix = "not before "
                            string_year = date_year + " "
                            start_year = int(date_year)
                            end_year = int(date_year) + 2
                        case "After " | "after ":
                            string_prefix = "after "
                            string_year = date_year + " "
                            start_year = int(date_year)
                            end_year = int(date_year) + 2
                        case "Shortly after " | "shortly after ":
                            string_prefix = "shortly after "
                            string_year = date_year + " "
                            start_year = int(date_year)
                            end_year = int(date_year) + 1
                        case "Not after " | "not after ":
                            string_prefix = "not after "
                            string_year = date_year + " "
                            start_year = int(date_year) - 2
                            end_year = int(date_year)
                elif date_prefix in ("Between ", "between ") \
                    and date_between_year != "":
#                    print("timespan with between")
                    string_prefix = "between "
                    string_year_between = date_between_year

                    if date_year != "":
                        #if the start and and the end of the time-span are not in the same year
                        print("Start of timespan has a year")
                        string_year = date_year
                        start_year = int(date_year)
                        end_year = int(date_between_year)
                    else:
#                        print("start of timespan has no year")
                        string_year = ""
                        start_year = int(date_between_year)
                        end_year = int(date_between_year)

                elif date_year_to:
                    if date_year_to[0] == "-": # Question: is this really different from 'between'?
                        #(I would guess that '-' could mean that
                        # the production took from a to b, and
                        # between that it happened after a and before b?????)
                        start_year = int(date_year)
                        if len(date_year_to[1:]) == 4:
                            end_year = int(date_year_to[1:])
                        else:
                            end_year = int("14" + date_year_to[1:])
                        string_year = date_year + "-" + str(end_year)
                        if date_prefix == "About " or date_prefix == "about ":
                            string_prefix = "about "
                            #in this case I don't change the dates, just add the 'about'
                        else:
                            string_prefix = ""


                    if date_year_to[0] == "/":
                        #This should mean exact dates from countries
                        # where the year started in March/April,
                        #so that a date like January 1490 is Jan 1491 in our calendar
                        start_year = int(date_year)+1
                        end_year = int(date_year)+1
                        string_year = date_year + " (in modern calendar " + \
                            str(int(date_year)+1) + ")"

                if date_between_month !="":
                    string_month_between = month_names[date_between_month]
                    number_month_between = month_numbers[date_between_month]
                    end_month = int(number_month_between)
                elif date_between_year != "":
                    # Thus, there is no end month but an end year in this case,
                    # the end month has to be December.
                    end_month = 12

                if date_month != "":
                    string_month = month_names[date_month]
                    number_month = month_numbers[date_month]
                    start_month = int(number_month)
                    if end_month == 0:
                        #thus, if there is no indication of an end month, as in a timespan
                        end_month = int(number_month)
                else:
                    string_month = ""
                    start_month = 1
                    if end_month == 0: # If it has not been defined elsewhere
                        end_month = 12

                if date_between_day != "":
                    string_day_between = date_between_day
                    end_day = int(string_day_between)
                elif date_between_year != "":
                    # Thus, there is no end day but an end year in this case,
                    # the end month has to be December.
                    if end_month in [1, 3, 5, 7, 8, 10, 12]:
                        end_day = 31
                    if end_month in [4, 6, 9, 11]:
                        end_day = 30
                    if end_month == 2 and end_year%4 == 0:
                        # In the Julian calendar, 1500 is a leap year
                        end_day = 29
                    if end_month == 2 and end_year%4 != 0:
                        end_day = 28


                if date_day !="":
                    string_day = date_day
                    start_day = int(date_day)
                    if end_day == 0:
                        end_day = int(date_day)
                else:
                    string_day = ""
                    start_day = 1
                    if end_day == 0:
                        if end_month in [1, 3, 5, 7, 8, 10, 12]:
                            end_day = 31
                        if end_month in [4, 6, 9, 11]:
                            end_day = 30
                        if end_month == 2 and end_year%4 == 0:
                            # In the Julian calendar, 1500 is a leap year
                            end_day = 29
                        if end_month == 2 and end_year%4 != 0:
                            end_day = 28
#            print("Date: ")
#            if string_prefix :
#                print(string_prefix)
#            if string_day:
#                print(string_day)
#            if string_month:
#                print(string_month)
#            if string_year:
#                print(string_year)
            print("start_day: ")
            print(start_day)
            print("start_month: ")
            print(start_month)
            print("start_year: ")
            print(start_year)
            bi.date_string = string_prefix + string_day + string_month + string_year + \
                date_between_indicator + string_day_between + \
                string_month_between + string_year_between
#            bi.date_start = datetime(start_year, start_month, start_day, 0, 0, 0, 0)
#            bi.date_end = datetime(end_year, end_month, end_day, 23, 59, 59, 0)
#            bi.date_start = (start_year, start_month, start_day)
#            bi.date_end = (end_year, end_month, end_day)
            bi.date_start = (1500, 1, 1)
            bi.date_end = (1550, 12, 31)
            print("date ended")

            # Until I have changed it everyhwhere and also in the FE,
            # I still use the old bi.printing_date function.

#            bi.printing_date = bi.date_string + " (" + bi.date_start.isoformat()[0:10] +
#              " - " + bi.date_end.isoformat()[0:10] + ")"



            if imprint_name_long:
                print("imprint_name_long before replacement: " + imprint_name_long)
                imprint_name_long = imprint_name_long.replace("and for", "and")
                # sometimes, the "for" is repeated for a second publisher, what is confusing
                print("imprint_name_long after replacement: " + imprint_name_long)
                if " for " in imprint_name_long:
                    # in this case there are both a printer and a publisher
                    imprint_name_long_divided = imprint_name_long.split(" for ")
                    printer_name_long = imprint_name_long_divided[0]
                    publisher_name_long = imprint_name_long_divided[1]
                    printer_name_long = printer_name_long.strip(",")
                    pl_duplicate = classes.Place()
                    pl_duplicate.name = bi.places[0].name
                    pl_duplicate.role = "pup"
                    bi.places.append(pl_duplicate)
                    # I append the place again, this time as place of publication
                    # I could instead replace the string for the role with a list,
                    # but this is a lot more work, so I have to think
                    # if this is appropriate (I fear it is)
                else: printer_name_long = imprint_name_long


                if printer_name_long:
                    print("printer_name_long: " + printer_name_long)
                    printer_name_long = printer_name_long.replace("[", "")
                    printer_name_long = printer_name_long.replace("]", "")

                    if " and " in printer_name_long: #in this case, there are two printers
                        printer_name_long_divided = printer_name_long.split(" and ")
                        printer_counter = 0
                        while printer_counter < len(printer_name_long_divided):
                            pe = classes.Person()
                            printer_name = printer_name_long_divided[printer_counter]
                            printer_name = printer_name.strip(" [],")
                            if " " in printer_name:
                                #if there is a blank inside the name -
                                # hence it is more than just a Christian name
                                pe.name = printer_name
                            else: # If there is only a Christian name

                                if printer_name_long_divided[printer_counter+1]:
                                    next_printer = printer_name_long_divided\
                                        [printer_counter+1].strip()
                                    # if there is a next printer in the list
                                    # whose name has at least two words
                                    if " " in next_printer:
                                        next_printer_divided = next_printer.split(" ")
                                        next_printer_surname = next_printer_divided[-1]
                                        pe.name = printer_name + " " + next_printer_surname
                                else: # if there is no next printer,
                                    #or the next printer does not have a surname, either
                                    pe.name = printer_name
                            pe.role = "prt"
                            bi.persons.append(pe)
                            printer_counter = printer_counter + 1
                    else: #If there is only one printer
                        pe = classes.Person()
                        pe.name = printer_name_long
                        pe.role = "prt"
                        bi.persons.append(pe)

                if publisher_name_long:
                    print("publisher_name_long: " + publisher_name_long)
                    if " and " in publisher_name_long: #in this case, there are two publishers
                        publisher_name_long_divided = publisher_name_long.split(" and ")
                        print("Two publishers")
                        publisher_counter = 0
                        while publisher_counter < len(publisher_name_long_divided):
                            pe = classes.Person()
                            publisher_name = publisher_name_long_divided[publisher_counter]
                            publisher_name = publisher_name.strip(" []")
                            if " " in publisher_name:
                                #if there is a blank inside the name -
                                # hence it is more than just a Christian name
                                pe.name = publisher_name
                            elif "himself" in publisher_name:
                                pe.name = printer_name_long
                                # in this case there can only be one printer
                            else: # If there is only a Christian name
                                if publisher_name_long_divided[publisher_counter+1]:
                                    next_publisher = publisher_name_long_divided\
                                        [publisher_counter+1].strip()
                                    # if there is a next publisher in the list
                                    # whose name has at least two words
                                    if " " in next_publisher:
                                        next_publisher_divided = next_publisher.split(" ")
                                        next_publisher_surname = next_publisher_divided[-1]
                                        pe.name = publisher_name + " " + next_publisher_surname
                                    else: # if the next printer doesn't have a surname, either
                                        pe.name = publisher_name
                                else: # if there is no next printer
                                    pe.name = publisher_name
                            print("Publisher name: "+ pe.name)
                            pe.role = "pbl"
                            bi.persons.append(pe)
                            publisher_counter = publisher_counter + 1
                    else: #If there is only one publisher
                        pe = classes.Person()
                        pe.name = publisher_name_long
                        pe.role = "pbl"
                        bi.persons.append(pe)
        if "title" in istc_record_short:
            bi.title = istc_record_short["title"]
    return bi
