"""
Testing of main
"""
import main


def test_get_metadata():
    # Herbarius as standard test case
    iiif_url="https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb00027407/manifest"
    material="book"
    
