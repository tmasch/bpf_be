import re
from lxml import etree
import books_parsing_manifests
import books_parsing_bibliographies
URI_entered = "abc"


def iiifparse(URI_entered):

# Step 1: Information is collected from the IIIF manifest

    #if URI_entered == "":
    #        break
    if "digitale-sammlungen.de" in URI_entered:
        m = books_parsing_manifests.BSB_parsing(URI_entered)
    elif "uni-halle.de" in URI_entered:
        m = books_parsing_manifests.Halle_parsing(URI_entered)
    elif "staatsbibliothek-berlin" in URI_entered:
        m = books_parsing_manifests.Berlin_parsing(URI_entered)
    elif "trin.cam." in URI_entered:
        m = books_parsing_manifests.Cambridge_Trinity_parsing(URI_entered)
    elif "Parker" in URI_entered:
        m = books_parsing_manifests.Cambridge_Corpus_parsing(URI_entered)
    elif "thulb.uni-jena" in URI_entered:        
        m = books_parsing_manifests.ThULB_parsing(URI_entered)
    elif "slub-dresden" in URI_entered:
        m = books_parsing_manifests.SLUB_parsing(URI_entered)
    elif "ub.uni-leipzig" in URI_entered:
        m = books_parsing_manifests.Leipzig_parsing(URI_entered)
    #else:
    #    print("This book comes from a library that is not yet supported by the system.")
    #    break

    
    m.iiifUrl = URI_entered


# Step 2: The bibliographical references in the manifest (in a later development also bibliographical references entered manually) will be parsed, and information from them added. 

    for step1 in range(len(m.bibliographic_id)):
        #print(m.bibliographic_id[step1][1])        
        if (m.bibliographic_id[step1]).name == "VD17" or (m.bibliographic_id[step1]).name == "vd17":
            url_bibliography = r"http://sru.k10plus.de/vd17?version=2.0&operation=searchRetrieve&query=pica.vds=" + (m.bibliographic_id[step1]).id + r'&maximumRecords=10&startRecord=1&recordSchema=marcxml'
            #bibliographic_information_single = VD17_parsing((book_properties[2][step1])[2])
            bibliographic_information_single = books_parsing_bibliographies.VD17_parsing(url_bibliography)
        elif (m.bibliographic_id[step1]).name == "VD18" or (m.bibliographic_id[step1]).name == "vd18":
            url_bibliography = r"http://sru.k10plus.de/vd18?version=2.0&operation=searchRetrieve&query=pica.vdt=vd18" + (m.bibliographic_id[step1]).id + r'&maximumRecords=10&startRecord=1&recordSchema=marcxml'
            print(url_bibliography)
            bibliographic_information_single = books_parsing_bibliographies.VD17_parsing(url_bibliography)
        elif(m.bibliographic_id[step1]).name == "VD16" or (m.bibliographic_id[step1]).name == "vd16":
            vd16_complete = (m.bibliographic_id[step1]).id
            vd16_divided = re.split(" ", vd16_complete)            
            url_bibliography = r"http://gateway-bayern.de/VD16+" + vd16_divided[0] + "+" + vd16_divided[1]            
            bibliographic_information_single = books_parsing_bibliographies.VD16_parsing(url_bibliography)            
            #url_bibliography = r''
        elif(m.bibliographic_id[step1]).name == "GW":
            GW_number = (m.bibliographic_id[step1]).id.lstrip("0")
              ##Removing leading zeros that are accepted in many cases but not by the ISTC            
            url_bibliography = r'https://data.cerl.org/istc/_search?_format=json&pretty=false&query=reference%3A%22GW ' + GW_number + r'%22&size=10&sort=default&from=0&file=false&orig=true&facet=dimensions&facet=printingcountry&facet=holdingcountry&nofacets=true&mode=default&aggregations=true'
            bibliographic_information_single = books_parsing_bibliographies.ISTC_parsing(url_bibliography) 
        elif(m.bibliographic_id[step1]).name == "ISTC":
            ISTC_number = (m.bibliographic_id[step1]).id
            url_bibliography = r'https://data.cerl.org/istc/_search?_format=json&pretty=false&query=_id%3A' + ISTC_number + r'&size=10&sort=default&from=0&file=false&orig=true&facet=Format&facet=Holding%20country&facet=Publication%20country&nofacets=true&mode=default&aggregations=true'
            bibliographic_information_single = books_parsing_bibliographies.ISTC_parsing(url_bibliography) 
        if bibliographic_information_single != "": #omit appending if nothing came back from the function (this is the case when the record
            #describes a series, not a book)
            m.bibliographic_information.append(bibliographic_information_single)
    return m