#pylint: disable=W0612
"""
\todo
"""
import re
import classes
import get_external_data




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
    bi.type="BibliographicInformation"

####### FINDING BIBILIOGRAPHIC ID
    bib_ids = parse_istc_bibliographic_id(istc_record_short)
    bi.external_id.extend(bib_ids)

####### FINDING AUTHOR
    if "author" in istc_record_short:
        author=classes.Node()
        author.type="person"
        author.set_attribute("role","aut")
        author.name=istc_record_short["author"]
        results.nodes.append(author)

    return results


def parse_istc_imprint(record):

    result=classes.Graph()

    if "imprint" in record:
        for imprint in record["imprint"]:
            # this is iterated in case there are several imprints, I reckon
            printer_name_long = ""
            publisher_name_long = ""
#            print("step1 in imprint: ")
#            print(step1)

            if "imprint_place" in imprint:
                place = classes.Node()
                place.name = imprint["imprint_place"].strip("[]")
                place.set_attribute("chosen_candidate_id",-1)
                place.set_attribute("role","mfp")
                result.nodes.append(place)

            if "imprint_date" in imprint:
#                print(step1["imprint_date"])
                #bi.printing_date = step1["imprint_date"].strip("[]")
                printing_date_raw = imprint["imprint_date"].strip("[]")
                bi.date_string, bi.date_start, bi.date_end = istc_date_working(printing_date_raw)

#
#            bi.date_start = datetime(start_year, start_month, start_day, 0, 0, 0, 0)
#            bi.date_end = datetime(end_year, end_month, end_day, 23, 59, 59, 0)
#            bi.date_start = (start_year, start_month, start_day)
#            bi.date_end = (end_year, end_month, end_day)
#            bi.date_start = (1500, 1, 1)
#            bi.date_end = (1550, 12, 31)
#            print("date ended")





            # Until I have changed it everyhwhere and also in the FE,
            # I still use the old bi.printing_date function.

#            bi.printing_date = bi.date_string + " (" + bi.date_start.isoformat()[0:10] +
#              " - " + bi.date_end.isoformat()[0:10] + ")"

            if "imprint_name" in imprint:
                imprint_name_long = imprint["imprint_name"].strip("[]")


            if imprint_name_long:
#                print("imprint_name_long before replacement: " + imprint_name_long)
                imprint_name_long = imprint_name_long.replace("and for", "and")
                # sometimes, the "for" is repeated for a second publisher, what is confusing
#                print("imprint_name_long after replacement: " + imprint_name_long)
                if " for " in imprint_name_long:
                    # in this case there are both a printer and a publisher
                    imprint_name_long_divided = imprint_name_long.split(" for ")
                    printer_name_long = imprint_name_long_divided[0]
                    publisher_name_long = imprint_name_long_divided[1]
                    printer_name_long = printer_name_long.strip(",")
                    pl_duplicate = classes.Node()
                    pl_duplicate.name = bi.places[0].name
                    pl_duplicate.role = "pup"
                    bi.places.append(pl_duplicate)
                    # I append the place again, this time as place of publication
                    # I could instead replace the string for the role with a list,
                    # but this is a lot more work, so I have to think
                    # if this is appropriate (I fear it is)
                else:
                    printer_name_long = imprint_name_long


                if printer_name_long:
#                    print("printer_name_long: " + printer_name_long)
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
                                        person_name = printer_name + " " + next_printer_surname
                                else: # if there is no next printer,
                                    #or the next printer does not have a surname, either
                                    person_name = printer_name
                            pe=classes.make_new_role(role="prt",person_name=person_name)
                            print("pe in parse_istc")
                            print(pe)
                            bi.persons.append(pe)
                            printer_counter = printer_counter + 1
                    else: #If there is only one printer
                        pe=classes.make_new_role(role="prt",person_name=printer_name_long)
                        print(pe)
                        bi.persons.append(pe)

                if publisher_name_long:
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
                                pepersonname = printer_name_long
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
                            print("Publisher name: "+ pe.name)
#                            pe = classes.SelectionCandidate()
#                            pe.person = classes.Person()
#                            pe.person.role = "pbl"
                            publisher=classes.make_new_role(role="pbl",person_name=pepersonname)
                            bi.persons.append(publisher)
                            publisher_counter = publisher_counter + 1
                    else: #If there is only one publisher
#                        pe = classes.SelectionCandidate()
#  #                       pe.person = classes.Person()
#                         pe.person.name = publisher_name_long
#                         pe.person.role = "pbl"
                        publisher=classes.make_new_role(role="pbl",person_name=publisher_name_long)
                        bi.persons.append(publisher)
        if "title" in istc_record_short:
            bi.title = istc_record_short["title"]


    return bi



@classes.func_logger
def parse_istc_bibliographic_id(istc_record_short):
    """
    Parses ID numbers from ISTC and GND
    """
    bib_ids=[]

    bib_id = classes.ExternalReference()
    bib_id.external_id = istc_record_short["id"]
    bib_id.name = "ISTC"
    bib_id.uri = r"https://data.cerl.org/istc/"+bib_id.external_id
    bib_ids.append(bib_id)


    for reference in istc_record_short['references']:
        #print("step1: " + step1)
        if reference["reference_name"] == "GW":
            bib_id = classes.ExternalReference()
            bib_id.external_id = str(reference["reference_location_in_source"])
            bib_id.name = "GW"
            gw_type0 = r'\d{1,5}' # the standard type
            gw_type1 = r'M\d{5,7}' # a number from the still unpublished volumes
            gw_type2 = r'\d{7}N' # a later addition
            gw_type3 = x = r'([XVI]{1,4}) Sp\.(\d{1,3})([a-z])'
            # a reference to a book that is now not regarded as an incunable
            gw_type4 = x = r'([XVI]{1,4}) Sp\.(\d{1,3})([a-z]P)' # no clue what this is
            if re.match(gw_type0, bib_id.external_id):
                x = 5 - len(bib_id.external_id)
                y = "0" * x
                bib_id.uri = "https://www.gesamtkatalogderwiegendrucke.de/docs/GW" \
                    + y + bib_id.external_id + ".htm"
            elif re.match(gw_type1, bib_id.external_id):
                bib_id.uri = "https://www.gesamtkatalogderwiegendrucke.de/docs/" + \
                    bib_id.external_id + ".htm"
            elif re.match(gw_type2, bib_id.external_id):
                bib_id.uri = "https://www.gesamtkatalogderwiegendrucke.de/docs/GW" + \
                    bib_id.external_id + ".htm"
            elif re.match(gw_type3, bib_id.external_id) or re.match(gw_type4, bib_id.external_id):
                x = re.match(gw_type3, bib_id.external_id)
                bib_id.uri = "https://www.gesamtkatalogderwiegendrucke.de/docs/GW" + \
                    x[1] + x[2] + (x[3]).upper() + ".htm"

#                classes.BibliographicInformation.model_validate(bid)
            bib_ids.append(bib_id)
    return bib_ids



@classes.func_logger
def istc_date_working(printing_date_raw):
    """
    \todo
    """
#    date_pattern = r'(About |about |Before |before |Not before |not before |Shortly before \
#    |shortly before |Between |between |After |after |Not after \
#    |not after |Shortly after |shortly after )?(\d{1,2} )?\
#    ([A-Za-z\.]{3,5} )?(\d{4})?(/\d{2,4}|-\d{2,4})?( and |and )?\
#    (\d{1,2} )?([\w\.]{3,5} )?(\d{4})?'
    # I have no clue what is going on here - when breaking the last line of this pattern
    # at a less awkward place it was rendered invalid.
    date_pattern = r'(About |about |Before |before |Not before |not before \
        |Shortly before |shortly before |Between |between |After |after |Not after \
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

#    print(step1["imprint_date"])
    #bi.printing_date = step1["imprint_date"].strip("[]")
#                printing_date_raw = step1["imprint_date"].strip("[]")
#    print("printing_date_raw: " + printing_date_raw)
#    print("printing_date_raw: "+"x"+printing_date_raw + "x")
#    print( re.match(date_pattern, printing_date_raw))
    #printing_date_divided = printing_date_raw
    if  re.match(date_pattern, printing_date_raw):
        print("date matching with pattern")
        printing_date_divided = re.match(date_pattern, printing_date_raw).groups()
#        date_prefix = ""
#        date_prefix, date_day, date_month, date_year, date_year_to, date_between_indicator, \
#        date_between_day, date_between_month, date_between_year = printing_date_divided
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

#    print("Raw date: ")
#    print(printing_date_raw)
#    print("Prefix: ")
#    if date_prefix != "":
#        print(date_prefix) #+ "x"
#    print("Day: ")
#    if date_day:
#        print(date_day) #+ "x"
#    print("Month: ")
#    if date_month:
#        print(date_month) #+ "x"
#    print("Year: ")
#    if date_year:
#        print(date_year) #+ "x"
#    print("Year - to: ")
#    if date_year_to:
#        print(date_year_to) #+ "x"
#    if date_between_day:
#        print("date_between_day: ")
#        print(date_between_day)
#    if date_between_month:
#        print("date_between_month: ")
#        print(date_between_month)
#    if date_between_year:
#        print("date_between_year: ")
#        print(date_between_year) #+ "x"
    string_prefix, string_year, string_year_between, start_year, end_year = \
        analyse_year(date_prefix, date_year, date_year_to, date_between_year)
    string_month, start_month, end_month = \
        analyse_month(date_between_year, date_between_month, date_month)
    string_day, start_day, end_day = analyse_day(date_between_day, \
        date_between_year, string_day_between, date_day, end_month, end_year)
#            print("Date: ")
#            if string_prefix :
#                print(string_prefix)
#            if string_day:
#                print(string_day)
#            if string_month:
#                print(string_month)
#            if string_year:
#                print(string_year)
#    print("start_day: ")
#    print(start_day)
#    print("start_month: ")
#    print(start_month)
#    print("start_year: ")
#    print(start_year)

    date_string = string_prefix + string_day + string_month + string_year + \
         date_between_indicator + string_day_between + \
         string_month_between + string_year_between
    date_start = (start_year, start_month, start_day)
    date_end = (end_year, end_month, end_day)

    return (date_string, date_start, date_end)

@classes.func_logger
def analyse_prefix(date_prefix, date_year, string_prefix, start_year, end_year):
    """
    This function reads the prefix of the date from ISTC and returns both a standardised prefix and
    adopted settings for start_year and end_year. 
    """
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
    return(string_prefix, string_year, start_year, end_year)

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

    if date_prefix == "" and date_year_to == "" and date_between_year == "":
        #If there is only one date
        print("Only one year: ")
        print(date_year)
        if date_year != "":
        #This is not the case if there is a date such as "Between Jan. and Oct. 1488"
            string_year = date_year + " "
            start_year = int(date_year)
            end_year = int(date_year)
    elif date_prefix != "" and date_year_to == "" and date_between_year == "":
        #If there is only one date, that is not exact
#                    print("only one year, but prefixes")
        string_prefix, string_year, start_year, end_year = \
            analyse_prefix(date_prefix, date_year, string_prefix, start_year, end_year)
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
                   "Apr. ": "April", "May " : "May ", "June " : "June ", "July " : "July ", \
                    "Aug. " : "August ", "Sep. " : "September ", "Sept. " : "September ", \
                    "Oct. " : "October ", "Nov. " : "November ", "Dec. " : "December "}
    month_numbers = {"Jan. " : 1, "Feb. " : 2, "Mar. " : 3, "Apr. ": 4, "May " : 5, "June " : 6, \
                     "July " : 7, "Aug. " : 8, \
                    "Sep. " : 9, "Sept. " : 9, "Oct. " : 10, "Nov. " : 11, "Dec. " : 12}
    start_month = 0
    end_month = 0

    if date_between_month !="":
        string_month_between = month_names[date_between_month]
        number_month_between = month_numbers[date_between_month]
        end_month = int(number_month_between)
    elif date_between_year != "":
        # Thus, there is no end month but an end year in this case,
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
    return (string_month, start_month, end_month)

@classes.func_logger
def analyse_day(date_between_day, date_between_year, string_day_between, \
                date_day, end_month, end_year):
    """
    This function parses indications of days. 
    """
    end_day = 0
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
    return (string_day, start_day, end_day)
