#pylint: disable=C0301,C0303
"""
In the GND, dates are indicated in a somewhat confusing way. First of all, there can be more than one date statement for an entry, e.g. one can give only years, the other exact days. 
Each statement consists of the main date expression, a comment field, and a standardised field that has for persons four settings - years of life / exact days of life / years of activity / exact days of activity. 
In some cases, all information is in the main expression, in some cases the information in the comment field modifies it, sometimes, the comment field gives more precise dates. 
The first iteration of the date parser only uses the main expression but not yet the comment field. 
It first checks if there is only one date, or if there are two dates as start and end, and sends each single date to date_single_parsing. 
The resulting information (in a number of individual fields) is then assessed and used to construct a string and dates for start and end of a search as tuples, as well as an indicator if it is a lifespan or an activity span
Tuples are used instead of standard datetime objects because (a) they allow dates BC without difficulty and (b) there is no need for timedelta functions. 
"""
import re
import classes


def english_ordinal_suffix(number):
    """
This function returns the suffix transforming an English number into an ordinal
    """
    if len(number) > 1 and number[-2] == "1": #it cannot be longer, but shorter
        abbreviation = "th"
    else:
        if number[-1] == "1":
            abbreviation = "st"
        elif number[-1] == "2":
            abbreviation = "nd"
        elif number[-1] == "3":
            abbreviation = "rd"
        else:
            abbreviation = "th"
    return abbreviation

def date_single_parsing(datestring_raw):
    """ This function parses a single date (e.g., one of a date in a "9999-9999" statement) and returns a number of strings that have to be pieced together for a datestring as well as a start date
        and an end date as tuples
    """
    date_precision = "" # for determination of precision
    date_aspect = "" # for determination whether it is dates of life or dates of activity
    date_type = "" # states if there is an indication that it is a start date or an end date    
    short_date = True #This field indicates if the date is simple so that it can be written in the fortm "X-Y" instead of "born X, died Y"
    BC_indicator = False
    day_string_raw = ""
    month_string_raw = ""
    year_string_raw = ""
    year_end_string_raw = ""
    year_string = "xxx"
    date_prefix_1 = ""
    date_prefix_2 = ""
    date_suffix = ""
    day_string = ""
    month_string = ""
    year_string = ""
    year_end_string = ""
    prefix_0_raw = ""
    prefix_1_raw = ""
    prefix_2_raw = ""
    year_value_start = 0

    month_names = {"1" : "January ", "2" : "February ", "3": "March ", "4" : "April ", "5" : "May ", "6" : "June ", "7" : "July ", \
                   "8" : "August ", "9" : "September ", "10" : "October ", "11" : "November ", "12" : "December "}
    date_single_pattern = r'(gest\.|gestorben |starb |tod |todesjahr |todesdatum |lebte noch |lebte |aktiv |wirkte |tätig |schrieb |active |\*|b\.|geb |geb\.|geboren |geburtsjahr |\(get\.\) |getauft am |getauft |\(getauft\) |taufe |taufdatum '\
        r'begraben\) |begraben am |nachweisbar |nachgewiesen |bezeugt |dokumentiert |erwähnt |erw.|belegt |fl |fl\.|flor\.|tätig |wirkte |wirkungsdaten |wirkungsdaten: |wirkungsjahr |erstmals erwähnt |letztmals erwähnt |veröff\.|veroeff\.|erscheinungsjahr )?'\
        r'((\d\.h\.|\d\.hälfte |\d h\.|\d hälfte |erste hälfte |\d\.v\.|\d\.viertel |\d v\.|\d viertel |erstes viertel |letztes viertel |\d\.drittel |\d drittel|letztes drittel |in der \d\.hälfte )(d\.|des )?)?' \
        r'([a-wyzäöüß()\.* :,]*( |\.))?([\d\.\?xv/]*)([a-zäöüß()\.\?, =]*)?'


    if re.match(r"\d{4}, ?\d{4}", datestring_raw): # This means the special case of several years separated by comma. It is simply since it seems to always about exact years AD
        date_aspect = "a"
        date_precision = "year"
        prefix_1_raw = ""
        prefix_0_raw = "erwähnt"
        figures_raw = ""
        day_string = ""
        day_value_start = 1
        day_value_end = 31
        month_string = ""
        month_value_start = 1
        month_value_end = 12
        suffix_raw = ""
        datestring_raw = datestring_raw.replace(", ", ",")
        if re.match(r"\d{4},\d{4},\d{4}", datestring_raw):                       
            year1 = datestring_raw[0:4]
            year2 = datestring_raw[5:9]
            year3 = datestring_raw[10:14]
            year_value_start = min(int(year1), int(year2), int(year3))
            year_value_end = max(int(year1), int(year2), int(year3))
            year_string = year1 + ", " + year2 + ", and " + year3
        else:
            year1 = datestring_raw[0:4]
            year2 = datestring_raw[5:9]
            year_value_start = min(int(year1), int(year2))
            year_value_end = max(int(year1), int(year2))
            year_string = year1 + " and " + year2
        if "erscheinungsjahr" in datestring_raw:
            prefix_0_raw = "erscheinungsjahr"
            date_aspect = "a"
        date_precision = "year"    

        


    else: # all normal dates
        if "zwischen " in datestring_raw:  # turns "zwischen XXXX and XXXX" into "XXXX/XXXX"
            datestring_raw = datestring_raw.replace("zwischen ", "")
            datestring_raw = datestring_raw.replace(" und ", "/")
            datestring_raw = datestring_raw.replace(" u.", "/")
        date_single_parsed = re.match(date_single_pattern, datestring_raw).groups()
        prefix_0_raw = date_single_parsed[0]        
        prefix_1_raw = date_single_parsed[1] #elements 2, 3, 5 are not needed
        prefix_2_raw = date_single_parsed[4]
        figures_raw = date_single_parsed[6]
        suffix_raw = date_single_parsed[7]
        if suffix_raw:
            suffix_raw = suffix_raw.strip()
        figures_raw = figures_raw.replace("..", "xx") # sometimes, two dots are used for missing numbers, e.g. 19.. instead of 19XX. This is here changed, since ".." causes troubles

    figures_pattern = r'(v)?([\d\?x]{1,2}\.)?([\d\?x]{1,2}\.)?(v?\d{1,4}[x\?]{0,2}\.?v?|xxxx)(/\d{1,2}\.|/\d{1,4})?' #This pattern should work for most cases, with 
    figures_divided = re.match(figures_pattern, figures_raw)
    if figures_divided:
        BC_string_raw = figures_divided.groups()[0]
        day_string_raw = figures_divided.groups()[1]
        month_string_raw = figures_divided.groups()[2]
        if day_string_raw and not month_string_raw: # If there is onl(um a month given, but no da(um.
            month_string_raw = day_string_raw
            day_string_raw = ""
        year_string_raw = figures_divided.groups()[3]
        year_end_string_raw = figures_divided.groups()[4]
        
        # Days
        if day_string_raw and (day_string_raw == "0." or day_string_raw == "00."):
            day_string = ""
            day_value_start = 1
            day_value_end = 99
        elif day_string_raw and day_string_raw[0:-1].isnumeric():
            day_string = day_string_raw[0:-1].lstrip("0")
            day_string = day_string + " "
            day_value_start = int(day_string)
            day_value_end = int(day_string)
            date_precision = "day"
        elif day_string_raw == "1x." or day_string_raw == "2x.":                       
            day_string = "between " + day_string_raw[0:-2] + "0 and " + day_string_raw[0:-2] + "9 "
            day_value_start = int(day_string_raw[0:-2] + "0")
            day_value_end = int(day_string_raw[0:-2] + "9")
            date_precision = "day - circa"
            short_date = False
        elif day_string_raw == "0x.":
            day_string = "between 1 and 9 "
            day_value_start = 1
            day_value_end = 9
            date_precision = "day - circa"
            short_date = False
        elif day_string_raw == "xx.":
            day_string = ""
            day_value_start = 1
            day_value_end = 99
        else:
            day_string = ""
            day_value_start = 1
            day_value_end = 99 #must be adjusted to the number of days in a month

        # Months
        if month_string_raw and month_string_raw[0:-1].isnumeric() and month_string_raw[0:-1] != "00":
            month_string_raw = month_string_raw[0:-1].lstrip("0")
            if month_string_raw in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]:

                month_string = month_names[month_string_raw]
                month_value_start = int(month_string_raw)
                month_value_end = int(month_string_raw)
                if date_precision == "":
                    date_precision = "month"
            else:
                month_string = "!!!!!month could not be parsed!!!!!!"
                month_value_start = 1
                month_value_end = 12
        elif month_string_raw == "00." or month_string_raw == "xx." and day_string != "":
            month_string = "?? "
            month_value_start = 1
            month_value_end = 12
        else: 
            month_string = ""
            month_value_start = 1
            month_value_end = 12
        # Years
        if BC_string_raw == "v":
            BC_indicator = True
        if suffix_raw == "v.chr." or suffix_raw == "v. chr." or suffix_raw == "jh.v.chr." or suffix_raw == "jh. v.chr." or suffix_raw == "jh. v. chr." or suffix_raw == "jh.v.chr":
            BC_indicator = True
        if year_string_raw[0:1] == "v":
            BC_indicator = True
            year_string_raw = year_string_raw[1:]
        if year_string_raw[-1:] == "v":
            BC_indicator = True
            year_string_raw = year_string_raw[:-1]
        if year_string_raw and year_string_raw.isnumeric() and (suffix_raw and (suffix_raw[:2] == "jh" or suffix_raw[:5] == "jahrh")):
            #this is for the common mistake that the century is indicated, but without a dot after the number, e.g. "8 Jh."
            #it seemed easiest just to add the dot. 
            year_string_raw = year_string_raw + "."
        if year_string_raw and year_string_raw.isnumeric() and not year_end_string_raw:
            year_string = year_string_raw
            year_value_start = int(year_string)
            year_value_end = int(year_string)
            if date_precision == "":
                date_precision = "year"
        elif year_string_raw and year_string_raw.isnumeric() and year_end_string_raw and year_end_string_raw != ".": #the last condition means that the year_end is not a century
            if year_end_string_raw[-1] != ".":
                year_end_string_raw = year_end_string_raw[1:] #removing the leading slash
                if len(year_end_string_raw) == 1:
                    year_end_string = year_string_raw[:-1] + year_end_string_raw
                elif len(year_end_string_raw) == 2:
                    year_end_string = year_string_raw[:-2] + year_end_string_raw
                elif len(year_end_string_raw) >= 3: # I assume that in this case there is no abbreviation
                    year_end_string = year_end_string_raw
                else:
                    year_end_string = "!!!!!year_end_string could not be parsed"


                year_value_start = int(year_string_raw)
                if year_end_string.isnumeric(): # if it is not an error message
                    year_value_end = int(year_end_string)
                if year_value_end - year_value_start > 500: # this is the case if the first year is from the Islamic Calendar
                    year_string = str(year_value_end) + " (" + str(year_value_start) + " AH)"
                    year_value_start = year_value_end
                    date_precision = "year"
                elif year_value_end - year_value_start > 500: # this is the case if the second year is from the Islamic Calendar
                    year_string = str(year_value_start) + " (" + str(year_value_end) + " AH)"
                    year_value_end = year_value_start
                    date_precision = "year"
                else: 
                    date_precision = "year - circa"
                    year_string = "between " + year_string_raw + " and " + year_end_string

                    short_date = False
                
        elif year_string_raw and year_string_raw[0:-1].isnumeric() and (year_string_raw[-1] == "x" or year_string_raw[-1] == "?"):
            if len(year_string_raw) < 5: # if it is more than 5, a final question mark does not mean a missing digit, but rather that it is unclear, e.g., -1750?
                year_string = "between " + year_string_raw[0:-1] + "0 and " + year_string_raw[0:-1] + "9"
                if BC_indicator == False:
                    year_value_start = int(year_string_raw[0:-1] + "0")
                    year_value_end = int(year_string_raw[0:-1] + "9")
                else: 
                    year_value_start = int(year_string_raw[0:-1] + "9")
                    year_value_end = int(year_string_raw[0:-1] + "1")
                date_precision = "decade"
                short_date = False
            else: # This means the type "1550?"
                year_string = year_string_raw[:4]
                date_prefix_2 = "c. "
                if BC_indicator == False:
                    year_value_start = int(year_string_raw[:4]) - 5
                    year_value_end = int(year_string_raw[:4]) + 5
                else:
                    year_value_start = int(year_string_raw[:4]) + 5
                    year_value_end = int(year_string_raw[:4]) -5

        elif year_string_raw and year_string_raw[0:-2].isnumeric() and (year_string_raw[-2:] == "xx" or year_string_raw[-2:] == "??" \
                                                                        or year_string_raw[-2:] == "x?" or year_string_raw[-2:] == "?x"):                
            year_string = "between " + year_string_raw[0:-2] + "00 and " + year_string_raw[0:-2] + "99"
            if BC_indicator == False:
                year_value_start = int(year_string_raw[0:-2] + "00")
                year_value_end = int(year_string_raw[0:-2] + "99")
            else: 
                year_value_end = int(year_string_raw[0:-2] + "00")
                year_value_start = int(year_string_raw[0:-2] + "99")
            date_precision = "century"
            short_date = False
        elif year_string_raw and year_string_raw == "xxxx":
            year_string = "????"
            year_value_start = 0
            year_value_end = 0
        elif year_string_raw and year_string_raw[0:-1].isnumeric() and year_string_raw[-1] == ".": #if it is an indication of centuries          
            # this is normally followed by an abbrevation such as "Jh.", but the dot alone shows that a century is indicated, and the "Jh." etc. can be ignored for parsing
            if year_end_string_raw and year_end_string_raw[-1] == ".":
                century_start_number = year_string_raw[0:-1]
                century_end_number = year_end_string_raw[1:-1]
                year_string = "between " + century_start_number + english_ordinal_suffix(century_start_number) + " and " + century_end_number + english_ordinal_suffix(century_end_number) + " century"
                if BC_indicator == False:
                    year_value_start = int(str(int(century_start_number)-1) + "01")
                    year_value_end = int(century_end_number + "00")
                else:
                    year_value_start = int(century_start_number + "00")
                    year_value_end = int(str(int(century_end_number)-1) + "01")
            else:
            
                century_number = year_string_raw[0:-1]           
                year_string = century_number + english_ordinal_suffix(century_number) + " century"
                if BC_indicator == False:
                    year_value_start = int(str(int(century_number)-1) + "01")
                    year_value_end = year_value_start + 99
                else:
                    year_value_start = int(century_number + "00")
                    year_value_end = year_value_start - 99      
        else: 
            year_string = "!!!!year could not be parsed!!!!"
        if BC_indicator == True:
            year_string = year_string + " BC"
            year_value_start = 0 - year_value_start
            year_value_end = 0 - year_value_end

        # The following adjust day_value_end to the last day of the month
        if day_value_end == 99:
            match month_value_start:
                case 1|3|5|7|8|10|12:
                    day_value_end = 31
                case 4|6|9|11:
                    day_value_end = 30
                case 2:
                    if year_value_start%4 == 0 and (year_value_start%100 != 0 or year_value_start%400 == 0):
                        day_value_end = 29
                    else:
                        day_value_end = 28
    
    if prefix_0_raw:
        prefix_0_raw = prefix_0_raw.strip()
        match prefix_0_raw:
            case "*"|"b."|"geb"|"geb."|"geboren"|"geburtsjahr":
                date_aspect = "l"
                date_type = "start"
            case  "(get.)"|"(getauft)"|"getauft"|"getauft am"|"getauft"|"taufe"|"taufdatum":
                date_prefix_1 = "baptised "
                date_aspect = "l"
                date_type = "start"
                short_date = False
            case "lebte":
                date_aspect = "l"
            case "aktiv"|"wirkte"|"tätig"|"schrieb"|"active"|"fl"|"fl."|"flor."|"tätig"|"wirkte"|"wirkungsdaten"|"wirkungsdaten:":
                date_aspect = "a"
            case "nachweisbar"|"nachgewiesen"|"bezeugt"|"dokumentiert"|"erwähnt"|"erw."|"belegt":
                date_prefix_1 = "documented "
                date_aspect = "a"
            case "veröff."|"veroeff."|"erscheinungsjahr)"|"erscheinungsjahr":
                date_aspect = "a"
                date_prefix_1 = "publications from "
            case "gest."|"gestorben"|"starb"|"tod"|"todesjahr"|"todesdatum":
                date_aspect = "l"
                date_type = "end"
            case "lebte noch": #Here, the separation into prefix_0 and prefix_2 didn't work
                date_prefix_2 = "after "
                year_value_end = year_value_end + 10
                date_type = "end"
                date_aspect = "l"
            case "begraben"|"begraben am":
                date_prefix_1 = "buried "
                date_aspect = "l"
                date_type = "end"
                short_date = False
            case "erstmals erwähnt":
                date_aspect = "a"
                date_type = "start"
                date_prefix_1 = "first documented "
            case "letztmals erwähnt":
                date_aspect = "a"
                date_type = "end"
                date_prefix_1 = "last documented "

    if prefix_1_raw:
        prefix_1_raw = prefix_1_raw.strip()
        prefix_1_pattern = r'(in der )?(\d\.|\d |letztes |erste |erstes )(h\.|hälfte|drittel|v\.|viertel)( d\.| des)?'
        prefix_1_divided = re.match(prefix_1_pattern, prefix_1_raw)
        if prefix_1_divided:
            part_number = prefix_1_divided.groups()[1]
            part_name = prefix_1_divided.groups()[2] # parts 0 and 3 are not relevant
            date_precision = "century - part"
            match part_name:
                case "h."|"hälfte":
                    if part_number == "1." or part_number == "1 " or part_number == "erste ":
                        date_prefix_2 = "first half "
                        year_value_end = year_value_end -50
                    if part_number == "2." or part_number == "2 ":
                        date_prefix_2 = "second half "
                        year_value_start = year_value_start +50
                case "drittel":
                    if part_number == "1." or part_number == "1 ":
                        date_prefix_2 = "first third "
                        year_value_end = year_value_end -67
                    if part_number == "2." or part_number == "2 ":
                        date_prefix_2 = "second third "
                        year_value_start = year_value_start +33
                        year_value_end = year_value_start + 32
                    if part_number == "3." or part_number == "3 " or part_number == "letztes ":
                        date_prefix_2 = "last third "
                        year_value_start = year_value_start +66
                case "v."|"viertel":
                    if part_number == "1." or part_number == "1 " or part_number == "erstes ":
                        date_prefix_2 = "first quarter "
                        year_value_end = year_value_start + 24
                    if part_number == "2." or part_number == "2 ":
                        date_prefix_2 = "second quarter "
                        year_value_start = year_value_start +25
                        year_value_end = year_value_start + 24
                    if part_number == "3." or part_number == "3 ":
                        date_prefix_2 = "third quarter "
                        year_value_start = year_value_start +50
                        year_value_end = year_value_start + 24
                    if part_number == "4." or part_number == "letztes ":
                        date_prefix_2 = "last quarter "
                        year_value_start = year_value_start +75
                case _:
                    pass
        else:
            pass
    if prefix_2_raw:    
        prefix_2_raw = prefix_2_raw.strip()
        match prefix_2_raw:
            case "im": #important information in the suffix
                pass
            case "anfang"|"anfang des"|"anfang d."|"ca.anf."|"ca.anfang"|"seit anfang d."|"frühes"|"anf."|"beginn des"|"beginn"|"beginn d.":
                date_prefix_2 = "early "
                if BC_indicator == False:
                    year_value_end = year_value_start + 19
                else:
                    year_value_end = year_value_start +20
            case "mitte"|"mitte des"|"ca mitte"|"ca.mitte":
                date_prefix_2 ="Mid-"
                if BC_indicator == False:
                    year_value_start = year_value_start + 39
                    year_value_end = year_value_start + 20
                else: 
                    year_value_start = year_value_start + 39
                    year_value_end = year_value_start + 20
            case "spätes"|"ende"|"ende des"|"ca.ende"|"ausgang"|"ende d.":
                date_prefix_2 = "late "
                year_value_start = year_value_start + 80 
            case "mitte/ende":
                date_prefix_2 = "Mid- to late"
                year_value_start = year_value_start + 40 # should mean, from e.g. 1900-1960
            case "um"|"(um)"|"c"|"c."|"ca"|"ca."|"ca,"|"ca.("|"circa": 
                date_prefix_2 = "c. "
                if year_value_start != 0: #this rules out dates such as "ca. unbekannt" that otherwise create error messages
                    year_value_start = year_value_start - 5
                    year_value_end = year_value_end + 5
            case "ca.geboren": #in this case, the division into prefix_0 and prefix_2 doesn't work
                date_prefix_2 = "c. "
                year_value_start = year_value_start - 5
                year_value_end = year_value_end + 5
                date_aspect = "l"
                date_type = "start"
            case "seit ca.":
                date_prefix_2 = "c. "
                year_value_start = year_value_start - 5
                year_value_end = year_value_end + 5
                date_aspect = "a"
                date_type = "start"
            case "(vor)"|"vor)"|"vor"|"vor ca."|"kurz vor"|"vor dem":
                date_prefix_2 = "before "
                year_value_start = year_value_start - 10
            case "(nach)"|"nach)"|"nach"|"nach dem"|"kurz nach"|"post"|"ca.nach":
                date_prefix_2 = "after "
                year_value_end = year_value_end + 10
            case "ab"|"ab dem"|"seit"|"seit d."|"seit dem"|"seit ca."|"seit anfang d.": 
                date_type = "start"
            case "umnach":
                date_prefix_2 = "c. or after"
                short_date = False
                year_value_start = year_value_start - 5
                year_value_end = year_value_end + 10
            case "(":
                pass           
            case _:
                pass
                  

    if suffix_raw:

        match suffix_raw:
            case "v.chr."|"jh.v.chr."|"jh.v.chr":
                pass # This option has been dealt with earlier
            case "jh"|"jh."|"jahrhundert"|"jahrhunderts"|"jd."|"jhd."|"jhr."|"jht"|"jht."|"jahrh.":            
                pass # if the year ends with a full-stop, it is deemed to mean a century
            case "|":
                pass # no idea why this is displayed
            case "(?)"|", ca."|",ca."|"ca."|"(ca."|"?"|"um"|"(um)"|"jh.?"|"jhd.?"|"jht.?":
                date_prefix_2 = "c. "
                date_precision = "year - circa"
                if year_value_start != 0:
                    year_value_start = year_value_start - 5
                    year_value_end = year_value_end + 5
            case "(nach)"|"(post)":
                date_prefix_2 = "after "
                year_value_end = year_value_end + 10
            case "(vor)":
                date_prefix_2 = "before "
                year_value_end = year_value_end - 10
            case "odanach":  # I replace "oder danach" / "oder später" with "odanach" to avoid confusion with two dates separated by "oder"
                date_suffix = "or later"
                date_precision = "year - circa"
                year_value_end = year_value_end + 10
            case "ofrüher": # I replace "oder früher" with "ofrüher" to avoid confusion with two dates separated by "oder"
                date_suffix = "or earlier"
                date_precision = "year - circa"
                year_value_start = year_value_start - 10
            case "jahrhundert, anfang biis mitte":
                date_prefix_2 = "early to Mid-"
                date_precision = "century - part"
                year_value_end = year_value_end - 40 # should mean, from e.g. 1900-1960
            case "jahrhundert, mitte biis ende"|"jh., mitte biis ende":
                date_prefix_2 = "Mid- to late "
                date_precision = "century - part"
                year_value_start = year_value_start + 40 # should mean, from e.g. 1900-1960
            case "jahrhundert, mitte":                
                date_prefix_2 ="Mid-"
                date_precision = "century - part"
                if BC_indicator == False:
                    year_value_start = year_value_start + 39
                    year_value_end = year_value_start + 20
                else: 
                    year_value_start = year_value_start + 40
                    year_value_end = year_value_start + 20              
            case "er"|"er jahre": # as 1990er
                year_string = "between " + year_string + " and " + str(int(year_string)+9)
                year_value_end = year_value_start + 9
                date_precision = "decade"
            case "erscheinungsjahr"|"(erscheinungsjahr)"|"erscheinungjahr"|"erscheinungsjahre"|"(erscheinungsjahre)"|"erschienen"|"jh.erscheinungsjahr": 
                date_aspect = "a"
                date_prefix_1 = "publications from "
            case "(wirkungszeit)"|"fl."|"(wirkungsjahr)"|"wirkungsjahr"|"wirkungsjahre"|"erwähnungsjahr"|"jh.(wirkungszeit)":
                date_aspect = "a"
            case "nachgewiesen"|"erwähnt"|"(erwähnt)"|"erwähnungsjahr"|"nachweisbar"|"belegt":
                date_prefix_1 = "documented "
                date_aspect = "a"
            case "geb." |"geboren"|"jh.geb.":
                date_aspect = "l"
                date_type = "start"
            case "(= taufdatum)"|"( = taufdatum)"|"(taufe)"|"(getauft)":
                date_prefix_1 = "baptised "
                short_date = False
                date_aspect = "l"
                date_type = "start"
            case "(erste erwähnung)":
                date_aspect = "a"
                date_type = "start"
                date_prefix_1 = "first documented "
            case "gest."|"gestorben"|"gestorb."|"%todesjahr ca."|"todesjahr ca.":
                date_aspect = "l"
                date_type = "end"
            case "jh.ff."|"jh.ff": # used primarily for families
                date_type = "start"
            case "h"|"h.s.":
                date_suffix = "AH (start and end date will not be calculated correctly)"
            case "ff."|"jh.ff.": # typically used for families
                date_suffix = "and later"
                date_type = "start"
            case _:
                date_suffix = "!!!!!Suffix_raw could not be parsed!!!!!!!"
    if year_string[0:7] == "between" and date_prefix_2 == "late ": # Reformatting awkward formulae
        year_string = year_string[0:8] + "late " + year_string[8:]
        date_prefix_2 = ""
    year_string = year_string + " " # I do this at the end because there are so many manipulations of year_string
    if year_value_start: #this is to prvent an error messages
        date_start = (year_value_start, month_value_start, day_value_start)
        date_end = (year_value_end, month_value_end, day_value_end)
    return(date_prefix_1, date_prefix_2, day_string, month_string, year_string, date_suffix, short_date, date_aspect, date_precision, date_type, date_start, date_end)




def date_overall_parsing(datestring, date_comments, date_indicator):
    """
\todo
    """
    date_start_parsed = ""
    date_end_parsed = ""
    date_only_parsed = ""
    start_aspect = ""
    end_aspect = ""
    start_prefix_1 = ""
    start_prefix_2 = ""
    start_suffix = ""
    start_alternative_prefix_1 = ""
    start_alternative_prefix_2 = ""
    start_alternative_day = ""
    start_alternative_month = ""
    start_alternative_year = ""
    start_alternative_suffix = ""
    start_alternative_string = ""
    end_alternative_string = ""
    only_alternative_type = ""
    start_alternative_start_date = ()
    start_alternative_end_date = ()
    end_alternative_start_date = ()
    end_alternative_end_date = ()
    only_alternative_start_date = ()
    only_alternative_end_date = ()

    end_prefix_1 = ""
    end_prefix_2 = ""
    end_suffix = ""
    start_day = ""
    start_month = ""
    start_year = ""
    end_day = ""
    end_month = ""
    end_year = ""
    only_alternative_string = ""
    date_type = ""
    date_string = ""
    string_replacement = {"–" : "-", "- " : "-", " -" : "-", "  " : " ", ". " : ".", " ." : ".", "–" : "-", "−" : "-", " " : " ", "[" : "", "]" : "", "|": "", "/ " : "/", "/Anf." : "-Anf. ", \
                          "/Anfang" : "-Anfang", "- Anf." : "-Anfang ", "-Anf.": "-Anfang ", "-ca.Anf." : "-Anfang ", "Anfang bis Mitte" : "Anfang biis Mitte", "Mitte bis Ende" : "Mitte biis Ende",  \
                          "/1.H." : "-1.H.", "/2.H." : "-2.H.", "/1.Hälfte " : "-1.H.", "/2.Hälfte " : "-2.H.", "Jh./" : "/", "ca.1.H." : "1.H.", "ca.2.H." : "2.H.",\
                          " bis " : "-", "bis " : "-", "ca.(" : "ca.", "ca.)" : "ca.", "*": "geb.", ", +" : "-", "+" : "gest.", "th century" : ". Jh.", "th cent" : ". Jh", \
                          ", †" : "-",  "; †" : "-", "†" : "gest." , "um/nach" : "umnach", "oder danach" : "odanach", "oder später" : "odanach", "oder früher" : "ofrüher", \
                            "Januar " : "01.", "Februar " : "02.", "März " :"03.", "April " : "04.", "Mai " : "05.", "Juni " : "06.", "Juli ":"07.", "August ": "08.", \
                            "September " : "09.", "Oktober ": "10.", "November " : "11.", "Dezember " : "12.", "Ersch.-Jahr" : "erscheinungsjahr", "Ersch.-jahr" : "erscheinungsjahr", ", gest." : "-", "; gest." : "-", ", gestorben" : "-"}
    # The replacment of some "bis" with "biis" prevents its replacement in the next step. Some signs such as '*" are replaced here with words to avoid later confusion"
    for old, new in string_replacement.items():
        datestring = datestring.replace(old, new)        
    datestring = datestring.lower()
    if datestring == "ca. ":
        datestring = ""
    if datestring[0] == "%": #some strings start with this
        datestring = datestring[1:]
    if re.match(r'ca\.\!\d{8}\w\!', datestring): #exlucdes references to Pica PPN numbers
        datestring = ""
    if datestring[0:3] == "ca.": #"ca." can have the meaning "circa", but it is also (today) and obligatory introdcution for any datestring that is freely formulated
                                # in this case, it has no meaning and it should be removed
        for x in datestring[3:]:
            if x in "abcdefghijklmnopqrstuwyz,": # freely formulated datestrings will contain letters, whereas standard datestrings can only contain the letters v(or Christus) and x(unknown digit)
                datestring = datestring[3:]
                break
    if datestring[0:4] == "ca.-":
        datestring = "-ca." + datestring[4:]
    missing_dot = re.search(r"\d{2}\.\d{6}", datestring) # Not rarely, there is no dot between the digits for the months and those for the year, e.g. "15.111380". It has to run twice, since the problem can occur twice
    if missing_dot:
        missing_dot_position = missing_dot.start() + 5
        datestring = datestring[:missing_dot_position] + "." + datestring[missing_dot_position:]
    missing_dot = re.search(r"\d{2}\.\d{6}", datestring) 
    if missing_dot:
        missing_dot_position = missing_dot.start() + 5
        datestring = datestring[:missing_dot_position] + "." + datestring[missing_dot_position:]
    um_missing_space = re.search(r"um\d{2}", datestring) # Sometimes, there is no blank after "um"
    if um_missing_space:
        um_missing_space_position = um_missing_space.start() + 2
        datestring = datestring[:um_missing_space_position] + " " + datestring[um_missing_space_position:]
    vor_missing_space = re.search(r"vor\d{2}", datestring) # Sometimes, there is no blank after "vor"
    if vor_missing_space:
        vor_missing_space_position = vor_missing_space.start() + 3
        datestring = datestring[:vor_missing_space_position] + " " + datestring[vor_missing_space_position:]
    nach_missing_space = re.search(r"nach\d{2}", datestring) # Sometimes, there is no blank after "nach"
    if nach_missing_space:
        nach_missing_space_position = nach_missing_space.start() + 4
        datestring = datestring[:nach_missing_space_position] + " " + datestring[nach_missing_space_position:]


    
    # There are the following possibilities: a start date and an end date / a start date only / an end date only / a date that does not specify if it is start or end (e.g., just  rough century)
    # If there is a start date and an end date, they are separated by a dash. 
    # If there is only one unspecified date, it comes without a dash. 
    # Only a start date or only an end date can be written in two ways: either a dash that has on one side a date and on the other side nothing for a placeholder,#
    # or a single date with a verbal indication that it is a start date or an end date (e.g. "gestorben 1550")
    if "-" in datestring:
        #date_only_type = "none" #This would be used if there is only one date given that is neither identified as start or as end date
        datestring_overall_pattern = r"([^-].*)?(-|--)([^-].*)?"
        datestring_overall_divided = re.match(datestring_overall_pattern, datestring).groups()
        if datestring_overall_divided[0] == None or datestring_overall_divided[0] == "" or datestring_overall_divided[0] == "xxxx" or datestring_overall_divided[0] == "xx.xx.xxxx" \
            or datestring_overall_divided[0] == "?" or datestring_overall_divided[0] == "ca." or datestring_overall_divided[0] == "ca. "or datestring_overall_divided[0] == "ca.?" \
            or datestring_overall_divided[0] == "(?)" or datestring_overall_divided[0] == "ca.xxxx" or datestring_overall_divided[0] == "1xxx" or datestring_overall_divided[0] == "xx.xx.1xxx":
            date_type = "end"
        else:
            datestring_start_raw = datestring_overall_divided[0]
            if "bzw." in datestring_start_raw or "oder" in datestring_start_raw or " or" in datestring_start_raw or "od." in datestring_start_raw or "o." in datestring_start_raw: \
                # "or" needs a blank that it cannot be confused with "vor", but eg. "Jh.or" does not occur, anyway
                datestring_start_raw_divided = re.match(r"(.*?)(bzw.|oder| or|od.|o.)(.*)", datestring_start_raw).groups()              
                date_raw_start_parsed = datestring_start_raw_divided[0].strip()
                date_raw_start_alternative_parsed = datestring_start_raw_divided[2].strip()
                date_start_parsed = date_single_parsing(date_raw_start_parsed)
                date_start_alternative_parsed = date_single_parsing(date_raw_start_alternative_parsed)
                start_alternative_prefix_1 = date_start_alternative_parsed[0]
                start_alternative_prefix_2 = date_start_alternative_parsed[1]
                start_alternative_day = date_start_alternative_parsed[2]
                start_alternative_month = date_start_alternative_parsed[3]
                start_alternative_year = date_start_alternative_parsed[4]
                start_alternative_suffix = date_start_alternative_parsed[5]
                start_alternative_string = "(or " + (start_alternative_prefix_1 + start_alternative_prefix_2 + start_alternative_day + start_alternative_month + start_alternative_year + start_alternative_suffix).strip() + ")"
                start_alternative_start_date = date_start_alternative_parsed[10]
                start_alternative_end_date = date_start_alternative_parsed[11]
            else:
                date_start_parsed = date_single_parsing(datestring_start_raw)
            start_prefix_1 = date_start_parsed[0]
            start_prefix_2 = date_start_parsed[1]
            start_day = date_start_parsed[2]
            start_month = date_start_parsed[3]
            start_year = date_start_parsed[4]
            start_suffix = date_start_parsed[5]
            start_short = date_start_parsed[6]
            start_aspect = date_start_parsed[7]
            start_precision = date_start_parsed[8]
            start_start_date = date_start_parsed[10]
            start_end_date = date_start_parsed[11]
            if start_alternative_string != "": # If there are alternatives, always use long form of date
                start_short = False

        if datestring_overall_divided[2] == None or datestring_overall_divided[2] == "" or datestring_overall_divided[2] == "xx.xx.xxxx" or datestring_overall_divided[2] == "xxxx" or \
            datestring_overall_divided[2] == "?" or datestring_overall_divided[2] == "ca." or datestring_overall_divided[2] == "ca. " or datestring_overall_divided[2] == "ca.?" \
                or datestring_overall_divided[2] == "(?)" or datestring_overall_divided[2] == "ca.xxxx" or datestring_overall_divided[2] == "1xxx" or datestring_overall_divided[2] == "xx.xx.1xxx":
            date_type = "start"
        else:
            datestring_end_raw = datestring_overall_divided[2]
            if "bzw." in datestring_end_raw or "oder" in datestring_end_raw or " or" in datestring_end_raw or "od." in datestring_end_raw  or "o." in datestring_end_raw: # "or" needs a blank that it cannot be confused with "vor", but eg. "Jh.or" does not occur, anyway
                datestring_end_raw_divided = re.match(r"(.*?)(bzw.|oder| or|od.|o.)(.*)", datestring_end_raw).groups()              
                date_raw_end_parsed = datestring_end_raw_divided[0].strip()
                date_raw_end_alternative_parsed = datestring_end_raw_divided[2].strip()
                if date_raw_end_alternative_parsed[0:1] == "-": #If there is a dash at the start of the alternative date ("-1500 oder -1510"), this should only be necessary for the end
                    date_raw_end_alternative_parsed = date_raw_end_alternative_parsed[1:]
                date_end_parsed = date_single_parsing(date_raw_end_parsed)
                date_end_alternative_parsed = date_single_parsing(date_raw_end_alternative_parsed)
                end_alternative_prefix_1 = date_end_alternative_parsed[0]
                end_alternative_prefix_2 = date_end_alternative_parsed[1]
                end_alternative_day = date_end_alternative_parsed[2]
                end_alternative_month = date_end_alternative_parsed[3]
                end_alternative_year = date_end_alternative_parsed[4]
                end_alternative_suffix = date_end_alternative_parsed[5]
                end_alternative_start_date = date_end_alternative_parsed[10]
                end_alternative_end_date = date_end_alternative_parsed[11]
                end_alternative_string = "(or " + (end_alternative_prefix_1 + end_alternative_prefix_2 + end_alternative_day + end_alternative_month + end_alternative_year + end_alternative_suffix).strip() + ")"
            else:
                date_end_parsed = date_single_parsing(datestring_end_raw)
            end_prefix_1 = date_end_parsed[0]
            end_prefix_2 = date_end_parsed[1]
            end_day = date_end_parsed[2]
            end_month = date_end_parsed[3]
            end_year = date_end_parsed[4]
            end_suffix = date_end_parsed[5]
            end_short = date_end_parsed[6]
            end_aspect = date_end_parsed[7]
            end_precision = date_end_parsed[8]
            end_start_date = date_end_parsed[10]
            end_end_date = date_end_parsed[11]
            if end_alternative_string != "": # If there are alternatives, always use long form of date
                end_short = False


    else:
        if "bzw." in datestring or "oder" in datestring or " or" in datestring or "od." in datestring or "o." in datestring: # "or" needs a blank that it cannot be confused with "vor", but eg. "Jh.or" does not occur, anyway
            datestring_raw_divided = re.match(r"(.*?)(bzw.|oder| or|od.|o.)(.*)", datestring).groups()              
            date_raw_parsed = datestring_raw_divided[0].strip()
            date_raw_alternative_parsed = datestring_raw_divided[2].strip()
            date_only_parsed = date_single_parsing(date_raw_parsed)
            date_alternative_parsed = date_single_parsing(date_raw_alternative_parsed)
            only_alternative_prefix_1 = date_alternative_parsed[0]
            only_alternative_prefix_2 = date_alternative_parsed[1]
            only_alternative_day = date_alternative_parsed[2]
            only_alternative_month = date_alternative_parsed[3]
            only_alternative_year = date_alternative_parsed[4]
            only_alternative_suffix = date_alternative_parsed[5]
            only_alternative_type = date_alternative_parsed[9]
            only_alternative_start_date = date_alternative_parsed[10]
            only_alternative_end_date = date_alternative_parsed[11]
            only_alternative_string = "(or " + (only_alternative_prefix_1 + only_alternative_prefix_2 + only_alternative_day + only_alternative_month + only_alternative_year + only_alternative_suffix).strip() + ")"
        else:
            date_only_parsed = date_single_parsing(datestring)
        date_type = date_only_parsed[9]
        # The following lines make sure that, if there is no indication of the date type parsed with the date proper but something parsed with the alternative date (e.g. '1550 (1560) geboren'), the latter is used
        if date_type == "" and only_alternative_type == "start":
            date_type = "start"
        if date_type == "" and only_alternative_type == "end":
            date_type = "end"


        match date_type:
            case "start":                
                start_prefix_1 = date_only_parsed[0]
                start_prefix_2 = date_only_parsed[1]
                start_day = date_only_parsed[2]
                start_month = date_only_parsed[3]
                start_year = date_only_parsed[4]
                start_suffix = date_only_parsed[5]
                start_short = date_only_parsed[6]
                start_aspect = date_only_parsed[7]
                start_precision = date_only_parsed[8]
                start_start_date = date_only_parsed[10]
                start_end_date = date_only_parsed[11]
            case "end":                
                end_prefix_1 = date_only_parsed[0]
                end_prefix_2 = date_only_parsed[1]
                end_day = date_only_parsed[2]
                end_month = date_only_parsed[3]
                end_year = date_only_parsed[4]
                end_suffix = date_only_parsed[5]
                end_short = date_only_parsed[6]
                end_aspect = date_only_parsed[7]
                end_precision = date_only_parsed[8]
                end_type = date_only_parsed[9]
                end_start_date = date_only_parsed[10]
                end_end_date = date_only_parsed[11]

            case "":
                date_type = "only"
                only_prefix_1 = date_only_parsed[0]
                only_prefix_2 = date_only_parsed[1]
                only_day = date_only_parsed[2]
                only_month = date_only_parsed[3]
                only_year = date_only_parsed[4]
                only_suffix = date_only_parsed[5]
                only_short = date_only_parsed[6]
                only_aspect = date_only_parsed[7]
                only_precision = date_only_parsed[8]
                only_start_date = date_only_parsed[10]
                only_end_date = date_only_parsed[11]


    if date_start_parsed and date_end_parsed:
        if start_year.strip() != "" and end_year.strip() != "": # This and the following clauses remove 'pseudo-dates'. 
            date_type = "both"
        elif start_year.strip() != "" and end_year.strip() == "":
            date_type = "start"
        elif start_year.strip() == "" and end_year.strip() != "":
            date_type = "end"
        elif start_year.strip() == "" and end_year.strip() == "":
            pass # I have to think how I call it if there is no date
        




    ##### Add here extra material from the comment field
        

    
        
    if date_type == "both":
        if start_aspect == "": #here, the defaults settings are given, if there is no more specific information available
            if date_indicator == "datl" or date_indicator == "datx":
                start_aspect = "l"
            if date_indicator == "datw" or date_indicator == "datz":
                start_aspect = "a"
        if end_aspect == "":
            end_aspect = start_aspect
        # The following lines achieve that, if the alternative dates give a larger timespan than the main dates, they are used for the search timespan
        if start_alternative_start_date:
            if start_alternative_start_date < start_start_date:
                start_start_date = start_alternative_start_date
        if end_alternative_end_date:
            if end_alternative_end_date > end_end_date:
                end_end_date = end_alternative_end_date
        
        
        if start_start_date[0] > 0 and end_start_date[0] < 0: #This means that onyl the second date is marked as "BC"
            start_start_date = (0-start_start_date[0], start_start_date[1], start_start_date[2])
            start_year = start_year + "BC"


        if start_short and end_short and (end_aspect == start_aspect or end_aspect == ""):
            if start_prefix_1 == "" and start_aspect == "a":
                start_prefix_1 = "active "
            date_string = start_prefix_1 + start_prefix_2 + start_day + start_month + start_year + start_suffix + "-" + end_prefix_1 + end_prefix_2 + end_day + end_month + end_year + end_suffix
            date_start = start_start_date
            date_end = end_end_date

        else: 
            if start_prefix_1 == "":
                if start_aspect == "l":
                    start_prefix_1 = "born "
                else: #can only be 'life' or 'activity'
                    start_prefix_1 == "active from "
            
            if end_prefix_1 == "":
                if end_aspect == "l":
                    end_prefix_1 = ", died "
                else:
                    if end_aspect == "a":
                        if start_aspect == "a":
                            end_prefix_1 = " to "
                        else: 
                            end_prefix_1 = ", active until "
            else:
                end_prefix_1 = ", " + end_prefix_1
            # Add something that, if end date of start later than start date of end or vice versa and one of the two string is a "between ... and ... ", it is changed to an "after ..." or similar
            if start_year != "" or end_year != "":
                date_string = (start_prefix_1 + start_prefix_2 + start_day + start_month + start_year + start_suffix + start_alternative_string + end_prefix_1 + end_prefix_2 + end_day + end_month + end_year + end_suffix + end_alternative_string).strip()
                date_start = start_start_date
                date_end = end_end_date
            else:
                date_string = ""
        date_aspect = start_aspect    
    if date_type == "start":
        if not start_aspect: #== "": #here, the defaults settings are given, if there is no more specific information available
            if date_indicator == "datl" or date_indicator == "datx":
                start_aspect = "l"
            if date_indicator == "datw" or date_indicator == "datz":
                start_aspect = "a"
        if start_prefix_1 == None or start_prefix_1 == "":
            if start_aspect == "l":                    
                start_prefix_1 = "born "
            else: #can only be 'life' or 'activity'
                start_prefix_1 = "active from "
        if start_prefix_1 == "documented ":
            start_prefix_1 = "documented from "
        date_string = (start_prefix_1 + start_prefix_2 + start_day + start_month + start_year + start_suffix + start_alternative_string + only_alternative_string).strip()
        # The following lines achieve that, if the alternative dates give a larger timespan than the main dates, they are used for the search timespan
        if start_alternative_start_date:
            if start_alternative_start_date < start_start_date:
                start_start_date = start_alternative_start_date
        if start_alternative_end_date:
            if start_alternative_end_date > start_end_date:
                start_end_date = start_alternative_end_date

        date_start = start_start_date
        date_end = start_end_date
        date_aspect = start_aspect

    if date_type == "end":
        if end_aspect == "": #here, the defaults settings are given, if there is no more specific information available
            if date_indicator == "datl" or date_indicator == "datx":
                end_aspect = "l"
            if date_indicator == "datw" or date_indicator == "datz":
                end_aspect = "a"
        if end_prefix_1 == "":
            if end_aspect == "l":                    
                end_prefix_1 = "died "
            else: #can only be 'life' or 'activity'
                end_prefix_1 == "active until "
        date_string = (end_prefix_1 + end_prefix_2 + end_day + end_month + end_year + end_suffix + end_alternative_string + only_alternative_string).strip()
        if end_alternative_start_date: # This makes sure that, if the alternative dates give a greater datespan, the latter will be used for searches
            if end_alternative_start_date < end_start_date:
                end_start_date = end_alternative_start_date
        if end_alternative_end_date:
            if end_alternative_end_date > end_end_date:
                end_end_date = end_alternative_end_date

        date_start = end_start_date
        date_end = end_end_date
        date_aspect = end_aspect


    if date_type == "only":
        if only_aspect == "": #here, the defaults settings are given, if there is no more specific information available
            if date_indicator == "datl" or date_indicator == "datx":
                only_aspect = "l"
            if date_indicator == "datw" or date_indicator == "datz":
                only_aspect = "a"
        if only_prefix_1 == "":
            if only_aspect == "a":                    
                only_prefix_1 = "active "
            # if it is just a period of life, there is no prefix
        date_string = (only_prefix_1 + only_prefix_2 + only_day + only_month + only_year + only_suffix + only_alternative_string).strip()
        if only_alternative_start_date: # This makes sure that, if the alternative dates give a greater datespan, the latter will be used for searches
            if only_alternative_start_date < only_start_date:
                only_start_date = only_alternative_start_date
        if only_alternative_end_date:
            if only_alternative_end_date > only_end_date:
                only_end_date = only_alternative_end_date
        date_start = only_start_date
        date_end = only_end_date
        date_aspect = only_aspect
    # question: should one have fictive end dates for start dates only given? e.g. for life + 70, for active + 50? ditto for fictive start dates?
    return (date_string, date_start, date_end, date_aspect)




def artist_date_single_parsing(date_raw):
    """
This function is called by artist_date_parsing. It receives an element of the date (the original date statement is broken at commas and dashes into these elements)
it returns a datestring, start and end dates, the date_aspect (life or activity), the date_type (beginning or end), and if it can be used as a 'short date' (e.g., written with dash)
    """
    prefix_0_raw = ""
    prefix_1_raw = ""
    prefix_1_raw = ""
    date_prefix_0 = ""
    date_prefix_1 = ""
    date_prefix_2 = ""
    year_string_raw = ""
    year_string_raw = ""
    year_end_string_raw = ""
    year_end_value_end = 0
    year_string = ""
    year_start_string = ""
    year_end_string = ""
    year_value_start = 0
    year_value_end = 0
    BC_indicator = False
    date_aspect = ""
    date_type = ""
    short_date = True
    date_pattern = r'(active |active from | active by |master |active in |active until |documented |documented from |documented in |born |baptised |died |buried )?(ca. |approximately |before |by |after )?(early |early to mid |late |mid |mid to late |first half of the |second half of the |first quarter of the |second quarter of the |third quarter of the |fourth quarter of the |last quarter of the )?(\d{1,4})(st|nd|rd|th)?(/| or )?(\d{,4})?(st|nd|rd|th)?( bc)?(.*)?'
    try:
        date_single_parsed = re.match(date_pattern, date_raw).groups()
    except AttributeError:
        return(("", 0, 0, "", "", False))
    prefix_0_raw = date_single_parsed[0]        
    prefix_1_raw = date_single_parsed[1] 
    prefix_2_raw = date_single_parsed[2]
    year_string_raw = date_single_parsed[3]
    centuries_ordinal_raw = date_single_parsed[4]
    figures_combination_raw = date_single_parsed[5]
    year_end_string_raw = date_single_parsed[6]
    centuries_end_ordinal_raw = date_single_parsed[7]
    bc_string_raw = date_single_parsed[8]
        
    if bc_string_raw == " bc":
        BC_indicator = True
    if centuries_ordinal_raw:
        if figures_combination_raw: # if there is something like "15th or 16th century, the word 'century is not repeated"
            year_start_string = year_string_raw + centuries_ordinal_raw 
        else:
            year_start_string = year_string_raw + centuries_ordinal_raw + " century"
        if not BC_indicator:
            year_start_value_start = (int(year_string_raw)-1) * 100 + 1
            year_start_value_end = int(year_string_raw) * 100
        else: 
            year_start_value_start = -int(year_string_raw) * 100
            year_start_value_end = -(int(year_string_raw)-1) * 100 -1
    else:
        year_start_string = year_string_raw
        if not BC_indicator:
            year_start_value_start = int(year_string_raw)
            year_start_value_end = int(year_string_raw)
        else: 
            year_start_value_start = -int(year_string_raw)
            year_start_value_end = -int(year_string_raw)
            

    if year_end_string_raw:
        if centuries_end_ordinal_raw: # if it is a century
            year_end_string = year_end_string_raw + centuries_end_ordinal_raw + " century"
            if not BC_indicator:
                year_end_value_start = (int(year_end_string_raw)-1) * 100 + 1
                year_end_value_end = int(year_end_string_raw) * 100
            else: 
                year_end_value_start = -int(year_end_string_raw) * 100
                year_end_value_end = -(int(year_end_string_raw)-1) * 100 -1
        elif len(year_start_string) > 2 and len(year_end_string_raw) == 1:
            year_end_string = year_start_string[:-1] + year_end_string_raw
            year_end_value_start = int(year_end_string)
            year_end_value_end = int(year_end_string)
        elif len(year_start_string) > 2 and len(year_end_string_raw) == 2:
            year_end_string = year_start_string[:-2] + year_end_string_raw
            year_end_value_start = int(year_end_string)
            year_end_value_end = int(year_end_string)
        else: 
            year_end_string = year_end_string_raw
            if not BC_indicator:
                year_end_value_start = int(year_end_string_raw)
                year_end_value_end = int(year_end_string_raw)
            else: 
                year_end_value_start = -int(year_end_string_raw)
                year_end_value_end = -int(year_end_string_raw)

        
    if figures_combination_raw and year_end_string:
        short_date = False
        if figures_combination_raw == "/":
            year_string = "between " + year_start_string + " and " + year_end_string
        elif figures_combination_raw == " or ":
            if year_start_value_start > year_end_value_start: # to put them into correct order
                year_provisional_start = year_start_value_start
                year_provisional_end = year_start_value_end
                year_start_value_start = year_end_value_start
                year_start_value_end = year_end_value_end
                year_end_value_start = year_provisional_start
                year_end_value_end = year_provisional_end                
                year_string = year_end_string + " or " + year_start_string
            else:
                year_string = year_start_string + " or " + year_end_string
        year_value_start = year_start_value_start
        year_value_end = year_end_value_end
    else: 

        year_string = year_start_string
        year_value_start = year_start_value_start
        year_value_end = year_start_value_end

    if BC_indicator:
        year_string = year_string + " BC"
        
            
    if prefix_0_raw:
        prefix_0_raw = prefix_0_raw.strip()
        match prefix_0_raw:
            case "born":
                date_aspect = "l"
                date_type = "start"
            case  "baptised":
                date_prefix_0 = "baptised "
                date_aspect = "l"
                date_type = "start"
                short_date = False
            case "active"|"active in":
                date_aspect = "a"
            case "active from":
                date_aspect = "a"
                date_type = "start"
                short_date = False
            case "master":
                date_prefix_0 = "master "
                date_aspect = "a"
                date_type = "start"
                short_date = False
            case "active by":
                date_prefix_0 = "active by"
                date_aspect = "a"
                date_type = "start"
                short_date = False
            case "active until":
                date_aspect = "a"
                date_type = "end"
                short_date = False
            case "documented"|"documented in":
                date_prefix_0 = "documented "
                date_aspect = "a"
            case "documented from":
                date_prefix_0 = "documented from "
                date_aspect = "a"
                date_type = "start"
            case "died":
                date_aspect = "l"
                date_type = "end"
            case "buried":
                date_prefix_1 = "buried "
                date_aspect = "l"
                date_type = "end"
                short_date = False
    if prefix_1_raw:
        prefix_1_raw = prefix_1_raw.strip()
        match prefix_1_raw:
            case "ca."|"approximately":
                date_prefix_1 = "c. "
                year_value_start = year_value_start - 5
                year_value_end = year_value_end + 5
            case "before":
                date_prefix_1 = "before "
                year_value_start = year_value_start - 10
            case "by":
                date_prefix_1 = "by " # I don't have this in date_parsing
                year_value_end = year_value_start
                year_value_start = year_value_start - 10
            case "after":
                date_prefix_1 = "after "
                year_value_end = year_value_end + 10  
    
    
    
    if prefix_2_raw:
        prefix_2_raw = prefix_2_raw.strip()
        match prefix_2_raw: # under these conditions, year_end_value_start and year_end_value_end are never in use
            case "first half of the": 
                date_prefix_2 = "first half "
                year_value_end = year_value_end -50
            case "second half of the":
                date_prefix_2 = "second half "
                year_value_start = year_value_start +50
            case "first quarter of the":
                date_prefix_2 = "first quarter "
                year_value_end = year_value_start + 24
            case "second quarter of the":
                date_prefix_2 = "second quarter "
                year_value_start = year_value_start +25
                year_value_end = year_value_start + 24
            case "third quarter of the":
                date_prefix_2 = "third quarter "
                year_value_start = year_value_start +50
                year_value_end = year_value_start + 24
            case "fourth quarter of the":
                date_prefix_2 = "last quarter "
                year_value_start = year_value_start +75
            case "early":
                date_prefix_2 = "early "
                if BC_indicator == False:
                    year_value_end = year_value_start + 19
                else:
                    year_value_end = year_value_start +20
            case "mid":
                date_prefix_2 ="Mid-"
                if BC_indicator == False:
                    year_value_start = year_value_start + 39
                    year_value_end = year_value_start + 20
                else: 
                    year_value_start = year_value_start + 39
                    year_value_end = year_value_start + 20
            case "late":
                date_prefix_2 = "late "
                year_value_start = year_value_start + 80 
            case "early to mid":
                date_prefix_2 = "early to Mid-"
                year_value_end = year_value_end - 40 # should mean, from e.g. 1900-1960
            case "mid to late":
                date_prefix_2 = "Mid- to late "
                year_value_start = year_value_start + 40 # should mean, from e.g. 1900-1960

            case _:
                pass
    else:
        pass             
    
    date_string = date_prefix_0 + date_prefix_1 + date_prefix_2 + year_string 

    return(date_string, year_value_start, year_value_end, date_type, date_aspect, short_date)
    
def artist_date_parsing(date_from_source):
    """
This programme takes the date from source from ULAN (i.e., the short biography text, with all sections between commas that contain no figures cut out)
It returns a date string, start and end dates (only years, since Getty ULAN normally only gives yers, and the aspect - if date of life or of activity)
    """
    date_from_source_divided = []
    date_single_start = []
    date_single_end = []
    date_processed = ()
    dates_processed_list = []
    start_aspect = ""
    end_aspect = ""
    single_aspect = ""
    date_aspect = ""
    datestring = ""
    date_replacement = {"–" : "-", "c." : "", ";" : ",", "st c " : "st ", "nd c " : "nd ", "rd c " : "rd ", "th c ": "th ", "centuries" : "", "cs." : "", "century" : "", "b.c." : "bc", "bce" : "bc", "cent." : "", "b." : "born ", "d.": "died ", \
                        "act." : "active", "act " : "active ", "acitve" : "active", "1st half" : "first half", "2nd half" : "second half", "last half" : "second half", "1st quarter" : "first quarter", "2nd quarter" : "second quarter", "3rd quarter" : "third quarter", "4th quarter" : "fourth quarter", "mid-late" : "mid to late", "mid-" : "mid ", "th to mid" : "th - mid",\
                        "fl. -" : "-active ", "fl." : "active", "flourished" : "active", "fl " : "active ", "active in the" : "active", "active to" : "active until", "active since" : "active from", "active beginning" : "active from", "-p." : "-after ", "aft." : "after", "-a." : "-before", "bef." : "before ", "(?)" : "?", "op." : "active ",\
                            "baptized" : "baptised", "baptised in" : "baptised", "sculptor" : "sculptor,", "painter" : "painter,", "artist" : "artist,", "printmaker" : "printmaker,", "miniaturist" : "miniaturist,", "illustrator" : "illustrator,", "illuminator" : "illuminator," , "architect" : "architect,", "draftsman" : "draftsman,", "medalist" : "medalist," , "etcher" : "etcher," , "clockmaker" : "clockmaker,", "united states" : "",
                        "half " : "half of the ", "quarter " : "quarter of the ", "of the of the" : "of the", "of the of" : "of the", "   " : " ", "  " : " ", " in 1" : " 1",\
                        "probably active" : "active ca.", "probably died" : "died ca.", "possibly active" : "active ca.", "possibly born" : "born ca.", "probably born" : "born ca.", "probably" : "ca.", "before ca." : "before", "possibly died" : "died ca.", "possibly" : "ca.",\
                        "in the early" : "early", "in the late" : "late", "in the mid" : "mid", "early-to mid" : "early to mid", "early-mid" : "early to mid", "ca. after" : "after", "born in the " : "born ", "born in 1" : "born 1", "died in" : "died", "active after" : "active from", "active from ca." : "active from", "after ca." : "after", \
                            "ca " : "ca. ", "between " : "", " and " : "/"}
    date_from_source = date_from_source.lower()
    for old, new in date_replacement.items():
        date_from_source = date_from_source.replace(old, new)
        
    if "," in date_from_source:
        date_from_source_divided = date_from_source.split(",")
    else:
        date_from_source_divided.append(date_from_source)
    activity_place_pattern = r'(active in )([a-z].*? )(.*)'
    birth_place_pattern = r'(born in )([a-z].*? )(.*)'
    documented_place_pattern = r'(documented in )([a-z].*? )(.*)'
    for date_raw in date_from_source_divided:
        date_raw = date_raw.strip()
        if re.match(activity_place_pattern, date_raw): # taking out place-names in phrases like "active in Rome 1500" (works only if the place name consists of one word)
            date_raw = "active " + re.match(activity_place_pattern, date_raw).groups()[2]
        elif re.match(birth_place_pattern, date_raw):
            date_raw = "born " + re.match(birth_place_pattern, date_raw).groups()[2]
        elif re.match(documented_place_pattern, date_raw):
            date_raw = "documented " + re.match(documented_place_pattern, date_raw).groups()[2]
   
        if "-" in date_raw:
            date_raw_pattern = r'([^-]*)?(-)(.*)?'
            try:
                date_raw_divided = re.match(date_raw_pattern, date_raw).groups()
            except AttributeError:
                return(("xxx", 0, 0, ""))
            if date_raw_divided[0] and date_raw_divided[0] != "xxx":
                date_single_start = artist_date_single_parsing(date_raw_divided[0].strip())
                start_datestring = date_single_start[0]
                start_start = date_single_start[1]
                start_end = date_single_start[2]
                start_type = date_single_start[3]
                start_aspect = date_single_start[4]
                start_short = date_single_start[5]
            if date_raw_divided[2] and date_raw_divided[2] != "xxx":
                date_single_end = artist_date_single_parsing(date_raw_divided[2].strip())
                end_datestring = date_single_end[0]
                end_start = date_single_end[1]
                end_end = date_single_end[2]
                end_type = date_single_end[3]
                end_aspect = date_single_end[4]
                end_short = date_single_end[5]

            if date_single_start and not date_single_end:
                if start_aspect == "a" and "documented" not in start_datestring:
                    date_aspect = "a"
                    datestring = "active from " + start_datestring
                    date_start = start_start
                    date_end = start_end
                else:
                    date_aspect = "l" # everything is dates of life, unless defined otherwise
                    datestring = "born " + start_datestring
                    date_start = start_start
                    date_end = start_end
            elif date_single_end and not date_single_start:

                if end_aspect == "a":
                    date_aspect = "a"
                    datestring = "active until " + end_datestring
                    date_end = end_end

                    date_start = end_start
                else:
                    date_aspect = "l" # everything is dates of life, unless defined otherwise
                    datestring = "died " + end_datestring
                    date_end = end_end
                    date_start = end_start
            elif date_single_start and date_single_end:
                date_start = start_start
                date_end = end_end
                if date_end < 0 and date_start > 0:
                    date_start = 0 - date_start
                if start_short and end_short:
                    if start_aspect == "a" and end_aspect != "l":
                        date_aspect = "a"
                        if "documented" not in start_datestring and "master" not in start_datestring:
                            datestring = "active " + start_datestring + " - " + end_datestring
                        else: 
                            datestring = start_datestring + " - " + end_datestring

                    elif start_aspect != "a" and end_aspect != "a":
                        datestring = start_datestring + " - " + end_datestring
                        date_aspect = "l"
                    elif start_aspect == "a" and end_aspect == "l": # I am not sure if this will ever happen
                        date_aspect = "a"
                        if start_type == "start" and "documented" not in start_datestring and "master" not in start_datestring:
                            start_datestring = "active from " + start_datestring
                        elif start_type != "start" and "documented" not in start_datestring:
                            start_datestring = "active "
                        end_datestring = "died " + end_datestring
                        datestring = start_datestring + ", " + end_datestring
                    elif start_aspect == "l" and end_aspect == "a": # I am not sure if this will ever happen
                        date_aspect = "l"
                        if "bapti" not in start_datestring:
                            start_datestring = "born " + start_datestring
                        if end_type == "end" and "documented" not in end_datestring:
                            end_datestring = "active until " + end_datestring
                        if end_type != "end" and "documented" not in datestring:
                            end_datestring = "active " + end_datestring
                        datestring = start_datestring + ", " + end_datestring

                else:
                    if start_aspect == "a" and start_type == "start" and "documented" not in start_datestring and "master" not in start_datestring:
                        start_datestring = "active from " + start_datestring
                    if start_aspect != "a" and start_type == "start" and "bapti" not in start_datestring:
                        start_datestring = "born " + start_datestring
                    if end_aspect == "a" and end_type == "end" and "documented" not in end_datestring and "master" not in end_datestring:
                        end_datestring = "active until " + end_datestring
                    if end_aspect != "a" and end_type == "end" and "buried" not in end_datestring:
                        end_datestring = "died " + end_datestring
                    datestring = start_datestring + ", " + end_datestring
                    date_start = start_start
                    date_end = end_end
            else: # no usable date            
                datestring = "xxx"
                date_start = 0
                date_end = 0
                date_aspect = "l"
            
        else:
            date_single = artist_date_single_parsing(date_raw)
            if date_single[0] != "xxx": # that is invalid date
                single_datestring = date_single[0]
                single_start = date_single[1]
                single_end = date_single[2]
                single_type = date_single[3]
                single_aspect = date_single[4]

            if single_aspect == "a":
                date_aspect = "a"
                if single_type == "start" :
                    if "master" not in single_datestring and "documented" not in single_datestring:
                        datestring = "active from " + single_datestring
                    else: 
                        datestring = single_datestring
                    date_start = single_start
                    date_end = single_end + 50 # fictive dates if only start/end are given. They are not yet included in the GND dates parser                    
                elif single_type == "end":
                    if "master" not in single_datestring and "documented" not in single_datestring:
                        datestring = "active until " + single_datestring
                    else: 
                        datestring = single_datestring
                    date_start = single_start-50 # fictive dates if only start/end are given. They are not yet included in the GND dates parser
                    date_end = single_end  
                else:
                    if "master" not in single_datestring and "documented" not in single_datestring:
                        datestring = "active " + single_datestring
                    else: 
                        datestring = single_datestring
                    date_start = single_start
                    date_end = single_end
            else:
                date_aspect = "l" # everything is dates of life, unless defined otherwise
                if single_type == "start" and "bapti" not in single_datestring:
                    datestring = "born " + single_datestring
                    date_start = single_start
                    date_end = single_end
                elif single_type == "end" and "buried" not in single_datestring:
                    datestring = "died " + single_datestring
                    date_start = single_start
                    date_end = single_end  
                else:
                    datestring = single_datestring
                    date_start = single_start
                    date_end = single_end
        date_processed = (datestring, date_start, date_end, date_aspect)
        dates_processed_list.append(date_processed)
        if len(dates_processed_list) == 2: # is either 1 or 2
            if dates_processed_list[0][1] < dates_processed_list[1][1]:
                datestring = dates_processed_list[0][0] + ", " + dates_processed_list[1][0]
                date_start = dates_processed_list[0][1]
                if dates_processed_list[1][2] > dates_processed_list[0][2]:
                    date_end = dates_processed_list[1][2]
                else:
                    date_end = dates_processed_list[0][2]
                date_aspect = dates_processed_list[0][3]
            elif dates_processed_list[0][1] > dates_processed_list[1][1]:
                datestring = dates_processed_list[1][0] + ", " + dates_processed_list[0][0]
                date_start = dates_processed_list[1][1]
                if dates_processed_list[1][2] > dates_processed_list[0][2]:
                    date_end = dates_processed_list[1][2]
                else:
                    date_end = dates_processed_list[0][2]

                date_aspect = dates_processed_list[1][3]
            date_processed = (datestring, date_start, date_end, date_aspect)
        else:
            if date_start == date_end: # I do not yet have anything like that in the GND parsing sequence
                if "born" in datestring or "bapti" in datestring:
                    date_end = date_start + 70
                elif "active from" in datestring or "active by" in datestring:                                           
                    date_end = date_start + 50
                elif "died" in datestring or "buried" in datestring:                                           
                    date_start = date_start - 70
                elif "active until" in datestring:
                    date_start = date_start - 50
            date_processed = (datestring, date_start, date_end, date_aspect)
    return date_processed


def entered_single_date(date_raw, position):
    """
This module is one of two modules for the manual entering of dates. entered_date divides the term in up to four units.  
It then hands to this module a single unit and its position. 
This module returns a datestring, start and end dates as tuples, as well as indicators if it is the date of activity or the date of death
    """
    prefix, suffix_1, suffix_2 = "", "", ""
    date_single_active = False
    date_single_died = False
    century = False
    date_ready = ""
    date_raw = date_raw.replace("-a", "a-") # This block normalises some possible variants in entering dates
    date_raw = date_raw.replace("-d", "d-")
    date_raw = date_raw.replace(".", ",")
    date_raw = date_raw.replace("/", ",")
    date_single_pattern = r'(a|d)?(-)?(\d{1,4})(,\d{0,2})?(,\d{0,2})?([abcemlt]|na|nb|h[12]|q[1-4])?$'
    date_single_divided = re.match(date_single_pattern, date_raw)
    if not date_single_divided:
        raise classes.InvalidDateException(f"Invalid date {date_raw}")
    date_single_groups = date_single_divided.groups()

    month_string = ""
    month_name = ""
    day_string = ""
    year_start = 1 
    year_end = 1
    month_start = 1
    month_end = 12
    day_start = 1
    day_end = 31
#    month_indicated = False
 #   day_indicated = False
    month_list = {1: ' Jan ', 2:' Feb ', 3:' Mar ', 4:' Apr ', 5:' May ', 6:' Jun ', 7:' Jul ', 8:' Aug ', 9:' Sep ', 10:' Oct ', 11:' Nov ', 12:' Dec '}
        
    year_string = date_single_groups[2].strip()
    year_number = int(year_string)
    year_start = year_number # This is the default, it will be modified in many options later
    year_end = year_number

    if date_single_groups[0]:
        match date_single_groups[0].strip():
            case "a" if position == 0: #'active' only makes sense with the first item
                date_single_active = True   # In Iconobase, this information would be needed for calculating dates of works of art. 
            case "d":
                date_single_died = True
        
    if date_single_groups[1] == "-":
        suffix_2 = " BC"
        year_start = 0-year_start
        year_end = 0-year_end
    else:
        suffix_2 = " AD"
        


    if date_single_groups[3]:
        month_comma = date_single_groups[3].strip()
        month_string = month_comma[1:].strip()
        month_number = int(month_string)
        month_start = month_number
        month_end = month_number
        if month_number < 13:
            month_name = month_list[month_number]
        else: 
            raise classes.InvalidMonthException(f"{str(position+1)}: Invalid number of month {month_number}")
        month_indicated = True

    if date_single_groups[4]:
        day_comma = date_single_groups[4].strip()
        day_string = day_comma[1:].strip()
        day_number = int(day_string)
        day_start = day_number
        day_end = day_number
        day_indicated = True

    if date_single_groups[5]:
        match date_single_groups[5]:
            case "na":
                prefix = "not after "
                year_start = year_number - 5
            case "nb":
                prefix = "not before "
                year_end = year_number + 5
            case "h1":
                prefix = "first half "
                century = True
                if suffix_2 == " AD":
                    year_start = (year_number-1)*100+1
                    year_end = (year_number-1)*100+50
                elif suffix_2 == " BC":
                    year_start = 0-(year_number*100)
                    year_end = 0-((year_number-1)*100+51)
            case "h2":
                prefix = "second half "
                century = True
                if suffix_2 == " AD":
                    year_start = (year_number-1)*100+51
                    year_end = (year_number)*100
                elif suffix_2 == " BC":
                    year_start = 0-((year_number-1)*100+50)
                    year_end = 0-((year_number-1)*100+1)
            case "q1": 
                prefix = "first quarter "
                century = True
                if suffix_2 == " AD":                    
                    year_start = (year_number-1)*100+1
                    year_end = (year_number-1)*100+25
                elif suffix_2 == " BC":
                    year_start = 0-(year_number*100)
                    year_end = 0-((year_number-1)*100+76)
            case "q2":
                prefix = "second quarter "
                century = True
                if suffix_2 == " AD":
                    year_start = (year_number-1)*100+26
                    year_end = (year_number-1)*100+50
                elif suffix_2 == " BC":
                    year_start = 0-((year_number-1)*100+75)
                    year_end = 0-((year_number-1)*100+51)
            case "q3":
                prefix = "third quarter "
                century = True
                if suffix_2 == " AD":
                    year_start = (year_number-1)*100+51
                    year_end = (year_number-1)*100+75
                elif suffix_2 == " BC":
                    year_start = 0-((year_number-1)*100+50)
                    year_end = 0-((year_number-1)*100+26)
            case "q4": 
                prefix = "fourth quarter "
                century = True
                if suffix_2 == " AD":
                    year_start = (year_number-1)*100+76
                    year_end = (year_number)*100
                elif suffix_2 == " BC":
                    year_start = 0-((year_number-1)*100+25)
                    year_end = 0-((year_number-1)*100+1)
            case "a":
                prefix = "after "
                year_start = year_number
                year_end = year_number + 5
            case "b": 
                prefix = "before "
                year_start = year_number - 5
                year_end = year_number
            case "c":
                prefix = "circa "
                year_start = year_number - 5
                year_end = year_number + 5
            case "e":
                prefix = "early "
                century = True
                if suffix_2 == " AD":                    
                    year_start = (year_number-1) * 100 + 1
                    year_end = (year_number-1) * 100 + 20
                elif suffix_2 == " BC":
                    year_start = year_number * 100
                    year_end = (year_number-1) * 100 + 80
            case "l": 
                prefix = "late "
                century = True
                if suffix_2 == " AD":
                    year_start = (year_number-1)*100+80
                    year_end = year_number * 100
                    print("in case l")
                    print(year_start) # zum Probien
                if suffix_2 == " BC":
                    year_start = 0-((year_number-1) * 100 + 20)
                    year_end = 0-((year_number-1) * 100 + 1)
            case "m": 
                prefix = "Mid-"
                century = True
                if suffix_2 == " AD":
                    year_start = (year_number-1) * 100 + 41
                    year_end = (year_number-1) * 100 + 60
                if suffix_2 == " BC":
                    year_start = 0-((year_number-1) * 100 + 60 )                  
                    year_end = 0-((year_number-1) * 100 + 41)
            case "t":
                prefix = "" # for the 'naked' century
                century = True
                if suffix_2 == " AD":
                    year_start = (year_number-1)*100+1
                    year_end= (year_number)*100
                if suffix_2 == " BC":
                    year_start = 0-(year_number * 100)
                    year_end = 0-((year_number-1) * 100 + 1)

    if century: # adds the right ordinal number + 'century' after indications of centuries
        if year_number <= 100:
            if year_number % 10 == 1 and year_number != 11:
                suffix_1 = "st century"
            elif year_number % 10 == 2 and year_number != 12:
                suffix_1 = "nd century"
            elif year_number % 10 == 3 and year_number != 13:
                suffix_1 = "rd century"
            else:
                suffix_1 = "th century"

        
    date_ready = prefix + year_string + month_name + day_string + suffix_1 + suffix_2

    if (month_start == 4 or month_start == 6 or month_start == 9 or month_start == 11) and day_start > 30: # makes sure that no error occurs if a month but no day is given
        raise classes.InvalidDayException(f"{str(position+1)}: Invalid number of day: {day_start}")
    if day_start > 31:
        raise classes.InvalidDayException(f"{str(position+1)}: Invalid number of day: {day_start}")
    if month_end == (4 or 6 or 9 or 11) and day_end > 30: 
        raise classes.InvalidDayException(f"{str(position+1)}: Invalid number of day: {day_end}")
    if month_start == 2 and day_start > 29:
        raise classes.InvalidDayException(f"{str(position+1)}: Invalid number of day: {day_start}")
    if month_end == 2 and day_end > 29:
        raise classes.InvalidDayException(f"{str(position+1)}: Invalid number of day: {day_end}")

    if date_single_died: # This is only relevant if the year of death is the only thing indicated, otherwise it will be overwritten. 
        daterange_start = (year_start-30, month_start, day_start)
    else: 
        daterange_start = (year_start, month_start, day_start)
    daterange_end = (year_end, month_end, day_end)
    return date_ready, date_single_active, date_single_died, daterange_start, daterange_end


def parse_manually_entered_date(date_entered):
    """
This module receis a date-string entered manually and (hopefully) following a certain set of rules. 
It divides the string into up to four parts, sends them to entered_single_date, and receives the parsed results back
It return a datestring and tuples expressing the start and end dates. 
    """
    #In the first step, I divide the string into a number of dates
    #Maximum = 4 (meaning 'born between 1405 and 1406, died between 1450 and 1455)
    date_complete_pattern =  r'(.{0,2}\d[^-:]*)-?(.{0,2}\d[^-:]*)?(?:\:(.{0,2}\d[^-:]*)?-?(.{0,2}\d[^-:]*)?)?$'
    date_analysed = re.match(date_complete_pattern, date_entered)
    if not date_analysed:
        raise classes.InvalidDateStringException(f"{date_entered}")
    date_divided = date_analysed.groups()
    if date_divided[0]:
        date_0 = date_divided[0]
        date_result_0  = entered_single_date(date_0, 0)
        date_formatted_0, date_active_0, date_died_0, date_start_0, date_end_0 = date_result_0
    if date_divided[1]:
        date_1 = date_divided[1]
        date_result_1 = entered_single_date(date_1, 1)
        date_formatted_1, date_active_1, date_died_1, date_start_1, date_end_1 = date_result_1
    else:
        date_formatted_1 = ""
    if date_divided[2]:
        date_2 = date_divided[2]
        date_result_2 = entered_single_date(date_2, 2)
        date_formatted_2, date_active_2, date_died_2, date_start_2, date_end_2 = date_result_2
    else:
        date_formatted_2 = ""
    if date_divided[3]:
        date_3 = date_divided[3]
        date_result_3 =  entered_single_date(date_3, 3)
        date_formatted_3, date_active_3, date_died_3, date_start_3, date_end_3 = date_result_3
    else:
        date_formatted_3 = ""

    if date_formatted_0 and not date_formatted_1 and not date_formatted_2 and not date_formatted_3:       
        if date_formatted_0[-3:] == " AD": # a single date is deemed to be AD, no need to indicate it
            date_formatted_0 = date_formatted_0[:-3]
        if date_active_0:
            date_complete = "active " + date_formatted_0
        elif date_died_0:
            date_complete = "died " + date_formatted_0             
        else: 
            date_complete = date_formatted_0
        daterange_complete_start = date_start_0
        daterange_complete_end = date_end_0
    if date_formatted_0 and date_formatted_1 and not date_formatted_2 and not date_formatted_3:
        if date_formatted_0[-3:] == " AD": # if the start date is AD, all dates must be AD, and there is no reason to indicate it. 
            date_formatted_0 = date_formatted_0[:-3]            
            date_formatted_1 = date_formatted_1[:-3]            
        if date_active_0 and date_died_1:
            date_complete = "active " + date_formatted_0 + ", died " + date_formatted_1
        else:
            if date_formatted_1[-3:] == " BC":
                date_formatted_0 = date_formatted_0[:-3]
            date_complete = date_formatted_0 + "-" + date_formatted_1
        daterange_complete_start = date_start_0
        daterange_complete_end = date_end_1
    if date_formatted_0 and not date_formatted_1 and date_formatted_2 and not date_formatted_3:
        if date_formatted_0[-3:] == " AD": # if the start date is AD, all dates must be AD, and there is no reason to indicate it. 
            date_formatted_0 = date_formatted_0[:-3]            
            date_formatted_2 = date_formatted_2[:-3]                        
        if date_active_0 and date_died_2:
            date_complete = "active " + date_formatted_0 + ", died" + date_formatted_2
        else:
            date_complete = date_formatted_0 + "-" + date_formatted_2
        daterange_complete_start = date_start_0
        daterange_complete_end = date_end_2
    if date_formatted_0 and date_formatted_1 and date_formatted_2 and not date_formatted_3:
        if date_formatted_0[-3:] == " AD": # if the start date is AD, all dates must be AD, and there is no reason to indicate it. 
            date_formatted_0 = date_formatted_0[:-3]            
            date_formatted_1 = date_formatted_1[:-3]  
            date_formatted_2 = date_formatted_2[:-3]                        
        if date_active_0:
            if date_died_2:
                date_complete = "active from" + date_formatted_0 + "-" + date_formatted_1 + ", died " + date_formatted_2
            else:
                date_complete = "active from" + date_formatted_0 + "-" + date_formatted_1 + " until " + date_formatted_2
        else: 
            date_complete = "born " + date_formatted_0 + "-" + date_formatted_1 + ", died " + date_formatted_2
        daterange_complete_start = date_start_0
        daterange_complete_end = date_end_2
    if date_formatted_0 and not date_formatted_1 and date_formatted_2 and date_formatted_3:
        if date_formatted_0[-3:] == " AD": # if the start date is AD, all dates must be AD, and there is no reason to indicate it. 
            date_formatted_0 = date_formatted_0[:-3]            
            date_formatted_2 = date_formatted_2[:-3]  
            date_formatted_3 = date_formatted_3[:-3]                        
        if date_active_0:
            if date_died_2:
                date_complete = "active from" + date_formatted_0 + ", died " + date_formatted_2 + "-" + date_formatted_3
            else:
                date_complete = "active from" + date_formatted_0 + " until " + date_formatted_2 + "-" + date_formatted_3
        else: 
            date_complete = "born " + date_formatted_0 + ", died " + date_formatted_2 + "-" + date_formatted_3
        daterange_complete_start = date_start_0
        daterange_complete_end = date_end_3
    if date_formatted_0 and date_formatted_1 and date_formatted_2 and date_formatted_3:    
        if date_formatted_0[-3:] == " AD": # if the start date is AD, all dates must be AD, and there is no reason to indicate it. 
            date_formatted_0 = date_formatted_0[:-3]            
            date_formatted_1 = date_formatted_1[:-3]  
            date_formatted_2 = date_formatted_2[:-3]                        
            date_formatted_3 = date_formatted_3[:-3]                        
        if date_active_0:
            if date_died_2:
                date_complete = "active from " + date_0 + "-" + date_1 + ", died " + date_2 + "-" + date_3
            else: 
                date_complete = "active from " + date_0 + "-" + date_1 + " until " + date_2 + "-" + date_3
        else:
            date_complete = "born " + date_0 + "-" + date_1 + ", died " + date_2 + "-" + date_3
        daterange_complete_start = date_start_0
        daterange_complete_end = date_end_3

    if daterange_complete_start > daterange_complete_end:
        raise classes.InvalidDateRangeException(f"start date: {daterange_complete_start} later than end date: {daterange_complete_end}")

    date_new =classes.DateImport()
    date_new.datestring_raw = date_entered
    date_new.datestring = date_complete
    date_new.date_start = daterange_complete_start
    date_new.date_end = daterange_complete_end
    print(date_new)
    return date_new
