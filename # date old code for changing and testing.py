import re
from classes import *

class InvalidDateException(Exception):
    pass

class InvalidMonthException(Exception):
    pass

class InvalidDayException(Exception):
    pass

class InvalidDateStringException(Exception):
    pass

class InvalidDateRangeException(Exception):
    pass

def entered_single_date(date_raw, position):
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
        raise InvalidDateException(f"Invalid date {date_raw}")
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
    month_indicated = False
    day_indicated = False
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
            raise InvalidMonthException(f"{str(position+1)}: Invalid number of month {month_number}")
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
        raise InvalidDayException(f"{str(position+1)}: Invalid number of day: {day_start}")
    if day_start > 31:
        raise InvalidDayException(f"{str(position+1)}: Invalid number of day: {day_start}")
    if month_end == (4 or 6 or 9 or 11) and day_end > 30: 
        raise InvalidDayException(f"{str(position+1)}: Invalid number of day: {day_end}")
    if month_start == 2 and day_start > 29:
        raise InvalidDayException(f"{str(position+1)}: Invalid number of day: {day_start}")
    if month_end == 2 and day_end > 29:
        raise InvalidDayException(f"{str(position+1)}: Invalid number of day: {day_end}")

    if date_single_died: # This is only relevant if the year of death is the only thing indicated, otherwise it will be overwritten. 
        daterange_start = (year_start-30, month_start, day_start)
    else: 
        daterange_start = (year_start, month_start, day_start)
    daterange_end = (year_end, month_end, day_end)
    return date_ready, date_single_active, date_single_died, daterange_start, daterange_end


def parse_date_string(date_entered):
    #In the first step, I divide the string into a number of dates
    #Maximum = 4 (meaning 'born between 1405 and 1406, died between 1450 and 1455)
    date_complete_pattern =  r'(.{0,2}\d[^-:]*)-?(.{0,2}\d[^-:]*)?(?:\:(.{0,2}\d[^-:]*)?-?(.{0,2}\d[^-:]*)?)?$'
    date_analysed = re.match(date_complete_pattern, date_entered)
    if not date_analysed:
        raise InvalidDateStringException(f"{date_entered}")
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
            raise InvalidDateRangeException(f"start date: {daterange_complete_start} later than end date: {daterange_complete_end}")

    date_new = Date()
    date_new.date_string = date_complete
    date_new.date_start = daterange_complete_start
    date_new.date_end = daterange_complete_end
    print(date_new)
    return date_new


def main():
    date_0 = ""
    date_1 = ""
    date_2 = ""
    date_3 = ""
    date_entered = "x"

    print("""This programme transforms a date entered in an abbreviated Form both into a form for display and a start and end date
    for searches. Please follow these conventions: 
        - for dates BC put a minus in front of the year
        - months and days are appended to year and separated by dots, commas, or slashes
        - an 'a' at the beginning means 'active', a following death date can be marked by a 'd' (to be used for dates of artists)
        - abbreviations after the year can mean 'c'(irca), 'b'(efore), 'a'(fter) as well as 'nb' (not before) or 'na' (not after)
        -for centuries only give the number of the century followed by a 't', 
            or by the letters 'e'(arly), 'm'(id) or 'l'(ate)
            or by indications of parts, e.g. "h1" for first half, or "q3" for third quarter.
        - You can give up to four dates (e.g. for "born between A and B, died between C and D", 
            in this case please mark the main distinction with a colon, the minor ones with a dash)
        - To stop, press return
        The result shows first the display form of the date, and then the start and the end of the range in ISO format
        as well as an indication if they are BC or AD - which is not expressed by the standard date format""")

    while date_entered != "":
        date_entered = input("Enter Date: ")         
        date_entered.strip()
        if date_entered == "":
            break

        print("starting parse_date_string")
        date_new = parse_date_string(date_entered)
        print(date_new)

if __name__ == '__main__':
    main()
