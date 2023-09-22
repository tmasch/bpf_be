from pydantic import BaseModel
#import pydantic
#import pydantic
from typing import Optional

class Image(BaseModel):
    def __str__(self):
        t="Index: "+self.index+"\n"
    index : Optional[int] = ""
    label :  Optional[str] = ""
    width : Optional[int] = ""
    height : Optional[int] = ""
    baseurl : Optional[str] = ""
    format : Optional[str] = ""
    
    
    
class Metadata(BaseModel):
    def __str__(self):
        t="ID:"+self.id+"\n"
        t=t+"title: "+self.title+"\n"
        t=t+"location: "+self.location+"\n"
        t=t+"markxml: "+self.markxml+"\n"
        t=t+"number of images: "+str(self.numberOfImages)+"\n"
        t=t+"IIIF url"+self.iiifUrl
#        t=t+"Manifest"+self.manifest
        return(t)
    id : Optional[str] = ""
    title : Optional[str] = ""
    location : Optional[str] = ""
    markxml : Optional[str] = ""
    numberOfImages : Optional[int] = ""
    iiifUrl : Optional[str] = ""
    manifest : Optional[str] = ""
    images : Optional[list[Image]]
     
    
