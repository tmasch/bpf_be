# pylint: disable-all
import asyncio
#from pymarc import MARCReader
#import pymarc
#from pymarc import parse_xml_to_array, Record, Field, Subfield, Indicators
import requests

#import pymarc
from lxml import etree
#import xml.etree.ElementTree
#from xml.dom import minidom 

# def get_field_subfield(record,field,subfield):
#     contents=""
#     print(field)
#     print(subfield)
#     for step1 in record[2][0]:
#         match step1.get('tag'):
#             case field:
#                 for step2 in step1:
#                     match step2.get('code'):
#                         case subfield:
#                         #     pe_id = classes.ExternalReference()
#                         #     pe_id.name = "GND"
#                         #     if step2.text[0:8] == "(DE-588)":
#                             contents = step2.text
#     return contents

async def main():

    f = open("schoeffer.xml","rb")
    xml_string = f.read()
#    print(type)
#    xml_string.
    root=etree.XML(xml_string)
    for child in root:
        print(child.tag)

    url = "https://services.dnb.de/sru/authorities?version=1.1&operation=searchRetrieve&query=Per=Peter%20and%20Per=Schoeffer%20and%20BBG%3DTp*&recordSchema=MARC21-xml&maximumRecords=100"
    response = requests.get(url)
    content = response.content
#    print(content)
    root = etree.XML(content)

    records=root.find("records", namespaces=root.nsmap)
#    print(records)
#    print(records.tag)
    tag_id='400'
    for record in records:

        x = find_datafields(record,"035")
        for y in x:
#            print(y)
            if y.get("a") != None : 
                print(y["a"])
#        print(record.tag)
#        for child in record:
#            print(child.tag)
#            for c in child:
#                print(c.tag)
        ids=record.findall("{*}recordData/{*}record/{*}datafield[@tag='"+tag_id+"']")
#        for i in ids:
#            print("id tags")
#            print(i.tag)
#            ii=i.findall("{*}subfield[@code=]")
#            print(ii[0].text)

        r = find_datafields(record,"100")
        print(r)#
        print(r[0]["a"])





def find_datafields(record,tag_id):
    result=[]
    datafields=record.findall("{*}recordData/{*}record/{*}datafield[@tag='"+tag_id+"']")
    for datafield in datafields:
        subfields=datafield.findall("{*}subfield")
        hash={}
        for subfield in subfields:
            key= subfield.get("code")
            value=subfield.text
            hash[key]=value
        result.append(hash)
    return result

#        print(ii[0].text)
#        print(ii[0].get("code"))
#        print(type(ii[0]))



#    etree.fromstring()
#    etree.
#    print(type(xml))
#    print("input")
#    print(xml)
#    root = tree.getroot()
#    root = xml.etree.ElementTree.fromstring(xml_string)
    #root = tree.getroot()
#    print(root)
#    print(root[2])
#    print(type(root[2]))
#    print(root[2].get("record"))
    # field="375"
    # subfield="a"
    # for record in root[2]:
    #     print(get_field_subfield(record,field,subfield))
    # for record in root[2]:
    #     for step1 in record[2][0]:
    #         match step1.get('tag'):
    #             case field:
    #                 for step2 in step1:
    #                     match step2.get('code'):
    #                         case subfield:
    #                         #     pe_id = classes.ExternalReference()
    #                         #     pe_id.name = "GND"
    #                         #     if step2.text[0:8] == "(DE-588)":
    #                             print(step2.text)


    # for record in root[2][1]:
    #     print("Parsing person information")
    #     print(type(record))
    #     print(record.get('tag'))
#        print(record.find("./recordData"))
#        print(record.text())
#       data=record.get("recordData")
#        print(data)

#    doc = minidom.parse("schoeffer.xml")
#    searchRetrieveResponse=doc.getElementsByTagName("searchRetrieveResponse")[0]
#    rr[0].attributes
#    print(type(searchRetrieveResponse))
#    print(searchRetrieveResponse.toprettyxml())
#    print(searchRetrieveResponse.attributes)
    # print("records")
    # records=doc.getElementsByTagName("record"
    # )
    # records = doc.findall("./searchRetrieveResponse")
    # print(records)
#    print(records.toprettyxml())
#    record=records.getElementsByTagName("record")
#    print(record)
    

    # records=doc.getElementsByTagName("records")
    # print(type(records))
    # record=records[1]
    # print(record)


#     with open('schoeffer.xml', 'rb') as fh:
#         reader = MARCReader(fh)
#         print(reader)
#         print(reader.current_chunk)
# #        reader.current_chunk
#         for record in reader:
# #            record.g
# #            record.get_fields("500")
#             print(record)

#     records = parse_xml_to_array("schoeffer.xml")
#     for record in records:
#         print("record")
# #        print(record)
#         print(type(record))
#         if record: 
#             print(record.get_fields("500"))


#def get_subfield

asyncio.run(main())