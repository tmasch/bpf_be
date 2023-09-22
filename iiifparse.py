import json
from jsonpath_ng.ext import parse
from classes import *
    
  


def iiifparse(manifest):
    print("Parsing the iiif manifest")
    mnf = json.loads(manifest)
    metadata=mnf["metadata"]
    m=parseMeta(metadata)
#    if "seeAlso" in mnf:
#        x=mnf["seeAlso"]
#        print(x)
#        for xx in x:
#            if (xx["label"] == "MARCXML"): 
#                m.markxml=xx["@id"]
    canvases=mnf["sequences"][0]["canvases"]    
    i=parseImages(canvases)
    m.numberOfImages=len(i)
    m.images=i
    print(m)
    return(m)
    
    
def parseMeta(metadata):
#    print(metadata)
    m = Metadata()
    for x in metadata:
        for xx in x["label"]:
            if "@value" in xx:
                if (xx["@value"] == "Title"):
                    m.title=x["value"]
                if (xx["@value"] == "Location"):
                    m.location=x["value"]
        if(x["label"] == "Title"):
            m.title=x["value"]
        if(x["label"] == "Auteur, titre, oeuvre"):
            m.title=x["value"]
        if(x["label"] == "Cote"):
            m.location=x["value"]
    return(m)
    
def parseImages(canvases):
    print("Images")
    i=0
    images=[]
    for c in canvases:
        i=i+1
#        print(i)
#        print(c)
        label=c["label"]
#        print(label)
        baseurl=c["images"][0]["resource"]["service"]["@id"] 
#        print(baseurl)
        width=c["images"][0]["resource"]["width"]
        height=c["images"][0]["resource"]["height"]
#        print(width,height)
        im = Image()
        im.index = i
        im.label = label
        im.baseurl = baseurl
        im.width = width
        im.height = height
        images.append(im)
    return(images)