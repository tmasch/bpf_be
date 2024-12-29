import parsing_helpers

def test_convert_roman_numerals_mdcc():
    rn = "MDCC"
    an = parsing_helpers.convert_roman_numerals(rn)    
    print(rn)
    print(an)
    assert an == "1700"
    


def test_convert_roman_numerals_mcmxii():
    rn = "MCMXII"
    an = parsing_helpers.convert_roman_numerals(rn)
    print(rn)
    print(an)
    assert an == "1912"


def test_convert_roman_numerals_mccmxiix():
    rn = "MCCMXIIX"
    an = parsing_helpers.convert_roman_numerals(rn)
    print(rn)
    print(an)
    assert an == "1818"