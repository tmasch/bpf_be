#pylint: disable=C0114,C0304,C0116
import re
import classes


@classes.func_logger
def parse_date(ds):
#    print(ds)
    messages=["date parsing"]
    state = "FAIL"
    d=classes.Dt()
    day = ""
    month = ""
    year = ""

    messages.append(ds)


#if "zwischen " in datestring_raw:  # turns "zwischen _X and _X" into "_X/_X"
#    ds = ds.replace("zwischen", "")
#    ds = ds.replace("und", "/")
#    ds = ds.replace("u.", "/")

#    print(ds)
    # case there is nothing
    if len(ds) == 0:
        messages.append("No input")
        state="SUCCESS"

    ds=remove_tags(ds)
    ds=ds.replace(" ","")
    ds=ds.replace("()","")
#    print("parse_date input:")
#    print(ds)

    if re.match(r"\?", ds) and len(ds) == 1:
        state="SUCCESS"
        messages.append("No date known")

    if len(ds) == 1:
        state="SUCCESS"
        messages.append("No valid input")

    if len(ds) == 2:
        state="SUCCESS"
        messages.append("No valid input")

    if ds == "99xx-":
        state="SUCCESS"
        messages.append("No valid input")

    # Date is four-digit year, e.g. 1234
    if len(ds) == 3 and re.match(r"\d{3}",ds):
        year="0"+ds
        messages.append('Success')
        messages.append('Only year')
        state="SUCCESS"



    # Date is DD.MM.YYYY
    if re.match(r"\d{2}\.\d{2}\.\d{4}", ds) and len(ds) == 10:
        t=ds.split(".")
        day=t[0]
        month=t[1]
        year=t[2]
        messages.append('Success')
        messages.append('Date in DD.MM.YYYY format')
        state="SUCCESS"

    # Date is ??.MM.YYYY
    if re.match(r"\?\?\.\d{2}\.\d{4}", ds) and len(ds) == 10:
        t=ds.split(".")
        day=""
        month=t[1]
        year=t[2]
        messages.append('Success')
        messages.append('Date in ??.MM.YYYY format')
        state="SUCCESS"

    # Date is XX.MM.YYYY
    if re.match(r"xx\.\d{2}\.\d{4}", ds) and len(ds) == 10:
        t=ds.split(".")
        day=""
        month=t[1]
        year=t[2]
        messages.append('Success')
        messages.append('Date in ??.MM.YYYY format')
        state="SUCCESS"

    # Date is ??.??.YYYY
    if re.match(r"\?\?\.\?\?\.\d{4}", ds) and len(ds) == 10:
        t=ds.split(".")
        year=t[2]
        messages.append('Success')
        messages.append('Date in ??.??.YYYY format')
        state="SUCCESS"

    # Date is XX.XX.YYYY
    if re.match(r"xx\.xx\.\d{4}", ds) and len(ds) == 10:
        t=ds.split(".")
        year=t[2]
        messages.append('Success')
        messages.append('Date in ??.??.YYYY format')
        state="SUCCESS"

    # Date is ??.??.????
    if re.match(r"\?\?\.\?\?\.\?\?\?\?", ds) and len(ds) == 10:
        messages.append('Success')
        messages.append('Date in ??.??.???? format')
        state="SUCCESS"

    # Date is XX.XX.XXXX
    if re.match(r"xx\.xx\.xxxx", ds) and len(ds) == 10:
        messages.append('Success')
        messages.append('Date in ??.??.???? format')
        state="SUCCESS"

    # Date is D.MM.YYYY
    if re.match(r"\d{1}\.\d{2}\.\d{4}", ds) and len(ds) == 9:
        t=ds.split(".")
        day="0"+t[0]
        month=t[1]
        year=t[2]
        messages.append('Success')
        messages.append('Date in D.MM.YYYY format')
        state="SUCCESS"

    # Date is ?.MM.YYYY
    if re.match(r"\?\.\d{2}\.\d{4}", ds) and len(ds) == 9:
        t=ds.split(".")
        month=t[1]
        year=t[2]
        messages.append('Success')
        messages.append('Date in ?.MM.YYYY format')
        state="SUCCESS"

    # Date is X.MM.YYYY
    if re.match(r"x\.\d{2}\.\d{4}", ds) and len(ds) == 9:
        t=ds.split(".")
        month=t[1]
        year=t[2]
        messages.append('Success')
        messages.append('Date in ?.MM.YYYY format')
        state="SUCCESS"

    # Date is ?.??.YYYY
    if re.match(r"\?\.\?\?\.\d{4}", ds) and len(ds) == 9:
        t=ds.split(".")
        year=t[2]
        messages.append('Success')
        messages.append('Date in ?.??.YYYY format')
        state="SUCCESS"

    # Date is X.XX.YYYY
    if re.match(r"x\.xx\.\d{4}", ds) and len(ds) == 9:
        t=ds.split(".")
        year=t[2]
        messages.append('Success')
        messages.append('Date in ?.??.YYYY format')
        state="SUCCESS"

    # Date is D.M.YYYY
    if re.match(r"\d{1}\.\d{1}\.\d{4}", ds) and len(ds) == 8:
        t=ds.split(".")
        day="0"+t[0]
        month="0"+t[1]
        year=t[2]
        messages.append('Success')
        messages.append('Date in D.M.YYYY format')
        state="SUCCESS"

    # Date is DD.M.YYYY
    if re.match(r"\d{2}\.\d{1}\.\d{4}", ds) and len(ds) == 9:
        t=ds.split(".")
        day=t[0]
        month="0"+t[1]
        year=t[2]
        messages.append('Success')
        messages.append('Date in D.M.YYYY format')
        state="SUCCESS"


    # Date is X.M.YYYY
    if re.match(r"x\.\d{1}\.\d{4}", ds) and len(ds) == 8:
        t=ds.split(".")
        month="0"+t[1]
        year=t[2]
        messages.append('Success')
        messages.append('Date in X.MM.YYYY format')
        state="SUCCESS"

    # Date is ?.M.YYYY
    if re.match(r"\?\.\d{1}\.\d{4}", ds) and len(ds) == 8:
        t=ds.split(".")
        day=""
        month="0"+t[1]
        year=t[2]
        messages.append('Success')
        messages.append('Date in DD.MM.YYYY format')
        state="SUCCESS"

    # Date is ?.?.YYYY
    if re.match(r"\?\.\?\.\d{4}", ds) and len(ds) == 8:
        t=ds.split(".")
        day=""
        year=t[2]
        messages.append('Success')
        messages.append('Date in DD.MM.YYYY format')
        state="SUCCESS"

    # Date is X.X.YYYY
    if re.match(r"x\.x\.\d{4}", ds) and len(ds) == 8:
        t=ds.split(".")
        year=t[2]
        messages.append('Success')
        messages.append('Date in X.X.YYYY format')
        state="SUCCESS"


    # Date is MM.YYYY
    if re.match(r"\d{2}\.\d{4}", ds) and len(ds) == 7:
        t=ds.split(".")
        month=t[0]
        year=t[1]
        messages.append('Success')
        messages.append('Date in MM.YYYY format')
        state="SUCCESS"

    # Date is ??.YYYY
    if re.match(r"\?\?\.\d{4}", ds) and len(ds) == 7:
        t=ds.split(".")
        year=t[1]
        messages.append('Success')
        messages.append('Date in MM.YYYY format')
        state="SUCCESS"

    # Date is XX.YYYY
    if re.match(r"xx\.\d{4}", ds) and len(ds) == 7:
        t=ds.split(".")
        year=t[1]
        messages.append('Success')
        messages.append('Date in MM.YYYY format')
        state="SUCCESS"

    # Date is four-digit year, e.g. 1234
    if len(ds) == 4 and re.match(r"\d{4}",ds):
        year=ds
        messages.append('Success')
        messages.append('Date in YYYY format')
        state="SUCCESS"

    if len(ds) == 4 and re.match(r"\?\?\?\?",ds):
        year=ds
        messages.append('Success')
        messages.append('Date in ???? format ')
        state="SUCCESS"

    if len(ds) == 4 and re.match(r"xxxx",ds):
        year=ds
        messages.append('Success')
        messages.append('Date in ???? format ')
        state="SUCCESS"

    if year=="9999":
        day=""
        month=""
        year=""
        messages.append("No valid input")

    d.day=day
    d.month=month
    d.year=year
    d.messages=messages
    d.state=state
#    logger.debug(d)
    return d


REPLACEMENTS = {
"BORN" : "_BORN_",
"BAPTISED" : "_BAPTISED_",
"ACTIVE" : "_ACTIVE_",
"DOCUMENTED" : "_DOCUMENTED_",
"BURIED" : "_BURIED_",
"FIRST_DOCUMENTED" : "_FIRST_DOCUMENTED_",
"PUBLICATIONS_FROM" : "_PUBLICATIONS_FROM_",
"LAST_DOCUMENTED" : "_LAST_DOCUMENTED_",
"START" : "_START_",
"HALF" : "_HALF_",
"THIRD" : "_THIRD_",
"QUARTER" : "_QUARTER_",
"BEGIN" : "_BEGIN_",
"END" : "_END_",
"UNTIL" : "_UNTIL_",
"MID" : "_MID_",
"CENTURY" : "_CENTURY_",
"ABOUT" : "_ABOUT_",
"BEFORE" : "_BEFORE_",
"BC_INDICATOR" : "_BC_INDICATOR_",
}


def replace_substring(s,substring,constant):
#    print(s)
#    print("substring")
#    print(substring)
#    print(re.search(substring, s))
    if bool(re.search(substring, s)):
#        ss=s.replace(substring,constant)
#        ss=s
        ss=re.sub(substring,constant,s)
#        print("found substring "+substring+" "+constant+s+" "+ss)
#        print(ss)
        s=ss
#    print(s)
    return s


def remove_tags(string):

    for key in REPLACEMENTS:
        string=string.replace(REPLACEMENTS[key],"")

    return string


@classes.func_logger
def get_date_aspect(ds):
    replace_substring(ds,"geb.",REPLACEMENTS["BORN"])
#    pattern=""
    ds=ds.replace("[","")
    ds=ds.replace("[","")

    ds=ds.replace("januar","01.")
    ds=ds.replace("februar","02.")
    ds=ds.replace("märz","03.")
    ds=ds.replace("april","04.")
    ds=ds.replace("mai","05.")
    ds=ds.replace("juni","06.")
    ds=ds.replace("juli","07.")
    ds=ds.replace("august","08.")
    ds=ds.replace("september","09.")
    ds=ds.replace("oktober","10.")
    ds=ds.replace("november","11.")
    ds=ds.replace("dezember","12.")

    ds=ds.replace("erste","1.")
    ds=ds.replace("zweite","2.")

    #ds = replace_substring(ds,"[?]",REPLACEMENTS["BORN"])

    ds=ds.replace("geb.","geboren")
#    print(ds)
    ds = replace_substring(ds,"[*]",REPLACEMENTS["BORN"])
#    print(ds)
    ds = replace_substring(ds,"geboren",REPLACEMENTS["BORN"])
    ds = replace_substring(ds,"geburtsjahr",REPLACEMENTS["BORN"])

    ds = replace_substring(ds,"getauft am",REPLACEMENTS["BAPTISED"])
    ds = replace_substring(ds,"getauft",REPLACEMENTS["BAPTISED"])
    ds = replace_substring(ds,"taufe",REPLACEMENTS["BAPTISED"])
    ds = replace_substring(ds,"getauft am",REPLACEMENTS["BAPTISED"])
    ds = replace_substring(ds,"taufdatum",REPLACEMENTS["BAPTISED"])
    ds = replace_substring(ds,"get.",REPLACEMENTS["BAPTISED"])


    ds = replace_substring(ds,"wirkungszeit",REPLACEMENTS["ACTIVE"])


    ds = replace_substring(ds,"aktiv",REPLACEMENTS["ACTIVE"])
    ds = replace_substring(ds,"tätig",REPLACEMENTS["ACTIVE"])
    ds = replace_substring(ds,"schrieb",REPLACEMENTS["ACTIVE"])
    ds = replace_substring(ds,"fl.",REPLACEMENTS["ACTIVE"])
    ds = replace_substring(ds,"flor.",REPLACEMENTS["ACTIVE"])
    ds = replace_substring(ds,"wirkte",REPLACEMENTS["ACTIVE"])
    ds = replace_substring(ds,"wirkungsdaten",REPLACEMENTS["ACTIVE"])
    ds = replace_substring(ds,"nachweisbar",REPLACEMENTS["DOCUMENTED"])
    ds = replace_substring(ds,"nachgewiesen",REPLACEMENTS["DOCUMENTED"])
    ds = replace_substring(ds,"bezeugt",REPLACEMENTS["DOCUMENTED"])
    ds = replace_substring(ds,"erwähnt",REPLACEMENTS["DOCUMENTED"])
    ds = replace_substring(ds,"erw",REPLACEMENTS["DOCUMENTED"])
    ds = replace_substring(ds,"belegt",REPLACEMENTS["DOCUMENTED"])

    ds = replace_substring(ds,"begraben am",REPLACEMENTS["BURIED"])



    ds = replace_substring(ds,"erstmals erwähnt",REPLACEMENTS["FIRST_DOCUMENTED"])

    ds = replace_substring(ds,"letztmals erwähnt",REPLACEMENTS["LAST_DOCUMENTED"])

    ds=ds.replace("anf.","anfang")
    ds = replace_substring(ds,"seit anfang",REPLACEMENTS["START"])
    ds = replace_substring(ds,"ab dem",REPLACEMENTS["START"])
    ds = replace_substring(ds,"ab",REPLACEMENTS["START"])
    ds = replace_substring(ds,"seit",REPLACEMENTS["START"])

    ds = replace_substring(ds,"v. chr.",REPLACEMENTS["BC_INDICATOR"])
    ds = replace_substring(ds,"v.chr.",REPLACEMENTS["BC_INDICATOR"])



    ds=ds.replace("jahrhunderts","jahrhundert")
    ds=ds.replace("jhd.","jahrhundert")
    ds=ds.replace("jht.","jahrhundert")
    ds=ds.replace("jh.","jahrhundert")

    ds = replace_substring(ds,"jahrhundert",REPLACEMENTS["CENTURY"])
#    ds = replace_substring(ds,"jh",REPLACEMENTS["CENTURY"])
#    ds = replace_substring(ds,"century",REPLACEMENTS["CENTURY"])

    ds = replace_substring(ds,"hälfte des",REPLACEMENTS["HALF"])
    ds = replace_substring(ds,"hälfte d.",REPLACEMENTS["HALF"])
    ds = replace_substring(ds,"hälfte",REPLACEMENTS["HALF"])
    ds = replace_substring(ds,"hl.",REPLACEMENTS["HALF"])
    ds = replace_substring(ds,"h.",REPLACEMENTS["HALF"])

    ds = replace_substring(ds,"drittel des",REPLACEMENTS["THIRD"])
    ds = replace_substring(ds,"drittel d. ",REPLACEMENTS["THIRD"])
    ds = replace_substring(ds,"drittel",REPLACEMENTS["THIRD"])
    ds = replace_substring(ds,"viertel des",REPLACEMENTS["QUARTER"])
    ds = replace_substring(ds,"viertel d.",REPLACEMENTS["QUARTER"])
    ds = replace_substring(ds,"viertel",REPLACEMENTS["QUARTER"])


#    ds = replace_substring(ds,"[(?)]",REPLACEMENTS["ABOUT"])
    ds = replace_substring(ds,"ca.",REPLACEMENTS["ABOUT"])
    ds = replace_substring(ds,"um",REPLACEMENTS["ABOUT"])
#    replace_substring(ds,"jahrhundert",REPLACEMENTS["CENTURY"])

    ds = replace_substring(ds,"vor dem",REPLACEMENTS["BEFORE"])
    ds = replace_substring(ds,"vor",REPLACEMENTS["BEFORE"])
    ds = replace_substring(ds,"ende",REPLACEMENTS["END"])

#    ds = replace_substring(ds,"bis",REPLACEMENTS["BEGIN"])

    ds = replace_substring(ds,"anfang",REPLACEMENTS["BEGIN"])
    ds = replace_substring(ds,"mitte",REPLACEMENTS["MID"])


    ds = ds.replace("(_","_")
    ds = ds.replace("_)","_")
    return ds






@classes.func_logger
def parse_century(ds):
#    print("Parsing century")
    d=classes.DateRange()
    d.start=classes.Dt()
    d.end=classes.Dt()
    d.messages=["century parsing"]
    d.state="FAIL"
    # case there is nothing
    if len(ds) == 0:
        d.messages.append("No input")
        d.state="SUCCESS"

    ds = ds.replace(REPLACEMENTS["CENTURY"],"")
    ds = ds.replace(" ","")

    if re.match(REPLACEMENTS["ABOUT"],ds):
        ds = ds.replace(REPLACEMENTS["ABOUT"],"")

    if re.match(REPLACEMENTS["BEFORE"],ds):
        ds = ds.replace(REPLACEMENTS["BEFORE"],"")

    if re.match(REPLACEMENTS["BEGIN"],ds):
        ds = ds.replace(REPLACEMENTS["BEGIN"],"")

    if re.match(REPLACEMENTS["MID"],ds):
        ds = ds.replace(REPLACEMENTS["MID"],"")

    if re.match(REPLACEMENTS["ACTIVE"],ds):
        ds = ds.replace(REPLACEMENTS["ACTIVE"],"")

    if re.match(REPLACEMENTS["START"],ds):
        ds = ds.replace(REPLACEMENTS["START"],"")

    if re.match(REPLACEMENTS["BC_INDICATOR"],ds):
        ds = ds.replace(REPLACEMENTS["BC_INDICATOR"],"")


    if re.search("/",ds):
        ds=ds.replace(".","")
        t=ds.split("/")
        d.start.year=t[0]
        d.end.year=t[1]
        d.start.state="SUCCESS"
        d.end.state="SUCCESS"
        d.state="SUCCESS"


#    print(ds)
    # simple case n. CENTURY
    if len(ds) == 2 and re.match(r"\d{1}\.",ds):
#        print("simple century")
#        print(ds)
        x=int(ds[0:1])
        start=(x-1)*100
        end=start+99
        d.start.year=str(start)
        d.end.year= str(end)
        d.messages.append('Success')
        d.messages.append('Only year from century')
        d.start.state="SUCCESS"
        d.end.state="SUCCESS"
        d.state="SUCCESS"



    if len(ds) == 2 and ds.isnumeric():
        x=int(ds[0:2])
        start=(x-1)*100
        end=start+99
        d.start.year=str(start)
        d.end.year= str(end)
        d.messages.append('Success')
        d.messages.append('Only year from century')
        d.end.state="SUCCESS"
        d.start.state="SUCCESS"
        d.state="SUCCESS"

    # simple case nn. CENTURY
    if len(ds) == 3 and re.match(r"\d{2}\.",ds):
        x=int(ds[0:2])
        start=(x-1)*100
        end=start+99
        d.start.year=str(start)
        d.end.year= str(end)
        d.messages.append('Success')
        d.messages.append('Only year from century')
        d.end.state="SUCCESS"
        d.start.state="SUCCESS"
        d.state="SUCCESS"

    if re.search(REPLACEMENTS["HALF"],ds):
        #ds=ds.replace(REPLACEMENTS["HALF"],"")
        ds=ds.replace(".","")
        t=ds.split(REPLACEMENTS["HALF"])
        x=0
        if t[0].isnumeric():
            x=int(t[0])
#        print("half")
#        print(x)
        c = 0
        if t[1].isnumeric():
            c=int(t[1])
#        print(c)
        if x == 1 and c != 0:
            d.start.year=(c-1)*100
            d.end.year=d.start.year+49
            d.end.state="SUCCESS"
            d.start.state="SUCCESS"
            d.state="SUCCESS"
        if x == 2 and c != 0:
            d.start.year=(c-1)*100+50
            d.end.year=d.start.year+49
            d.end.state="SUCCESS"
            d.start.state="SUCCESS"
            d.state="SUCCESS"
        if x==9 and c==99:
            d.end.state="SUCCESS"
            d.start.state="SUCCESS"
            d.state="SUCCESS"


    if re.search(REPLACEMENTS["THIRD"],ds):
        #ds=ds.replace(REPLACEMENTS["HALF"],"")
        ds=ds.replace(".","")
        t=ds.split(REPLACEMENTS["THIRD"])
        x=0
        if t[0].isnumeric():
            x=int(t[0])
#        print("half")
#        print(x)
        c = 0
        if t[1].isnumeric():
            c=int(t[1])
#        print(c)
        if x == 1 and c != 0:
            d.start.year=(c-1)*100
            d.end.year=d.start.year+32
            d.end.state="SUCCESS"
            d.start.state="SUCCESS"
            d.state="SUCCESS"
        if x == 2 and c != 0:
            d.start.year=(c-1)*100+33
            d.end.year=d.start.year+32
            d.end.state="SUCCESS"
            d.start.state="SUCCESS"
            d.state="SUCCESS"
        if x == 2 and c != 0:
            d.start.year=(c-1)*100+66
            d.end.year=d.start.year+32
            d.end.state="SUCCESS"
            d.start.state="SUCCESS"
            d.state="SUCCESS"

    if re.search(REPLACEMENTS["QUARTER"],ds):
        #ds=ds.replace(REPLACEMENTS["HALF"],"")
        ds=ds.replace(".","")
        t=ds.split(REPLACEMENTS["QUARTER"])
        x=0
        if t[0].isnumeric():
            x=int(t[0])
#        print("half")
#        print(x)
        c = 0
        if t[1].isnumeric():
            c=int(t[1])
#        print(c)
        if x == 1 and c != 0:
            d.start.year=(c-1)*100
            d.end.year=d.start.year+24
            d.end.state="SUCCESS"
            d.start.state="SUCCESS"
            d.state="SUCCESS"
        if x == 2 and c != 0:
            d.start.year=(c-1)*100+25
            d.end.year=d.start.year+24
            d.end.state="SUCCESS"
            d.start.state="SUCCESS"
            d.state="SUCCESS"
        if x == 2 and c != 0:
            d.start.year=(c-1)*100+50
            d.end.year=d.start.year+24
            d.end.state="SUCCESS"
            d.start.state="SUCCESS"
            d.state="SUCCESS"
        if x == 2 and c != 0:
            d.start.year=(c-1)*100+75
            d.end.year=d.start.year+24
            d.end.state="SUCCESS"
            d.start.state="SUCCESS"
            d.state="SUCCESS"

    if re.search(r"99\./99\.",ds):
        d.start.state="SUCCESS"
        d.end.state="SUCCESS"
        d.state="SUCCESS"


#    print(d)

    return d



@classes.func_logger
def parse_date_range(ds):

#    print("parse_date_range input:")
#    print(ds)

    messages = []
    state = " "
    d=classes.DateRange()
    start=classes.Dt()
    end=classes.Dt()
    set_result=True

    # case there is nothing
    if len(ds) == 0:
        messages.append("No input")
        state="FAIL"

    # clean string
    ds=re.sub("--","-",ds)
    if len(ds)>=3 and ds[0:3] == "ca.":
        ds=ds[3::]
    ds=re.sub("%"," ",ds)
    ds=re.sub(" des "," ",ds)

#    ds=re.sub("biis","bis",ds)
#    ds=re.sub("bis","-",ds)
#    print("cleaned string")
#    print(ds)
    ds=ds.lower()
    ds=get_date_aspect(ds)
    messages.append(ds)

#    print(ds)
#    print(REPLACEMENTS["CENTURY"])
#    if re.search(REPLACEMENTS["CENTURY"],ds):
#        print("asdgsadf")
#        d = parse_century(ds)

#    else:
    dates = ds.split("-")
    if len(dates) >2:
        messages.append("ADDITIONAL DATE RANGE")


    if len(dates) == 1 and re.search(REPLACEMENTS["CENTURY"],ds):
#        print("asdgsadf")
        d = parse_century(ds)
        d.messages.append(ds)
        set_result=False


    if len(dates) >= 1 :
        start = parse_date(dates[0])
        if start.state=="SUCCESS":
            state="SUCCESS"
    if len(dates) == 2:
#        print("parsing end")
        end = parse_date(dates[1])
        if end.state=="SUCCESS":
            state="SUCCESS"

    if set_result:
#        print("setting result")
        d.start=start
        d.end=end
        d.messages=messages
        d.state=state
#        print(d)

    return d