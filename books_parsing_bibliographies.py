# pylint: disable=C0302,C0303,I1101
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

# import requests
import classes
import parsing_helpers



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
        record_text = etree.tostring(tree, encoding=str)
    except TypeError:
        return
    record_removal = (
        r'(<var>|<strong>|<strong class="c2">|</strong>|</li>|<ul>|</p></div>)'
    )
    record_cleaned = re.sub(record_removal, "", record_text)
    record_pattern = (
        r"(.*)(Erfassungsdatum)(.*)"  # cut off everything after 'Permalink'
    )
    record_parts = re.match(record_pattern, record_cleaned, re.DOTALL)
    record_parts_standardised = record_parts[1].replace("Normnummer", "<br/>Normnummer")
    # The first line, 'Normummer', does not start with 'Break',
    # I insert this so that the records can be chopped up properly
    record_divided = re.split("<br/>", record_parts_standardised)
    # divide record into individual lines
    record_line_pattern = r"(.*?)(\: )(.*)"
    for record_line in record_divided:
        record_line_divided = re.match(record_line_pattern, record_line)
        # divide record into key-value-pairs
        if record_line_divided:
            record_structured[record_line_divided[1]] = record_line_divided[3]
    print(record_structured)

    # parsing the individual values
    bibliographic_id = record_structured["Normnummer"]
    bibliographic_id_pattern = r"(....)(\s)([A-Z]{1,2}\s[0-9]{1,5})(.*)"
    bid = classes.BibliographicId()
    bid.name = re.match(bibliographic_id_pattern, bibliographic_id)[1]
    bid.id = re.match(bibliographic_id_pattern, bibliographic_id)[3]
    #    bibliographic_id_single = (bibliographic_id_name, bibliographic_id_number)
    bi.bibliographic_id.append(bid)
    #    bibliographic_id_list.append(bibliographic_id_single)
    #   in the VD16, there is only one ID,
    #   this list is only introduced for the sake of consistence with incunables

    person_list_pattern = r"<a href.*?</a>"
    person_single_pattern = (
        r"(<a h.*?>)(.*?)(</a>|&.*?</a>)(.*)?(DE-588)?(.*)?(: Datensatz)?(.*)?"
    )
    #    person_single_pattern = r'(<a h.*?>)(.*?)(</a>)(.*?)(DE-588)?(.*)?(: Datensatz)?(.*)?'
    ###currently, the system only reads the last author or contributor,
    # and it does not read his bibliographic ID number.
    if "Verfasser" in record_structured:
        pe = classes.Person()
        author = record_structured["Verfasser"]
        print("Author found")
        print(author)
        # author_list_divided = re.findall(person_list_pattern, author_list)
        # for step1 in author_list_divided:
        author_single_divided = re.match(person_single_pattern, author)
        pe.name = author_single_divided[2]
        pe.id = author_single_divided[6]  # That doesn't work!
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
        impressum_pattern = r"([^:]*)(: )?([^;]*)?(; )?([^:]*)?(: )?(.*)?(, )([^,]*)"
        impressum_divided = re.match(impressum_pattern, impressum)
        pl = classes.Entity()
        pl.name = impressum_divided[1]
        pl.role = "mfp"
        bi.places.append(pl)
        if impressum_divided[5]:
            pl = classes.Entity()
            pl.name = impressum_divided[5]
            pl.role = "pup"
            bi.places.append(pl)
        if not impressum_divided[5] and impressum_divided[7]:
            # if the printer (in section 3) and the publisher (in section 7)
            # are in the same place, this place name
            # is only given in section 1 and not repeated in section 5.
            # However, it needs to entered twice into the database,
            # as place of publishing and as place of printing.
            pl = classes.Entity()
            pl.name = impressum_divided[1]
            pl.role = "pup"
            bi.places.append(pl)
        if impressum_divided[3]:
            impressum_single_person1 = re.split(" und ", impressum_divided[3])
            # If there are several printers or several publishers,
            # they are separated by "und" (at least, if there are two,
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
        bi.title = record_structured["Titel"]
        bi.printing_information = record_structured["Ausgabebezeichnung"]
    # Although some early 16th-century books give a day, the date field in the VD16 only contains
    #  a year, two years separated by "/" (two different years given in the book) "-"
    if printing_date_long != "":
        start_year=1000
        end_year=1001
        if "/" in printing_date_long:
            printing_date_divided = printing_date_long.split("/")
        elif "-" in printing_date_long:
            printing_date_divided = printing_date_long.split("-")
        else:
            printing_date_long = printing_date_long.strip()
            if len(printing_date_long) == 4:  # If there are only four digits
                bi.date_string = printing_date_long
                start_year = int(printing_date_long)
                end_year = int(printing_date_long)

        if printing_date_divided != []:
            if len(printing_date_divided[1]) == 2:
                # If for the second year only the last two digits are given
                printing_date_divided[1] = "15" + printing_date_divided[1]
            if int(printing_date_divided[0]) < int(printing_date_divided[1]):
                # if the first figure is lower (this is not always the case)
                bi.date_string = (
                    printing_date_divided[0] + "-" + printing_date_divided[1]
                )
                start_year = int(printing_date_divided[0])
                end_year = int(printing_date_divided[1])
            else:
                bi.date_string = (
                    printing_date_divided[1] + "-" + printing_date_divided[0]
                )
                start_year = int(printing_date_divided[1])
                end_year = int(printing_date_divided[0])
        start_day = 1
        start_month = 1
        end_day = 31
        end_month = 12
        # bi.date_start = datetime(start_year, start_month, start_day, 0, 0, 0, 0)
        # bi.date_end = datetime(end_year, end_month, end_day, 23, 59, 59, 0)
        # bi.printing_date = bi.date_string + " (" + bi.date_start.isoformat()[0:10] +
        # " - " + bi.date_end.isoformat()[0:10] + ")"
        bi.date_start = (start_year, start_month, start_day)
        bi.date_end = (end_year, end_month, end_day)
    return bi


# def istc_parsing_alt(url_bibliography):
#     """Is this even in use????"""
#     # I have two problems concerning the API I used here to download the data
#     # - if they are solved, some parts of the programme
#     # should be changed
#     # (1): I downloaded the "imprint" section as a unit and had to
#     # divide it into place, printer(s), and date, which works ok.
#     # This should not be necessary since it should be possible
#     # to download them in separate fields, however, this did not work.
#     # (2): in a small number of cases, the system gives
#     # two different "imprints" (because there is some uncertainty).
#     # Oddly, the API only downloads the first of them and ignores all the others.
#     # If several can be downloaded, one needs a loop to parse all of them one by one.
#     bi = classes.BibliographicInformation()
#     istc_record_raw = requests.get(url_bibliography, timeout = 10)
#     istc_record_full = (istc_record_raw).json()

#     if (istc_record_full["hits"])["value"] == 0:
#         print("No hits")
#         return

#     istc_record_short = (istc_record_full["rows"])[0]
#     bid = classes.BibliographicId()
#     bid.id = istc_record_short["id"]
#     bid.name = "ISTC"
#     bid.uri = r"https://data.cerl.org/istc/"+bid.id
#     bi.bibliographic_id.append(bid)
#     #bibliographic_id_single_1 = ("ISTC", bibliographic_id_number_1)
#     #bibliographic_id_list.append(bibliographic_id_single_1)
#     for step1 in istc_record_short['references']:
#         if step1[0:3] == "GW ":
#             bid = classes.BibliographicId()
#             bid.id = step1[3:]
#             bid.name = "GW"
# #            bid.uri = This will need more work!
#             bi.bibliographic_id.append(bid)
#             #bibliographic_id_single_2 = ("GW", bibliographic_id_number_2)
#             #bibliographic_id_list.append(bibliographic_id_single_2)


#     if "author" in istc_record_short:
#         pe = classes.Person()
#         pe.name = istc_record_short["author"]
#         pe.role = "aut"
#         #author_single = (author, "", "aut")
#         bi.persons.append(pe)
#         #person_list.append(author_single)

#     if "imprint" in istc_record_short:
#         printing_information = istc_record_short["imprint"]
#         bi.printing_information = printing_information
#         printing_information = printing_information.replace(r"[", "")
#         printing_information = printing_information.replace(r"]", "")
#         printing_information_pattern =  r"([^:]*)(: .*)?(, [^,]*)$"
#         printing_information_divided = re.match(printing_information_pattern,
#  printing_information)
#         pl = classes.Place()
#         pl.name = (printing_information_divided[1]).strip()
#         pl.role = "mfp"
#         bi.places.append(pl)
#         #place_single = (place, "", "mfp")
#         #place_list.append(place_single)
#         printer_raw = (printing_information_divided[2][2:]).strip()
#         if ", for " in printer_raw:
#             #the 'for' means that there are a printer and a publisher.
#             # In this case, the publisher's town is not indicated
#             printer_divided = re.split(", for ", printer_raw)
#             printer_only = printer_divided[0]
#             publisher_only = printer_divided[1]
#             pl = classes.Place()
#             pl.name = (printing_information_divided[1]).strip()
#             pl.role = "pup"
#             bi.places.append(pl)
#             #place_single = (place, "", "pup")
#             #place_list.append(place_single)
#             if " and " in publisher_only:
#                 publisher_divided = re.split(" and ", publisher_only)
#                 pe = classes.Person()
#                 pe.name = publisher_divided[0]
#                 pe.role = "pbl"
#                 bi.persons.append(pe)
#                 #person_list.append(person_single)
#                 pe = classes.Person()
#                 pe.name = publisher_divided[1]
#                 pe.role = "pbl"
#                 bi.persons.append(pe)
#                 #person_list.append(person_single)
#             else:
#                 pe = classes.Person()
#                 pe.name = publisher_only
#                 pe.role = "pbl"
#                 bi.persons.append(pe)
#         else:
#             printer_only = printer_raw
#         if " and " in printer_only:
#             # in case of two printers with the same surname,
#             # the entry reads "John and Paul Smith", leading to the two printers
#             # "JOhn" ad "Paul Smith". This happens very rarely and should be corrected manually.
#             printer_divided = re.split(" and ", printer_only)
#             pe = classes.Person()
#             pe.name = printer_divided[0]
#             pe.role = "prt"
#             bi.persons.append(pe)
#             #person_list.append(person_single)
#             pe = classes.Person()
#             pe.name = printer_divided[1]
#             pe.role = "prt"
#             bi.persons.append(pe)
#         else:
#             pe = classes.Person()
#             pe.name = printer_only
#             pe.role = "prt"
#             bi.persons.append(pe)
#             #person_list.append(person_single)
#         bi.printing_date = (printing_information_divided[3][2:]).strip()
#         if "title" in istc_record_short:
#             bi.title = istc_record_short["title"]
#     return bi
#     #return(bibliographic_id_list, person_list, place_list, \
#     # title, "", "", printing_date, printing_information)
