def roman_numerals(roman_number):
    # This function translates a Roman numeral written according to rules (permitting two "I", "X" or "C" left of a higher value) into Arabic numbers
    roman_number = roman_number.upper()
    roman_number = roman_number.replace(".", "")
    roman_number = roman_number.replace(" ", "")
    roman_number = roman_number.replace("J", "I")
    l = len(roman_number)
    print("length: " + str(l))
    result = 0
    for x in range(0, l):
        match roman_number[x]:
            case "M":
                result = result + 1000
            case "D":
                result = result + 500
            case "C":
                if l-x > 2: # if there are at least four characters following
                    if roman_number[x+1] == "M" or (roman_number[x+1] == "C" and roman_number[x+2] == "M"):
                        result = result - 100
                    elif roman_number[x+1] == "D" or (roman_number[x+1] == "C" and roman_number[x+2] == "D"):
                        result = result - 100
                    else:
                        result = result + 100
                elif l-x == 2: #if it is the penultima charachter
                    if roman_number[x+1] == "M" or roman_number[x+1] == "D":
                        result = result - 100
                    else:
                        result = result + 100
                else: #if it is the ultimate character
                    result = result + 100
            case "L":
                result = result + 50
            case "X":
                if l-x > 2: # if there are at least four characters following
                    if roman_number[x+1] == "C" or (roman_number[x+1] == "X" and roman_number[x+2] == "C"):
                        result = result - 10
                    elif roman_number[x+1] == "L" or (roman_number[x+1] == "X" and roman_number[x+2] == "L"):
                        result = result - 10
                    else:
                        result = result + 10
                elif l-x == 2: #if it is the penultima charachter
                    if roman_number[x+1] == "C" or roman_number[x+1] == "L":
                        result = result - 10
                    else:
                        result = result + 10
                else: 
                    result = result + 10
            case "V":
                result = result + 5
            case "I":
                if l-x > 2: # if there are at least four characters following
                    if roman_number[x+1] == "X" or (roman_number[x+1] == "I" and roman_number[x+2] == "X"):
                        result = result - 1
                    elif roman_number[x+1] == "V" or (roman_number[x+1] == "I" and roman_number[x+2] == "V"):
                        result = result - 1
                    else:
                        result = result + 1
                elif l-x == 2: #if it is the penultima charachter
                    if roman_number[x+1] == "X" or roman_number[x+1] == "V":
                        result = result - 1
                    else:
                        result = result + 1
                else: 
                    result = result + 1
    return str(result)


roman_number = input("Enter number: ")
x = roman_numerals(roman_number)
print(x)