#pylint: disable=C0115,C0303,W0212,C0116
""""
This file contains class definitions
"""
import json
from typing import Optional, List
import logging
import sys
from pydantic import 
from beanie import Document, UnionDoc, Link

logging.basicConfig(filename="general.log",level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler())
logger = logging.getLogger(__name__)


def func_logger(func):
    """
Logger for all function calls
Place as annotation befor function definition
    """
    def inner(*args, **kwargs):
        caller = sys._getframe(1)
        caller_name=caller.f_globals['__name__']
        logger.debug('       DEBUG Call func %s from %s',func.__name__,caller_name)
        ret = func(*args, **kwargs)
        # with {args, kwargs} returns {ret}
        logger.debug('       DEBUG  %s from %s done',func.__name__,caller_name)
        return ret
    return inner
class InvalidDateException(Exception):
    """
    \todo
    """


class InvalidMonthException(Exception):
    """
    \todo
    """

class InvalidDayException(Exception):
    """
    \todo
    """

class InvalidDateStringException(Exception):
    """
    \todo
    """

class InvalidDateRangeException(Exception):
    """
    \todo
    """

class PersonAgainstDuplication():
    """
    \todo
    """
# I have these classes here and not in 'classes' because they are only needed in these functions.
    preview : str = ""
#    id : str = ""
    person_type1 : str  = ""

class OrgAgainstDuplication():
    """
    \todo
    """
    preview : str = ""
#    id : str = ""
    org_type1 : str  = ""

class PlaceAgainstDuplication():
    """
    \todo
    """
    preview : str = ""
#    id : str = ""
    place_type1 : str  = ""

# class Record():
#     """
# \todo
#     """
#     type : str = ""
#     identifier : str = ""
#     metadata : Metadata = ""
#     book : BookDb = ""
#     organisation : OrganisationDb = ""
#     person : Person = ""
#     pages : PagesDb = ""
#     place : PlaceDb = ""






# class ConnectedEntityDbDisplay():
#     """
# This class is for the links of persons, organisations and places to book records
#     """
# #    id : str = ""
#     role : str = ""
#     preview : str = ""



class DateImport():
    """
This class is used for the import of dates of life or activity of persons.
Currently, it is still saved in the database, but eventually it will be replaced with a
class Date_person
    """
    datestring_raw : str = ""
    date_comments : str = ""
    datetype : str = ""
    datestring : str = ""
    date_start : tuple = ()
    date_end : tuple = ()
    date_aspect : str = ""

class Date():
    """
    Date class
    """
    date_string : str = ""
#    date_type : str = ""
# The only current plan to use it is to determinate dates of life and dates of activity of a person.
#    I can probably omit the date_type and have a separate class for dates of persons
    date_start : tuple = ()
    date_end : tuple = ()


class Dt():

    day : str = ""
    month : str = ""
    year : str = ""
    datestring : str = ""
    messages : str = ""
    state : str = ""


class DateRange():
    start : Dt = ""
    end : Dt = ""
    messages : str = ""
    state : str = ""


class Frame():
    """
    Class frame
    """
    def __str__(self):
        s="Index: "+str(self.index)+"\n"
        return s
    def to_json(self):
        """ Returns class as json """
        s=json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)
        return s
    ## Page index of the frame
    index : int = ""
    ## Absolute x position of the left bottom corner of the frame in pixels
    x_abs : int = ""
    ## Absolute y position of the left bottom corner of the frame in pixels
    y_abs : int = ""
    ## Absolute width of the frame in pixels
    w_abs : int = ""
    ## Absolute height of the frame in pixels
    h_abs : int = ""
    x_rel : float = ""
    y_rel : float = ""
    w_rel : float = ""
    h_rel : float = ""

class LinkToRepository():
    """
    This class is used for entering the link between manuscripts and repositories into the database.
It can probably be later also used for the link between artworks and repositories
    """
    number : int = 0
    #This is only needed if several former locations
    #are added later so that they can show in a sensible order (probably back in time)
    place_id : str = ""
    current : bool = True
    collection : bool = True
    # This field will be set to 'true' if the place has the type "Organisation" and t
    # he type_org1 "Collection", it will be set to 'false' if the place has the type 'Place'
    # The purpose of this field is to simplify searches.
    id_preferred : str = "" # Inventory number of shelf mark
    id_variant : str = ""



class Image():
    """
    Image class
    """
    def __str__(self):
        t="Index: "+str(self.index)+"\n"
        return t
    index : int = ""
    label_raw :  str = ""
    label_volume : str = ""
    label_prefix : str = ""
    label_page : str = ""
    width : int = ""
    height : int = ""
    baseurl : str = ""
    format : str = ""
    label : str = ""
    frames : Frame = ""


class Coordinates():
    """
This class is used for importing coordinates from the GND, it may be usable more
generally for handling this date
    """
    west : str = ""
    east : str = ""
    north : str = ""
    south : str = ""


class BibliographicId(Document):
    """
Here, the name is the name of the repertory (e.g., VD16), the id the id of a book in the repertory
and the uri the uri of the record of the book in the repertory.
This class should be superseded everywhere by External_id, I keep it for the moment just to be sure
    """
#    id : str
    uri : str = ""
    name : str = ""
    bib_id : str = ""
#    id : str = ""


class ExternalReference():
    """
This class is used for references to external IDs in bibliographic records and in authority
files such as the GND. It contains the name of the repertory (e.g., VD16, GND), the ID of the
book or person within the repertory and, if available, the URI of the entry.
    """
    uri : str = ""
    name : str = ""
    external_id : str = ""





# class PersonImport():
#     """
#     Person class for importing
#     """
#     external_id : ExternalId = ""
#     internal_id : str = ""
#     internal_id_person_type1 : str = ""
#     internal_id_person_type1_comment : str = ""
#     name_preferred : str = ""
#     name_variant : str = ""
#     sex : str = ""
#     dates_from_source : DateImport = ""
#     datestring : str = ""
#     date_start : tuple = ()
#     date_end : tuple = ()
#     date_aspect : str = ""
#     connected_persons : ConnectedEntity = ""
#     connected_organisations : ConnectedEntity = ""
#     connected_locations : ConnectedEntity = ""
#     comments : str = ""
#     preview : str = ""

class Union(UnionDoc):
    class Settings:
        name = "all_collections"
        class_id = "_class_id"

class Person(Document):
    """
 This class is used for references to persons in book records.
 id is the id of the person in authority files (currently, the GND), name the name given in the
 source and role the person's role in making the book, according to standard bibliographical
 abbreviations, e.g. "prt" for printer. If the person's ID (GND, ULAN etc.) is found to already
 have a record in the database, internal_id and internal_id_preview are filled. If the person's
 name is searched in the database, or if the person's ID or name is searched in an external
 repository such as the GND,
 The results will be put into the field 'potential candidates'.
 The user can pick one of them (or confirm if only one was found)
    """
    gnd_id : str = ""
    id_name : str = ""
    internal_id : str = ""
    internal_id_person_type1 : str = ""
    internal_id_person_type1_needed : str = ""
    internal_id_person_type1_comment : str = ""
    internal_id_preview : str = ""
    name : str = ""
    new_authority_id : str = ""
    external_id : ExternalReference = ""
    internal_id : str = ""
#    internal_id_person_type1 : str = ""
#    internal_id_person_type1_comment : str = ""
    name_preferred : str = ""
    name_variant : str = ""
    sex : str = ""
    dates_from_source : DateImport = ""
    datestring : str = ""
    date_start : tuple = ()
    date_end : tuple = ()
    date_aspect : str = ""
    #model_config = ConfigDict(arbitrary_types_allowed=True)
#    id : str = ""
#    role : str = ""
#    chosen_candidate : int = ""
#    potential_candidates : Person = ""
#    connected_persons : ConnectedEntity = ""
#    connected_organisations : ConnectedEntity = ""
#    connected_locations : ConnectedEntity = ""
    comments : str = ""
    preview : str = ""
#    id : str = ""
    type : str = "" # Is always 'Person'
    person_type1 : str = ""
    # Types 1 are: "Author", "Printer", "Artist", "Depicted Person"
    person_type2 : str = ""
    # Type 2 is a subtype only needed if type1 is "depicted Person"
    person_type3 : str = ""
    # Type 3 is a subtype only needed if typ2 is "Saint"
#    external_id : ExternalId = ""
#    name_preferred : str = ""
#    name_variant : str = ""
#    sex : str = ""
#    dates_from_source : DateImport = ""
    # This is only provisional - there will be some functions to turn the dates
    # from import into standardised dates
#    connected_persons : ConnectedEntity = ""
#    connected_organisations : ConnectedEntity = ""
#    connected_locations : ConnectedEntity = ""
#    comments : str = ""
    # At least two fields are still missing, they are not needed at this step but
    #  will be needed for records of the type1 "depicted Person":
    # 'Office' and 'Profession' (one would preferably give an office (in the widest sense)
    #  together with a term, and, if the person held no office, a profession)
#    id : str = ""
#    type : str = "" # Is always 'Person'
#    person_type1 : str = ""
    # Types 1 are: "Author", "Printer", "Artist", "Depicted Person"
#    person_type2 : str = ""
 #   # Type 2 is a subtype only needed if type1 is "depicted Person"
 #   person_type3 : str = ""
    # Type 3 is a subtype only needed if typ2 is "Saint"
#    external_id : ExternalId = ""
#    name_preferred : str = ""
#    name_variant : str = ""
#    sex : str = ""
#    dates_from_source : DateImport = ""
    # This is only provisional - there will be some functions to turn the
    # dates from import into standardised dates
#    connected_persons : ConnectedEntity = ""
#    connected_organisations : ConnectedEntity = ""
#    connected_locations : ConnectedEntity = ""
#    comments : str = ""
    class Settings:
        union_doc = Union
    # def __init__(self,name):
    #     super.__init__()
    #     self.name=name




# #@dataclass
# class PersonDb(Document):
#     """
# This class is for entering Person authority records into the database.
# It contains all needed fields (or better, will do so), so many will remain empty.
# I hope it will be possible to delete empty fields when turning it into a dict object.
# If not, one should probably have different classes for different
#     """
#     id : str = ""
#     type : str = "" # Is always 'Person'
#     person_type1 : str = ""
#     # Types 1 are: "Author", "Printer", "Artist", "Depicted Person"
#     person_type2 : str = ""
#     # Type 2 is a subtype only needed if type1 is "depicted Person"
#     person_type3 : str = ""
#     # Type 3 is a subtype only needed if typ2 is "Saint"
#     external_id : ExternalId = ""
#     name_preferred : str = ""
#     name_variant : str = ""
#     sex : str = ""
#     dates_from_source : DateImport = ""
#     # This is only provisional - there will be some functions to turn the dates
#     # from import into standardised dates
#     connected_persons : ConnectedEntity = ""
#     connected_organisations : ConnectedEntity = ""
#     connected_locations : ConnectedEntity = ""
#     comments : str = ""
#     # At least two fields are still missing, they are not needed at this step but
#     #  will be needed for records of the type1 "depicted Person":
#     # 'Office' and 'Profession' (one would preferably give an office (in the widest sense)
#     #  together with a term, and, if the person held no office, a profession)
#     class Settings:
#         union_doc = Union



# class OrganisationImport():
#     """
#  This class is used for importing data on organisations from authority records such as the GND
#     """
#     external_id : ExternalReference = ""
#     internal_id : str = ""
#     internal_id_org_type1 : str = ""
#     internal_id_org_type1_needed : str = ""
#     internal_id_org_type1_comment : str = ""
#     name_preferred : str = ""
#     name_variant : str = ""
#     dates_from_source : DateImport = ""
#     connected_persons : ConnectedEntity = ""
#     connected_organisations : ConnectedEntity = ""
#     connected_locations : ConnectedEntity = ""
#     comments : str = ""
#     preview : str = ""

class Organisation(Document):
    """
 This class is used for references to organisations (publishing houses) in book records.
 id is the id of the place in authority files (currently, the GND), name the name given the source
 and role either "pub" for the publisher, or "prt" for the printer
 If an organisation is both, there will be two different record for it.
    """
#    id : str = ""
    external_id : ExternalReference = ""
    internal_id : str = ""
    internal_id_org_type1 : str = ""
    internal_id_org_type1_needed : str = ""
    internal_id_org_type1_comment : str = ""
    name_preferred : str = ""
    name_variant : str = ""
    dates_from_source : DateImport = ""
#    connected_persons : ConnectedEntity = ""
 #   connected_organisations : ConnectedEntity = ""
 #   connected_locations : ConnectedEntity = ""
    comments : str = ""
    preview : str = ""
    id_name : str = ""
    internal_id : str = ""
    internal_id_preview : str = ""
    internal_id_org_type1 : str = ""
    internal_id_org_type1_needed : str = ""
    internal_id_org_type1_comment : str = ""
    name : str = ""
#    role : str = ""
#    chosen_candidate : int = ""
    #potential_candidates : Organisation = ""
    new_authority_id : str = ""
#    id : str = ""
    type : str = ""  # Is always "Organisation"
    org_type1: str = ""
    # Types 1 are: "Printer", "Collection", "Group of Persons"
    org_type2: str = ""
    # Type 21 is a subtype only needed if type1 is "Group of Persons",
    #  it would be e.g. 'Guild', 'Monastery', 'Ruling Body'
    external_id : ExternalReference = ""
    name_preferred : str = ""
    name_variant : str = ""
    dates_from_source : DateImport = ""
    # This is only provisional - there will be some functions to turn the dates
    #  from import into standardised dates
#    connected_persons : ConnectedEntity = ""
#    connected_organisations : ConnectedEntity = ""
#    connected_locations : ConnectedEntity = ""
    comments : str = ""
    class Settings:
        union_doc = Union



# class PlaceImport():
#     """
#  This class is used for importing data on places from authority records such as the GND
#     """
#     external_id : ExternalReference = ""
#     internal_id : str = ""
#     internal_id_place_type1 : str = ""
#     internal_id_place_type1_comment : str = ""
#     # I will need that field later, when I extend the search for matching types also do
#     # name searches in Iconobase
#     name_preferred : str = ""
#     name_variant : str = ""
#     coordinates : Coordinates = ""
#     dates_from_source : DateImport = ""
#     connected_persons : ConnectedEntity = ""
#     connected_organisations : ConnectedEntity = ""
#     connected_locations : ConnectedEntity = ""
#     comments : str = ""
#     preview : str = ""

class Place(Document):
    """
 This class is used for references to places (virtually alwys towns) in book records.
 id is the id of the place in authority files (currently, the GND), name the name given the source
 and role either "mfp" for the place of printing, or "pup" for the place of publishing.
 If a place is both, there will be two different record for it.
    """
    external_id : ExternalReference = ""
    internal_id : str = ""
    internal_id_place_type1 : str = ""
    internal_id_place_type1_comment : str = ""
    # I will need that field later, when I extend the search for matching types also do
    # name searches in Iconobase
    name_preferred : str = ""
    name_variant : str = ""
    coordinates : Coordinates = ""
    dates_from_source : DateImport = ""
#    connected_persons : ConnectedEntity = ""
#    connected_organisations : ConnectedEntity = ""
#    connected_locations : ConnectedEntity = ""
    comments : str = ""
    preview : str = ""
#    id : str = ""
#    id_name : str = ""
    internal_id : str = ""
    internal_id_preview : str = ""
    internal_id_place_type1 : str = ""
    internal_id_place_type1_needed : str = ""
    internal_id_place_type1_comment : str = ""
    name : str = ""
#    role : str = ""
#    chosen_candidate : int = ""
#    potential_candidates : PlaceImport = ""
    new_authority_id : str = ""
#    id : str = ""
    type : str = "" # Is always "Place"
    place_type1 : str = ""
    # Types 1 are: "Region - historical", "Region - modern", "Town - historical",
    # "Town - modern", "Building", "Building-part"
    # There should be only one place_type1 per record, but I keep it as list for the sake of
    # consistency
    external_id : ExternalReference = ""
    name_preferred : str = ""
    name_variant : str = ""
    coordinates : Coordinates = ""
    dates_from_source : DateImport = ""
    # This is only provisional - there will be some functions to turn the dates from import into
    # standardised dates
#    connected_persons : ConnectedEntity = ""
#    connected_organisations : ConnectedEntity = ""
#    connected_locations : ConnectedEntity = ""
    comments : str = ""
    class Settings:
        union_doc = Union


class EntityConnection(Document):
    """
    Class
    """
#    id : str = ""
    external_id : ExternalReference = ""
    name : str = ""
    connection_type : str = ""
# In the GND; the role of a connected person must be given through an abbrevation
# that gives rather general information, e.g. "bezf" = "family relation";
# more detailed information can be given in a comment field
    connection_comment : str = ""
    connection_time : str = ""
    type : str = ""
    person : Person = ""
    organisation : Organisation = ""
    place : Place = ""
    class Settings:
        union_doc = Union









# class OrganisationDb(Document):
#     """
# This class is for entering Organisation authority records into the database.
#     """
#     id : str = ""
#     type : str = ""  # Is always "Organisation"
#     org_type1: str = ""
#     # Types 1 are: "Printer", "Collection", "Group of Persons"
#     org_type2: str = ""
#     # Type 21 is a subtype only needed if type1 is "Group of Persons",
#     #  it would be e.g. 'Guild', 'Monastery', 'Ruling Body'
#     external_id : ExternalReference = ""
#     name_preferred : str = ""
#     name_variant : str = ""
#     dates_from_source : DateImport = ""
#     # This is only provisional - there will be some functions to turn the dates
#     #  from import into standardised dates
#     connected_persons : ConnectedEntity = ""
#     connected_organisations : ConnectedEntity = ""
#     connected_locations : ConnectedEntity = ""
#     comments : str = ""
#     class Settings:
#         union_doc = Union


# class PlaceDb(Document):
#     """
# This class is for entering Place authority records into the database
#     """
#     id : str = ""
#     type : str = "" # Is always "Place"
#     place_type1 : str = ""
#     # Types 1 are: "Region - historical", "Region - modern", "Town - historical",
#     # "Town - modern", "Building", "Building-part"
#     # There should be only one place_type1 per record, but I keep it as list for the sake of
#     # consistency
#     external_id : ExternalReference = ""
#     name_preferred : str = ""
#     name_variant : str = ""
#     coordinates : Coordinates = ""
#     dates_from_source : DateImport = ""
#     # This is only provisional - there will be some functions to turn the dates from import into
#     # standardised dates
#     connected_persons : ConnectedEntity = ""
#     connected_organisations : ConnectedEntity = ""
#     connected_locations : ConnectedEntity = ""
#     comments : str = ""
#     class Settings:
#         union_doc = Union







# class PersonAndConnections(Document):
#     id : str = ""
#     comment : str = ""
#     person : Person = ""
#     connected_persons : ConnectedEntity = ""
# #    connected_places : ConnectedEntity = ""
# #    connected_organisations : ConnectedEntity = ""
#     class Settings:
#         union_doc = Union

# class SelectionCandidate():
#     chosen_candidate : int = 0
#     person : Person = ""
#     person_candidates : Person = ""
#     place : Place = ""
#     place_candidates : Place = ""
#     organisation : Organisation = ""
#     organisation_candidates : Organisation = ""



class EntityAndConnections(Document):
    """
This class is for the links of persons, organisations and places to book records
    """
#    id : str = ""
    name : str = "" # This field is only a stopgap measure, if
    comment : str = ""
    preview : str = ""
    person : Person = ""
    connected_persons : EntityConnection = ""
    organisation : Organisation = ""
    connected_organisations : EntityConnection = ""
    place : Place = ""
    connected_places : EntityConnection = ""
    class Settings:
        union_doc = Union

class Role(Document):
#    id : str = ""
    role : str = ""
    name : str = "" # This field is only a stopgap measure, if
    type : str = ""
    chosen_candidate : int = 0
    comment : str = ""
    preview : str = ""
    entity_and_connections : EntityAndConnections = ""
    class Settings:
        union_doc = Union
#     def __init__(self,role,person_name):
#         self.role=role
#         p=Person(person_name)
#         self.entity_and_connections.append(p)
# #        self.entity_and_connections

def make_new_role(role,person_name):
    r=Role(role=role,chosen_candidate=-1)
    if person_name:
        r.entity_and_connections=EntityAndConnections()
        r.entity_and_connections.person=Person(name=person_name)
    return r

class MakingProcess(Document):
    """
    \todo
    """
    process_number : int = 0
    process_type : str = ""
    process_qualifier : str = ""
    person : Role = ""
    place : Role = ""
    date : Date = ""
    class Settings:
        union_doc = Union

# class MakingProcess():
#     """
#     Making process
#     """
#     process_number : int = 0
#     process_type : str = ""
#     process_qualifier : str = ""
#     person : Person = ""
#     place : Place = ""
#     date : DateImport = ""



class BibliographicInformation(Document):
    """
    Class bibliograpic information
    """
#    model_config = ConfigDict(arbitrary_types_allowed=True)
    bibliographic_id : BibliographicId = ""
    persons : Role = ""
    organisations : Role = ""
    places : Role = ""
    title: str = ""
    volume_number : str = ""
    part_title : str = ""
    printing_date : str = "" # This will be later replaced
    date_string : str = ""
    date_start : tuple = ()
    date_end : tuple = ()
    printing_information : str = ""
    class Settings:
        union_doc = Union




class Metadata(Document):
    """
    Metadata
    """
#    model_config = ConfigDict(arbitrary_types_allowed=True)
#    def __str__(self):
#        t="ID:"+self.id+"\n"
#        #t=t+"title: "+self.title+"\n"
#        t=t+"location: "+self.location+"\n"
#        t=t+"markxml: "+self.markxml+"\n"
#        t=t+"number of images: "+str(self.numberOfImages)+"\n"
#        t=t+"IIIF url"+self.iiifUrl
#        t=t+"Manifest"+self.manifest
#        return(t)
    type : str = "Manifest"
#    id : str = ""
    material : str = ""
#    repository : (dataclass.field(default_factory=list))

    repository: Role = ""
    shelfmark : str = ""
    license : str = ""
    bibliographic_id : ExternalReference = ""
    bibliographic_information : BibliographicInformation = ""
    location : str = ""
    markxml : str = ""
    numberOfImages : int = ""
    iiifUrl : str = ""
    manifest : str = ""
    images : Image = ""
    title : str = ""
    making_processes : MakingProcess = ""
    class Settings:
        union_doc = Union


class BookDb(Document):
    """
This class is for entering Book records into the database
    """
#    id : str = ""
    type : str = "Book"
    bibliographic_id : ExternalReference = ""
    persons : Role = ""
#    persons2 : Person = ""
    organisations :  Role = ""
 #   organisations2 : OrganisationDb = ""
    places :  Role = ""
 #   places2 : PlaceDb = ""
    title: str = ""
    volume_number : str = ""
    part_title : str = ""
    printing_date : str = "" # Has to be later replaced with a date object
    date_string : str = ""
    date_start : tuple = ()
    date_end : tuple = ()
    preview : str = ""
    # This preview is to be shown in lists of titles
    # - I am not sure if it will be needed long-term
    class Settings:
        union_doc = Union

class ManuscriptDb():
    """
This class is for entering Manuscript records into the database
    """
#    id : str = ""
    type : str = "Manuscript" # is always "Manuscript"
    repository : ToRepository = ""
    preview : str = ""
    # This preview is to be shown in lists of titles
    # - I am not sure if it will be needed long-term
    class Settings:
        union_doc = Union


# class ConnectedRecord():
#     """
# Class for linked Persons, Organsations, Places
#     """
#     id : str = ""
#     role : str = ""
#     name : str = "" # This field is only a stopgap measure, if
#     person : Person = ""
#     organisation : OrganisationDb = ""
#     place : PlaceDb = ""


# class BookDbDisplay():
#     """
# This class is for displaying (and perhaps later also for editing) book records from the database
#     """
#     id : str = ""
#     type : str = "Book"
#     bibliographic_id : ExternalReference = ""
#     persons :  ConnectedEntityDbDisplay = ""
#     organisations :  ConnectedEntityDbDisplay = ""
#     places :  ConnectedEntityDbDisplay = ""
#     title: str = ""
#     volume_number : str = ""
#     part_title : str = ""
#     printing_date : str = "" # Has to be later replaced with a date object
#     date_string : str = ""
#     date_start : tuple = ()
#     date_end : tuple = ()
#     preview : str = ""
#     # This preview is to be shown in lists of titles
#     # - I am not sure if it will be needed long-term

class PagesDb(Document):
    """
This class is for entering a record that contains information that will be later
needed for the individual Artwork and Photograph records
    """
#    id: str = ""
    book_record_id : str = ""
    book : BookDb = ""
    type : str = "Pages"
    repository : str = ""
    shelfmark : str = ""
    license : str = ""
    numberOfImages : int = 0
    images : Image = ""
    preview : str = ""
    making_processes : MakingProcess = ""
    class Settings:
        union_doc = Union

# class PreviewListDb():
#     """
# This class is for displaying preview and id of all manuscripts and books in Iconobase.
# It is made only as a provisional measure for display purposes, but a similar function could
# be used to access all manuscripts and books still in the ingest process
#     """
#     id : str = ""
#     type : str = ""
#     preview : str = ""
#     name_preferred : str = ""
#     title : str = ""



# class LinkToRepositoryDisplay():
#     """
# This class is used for displaying (and later also editing) the link between manuscripts
# and repositories into the database.
# It can probably be later also used for the link between artworks and repositories
#     """
#     number : int = 0
#     #This is only needed if several former locations are added later so that they can
#     # show in a sensible order (probably back in time)
#     place_id : str = ""
#     current : bool = True
#     collection : bool = True
#     # This field will be set to 'true' if the place has the type "Organisation"
#     # and the type_org1 "Collection", it will be set to 'false' if the place has the type 'Place'
#     # The purpose of this field is to simplify searches.
#     id_preferred : str = "" # Inventory number of shelf mark
#     id_variant : str = ""
#     preview : Optional[str]


# class ManuscriptDbDisplay():
#     """
# This class is for displaying (and perhaps later also for editing) manuscript records
# from the database
#     """
#     id : str = ""
#     type : str = "Manuscript" # is always "Manuscript"
#     repository : ToRepositoryDisplay = ""
#     preview : str = ""
#     # This preview is to be shown in lists of titles - I
#  am not sure if it will be needed long-term


# class PersonDbDisplay():
#     """
# This class is for displaying (and perhaps later also for editing) person records from the database
#     """
#     id : str = ""
#     type : str = "" # Is always 'Person'
#     person_type1 : str = ""
#     # Types 1 are: "Author", "Printer", "Artist", "Depicted Person"
#     person_type2 : str = ""
#     # Type 2 is a subtype only needed if type1 is "depicted Person"
#     person_type3 : str = ""
#     # Type 3 is a subtype only needed if typ2 is "Saint"
#     external_id : ExternalId = ""
#     name_preferred : str = ""
#     name_variant : str = ""
#     sex : str = ""
#     dates_from_source : DateImport = ""
#     # This is only provisional - there will be some functions to turn the
#     # dates from import into standardised dates
#     connected_persons : ConnectedEntity = ""
#     connected_organisations : ConnectedEntity = ""
#     connected_locations : ConnectedEntity = ""
#     comments : str = ""

# class OrgDbDisplay():
#     """
# This class is for displaying (and perhaps later also for editing) Organisation
# authority records from the database.
#     """
#     id : str = ""
#     type : str = ""  # Is always "Organisation"
#     org_type1: str = "" # Types 1 are
#     org_type2: str = ""
#     # Type 21 is a subtype only needed if type1 is "Group of Persons",
#     # it would be e.g. 'Guild', 'Monastery', 'Ruling Body'
#     external_id : ExternalReference = ""
#     name_preferred : str = ""
#     name_variant : str = ""
#     dates_from_source : DateImport = ""
#     # This is only provisional - there will be some functions to turn the dates
#     # from import into standardised dates
#     connected_persons : ConnectedEntity = ""
#     connected_organisations : ConnectedEntity = ""
#     connected_locations : ConnectedEntity = ""
#     comments : str = ""

# class PlaceDbDisplay():
#     """
# This class is for displaying (and perhaps later also editing) Place authority records
# from the database
#     """
#     id : str = ""
#     type : str = "" # Is always "Place"
#     place_type1 : str = ""
#     # Types 1 are: "Region - historical", "Region - modern", "Town - historical",
#     #  "Town - modern", "Building", "Building-part"
#     # There should be only one place_type1 per record, but I keep it as list for
#     # the sake of consistency
#     external_id : ExternalReference = ""
#     name_preferred : str = ""
#     name_variant : str = ""
#     coordinates : Coordinates = ""
#     dates_from_source : DateImport = ""
#     # This is only provisional - there will be some functions to turn the
#     # dates from import into standardised dates
#     connected_persons : ConnectedEntity = ""
#     connected_organisations : ConnectedEntity = ""
#     connected_locations : ConnectedEntity = ""
#     comments : str = ""
