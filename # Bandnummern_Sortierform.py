# This programme demonstrates the conversion of the 
# standardised form of a volume number in Aleph and Sisis 
# to a string allows correct ordering of the volumes
# by means of simple alphanumerical sorting

import re #module for regular expressions

volume_number = input("enter volume number: ")
counter = 0
volume_number_length = len(volume_number)-1
volume_number_sortable = volume_number

for i in range(volume_number_length, -1, -1): 
    #counts backwards characted by character. 
    # The "-1" is necessary since the end point is always excluded
    if re.match(r'[0-9]', volume_number[i]): #if the character is a number
        counter = counter + 1
    else: #if there is a character that is no number
        if counter > 0: 
            #if the character right of the not-numerical character is a number
            zeroes_number = 4 - counter
            padding = "0" * zeroes_number
            volume_number_sortable = volume_number_sortable[0:i+1] + padding + volume_number_sortable[i+1:] 
                # inserting the padding at the correct place
            counter = 0
  

if counter >0: # if the first character is a number
    zeroes_number = 4 - counter
    padding = "0" * zeroes_number
    volume_number_sortable = padding + volume_number_sortable
print(volume_number_sortable)


