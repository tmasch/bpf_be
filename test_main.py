"""
Testing of main
"""
#import os
import main

#os.environ["MONGODB_HOST"] = "localhost"
#os.environ["MONGODB_PORT"] = "27017"

def test_get_metadata():
    # Herbarius as standard test case
    iiif_url="https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb00027407/manifest"
    material="book"
    
