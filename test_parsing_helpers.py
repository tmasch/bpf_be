#
"""
Testing of parsing_helpers.py
"""
import parsing_helpers

def test_turn_umlaut_to_unicode():
    for old, new in parsing_helpers.encoding_list.items():
        assert new==parsing_helpers.turn_umlaut_to_unicode(old)

def test_convert_roman_numerals_mdcc():
    rn = "MDCC"
    an = parsing_helpers.convert_roman_numerals(rn)    
    assert an == "1700"

def test_convert_roman_numerals_mcmxii():
    rn = "MCMXII"
    an = parsing_helpers.convert_roman_numerals(rn)
    assert an == "1912"

def test_convert_roman_numerals_mccmxiix():
    rn = "MCCMXIIX"
    an = parsing_helpers.convert_roman_numerals(rn)
    assert an == "1818"

def test_convert_roman_numerals_mmxxv():
    rn = "mmxxv"
    an = parsing_helpers.convert_roman_numerals(rn)
    assert an == "2025"

def test_convert_roman_numerals_mxm():
    rn = "mxm"
    an = parsing_helpers.convert_roman_numerals(rn)
    assert an == "1990"

def test_convert_roman_numerals_ccxc():
    rn = "ccxc"
    an = parsing_helpers.convert_roman_numerals(rn)
    assert an == "290"
