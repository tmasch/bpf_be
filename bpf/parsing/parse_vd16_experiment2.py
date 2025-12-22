import requests
from lxml import html, etree

url = "https://gateway-bayern.de/VD16+L+7550"
response = requests.get(url)
doc = html.fromstring(response.content)

details = doc.xpath("//div[@id='details']")[0]
data = {}

# all <strong class="c2"> in document order
strongs = details.xpath(".//strong[@class='c2']")
print("length of strongs")
print(len(strongs))

for i, s in enumerate(strongs):
    print("i, s")
    print(i)
    print(s)
    key = s.text_content().strip().rstrip(":")
    print(key)

    # Find the next <strong class="c2"> in document order
    next_strong = strongs[i+1] if i+1 < len(strongs) else None

    # Build an XPath expression to get all text nodes between s and next_strong
    
    if next_strong is not None:
        nodes = details.xpath(".//text()[preceding::strong[@class='c2'][1]=$s and following::strong[@class='c2'][1]=$n]",
            s=s, n=next_strong)
    else:
        # last field: collect everything after this strong
        nodes = details.xpath(".//text()[preceding::strong[@class='c2'][1]=$s]", s=s)

    nodes = details.xpath("..//text()[preceding::strong[@class='c2'][1]=$s]", s=len(strongs)-1)
    print("nodes")
    print(nodes)
    # Clean up
    values = [t.strip() for t in nodes if t.strip()]
    data[key] = " ".join(values)

# Output
for k, v in data.items():
    print(f"{k}: {v}")
