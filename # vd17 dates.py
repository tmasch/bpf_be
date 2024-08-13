import re
import urllib.request
import xml.etree.ElementTree

start_number = 268000
#start_number = 1
year_pattern = r'\d{4}'
year_list = []
while start_number < 310000:
#while start_number < 1500:
    #url_bibliography = r'http://sru.k10plus.de/vd18?version=2.0&operation=searchRetrieve&query=bbg%3D(Aa*%20or%20Af*)&maximumRecords=500&startRecord=' + str(start_number) + '&recordSchema=picaxml'
    url_bibliography = r'http://sru.k10plus.de/vd18?version=2.0&operation=searchRetrieve&query=pica.bbg=(Aa*%20or%20Af*)&maximumRecords=500&startRecord='+ str(start_number) + '&recordSchema=picaxml'
    print(url_bibliography)
    url = urllib.request.urlopen(url_bibliography)
    print("File downloaded")
    tree = xml.etree.ElementTree.parse(url)
    root = tree.getroot()
    record_list = root[1]
    for record in record_list:
        #print("parsing individual record")
        #if "a4" in record[0].text:
        #    break
        record_proper = record[2][0]
        for step1 in record_proper:
            match step1.get('tag'):
                    case "011@":
                        print("Date found")
                        for step2 in step1:
                            match step2.get('code'):
                                    case "n":
                                        year = step2.text
                                        print(year)
                                        year_checked = re.match(year_pattern, year)
                                        if not year_checked:
                                            year_list.append(year)
    print(year_list)
    print(start_number)
    print(len(year_list))
    with open(r"C:\Users\berth\bpf_be_fastapi\vd18_dates.txt", "a") as g:
        for line in year_list:
            line = line + "%"
            g.writelines(line)
    year_list = []
    start_number = start_number + 500



