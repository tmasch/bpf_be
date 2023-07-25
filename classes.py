from pydantic import BaseModel

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
    id = ''
    title = '' 
    location = ''
    markxml =  ''
    numberOfImages = '' 
    iiifUrl = ''
    manifest = ''
    images =[]
    
    
class Image:
    def __str__(self):
        t="Index: "+self.index+"\n"
    index = ''
    label = ''
    width = ''
    height = ''
    baseurl = ''
    format = ''  