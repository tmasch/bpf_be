# pylint: disable=C0301, C0303
"""
Place
"""

import re
from nanoid import generate

import classes
import db_actions
import get_external_data
import person_relations
import parsing_helpers

@classes.async_func_logger
async def add_connected_person_to_place(place_new,connected_persons,list_of_ids_to_check):
    # This is step 1 of the stitching process
    for connected_person in connected_persons:
        connected_person.connection_comment, connected_person.connection_type = (
            parsing_helpers.parse_relationship(
                "location",
                "person",
                connected_person.connection_comment,
                connected_person.connection_type,
                "",
            )
        )
        for external_id in connected_person.external_id:
            #                person_found = coll.find_one({"external_id": {"$elemMatch": {"name": external_id.name, "id": external_id.id}}}, {"id": 1, "name_preferred" : 1, "sex" : 1, "connected_locations" : 1})
            person_found = db_actions.find_person(
                external_id, "external_id_connected_location"
            )
            if person_found:
                print("---------------------------------------------")
                print("step 1 (GND): person connected to place found")
                connected_person.id = person_found["id"]
                connected_person.name = person_found[
                    "name_preferred"
                ]  # Here, the year must be added. One should probably rename it as 'preview'.
                type_correction, time_correction, comment_correction = (
                    db_actions.add_relationship_in_far_record(
                        person_found,
                        place_new,
                        "connected_locations",
                        connected_person.connection_type,
                        connected_person.connection_time,
                        connected_person.connection_comment,
                    )
                )  # This is step 2, the reciprocal connection
                if type_correction != "":
                    connected_person.connection_type = type_correction
                if time_correction != "":
                    connected_person.connection_time = time_correction
                if comment_correction != "":
                    connected_person.connection_comment = comment_correction

                break  # if a connection with one ID is found, the other connections would be the same.
        if not person_found and connected_person.external_id:
            list_of_ids_to_check.append(
                connected_person.external_id[0].uri
            )  # I just use the first ID given here, since all IDs should be in VIAF
            # (although the modul for getting IDs from VIAF currently only processes GND and ULAn)
    return place_new, list_of_ids_to_check

@classes.async_func_logger
async def add_connected_organisation_to_place(place_new,connected_organisations,list_of_ids_to_check):
    for connected_org in connected_organisations:
        connected_org.connection_comment, connected_org.connection_type = (
            parsing_helpers.parse_relationship(
                "location",
                "organisation",
                connected_org.connection_comment,
                connected_org.connection_type,
                "",
            )
        )
        for external_id in connected_org.external_id:
            #                org_found = coll.find_one({"external_id": {"$elemMatch": {"name": external_id.name, "id": external_id.id}}}, {"id": 1, "name_preferred" : 1, "connected_locations" : 1})
            org_found = db_actions.find_organisation(
                external_id, "external_id_location"
            )
            if org_found:
                print("---------------------------------------------")
                print("step 1 (GND): org connected to place found")
                connected_org.id = org_found["id"]
                connected_org.name = org_found[
                    "name_preferred"
                ]  # Here, the year must be added. One should probably rename it as 'preview'.
                type_correction, time_correction, comment_correction = (
                    db_actions.add_relationship_in_far_record(
                        org_found,
                        place_new,
                        "connected_locations",
                        connected_org.connection_type,
                        connected_org.connection_time,
                        connected_org.connection_comment,
                    )
                )  # This is step 2, the reciprocal connection
                if type_correction != "":
                    connected_org.connection_type = type_correction
                if time_correction != "":
                    connected_org.connection_time = time_correction
                if comment_correction != "":
                    connected_org.connection_comment = comment_correction

                break  # if a connection with one ID is found, the other connections would be the same.
        if not org_found and connected_org.external_id:
            if "-" in connected_org.external_id[0].id:
                gnd_internal_id = get_external_data.transform_gnd_id_with_hyphen(
                    connected_org.external_id[0].id
                )
                connected_org.external_id.insert(0, gnd_internal_id)
                print("This is the gnd_internal_id produced by the new module: ")
                print(gnd_internal_id)
                list_of_ids_to_check.append(gnd_internal_id.uri)
            else:
                list_of_ids_to_check.append(
                    connected_org.external_id[0].uri
                )  # I just use the first ID given here, since all IDs should be in VIAF

#           The following two lines are commented out until VIAF can deal with GND organisations
#            if not org_found and connected_org.external_id:
#                    list_of_ids_to_check.append(connected_org.external_id[0].uri) # I just use the first ID given here, since all IDs should be in VIAF
    return place_new, list_of_ids_to_check


@classes.async_func_logger
async def ingest_place(place):
    """
This function saves a place in the database
    """
    list_of_ids_to_check = []
    new_record_viaf_id = ""
    new_record_gnd_id = ""
    person_found = {}
    org_found = {}
    location_found = {}
    connected_location_comment_is_date = r"(ab|bis|ca.|seit)?(\d \-)"  # if the comment for a connection between person and location follows this pattern, it is moved to connection time
    # Maybe I should adapt this for the dates connected with places.
    # This function is about translating the imported information of a place into the place record used for the database.
    # It directly sends the new records to the function for writing it and only returns its ID to metadata_dissection
    print("place_ingest, start, number of potential candidates:")
    print(len(place.potential_candidates))
    print("place_ingest, start, number of chosen candidate")
    print(place.chosen_candidate)
    place_selected = place.potential_candidates[place.chosen_candidate]
    if len(place_selected.external_id) > 1:
        new_record_gnd_id = place_selected.external_id[
            1
        ].id  # I need this only as long as I cannot get VIAF to work for organisations. Normally, the GND ID is listed second.
    else:
        new_record_gnd_id = place_selected.external_id[0].id
    place_new = classes.PlaceDb()
    place_new.id = generate()
    place_new.type = "Place"
#    print("----------------------------------")
#    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
#    print("----------------------------------")
    print("NOW PROCESSING PLACE")
    print(place_new.name_preferred)
    print(place_new.id)

    place_new.place_type1 = ["Town - historical"]
    place_new.external_id = place_selected.external_id
    print(place_new.external_id)
    for place_id in place_new.external_id:
        if place_id.name == "GND_intern":
            list_of_ids_to_check.append(place_id.uri)
            break
        elif place_id.name == "GND":  # this would normally not be the case.
            new_record_gnd_id = place_id.id
            if "-" in place_id.id:
                gnd_internal_id = get_external_data.transform_gnd_id_with_hyphen(place_id.id)
                print("This is the gnd_internal_id produced by the new module: ")
                print(gnd_internal_id)
                place_new.external_id.insert(0, gnd_internal_id)
                list_of_ids_to_check.append(gnd_internal_id.uri)
                break
            else:
                list_of_ids_to_check.append(place_id.uri)
                break

    place_new.name_preferred = place_selected.name_preferred
    place_new.name_variant = place_selected.name_variant
    if (
        place.name not in place_new.name_variant
    ):  # Thus, the name that was used for the search is added as name variant to the iconobase.
        # This is necessary because up to now, Iconobase uses a string search for variants and not a word search.
        place_new.name_variant.append(place.name)
    place_new.dates_from_source = (
        place_selected.dates_from_source
    )  # A lot of works needs to be done here.
    if place_selected.connected_persons:
        place_new, list_of_ids_to_check = add_connected_person_to_place(place_new,place_selected.connected_persons,list_of_ids_to_check)



    if place_selected.connected_organisations:
        place_new, list_of_ids_to_check = add_connected_organisation_to_place(place_new,place_selected.connected_organisations,list_of_ids_to_check)


    if place_selected.connected_locations:
        for connected_location in place_selected.connected_locations:
            (
                connected_location.connection_comment,
                connected_location.connection_type,
            ) = parsing_helpers.parse_relationship(
                "location",
                "location",
                connected_location.connection_comment,
                connected_location.connection_type,
                "",
            )
            for external_id in connected_location.external_id:
                #                location_found = coll.find_one({"external_id": {"$elemMatch": {"name": external_id.name, "id": external_id.id}}}, {"id": 1, "name_preferred" : 1, "connected_locations" : 1})
                location_found = db_actions.find_place(
                    external_id, "external_id_connected_locations"
                )
                if location_found:
                    print("---------------------------------------------")
                    print("step 1 (GND): place connected to place found")
                    connected_location.id = location_found["id"]
                    connected_location.name = location_found["name_preferred"]
                    type_correction, time_correction, comment_correction = (
                        db_actions.add_relationship_in_far_record(
                            location_found,
                            place_new,
                            "connected_locations",
                            connected_location.connection_type,
                            connected_location.connection_time,
                            connected_location.connection_comment,
                        )
                    )  # This is step 2, the reciprocal connection
                    if type_correction != "":
                        connected_location.connection_type = type_correction
                    if time_correction != "":
                        connected_location.connection_time = time_correction
                    if comment_correction != "":
                        connected_location.connection_comment = comment_correction
                    print(connected_location)
                    break  # if a connection with one ID is found, the other connections would be the same.
            if not location_found and connected_location.external_id:
                if "-" in connected_location.external_id[0].id:
                    print(connected_location)
                    print("location with hyphen found")
                    print("sending id to transform_gnd_id_with_hyphen")
                    print(connected_location.external_id[0].id)
                    gnd_internal_id = get_external_data.transform_gnd_id_with_hyphen(
                        connected_location.external_id[0].id
                    )
                    print("This is the gnd_internal_id produced by the new module: ")
                    print(gnd_internal_id)
                    connected_location.external_id.insert(0, gnd_internal_id)
                    list_of_ids_to_check.append(gnd_internal_id.uri)
                else:
                    list_of_ids_to_check.append(
                        connected_location.external_id[0].uri
                    )  # I just use the first ID given here, since all IDs should be in VIAF

    #           The following two lines are commented out until VIAF can deal with GND locations
    #            if not location_found and connected_location.external_id:
    #                    list_of_ids_to_check.append(connected_location.external_id[0].uri) # I just use the first ID given here, since all IDs should be in VIAF

    # Here, I send the list of all collected IDs for which I need a VIAF ID to the function that contacts VIAF.
    list_of_viaf_ids = await get_external_data.get_viaf_from_authority(list_of_ids_to_check)
    print(list_of_viaf_ids)


    location_viaf_url = list_of_viaf_ids[place_new.external_id[0].uri]
    place_id = classes.ExternalReference()
    place_id.name = "viaf"
    place_id.uri = location_viaf_url
    place_id.id = location_viaf_url[21:]  #####
    new_record_viaf_id = place_id.id  # I need this later
    print(place_id)
    place_new.external_id.append(place_id)
    # this has to be expanded for organisations and locations, once this is possible
    # then, to the record of the connected person

    print("here 12")
    print(place_new.connected_locations)
    print("here 12")


    for connected_person in place_selected.connected_persons:
        if connected_person.external_id:
            if connected_person.external_id[0].uri in list_of_viaf_ids:
                person_viaf_url = list_of_viaf_ids[connected_person.external_id[0].uri]
                person_id = classes.ExternalReference()
                person_id.name = "viaf"
                person_id.uri = person_viaf_url
                person_id.id = person_viaf_url[21:]
                connected_person.external_id.append(person_id)
    for connected_org in place_selected.connected_organisations:
        if connected_org.external_id:
            if connected_org.external_id[0].uri in list_of_viaf_ids:
                org_viaf_url = list_of_viaf_ids[connected_org.external_id[0].uri]
                org_id = classes.ExternalReference()
                org_id.name = "viaf"
                org_id.uri = org_viaf_url
                org_id.id = org_viaf_url[21:]
                print(org_id)
                connected_org.external_id.append(org_id)
    for connected_location in place_selected.connected_locations:
        if connected_location.external_id:
            if connected_location.external_id[0].uri in list_of_viaf_ids:
                location_viaf_url = list_of_viaf_ids[
                    connected_location.external_id[0].uri
                ]
                place_id = classes.ExternalReference()
                place_id.name = "viaf"
                place_id.uri = location_viaf_url
                place_id.id = location_viaf_url[21:]
                print("here 13")
                print(place_id)
                connected_location.external_id.append(place_id)
                print(connected_location)
                print("here 13")

    if place_selected.connected_persons:
        for connected_person in place_selected.connected_persons:
            if (
                not connected_person.id and connected_person.external_id
            ):  # If there is already an id, no 'stitching' is required
                for external_id in connected_person.external_id:
                    if (
                        external_id.name != "DNB"
                    ):  # If it is, the connection has been made earlier
                        # This is 'stitching' step 1 for the records that can only be connected through VIAF
                        #                        person_found = coll.find_one({"external_id": {"$elemMatch": {"name": external_id.name, "id": external_id.id}}}, {"id": 1, "name_preferred" : 1, "sex" : 1, "connected_locations" : 1})
                        person_found = db_actions.find_person(
                            external_id, "external_id_connected_location"
                        )
                    if person_found:
                        connected_person.id = person_found["id"]
                        connected_person.name = person_found[
                            "name_preferred"
                        ]  # Here, the year must be added. One should probably rename it as 'preview'.
                        print("---------------------------------------------")
                        print("step 1 (VIAF): person connected to place found")

                        # if a connection with one ID is found, the other connections would be the same.
                        db_actions.add_relationship_in_far_record(
                            person_found,
                            place_new,
                            "connected_persons",
                            connected_person.connection_type,
                            connected_person.connection_time,
                            connected_person.connection_comment,
                        )  # This is step 2, the reciprocal connection
                        break

            new_connected_person = classes.EntityConnection()
            new_connected_person.id = connected_person.id
            new_connected_person.name = connected_person.name
            new_connected_person.external_id = connected_person.external_id
            if (
                connected_person.name == ""
            ):  # if there is no preview, i.e. no connection found
                new_connected_person.name = connected_person.name
            new_connected_person.connection_type = connected_person.connection_type
            new_connected_person.connection_time = connected_person.connection_time
            new_connected_person.connection_comment = (
                connected_person.connection_comment
            )
            # In theory, one should also replace this time string through a proper date object However, since I don't assume that anything will ever be made with
            # this information apart from displaying it, this is unnecessary or at least not urgent.         place_new.connected_persons.append(new_connected_person)
    if place_selected.connected_organisations:
        for connected_organisation in place_selected.connected_organisations:
            print(
                "now processing connected organisation " + connected_organisation.name
            )
            new_connected_organisation = classes.EntityConnection()
            new_connected_organisation.id = connected_organisation.id
            new_connected_organisation.external_id = connected_organisation.external_id
            new_connected_organisation.name = connected_organisation.name
            new_connected_organisation.connection_type = (
                connected_organisation.connection_type
            )
            new_connected_organisation.connection_time = (
                connected_organisation.connection_time
            )
            # For connection time see above under new connected person
            place_new.connected_organisations.append(new_connected_organisation)
    if place_selected.connected_locations:
        for connected_location in place_selected.connected_locations:
            # in not few cases, dates are written not into the date field but into the comment field of the connection, or they follow the descriptions "Wohnort" or "Wirkungsort"
            if re.match(
                connected_location_comment_is_date,
                connected_location.connection_comment,
            ):  # This means that the 'comment' field contains information that should have gone into the 'time' field.
                if connected_location.connection_time:
                    connected_location.connection_time = (
                        connected_location.connection_time
                        + ", "
                        + connected_location.connection_comment
                    )
                else:
                    connected_location.connection_time = (
                        connected_location.connection_comment
                    )
                connected_location.connection_comment = ""
            elif connected_location.connection_comment[0:12] == "Wirkungsort ":
                connected_location.connection_time = (
                    connected_location.connection_comment[12:]
                )
                connected_location.connection_comment = "wirkungsort"
            elif connected_location.connection_comment[0:8] == "Wohnort ":
                connected_location.connection_time = (
                    connected_location.connection_comment[8:]
                )
                connected_location.connection_comment = "wohnort"

            new_connected_location = classes.EntityConnection()
            new_connected_location.id = connected_location.id
            new_connected_location.external_id = connected_location.external_id
            new_connected_location.name = connected_location.name
            new_connected_location.connection_type = connected_location.connection_type
            new_connected_location.connection_time = connected_location.connection_time
            new_connected_location.connection_comment = (
                connected_location.connection_comment
            )
            # For connection time see above under new connected person (only relevant for location of activity)
            place_new.connected_locations.append(new_connected_location)
    place_new.comments = place_selected.comments
    place_new.coordinates = (
        place_selected.coordinates
    )  # I leave them now as they are, but perhaps I should remove duplicates

    print(place_new.connected_locations)

    # Here comes step 3 of the stitching process: checking if there is any record in Iconobase that has a reference to the new record (only relevant if the new record has no reference to that record)
    # I must define what external_id is!
    # person_found = list(coll.find({"connected_persons.external_id.name": "viaf", "connected_persons.external_id.id": new_record_viaf_id.id}, {"id": 1, "name_preferred" : 1, "connected_persons" : 1}))

    #   The following line should be reinstated once every goes via VIAF, the line afterwards is a stopgap to work with both VIAF and GND
    #    person_found = list(coll.find({"connected_persons.external_id.name" : "viaf", "connected_persons.external_id.id" : new_record_viaf_id}, {"id": 1, "name_preferred" : 1, "sex": 1, "connected_persons" : 1}))
    # record with sex
    #    list_found = list(coll.find({ "$or": [{"connected_locations.external_id.name" : "viaf", "connected_locations.external_id.id" : new_record_viaf_id}, {"connected_locations.external_id.name" : "GND", "connected_locations.external_id.id" : new_record_gnd_id}]}, {"id": 1, "type" : 1, "name_preferred" : 1, "sex": 1, "connected_locations" : 1}))
    list_found = db_actions.find_place_viaf(new_record_viaf_id, new_record_gnd_id)
    print("ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ")
    print("new_record_viaf_id: ")
    print(new_record_viaf_id)
    print("new_record_gnd_id: ")
    print(new_record_gnd_id)
    print("step 3: far records found: ")
    print(list_found)



    for far_record in list_found:
        # I have to change that and rather go through every connection in far_record - I have gone through all connections in new_record before
        # check for every connected person if it has correct VIAF ID - if so, check if it has internal ID, if not > add.
        far_connected_places_list = far_record["connected_locations"]
        for far_connected_place in far_connected_places_list:
            print("connection to plae in far record:")
            print(far_connected_place)
            for far_id in far_connected_place["external_id"]:
                if (
                    far_id["name"] == "viaf" and far_id["id"] == new_record_viaf_id
                ) or (far_id["name"] == "GND" and far_id["id"] == new_record_gnd_id):
                    print("connected place in far record found: ")
                    print(far_connected_place)
                    if far_connected_place["id"]:
                        print(
                            "connected org already in new record, no action necessary"
                        )
                        break  # in this case, a connection has already been established
                    else:
                        print("connected org not yet in new record, needs to be added")
                        far_connection_type = far_connected_place["connection_type"]
                        db_actions.add_connection_id_and_name(
                            far_record["id"],
                            "connected_locations",
                            far_connection_type,
                            far_connected_place["name"],
                            place_new.name_preferred,
                            place_new.id,
                            far_connected_place["connection_type"],
                            far_connected_place["connection_time"],
                            far_connected_place["connection_comment"],
                        )
                        new_connection = classes.EntityConnection()
                        new_connection.id = far_record["id"]
                        new_connection.name = far_record["name_preferred"]
                        new_connection.connection_type = (
                            person_relations.relation_correspondence(
                                far_connection_type, ""
                            )
                        )
                        new_connection.connection_comment = far_connected_place[
                            "connection_comment"
                        ]
                        new_connection.connection_time = far_connected_place[
                            "connection_time"
                        ]
                        print("establishing new connection: ")
                        print("far_connection_type: ")
                        print(far_connection_type)
                        print("connection_type for insertion: ")
                        print(new_connection.connection_type)
                        print("new connection added to place record: ")
                        print(new_connection)
                        #            new_connection.connection_type = "counterpart to " + far_connection_type
                        if far_record["type"] == "Person":
                            place_new.connected_persons.append(new_connection)
                        if far_record["type"] == "Organisation":
                            place_new.connected_organisations.append(new_connection)
                        if far_record["type"] == "Place":
                            place_new.connected_locations.append(new_connection)

    print("INSERTING PLACE")
    print(type(place_new))
    print(place_new)
    await db_actions.insert_record_place(place_new)

    return place_new.id


