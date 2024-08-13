import asyncio
import re
import requests
from classes import *

url_replacement = {" " : "%20", "ä" : "%C3%A4", "ö" : "%C3%B6", "ü" : "%C3%BC", "Ä" : "%C3%84", "Ö" : "%C3%96", "Ü": "%C3%9C", \
                   "ß" : r"%C3%9F", "(" : "", ")" : "", "," : "",  "." : "" , "-" : "", \
                    "â": "%C3%A2", "ê" : "%C3%AA", "î" : "%C3%AE", "ô": "%C3%B4", "û" : "%C3%BB", "&" : "", \
                        "á" : "%C3%A1", "é" : "%C3%A9", "í" : "%C3%AD", "ó" : "%C3%B3", "ú": "%C3%BA", \
                        "à" : "%C3%A0", "è" : "%C3%A8", "ì": "%C3%AC", "ò" : "%C3%B2", "ù" : "%C3%B9", \
                        "Č" : "%C4%8C", "č" : "%C4%8D", "Ř": "%C5%98", "ř" : "%C5%99", "Š" : "%C5%A0", "š" : "%C5%A1"}  



async def artist_record_parsing(authority_url):
    print("arrived in artists_parsing")
    pe = Person_import()
    url = requests.get(authority_url)
    artist_record = url.json()
    external_id = External_id()
    external_id.uri = authority_url
    external_id.name = "ULAN"
    external_id.id = authority_url[29:-5]
    pe.external_id.append(external_id)
    pe.name_preferred = artist_record["_label"]
    connections_list = []
    if "identified_by" in artist_record:
        name_variant_list = []       
        for variant in artist_record["identified_by"]:
            name_variant = variant["content"]
            name_variant_list.append(name_variant)
        if len(name_variant_list) > 1: 
            # The first name in the list is name_preferred. Hence, there are only variants if there are at least two names, and I have to remove the first
            name_variant_list = name_variant_list[1:]
            pe.name_variant = name_variant_list
    if "classified_as" in artist_record:
        for property in artist_record["classified_as"]:
            if property["id"] == "http://vocab.getty.edu/aat/300189559":
                pe.sex = "male"
            if property["id"] == "http://vocab.getty.edu/aat/300189557":
                pe.sex = "female"
    if "referred_to_by" in artist_record:
        date_pattern = r'([^,]*),(.*)'
        for property in artist_record["referred_to_by"]:
            date_raw = property["content"]
            if "," in date_raw:
                date_raw_divided = re.match(date_pattern, date_raw)
                date = date_raw_divided[2].strip()
                pe.dates_from_source.append(date)
    
    if "la:related_from_by" in artist_record:
        connections_list = []
        if type((artist_record["la:related_from_by"])) is dict: # only one entry
            connections_list.append(artist_record["la:related_from_by"])           
        else:
            for connection in artist_record["la:related_from_by"]:
                connections_list.append(connection)
        for connection in connections_list:
            conn_ent = Connected_entity()
            conn_ent.external_id = []
            conn_id = External_id()
            id_raw = connection["la:relates_to"]["id"]
            conn_id.uri = id_raw
            if "ulan" in id_raw: #should normally happen, but maybe they have some strange connections
                conn_id.name = "ULAN"
                conn_id.id = id_raw[29:]
                conn_ent.external_id.append(conn_id)
            if type(connection["classified_as"][0]) is str:
                conn_ent.connection_type = connection["classified_as"][0]
            else: 
                conn_ent.connection_type = connection["classified_as"][0]["id"]
            
            match conn_ent.connection_type:
                case "http://vocab.getty.edu/ulan/relationships/1000":                
                    conn_ent.connection_comment = "related to"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1003":                
                    conn_ent.connection_comment = "associated with"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1005":                
                    conn_ent.connection_comment = "possibly identified with"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1006":                
                    conn_ent.connection_comment = "formerly identified with"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1007":                
                    conn_ent.connection_comment = "distinguished from"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1008":                
                    conn_ent.connection_comment = "meaning overlaps with"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1101":                
                    conn_ent.connection_comment = "was teacher of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1102":                
                    conn_ent.connection_comment = "was student of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1105":                
                    conn_ent.connection_comment = "was apprentice of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1106":                
                    conn_ent.connection_comment = "apprentice was"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1107":                
                    conn_ent.connection_comment = "influenced"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1108":                
                    conn_ent.connection_comment = "influenced by"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1111":                
                    conn_ent.connection_comment = "was master of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1112":                
                    conn_ent.connection_comment = "master was"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1113":                
                    conn_ent.connection_comment = "fellow student of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1201":                
                    conn_ent.connection_comment = "was patron of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1202":                
                    conn_ent.connection_comment = "patron was"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1203":                
                    conn_ent.connection_comment = "was donor of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1204":                
                    conn_ent.connection_comment = "donor was"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1205":                
                    conn_ent.connection_comment = "client of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1206":                
                    conn_ent.connection_comment = "client was"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1211":                
                    conn_ent.connection_comment = "artist to"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1212":                
                    conn_ent.connection_comment = "artist was"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1213":                
                    conn_ent.connection_comment = "court artist to"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1214":                
                    conn_ent.connection_comment = "court artist was"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1217":                
                    conn_ent.connection_comment = "employee of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1218":                
                    conn_ent.connection_comment = "employee was"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1221":                
                    conn_ent.connection_comment = "appointed by"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1222":                
                    conn_ent.connection_comment = "appointee of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1223":                
                    conn_ent.connection_comment = "crowned by"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1224":                
                    conn_ent.connection_comment = "crowned"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1301":                
                    conn_ent.connection_comment = "colleague of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1302":                
                    conn_ent.connection_comment = "associate of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1303":                
                    conn_ent.connection_comment = "collaborated with"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1305":                
                    conn_ent.connection_comment = "worked with"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1306":                
                    conn_ent.connection_comment = "performed with"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1307":                
                    conn_ent.connection_comment = "assistant of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1308":                
                    conn_ent.connection_comment = "assisted by"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1309":                
                    conn_ent.connection_comment = "advisor of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1311":                
                    conn_ent.connection_comment = "partner of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1315":                
                    conn_ent.connection_comment = "principal of"
                    conn_ent.connection_type = "organisation"
                case "http://vocab.getty.edu/ulan/relationships/1317":                
                    conn_ent.connection_comment = "member of"
                    conn_ent.connection_type = "organisation"
                case "http://vocab.getty.edu/ulan/relationships/1321":                
                    conn_ent.connection_comment = "school of"
                    conn_ent.connection_type = "organisation"
                

                # 1313/1314 partner (in firm) not included
                # 1318 member (of corporation) was > for orgs
                # 1322 school was für > for orgs
                # 1411/1412 successor of / predecessor of, only for organisations
                # 1413 administration overlaps brauche ich wohl nicht
                # 1414 join venture brauche ich wohl nicht
                # 1421/1422 founded by / founded (für organisationen auf beiden Seiten) wohl nicht
                # 1544 significant partner brauche ich wohl nicht


                case "http://vocab.getty.edu/ulan/relationships/1331":                
                    conn_ent.connection_comment = "worked with"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1332":                
                    conn_ent.connection_comment = "worker was"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1500":                
                    conn_ent.connection_comment = "related to"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1501":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "brother of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "sister of"
                    else:
                        conn_ent.connection_comment = "brother or sister of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1511":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "son of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "daughter of"
                    else:
                        conn_ent.connection_comment = "son or daughter of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1512":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "father of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "mother of"
                    else:
                        conn_ent.connection_comment = "father or mother of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1513":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "grandson of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "granddaughter of"
                    else:
                        conn_ent.connection_comment = "grandchild of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1514":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "grandfather of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "grandmother of"
                    else:
                        conn_ent.connection_comment = "grandfather or grandmother of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1515":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "great-grandfather of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "great-grandmother of"
                    else:
                        conn_ent.connection_comment = "great-grandfather or great-grandmother off"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1516":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "great-grandson of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "great-granddaughter of"
                    else:
                        conn_ent.connection_comment = "great-grandchild of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1521":                
                    conn_ent.connection_comment = "cousin of"
                case "http://vocab.getty.edu/ulan/relationships/1531":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "nephew of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "niece of"
                    else:
                        conn_ent.connection_comment = "nephew or niece of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1532":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "uncle of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "aunt of"
                    else:
                        conn_ent.connection_comment = "uncle or aunt of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1541":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "husband of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "wife of"
                    else:
                        conn_ent.connection_comment = "husband or wife of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1542":                
                    conn_ent.connection_comment = "consort of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1543":                
                    conn_ent.connection_comment = "consort was"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1547":                
                    conn_ent.connection_comment = "romantic partner of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1548":                
                    conn_ent.connection_comment = "domestic partner of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1550":                
                    conn_ent.connection_comment = "relative by marriage of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1551":
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "brother-in-law of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "sister-in-law of"
                    else:
                        conn_ent.connection_comment = "brother or sister-in-law of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1552":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "father-in-law of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "mother-in-law of"
                    else:
                        conn_ent.connection_comment = "father or mother-in-law of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1553":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "son-in-law of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "daughter-in-law of"
                    else:
                        conn_ent.connection_comment = "son or daughter-in-law of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1554":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "adoptive father of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "adoptive mother of"
                    else:
                        conn_ent.connection_comment = "adoptive father or mother of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1555":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "adopted son of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "adopted daughter of"
                    else:
                        conn_ent.connection_comment = "adopted son or daughter of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1556":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "half-brother of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "half-sister of"
                    else:
                        conn_ent.connection_comment = "half-brother or half-sister of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1557":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "step-brother of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "step-sister of"
                    else:
                        conn_ent.connection_comment = "step-brother or step-sister of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1561":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "step-son of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "step-daughter of"
                    else:
                        conn_ent.connection_comment = "step-son or step-daughter of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1562":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "step-father of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "step-mother of"
                    else:
                        conn_ent.connection_comment = "step-father or step-mother of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1571":                
                    conn_ent.connection_comment = "guardian of"   
                case "http://vocab.getty.edu/ulan/relationships/1573":                
                    conn_ent.connection_comment = "ward of"   
                case "http://vocab.getty.edu/ulan/relationships/1574":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "godfather of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "godmother of"
                    else:
                        conn_ent.connection_comment = "godfather or godmother of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1575":                
                    if pe.sex == "male":                                        
                        conn_ent.connection_comment = "godson of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "goddaughter of"
                    else:
                        conn_ent.connection_comment = "godson or goddaughter of"
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1581":                
                    conn_ent.connection_comment = "descendant of"   
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1590":                
                    conn_ent.connection_comment = "possibly related to"   
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/2550":                
                    conn_ent.connection_comment = "friend of"   
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/2576":                
                    conn_ent.connection_comment = "patron of"   
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/2577":                
                    conn_ent.connection_comment = "patron was"   
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/1573":                
                    conn_ent.connection_comment = "ward of"   
                    conn_ent.connection_type = "person"
                case "http://vocab.getty.edu/ulan/relationships/2572":                
                    conn_ent.connection_comment = "founder of"   
                    conn_ent.connection_type = "organisation"
                case "http://vocab.getty.edu/ulan/relationships/2574":                
                    conn_ent.connection_comment = "director of"   
                    conn_ent.connection_type = "organisation"
                case "http://vocab.getty.edu/ulan/relationships/2581":                
                    conn_ent.connection_comment = "administrator of"   
                    conn_ent.connection_type = "organisation"
                case "http://vocab.getty.edu/ulan/relationships/2674":                
                    conn_ent.connection_comment = "professor at"   
                    conn_ent.connection_type = "organisation"
                case "http://vocab.getty.edu/ulan/relationships/2696":                
                    conn_ent.connection_comment = "leader of"   
                    conn_ent.connection_type = "organisation"
                case "http://vocab.getty.edu/ulan/relationships/2778":                
                    conn_ent.connection_comment = "owner of"   
                    conn_ent.connection_type = "organisation"
                case "http://vocab.getty.edu/ulan/relationships/2828":                
                    conn_ent.connection_comment = "student at"   
                    conn_ent.connection_type = "organisation"




                # 2573 founded by > for organisations
                # 2575 directed by [i.e., having as director] > for organisation
                # 2578 / 2579 trustee of / trustee was > for organisation, but probably not needed
                # 22582 administrated by > for orgs
                # 2583/2584 chairman / chaired by > probably not needed
                # 2650/2651: publisher was / publisher of (person > org > is this needed?)
                # 2675: professor was > for orgs
                # 2677: teacher was > for orgs
                # 2693: president was > for orgs
                # 2697: leader was > for orgs
                # 2779: owned by > for orgs
                # 2781/2782: dedicatee of , e.g. Rodin > Musée Rodin > das braucht man doch nicht??
                # 2794/2795: representative of / representative was > not needed?
                # 2829: student was > for orgs
                # 2840/2841: Performer with / performer was > not needed



            if conn_ent.connection_type == "person": 
                pe.connected_persons.append(conn_ent)
            if conn_ent.connection_type == "organisation": 
                pe.connected_organisations.append(conn_ent)
                # I could not test the connected organisations since they apparently used very rarely
          
        """Annoyingly, the timespan of the connection does not appear in the json file but only in the rdf and nt files. So, one has to add it later for the selected person only """
    if "born" in artist_record:
        if "took_place_at" in artist_record["born"]:
            if artist_record["born"]["took_place_at"][0]:
                for place_raw in artist_record["born"]["took_place_at"]:
                    conn_place = Connected_entity()
                    conn_place.name = place_raw["_label"]
                    conn_place.connection_type = "ortg"
                    place_id_list = []
                    place_id = External_id()
                    place_id.uri = place_raw["id"]
                    place_id.id = place_id.uri[27:]
                    place_id.name = "tgn"
                    place_id_list.append(place_id)
                    pe.connected_locations.append(conn_place)
    if "died" in artist_record:
        if "took_place_at" in artist_record["died"]:
            if artist_record["died"]["took_place_at"][0]:
                for place_raw in artist_record["died"]["took_place_at"]: # in case several alternative places are given
                    conn_place = Connected_entity()
                    conn_place.name = place_raw["_label"]
                    conn_place.connection_type = "orts"
                    place_id_list = []
                    place_id = External_id()
                    place_id.uri = place_raw["id"]
                    place_id.id = place_id.uri[27:]
                    place_id.name = "tgn"
                    place_id_list.append(place_id)
                    pe.connected_locations.append(conn_place)
    if "carried_out" in artist_record:
        print("carried_out found")
        for activity in artist_record["carried_out"]:
            print(activity)
            print(activity["classified_as"][0]["id"])
            if activity["classified_as"][0]["id"] == "http://vocab.getty.edu/aat/300393177":
                place_list = activity["took_place_at"]
                for place_raw in place_list: # I have the feeling, that there is an 'activity' record for every place, but perhaps there may be also sometimes two places linked to one 'activity' record
                    print("place of activity found")
                    print(place_raw)
                    conn_place = Connected_entity()
                    conn_place.name = place_raw["_label"]
                    conn_place.connection_type = "ortw"
                    place_id_list = []
                    place_id = External_id()
                    place_id.uri = place_raw["id"]
                    place_id.id = place_id.uri[27:]
                    place_id.name = "tgn"
                    place_id_list.append(place_id)
                    pe.connected_locations.append(conn_place)
    # attention: ULAN defines any number of places of activity. I will need one and only one place defined as preferred place. 
    # thus: I need to introduce a function that makes the editor choose one place if there are several, and enter one if there are none. 


                




        


    print(pe)








    return pe





async def artist_name_parsing(person):
    authority_url = r'https://vocab.getty.edu/sparql.json?query=select+distinct+%3Fartist_id+%7B%0A+%7B%3FSubject+luc%3Aterm+%22' + \
    person.name + r'%22%3B+skos%3AinScheme+ulan%3A+%3B+a+%3Ftyp%3B+gvp%3AprefLabelGVP+%5Bxl%3AliteralForm+%3FTerm%5D%7D'+ \
    r'+union+%7B%3FSubject+luc%3Aterm+%22' + person.name + r'%22%3B+skos%3AinScheme+ulan%3A+%3B+a+%3Ftyp%3B+xl%3AaltLabel+%5Bxl%3AliteralForm+%3FTerm%5D%7D%0A+' + \
    r'filter+%28regex%28%3FTerm%2C%22' + person.name + r'%22%2C%22i%22%29%29%0A+%3Ftyp+rdfs%3AsubClassOf+gvp%3ASubject%3B+rdfs%3Alabel+' + \
    r'%3FType.%0A+filter+%28%3Ftyp+%21%3D+gvp%3ASubject%29+%0A+optional+%7B%3FSubject+gvp%3AagentTypePreferred+%5Bgvp%3AprefLabelGVP+'  + \
    r'%5Bxl%3AliteralForm+%3FType2%5D%5D%7D%0A+filter+%28%3FType2+%3D+%22artists+%28visual+artists%29%22%40en%29+%0A+optional+' + \
    r'%7B%3FSubject+dc%3Aidentifier+%3Fartist_id%7D%7D%0AORDER+BY+%28fn%3Alower-case%28str%28%3FTerm%29%29%29%0A%0A&toc=Finding_Subjects&implicit=true&equivalent=false&_form=%2FqueriesF'
    print(authority_url)
    ulan_list_raw = requests.get(authority_url)
    ulan_list = ulan_list_raw.json()
    artist_id_list = []
    authority_url_list = []
    if "results" in ulan_list:
        list_results = ulan_list["results"]
        if "bindings" in list_results:
            bindings = list_results["bindings"]
            for artist in bindings:
                artist_id = artist["artist_id"]["value"]
                artist_authority_url = r'https://vocab.getty.edu/ulan/' + artist_id + r'.json'
                artist_authority_url_function = "artist_record_parsing(" + artist_authority_url + ")"
                authority_url_list.append(artist_authority_url_function)
            print(authority_url_list)
                #print(artist_authority_url)
            candidate_list = await asyncio.gather(artist_record_parsing("https://vocab.getty.edu/ulan/500392228.json"), artist_record_parsing("https://vocab.getty.edu/ulan/500381287.json"), artist_record_parsing("https://vocab.getty.edu/ulan/500082742.json"), artist_record_parsing("https://vocab.getty.edu/ulan/500110947.json"))
                #authority_url_list.append(artist_authority_url)
            print(candidate_list)
                #person.potential_candidates.append(candidate)

    
    # This works slightly different than with the searches for authors etc.: In these cases, I search in the GND and get back one file
    # with a list of results I then  parse. With ULAN, the above query leads to a list of IDs of potential candidates, and I have to 
    # run the parser for each of them. 
    

    return person

async def main():
    artist_name_search = input("Artist: ")
    for old, new in url_replacement.items():
        artist_name_search = artist_name_search.replace(old, new)
    person = Person() # This later come from the main metadata section
    person.name = artist_name_search.strip()
    print("now doing sub-routine")
    x = await artist_name_parsing(person)
    return person


def datatest():
    with open(r"C:\Users\berth\bpf_files\ulan_dates_test.txt", "r+", encoding="utf-8") as f:
#        for line in f:
        counter = 1
        for counter in range(1,500000):
            datestring = f.readline()
            if datestring[-1:] == "\n":
                datestring = datestring[:-1]
            if datestring is None or datestring == "":
                continue
            y = artist_date_parsing(datestring)
            #print("Date as returned: ")
            #print(x)
            x = ""
            if len(y) > 0:
                x = y[0]
            if not x:
                x = ""
            datestring_new = "#" + datestring + "$" + x
            print("Date as to be written: ")
            print(datestring_new)
            datestring_new = datestring_new + "\n"

            with open(r"C:\Users\berth\bpf_files\ulan_dates_test_done.txt", "a") as g:
                g.writelines(datestring_new) 


if __name__ == "__main__":
    x = asyncio.run(main())
#    date_raw = input("date: ")
#    x = artist_date_parsing(date_raw)
#    x = datatest()
    print(x)