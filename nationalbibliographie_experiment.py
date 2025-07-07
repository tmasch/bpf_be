import requests
from lxml import etree




def main():
    bibliographie = input("Bitte Jahr, Reihe und Monat eingeben, z.B. 25A07: ")
    eintragsliste = datensaetze_herunterladen(bibliographie)
    for eintrag in eintragsliste:
        titelangabe = lade_titel(eintrag)
        print(titelangabe)
        print("xxx" + titelangabe[0:3] + "xxx")



def find_datafields(record,tag_id):
    """
    Returns a list of all datafields of a MARCXML Document with the same field number
    """
    datafields=record.findall("{*}recordData/{*}record/{*}datafield[@tag='"+tag_id+"']")
    return datafields

def find_subfields(datafield,subfield_id):
    """
    Returns a list of all subfields of a datafield in a MARCXML 
    Document with the same subfield number
    """
    r=[]
    subfields=datafield.findall("{*}subfield")
    for subfield in subfields:
        key= subfield.get("code")
        value=subfield.text
        if key == subfield_id:
            r.append(value)
    return r



def datensaetze_herunterladen(bibliographie):
    """
    lädt die entsprechende Liste aus der GND herunter und gibt sie zurück
    """
    #bibliography = input("Bitte Jahr, Reihe und Monat eingeben, z.B. 25A07")
    url = r'https://services.dnb.de/sru/dnb?version=1.1&operation=searchRetrieve&query=WVN%3D'+bibliographie + r'&recordSchema=MARC21-xml&maximumRecords=10'
    antwort_roh = requests.get(url, timeout = 10)
    antwort = antwort_roh.content
    print(antwort)
    root = etree.XML(antwort)
    eintragsliste = root.find("records", namespaces=root.nsmap)
    return eintragsliste


def lade_titel(eintrag):
    """wertet das Feld MARC 245 (Titel + Titelzusatz + Verantwortlichkeitsangabe) aus"""
    titelangabe, titel, titelzusatz, verantwortlichkeitsangabe = "", "", "", ""
    datafields = find_datafields(eintrag, "245")
    if datafields:
        subfields = find_subfields(datafields[0], "a")
        if subfields:
            titel = subfields[0]
            if "&#152;" in titel:
                print("Sonderzeichen gefunden")
                titel = titel.replace("&#152;", "")
            #print(titel)
        subfields = find_subfields(datafields[0], "b")
        if subfields:
           titelzusatz = subfields[0]
        subfields = find_subfields(datafields[0], "c")
        if subfields:
            verantwortlichkeitsangabe = subfields[0]
        if titelzusatz:
            titelzusatz = " : " + titelzusatz
        if verantwortlichkeitsangabe:
            verantwortlichkeitsangabe = " / " + verantwortlichkeitsangabe
        titelangabe = titel + titelzusatz + verantwortlichkeitsangabe

    return titelangabe



if __name__ == "__main__":
    main()