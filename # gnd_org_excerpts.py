import xml.etree.ElementTree
import re

def gnd_org_excerpts():
    with open(r"C:\Users\berth\bpf_files\gnd_org_first_attempt.xml", "r", encoding = "utf-8") as f:
        tree = xml.etree.ElementTree.parse(f)    
        root = tree.getroot()
        print("Wurzel gezogen")
        conn_person_list = []
        conn_org_list = []
        dates_list = []
        conn_date_list = []
        conn_keyword_list = []
        conn_place_list = []
        date_pattern = r'(v?\d{1,4})(-| - )(v?\d{1,4})'
        for record in root:
            for step1 in record:           
                match step1.get('tag'):
                    case "500": #persons
                        conn_person = ""
                        conn_person_comment = ""
                        for step2 in step1:
                            match step2.get('code'):
                                case "4":
                                    if step2.text[0:4] != "http":
                                        conn_person = step2.text
                                case "9":
                                    conn_person_comment = step2.text
                        if conn_person != "":
                            conn_person_complete = (conn_person, conn_person_comment)
                            conn_person_list.append(conn_person_complete)
                    case "510": #other organisation
                        conn_org = ""
                        conn_org_comment = ""
                        for step2 in step1:
                            match step2.get('code'):
                                case "4":
                                    if step2.text[0:4] != "http":
                                        conn_org = step2.text
                                case "9":
                                    conn_org_comment = step2.text
                        if conn_org != "":
                            conn_org_complete = (conn_org, conn_org_comment)
                            conn_org_list.append(conn_org_complete)
                    case "548": #date
                        conn_date = ""
                        conn_date_comment = ""
                        for step2 in step1:
                            match step2.get('code'):
                                case "a":
                                    date_standard = re.match(date_pattern, step2.text)
                                    if not date_standard:
                                        datestring = step2.text
                                        dates_list.append(datestring)
                                case "4":
                                    if step2.text[0:4] != "http":
                                        conn_date = step2.text
                                case "9":
                                    conn_date_comment = step2.text
                        if conn_date != "":
                            conn_date_complete = (conn_date, conn_date_comment)
                            conn_date_list.append(conn_date_complete)
                    case "550": #keyword
                        conn_keyword = ""
                        conn_keyword_comment = ""
                        for step2 in step1:
                            match step2.get('code'):
                                case "4":
                                    if step2.text[0:4] != "http":
                                        conn_keyword = step2.text
                                case "9":
                                    conn_keyword_comment = step2.text
                        if conn_keyword != "":
                            conn_keyword_complete = (conn_keyword, conn_keyword_comment)
                            conn_keyword_list.append(conn_keyword_complete)
                    case "551": #place
                        conn_place = ""
                        conn_place_comment = ""
                        for step2 in step1:
                            match step2.get('code'):
                                case "4":
                                    if step2.text[0:4] != "http":
                                        conn_place = step2.text
                                case "9":
                                    conn_place_comment = step2.text
                        if conn_place != "":
                            conn_place_complete = (conn_place, conn_place_comment)
                            conn_place_list.append(conn_place_complete)
    #print (conn_person_list)
    #print (conn_org_list)
    #print(dates_list)
    #print(conn_date_list)
    #print(conn_keyword_list)
    #print(conn_place_list)
                        
            if len(conn_person_list) > 100:
                with open(r"C:\Users\berth\bpf_files\gnd_org_persons.txt", "a", encoding = "utf-8") as g:
                    for person in conn_person_list:
                        g.writelines("#".join(person) + "\n")
                conn_person_list = []
            if len(conn_org_list) > 100:
                with open(r"C:\Users\berth\bpf_files\gnd_org_orgs.txt", "a", encoding = "utf-8") as h:
                    for org in conn_org_list:
                        h.writelines("#".join(org) + "\n")
                conn_org_list = []
            if len(dates_list) > 100:
                with open(r"C:\Users\berth\bpf_files\gnd_org_datestrings.txt", "a", encoding = "utf-8") as i:
                    for datestring in dates_list:
                        i.writelines(datestring + "\n")
                dates_list = []
                print("100 datestrings")
            if len(conn_date_list) > 100:            
                with open(r"C:\Users\berth\bpf_files\gnd_org_dates.txt", "a", encoding = "utf-8") as j:
                    for date in conn_date_list:
                        j.writelines("#".join(date) + "\n")
                conn_date_list = []
            if len(conn_keyword_list) > 100:
                with open(r"C:\Users\berth\bpf_files\gnd_org_keywords.txt", "a", encoding = "utf-8") as k:
                    for keyword in conn_keyword_list:
                        k.writelines("#".join(keyword) + "\n")
                conn_keyword_list = []
            if len(conn_place_list) > 100:
                with open(r"C:\Users\berth\bpf_files\gnd_org_places.txt", "a", encoding = "utf-8") as l:
                    for place in conn_place_list:
                        l.writelines("#".join(place) + "\n")
                conn_place_list = []
    
                    

                    




    return


def gnd_person_excerpts():
    with open(r"C:\Users\berth\bpf_files\gnd_persons\gnd_person_excerpt.xml", "r", encoding = "utf-8") as f:
        tree = xml.etree.ElementTree.parse(f)    
        root = tree.getroot()
        print("Wurzel gezogen")
        conn_person_list = []

        conn_org_list = []
        dates_list = []
        conn_date_list = []
        conn_keyword_list = []
        conn_place_list = []
        date_pattern = r'(v?\d{1,4})(-| - )(v?\d{1,4})'
        for record in root:
            for step1 in record:           
                match step1.get('tag'):
                    case "500": #persons
                        conn_person = ""
                        conn_person_comment = ""
                        for step2 in step1:
                            match step2.get('code'):
                                case "4":
                                    if step2.text[0:4] != "http":
                                        conn_person = step2.text
                                case "9":
                                    conn_person_comment = step2.text
                        if conn_person != "":
                            conn_person_complete = (conn_person, conn_person_comment)
                            conn_person_list.append(conn_person_complete)
                    case "510": #other organisation
                        conn_org = ""
                        conn_org_comment = ""
                        for step2 in step1:
                            match step2.get('code'):
                                case "4":
                                    if step2.text[0:4] != "http":
                                        conn_org = step2.text
                                case "9":
                                    conn_org_comment = step2.text
                        if conn_org != "":
                            conn_org_complete = (conn_org, conn_org_comment)
                            conn_org_list.append(conn_org_complete)
                    case "548": #date
                        conn_date = ""
                        conn_date_comment = ""
                        for step2 in step1:
                            match step2.get('code'):
                                case "a":
                                    date_standard = re.match(date_pattern, step2.text)
                                    if not date_standard:
                                        datestring = step2.text
                                        dates_list.append(datestring)
                                    else:
                                        datestring = ""
                                case "4":
                                    if step2.text[0:4] != "http":
                                        conn_date = step2.text
                                case "9":
                                    conn_date_comment = step2.text
                        if conn_date != "":
                            conn_date_complete = (conn_date, conn_date_comment, datestring)
                            conn_date_list.append(conn_date_complete)
                    case "550": #keyword
                        conn_keyword = ""
                        conn_keyword_comment = ""
                        for step2 in step1:
                            match step2.get('code'):
                                case "4":
                                    if step2.text[0:4] != "http":
                                        conn_keyword = step2.text
                                case "9":
                                    conn_keyword_comment = step2.text
                        if conn_keyword != "":
                            conn_keyword_complete = (conn_keyword, conn_keyword_comment)
                            conn_keyword_list.append(conn_keyword_complete)
                    case "551": #place
                        conn_place = ""
                        conn_place_comment = ""
                        for step2 in step1:
                            match step2.get('code'):
                                case "4":
                                    if step2.text[0:4] != "http":
                                        conn_place = step2.text
                                case "9":
                                    conn_place_comment = step2.text
                        if conn_place != "":
                            conn_place_complete = (conn_place, conn_place_comment)
                            conn_place_list.append(conn_place_complete)
    #print (conn_person_list)
    #print (conn_org_list)
    #print(dates_list)
    #print(conn_date_list)
    #print(conn_keyword_list)
    #print(conn_place_list)
                        
            if len(conn_person_list) > 100:
                with open(r"C:\Users\berth\bpf_files\gnd_person_persons.txt", "a", encoding = "utf-8") as g:
                    for person in conn_person_list:
                        g.writelines("#".join(person) + "\n")
                conn_person_list = []
            if len(conn_org_list) > 100:
                with open(r"C:\Users\berth\bpf_files\gnd_person_orgs.txt", "a", encoding = "utf-8") as h:
                    for org in conn_org_list:
                        h.writelines("#".join(org) + "\n")
                conn_org_list = []
            if len(dates_list) > 100:
                with open(r"C:\Users\berth\bpf_files\gnd_person_datestrings.txt", "a", encoding = "utf-8") as i:
                    for datestring in dates_list:
                        i.writelines(datestring + "\n")
                dates_list = []
                print("100 datestrings")
            if len(conn_date_list) > 100:            
                with open(r"C:\Users\berth\bpf_files\gnd_person_dates.txt", "a", encoding = "utf-8") as j:
                    for date in conn_date_list:
                        j.writelines("#".join(date) + "\n")
                conn_date_list = []
            if len(conn_keyword_list) > 100:
                with open(r"C:\Users\berth\bpf_files\gnd_person_keywords.txt", "a", encoding = "utf-8") as k:
                    for keyword in conn_keyword_list:
                        k.writelines("#".join(keyword) + "\n")
                conn_keyword_list = []
            if len(conn_place_list) > 100:
                with open(r"C:\Users\berth\bpf_files\gnd_person_places.txt", "a", encoding = "utf-8") as l:
                    for place in conn_place_list:
                        l.writelines("#".join(place) + "\n")
                conn_place_list = []
    
                    

                    




    return


def gnd_org_excerpts_for_BSB():
    with open(r"C:\Users\berth\bpf_files\gnd_org_first_attempt.xml", "r", encoding = "utf-8") as f:
        print("opened")
        tree = xml.etree.ElementTree.parse(f)    
        root = tree.getroot()
        print("Wurzel gezogen")
        records_excerpts_list = []
        for record in root:
            keyword_comment_list = []
            comment_list = []
            for step1 in record:           
                match step1.get('tag'):
                    case "024": #ID number
                        id = ""
                        for step2 in step1:
                            match step2.get("code"):
                                case "a":
                                    id = step2.text
                    case "550": #keyword
                        conn_keyword_comment = ""
                        for step2 in step1:
                            match step2.get('code'):
                                case "9":
                                    if "{" in step2.text:
                                        conn_keyword_comment = step2.text
                                    if conn_keyword_comment != "":
                                        print(conn_keyword_comment)
                                        keyword_comment_list.append(conn_keyword_comment)
                    case "678": 
                        comment = ""
                        for step2 in step1:
                            match step2.get("code"):
                                case "b":
                                    #if step2.text[0:5] == "Sitz:":
                                    if "{" in step2.text:
                                        comment = step2.text
                                    if comment != "":
                                        print(comment)
                                        comment_list.append(comment)
            # I assume here that there will be no more than three comments
            # What I do here is the opposite of elegant, but it will be quick
            if keyword_comment_list != [] or comment_list != []:
                if len(keyword_comment_list) == 0:
                    keyword_comment_0 = ""
                    keyword_comment_1 = ""
                    keyword_comment_2 = ""
                elif len(keyword_comment_list) == 1:
                    keyword_comment_0 = keyword_comment_list[0]
                    keyword_comment_1 = ""
                    keyword_comment_2 = ""
                elif len(keyword_comment_list) == 2:
                    keyword_comment_0 = keyword_comment_list[0]
                    keyword_comment_1 = keyword_comment_list[1]
                    keyword_comment_2 = ""
                elif len(keyword_comment_list) == 3:
                    keyword_comment_0 = keyword_comment_list[0]
                    keyword_comment_1 = keyword_comment_list[1]
                    keyword_comment_2 = keyword_comment_list[2]
                if len(comment_list) == 0:
                    comment_0 = ""
                    comment_1 = ""
                    comment_2 = ""
                elif len(comment_list) == 1:
                    comment_0 = comment_list[0]
                    comment_1 = ""
                    comment_2 = ""
                elif len(comment_list) == 2:
                    comment_0 = comment_list[0]
                    comment_1 = comment_list[1]
                    comment_2 = ""
                elif len(comment_list) == 3:
                    comment_0 = comment_list[0]
                    comment_1 = comment_list[1]
                    comment_2 = comment_list[2]
                record_excerpt = id + "#" + keyword_comment_0 + "#" + keyword_comment_1 + "#" + keyword_comment_2 + "#" + comment_0 + "#" + comment_1 + '#' + comment_2
                records_excerpts_list.append(record_excerpt)
                        
            if len(records_excerpts_list) > 100: # nach mehr als 100 Datensätzen wird die Liste in eine Datei geschrieben und dann geleert
                # (das ist nicht unbedingt nötig, weil die Menge klein ist, aber bei meinen größeren Exzerpten ist das Programm sonst abgestürzt)
                with open(r"C:\Users\berth\bpf_files\gnd_org_excerpts_for_BSB.txt", "a", encoding = "utf-8") as g:
                    for excerpt in records_excerpts_list:
                        g.writelines(excerpt + "\n")
                records_excerpts_list = []
    with open(r"C:\Users\berth\bpf_files\gnd_org_excerpts_for_BSB.txt", "a", encoding = "utf-8") as g:
        # dann werden noch die restlichen Einträge (also unter 100) hinzugefügt (das hatte ich bisher vergessen, so daß wohl 1-2 % fehlen)
        for excerpt in records_excerpts_list:
            g.writelines(excerpt + "\n")        
    return


#x = gnd_org_excerpts()
#x = gnd_person_excerpts()
x = gnd_org_excerpts_for_BSB()
    