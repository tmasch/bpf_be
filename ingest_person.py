# pylint: disable=C0301, C0303
"""
Person related business logic
"""

import re
from nanoid import generate
import classes
import db_actions
import person_relations
import parse_date
import get_external_data
import parsing_helpers


@classes.func_logger
async def ingest_person(person: classes.Entity):
    # This function is about translating the imported information of a person into the
    #  information record used for the database.
    # It directly sends the new records to the function for writing it and only
    # returns its ID to metadata_dissection

    """
    One of its roles is to 'stitch' the new entry into the system by creating connections
      to internal IDs. It does so in different steps.
        Step 1: Checking the list of connected_entities in the new record, and if one of these
        entities is already in Iconobase, inserting its ID in the connected_entities record
        (I check first, if I can do
        any stitching already with GND IDs so that I don't have to import VIAF IDs for such
        records. Hence, I first run this step close to the start, and then a second time after
        I got all the VIAF IDs. )
        Step 2: Checking if the identified connected record gives the new connected record as
          connected_entity.
            Step 2a: if yes: adding the internal ID of the new record as connected_entity
            (+ checking if the connection_types are compatible)
            Step 2b: if no: adding the connection, with a connection type that is the complement
            to the one used in the original connection
        Steps 1 and 2 happen twice: once, if a connection can already made through the default GND
        records, once, when it is necessary to download the VIAF records.
        Step 3: Check if any record already in Iconobase has a connection with the new record,
        without the new record having a connection with it.
            If yes, addition of a connection to the extant record with a complementary
            connection in the new record.
    """
#    f = open("export.txt", "w")
#    f.write(person.model_dump_json())
#    f.close()

    list_of_ids_to_check = []
    list_of_viaf_ids = []
    new_record_viaf_id = ""
    new_record_gnd_id = (
        ""  # This can be deleted once VIAF also works for organisations and places
    )
    person_found = {}
    org_found = {}
    location_found = {}

    #    connection_already_made = False
    person_selected = person.potential_candidates[person.chosen_candidate]
    print(type(person_selected))
    #    r = db_actions.find_person

    person_new = classes.Entity()
#    person_new.id = generate()
    person_new.type = "Person"
    person_new.person_type1.append(parsing_helpers.map_role_to_person_type(person.role))
    person_new.external_id = person_selected.external_id
    person_new.sex = person_selected.sex
    person_new.name_preferred = person_selected.name_preferred
    person_new.name_variant = person_selected.name_variant
    if (
        person.name not in person_new.name_variant
    ):  # Thus, the name that was used for the search is added as name variant to the iconobase.
        # This is necessary because up to now, Iconobase uses a string search for 
        # variants and not a word search.
        person_new.name_variant.append(person.name)

    for person_id in person_new.external_id:
        if person_id.name == "GND":
            new_record_gnd_id = person_id.id
            list_of_ids_to_check.append(person_id.uri)
            break
        if person_id.name == "ULAN":
            list_of_ids_to_check.append(person_id.uri)

    # new_record_gnd_id = person_selected.external_id[0].id # I need this only as long as I cannot get VIAF to work for organisations.
    # list_of_ids_to_check.append(person_new.external_id[0].uri) # The VIAF IDs added from this list will later be added to the record

    print(person_new.name_preferred)
    print(person_new.id)
    print(person_new.external_id)
    print(person_selected.connected_persons)

    # Currently, I still use the list of dates_from_source and simply add
    # the newly parsed datestring and start and end dates to it.
    #    In a later stage, the entire list will be sent to the parsing function,
    # and only one date will come back for inclusion into the database
    for date_from_source in person_selected.dates_from_source:
        date_parsed = parse_date.parse_date_overall(
            date_from_source.datestring_raw,
            date_from_source.date_comments,
            date_from_source.datetype,
        )
        datestring = date_parsed[0]
        date_start = date_parsed[1]
        date_end = date_parsed[2]
        date_aspect = date_parsed[3]
        date = classes.DateImport()
        date.datestring_raw = date_from_source.datestring_raw
        date.date_comments = date_from_source.date_comments
        date.datetype = date_from_source.datetype
        date.datestring = datestring
        date.date_start = date_start
        date.date_end = date_end
        date.date_aspect = date_aspect
        person_new.dates_from_source.append(date)

    if person_selected.connected_persons:
        # As part of the process of 'stitching' the records of connected persons together
        # with other records already dealing with these persons, I first check if connections
        # can be made via the
        # GND ID - and if not, I check the VIAF ID. Since donwloading VIAF IDs is a slow process,
        #  I try to use get them in one go through async.
        # Once I extend this to connected organisations and places, I can get their VIAF records 
        # in the same process

        # This is step 1 of the stitching process
        for connected_person in person_selected.connected_persons:
            connected_person.connection_comment, connected_person.connection_type = (
                parsing_helpers.parse_relationship(
                    "person",
                    "person",
                    connected_person.connection_comment,
                    connected_person.connection_type,
                    person_new.sex,
                )
            )
            for external_id in connected_person.external_id:
                #                person_found = coll.find_one({"external_id": {"$elemMatch": {"name": external_id.name, "id": external_id.id}}}, {"id": 1, "name_preferred" : 1, "sex" : 1, "connected_persons" : 1})
                person_found = await db_actions.find_person(external_id, "external_id")
                if person_found:
                    print("---------------------------------------------")
                    print("step 1 (GND): person connected to person found")
                    print(person_found.id + person_found.name_preferred)
                    connected_person.id = person_found.id
                    connected_person.name = person_found.name_preferred  # Here, the year must be added. One should probably rename it as 'preview'.

                    # type_correction, time_correction, comment_correction = \
                    #       db_actions.add_relationship_in_far_record(person_found,\
                    #                                                 person_new,\
                    #                                                  "connected_persons",\
                    #                                                 connected_person.connection_type,\
                    #                                                 connected_person.connection_time,\
                    #                                                 connected_person.connection_comment)
                    # This is step 2, the reciprocal connection
                    # if type_correction != "":
                    #     connected_person.connection_type = type_correction
                    # if time_correction != "":
                    #     connected_person.connection_time = time_correction
                    # if comment_correction != "":
                    #     connected_person.connection_comment = comment_correction

                    break  # if a connection with one ID is found, the other connections would be the same.

            if not person_found and connected_person.external_id:
                list_of_ids_to_check.append(
                    connected_person.external_id[0].uri
                )  # I just use the first ID given here, since all IDs should be in VIAF
                # (although the modul for getting IDs from VIAF currently only processes GND and ULAn)

    if person_selected.connected_organisations:
        for connected_org in person_selected.connected_organisations:
            connected_org.connection_comment, connected_org.connection_type = (
                parsing_helpers.parse_relationship(
                    "person",
                    "organisation",
                    connected_org.connection_comment,
                    connected_org.connection_type,
                    person_new.sex,
                )
            )
            for external_id in connected_org.external_id:
                #                org_found = coll.find_one({"external_id": {"$elemMatch": {"name": external_id.name, "id": external_id.id}}}, {"id": 1, "name_preferred" : 1, "connected_persons" : 1})
                org_found = db_actions.find_organisation(
                    external_id, "external_id_ingest"
                )
                if org_found:
                    print("---------------------------------------------")
                    print("step 1 (GND): org connected to person found")
                    connected_org.id = org_found["id"]
                    connected_org.name = org_found[
                        "name_preferred"
                    ]  # Here, the year must be added. One should probably rename it as 'preview'.
                    #                    if connected_org.connection_type in vague_connection and org_found["connection_type"] not in vague_connection:
                    #                        connected_org.connection_type = person_relations.correspoding_relationships(org_found["connection_type"], "")
                    #                    type_correction, time_correction, comment_correction = add_relationship_in_far_record(org_found, person_new, "connected_persons", connected_org.connection_type, connected_org.connection_time, connected_org.connection_comment), connected_org.connection_time # This is step 2, the reciprocal connection
                    # The following lines were inserted since inexplicably here the function returns not three strings alone, but puts them as first element into a tuple
                    type_correction, time_correction, comment_correction = (
                        # db_actions.add_relationship_in_far_record(
                        #     org_found,
                        #     person_new,
                        #     "connected_persons",
                        #     connected_org.connection_type,
                        #     connected_org.connection_time,
                        #     connected_org.connection_comment,
                        # )
                    )  # This is step 2, the reciprocal connection
                    #                    print("values returned by add_relationship_in_far_record")
                    #                    print(x)
                    #                    if len(x) == 3:
                    #                        type_correction = x[0]
                    #                        time_correction = x[1]
                    #                        comment_correction = x[2]
                    #                    elif len(x) == 2 and len(x[0]) == 3:
                    #                        type_correction = x[0][0]
                    #                        time_correction = x[0][1]
                    #                        comment_correction = x[0][2]
                    # type_correction, time_correction, comment_correction = add_relationship_in_far_record(org_found, person_new, "connected_persons", connected_org.connection_type, connected_org.connection_time, connected_org.connection_comment), connected_org.connection_time # This is step 2, the reciprocal connection

                    print("values returned from add_relationship_in_far_record")
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

    if person_selected.connected_locations:
        for connected_location in person_selected.connected_locations:
            (
                connected_location.connection_comment,
                connected_location.connection_type,
            ) = parsing_helpers.parse_relationship(
                "person",
                "location",
                connected_location.connection_comment,
                connected_location.connection_type,
                person_new.sex,
            )
            for external_id in connected_location.external_id:
                #               location_found = coll.find_one({"external_id": {"$elemMatch": {"name": external_id.name, "id": external_id.id}}}, {"id": 1, "name_preferred" : 1, "connected_persons" : 1})
                location_found = db_actions.find_place(
                    external_id, "external_id_ingest"
                )
                if location_found:
                    print("---------------------------------------------")
                    print("step 1 (GND): place connected to person found")
                    connected_location.id = location_found["id"]
                    connected_location.name = location_found["name_preferred"]
                    # type_correction, time_correction, comment_correction = (
                    #     db_actions.add_relationship_in_far_record(
                    #         location_found,
                    #         person_new,
                    #         "connected_persons",
                    #         connected_location.connection_type,
                    #         connected_location.connection_time,
                    #         connected_location.connection_comment,
                    #     )
                    # )  # This is step 2, the reciprocal connection
                    if type_correction != "":
                        connected_location.connection_type = type_correction
                    if time_correction != "":
                        connected_location.connection_time = time_correction
                    if comment_correction != "":
                        connected_location.connection_comment = comment_correction

                    break  # if a connection with one ID is found, the other connections would be the same.
            if not location_found and connected_location.external_id:
                if (
                    "-place" in connected_location.external_id[0].id
                ):  # Currently, I do not know how to further process these IDs
                    pass
                elif "-" in connected_location.external_id[0].id:
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

    # Here, I send the list of all collected IDs for which I need a VIAF ID to the function that contacts VIAF.
    list_of_viaf_ids = await get_external_data.get_viaf_from_authority(
        list_of_ids_to_check
    )
    #    print(list_of_viaf_ids)

    print("created viaf ids")
    print(list_of_viaf_ids)
    print(person_new.external_id)
    print("newly created VIAF URLs: ")
    print(list_of_viaf_ids)
    person_viaf_url = list_of_viaf_ids[person_new.external_id[0].uri]
    viaf_id = classes.ExternalReference()
    viaf_id.name = "viaf"
    viaf_id.uri = person_viaf_url
    viaf_id.id = person_viaf_url[21:]
    new_record_viaf_id = viaf_id.id  # I need this later
    person_new.external_id.append(viaf_id)
    # this has to be expanded for organisations and locations, once this is possible
    # then, to the record of the connected person

    for connected_person in person_selected.connected_persons:
        if connected_person.external_id:
            if connected_person.external_id[0].uri in list_of_viaf_ids:
                person_id = classes.ExternalReference()
                person_id.name = "viaf"
                person_viaf_url = list_of_viaf_ids[connected_person.external_id[0].uri]
                person_id.uri = person_viaf_url
                person_id.id = person_viaf_url[21:]
                connected_person.external_id.append(person_id)

    for connected_org in person_selected.connected_organisations:
        if connected_org.external_id:
            if connected_org.external_id[0].uri in list_of_viaf_ids:
                org_viaf_url = list_of_viaf_ids[connected_org.external_id[0].uri]
                org_id = classes.ExternalReference()
                org_id.name = "viaf"
                org_id.uri = org_viaf_url
                org_id.id = org_viaf_url[21:]
                connected_org.external_id.append(org_id)

    for connected_location in person_selected.connected_locations:
        if connected_location.external_id:
            if connected_location.external_id[0].uri in list_of_viaf_ids:
                location_viaf_url = list_of_viaf_ids[
                    connected_location.external_id[0].uri
                ]
                place_id = classes.ExternalReference()
                place_id.name = "viaf"
                place_id.uri = location_viaf_url
                place_id.id = location_viaf_url[21:]
                connected_location.external_id.append(place_id)

    if person_selected.connected_persons:
        for connected_person in person_selected.connected_persons:
            if (
                not connected_person.id and connected_person.external_id
            ):  # If there is already an id, no 'stitching' is required
                for external_id in connected_person.external_id:
                    if (
                        external_id.name != "DNB"
                    ):  # If it is, the connection has been made earlier
                        # This is 'stitching' step 1 for the records that can only be connected through VIAF
                        #                        person_found = coll.find_one({"external_id": {"$elemMatch": {"name": external_id.name, "id": external_id.id}}}, {"id": 1, "name_preferred" : 1, "sex" : 1, "connected_persons" : 1})
                        person_found = await db_actions.find_person(
                            external_id, "external_id_ingest"
                        )
                    if person_found:
                        print("---------------------------------------------")
                        print("step 1 (VIAF): person connected to person found")

                        connected_person.id = person_found["id"]
                        connected_person.name = person_found[
                            "name_preferred"
                        ]  # Here, the year must be added. One should probably rename it as 'preview'.
                        # if a connection with one ID is found, the other connections would be the same.
                        # type_correction, time_correction, comment_correction = (
                        #     db_actions.add_relationship_in_far_record(
                        #         person_found,
                        #         person_new,
                        #         "connected_persons",
                        #         connected_person.connection_type,
                        #         connected_person.connection_time,
                        #         connected_person.connection_comment,
                        #     )
                        # )  # This is step 2, the reciprocal connection
                        if type_correction != "":
                            connected_person.connection_type = type_correction
                        if time_correction != "":
                            connected_person.connection_time = time_correction
                        if comment_correction != "":
                            connected_person.connection_comment = comment_correction
                        break

            new_connected_person = classes.EntityConnection()
            new_connected_person.id = connected_person.id
            new_connected_person.name = connected_person.name
            new_connected_person.external_id = connected_person.external_id

            # I don't understand the next two lines and have hence commented them out and replaced them with a third line
            #            if connected_person.name == "": # if there is no preview, i.e. no connection found
            #                new_connected_person.name = connected_person.name
            new_connected_person.name = connected_person.name
            new_connected_person.connection_type = connected_person.connection_type
            new_connected_person.connection_time = connected_person.connection_time
            new_connected_person.connection_comment = (
                connected_person.connection_comment
            )
            # In theory, one should also replace this time string through a proper date object However, since I don't assume that anything will ever be made with
            # this information apart from displaying it, this is unnecessary or at least not urgent.
            person_new.connected_persons.append(new_connected_person)

    if person_selected.connected_organisations:
        for connected_organisation in person_selected.connected_organisations:
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
            person_new.connected_organisations.append(new_connected_organisation)

    connected_location_comment_is_date = r"(ab|bis|ca.|seit)?(\d \-)"  # if the comment for a connection between person and location follows this pattern, it is moved to connection time
    if person_selected.connected_locations:
        for connected_location in person_selected.connected_locations:
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
            person_new.connected_locations.append(new_connected_location)
    person_new.comments = person_selected.comments

    # Here comes step 3 of the stitching process: checking if there is any record in Iconobase that has a reference to the new record (only relevant if the new record has no reference to that record)
    # I must define what external_id is!
    # person_found = list(coll.find({"connected_persons.external_id.name": "viaf", "connected_persons.external_id.id": new_record_viaf_id.id}, {"id": 1, "name_preferred" : 1, "connected_persons" : 1}))

    #   The following line should be reinstated once every goes via VIAF, the line afterwards is a stopgap to work with both VIAF and GND
    #    person_found = list(coll.find({"connected_persons.external_id.name" : "viaf", "connected_persons.external_id.id" : new_record_viaf_id}, {"id": 1, "name_preferred" : 1, "sex": 1, "connected_persons" : 1}))
    # record with sex
    #    list_found = list(coll.find({ "$or": [{"connected_persons.external_id.name" : "viaf", "connected_persons.external_id.id" : new_record_viaf_id}, {"connected_persons.external_id.name" : "GND", "connected_persons.external_id.id" : new_record_gnd_id}]}, {"id": 1, "type" : 1, "name_preferred" : 1, "sex": 1, "connected_persons" : 1}))
    list_found = db_actions.find_person_viaf(new_record_viaf_id, new_record_gnd_id)
    print("step 3: far records found: ")
    print(list_found)

    for far_record in list_found:
        # I have to change that and rather go through every connection in far_record - I have gone through all connections in new_record before
        # check for every connected person if it has correct VIAF ID - if so, check if it has internal ID, if not > add.
        far_connected_person_list = far_record["connected_persons"]
        for far_connected_person in far_connected_person_list:
            print("connection to person in far record:")
            print(far_connected_person)
            for far_id in far_connected_person["external_id"]:
                if (
                    far_id["name"] == "viaf" and far_id["id"] == new_record_viaf_id
                ) or (far_id["name"] == "GND" and far_id["id"] == new_record_gnd_id):
                    print("connected person in far record found: ")
                    print(far_connected_person)
                    if far_connected_person["id"]:
                        print(
                            "connected person already in new record, no action necessary"
                        )
                        break  # in this case, a connection has already been established
                    else:
                        print(
                            "connected person not yet in new record, needs to be added"
                        )
                        far_connection_type = far_connected_person["connection_type"]
                        db_actions.add_connection_id_and_name(
                            far_record["id"],
                            "connected_persons",
                            far_connection_type,
                            far_connected_person["name"],
                            person_new.name_preferred,
                            person_new.id,
                            far_connection_type,
                            far_connected_person["connection_time"],
                            far_connected_person["connection_comment"],
                        )
                        new_connection = classes.EntityConnection()
                        new_connection.id = far_record["id"]
                        new_connection.name = far_record["name_preferred"]
                        new_connection.connection_type = (
                            person_relations.relation_correspondence(
                                far_connection_type, person_new.sex
                            )
                        )
                        new_connection.connection_comment = far_connected_person[
                            "connection_comment"
                        ]
                        new_connection.connection_time = far_connected_person[
                            "connection_time"
                        ]
                        print("connection time found")
                        print(far_connected_person["connection_time"])
                        #            new_connection.connection_type = "counterpart to " + far_connection_type
                        if far_record["type"] == "Person":
                            person_new.connected_persons.append(new_connection)
                        if far_record["type"] == "Organisation":
                            person_new.connected_organisations.append(new_connection)
                        if far_record["type"] == "Place":
                            person_new.connected_locations.append(new_connection)
                        break
    await db_actions.insert_atom(person_new)
    return person_new
