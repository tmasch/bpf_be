#pylint: disable=C0301, C0303
"""
Organisation related business logic
"""
import re
from nanoid import generate
from bpf import classes
from bpf import db_actions
from bpf import get_external_data
from bpf import person_relations
from bpf.parsing import parsing_helpers



@classes.async_func_logger
async def ingest_organisation(org):
    """
    This function is about translating the imported information of a organisation into the information record used for the database. 
    It directly sends the new records to the function for writing it and only returns its ID to metadata_dissection
    """
    list_of_ids_to_check = []
    new_record_viaf_id = ""
    new_record_gnd_id = ""
    person_found = {}
    org_found = {}
    location_found = {}
    connected_location_comment_is_date = r'(ab|bis|ca.|seit)?(\d \-)' # if the comment for a connection between person and location follows this pattern, it is moved to connection time
    # Maybe I should adapt this for the dates connected with orgs.
    org_selected = org.potential_candidates[org.chosen_candidate]
    new_record_gnd_id = org_selected.external_id[0].id # I need this only as long as I cannot get VIAF to work for organisations. 
    org_new = classes.OrganisationDb()
    org_new.id = generate()
    org_new.type = "Organisation"
    org_new.org_type1.append(parsing_helpers.map_role_to_organisation_type(org.role))
    org_new.external_id = org_selected.external_id
    for org_id in org_new.external_id:
        if org_id.name == "GND_intern":
            list_of_ids_to_check.append(org_id.uri)
            break
        elif org_id.name == "GND":
            new_record_gnd_id = org_id.id
            if "-" in org_id.id:
                gnd_internal_id = get_external_data.transform_gnd_id_with_hyphen(org_id.id)
                print("This is the gnd_internal_id produced by the new module: ")
                print(gnd_internal_id)
                org_new.external_id.insert(0,gnd_internal_id)
                list_of_ids_to_check.append(gnd_internal_id.uri)
                break
            else:
                list_of_ids_to_check.append(org_id.uri)
                break

    # Here, the VIAF ID is added to the organisation's record
# I have cancelled the next two lines as long as VIAF doesn't work properly with organisation IDs. 
    #new_record_viaf_id = get_viaf_from_authority(org_new.external_id[0].uri)
    #org_new.external_id.append(new_record_viaf_id)
    org_new.name_preferred = org_selected.name_preferred
    print("----------------------------------")
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print("----------------------------------")
    print("NOW PROCESSING ORG")
    print(org_new.name_preferred)
    print(org_new.id)

    org_new.name_variant = org_selected.name_variant
    if org.name not in org_new.name_variant: # Thus, the name that was used for the search is added as name variant to the iconobase.
        # This is necessary because up to now, Iconobase uses a string search for variants and not a word search. 
        org_new.name_variant.append(org.name)
    org_new.dates_from_source = org_selected.dates_from_source # A lot of works needs to be done here. 
    if org_selected.connected_persons:
        # The GND has very few standardised abbreviations for relationships, largely 'bezf' (family relationship), 'bezb' (professional relationship) and 'beza' (anything else)
        # Sometimes, the concrete type of relationship is given in a comment field, but it is not standardised. 
        # Hence, the only thing I can come up with is the following: 
            # If there is only the general abbreviation, I replace it with a general English phrase
            # If there is the general abbreviation plus a common word in the comments field, I use an English translation of the concrete relationship)
            # If there is the general abbreviation plus a word in the comments field that is not common (or simply has escaped me), the relationship will be a general English phrase plus the original German comment
        for connected_person in org_selected.connected_persons:
            connected_person.connection_comment, connected_person.connection_type = parsing_helpers.parse_relationship("organisation", "person", connected_person.connection_comment, connected_person.connection_type, "")
            for external_id in connected_person.external_id:
#                person_found = coll.find_one({"external_id": {"$elemMatch": {"name": external_id.name, "id": external_id.id}}}, {"id": 1, "name_preferred" : 1, "sex" : 1, "connected_organisations" : 1})
                person_found = db_actions.find_person(external_id,"external_id_connected_organisation")
                if person_found:
                    print("---------------------------------------------")
                    print("step 1 (GND): person connected to org found")
                    connected_person.id = person_found["id"]
                    connected_person.name = person_found["name_preferred"] # Here, the year must be added. One should probably rename it as 'preview'. 
                    type_correction, time_correction, comment_correction = db_actions.add_relationship_in_far_record(person_found, org_new, "connected_organisations", connected_person.connection_type, connected_person.connection_time, connected_person.connection_comment) # This is step 2, the reciprocal connection
                    if type_correction != "":
                        connected_person.connection_type = type_correction
                    if time_correction != "":
                        connected_person.connection_time = time_correction
                    if comment_correction != "":
                        connected_person.connection_comment = comment_correction

                    break # if a connection with one ID is found, the other connections would be the same. 

            if not person_found and connected_person.external_id:
                list_of_ids_to_check.append(connected_person.external_id[0].uri) # I just use the first ID given here, since all IDs should be in VIAF
                # (although the modul for getting IDs from VIAF currently only processes GND and ULAn)
    if org_selected.connected_organisations:
        print("the following organisations are connected to the new record: ")
        print(org_selected.connected_organisations)
        for connected_org in org_selected.connected_organisations:
            connected_org.connection_comment, connected_org.connection_type = parsing_helpers.parse_relationship("organisation", "organisation", connected_org.connection_comment, connected_org.connection_type, "")
            for external_id in connected_org.external_id:
#                org_found = coll.find_one({"external_id": {"$elemMatch": {"name": external_id.name, "id": external_id.id}}}, {"id": 1, "name_preferred" : 1, "connected_organisations" : 1})
                org_found = db_actions.find_organisation(external_id,"external_id_organisation")
                if org_found:
                    print("---------------------------------------------")
                    print("step 1 (GND): org connected to org found")
                    connected_org.id = org_found["id"]
                    connected_org.name = org_found["name_preferred"] # Here, the year must be added. One should probably rename it as 'preview'. 
                    type_correction, time_correction, comment_correction = db_actions.add_relationship_in_far_record(org_found, org_new, "connected_organisations", connected_org.connection_type, connected_org.connection_time, connected_org.connection_comment) # This is step 2, the reciprocal connection
                    if type_correction != "":
                        connected_org.connection_type = type_correction
                    if time_correction != "":
                        connected_org.connection_time = time_correction
                    if comment_correction != "":
                        connected_org.connection_comment = comment_correction

                    break # if a connection with one ID is found, the other connections would be the same. 
            if not org_found and connected_org.external_id:
                if "-" in connected_org.external_id[0].id:
                    gnd_internal_id = get_external_data.transform_gnd_id_with_hyphen(connected_org.external_id[0].id)
                    connected_org.external_id.insert(0,gnd_internal_id)
                    print("This is the gnd_internal_id produced by the new module: ")
                    print(gnd_internal_id)
                    list_of_ids_to_check.append(gnd_internal_id.uri)
                else:
                    list_of_ids_to_check.append(connected_org.external_id[0].uri) # I just use the first ID given here, since all IDs should be in VIAF


#           The following two lines are commented out until VIAF can deal with GND organisations
#            if not org_found and connected_org.external_id:
#                    list_of_ids_to_check.append(connected_org.external_id[0].uri) # I just use the first ID given here, since all IDs should be in VIAF
    if org_selected.connected_locations:
        for connected_location in org_selected.connected_locations:
            connected_location.connection_comment, connected_location.connection_type = parsing_helpers.parse_relationship("organisation", "location", connected_location.connection_comment, connected_location.connection_type, "")
            for external_id in connected_location.external_id:
                # I must introduce distinction between historical and modern locations! 
#                location_found = coll.find_one({"external_id": {"$elemMatch": {"name": external_id.name, "id": external_id.id}}}, {"id": 1, "name_preferred" : 1, "connected_organisations" : 1})
                location_found = db_actions.find_place(external_id,"external_id_connected_organisations")
                if location_found:
                    print("---------------------------------------------")
                    print("step 1 (GND): place connected to org found")
                    connected_location.id = location_found["id"]
                    connected_location.name = location_found["name_preferred"]
                    type_correction, time_correction, comment_correction = db_actions.add_relationship_in_far_record(location_found, org_new, "connected_organisations", connected_location.connection_type, connected_location.connection_time, connected_location.connection_comment) # This is step 2, the reciprocal connection
                    if type_correction != "":
                        connected_location.connection_type = type_correction
                    if time_correction != "":
                        connected_location.connection_time = time_correction
                    if comment_correction != "":
                        connected_location.connection_comment = comment_correction
                    break # if a connection with one ID is found, the other connections would be the same. 
            if not location_found and connected_location.external_id:
                if "-" in connected_location.external_id[0].id:
                    print("location with hyphen found")
                    print("sending id to transform_gnd_id_with_hyphen")
                    print(connected_location.external_id[0].id)
                    gnd_internal_id = get_external_data.transform_gnd_id_with_hyphen(connected_location.external_id[0].id)
                    print("This is the gnd_internal_id produced by the new module: ")
                    print(gnd_internal_id)
                    connected_location.external_id.insert(0,gnd_internal_id)
                    list_of_ids_to_check.append(gnd_internal_id.uri)
                else:
                    list_of_ids_to_check.append(connected_location.external_id[0].uri) # I just use the first ID given here, since all IDs should be in VIAF


#           The following two lines are commented out until VIAF can deal with GND locations
#            if not location_found and connected_location.external_id:
#                    list_of_ids_to_check.append(connected_location.external_id[0].uri) # I just use the first ID given here, since all IDs should be in VIAF
    # Here, I send the list of all collected IDs for which I need a VIAF ID to the function that contacts VIAF. 

    list_of_viaf_ids = await get_external_data.get_viaf_from_authority(list_of_ids_to_check)
#    print(list_of_viaf_ids)

# The following has to be commented out until I can process organisation VIAF IDs

    org_viaf_url = list_of_viaf_ids[org_new.external_id[0].uri]
    org_id = classes.ExternalReference()
    org_id.name = "viaf"
    org_id.uri = org_viaf_url
    org_id.id = org_viaf_url[21:]
    new_record_viaf_id = org_id.id # I need this later
    org_new.external_id.append(org_id)
    # this has to be expanded for organisations and locations, once this is possible
    # then, to the record of the connected person

    for connected_person in org_selected.connected_persons:
        if connected_person.external_id:
            if connected_person.external_id[0].uri in list_of_viaf_ids:
                person_viaf_url = list_of_viaf_ids[connected_person.external_id[0].uri]
                person_id = classes.ExternalReference()
                person_id.name = "viaf"
                person_id.uri = person_viaf_url
                person_id.id = person_viaf_url[21:]
                connected_person.external_id.append(person_id)
    for connected_org in org_selected.connected_organisations:
        if connected_org.external_id:
            if connected_org.external_id[0].uri in list_of_viaf_ids:
                org_viaf_url = list_of_viaf_ids[connected_org.external_id[0].uri]
                org_id = classes.ExternalReference()
                org_id.name = "viaf"
                org_id.uri = org_viaf_url
                org_id.id = org_viaf_url[21:]
                connected_org.external_id.append(org_id)
    for connected_location in org_selected.connected_locations:
        if connected_location.external_id:
            if connected_location.external_id[0].uri in list_of_viaf_ids:
                location_viaf_url = list_of_viaf_ids[connected_location.external_id[0].uri]
                place_id = classes.ExternalReference()
                place_id.name = "viaf"
                place_id.uri = location_viaf_url
                place_id.id = location_viaf_url[21:]
                connected_location.external_id.append(place_id)



    if org_selected.connected_persons:
        for connected_person in org_selected.connected_persons:
            if not connected_person.id and connected_person.external_id: # If there is already an id, no 'stitching' is required                               
                for external_id in connected_person.external_id:
                    if external_id.id != "DNB": # If it is, the connection has been made earlier
                    # This is 'stitching' step 1 for the records that can only be connected through VIAF
#                        person_found = coll.find_one({"external_id": {"$elemMatch": {"name": external_id.name, "id": external_id.id}}}, {"id": 1, "name_preferred" : 1, "sex" : 1, "connected_organisations" : 1})
                        person_found = db_actions.find_person(external_id,"external_id_connected_organisation")
                    if person_found:
                        print("---------------------------------------------")
                        print("step 1 (VIAF): person connected to org found")

                        connected_person.id = person_found["id"]
                        connected_person.name = person_found["name_preferred"] # Here, the year must be added. One should probably rename it as 'preview'. 
                         # if a connection with one ID is found, the other connections would be the same. 
                        type_correction, time_correction, comment_correction = db_actions.add_relationship_in_far_record(person_found, org_new, "connected_organisations", connected_person.connection_type, connected_person.connection_time, connected_person.connection_comment) # This is step 2, the reciprocal connection
                        if type_correction != "":
                            connected_org.connection_type = type_correction
                        if time_correction != "":
                            connected_org.connection_time = time_correction
                        if comment_correction != "":
                            connected_org.connection_comment = comment_correction

                        break

# Similar features have to be added for connected organisations and places, once this is possible.             

            new_connected_person = classes.Edge()
            new_connected_person.id = connected_person.id
            new_connected_person.name = connected_person.name
            new_connected_person.external_id = connected_person.external_id
            if connected_person.name == "": # if there is no preview, i.e. no connection found
                new_connected_person.name = connected_person.name
            new_connected_person.connection_type = connected_person.connection_type
            new_connected_person.connection_time = connected_person.connection_time
            new_connected_person.connection_comment = connected_person.connection_comment
            # In theory, one should also replace this time string through a proper date object However, since I don't assume that anything will ever be made with 
            # this information apart from displaying it, this is unnecessary or at least not urgent. 
            org_new.connected_persons.append(new_connected_person)

    if org_selected.connected_organisations:
        for connected_organisation in org_selected.connected_organisations:
            print("now processing connected organisation " + connected_organisation.name)
            new_connected_organisation = classes.Edge()
            new_connected_organisation.id = connected_organisation.id
            new_connected_organisation.external_id = connected_organisation.external_id
            new_connected_organisation.name = connected_organisation.name
            new_connected_organisation.connection_type = connected_organisation.connection_type
            new_connected_organisation.connection_time = connected_organisation.connection_time
            # For connection time see above under new connected person
            org_new.connected_organisations.append(new_connected_organisation)

    if org_selected.connected_locations:
        for connected_location in org_selected.connected_locations:
            # in not few cases, dates are written not into the date field but into the comment field of the connection, or they follow the descriptions "Wohnort" or "Wirkungsort"
            if re.match(connected_location_comment_is_date, connected_location.connection_comment): # This means that the 'comment' field contains information that should have gone into the 'time' field.
                if connected_location.connection_time:
                    connected_location.connection_time = connected_location.connection_time + ", " + connected_location.connection_comment
                else:
                    connected_location.connection_time = connected_location.connection_comment
                connected_location.connection_comment = ""
            elif connected_location.connection_comment[0:12] == "Wirkungsort ":
                connected_location.connection_time = connected_location.connection_comment[12:]
                connected_location.connection_comment = "wirkungsort"
            elif connected_location.connection_comment[0:8] == "Wohnort ":
                connected_location.connection_time = connected_location.connection_comment[8:]
                connected_location.connection_comment = "wohnort"

            new_connected_location = classes.Edge()
            new_connected_location.id = connected_location.id
            new_connected_location.external_id = connected_location.external_id
            new_connected_location.name = connected_location.name
            new_connected_location.connection_type = connected_location.connection_type
            new_connected_location.connection_time = connected_location.connection_time
            new_connected_location.connection_comment = connected_location.connection_comment
            # For connection time see above under new connected person (only relevant for location of activity)
            org_new.connected_locations.append(new_connected_location)
    org_new.comments = org_selected.comments
    # Here comes step 3 of the stitching process: checking if there is any record in Iconobase that has a reference to the new record (only relevant if the new record has no reference to that record)
    # I must define what external_id is! 
    #person_found = list(coll.find({"connected_persons.external_id.name": "viaf", "connected_persons.external_id.id": new_record_viaf_id.id}, {"id": 1, "name_preferred" : 1, "connected_persons" : 1}))

#   The following line should be reinstated once every goes via VIAF, the line afterwards is a stopgap to work with both VIAF and GND
#    person_found = list(coll.find({"connected_persons.external_id.name" : "viaf", "connected_persons.external_id.id" : new_record_viaf_id}, {"id": 1, "name_preferred" : 1, "sex": 1, "connected_persons" : 1}))
# record with sex
#    list_found = list(coll.find({ "$or": [{"connected_organisations.external_id.name" : "viaf", "connected_organisations.external_id.id" : new_record_viaf_id}, {"connected_organisations.external_id.name" : "GND", "connected_organisations.external_id.id" : new_record_gnd_id}]}, {"id": 1, "type" : 1, "name_preferred" : 1, "sex": 1, "connected_organisations" : 1}))
    list_found = db_actions.find_organisation_viaf(new_record_viaf_id,new_record_gnd_id)
    print("------------------------------------------")
    print("step 3: far records found: ")
    print("searching for: ")
    print("GND: ")
    print(new_record_gnd_id)
    print("VIAF: ")
    print(new_record_viaf_id)
    print(list_found)

    for far_record in list_found:
        # I have to change that and rather go through every connection in far_record - I have gone through all connections in new_record before
        # check for every connected person if it has correct VIAF ID - if so, check if it has internal ID, if not > add. 
        far_connected_org_list = far_record["connected_organisations"]
        for far_connected_org in far_connected_org_list:
            print("connection to organisation in far record:")
            print(far_connected_org)
            for far_id in far_connected_org["external_id"]:
                if (far_id["name"] == "viaf" and far_id["id"] == new_record_viaf_id) or (far_id["name"] == "GND" and far_id["id"] == new_record_gnd_id):
                    print("connected org in far record found: ")
                    print(far_connected_org)
                    if far_connected_org["id"]:
                        print("connected org already in new record, no action necessary")
                        break # in this case, a connection has already been established
                    else:
                        print("connected org not yet in new record, needs to be added")
                        far_connection_type = far_connected_org["connection_type"]
                        db_actions.add_connection_id_and_name(far_record["id"], "connected_organisations", far_connection_type, far_connected_org["name"], org_new.name_preferred, org_new.id, far_connection_type, far_connected_org["connection_time"], far_connected_org["connection_comment"])
                        new_connection = classes.Edge()
                        new_connection.id = far_record["id"]
                        new_connection.name = far_record["name_preferred"]
                        new_connection.connection_type = person_relations.relation_correspondence(far_connection_type, "")
                        new_connection.connection_comment = far_connected_org["connection_comment"]
                        new_connection.connection_time = far_connected_org["connection_time"]
            #            new_connection.connection_type = "counterpart to " + far_connection_type
                        if far_record["type"] == "Person":
                            org_new.connected_persons.append(new_connection)
                        if far_record["type"] == "Organisation":
                            org_new.connected_organisations.append(new_connection)
                        if far_record["type"] == "Place":
                            org_new.connected_locations.append(new_connection)
                        break

    await db_actions.insert_record_organisation(org_new)

    return org_new.id
