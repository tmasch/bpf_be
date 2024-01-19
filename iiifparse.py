import re
from lxml import etree
import books_parsing_manifests
import books_parsing_bibliographies
URI_entered = "abc"

def bibliography_select (bid_name, bid_id):
    if (bid_name == "VD17" or bid_name == "vd17"):
        url_bibliography = r"http://sru.k10plus.de/vd17?version=2.0&operation=searchRetrieve&query=pica.vds=" + bid_id + r'&maximumRecords=10&startRecord=1&recordSchema=marcxml'
        #bibliographic_information_single = VD17_parsing((book_properties[2][step1])[2])
        bibliographic_information_single = books_parsing_bibliographies.VD17_parsing(url_bibliography)
    elif (bid_name == "VD18" or bid_name == "vd18"):
        url_bibliography = r"http://sru.k10plus.de/vd18?version=2.0&operation=searchRetrieve&query=pica.vdt=vd18" + bid_id + r'&maximumRecords=10&startRecord=1&recordSchema=marcxml'
        print(url_bibliography)
        bibliographic_information_single = books_parsing_bibliographies.VD17_parsing(url_bibliography)
    elif(bid_name == "VD16" or bid_name == "vd16"):
        vd16_complete = bid_id
        vd16_divided = re.split(" ", vd16_complete)            
        url_bibliography = r"http://gateway-bayern.de/VD16+" + vd16_divided[0] + "+" + vd16_divided[1]            
        bibliographic_information_single = books_parsing_bibliographies.VD16_parsing(url_bibliography)            
            #url_bibliography = r''
    elif bid_name == "GW":
        GW_number = bid_id.lstrip("0")
        ##Removing leading zeros that are accepted in many cases but not by the ISTC            
        url_bibliography = r'https://data.cerl.org/istc/_search?_format=json&pretty=false&query=reference%3A%22GW ' + GW_number + r'%22&size=10&sort=default&from=0&file=false&orig=true&facet=dimensions&facet=printingcountry&facet=holdingcountry&nofacets=true&mode=default&aggregations=true&style=full'
        bibliographic_information_single = books_parsing_bibliographies.ISTC_parsing(url_bibliography) 
    elif bid_name  == "ISTC":
        ISTC_number = bid_id
        url_bibliography = r'https://data.cerl.org/istc/_search?_format=json&pretty=false&query=_id%3A' + ISTC_number + r'&size=10&sort=default&from=0&file=false&orig=true&facet=Format&facet=Holding%20country&facet=Publication%20country&nofacets=true&mode=default&aggregations=true&style=full'
        bibliographic_information_single = books_parsing_bibliographies.ISTC_parsing(url_bibliography) 
    # the following options (and perhaps more will have to follow) are only used for libraries such as the BnF that do not regularly give ISTC or GW numbers
    elif bid_name == "Goff":
        url_bibliography = r'https://data.cerl.org/istc/_search?_format=json&pretty=false&query=reference%3A%22Goff ' + bid_id + r'%22&size=10&sort=default&from=0&file=false&orig=true&facet=dimensions&facet=printingcountry&facet=holdingcountry&nofacets=true&mode=default&aggregations=true'
        bibliographic_information_single = books_parsing_bibliographies.ISTC_parsing(url_bibliography)
        if bibliographic_information_single == None: # Sometimes, ISTC write the Goff number without a hyphen
            bid_id = bid_id.replace("-", "")
            url_bibliography = r'https://data.cerl.org/istc/_search?_format=json&pretty=false&query=reference%3A%22Goff ' + bid_id + r'%22&size=10&sort=default&from=0&file=false&orig=true&facet=dimensions&facet=printingcountry&facet=holdingcountry&nofacets=true&mode=default&aggregations=true&style=full&style=full'
            print("search string without hyphen: ")
            print(url_bibliography)
            bibliographic_information_single = books_parsing_bibliographies.ISTC_parsing(url_bibliography)
    elif bid_name == "CIBN":
        url_bibliography = r'https://data.cerl.org/istc/_search?_format=json&pretty=false&query=reference%3A%22CIBN ' + bid_id + r'%22&size=10&sort=default&from=0&file=false&orig=true&facet=dimensions&facet=printingcountry&facet=holdingcountry&nofacets=true&mode=default&aggregations=true&style=full'
        bibliographic_information_single = books_parsing_bibliographies.ISTC_parsing(url_bibliography)
    elif bid_name == "C":
        url_bibliography = r'https://data.cerl.org/istc/_search?_format=json&pretty=false&query=reference%3A%22C ' + bid_id + r'%22&size=10&sort=default&from=0&file=false&orig=true&facet=dimensions&facet=printingcountry&facet=holdingcountry&nofacets=true&mode=default&aggregations=true&style=full'
        bibliographic_information_single = books_parsing_bibliographies.ISTC_parsing(url_bibliography)
    elif bid_name == "HC":
        url_bibliography = r'https://data.cerl.org/istc/_search?_format=json&pretty=false&query=reference%3A%22HC ' + bid_id + r'%22&size=10&sort=default&from=0&file=false&orig=true&facet=dimensions&facet=printingcountry&facet=holdingcountry&nofacets=true&mode=default&aggregations=true&style=full'
        bibliographic_information_single = books_parsing_bibliographies.ISTC_parsing(url_bibliography)
        if bibliographic_information_single == None: # ISTC makes a distinction between "H" (the main part of the work), "HC" (the most common addition) and "HCR" (the appendix), the BnF has them both as Hain-Copinger
            url_bibliography = r'https://data.cerl.org/istc/_search?_format=json&pretty=false&query=reference%3A%22H ' + bid_id + r'%22&size=10&sort=default&from=0&file=false&orig=true&facet=dimensions&facet=printingcountry&facet=holdingcountry&nofacets=true&mode=default&aggregations=true&style=full'
            bibliographic_information_single = books_parsing_bibliographies.ISTC_parsing(url_bibliography)
        if bibliographic_information_single == None: # ISTC makes a distinction between "HC" (the main part of the work) and "HCR" (the appendix), the BnF has them both as Hain-Copinger
            url_bibliography = r'https://data.cerl.org/istc/_search?_format=json&pretty=false&query=reference%3A%22HCR ' + bid_id + r'%22&size=10&sort=default&from=0&file=false&orig=true&facet=dimensions&facet=printingcountry&facet=holdingcountry&nofacets=true&mode=default&aggregations=true&style=full'
            bibliographic_information_single = books_parsing_bibliographies.ISTC_parsing(url_bibliography)       
    elif bid_name == "Pell Ms":
        url_bibliography = r'https://data.cerl.org/istc/_search?_format=json&pretty=false&query=reference%3A%22Pell Ms ' + bid_id + r'%22&size=10&sort=default&from=0&file=false&orig=true&facet=dimensions&facet=printingcountry&facet=holdingcountry&nofacets=true&mode=default&aggregations=true&style=full'
        bibliographic_information_single = books_parsing_bibliographies.ISTC_parsing(url_bibliography)
    elif bid_name == "Bod-inc":
        url_bibliography = r'https://data.cerl.org/istc/_search?_format=json&pretty=false&query=reference%3A%22Bod-inc ' + bid_id + r'%22&size=10&sort=default&from=0&file=false&orig=true&facet=dimensions&facet=printingcountry&facet=holdingcountry&nofacets=true&mode=default&aggregations=true&style=full'
        bibliographic_information_single = books_parsing_bibliographies.ISTC_parsing(url_bibliography)
    

    #print(bibliographic_information_single)
    return(bibliographic_information_single)



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
    elif "gallica.bnf.fr" in URI_entered:
        m = books_parsing_manifests.Gallica_parsing(URI_entered)
    elif "e-codices.ch" in URI_entered:
        m = books_parsing_manifests.Ecodices_parsing(URI_entered)
    elif "e-rara.ch" in URI_entered:
        m = books_parsing_manifests.Erara_parsing(URI_entered)
    elif "bodleian.ox.ac.uk" in URI_entered:
        m = books_parsing_manifests.Bodleian_parsing(URI_entered)
    elif "digi.ub.uni-heidelberg.de" in URI_entered:
        m = books_parsing_manifests.Heidelberg_parsing(URI_entered)
    elif "digi.vatlib.it" in URI_entered:
        m = books_parsing_manifests.Vaticana_parsing(URI_entered)
    elif "onb.ac.at" in URI_entered:
        m = books_parsing_manifests.Vienna_parsing(URI_entered)
    elif "loc.gov" in URI_entered:
        m = books_parsing_manifests.Washington_parsing(URI_entered)
    elif "sub.uni-goettingen" in URI_entered:
        m = books_parsing_manifests.Goettingen_parsing(URI_entered)
    elif "figgy.princeton.edu" in URI_entered:
        m = books_parsing_manifests.Princeton_parsing(URI_entered)
    elif "library.yale.edu" in URI_entered:
        m = books_parsing_manifests.Yale_parsing(URI_entered)
    elif "digitalcommonwealth" in URI_entered:
        m = books_parsing_manifests.Boston_parsing(URI_entered)
    elif "manchester.ac.uk" in URI_entered:
        m = books_parsing_manifests.Manchester_parsing(URI_entered)
    elif "cudl.lib.cam.ac.uk" in URI_entered:
        m = books_parsing_manifests.Cambridge_UL_parsing(URI_entered)
    elif "irht.cnrs.fr" in URI_entered:
        m = books_parsing_manifests.IRHT_parsing(URI_entered)
    elif "ub.uni-frankfurt.de" in URI_entered:
        m = books_parsing_manifests.Frankfurt_parsing(URI_entered)
    elif "haab-digital" in URI_entered:
        m = books_parsing_manifests.Weimar_parsing(URI_entered)
    elif "dibiki.ub.uni-kiel" in URI_entered:
        m = books_parsing_manifests.Kiel_parsing(URI_entered)
    elif "sub.uni-hamburg.de" in URI_entered:
        m = books_parsing_manifests.Hamburg_parsing(URI_entered)
    elif "rosdok.uni-rostock.de" in URI_entered:
        m = books_parsing_manifests.Rostock_parsing(URI_entered)
    elif "online-service.nuernberg.de" in URI_entered:
        m = books_parsing_manifests.Nuernberg_StB_parsing(URI_entered)
    elif "manuscriptorium.com" in URI_entered: # This is a system describing primarily MSS in Bohemian lands, but also some in Austria
        m = books_parsing_manifests.Manuscriptorium_parsing(URI_entered)

    #else:
    #    print("This book comes from a library that is not yet supported by the system.")
    #    break
    m.iiifUrl = URI_entered
    

# Step 2: The bibliographical references in the manifest (in a later development also bibliographical references entered manually) will be parsed, and information from them added. 



    
    for step1 in range(len(m.bibliographic_id)):
        #print(m.bibliographic_id[step1][1])        
        bid_name = (m.bibliographic_id[step1]).name
        bid_id = (m.bibliographic_id[step1]).id
        bibliographic_information_single = bibliography_select(bid_name, bid_id)


        if bibliographic_information_single != "": #omit appending if nothing came back from the function (this is the case when the record
            #describes a series, not a book)
            m.bibliographic_information.append(bibliographic_information_single)

    # If several bibliographical references are given that refer to the same (e.g., ISTC and GW), there will be duplicate bibliographical records that should be removed
    # This is a rather awkward way of doing it - but won't do much harm since only in very rare cases there will be more than 2 references
    if len(m.bibliographic_information) > 1:
        counter1 = 0
        print("counter1: " + str(counter1))
        
        while counter1 < len(m.bibliographic_information) -1:
            bibliography_short = m.bibliographic_information[counter1].bibliographic_id[0].uri + m.bibliographic_information[counter1].bibliographic_id[0].name + m.bibliographic_information[counter1].bibliographic_id[0].id
            print("first record: " + bibliography_short)
            counter2 = counter1 + 1
            print("counter2: " + str(counter2))
            while counter2 < len(m.bibliographic_information):
                bibliography_short_compare = m.bibliographic_information[counter2].bibliographic_id[0].uri + m.bibliographic_information[counter2].bibliographic_id[0].name + m.bibliographic_information[counter2].bibliographic_id[0].id
                print("second record: " + bibliography_short_compare)
                if bibliography_short_compare == bibliography_short:
                    m.bibliographic_information.pop(counter2)
                    print("found identical")
                else:
                    counter2 = counter2 + 1
                    print("found not identical")
                    print("counter2 after increment" + str(counter2))
            counter1 = counter1 + 1
            print("counter1 after increment" + str(counter1))



    return m


def supply_bibliographic_information(additional_bid):
# This function is needed if an IIIF manifest does not include a bibliographic reference. 
# If a bibliographic reference is known to the editor, he can add it in a second step. 
# This function parses it and sends the results to the function bibliography_select, and returns the resulting bibliographic data to main.py
    bid_pattern = r'([A-Za-z]{2,4}[\w]{0,2})( )(.*)'
    bid_divided = re.match(bid_pattern, additional_bid)
    bid_name = bid_divided[1]
    bid_id = bid_divided[3]
    bibliographic_information_single = bibliography_select(bid_name, bid_id)    
    return bibliographic_information_single


