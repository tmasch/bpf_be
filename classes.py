from pydantic import BaseModel, ConfigDict
import bson
#import pydantic
#import pydantic
from typing import Optional

class Image(BaseModel):
    def __str__(self):
        t="Index: "+self.index+"\n"
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
    
class External_id(BaseModel):
# This class is used for references to external IDs in bibliographic records and in authority files such as the GND
# It contains the name of the repertory (e.g., VD16, GND), the ID of the book or person within the repertory
# and, if available, the URI of the entry. 
    uri : Optional[str] = ""
    name : Optional[str] = ""
    id : Optional[str] = ""

class Connected_entity(BaseModel):
    id : Optional[str] = ""
    external_id : Optional[list[External_id]] = []
    name : Optional[str] = ""
    connection_type : Optional[str] = "" # In the GND; the role of a connected person must be given through an abbrevation
    # that gives rather general information, e.g. "bezf" = "family relation"; more detailed information can be given in a comment field
    connection_comment : Optional[str] = ""
    connection_time : Optional[str] = ""

class Date_import(BaseModel):
    datestring : Optional[str] = ""
    datetype : Optional[str] = ""
    


class Person_import(BaseModel):
    external_id : Optional[list[External_id]] = []
    internal_id : Optional[str] = ""
    name_preferred : Optional[str] = ""
    name_variant : Optional[list[str]] = []
    sex : Optional[str] = ""
    dates_from_source : Optional[list[Date_import]] = []
    connected_persons : Optional[list[Connected_entity]] = []
    connected_organisations : Optional[list[Connected_entity]] = []
    connected_locations : Optional[list[Connected_entity]] = []
    comments : Optional[str] = ""
    preview : Optional[str] = ""

class ObjectID(BaseModel):
    pass

class Person(BaseModel):
# This class is used for references to persons in book records. 
# id is the id of the person in authority files (currently, the GND), name the name given in the source
# and role the person's role in making the book, according to standard bibliographical abbreviations, e.g. "prt" for printer.
# If the person's ID (GND, ULAN etc.) is found to already have a record in the database, internal_id and internal_id_preview are filled.
# If the person's name is searched in the database, or if the person's ID or name is searched in an external repository such as the GND,
# The results will be put into the field 'potential candidates'. 
# The user can pick one of them (or confirm if only one was found)
    #model_config = ConfigDict(arbitrary_types_allowed=True)
    id : Optional[str] = ""
    id_name : Optional[str] = ""
    internal_id : Optional[str] = ""
    internal_id_preview : Optional[str] = ""
    name : Optional[str] = ""
    role : Optional[str] = ""
    chosen_candidate : Optional[int] = ""
    potential_candidates : Optional[list[Person_import]] = []
    


class Place(BaseModel):
# This class is used for references to places (virtually alwys towns) in book records.
# id is the id of the place in authority files (currently, the GND), name the name given the source
# and role either "mfp" for the place of printing, or "pup" for the place of publishing. 
# If a place is both, there will be two different record for it. 
    id : Optional[str] = ""
    id_name : Optional[str] = ""
    name : Optional[str] = ""
    role : Optional[str] = ""



class Organisation_import(BaseModel):
# This class is used for importing data on organisations from authority records such as the GND
    external_id : Optional[list[External_id]] = []
    internal_id : Optional[str] = ""
    name_preferred : Optional[str] = ""
    name_variant : Optional[list[str]] = []
    dates_from_source : Optional[list[Date_import]] = []
    connected_persons : Optional[list[Connected_entity]] = []
    connected_organisations : Optional[list[Connected_entity]] = []
    connected_locations : Optional[list[Connected_entity]] = []
    comments : Optional[str] = ""
    preview : Optional[str] = ""

class Organisation(BaseModel):
# This class is used for references to organisations (publishing houses) in book records. 
# id is the id of the place in authority files (currently, the GND), name the name given the source
# and role either "pub" for the publisher, or "prt" for the printer
# If an organisation is both, there will be two different record for it. 
    id : Optional[str] = ""
    id_name : Optional[str] = ""
    internal_id : Optional[str] = ""
    internal_id_preview : Optional[str] = ""
    name : Optional[str] = ""
    role : Optional[str] = ""
    name : Optional[str] = ""
    role : Optional[str] = ""
    chosen_candidate : Optional[int] = ""
    potential_candidates : Optional[list[Organisation_import]] = []




class Bibliographic_id(BaseModel):
# Here, the name is the name of the repertory (e.g., VD16), the id the id of a book in the repertory
# and the uri the uri of the record of the book in the repertory.
# This class should be superseded everywhere by External_id, I keep it for the moment just to be sure
    uri : Optional[str] = ""
    name : Optional[str] = ""
    id : Optional[str] = ""



    
class Bibliographic_information(BaseModel):
#    model_config = ConfigDict(arbitrary_types_allowed=True)
    bibliographic_id : Optional[list[External_id]] = []
    persons : Optional[list [Person]] = []
    organisations : Optional[list [Organisation]] = []
    places : Optional[list [Place]] = []
    title: Optional[str] = ""
    volume_number : Optional[str] = ""
    part_title : Optional[str] = ""
    printing_date : Optional[str] = ""
    printing_information : Optional[str] = ""



     
    
class Metadata(BaseModel):
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
    id : Optional[str] = ""
    material : Optional[str] = ""
    repository : Optional[list[Organisation]] = []
    shelfmark : Optional[str] = ""
    license : Optional[str] = ""
    bibliographic_id : Optional[list[External_id]] = []
    bibliographic_information : Optional[list[Bibliographic_information]] = []
    location : Optional[str] = ""
    markxml : Optional[str] = ""
    numberOfImages : Optional[int] = ""
    iiifUrl : Optional[str] = ""
    manifest : Optional[str] = ""
    images : Optional[list[Image]] = []
    title : Optional[str] = ""






