#pylint: disable=C0301,C0303
"""
Module to parse iiif files
"""
import re
#from lxml import etree
import classes
import parse_istc
import parse_manifests
import books_parsing_bibliographies
import get_external_data
import parse_gnd
import parse_vd17_vd18

import beanie
from beanie import WriteRules

#URI_entered = "abc"

@classes.async_func_logger
async def get_bibliographic_data (bid_name, bid_id):
    """
    \todo documentation
    """
    print("select_bibliography")
    if (bid_name == "VD17" or bid_name == "vd17"):
        url_bibliography = r"http://sru.k10plus.de/vd17?version=2.0&operation=searchRetrieve&query=pica.vds=" + bid_id + r'&maximumRecords=10&startRecord=1&recordSchema=marcxml'
        #bibliographic_information_single = VD17_parsing((book_properties[2][step1])[2])
        print("getting bibliography")
        print(url_bibliography)
        bibliographic_information_single = await parse_vd17_vd18.parse_vd17(url_bibliography)
    elif (bid_name == "VD18" or bid_name == "vd18"):
        url_bibliography = r"http://sru.k10plus.de/vd18?version=2.0&operation=searchRetrieve&query=pica.vdt=vd18" + bid_id + r'&maximumRecords=10&startRecord=1&recordSchema=marcxml'
        print(url_bibliography)
        bibliographic_information_single = await parse_vd17_vd18.parse_vd17(url_bibliography)
    elif(bid_name == "VD16" or bid_name == "vd16"):
        vd16_complete = bid_id
        vd16_divided = re.split(" ", vd16_complete)       
        url_bibliography = r"http://gateway-bayern.de/VD16+" + vd16_divided[0] + "+" + vd16_divided[1]            
        bibliographic_information_single = books_parsing_bibliographies.parse_vd16(url_bibliography)            
            #url_bibliography = r''
    elif bid_name == "GW":
        gw_number = bid_id.lstrip("0")
        ##Removing leading zeros that are accepted in many cases but not by the ISTC            
        url_bibliography = r'https://data.cerl.org/istc/_search?_format=json&pretty=false&query=reference%3A%22GW ' + gw_number + r'%22&size=10&sort=default&from=0&file=false&orig=true&facet=dimensions&facet=printingcountry&facet=holdingcountry&nofacets=true&mode=default&aggregations=true&style=full'
        bibliographic_information_single = await parse_istc.parse_istc(url_bibliography) 
    elif bid_name  == "ISTC":
        istc_number = bid_id
        url_bibliography = r'https://data.cerl.org/istc/_search?_format=json&pretty=false&query=_id%3A' + istc_number + r'&size=10&sort=default&from=0&file=false&orig=true&facet=Format&facet=Holding%20country&facet=Publication%20country&nofacets=true&mode=default&aggregations=true&style=full'
        bibliographic_information_single = await parse_istc.parse_istc(url_bibliography) 
    # the following options (and perhaps more will have to follow) are only used for libraries such as the BnF that do not regularly give ISTC or GW numbers
    elif bid_name == "Goff":
        url_bibliography = r'https://data.cerl.org/istc/_search?_format=json&pretty=false&query=reference%3A%22Goff ' + bid_id + r'%22&size=10&sort=default&from=0&file=false&orig=true&facet=dimensions&facet=printingcountry&facet=holdingcountry&nofacets=true&mode=default&aggregations=true'
        bibliographic_information_single = await parse_istc.parse_istc(url_bibliography)
        if bibliographic_information_single is None: # Sometimes, ISTC write the Goff number without a hyphen
            bid_id = bid_id.replace("-", "")
            url_bibliography = r'https://data.cerl.org/istc/_search?_format=json&pretty=false&query=reference%3A%22Goff ' + bid_id + r'%22&size=10&sort=default&from=0&file=false&orig=true&facet=dimensions&facet=printingcountry&facet=holdingcountry&nofacets=true&mode=default&aggregations=true&style=full&style=full'
            print("search string without hyphen: ")
            print(url_bibliography)
            bibliographic_information_single = await parse_istc.parse_istc(url_bibliography)
    elif bid_name == "CIBN":
        url_bibliography = r'https://data.cerl.org/istc/_search?_format=json&pretty=false&query=reference%3A%22CIBN ' + bid_id + r'%22&size=10&sort=default&from=0&file=false&orig=true&facet=dimensions&facet=printingcountry&facet=holdingcountry&nofacets=true&mode=default&aggregations=true&style=full'
        bibliographic_information_single = await parse_istc.parse_istc(url_bibliography)
    elif bid_name == "C":
        url_bibliography = r'https://data.cerl.org/istc/_search?_format=json&pretty=false&query=reference%3A%22C ' + bid_id + r'%22&size=10&sort=default&from=0&file=false&orig=true&facet=dimensions&facet=printingcountry&facet=holdingcountry&nofacets=true&mode=default&aggregations=true&style=full'
        bibliographic_information_single = await  parse_istc.parse_istc(url_bibliography)
    elif bid_name == "HC":
        url_bibliography = r'https://data.cerl.org/istc/_search?_format=json&pretty=false&query=reference%3A%22HC ' + bid_id + r'%22&size=10&sort=default&from=0&file=false&orig=true&facet=dimensions&facet=printingcountry&facet=holdingcountry&nofacets=true&mode=default&aggregations=true&style=full'
        bibliographic_information_single = await parse_istc.parse_istc(url_bibliography)
        if bibliographic_information_single is None: # ISTC makes a distinction between "H" (the main part of the work), "HC" (the most common addition) and "HCR" (the appendix), the BnF has them both as Hain-Copinger
            url_bibliography = r'https://data.cerl.org/istc/_search?_format=json&pretty=false&query=reference%3A%22H ' + bid_id + r'%22&size=10&sort=default&from=0&file=false&orig=true&facet=dimensions&facet=printingcountry&facet=holdingcountry&nofacets=true&mode=default&aggregations=true&style=full'
            bibliographic_information_single =  await parse_istc.parse_istc(url_bibliography)
        if bibliographic_information_single is None: # ISTC makes a distinction between "HC" (the main part of the work) and "HCR" (the appendix), the BnF has them both as Hain-Copinger
            url_bibliography = r'https://data.cerl.org/istc/_search?_format=json&pretty=false&query=reference%3A%22HCR ' + bid_id + r'%22&size=10&sort=default&from=0&file=false&orig=true&facet=dimensions&facet=printingcountry&facet=holdingcountry&nofacets=true&mode=default&aggregations=true&style=full'
            bibliographic_information_single = await parse_istc.parse_istc(url_bibliography)       
    elif bid_name == "Pell Ms":
        url_bibliography = r'https://data.cerl.org/istc/_search?_format=json&pretty=false&query=reference%3A%22Pell Ms ' + bid_id + r'%22&size=10&sort=default&from=0&file=false&orig=true&facet=dimensions&facet=printingcountry&facet=holdingcountry&nofacets=true&mode=default&aggregations=true&style=full'
        bibliographic_information_single = await parse_istc.parse_istc(url_bibliography)
    elif bid_name == "Bod-inc":
        url_bibliography = r'https://data.cerl.org/istc/_search?_format=json&pretty=false&query=reference%3A%22Bod-inc ' + bid_id + r'%22&size=10&sort=default&from=0&file=false&orig=true&facet=dimensions&facet=printingcountry&facet=holdingcountry&nofacets=true&mode=default&aggregations=true&style=full'
        bibliographic_information_single = await parse_istc.parse_istc(url_bibliography)
    

    #print(bibliographic_information_single)
    return bibliographic_information_single



@classes.async_func_logger
async def parse_iiif(uri_entered, material) -> classes.Metadata:
    """
    Main iiif manifest parsing routine
    """

# Step 1: Information is collected from the IIIF manifest
#    print("getting manifest from url")
    manifest= await get_external_data.get_web_data_as_json(uri_entered)
    
    if "digitale-sammlungen.de" in uri_entered:
        m = parse_manifests.parse_manifests_bsb(manifest)
    elif "uni-halle.de" in uri_entered:
        m = parse_manifests.parse_manifest_halle(uri_entered)
    elif "staatsbibliothek-berlin" in uri_entered:
        m = parse_manifests.parse_manifest_berlin(uri_entered)
    elif "trin.cam." in uri_entered:
        m = parse_manifests.parse_manifest_cambridge_trinity(uri_entered)
    elif "Parker" in uri_entered:
        m = parse_manifests.parse_manifest_cambridge_corpus(uri_entered)
    elif "thulb.uni-jena" in uri_entered:
        m = parse_manifests.parse_manifest_thulb(uri_entered)
    elif "slub-dresden" in uri_entered:
        m = parse_manifests.parse_manifest_slub(uri_entered)
    elif "ub.uni-leipzig" in uri_entered:
        m = parse_manifests.parse_manifest_leipzig(uri_entered)
    elif "gallica.bnf.fr" in uri_entered:
        m = parse_manifests.parse_manifest_gallica(uri_entered)
    elif "e-codices.ch" in uri_entered:
        m = parse_manifests.parse_manifest_ecodices(uri_entered)
    elif "e-rara.ch" in uri_entered:
        m = parse_manifests.parse_manifest_erara(uri_entered)
    elif "bodleian.ox.ac.uk" in uri_entered:
        m = parse_manifests.parse_manifest_bodleian(uri_entered)
    elif "digi.ub.uni-heidelberg.de" in uri_entered:
        m = parse_manifests.parse_manifest_heidelberg(uri_entered)
    elif "digi.vatlib.it" in uri_entered:
        m = parse_manifests.parse_manifest_vaticana(uri_entered)
    elif "onb.ac.at" in uri_entered:
        m = parse_manifests.parse_manifest_vienna(uri_entered)
    elif "loc.gov" in uri_entered:
        m = parse_manifests.parse_manifest_washington(uri_entered)
    elif "sub.uni-goettingen" in uri_entered:
        m = parse_manifests.parse_manifest_goettingen(uri_entered)
    elif "figgy.princeton.edu" in uri_entered:
        m = parse_manifests.parse_manifest_princeton(uri_entered)
    elif "library.yale.edu" in uri_entered:
        m = parse_manifests.parse_manifest_yale(uri_entered)
    elif "digitalcommonwealth" in uri_entered:
        m = parse_manifests.parse_manifest_boston(uri_entered)
    elif "manchester.ac.uk" in uri_entered:
        m = parse_manifests.parse_manifest_manchester(uri_entered)
    elif "cudl.lib.cam.ac.uk" in uri_entered:
        m = parse_manifests.parse_manifest_cambridge_ul(uri_entered)
    elif "irht.cnrs.fr" in uri_entered:
        m = parse_manifests.parse_manifests_irht(uri_entered)
    elif "ub.uni-frankfurt.de" in uri_entered:
        m = parse_manifests.parse_manifest_frankfurt(uri_entered)
    elif "haab-digital" in uri_entered:
        m = parse_manifests.parse_manifest_weimar(uri_entered)
    elif "dibiki.ub.uni-kiel" in uri_entered:
        m = parse_manifests.parse_manifest_kiel(uri_entered)
    elif "sub.uni-hamburg.de" in uri_entered:
        m = parse_manifests.parse_manifest_hamburg(uri_entered)
    elif "rosdok.uni-rostock.de" in uri_entered:
        m = parse_manifests.parse_manifest_rostock(uri_entered)
    elif "online-service.nuernberg.de" in uri_entered:
        m = parse_manifests.parse_manifest_nuernberg_stb(uri_entered)
    elif "manuscriptorium.com" in uri_entered: # This is a system describing primarily MSS in Bohemian lands, but also some in Austria
        m = parse_manifests.parse_manifest_manuscriptorium(uri_entered)


    m.entity.add_attribute("iiifUrl",uri_entered)
    print("BSP DONE")
    m.entity.add_attribute("material",material)
# Step 2: The bibliographical references in the manifest (in a later development also bibliographical references entered manually) will be parsed, and information from them added.
    await m.save(link_rule=beanie.WriteRules.WRITE)
#    print("getting bibliography")
    for bibliogr_id in m.entity.external_id:
        #print(m.bibliographic_id[step1][1])
        bid_name = bibliogr_id.name
        bid_id = bibliogr_id.external_id
        bibliographic_information_single = await get_bibliographic_data(bid_name, bid_id)


        if bibliographic_information_single != "": #omit appending if nothing came back from the function (this is the case when the record
            #describes a series, not a book)
            m.bibliographic_information.append(bibliographic_information_single)




    # If several bibliographical references are given that refer to the same (e.g., ISTC and GW),
    #  there will be duplicate bibliographical records that should be removed
    # This is a rather awkward way of doing it - but won't do much harm since only in 
    # very rare cases there will be more than 2 references
    if len(m.bibliographic_information) > 1:
        counter1 = 0
#        print("counter1: " + str(counter1))

        while counter1 < len(m.bibliographic_information) -1:
            bibliography_short = m.bibliographic_information[counter1].bibliographic_id[0].uri + m.bibliographic_information[counter1].bibliographic_id[0].name + m.bibliographic_information[counter1].bibliographic_id[0].id
#            print("first record: " + bibliography_short)
            counter2 = counter1 + 1
#            print("counter2: " + str(counter2))
            while counter2 < len(m.bibliographic_information):
                bibliography_short_compare = m.bibliographic_information[counter2].bibliographic_id[0].uri + m.bibliographic_information[counter2].bibliographic_id[0].name + m.bibliographic_information[counter2].bibliographic_id[0].id
#                print("second record: " + bibliography_short_compare)
                if bibliography_short_compare == bibliography_short:
                    m.bibliographic_information.pop(counter2)
#                    print("found identical")
                else:
                    counter2 = counter2 + 1
#                    print("found not identical")
#                    print("counter2 after increment" + str(counter2))
            counter1 = counter1 + 1
#            print("counter1 after increment" + str(counter1))

#    The following lines create - depending on the type of material - 
#    fields for manually entering artist, place, date, and illustrated text. 
#    They will later be copied to the individual Artwork records
#    For manuscripts, there is one making process, for printed books, there are two (design / making of matrix)
#    The third making process for printed books, the printing, does not appear here, since the relevant information
#    will be taken automatically from the bibliographic information. 
#    print("Material: ")
#    print(material)
    if material == "m": # manuscripts
        making_process_blank = classes.MakingProcess()
        making_process_blank.process_number = 1
        making_process_blank.process_type = "Painting"
        person_blank = classes.Entity()
        person_blank.name = ""
#        person_blank.chosen_candidate = 999
        making_process_blank.person = person_blank
        place_blank = classes.Entity()
        place_blank.name = ""
#        place_blank.chosen_candidate = 999
        making_process_blank.place = place_blank
        date_blank = classes.DateImport()
        date_blank.datestring_raw = ""
        making_process_blank.date = date_blank

        m.making_processes.append(making_process_blank)

    if material == "b": #Printed books
        making_process_blank = classes.MakingProcess()
        making_process_blank.process_number = 1
        making_process_blank.process_type = "Design"
        person_blank = classes.Entity()
        person_blank.name = ""
#        person_blank.chosen_candidate = 999
        making_process_blank.person = person_blank
        place_blank = classes.Entity()
        place_blank.name = ""
#        place_blank.chosen_candidate = 999
        making_process_blank.place = place_blank
        date_blank = classes.DateImport()
        date_blank.datestring_raw = ""
        making_process_blank.date = date_blank
        m.making_processes.append(making_process_blank)
        making_process_blank = classes.MakingProcess()
        making_process_blank.process_number = 2
        making_process_blank.process_type = "Production of Matrix"
        person_blank = classes.Entity()
#        person_blank.chosen_candidate = 999
        person_blank.name = ""
        making_process_blank.person = person_blank
        place_blank = classes.Entity()
        place_blank.name = ""
#        place_blank.chosen_candidate = 999
        making_process_blank.place = place_blank
        date_blank = classes.DateImport()
        date_blank.datestring_raw = ""
        making_process_blank.date = date_blank
        m.making_processes.append(making_process_blank)

    if m.bibliographic_information:
        if m.bibliographic_information[0]:
            #print("m.bibliographic_information: ")
            #print(m.bibliographic_information)
            for person in m.bibliographic_information[0].persons:
                person = await parse_gnd.identify_person(person)
            #  m.bibliographic_information[0].persons[person_counter] = person
            # for organisation in m.bibliographic_information[0].organisations:
            #     organisation = parse_gnd.identify_organisation(organisation)
            # for place in m.bibliographic_information[0].places:
            #     place = parse_gnd.identify_place(place)
    # for repository in m.repository:
    #     repository = parse_gnd.identify_organisation(repository)
        # I had to define 'repository' as a list because Pydantic forced me to do so,
        #  but it only has one member.
        # repository.role = "col"
        # Normally, this role depends on the bibliographical data -
        # in this case, it has to be set here.

    # m.id=generate()
#    print("List of places to be sent to FE")
#    print(m.bibliographic_information[0].places)
#    print(m.model_dump())

    return m


@classes.async_func_logger
async def supply_bibliographic_information(additional_bid):
    """
This function is needed if an IIIF manifest does not include a bibliographic reference.
If a bibliographic reference is known to the editor, he can add it in a second step.
This function parses it and sends the results to the function bibliography_select, and returns the resulting bibliographic data to main.py
    """
    bid_pattern = r'([A-Za-z]{2,4}[\w]{0,2})( )(.*)'
    bid_divided = re.match(bid_pattern, additional_bid)
    bid_name = bid_divided[1]
    bid_id = bid_divided[3]
    bibliographic_information_single = await get_bibliographic_data(bid_name, bid_id)
    for person in bibliographic_information_single.persons:
        person = await parse_gnd.identify_person(person)
    for organisation in bibliographic_information_single.organisations:
        organisation = parse_gnd.identify_organisation(organisation)
    for place in bibliographic_information_single.places:
        place = parse_gnd.identify_place(place)

    return bibliographic_information_single
