import responses
from pytest import *

"""
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
    frames : Optional[list[Frame]] = []



    https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb00027407/manifest


    https://api.digitale-sammlungen.de/iiif/image/v2/bsb00027407_00001

"""


image_actions= __import__("imageActions.py")


fetch_image_from_web=imageActions.fetch_image_from_web