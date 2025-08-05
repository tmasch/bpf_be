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

class Attribute(BaseModel):
    key : Optional[str] = ""
    value : Optional[str] = ""

class ExternalReference(BaseModel):
    """
This class is used for references to external IDs in bibliographic records and in authority 
files such as the GND. It contains the name of the repertory (e.g., VD16, GND), the ID of the 
book or person within the repertory and, if available, the URI of the entry. 
    """
    uri : Optional[str] = ""
    name : Optional[str] = ""
    external_id : Optional[str] = ""

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
    def add_attribute(self,key,value):
        a=Attribute(key=key,value=value)
        self.attributes.append(a)
    def get_attribute(self,key):
        v=""
        for a in self.attributes:
            if a.key == key:
                v=a.value
        return v
    attributes : Optional[list[Attribute]] = []
    type : Optional[str] = "" 
    stub : Optional[bool] = True
    name : Optional[str] = ""
    external_id : Optional[List[ExternalReference]] = []
    name_preferred : Optional[str] = ""
    dates : Optional[list[Date]] = []
    comments : Optional[str] = ""
    preview : Optional[str] = ""
    linkedEntity : Optional[Link["Entity"]] = None
    class Settings:
        union_doc = Union
#    gnd_id : Optional[str] = ""
#    new_authority_id : Optional[str] = ""
#    external_id : Optional[list[ExternalReference]] = []
#    internal_id : Optional[str] = ""
#   name_variant : Optional[list[str]] = []
#    dates_from_source : Optional[list[DateImport]] = []
#    datestring : Optional[str] = ""
#    date_start : Optional[tuple] = ()
 #   date_end : Optional[tuple] = ()
#    date_aspect : Optional[str] = ""




class EntityConnection(Document):
    """
    Class 
    """
    external_id : Optional[List[ExternalReference]] = []
    name : Optional[str] = "" # Name of the person, place or organisation for easier access
    connection_type : Optional[str] = "" # either person, place or organisation
    connection_comment : Optional[str] = ""
    connection_time : Optional[str] = ""
    type : Optional[str] = ""
    subtype : Optional[str] = ""
    nameA : Optional[str] = ""
    nameB : Optional[str] = ""
    entityA : Optional[Link[Entity]] = None
    entityB : Optional[Link[Entity]] = None
    relationA : Optional[str] = ""
    relationB : Optional[str] = ""
    class Settings:
        union_doc = Union
#    id : Optional[str] = ""
# In the GND; the role of a connected person must be given through an abbrevation
# that gives rather general information, e.g. "bezf" = "family relation";
# more detailed information can be given in a comment field



# class Role(Document):
#     role : Optional[str] = ""
#     name : Optional[str] = "" # This field is only a stopgap measure, if
#     type : Optional[str] = ""
#     chosen_candidate_id : Optional[int] = 0
#     comment : Optional[str] = ""
#     preview : Optional[str] = ""
#     entity_and_connections : Optional[Link[EntityAndConnections]] = None
#     class Settings:
#         union_doc = Union

def make_new_role(role,person_name):
    r=Entity()
    if person_name:
        r.name=person_name
    a=Attribute()
    a.key="role"
    a.value=role
    r.attributes.append(a)
    a=Attribute()
    a.key="chosen_candidate"
    a.value=-1
    r.attributes.append(a)
    return r


class EntityAndConnections(Document):
    """
This class is for the links of persons, organisations and places to book records
    """
    def add_attribute(self,key,value):
        a=Attribute(key=key,value=value)
        self.attributes.append(a)
    def get_attribute(self,key):
        v=""
        for a in self.attributes:
            if a.key == key:
                v=a.value
        return v
    attributes : Optional[list[Attribute]] = []
    name : Optional[str] = "" # This field is only a stopgap measure, if
    type : Optional[str] = ""
    comment : Optional[str] = ""
    preview : Optional[str] = ""
    entity : Optional[Link[Entity]] = None
#    chosen_candidate_id : Optional[int] = 0
    connected_entities : Optional[List[Link[EntityConnection]]] = []
    connections : Optional[List[Link["EntityAndConnections"]]] = []
    class Settings:
        union_doc = Union


class MakingProcess(Document):
    """
    \todo
    """
    process_number : Optional[int] = 0
    process_type : Optional[str] = ""
    process_qualifier : Optional[str] = ""
    person : Optional[EntityConnection] = None
    place : Optional[EntityConnection] = None
    date : Optional[EntityConnection] = None
    class Settings:
        union_doc = Union


class BibliographicInformation(Document):
    """
    Class bibliograpic information
    """
#    model_config = ConfigDict(arbitrary_types_allowed=True)
    bibliographic_id : Optional[List[BibliographicId]] = []
    persons : Optional[List[Link[Entity]]] = []
    organisations : Optional[List[Link[Entity]]] = []
    places : Optional[List[Link[Entity]]] = []
    attributes : Optional[list[Attribute]] = []
    title: Optional[str] = ""
#    volume_number : Optional[str] = ""
#    part_title : Optional[str] = ""
    printing_date : Optional[str] = "" # This will be later replaced
    date_string : Optional[str] = ""
    date_start : Optional[tuple] = ()
    date_end : Optional[tuple] = ()
#    printing_information : Optional[str] = ""
    class Settings:
        union_doc = Union




class Metadata(Document):
    """
    Metadata
    """
    def add_attribute(self,key,value):
        a=Attribute(key=key,value=value)
        self.attributes.append(a)
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
    attributes : Optional[list[Attribute]] = []
#    material : Optional[str] = ""
#    repository : Optional(dataclass.field(default_factory=list))

    repository: Optional[Link[EntityAndConnections]] = None
#    shelfmark : Optional[str] = ""
#    license : Optional[str] = ""
    bibliographic_id : Optional[list[ExternalReference]] = []
    bibliographic_information : Optional[List[Link[BibliographicInformation]]] = []
#    location : Optional[str] = ""
#    markxml : Optional[str] = ""
    numberOfImages : Optional[int] = 0
#    iiifUrl : Optional[str] = ""
#    manifest : Optional[str] = ""
    images : Optional[list[Image]] = []
#    title : Optional[str] = ""
    making_processes : Optional[List[MakingProcess]] = []
    class Settings:
        union_doc = Union


class BookDb(Document):
    """
This class is for entering Book records into the database
    """
    type : Optional[str] = "Book"
    bibliographic_id : Optional[list[ExternalReference]] = []
    persons : Optional[list[Link[EntityConnection]]] = []
    organisations : Optional[list [Link[EntityConnection]]] = []
    places : Optional[list [EntityConnection]] = []
    title: Optional[str] = ""
    volume_number : Optional[str] = ""
    part_title : Optional[str] = ""
    printing_date : Optional[str] = "" # Has to be later replaced with a date object
    date_string : Optional[str] = ""
    date_start : Optional[tuple] = ()
    date_end : Optional[tuple] = ()
    preview : Optional[str] = ""
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


class WebCall(Document):
    url : Optional[str] = ""
    content : Optional[bytes] = ""
