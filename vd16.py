import urllib.request
from lxml import etree


def vd16Import(vd16url):
    url = urllib.request.urlopen(vd16url)
    raw = url.read()
    tree = etree.HTML(raw)
#    print(raw)
    r = tree.find(".//ul[@class='titleinfo']")
    print( etree.tostring(r,encoding=str))
    titleinfo=r[0]
    list=titleinfo.findall("li")
    for l in r:
        tag=l.find(".//strong")
        if (tag is not None):
            print(tag.text)
        text=l.find(".//a")
        if (text is not None):
            print(text.text)
        if (tag is not None and text is not None):
            if (tag == "Normnummer:"):
                vd16['normnummer']=text.text
            if (tag == "Titel:"):
                vd16['title']=text.text

#        l.remove("strong")
#        print(etree.tostringl)
        t=l.xpath("text()")
        if (len(t) > 0):
            print(t[0])
#        print( etree.tostring(l,encoding=str))
    
    
vd16url="https://gateway-bayern.de/VD16+G+309"
vd16url="https://gateway-bayern.de/VD16+L+7378"
print(vd16url)
vd16Import(vd16url)

