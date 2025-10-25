# This module is written for testing functions in books_parsing_manifests

import books_parsing_manifests
manifest_default = r'https://gallica.bnf.fr/iiif/ark:/12148/bpt6k8710648g/manifest.json'
entered = "a"
while entered != "":
    entered = input("Manifest: ")
    if entered == "d":
        entered = manifest_default
    if entered == "":
        break
    result = books_parsing_manifests.Gallica_parsing(entered)
    #print(result)
