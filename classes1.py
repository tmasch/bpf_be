#pylint: disable=C0115,C0303,W0212,C0116,C0302
""""
This file contains class definitions
"""
import json
from typing import Optional, List
import logging
import sys
from pydantic import 
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

class Attribute():
    key : str = ""
    value : str = ""

class ExternalReference():
    """
This class is used for references to external IDs in bibliographic records and in authority
files such as the GND. It contains the name of the repertory (e.g., VD16, GND), the ID of the
book or person within the repertory and, if available, the URI of the entry.
    """
    uri : str = ""
    name : str = ""
    external_id : str = ""

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
    type : str = ""
#    gnd_id : str = ""
    stub : bool = True
    attributes : Attribute = ""
    name : str = ""
#    new_authority_id : str = ""
#    external_id : ExternalReference = ""
#    internal_id : str = ""
    name_preferred : str = ""
#   name_variant : str = ""
#    dates_from_source : DateImport = ""
#    datestring : str = ""
    dates : Date = ""
#    date_start : tuple = ()
 #   date_end : tuple = ()
#    date_aspect : str = ""
    comments : str = ""
    preview : str = ""
    linkedEntity : "Entity" = ""
    class Settings:
        union_doc = Union




class EntityConnection(Document):
    """
    Class
    """
#    id : str = ""
    external_id : ExternalReference = ""
    name : str = "" # Name of the person, place or organisation for easier access
    connection_type : str = "" # either person, place or organisation
# In the GND; the role of a connected person must be given through an abbrevation
# that gives rather general information, e.g. "bezf" = "family relation";
# more detailed information can be given in a comment field
    connection_comment : str = ""
    connection_time : str = ""
    type : str = ""
    subtype : str = ""
    entityA : Entity = ""
    entityB : Entity = ""
    relationA : str = ""
    relationB : str = ""
    class Settings:
        union_doc = Union



# class Role(Document):
#     role : str = ""
#     name : str = "" # This field is only a stopgap measure, if
#     type : str = ""
#     chosen_candidate_id : int = 0
#     comment : str = ""
#     preview : str = ""
#     entity_and_connections : EntityAndConnections = ""
#     class Settings:
#         union_doc = Union

# def make_new_role(role,person_name):
#     r=Role(role=role,chosen_candidate=-1)
#     if person_name:
#         r.entity_and_connections=EntityAndConnections()
#         r.entity_and_connections.entity=Entity(name=person_name)
#     return r


class EntityAndConnections(Document):
    """
This class is for the links of persons, organisations and places to book records
    """
    name : str = "" # This field is only a stopgap measure, if
    comment : str = ""
    preview : str = ""
    entity : Entity = ""
    chosen_candidate_id : int = 0
    connected_entities : EntityConnection = ""
    class Settings:
        union_doc = Union


class MakingProcess(Document):
    """
    \todo
    """
    process_number : int = 0
    process_type : str = ""
    process_qualifier : str = ""
    person : EntityConnection = ""
    place : EntityConnection = ""
    date : EntityConnection = ""
    class Settings:
        union_doc = Union


class BibliographicInformation(Document):
    """
    Class bibliograpic information
    """
#    model_config = ConfigDict(arbitrary_types_allowed=True)
    bibliographic_id : BibliographicId = ""
    persons : EntityConnection = ""
    organisations : EntityConnection = ""
    places : EntityConnection = ""
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

    repository: EntityAndConnections = ""
    shelfmark : str = ""
    license : str = ""
    bibliographic_id : ExternalReference = ""
    bibliographic_information : BibliographicInformation = ""
    location : str = ""
    markxml : str = ""
    numberOfImages : int = 0
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
    type : str = "Book"
    bibliographic_id : ExternalReference = ""
    persons : EntityConnection = ""
    organisations :  EntityConnection = ""
    places :  EntityConnection = ""
    title: str = ""
    volume_number : str = ""
    part_title : str = ""
    printing_date : str = "" # Has to be later replaced with a date object
    date_string : str = ""
    date_start : tuple = ()
    date_end : tuple = ()
    preview : str = ""
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


class WebCall(Document):
    url : str = ""
    content : bytes = ""
