from pydantic import BaseModel
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
    
   

class Person(BaseModel):
# This class is used for references to persons in book records. 
# id is the id of the person in authority files (currently, the GND), name the name given in the source
# and role the person's role in making the book, according to standard bibliographical abbreviations, e.g. "prt" for printer.
    id : Optional[str] = ""
    name : Optional[str] = ""
    role : Optional[str] = ""

class Place(BaseModel):
# This class is used for references to places (virtually alwys towns) in book records.
# id is the id of the place in authority files (currently, the GND), name the name given the source
# and role either "mfp" for the place of printing, or "pup" for the place of publishing. 
# If a place is both, there will be two different record for it. 
    id : Optional[str] = ""
    name : Optional[str] = ""
    role : Optional[str] = ""


class Bibliographic_id(BaseModel):
# Here, the name is the name of the repertory (e.g., VD16), the id the id of a book in the repertory
# and the uri the uri of the record of the book in the repertor
    uri : Optional[str] = ""
    name : Optional[str] = ""
    id : Optional[str] = ""
    
class Bibliographic_information(BaseModel):
    bibliographic_id : Optional[list[Bibliographic_id]] = []
    persons : Optional[list [Person]] = []
    places : Optional[list [Place]] = []
    title: Optional[str] = ""
    volume_number : Optional[str] = ""
    part_title : Optional[str] = ""
    printing_date : Optional[str] = ""
    printing_information : Optional[str] = ""



     
    
class Metadata(BaseModel):
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
    repository : Optional[str] = ""
    shelfmark : Optional[str] = ""
    license : Optional[str] = ""
    bibliographic_id : Optional[list[Bibliographic_id]] = []
    bibliographic_information : Optional[list[Bibliographic_information]] = []
    location : Optional[str] = ""
    markxml : Optional[str] = ""
    numberOfImages : Optional[int] = ""
    iiifUrl : Optional[str] = ""
    manifest : Optional[str] = ""
    images : Optional[list[Image]] = []
    title : Optional[str] = ""