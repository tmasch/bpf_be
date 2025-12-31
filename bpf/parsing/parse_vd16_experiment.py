import requests
from lxml import html

url = "https://gateway-bayern.de/VD16+L+7550"  # example
response = requests.get(url)
doc = html.fromstring(response.content)

details = doc.xpath("//div[@id='details']")[0]

data = {}

# find all <strong class="c2">
strongs = details.xpath(".//strong[@class='c2']")

for s in strongs:
    key = s.text_content().strip().rstrip(":")
    
    # collect all following siblings until the next <strong class="c2">
    values = []
    node = s.getnext()
    
    while node is not None and not (node.tag == "strong" and node.get("class") == "c2"):
        # text content of the node
        text = node.text_content().strip()
        if text:
            values.append(text)
        node = node.getnext()

    data[key] = " ".join(values)

# Show results
for k, v in data.items():
    print(f"{k}: {v}")
