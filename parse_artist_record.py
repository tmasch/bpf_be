import classes
from parse_date import parse_artist_date


import ast


@classes.func_logger
def parse_artist_record(artist_record):
    """
Currently, this file is also used if an organisation is found at the search for artists. 
One needs a separate function for parsing organisations. 
    """
    print("arrived in artists_parsing")
    pe = classes.PersonImport()
    name_preferred_inversed = ""
    name_variant_preview = ""
    date_preview = ""
    ortg_preview = ""
    orts_preview = ""
    ortw_preview = ""
    print("artist_record as it arrives in artist_record_parsing")
    print("type of artist_record: ")
    print(type(artist_record))
    print(artist_record)

    artist_record = ast.literal_eval(artist_record)
    print("type of artist_record after transformation: ")
    print(type(artist_record))
    #url = requests.get(authority_url)
    #artist_record = artist_record.json()
    external_id = classes.ExternalId()
    external_id.uri = artist_record["id"]
    external_id.name = "ULAN"
    external_id.id = external_id.uri[28:]
    pe.external_id.append(external_id)
    pe.name_preferred = artist_record["_label"]
    name_preferred_split = pe.name_preferred.split(",", maxsplit = 1) # One of the variant names is normally just the preferred name inversed, e.g. "John Smith" instead of "Smith, John"
    if len(name_preferred_split) == 2: # excluding names without a comma, e.g. of non-Western artists
        name_preferred_inversed = name_preferred_split[1].strip() + " " + name_preferred_split[0]
    connections_list = []
    if "identified_by" in artist_record:
        name_variant_list = []
        for variant in artist_record["identified_by"]:
            if variant["type"] == "Name" and variant["content"] != name_preferred_inversed: # if the inversed versions of the names are ignored
                name_variant = variant["content"]
                name_variant_list.append(name_variant)
        if len(name_variant_list) > 1:
            # The first name in the list is name_preferred. Hence, there are only variants if there are at least two names, and I have to remove the first
            name_variant_list = name_variant_list[1:]
            pe.name_variant = name_variant_list
        if pe.name_variant:
            name_variant_preview = ", also called: "
            for variant in pe.name_variant:
                name_variant_preview = name_variant_preview + variant + "; "
            name_variant_preview = name_variant_preview[:-2]

    if "classified_as" in artist_record:
        for artist_property in artist_record["classified_as"]:
            if artist_property["id"] == "http://vocab.getty.edu/aat/300189559":
                pe.sex = "male"
            if artist_property["id"] == "http://vocab.getty.edu/aat/300189557":
                pe.sex = "female"
    if "referred_to_by" in artist_record:
        date_raw = ""
        for artist_property in artist_record["referred_to_by"]:
            biography = artist_property["content"]
            if "," in biography:
                biography_divided = biography.split(",")
                for biography_statement in biography_divided:
                    if any(character.isdigit() for character in biography_statement): # if there is a section with no digits (e.g. ", active in Spain"), it is deleted
                        date_raw = date_raw + biography_statement + ", "
                date_raw = date_raw[:-2].strip()
            date_from_source = classes.DateImport()
            date_from_source.datestring_raw = date_raw
            pe.dates_from_source.append(date_from_source)
            date_processed = parse_artist_date(date_raw)
            pe.datestring = date_processed[0]
            pe.date_start = (date_processed[1], 1, 1)
            pe.date_end = (date_processed[2], 12, 31)
            pe.date_aspect = date_processed[3]
            if pe.datestring:
                date_preview = " (" + pe.datestring + ")"

    if "la:related_from_by" in artist_record:
        connections_list = []
        if isinstance((artist_record["la:related_from_by"]), dict): # only one entry
            connections_list.append(artist_record["la:related_from_by"])
        else:
            for connection in artist_record["la:related_from_by"]:
                connections_list.append(connection)
        for connection in connections_list:
            conn_ent = classes.ConnectedEntity()
            conn_ent.external_id = []
            conn_id = classes.ExternalId()
            id_raw = connection["la:relates_to"]["id"]
            conn_id.uri = id_raw
            if "ulan" in id_raw: #should normally happen, but maybe they have some strange connections
                conn_id.name = "ULAN"
                conn_id.id = id_raw[29:]
                conn_ent.external_id.append(conn_id)
            if isinstance(connection["classified_as"][0], str):
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
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1006":
                    conn_ent.connection_comment = "formerly identified with"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1007":
                    conn_ent.connection_comment = "distinguished from"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1008":
                    conn_ent.connection_comment = "meaning overlaps with"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1101":
                    conn_ent.connection_comment = "teacher of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1102":
                    conn_ent.connection_comment = "student of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1105":
                    conn_ent.connection_comment = "apprentice of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1106":
                    conn_ent.connection_comment = "apprentice was"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1107":
                    conn_ent.connection_comment = "influenced"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1108":
                    conn_ent.connection_comment = "influenced by"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1111":
                    conn_ent.connection_comment = "master of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1112":
                    conn_ent.connection_comment = "master was"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1113":
                    conn_ent.connection_comment = "fellow student of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1201":
                    conn_ent.connection_comment = "patron of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1202":
                    conn_ent.connection_comment = "patron was"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1203":
                    conn_ent.connection_comment = "donor of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1204":
                    conn_ent.connection_comment = "donor was"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1205":
                    conn_ent.connection_comment = "client of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1206":
                    conn_ent.connection_comment = "client was"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1211":
                    conn_ent.connection_comment = "artist to"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1212":
                    conn_ent.connection_comment = "artist was"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1213":
                    conn_ent.connection_comment = "court artist to"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1214":
                    conn_ent.connection_comment = "court artist was"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1217":
                    conn_ent.connection_comment = "employee of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1218":
                    conn_ent.connection_comment = "employee was"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1221":
                    conn_ent.connection_comment = "appointed by"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1222":
                    conn_ent.connection_comment = "appointee of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1223":
                    conn_ent.connection_comment = "crowned by"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1224":
                    conn_ent.connection_comment = "crowned"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1301":
                    conn_ent.connection_comment = "colleague of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1302":
                    conn_ent.connection_comment = "associate of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1303":
                    conn_ent.connection_comment = "collaborated with"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1305":
                    conn_ent.connection_comment = "worked with"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1306":
                    conn_ent.connection_comment = "performed with"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1307":
                    conn_ent.connection_comment = "assistant of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1308":
                    conn_ent.connection_comment = "assisted by"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1309":
                    conn_ent.connection_comment = "advisor of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1311":
                    conn_ent.connection_comment = "partner of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1315":
                    conn_ent.connection_comment = "principal of"
                    conn_ent.connection_type= "organisation"
                case "http://vocab.getty.edu/ulan/relationships/1317":
                    conn_ent.connection_comment = "member of"
                    conn_ent.connection_type= "organisation"
                case "http://vocab.getty.edu/ulan/relationships/1321":
                    conn_ent.connection_comment = "school of"
                    conn_ent.connection_type= "organisation"


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
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1332":
                    conn_ent.connection_comment = "worker was"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1500":
                    conn_ent.connection_comment = "related to"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1501":
                    if pe.sex == "male":
                        conn_ent.connection_comment = "brother of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "sister of"
                    else:
                        conn_ent.connection_comment = "brother or sister of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1511":
                    if pe.sex == "male":
                        conn_ent.connection_comment = "son of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "daughter of"
                    else:
                        conn_ent.connection_comment = "son or daughter of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1512":
                    if pe.sex == "male":
                        conn_ent.connection_comment = "father of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "mother of"
                    else:
                        conn_ent.connection_comment = "father or mother of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1513":
                    if pe.sex == "male":
                        conn_ent.connection_comment = "grandson of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "granddaughter of"
                    else:
                        conn_ent.connection_comment = "grandchild of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1514":
                    if pe.sex == "male":
                        conn_ent.connection_comment = "grandfather of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "grandmother of"
                    else:
                        conn_ent.connection_comment = "grandparent of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1515":
                    if pe.sex == "male":
                        conn_ent.connection_comment = "great-grandfather of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "great-grandmother of"
                    else:
                        conn_ent.connection_comment = "great-grandfather or great-grandmother off"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1516":
                    if pe.sex == "male":
                        conn_ent.connection_comment = "great-grandson of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "great-granddaughter of"
                    else:
                        conn_ent.connection_comment = "great-grandchild of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1521":
                    conn_ent.connection_comment = "cousin of"
                case "http://vocab.getty.edu/ulan/relationships/1531":
                    if pe.sex == "male":
                        conn_ent.connection_comment = "nephew of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "niece of"
                    else:
                        conn_ent.connection_comment = "nephew or niece of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1532":
                    if pe.sex == "male":
                        conn_ent.connection_comment = "uncle of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "aunt of"
                    else:
                        conn_ent.connection_comment = "uncle or aunt of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1541":
                    if pe.sex == "male":
                        conn_ent.connection_comment = "husband of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "wife of"
                    else:
                        conn_ent.connection_comment = "husband or wife of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1542":
                    conn_ent.connection_comment = "consort of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1543":
                    conn_ent.connection_comment = "consort was"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1547":
                    conn_ent.connection_comment = "romantic partner of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1548":
                    conn_ent.connection_comment = "domestic partner of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1550":
                    conn_ent.connection_comment = "relative by marriage of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1551":
                    if pe.sex == "male":
                        conn_ent.connection_comment = "brother-in-law of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "sister-in-law of"
                    else:
                        conn_ent.connection_comment = "brother or sister-in-law of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1552":
                    if pe.sex == "male":
                        conn_ent.connection_comment = "father-in-law of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "mother-in-law of"
                    else:
                        conn_ent.connection_comment = "father or mother-in-law of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1553":
                    if pe.sex == "male":
                        conn_ent.connection_comment = "son-in-law of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "daughter-in-law of"
                    else:
                        conn_ent.connection_comment = "son or daughter-in-law of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1554":
                    if pe.sex == "male":
                        conn_ent.connection_comment = "adoptive father of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "adoptive mother of"
                    else:
                        conn_ent.connection_comment = "adoptive father or mother of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1555":
                    if pe.sex == "male":
                        conn_ent.connection_comment = "adopted son of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "adopted daughter of"
                    else:
                        conn_ent.connection_comment = "adopted son or daughter of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1556":
                    if pe.sex == "male":
                        conn_ent.connection_comment = "half-brother of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "half-sister of"
                    else:
                        conn_ent.connection_comment = "half-brother or half-sister of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1557":
                    if pe.sex == "male":
                        conn_ent.connection_comment = "step-brother of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "step-sister of"
                    else:
                        conn_ent.connection_comment = "step-brother or step-sister of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1561":
                    if pe.sex == "male":
                        conn_ent.connection_comment = "step-son of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "step-daughter of"
                    else:
                        conn_ent.connection_comment = "step-son or step-daughter of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1562":
                    if pe.sex == "male":
                        conn_ent.connection_comment = "step-father of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "step-mother of"
                    else:
                        conn_ent.connection_comment = "step-father or step-mother of"
                    conn_ent.connection_type= "person"
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
                        conn_ent.connection_comment = "godparent of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1575":
                    if pe.sex == "male":
                        conn_ent.connection_comment = "godson of"
                    elif pe.sex == "female":
                        conn_ent.connection_comment = "goddaughter of"
                    else:
                        conn_ent.connection_comment = "godchild of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1581":
                    conn_ent.connection_comment = "descendant of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1590":
                    conn_ent.connection_comment = "possibly related to"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/2550":
                    conn_ent.connection_comment = "friend of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/2576":
                    conn_ent.connection_comment = "patron of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/2577":
                    conn_ent.connection_comment = "patron was"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/1573":
                    conn_ent.connection_comment = "ward of"
                    conn_ent.connection_type= "person"
                case "http://vocab.getty.edu/ulan/relationships/2572":
                    conn_ent.connection_comment = "founder of"
                    conn_ent.connection_type= "organisation"
                case "http://vocab.getty.edu/ulan/relationships/2574":
                    conn_ent.connection_comment = "director of"
                    conn_ent.connection_type= "organisation"
                case "http://vocab.getty.edu/ulan/relationships/2581":
                    conn_ent.connection_comment = "administrator of"
                    conn_ent.connection_type= "organisation"
                case "http://vocab.getty.edu/ulan/relationships/2674":
                    conn_ent.connection_comment = "professor at"
                    conn_ent.connection_type= "organisation"
                case "http://vocab.getty.edu/ulan/relationships/2696":
                    conn_ent.connection_comment = "leader of"
                    conn_ent.connection_type= "organisation"
                case "http://vocab.getty.edu/ulan/relationships/2778":
                    conn_ent.connection_comment = "owner of"
                    conn_ent.connection_type= "organisation"
                case "http://vocab.getty.edu/ulan/relationships/2828":
                    conn_ent.connection_comment = "student at"
                    conn_ent.connection_type= "organisation"




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
                conn_ent.connection_type = "ulan"
                pe.connected_persons.append(conn_ent)
            if conn_ent.connection_type == "organisation":
                conn_ent.connection_type = "ulan"
                pe.connected_organisations.append(conn_ent)
                # I could not test the connected organisations since they apparently used very rarely

        #Annoyingly, the timespan of the connection does not appear in the json file but only in the rdf and nt files. 
        # So, one has to add it later for the selected person only 
    if "born" in artist_record:
        if "took_place_at" in artist_record["born"]:
            if artist_record["born"]["took_place_at"][0]:
                for place_raw in artist_record["born"]["took_place_at"]:
                    conn_place = classes.ConnectedEntity()
                    conn_place.name = place_raw["_label"]
                    conn_place.connection_type = "ortg"
                    place_id_list = []
                    place_id = classes.ExternalId()
                    place_id.uri = place_raw["id"]
                    place_id.id = place_id.uri[27:]
                    place_id.name = "tgn"
                    place_id_list.append(place_id)
                    pe.connected_locations.append(conn_place)
                    ortg_preview = ", born in " + conn_place.name
    if "died" in artist_record:
        if "took_place_at" in artist_record["died"]:
            if artist_record["died"]["took_place_at"][0]:
                for place_raw in artist_record["died"]["took_place_at"]: # in case several alternative places are given
                    conn_place = classes.ConnectedEntity()
                    conn_place.name = place_raw["_label"]
                    conn_place.connection_type = "orts"
                    place_id_list = []
                    place_id = classes.ExternalId()
                    place_id.uri = place_raw["id"]
                    place_id.id = place_id.uri[27:]
                    place_id.name = "tgn"
                    place_id_list.append(place_id)
                    conn_place.external_id = place_id_list
                    pe.connected_locations.append(conn_place)
                    orts_preview = ", died in " + conn_place.name
    if "carried_out" in artist_record:
        #print("carried_out found")
        for activity in artist_record["carried_out"]:
        #    print(activity)
        #    print(activity["classified_as"][0]["id"])
            if activity["classified_as"][0]["id"] == "http://vocab.getty.edu/aat/300393177" and "took_place_at" in activity:
                place_list = activity["took_place_at"]
                for place_raw in place_list: # I have the feeling, that there is an 'activity' record for every place, but perhaps there may be also sometimes two places linked to one 'activity' record
        #            print("place of activity found")
        #            print(place_raw)
                    conn_place = classes.ConnectedEntity()
                    conn_place.name = place_raw["_label"]
                    conn_place.connection_type = "ortw"
                    place_id_list = []
                    place_id = classes.ExternalId()
                    place_id.uri = place_raw["id"]
                    place_id.id = place_id.uri[27:]
                    place_id.name = "tgn"
                    place_id_list.append(place_id)
                    pe.connected_locations.append(conn_place)
                    ortw_preview = ", active in " + conn_place.name
    # attention: ULAN defines any number of places of activity. I will need one and only one place defined as preferred place. 
    # thus: I need to introduce a function that makes the editor choose one place if there are several, and enter one if there are none.          

    pe.preview = pe.name_preferred + " " + date_preview + " " + ortg_preview + ortw_preview + orts_preview + name_variant_preview

    print(pe)
    return pe