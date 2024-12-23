#pylint: disable=C0115,C0303,W0212,C0116,C0302
""""
This file contains class definitions
"""
import json
from typing import Optional, List
import logging
import sys
from pydantic import BaseModel
from beanie import Document, UnionDoc, Link
#import inspect

logging.basicConfig(filename="general.log",level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler())
logger = logging.getLogger("asyncio")


def func_logger(func):
    """
Logger for all function calls
Place as annotation befor function definition
    """
    def inner(*args, **kwargs):
        caller = sys._getframe(1)
        caller_name=caller.f_globals['__name__']
        module=sys.modules[func.__module__]
        logger.debug('       DEBUG %s in %s from %s async called',func.__name__,module,caller_name)
        ret = func(*args, **kwargs)
        # with {args, kwargs} returns {ret}
        logger.debug('       DEBUG  %s from %s done',func.__name__,caller_name)
        return ret
    return inner

def async_func_logger(func):
    """
Logger for all function calls
Place as annotation befor function definition
    """
    async def inner(*args, **kwargs):
        caller = sys._getframe(1)
        caller_name=caller.f_globals['__name__']
#        module=inspect.getmodule(func)
        module=sys.modules[func.__module__]
        logger.debug('       DEBUG %s in %s from %s async called',func.__name__,module,caller_name)
        ret = await func(*args, **kwargs)
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

class PersonAgainstDuplication(BaseModel):
    """
    \todo
    """
# I have these classes here and not in 'classes' because they are only needed in these functions.
    preview : Optional[str] = ""
#    id : Optional[str] = ""
    person_type1 : Optional[list[str]]  = []

class OrgAgainstDuplication(BaseModel):
    """
    \todo
    """
    preview : Optional[str] = ""
#    id : Optional[str] = ""
    org_type1 : Optional[list[str]]  = []

class PlaceAgainstDuplication(BaseModel):
    """
    \todo
    """
    preview : Optional[str] = ""
#    id : Optional[str] = ""
    place_type1 : Optional[list[str]]  = []

# class Record(BaseModel):
#     """
# \todo
#     """
#     type : str = ""
#     identifier : str = ""
#     metadata : Optional[Metadata] = ""
#     book : Optional[BookDb] = ""
#     organisation : Optional[OrganisationDb] = ""
#     person : Optional[Person] = ""
#     pages : Optional[PagesDb] = ""
#     place : Optional[PlaceDb] = ""






# class ConnectedEntityDbDisplay(BaseModel):
#     """
# This class is for the links of persons, organisations and places to book records
#     """
# #    id : Optional[str] = ""
#     role : Optional[str] = ""
#     preview : Optional[str] = ""



class DateImport(BaseModel):
    """
This class is used for the import of dates of life or activity of persons. 
Currently, it is still saved in the database, but eventually it will be replaced with a 
class Date_person
    """
    datestring_raw : Optional[str] = ""
    date_comments : Optional[str] = ""
    datetype : Optional[str] = ""
    datestring : Optional[str] = ""
    date_start : Optional[tuple] = ()
    date_end : Optional[tuple] = ()
    date_aspect : Optional[str] = ""

class Date(BaseModel):
    """
    Date class
    """
    date_string : Optional[str] = ""
#    date_type : Optional[str] = ""
# The only current plan to use it is to determinate dates of life and dates of activity of a person.
#    I can probably omit the date_type and have a separate class for dates of persons
    date_start : Optional[tuple] = ()
    date_end : Optional[tuple] = ()


class Dt(BaseModel):

    day : Optional[str] = None
    month : Optional[str] = None
    year : Optional[str] = None
    datestring : Optional[str] = ""
    messages : Optional[str] = ""
    state : Optional[str] = ""


class DateRange(BaseModel):
    start : Optional[Dt] = None
    end : Optional[Dt] = None
    messages : Optional[str] = ""
    state : Optional[str] = ""


class Frame(BaseModel):
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
    index : Optional[int] = ""
    ## Absolute x position of the left bottom corner of the frame in pixels
    x_abs : Optional[int] = ""
    ## Absolute y position of the left bottom corner of the frame in pixels
    y_abs : Optional[int] = ""
    ## Absolute width of the frame in pixels
    w_abs : Optional[int] = ""
    ## Absolute height of the frame in pixels
    h_abs : Optional[int] = ""
    x_rel : Optional[float] = ""
    y_rel : Optional[float] = ""
    w_rel : Optional[float] = ""
    h_rel : Optional[float] = ""

class LinkToRepository(BaseModel):
    """
    This class is used for entering the link between manuscripts and repositories into the database. 
It can probably be later also used for the link between artworks and repositories
    """
    number : Optional[int] = 0
    #This is only needed if several former locations
    #are added later so that they can show in a sensible order (probably back in time)
    place_id : Optional[str] = ""
    current : Optional[bool] = True
    collection : Optional[bool] = True
    # This field will be set to 'true' if the place has the type "Organisation" and t
    # he type_org1 "Collection", it will be set to 'false' if the place has the type 'Place'
    # The purpose of this field is to simplify searches.
    id_preferred : Optional[str] = "" # Inventory number of shelf mark
    id_variant : Optional[list[str]] = []



class Image(BaseModel):
    """
    Image class
    """
    def __str__(self):
        t="Index: "+str(self.index)+"\n"
        return t
    index : Optional[int] = ""
    label_raw :  Optional[str] = ""
    label_volume : Optional[str] = ""
    label_prefix : Optional[str] = ""
    label_page : Optional[str] = ""
    width : Optional[int] = ""
    height : Optional[int] = ""
    baseurl : Optional[str] = ""
    format : Optional[str] = ""
    label : Optional[str] = ""
    frames : Optional[list[Frame]] = []


class Coordinates(BaseModel):
    """
This class is used for importing coordinates from the GND, it may be usable more 
generally for handling this date
    """
    west : Optional[str] = ""
    east : Optional[str] = ""
    north : Optional[str] = ""
    south : Optional[str] = ""


class BibliographicId(Document):
    """
Here, the name is the name of the repertory (e.g., VD16), the id the id of a book in the repertory
and the uri the uri of the record of the book in the repertory.
This class should be superseded everywhere by External_id, I keep it for the moment just to be sure
    """
#    id : str
    uri : Optional[str] = ""
    name : Optional[str] = ""
    bib_id : Optional[str] = "" 
#    id : Optional[str] = ""


class ExternalReference(BaseModel):
    """
This class is used for references to external IDs in bibliographic records and in authority 
files such as the GND. It contains the name of the repertory (e.g., VD16, GND), the ID of the 
book or person within the repertory and, if available, the URI of the entry. 
    """
    uri : Optional[str] = ""
    name : Optional[str] = ""
    external_id : Optional[str] = ""





# class PersonImport(BaseModel):
#     """
#     Person class for importing
#     """
#     external_id : Optional[list[ExternalId]] = []
#     internal_id : Optional[str] = ""
#     internal_id_person_type1 : Optional[list[str]] = []
#     internal_id_person_type1_comment : Optional[str] = ""
#     name_preferred : Optional[str] = ""
#     name_variant : Optional[list[str]] = []
#     sex : Optional[str] = ""
#     dates_from_source : Optional[list[DateImport]] = []
#     datestring : Optional[str] = ""
#     date_start : Optional[tuple] = ()
#     date_end : Optional[tuple] = ()
#     date_aspect : Optional[str] = ""
#     connected_persons : Optional[list[ConnectedEntity]] = []
#     connected_organisations : Optional[list[ConnectedEntity]] = []
#     connected_locations : Optional[list[ConnectedEntity]] = []
#     comments : Optional[str] = ""
#     preview : Optional[str] = ""

class Union(UnionDoc):
    class Settings:
        name = "all_collections"
        class_id = "_class_id"

class Entity(Document):
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
    gnd_id : Optional[str] = ""
    id_name : Optional[str] = ""
    stub : Optional[bool] = True
    internal_id : Optional[str] = ""
    internal_id_person_type1 : Optional[list[str]] = []
    internal_id_person_type1_needed : Optional[str] = ""
    internal_id_person_type1_comment : Optional[str] = ""
    internal_id_preview : Optional[str] = ""
    name : Optional[str] = ""
    new_authority_id : Optional[str] = ""
    external_id : Optional[list[ExternalReference]] = []
    internal_id : Optional[str] = ""
#    internal_id_person_type1 : Optional[list[str]] = []
#    internal_id_person_type1_comment : Optional[str] = ""
    name_preferred : Optional[str] = ""
    name_variant : Optional[list[str]] = []
    sex : Optional[str] = ""
    dates_from_source : Optional[list[DateImport]] = []
    datestring : Optional[str] = ""
    date_start : Optional[tuple] = ()
    date_end : Optional[tuple] = ()
    date_aspect : Optional[str] = ""
    #model_config = ConfigDict(arbitrary_types_allowed=True)
#    id : Optional[str] = ""
#    role : Optional[str] = ""
#    chosen_candidate : Optional[int] = ""
#    potential_candidates : Optional[list[Person]] = []
#    connected_persons : Optional[list[ConnectedEntity]] = []
#    connected_organisations : Optional[list[ConnectedEntity]] = []
#    connected_locations : Optional[list[ConnectedEntity]] = []
    comments : Optional[str] = ""
    preview : Optional[str] = ""
#    id : Optional[str] = ""
    type : Optional[str] = "" # Is always 'Person'
#    properties : Optional[dict] = {}
    person_type1 : Optional[list[str]] = []
    # Types 1 are: "Author", "Printer", "Artist", "Depicted Person"
    person_type2 : Optional[list[str]] = []
    # Type 2 is a subtype only needed if type1 is "depicted Person"
    person_type3 : Optional[list[str]] = []
    # Type 3 is a subtype only needed if typ2 is "Saint"
#    external_id : Optional[list[ExternalId]] = []
#    name_preferred : Optional[str] = ""
#    name_variant : Optional[list[str]] = []
#    sex : Optional[str] = ""
#    dates_from_source : Optional[list[DateImport]] = []
    # This is only provisional - there will be some functions to turn the dates
    # from import into standardised dates
#    connected_persons : Optional[list[ConnectedEntity]] = []
#    connected_organisations : Optional[list[ConnectedEntity]] = []
#    connected_locations : Optional[list[ConnectedEntity]] = []
#    comments : Optional[str] = ""
    # At least two fields are still missing, they are not needed at this step but
    #  will be needed for records of the type1 "depicted Person":
    # 'Office' and 'Profession' (one would preferably give an office (in the widest sense)
    #  together with a term, and, if the person held no office, a profession)
#    id : Optional[str] = ""
#    type : Optional[str] = "" # Is always 'Person'
#    person_type1 : Optional[list[str]] = []
    # Types 1 are: "Author", "Printer", "Artist", "Depicted Person"
#    person_type2 : Optional[list[str]] = []
 #   # Type 2 is a subtype only needed if type1 is "depicted Person"
 #   person_type3 : Optional[list[str]] = []
    # Type 3 is a subtype only needed if typ2 is "Saint"
#    external_id : Optional[list[ExternalId]] = []
#    name_preferred : Optional[str] = ""
#    name_variant : Optional[list[str]] = []
#    sex : Optional[str] = ""
#    dates_from_source : Optional[list[DateImport]] = []
    # This is only provisional - there will be some functions to turn the
    # dates from import into standardised dates
#    connected_persons : Optional[list[ConnectedEntity]] = []
#    connected_organisations : Optional[list[ConnectedEntity]] = []
#    connected_locations : Optional[list[ConnectedEntity]] = []
#    comments : Optional[str] = ""
    class Settings:
        union_doc = Union

# class Organisation(Document):
#     """
#  This class is used for references to organisations (publishing houses) in book records. 
#  id is the id of the place in authority files (currently, the GND), name the name given the source
#  and role either "pub" for the publisher, or "prt" for the printer
#  If an organisation is both, there will be two different record for it. 
#     """
# #    id : Optional[str] = ""
#     external_id : Optional[list[ExternalReference]] = []
#     internal_id : Optional[str] = ""
#     internal_id_org_type1 : Optional[list[str]] = []
#     internal_id_org_type1_needed : Optional[str] = ""
#     internal_id_org_type1_comment : Optional[str] = ""
#     name_preferred : Optional[str] = ""
#     name_variant : Optional[list[str]] = []
#     dates_from_source : Optional[list[DateImport]] = []
# #    connected_persons : Optional[list[ConnectedEntity]] = []
#  #   connected_organisations : Optional[list[ConnectedEntity]] = []
#  #   connected_locations : Optional[list[ConnectedEntity]] = []
#     comments : Optional[str] = ""
#     preview : Optional[str] = ""
#     id_name : Optional[str] = ""
#     internal_id : Optional[str] = ""
#     internal_id_preview : Optional[str] = ""
#     internal_id_org_type1 : Optional[list[str]] = []
#     internal_id_org_type1_needed : Optional[str] = ""
#     internal_id_org_type1_comment : Optional[str] = ""
#     name : Optional[str] = ""
# #    role : Optional[str] = ""
# #    chosen_candidate : Optional[int] = ""
#     #potential_candidates : Optional[list[Organisation]] = []
#     new_authority_id : Optional[str] = ""
# #    id : Optional[str] = ""
#     type : Optional[str] = ""  # Is always "Organisation"
#     org_type1: Optional[list[str]] = []
#     # Types 1 are: "Printer", "Collection", "Group of Persons"
#     org_type2: Optional[list[str]] = []
#     # Type 21 is a subtype only needed if type1 is "Group of Persons",
#     #  it would be e.g. 'Guild', 'Monastery', 'Ruling Body'
#     class Settings:
#         union_doc = Union
#     # def __init__(self,name):
#     #     super.__init__()
#     #     self.name=name




# #@dataclass
# class PersonDb(Document):
#     """
# This class is for entering Person authority records into the database. 
# It contains all needed fields (or better, will do so), so many will remain empty. 
# I hope it will be possible to delete empty fields when turning it into a dict object. 
# If not, one should probably have different classes for different 
#     """
#     id : Optional[str] = ""
#     type : Optional[str] = "" # Is always 'Person'
#     person_type1 : Optional[list[str]] = []
#     # Types 1 are: "Author", "Printer", "Artist", "Depicted Person"
#     person_type2 : Optional[list[str]] = []
#     # Type 2 is a subtype only needed if type1 is "depicted Person"
#     person_type3 : Optional[list[str]] = []
#     # Type 3 is a subtype only needed if typ2 is "Saint"
#     external_id : Optional[list[ExternalId]] = []
#     name_preferred : Optional[str] = ""
#     name_variant : Optional[list[str]] = []
#     sex : Optional[str] = ""
#     dates_from_source : Optional[list[DateImport]] = []
#     # This is only provisional - there will be some functions to turn the dates
#     # from import into standardised dates
#     connected_persons : Optional[list[ConnectedEntity]] = []
#     connected_organisations : Optional[list[ConnectedEntity]] = []
#     connected_locations : Optional[list[ConnectedEntity]] = []
#     comments : Optional[str] = ""
#     # At least two fields are still missing, they are not needed at this step but
#     #  will be needed for records of the type1 "depicted Person":
#     # 'Office' and 'Profession' (one would preferably give an office (in the widest sense)
#     #  together with a term, and, if the person held no office, a profession)
#     class Settings:
#         union_doc = Union



# class OrganisationImport(BaseModel):
#     """
#  This class is used for importing data on organisations from authority records such as the GND
#     """
#     external_id : Optional[list[ExternalReference]] = []
#     internal_id : Optional[str] = ""
#     internal_id_org_type1 : Optional[list[str]] = []
#     internal_id_org_type1_needed : Optional[str] = ""
#     internal_id_org_type1_comment : Optional[str] = ""
#     name_preferred : Optional[str] = ""
#     name_variant : Optional[list[str]] = []
#     dates_from_source : Optional[list[DateImport]] = []
#     connected_persons : Optional[list[ConnectedEntity]] = []
#     connected_organisations : Optional[list[ConnectedEntity]] = []
#     connected_locations : Optional[list[ConnectedEntity]] = []
#     comments : Optional[str] = ""
#     preview : Optional[str] = ""

# class Organisation(Document):
#     """
#  This class is used for references to organisations (publishing houses) in book records. 
#  id is the id of the place in authority files (currently, the GND), name the name given the source
#  and role either "pub" for the publisher, or "prt" for the printer
#  If an organisation is both, there will be two different record for it. 
#     """
# #    id : Optional[str] = ""
#     external_id : Optional[list[ExternalReference]] = []
#     internal_id : Optional[str] = ""
#     internal_id_org_type1 : Optional[list[str]] = []
#     internal_id_org_type1_needed : Optional[str] = ""
#     internal_id_org_type1_comment : Optional[str] = ""
#     name_preferred : Optional[str] = ""
#     name_variant : Optional[list[str]] = []
#     dates_from_source : Optional[list[DateImport]] = []
# #    connected_persons : Optional[list[ConnectedEntity]] = []
#  #   connected_organisations : Optional[list[ConnectedEntity]] = []
#  #   connected_locations : Optional[list[ConnectedEntity]] = []
#     comments : Optional[str] = ""
#     preview : Optional[str] = ""
#     id_name : Optional[str] = ""
#     internal_id : Optional[str] = ""
#     internal_id_preview : Optional[str] = ""
#     internal_id_org_type1 : Optional[list[str]] = []
#     internal_id_org_type1_needed : Optional[str] = ""
#     internal_id_org_type1_comment : Optional[str] = ""
#     name : Optional[str] = ""
# #    role : Optional[str] = ""
# #    chosen_candidate : Optional[int] = ""
#     #potential_candidates : Optional[list[Organisation]] = []
#     new_authority_id : Optional[str] = ""
# #    id : Optional[str] = ""
#     type : Optional[str] = ""  # Is always "Organisation"
#     org_type1: Optional[list[str]] = []
#     # Types 1 are: "Printer", "Collection", "Group of Persons"
#     org_type2: Optional[list[str]] = []
#     # Type 21 is a subtype only needed if type1 is "Group of Persons",
#     #  it would be e.g. 'Guild', 'Monastery', 'Ruling Body'
#     external_id : Optional[list[ExternalReference]] = []
#     name_preferred : Optional[str] = ""
#     name_variant : Optional[list[str]] = []
#     dates_from_source : Optional[list[DateImport]] = []
#     # This is only provisional - there will be some functions to turn the dates
#     #  from import into standardised dates
# #    connected_persons : Optional[list[ConnectedEntity]] = []
# #    connected_organisations : Optional[list[ConnectedEntity]] = []
# #    connected_locations : Optional[list[ConnectedEntity]] = []
#     comments : Optional[str] = ""
#     class Settings:
#         union_doc = Union



# class PlaceImport(BaseModel):
#     """
#  This class is used for importing data on places from authority records such as the GND    
#     """
#     external_id : Optional[list[ExternalReference]] = []
#     internal_id : Optional[str] = ""
#     internal_id_place_type1 : Optional[list[str]] = []
#     internal_id_place_type1_comment : Optional[str] = ""
#     # I will need that field later, when I extend the search for matching types also do
#     # name searches in Iconobase
#     name_preferred : Optional[str] = ""
#     name_variant : Optional[list[str]] = []
#     coordinates : Optional[list[Coordinates]] = []
#     dates_from_source : Optional[list[DateImport]] = []
#     connected_persons : Optional[list[ConnectedEntity]] = []
#     connected_organisations : Optional[list[ConnectedEntity]] = []
#     connected_locations : Optional[list[ConnectedEntity]] = []
#     comments : Optional[str] = ""
#     preview : Optional[str] = ""

# class Place(Document):
#     """
#  This class is used for references to places (virtually alwys towns) in book records.
#  id is the id of the place in authority files (currently, the GND), name the name given the source
#  and role either "mfp" for the place of printing, or "pup" for the place of publishing. 
#  If a place is both, there will be two different record for it. 
#     """
#     external_id : Optional[list[ExternalReference]] = []
#     internal_id : Optional[str] = ""
#     internal_id_place_type1 : Optional[list[str]] = []
#     internal_id_place_type1_comment : Optional[str] = ""
#     # I will need that field later, when I extend the search for matching types also do
#     # name searches in Iconobase
#     name_preferred : Optional[str] = ""
#     name_variant : Optional[list[str]] = []
#     coordinates : Optional[list[Coordinates]] = []
#     dates_from_source : Optional[list[DateImport]] = []
# #    connected_persons : Optional[list[ConnectedEntity]] = []
# #    connected_organisations : Optional[list[ConnectedEntity]] = []
# #    connected_locations : Optional[list[ConnectedEntity]] = []
#     comments : Optional[str] = ""
#     preview : Optional[str] = ""
# #    id : Optional[str] = ""
# #    id_name : Optional[str] = ""
#     internal_id : Optional[str] = ""
#     internal_id_preview : Optional[str] = ""
#     internal_id_place_type1 : Optional[list[str]] = []
#     internal_id_place_type1_needed : Optional[str] = ""
#     internal_id_place_type1_comment : Optional[str] = ""
#     name : Optional[str] = ""
# #    role : Optional[str] = ""
# #    chosen_candidate : Optional[int] = ""
# #    potential_candidates : Optional[list[PlaceImport]] = []
#     new_authority_id : Optional[str] = ""
# #    id : Optional[str] = ""
#     type : Optional[str] = "" # Is always "Place"
#     place_type1 : Optional[list[str]] = []
#     # Types 1 are: "Region - historical", "Region - modern", "Town - historical",
#     # "Town - modern", "Building", "Building-part"
#     # There should be only one place_type1 per record, but I keep it as list for the sake of
#     # consistency
#     external_id : Optional[list[ExternalReference]] = []
#     name_preferred : Optional[str] = ""
#     name_variant : Optional[list[str]] = []
#     coordinates : Optional[list[Coordinates]] = []
#     dates_from_source : Optional[list[DateImport]] = []
#     # This is only provisional - there will be some functions to turn the dates from import into
#     # standardised dates
# #    connected_persons : Optional[list[ConnectedEntity]] = []
# #    connected_organisations : Optional[list[ConnectedEntity]] = []
# #    connected_locations : Optional[list[ConnectedEntity]] = []
#     comments : Optional[str] = ""
#     class Settings:
#         union_doc = Union


class EntityConnection(Document):
    """
    Class 
    """
#    id : Optional[str] = ""
    external_id : Optional[List[ExternalReference]] = []
    name : Optional[str] = "" # Name of the person, place or organisation for easier access
    connection_type : Optional[str] = "" # either person, place or organisation
# In the GND; the role of a connected person must be given through an abbrevation
# that gives rather general information, e.g. "bezf" = "family relation";
# more detailed information can be given in a comment field
    connection_comment : Optional[str] = ""
    connection_time : Optional[str] = ""
    type : Optional[str] = ""
    entityA : Optional[Link[Entity]] = None
    entityB : Optional[Link[Entity]] = None

    relationA : Optional[str] = ""
    relationB : Optional[str] = ""
#    person : Optional[Link[Person]] = None
#    personA : Optional[Link[Person]] = None
#    personB : Optional[Link[Person]] = None
#    organisationA : Optional[Link[Organisation]] = None
#    organisationB : Optional[Link[Organisation]] = None
#    placeA : Optional[Link[Place]] = None
#    placeB : Optional[Link[Place]] = None
    class Settings:
        union_doc = Union









# class OrganisationDb(Document):
#     """
# This class is for entering Organisation authority records into the database. 
#     """
#     id : Optional[str] = ""
#     type : Optional[str] = ""  # Is always "Organisation"
#     org_type1: Optional[list[str]] = []
#     # Types 1 are: "Printer", "Collection", "Group of Persons"
#     org_type2: Optional[list[str]] = []
#     # Type 21 is a subtype only needed if type1 is "Group of Persons",
#     #  it would be e.g. 'Guild', 'Monastery', 'Ruling Body'
#     external_id : Optional[list[ExternalReference]] = []
#     name_preferred : Optional[str] = ""
#     name_variant : Optional[list[str]] = []
#     dates_from_source : Optional[list[DateImport]] = []
#     # This is only provisional - there will be some functions to turn the dates
#     #  from import into standardised dates
#     connected_persons : Optional[list[ConnectedEntity]] = []
#     connected_organisations : Optional[list[ConnectedEntity]] = []
#     connected_locations : Optional[list[ConnectedEntity]] = []
#     comments : Optional[str] = ""
#     class Settings:
#         union_doc = Union


# class PlaceDb(Document):
#     """
# This class is for entering Place authority records into the database
#     """
#     id : Optional[str] = ""
#     type : Optional[str] = "" # Is always "Place"
#     place_type1 : Optional[list[str]] = ""
#     # Types 1 are: "Region - historical", "Region - modern", "Town - historical",
#     # "Town - modern", "Building", "Building-part"
#     # There should be only one place_type1 per record, but I keep it as list for the sake of
#     # consistency
#     external_id : Optional[list[ExternalReference]] = []
#     name_preferred : Optional[str] = ""
#     name_variant : Optional[list[str]] = []
#     coordinates : Optional[list[Coordinates]] = []
#     dates_from_source : Optional[list[DateImport]] = []
#     # This is only provisional - there will be some functions to turn the dates from import into
#     # standardised dates
#     connected_persons : Optional[list[ConnectedEntity]] = []
#     connected_organisations : Optional[list[ConnectedEntity]] = []
#     connected_locations : Optional[list[ConnectedEntity]] = []
#     comments : Optional[str] = ""
#     class Settings:
#         union_doc = Union







# class PersonAndConnections(Document):
#     id : str = ""
#     comment : Optional[str] = ""
#     person : Link[Person] = None
#     connected_persons : Optional[List[Link[ConnectedEntity]]] = []
# #    connected_places : Optional[list[Link[ConnectedEntity]]] = []
# #    connected_organisations : Optional[list[Link[ConnectedEntity]]] = []
#     class Settings:
#         union_doc = Union

# class SelectionCandidate(BaseModel):
#     chosen_candidate : Optional[int] = 0
#     person : Optional[Person] = None
#     person_candidates : Optional[list[Person]] = []
#     place : Optional[Place] = None
#     place_candidates : Optional[list[Place]] = []
#     organisation : Optional[Organisation] = None
#     organisation_candidates : Optional[list[Organisation]] = []



class EntityAndConnections(Document):
    """
This class is for the links of persons, organisations and places to book records
    """
    name : Optional[str] = "" # This field is only a stopgap measure, if
    comment : Optional[str] = ""
    preview : Optional[str] = ""
    entity : Optional[Link[Entity]] = None
    connected_entities : Optional[List[Link[EntityConnection]]] = []
    class Settings:
        union_doc = Union

class Role(Document):
    role : Optional[str] = ""
    name : Optional[str] = "" # This field is only a stopgap measure, if
    type : Optional[str] = ""
    chosen_candidate_id : Optional[int] = 0
    comment : Optional[str] = ""
    preview : Optional[str] = ""
    entity_and_connections : Optional[Link[EntityAndConnections]] = None
    class Settings:
        union_doc = Union

def make_new_role(role,person_name):
    r=Role(role=role,chosen_candidate=-1)
    if person_name:
        r.entity_and_connections=EntityAndConnections()
        r.entity_and_connections.entity=Entity(name=person_name)
    return r

class MakingProcess(Document):
    """
    \todo
    """
    process_number : Optional[int] = 0
    process_type : Optional[str] = ""
    process_qualifier : Optional[str] = ""
    person : Optional[Role] = None
    place : Optional[Role] = None
    date : Optional[Date] = None
    class Settings:
        union_doc = Union

# class MakingProcess(BaseModel):
#     """
#     Making process
#     """
#     process_number : Optional[int] = 0
#     process_type : Optional[str] = ""
#     process_qualifier : Optional[str] = ""
#     person : Optional[Person] = None
#     place : Optional[Place] = None
#     date : Optional[DateImport] = None



class BibliographicInformation(Document):
    """
    Class bibliograpic information
    """
#    model_config = ConfigDict(arbitrary_types_allowed=True)
    bibliographic_id : Optional[List[BibliographicId]] = []
    persons : Optional[List[Link[Role]]] = []
    organisations : Optional[List[Link[Role]]] = []
    places : Optional[List[Link[Role]]] = []
    title: Optional[str] = ""
    volume_number : Optional[str] = ""
    part_title : Optional[str] = ""
    printing_date : Optional[str] = "" # This will be later replaced
    date_string : Optional[str] = ""
    date_start : Optional[tuple] = ()
    date_end : Optional[tuple] = ()
    printing_information : Optional[str] = ""
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
    type : Optional[str] = "Manifest"
#    id : Optional[str] = ""
    material : Optional[str] = ""
#    repository : Optional(dataclass.field(default_factory=list))

    repository: Optional[Link[Role]] = None
    shelfmark : Optional[str] = ""
    license : Optional[str] = ""
    bibliographic_id : Optional[list[ExternalReference]] = []
    bibliographic_information : Optional[List[Link[BibliographicInformation]]] = []
    location : Optional[str] = ""
    markxml : Optional[str] = ""
    numberOfImages : Optional[int] = 0
    iiifUrl : Optional[str] = ""
    manifest : Optional[str] = ""
    images : Optional[list[Image]] = []
    title : Optional[str] = ""
    making_processes : Optional[List[MakingProcess]] = []
    class Settings:
        union_doc = Union


class BookDb(Document):
    """
This class is for entering Book records into the database
    """
#    id : Optional[str] = ""
    type : Optional[str] = "Book"
    bibliographic_id : Optional[list[ExternalReference]] = []
    persons : Optional[list[Link[Role]]] = []
#    persons2 : Optional[list[Link[Person]]] = ""
    organisations : Optional[list [Link[Role]]] = []
 #   organisations2 : Optional[list[Link[OrganisationDb]]] = ""
    places : Optional[list [Role]] = []
 #   places2 : Optional[list[Link[PlaceDb]]] = ""
    title: Optional[str] = ""
    volume_number : Optional[str] = ""
    part_title : Optional[str] = ""
    printing_date : Optional[str] = "" # Has to be later replaced with a date object
    date_string : Optional[str] = ""
    date_start : Optional[tuple] = ()
    date_end : Optional[tuple] = ()
    preview : Optional[str] = ""
    # This preview is to be shown in lists of titles
    # - I am not sure if it will be needed long-term
    class Settings:
        union_doc = Union

class ManuscriptDb(BaseModel):
    """
This class is for entering Manuscript records into the database
    """
#    id : Optional[str] = ""
    type : Optional[str] = "Manuscript" # is always "Manuscript"
    repository : Optional[list[LinkToRepository]] = []
    preview : Optional[str] = ""
    # This preview is to be shown in lists of titles
    # - I am not sure if it will be needed long-term
    class Settings:
        union_doc = Union


# class ConnectedRecord(BaseModel):
#     """
# Class for linked Persons, Organsations, Places
#     """
#     id : Optional[str] = ""
#     role : Optional[str] = ""
#     name : Optional[str] = "" # This field is only a stopgap measure, if
#     person : Optional[Link[Person]] = None
#     organisation : Optional[Link[OrganisationDb]] = None
#     place : Optional[Link[PlaceDb]] = None


# class BookDbDisplay(BaseModel):
#     """
# This class is for displaying (and perhaps later also for editing) book records from the database
#     """
#     id : Optional[str] = ""
#     type : Optional[str] = "Book"
#     bibliographic_id : Optional[list[ExternalReference]] = []
#     persons : Optional[list [ConnectedEntityDbDisplay]] = []
#     organisations : Optional[list [ConnectedEntityDbDisplay]] = []
#     places : Optional[list [ConnectedEntityDbDisplay]] = []
#     title: Optional[str] = ""
#     volume_number : Optional[str] = ""
#     part_title : Optional[str] = ""
#     printing_date : Optional[str] = "" # Has to be later replaced with a date object
#     date_string : Optional[str] = ""
#     date_start : Optional[tuple] = ()
#     date_end : Optional[tuple] = ()
#     preview : Optional[str] = ""
#     # This preview is to be shown in lists of titles
#     # - I am not sure if it will be needed long-term

class PagesDb(Document):
    """
This class is for entering a record that contains information that will be later 
needed for the individual Artwork and Photograph records
    """
#    id: Optional[str] = ""
    book_record_id : Optional[str] = ""
    book : Optional[Link[BookDb]] = ""
    type : Optional[str] = "Pages"
    repository : Optional[str] = ""
    shelfmark : Optional[str] = ""
    license : Optional[str] = ""
    numberOfImages : Optional[int] = 0
    images : Optional[list[Image]] = []
    preview : Optional[str] = ""
    making_processes : Optional[list[MakingProcess]] = []
    class Settings:
        union_doc = Union

# class PreviewListDb(BaseModel):
#     """
# This class is for displaying preview and id of all manuscripts and books in Iconobase.
# It is made only as a provisional measure for display purposes, but a similar function could 
# be used to access all manuscripts and books still in the ingest process
#     """
#     id : Optional[str] = ""
#     type : Optional[str] = ""
#     preview : Optional[str] = ""
#     name_preferred : Optional[str] = ""
#     title : Optional[str] = ""



# class LinkToRepositoryDisplay(BaseModel):
#     """
# This class is used for displaying (and later also editing) the link between manuscripts 
# and repositories into the database. 
# It can probably be later also used for the link between artworks and repositories
#     """
#     number : Optional[int] = 0
#     #This is only needed if several former locations are added later so that they can
#     # show in a sensible order (probably back in time)
#     place_id : Optional[str] = ""
#     current : Optional[bool] = True
#     collection : Optional[bool] = True
#     # This field will be set to 'true' if the place has the type "Organisation"
#     # and the type_org1 "Collection", it will be set to 'false' if the place has the type 'Place'
#     # The purpose of this field is to simplify searches.
#     id_preferred : Optional[str] = "" # Inventory number of shelf mark
#     id_variant : Optional[list[str]] = []
#     preview : Optional[str]


# class ManuscriptDbDisplay(BaseModel):
#     """
# This class is for displaying (and perhaps later also for editing) manuscript records 
# from the database
#     """
#     id : Optional[str] = ""
#     type : Optional[str] = "Manuscript" # is always "Manuscript"
#     repository : Optional[list[LinkToRepositoryDisplay]] = []
#     preview : Optional[str] = ""
#     # This preview is to be shown in lists of titles - I
#  am not sure if it will be needed long-term


# class PersonDbDisplay(BaseModel):
#     """
# This class is for displaying (and perhaps later also for editing) person records from the database
#     """
#     id : Optional[str] = ""
#     type : Optional[str] = "" # Is always 'Person'
#     person_type1 : Optional[list[str]] = []
#     # Types 1 are: "Author", "Printer", "Artist", "Depicted Person"
#     person_type2 : Optional[list[str]] = []
#     # Type 2 is a subtype only needed if type1 is "depicted Person"
#     person_type3 : Optional[list[str]] = []
#     # Type 3 is a subtype only needed if typ2 is "Saint"
#     external_id : Optional[list[ExternalId]] = []
#     name_preferred : Optional[str] = ""
#     name_variant : Optional[list[str]] = []
#     sex : Optional[str] = ""
#     dates_from_source : Optional[list[DateImport]] = []
#     # This is only provisional - there will be some functions to turn the
#     # dates from import into standardised dates
#     connected_persons : Optional[list[ConnectedEntity]] = []
#     connected_organisations : Optional[list[ConnectedEntity]] = []
#     connected_locations : Optional[list[ConnectedEntity]] = []
#     comments : Optional[str] = ""

# class OrgDbDisplay(BaseModel):
#     """
# This class is for displaying (and perhaps later also for editing) Organisation 
# authority records from the database. 
#     """
#     id : Optional[str] = ""
#     type : Optional[str] = ""  # Is always "Organisation"
#     org_type1: Optional[list[str]] = [] # Types 1 are: "Printer", "Collection", "Group of Persons"
#     org_type2: Optional[list[str]] = []
#     # Type 21 is a subtype only needed if type1 is "Group of Persons",
#     # it would be e.g. 'Guild', 'Monastery', 'Ruling Body'
#     external_id : Optional[list[ExternalReference]] = []
#     name_preferred : Optional[str] = ""
#     name_variant : Optional[list[str]] = []
#     dates_from_source : Optional[list[DateImport]] = []
#     # This is only provisional - there will be some functions to turn the dates
#     # from import into standardised dates
#     connected_persons : Optional[list[ConnectedEntity]] = []
#     connected_organisations : Optional[list[ConnectedEntity]] = []
#     connected_locations : Optional[list[ConnectedEntity]] = []
#     comments : Optional[str] = ""

# class PlaceDbDisplay(BaseModel):
#     """
# This class is for displaying (and perhaps later also editing) Place authority records 
# from the database
#     """
#     id : Optional[str] = ""
#     type : Optional[str] = "" # Is always "Place"
#     place_type1 : Optional[list[str]] = ""
#     # Types 1 are: "Region - historical", "Region - modern", "Town - historical",
#     #  "Town - modern", "Building", "Building-part"
#     # There should be only one place_type1 per record, but I keep it as list for
#     # the sake of consistency
#     external_id : Optional[list[ExternalReference]] = []
#     name_preferred : Optional[str] = ""
#     name_variant : Optional[list[str]] = []
#     coordinates : Optional[list[Coordinates]] = []
#     dates_from_source : Optional[list[DateImport]] = []
#     # This is only provisional - there will be some functions to turn the
#     # dates from import into standardised dates
#     connected_persons : Optional[list[ConnectedEntity]] = []
#     connected_organisations : Optional[list[ConnectedEntity]] = []
#     connected_locations : Optional[list[ConnectedEntity]] = []
#     comments : Optional[str] = ""

class WebCall(Document):
    url : Optional[str] = ""
    content : Optional[bytes] = ""
