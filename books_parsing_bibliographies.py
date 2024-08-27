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
import parsing_helpers

@classes.func_logger
def parse_vd17(url_bibliography):
    """
This function can be used for parsing both the VD17 and the VD18
    """
    print("PARSE VD17")
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
        print("bibliographic information from VD17:")
        print(bi)
        if printing_date_raw:
            bi.date_string, bi.date_start, bi.date_end = map_printing_date(printing_date_raw)
    return bi

@classes.func_logger
def map_printing_date(printing_date_raw):
    """
\todo 
    """
    year_pattern_isolated = r'\d{4}'
    year_pattern_brackets = r'\[(ca. |ca.|ca |circa |um |vor |nicht vor \
        |nach |nicht nach |erschienen |erschienen ca. |erschienen|\
        |erschienen nach |i.e. )?(\d{4})?([MDCLXVI\.]*)?(\?|\? )?(/\d{2}|/\d{4})?\]'
    year_pattern_arabic_in_text = r'(1\d{3})[\D$]?'
    # should mean 1XXX, then a non-number or end of string
    year_pattern_roman_in_text = r'(M[DCLXVI\. ]*)'

    start_year=1000
    end_year=1000
    date_string="1000"

    print("Rohdatum: ")
    print(printing_date_raw)
    if re.match(year_pattern_isolated, printing_date_raw) and len(printing_date_raw)==4:
        # This means ca. 80% of the cases, when there is just a four-digit year
        print("Year simple number")
        date_string = printing_date_raw
        start_year = int(printing_date_raw)
        end_year = int(printing_date_raw)
    elif re.search(year_pattern_brackets, printing_date_raw):
        # If there is a date given in brackets, it should be the preferred form to use
        printing_date_divided = re.search(year_pattern_brackets, printing_date_raw).groups()
        print("Year in square brackets matched")
        if printing_date_divided[1]:
            print("year string: " + printing_date_divided[1])
            year_string = printing_date_divided[1]
            date_string = year_string
            start_year = int(year_string)
            end_year = int(year_string)
        elif printing_date_divided[2]:
            year_string = parsing_helpers.convert_roman_numerals(printing_date_divided[2])
            date_string = year_string
            start_year = int(year_string)
            end_year = int(year_string)
        if printing_date_divided[4]: #if there is a second year given as end of a period
            year_end_string = printing_date_divided[4][1:]
            print("Year_end_string found: ")
            print(year_end_string)
            if len(year_end_string) == 2: #if there are only two digits
                year_end_string = "17" + year_end_string
            year_string = year_string + " / " + year_end_string
            date_string = year_string
            end_year = int(year_end_string)
        if printing_date_divided[0]:
            print("Year in square brackets with Prefix")
            match printing_date_divided[0]:
                case "erschienen ":
                    date_string = year_string
                    start_year = int(year_string)
                    end_year = int(year_string)
                case "ca. "|"ca."|"ca "|"circa "|"um "|"erschienen ca. ":
                    date_string =  "about " + year_string
                    start_year = int(year_string)- 2
                    end_year = int(year_string) + 2
                case "vor ": # I include the year for 'before' in the string
                    #since I am not sure if it always means 'before Jan 1st'
                    date_string =  "before " + year_string
                    start_year = int(year_string) - 5
                    end_year = int(year_string)
                case "nach "|"erschienen nach ": # cf. comment on "vor "
                    date_string =  "after " + year_string
                    start_year = int(year_string)
                    end_year = int(year_string) + 5
                case "nicht vor ":
                    date_string =  "not before " + year_string
                    start_year = int(year_string)
                    end_year = int(year_string) + 5
                case "nicht nach ":
                    date_string =  "not after " + year_string
                    start_year = int(year_string) - 5
                    end_year = int(year_string)
                case "i.e. ":
                    date_string = year_string + " (corrected date)"
                    start_year = int(year_string)
                    end_year = int(year_string)
        if printing_date_divided[3] == "?" or printing_date_divided[3] == "? ":
            date_string = date_string + "?"
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
            date_string = year_string
            start_year = int(year_string)
            end_year = int(year_string)
        if re.search(year_pattern_roman_in_text, printing_date_raw):
            # This means that there is a string in Roman numerals starting with "M"
            year_string = parsing_helpers.convert_roman_numerals(re.search(year_pattern_roman_in_text, \
                printing_date_raw).groups()[0])
            date_string = year_string
            print("Year in Roman numerals:")
            print(date_string)
            start_year = int(year_string)
            end_year = int(year_string)
        elif "18. Jh." in printing_date_raw or "18.Jh." in printing_date_raw:
            date_string = "18th century"
            start_year = 1701
            end_year = 1800

        else:
            print("year not digested")

    date_start = (start_year, 1, 1)
    date_end = (end_year, 12, 31)
    return date_string, date_start, date_end



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


