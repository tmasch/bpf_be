ulan_list_raw = open(r"C:\users\berth\Downloads\sparql(9).json", "r")
print(ulan_list_raw)
ulan_list = ulan_list_raw.json()
artist_id_list = []
#if "results" in ulan_list:        
#    list_results = ulan_list["results"]
#    if "bindings" in list_results:
#        bindings = list_results["bindings"]
#        for artist in bindings:
#            artist_id = bindings[artist]["artist_id"][value]
#            artist_id_list.append(artist_id)

#print(ulan_list)

