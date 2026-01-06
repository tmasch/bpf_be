#pylint: disable=W0612
"""
\todo
"""
import re
import json
import requests
from bpf import classes
from bpf import get_external_data




@classes.async_func_logger
async def get_istc_record_for_testing(istc_number):
    """
    This module is used for returning whole ISTC records in order to test parsing function. 
    """
    url = r'https://data.cerl.org/istc/_search?_format=json&pretty=false&query=_id%3A' + \
        istc_number + r'&size=10&sort=default&from=0&file=false&orig=true&facet=Format'\
            + r'facet=Holding%20country&facet=Publication%20country&'\
                + r'nofacets=true&mode=default&aggregations=true&style=full'
    response = requests.get(url, timeout = 10)
    content = response.content
    result = json.loads(content)
    istc_record_short = result["rows"]
#    print("record that is coming back to get_istc_record_for_testing")
#    print(istc_record_short)
    return istc_record_short



@classes.async_func_logger
async def parse_istc(url) -> classes.Graph:
    """
    This parses the istc records that can be downloaded in JSON. 
    Since the Imprint is normally one line only, some string processing is necessary
    """
    # A small problem: if there are several imprints, I take the
    # place and printer information from all, but the date only from the last.

    results=classes.Graph()

    istc_record_full = await get_external_data.get_web_data_as_json(url)
    istc_record_short = istc_record_full["rows"][0]
    if (istc_record_full["hits"])["value"] == 0:
        print("No hits")
        return

    bi = classes.Node()
    results.nodes.append(bi)
    results.nodes[0].type="BibliographicInformation"

####### FINDING BIBILIOGRAPHIC ID
    bib_ids = istc_get_bibliographic_id(istc_record_short)
    for bib_id in bib_ids:
        external_id = classes.ExternalReference()
        external_id.external_id = bib_id[0]
        external_id.name = bib_id[1]
        external_id.uri = bib_id[2]
        results.nodes[0].external_id.append(external_id)

####### FINDING AUTHOR
    if "author" in istc_record_short:
        author=classes.Node()
        author.type="person"
        author.set_attribute("role","author")
        author.set_attribute("chosen_candidate_id","-1")
        author.name_preferred = istc_record_short["author"]
        results.nodes.append(author)

###### FINDING TITLE
    if "title" in istc_record_short:
        title = istc_record_short["title"].strip()
        results.nodes[0].set_attribute("title", title)

###### FINDING IMPRINT
    if "imprint" in istc_record_short:
        for imprint in istc_record_short["imprint"]:
            place_list, date_string, date_start, date_end, printer_list, publisher_list = \
                parse_istc_imprint(imprint)
            for place in place_list:
                pl = classes.Node()
                pl.type = place[0]
                pl.name_preferred = place[1]
                pl.set_attribute("role", place[2])
                results.nodes.append(pl)
            for printer in printer_list:
                pe = classes.Node()
                pe.type = printer[0]
                pe.name_preferred = printer[1]
                pe.set_attribute("role", printer[2])
                results.nodes.append(pe)
            for publisher in publisher_list:
                pe = classes.Node()
                pe.type = publisher[0]
                pe.name_preferred = publisher[1]
                pe.set_attribute("role", publisher[2])
                results.nodes.append(pe)
            date = classes.Date()
            date.date_string = date_string
            date.date_start = date_start
            date.date_end = date_end
            results.nodes[0].dates.append(date)
    print("results overall")
    print(results)
    return results

@classes.func_logger
def parse_istc_imprint(imprint):
    """
    Parse the imprints (Places, Printers, Publishers, Dates)
    """

    #for imprint in record["imprint"]:
        # this is iterated in case there are several imprints, I reckon
    place_list = []
    printer_list = []
    publisher_list = []
    date = classes.Date()
    printer_name_long = ""
    publisher_name_long = ""
    date_string = ""
    date_start = None
    date_end = None
#            print("step1 in imprint: ")
#            print(step1)

    if "imprint_place" in imprint:
        node_type = "place"
        name_preferred = imprint["imprint_place"].strip("[]")
        #place.set_attribute("chosen_candidate_id","-1")
        role = "place of printing"
        place = (node_type, name_preferred, role)
        place_list.append(place)


    if "imprint_date" in imprint:
        printing_date_raw = imprint["imprint_date"].strip("[]")
        date_string, date_start, date_end = istc_analyse_date(printing_date_raw)


    if "imprint_name" in imprint:
        imprint_name_long = imprint["imprint_name"]


    if imprint_name_long:
        imprint_name_long = imprint_name_long.replace("[", "")
        imprint_name_long = imprint_name_long.replace("]", "")
        imprint_name_long = imprint_name_long.replace("and for", "and")
        if " for " in imprint_name_long:
            # in this case there are both a printer and a publisher
            imprint_name_long_divided = imprint_name_long.split(" for ")
            printer_name_long = imprint_name_long_divided[0]
            publisher_name_long = imprint_name_long_divided[1]
            printer_name_long = printer_name_long.strip(",")
            #pl_duplicate = classes.Node()
            duplicate_node_type = "place"
            duplicate_name_preferred = name_preferred
            #pl_duplicate.set_attribute("chosen_candidate_id","-1")
            duplicate_role = "place of publication"
            pl_duplicate = (duplicate_node_type, duplicate_name_preferred, duplicate_role)
            place_list.append(pl_duplicate)
            # I append the place again, this time as place of publication
            # I could instead replace the string for the role with a list,
            # but this is a lot more work, so I have to think
            # if this is appropriate (I fear it is)
        else:
            printer_name_long = imprint_name_long

        if printer_name_long:
            printer_list = istc_get_printer_name(printer_name_long)
            #results.nodes.extend(printer_list)
        if publisher_name_long:
            publisher_list = istc_get_publisher_name(publisher_name_long, printer_name_long)
            #results.nodes.extend(publisher_list)

    #print("final results in parse_imprint")
    #print(results)
    return place_list, date_string, date_start, date_end, printer_list, publisher_list

@classes.func_logger
def istc_get_printer_name(printer_name_long):
    """
    Parses printer_name and gets from there one or two names ofprinters
    """
#   print("printer_name_long: " + printer_name_long)
    printer_list = []
    printer_name_long = printer_name_long.replace("[", "")
    printer_name_long = printer_name_long.replace("]", "")

    if " and " in printer_name_long: #in this case, there are two printers
        printer_name_long_divided = printer_name_long.split(" and ")
        printer_counter = 0
        while printer_counter < len(printer_name_long_divided):
            person_name=""
            printer_name = printer_name_long_divided[printer_counter]
            printer_name = printer_name.strip(" [],")
            if " " in printer_name:
                #if there is a blank inside the name -
                # hence it is more than just a Christian name
                person_name = printer_name
            else: # If there is only a Christian name

                if printer_name_long_divided[printer_counter+1]:
                    next_printer = printer_name_long_divided\
                        [printer_counter+1].strip()
                    # if there is a next printer in the list
                    # whose name has at least two words
                    if " " in next_printer:
                        next_printer_divided = next_printer.split(" ")
                        next_printer_surname = next_printer_divided[-1]
                        # It should be -2 + -1 if -2 is something like "de",
                        # but this may be too much fuss.
                        person_name = printer_name + " " + next_printer_surname
                else: # if there is no next printer,
                    #or the next printer does not have a surname, either
                    person_name = printer_name
            #pe=classes.make_new_role(role="prt",person_name=person_name)
            #pe = classes.Node()
            name_preferred = person_name
            #pe.set_attribute("chosen_candidate_id","-1")
            node_type = "person"
            role = "printer"
            #print("pe in parse_istc")
            #print(pe)
            printer = (node_type, name_preferred, role)
            printer_list.append(printer)
            #bi.persons.append(pe)
            printer_counter = printer_counter + 1
    else: #If there is only one printer
        #pe = classes.Node()
        if printer_name_long != "n.pr.":
            # n.pr. means 'no printer identified
            name_preferred = printer_name_long
            node_type = "person"
            #pe.set_attribute("chosen_candidate_id","-1")
            role = "printer"
            #print("pe in parse_istc")
            printer = (node_type, name_preferred, role)
            printer_list.append(printer)

        #pe=classes.make_new_role(role="prt",person_name=printer_name_long)
        #print(pe)
        #bi.persons.append(pe)
    return printer_list

@classes.func_logger
def istc_get_publisher_name(publisher_name_long, printer_name_long):
    """
    Identifies one or more publishers (if they are indicated separately from the printers)
    """
    publisher_list = []
    pepersonname = ""
    print("publisher_name_long: " + publisher_name_long)
    if " and " in publisher_name_long: #in this case, there are two publishers
        publisher_name_long_divided = publisher_name_long.split(" and ")
        print("Two publishers")
        publisher_counter = 0
        while publisher_counter < len(publisher_name_long_divided):
            publisher_name = publisher_name_long_divided[publisher_counter]
            publisher_name = publisher_name.strip(" []")
            if " " in publisher_name:
                #if there is a blank inside the name -
                # hence it is more than just a Christian name
                pepersonname = publisher_name
            elif "himself" in publisher_name:
                pepersonname = printer_name_long.strip()
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
                        pepersonname = publisher_name + " " + next_publisher_surname
                    else: # if the next printer doesn't have a surname, either
                        pepersonname = publisher_name
                else: # if there is no next printer
                    pepersonname = publisher_name
            print("Publisher name: "+ pepersonname)
            node_type = "person"
            name_preferred = pepersonname
            role = "publisher"
            pe = (node_type, name_preferred, role)
            publisher_list.append(pe)

#                            pe = classes.SelectionCandidate()
#                            pe.person = classes.Person()
#                            pe.person.role = "pbl"
            #publisher=classes.make_new_role(role="pbl",person_name=pepersonname)
            #bi.persons.append(publisher)
            publisher_counter = publisher_counter + 1
    else: #If there is only one publisher
#                        pe = classes.SelectionCandidate()
#  #                       pe.person = classes.Person()
#                         pe.person.name = publisher_name_long
#                         pe.person.role = "pbl"
#                        publisher=classes.make_new_role(role="pbl",person_name=publisher_name_long)
#                        result.nodes.append(publisher)
        node_type = "person)"
        name_preferred = publisher_name_long
        role = "publisher"
        pe = (node_type, name_preferred, role)
        print(pe)
        publisher_list.append(pe)
    return publisher_list


@classes.func_logger
def istc_get_bibliographic_id(istc_record_short):
    """
    Parses ID numbers from ISTC and GND
    """
    bib_ids=[]

    #bib_id = classes.ExternalReference()
    external_id = istc_record_short["id"]
    id_name = "ISTC"
    uri = r"https://data.cerl.org/istc/" + external_id
    bib_id = (external_id, id_name, uri)
    bib_ids.append(bib_id)


    for reference in istc_record_short['references']:
        #print("step1: " + step1)
        if reference["reference_name"] == "GW":
            #bib_id = classes.ExternalReference()
            external_id = str(reference["reference_location_in_source"])
            id_name = "GW"
            gw_type0 = r'\d{1,5}' # the standard type
            gw_type1 = r'M\d{5,7}' # a number from the still unpublished volumes
            gw_type2 = r'\d{7}N' # a later addition
            gw_type3 = x = r'([XVI]{1,4}) Sp\.(\d{1,3})([a-z])'
            # a reference to a book that is now not regarded as an incunable
            gw_type4 = x = r'([XVI]{1,4}) Sp\.(\d{1,3})([a-z]P)' # no clue what this is
            if re.match(gw_type0, external_id):
                x = 5 - len(external_id)
                y = "0" * x
                uri = "https://www.gesamtkatalogderwiegendrucke.de/docs/GW" \
                    + y + external_id + ".htm"
            elif re.match(gw_type1, external_id):
                uri = "https://www.gesamtkatalogderwiegendrucke.de/docs/" + \
                    external_id + ".htm"
            elif re.match(gw_type2, external_id):
                uri = "https://www.gesamtkatalogderwiegendrucke.de/docs/GW" + \
                    external_id + ".htm"
            elif re.match(gw_type3, external_id) or re.match(gw_type4, external_id):
                x = re.match(gw_type3, external_id)
                uri = "https://www.gesamtkatalogderwiegendrucke.de/docs/GW" + \
                    x[1] + x[2] + (x[3]).upper() + ".htm"
            bib_id = (external_id, id_name, uri)
#                classes.BibliographicInformation.model_validate(bid)
            bib_ids.append(bib_id)
    return bib_ids



@classes.func_logger
def istc_analyse_date(printing_date_raw):
    """
    \todo
    """
    # The last options before the backslash did not work, hence I repeated them.
    date_pattern = r'(About |about |Before |before |Not before |not before |not before \
        |Shortly before |shortly before |Between |between |After |after |Not after |Not after \
        |not after |Shortly after |shortly after )?(\d{1,2} )?([A-Za-z\.]{3,5} )?(\d{4})?(/\d{2,4}|-\d{2,4})?( and |and )?(\d{1,2} )?([\w\.]{3,5} )?(\d{4})?'

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
    end_year = 0
    date_string = ""
    date_start = ()
    date_end = ()
    printing_date_raw = printing_date_raw.replace(".1", ". 1")
    # in case the blank after the abbreviation of the month has been forgotten.
    if  re.match(date_pattern, printing_date_raw):
        print("date matching with pattern")
        printing_date_divided = re.match(date_pattern, printing_date_raw).groups()
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


    string_prefix, string_year, string_year_between, start_year, end_year = \
        analyse_year(date_prefix, date_year, date_year_to, date_between_year)
    string_month, string_month_between, start_month, end_month = \
        analyse_month(date_between_year, date_between_month, date_month)
    string_day, string_day_between, start_day, end_day = analyse_day(date_between_day, \
        date_between_year, date_day, end_month, end_year)


    date_string = string_prefix + string_day + string_month + string_year + \
         date_between_indicator + string_day_between + \
         string_month_between + string_year_between

    date_string = date_string.strip()
    date_start = (start_year, start_month, start_day)
    date_end = (end_year, end_month, end_day)
    date = (date_string, date_start, date_end)
    return date


@classes.func_logger
def analyse_prefix(date_prefix, start_year, end_year):
    """
    This function reads the prefix of the date from ISTC and returns both a standardised prefix and
    adopted settings for start_year and end_year. 
    """
    string_prefix = "" # an insurance in case there is an unusual date_prefix
    match date_prefix:
        case "About "|"about ":
            string_prefix = "about "
            start_year = start_year - 1
            end_year = end_year + 1
        case "Before " | "before ":
            string_prefix = "before "
            start_year = start_year - 2
        case "Shortly before " | "shortly before ":
            string_prefix = "shortly before "
            # I am not sure if I will suppress this eventually??
            start_year = start_year - 1
        case "Not before " | "not before ":
            string_prefix = "not before "
            end_year = end_year + 2
        case "After " | "after ":
            string_prefix = "after "
            end_year = end_year + 2
        case "Shortly after " | "shortly after ":
            string_prefix = "shortly after "
            end_year = end_year + 1
        case "Not after " | "not after ":
            string_prefix = "not after "
            start_year = start_year - 2
        case _:
            string_prefix = "(unknown prefix - please check) "
    return(string_prefix, start_year, end_year)

@classes.func_logger
def analyse_year(date_prefix, date_year, date_year_to, date_between_year):
    """
    This function parses the indication of years
    """
    string_prefix = ""
    string_year = ""
    string_year_between = ""
    start_year = 0
    end_year = 0

    if date_year_to == "" and date_between_year == "":
        #If there is only one date
        print("Only one year: ")
        print(date_year)
        if date_year != "":
        #This is not the case if there is a date such as "Between Jan. and Oct. 1488"
            string_year = date_year
            start_year = int(date_year)
            end_year = int(date_year)
        if date_prefix != "":
        #If there is only one date, that is not exact
#                    print("only one year, but prefixes")
            string_prefix, start_year, end_year = \
                analyse_prefix(date_prefix, start_year, end_year)
        # This standardises the prefix and changes start year and end year accordingly
    elif date_prefix in ("Between ", "between ") \
        and date_between_year != "":
#                    print("timespan with between")
        string_prefix = "between "
        string_year_between = date_between_year

        if date_year != "":
            #if the start and and the end of the time-span are not in the same year
            # print("Start of timespan has a year")
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
    return (string_prefix, string_year, string_year_between, start_year, end_year)


@classes.func_logger
def analyse_month(date_between_year, date_between_month, date_month):
    """
    This function parses indications of months
    """
    month_names = {"Jan. " : "January ", "Feb. " : "February ", "Mar. " : "March ", \
                   "Apr. ": "April ", "May " : "May ", "June " : "June ", "July " : "July ", \
                    "Aug. " : "August ", "Sep. " : "September ", "Sept. " : "September ", \
                    "Oct. " : "October ", "Nov. " : "November ", "Dec. " : "December "}
    month_numbers = {"Jan. " : 1, "Feb. " : 2, "Mar. " : 3, "Apr. ": 4, "May " : 5, "June " : 6, \
                     "July " : 7, "Aug. " : 8, \
                    "Sep. " : 9, "Sept. " : 9, "Oct. " : 10, "Nov. " : 11, "Dec. " : 12}
    string_month_between = ""
    start_month = 0
    end_month = 0

    if date_between_month !="":
        string_month_between = month_names[date_between_month]
        number_month_between = month_numbers[date_between_month]
        end_month = int(number_month_between)
    elif date_between_year != "":
        # Thus, there is no end month but an end year. In this case,
        # the end month has to be December.
        end_month = 12

    if date_month != "":
        print("date_month in record: ")
        print(date_month)
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
    return (string_month, string_month_between, start_month, end_month)

@classes.func_logger
def analyse_day(date_between_day, date_between_year, \
                date_day, end_month, end_year):
    """
    This function parses indications of days. 
    """
    string_day_between = ""
    end_day = 0
    if date_between_day != "":
        string_day_between = date_between_day
        end_day = int(string_day_between)
    elif date_between_year != "":
        # Thus, there is no end day but an end year in this case,
        # the end month has to be December.
        if end_month in [1, 3, 5, 7, 8, 10, 12]:
            end_day = 31
        elif end_month in [4, 6, 9, 11]:
            end_day = 30
        elif end_month == 2 and end_year%4 == 0:
            # In the Julian calendar, 1500 is a leap year
            end_day = 29
        elif end_month == 2 and end_year%4 != 0:
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
            elif end_month in [4, 6, 9, 11]:
                end_day = 30
            elif end_month == 2 and end_year%4 == 0:
                # In the Julian calendar, 1500 is a leap year
                end_day = 29
            elif end_month == 2 and end_year%4 != 0:
                end_day = 28
    return (string_day, string_day_between, start_day, end_day)
