"""
This module contains a number of simple functions that standardise information about relationships taken from authority records. 
"""

def gnd_person_relation(relation, sex, relation_type): 
# This function takes the German phrase for a relationship from the GND and gives an English phrase (in reverse, since the GND describes the connection of the 'far' person to the 'near' person, and I do it vice versa)
# Up to now, it only covers relationships between persons - relationships between persons and organisations are to be added
# The function takes the relationship phrase from the GND plus the sex of the 'near' person and returns one phrase for the relationship. 
# The abbreviated relation types from 
    relation = relation.lower()
    gnd_person_relations_replace = {". ": ".", "ehegatte" : "ehemann", "ehegattin" : "ehefrau", "gemahl" : "ehemann", "gemahlin" : "ehefrau", \
        "erste " : "1.", "erster " : "1.", "zweite " : "2.", "zweiter " : "2.", "dritte " : "3.", "dritter " : "3.", "vierte" : "4.", "vierter" : "4.", "gross" : "groß"}
    for old, new in gnd_person_relations_replace.items():
        relation = relation.replace(old, new)

    gnd_person_relations = { \
    "1.ehe" : ["husband of (his first marriage)", "wife of (her first marriage)", "husband or wife of (first marriage)"], \
    "1.ehefrau" : ["husband of (his first marriage)"], \
    "1.ehemann" : ["wife of (her first marriage)"], \
    "1.kind" : ["father of (first child)", "mother of (first child)", "father or mother of (first child)"], \
    "1.schwiegervater" : ["son-in-law of (his first marriage)", "daughter-in-law of (her first marriage)", "son- or daughter-in-law of (first marriage)"], \
    "1.sohn" : ["father of (first son)", "mother of (first son)", "father or mother of (first son)"], \
    "1.tochter" : ["father of (first daughter)", "mother of (first daughter)", "father or mother of (first daughter)"], \
    "2.ehe" : ["husband of (his second marriage)", "wife of (her second marriage)", "husband or wife of (first marriage)"], \
    "2.ehefrau" : ["husband of (his second marriage)"], \
    "2.ehemann" : ["wife of (her second marriage)"], \
    "2.schwiegervater" : ["son-in-law of (his second marriage)", "daughter-in-law of (her second marriage)", "son- or daughter-in-law of (second marriage)"], \
    "2.sohn" : ["father of (second son)", "mother of (second son)", "father or mother of (second son)"], \
    "2.tochter" : ["father of (second daughter)", "mother of (second daughter)", "father or mother of (second daughter)"], \
    "3.ehe" : ["husband of (his third marriage)", "wife of (her third marriage)", "husband or wife of (second marriage)"], \
    "3.ehefrau" : ["husband of (his third marriage)"], \
    "3.ehemann" : ["wife of (her third marriage)"], \
    "3.schwiegervater" : ["son-in-law of (his third marriage)", "daughter-in-law of (her third marriage)", "son- or daughter-in-law of (third marriage)"], \
    "3.sohn" : ["father of (third son)", "mother of (third son)", "father or mother of (third son)"], \
    "3.tochter" : ["father of (third daughter)", "mother of (third daughter)", "father or mother of (third daughter)"], \
    "4.ehe" : ["husband of (his fourth marriage)", "wife of (her fourth marriage)", "husband or wife of (first marriage)"], \
    "4.ehefrau" : ["husband of (his fourth marriage)"], \
    "4.ehemann" : ["wife of (her fourth marriage)"], \
    "4.schwiegervater" : ["son-in-law of (his fourth marriage)", "daughter-in-law of (her fourth marriage)", "son- or daughter-in-law of (first marriage)"], \
    "4.sohn" : ["father of (fourth son)", "mother of (fourth son)", "father or mother of (fourth son)"], \
    "4.tochter" : ["father of (fourth daughter)", "mother of (fourth daughter)", "father or mother of (fourth daughter)"], \
    "5.ehe" : ["husband of (his fifth marriage)", "wife of (her fifth marriage)", "husband or wife of (first marriage)"], \
    "5.ehefrau" : ["husband of (his fifth marriage)"], \
    "5.ehemann" : ["wife of (her fifth marriage)"], \
    "5.schwiegervater" : ["son-in-law of (his fifth marriage)", "daughter-in-law of (her fifth marriage)", "son- or daughter-in-law of (first marriage)"], \
    "5.sohn" : ["father of (fifth son)", "mother of (fifth son)", "father or mother of (fifth son)"], \
    "5.tochter" : ["father of (fifth daughter)", "mother of (fifth daughter)", "father or mother of (fifth daughter)"], \
    "abkömmling" : ["ancestor of"], \
    "adoptivmutter" : ["adopted son of", "adopted daughter of", "adopted son or daughter of"], \
    "adoptivsohn" : ["adoptive father of", "adoptive mother of", "adoptive father or mother of"], \
    "adoptivtochter" : ["adoptive father of", "adoptive mother of", "adoptive father or mother of"], \
    "adoptivvater" : ["adopted son of", "adopted daughter of", "adopted son or daughter of"], \
    "akad. lehrer" : ["student of"], \
    "akademische betreuerin" : ["student of"], \
    "akademischer betreuer" : ["student of"], \
    "ältere schwester" : ["younger brother of", "younger sister of", "younger brother or sister of"], \
    "älterer bruder" : ["younger brother of", "younger sister of", "younger brother or sister of"], \
    "älteste tochter" : ["father of (first daughter)", "mother of (first daughter)", "father or mother of (first daughter)"], \
    "ältester bruder" : ["younger brother of", "younger sister of", "younger brother or sister of"], \
    "ältester sohn" : ["father of (first son)", "mother of (first son)", "father or mother of (first son)"], \
    "amtsnachfolger" : ["predecessor of"], \
    "amtsvorgänger" : ["successor to"], \
    "angehörige" : ["related to"], \
    "angehöriger" : ["related to"], \
    "arbeitsgeber" : ["employee of"], \
    "arbeitsgeberin" : ["employed by"], \
    "assistent" : ["assisted by"], \
    "assistentin" : ["assisted by"], \
    "attentäter" : ["murdered by"], \
    "attentatsopfer" : ["murderer of"], \
    "auftraggeber" : ["patron was"], \
    "base" : ["cousin of"], \
    "befreundet" : ["friend of"], \
    "befreundet mit" : ["friend of"], \
    "beichtkind" : ["confessor of"], \
    "beichtvater" : ["confessor was"], \
    "bekannte" : ["acquantaince of"], \
    "bekannter" : ["acquantaince of"], \
    "bekanntschaft" : ["acquaintance of"], \
    "berater" : ["counselled by"], \
    "berufskollege" : ["colleague of"], \
    "biograf" : ["biography by"], \
    "biografin" : ["biography by"], \
    "biograph" : ["biography by"], \
    "biographin" : ["biography by"], \
    "braut" : ["bridegroom of"], \
    "bräutigam" : ["bride of"], \
    "brieffreund" : ["corresponded with"], \
    "brieffreundin" : ["corresponded with"], \
    "briefpartner" : ["corresponded with"], \
    "briefpartnerin" : ["corresponded with"], \
    "briefverkehr" : ["corresponded with"], \
    "briefwechsel" : ["corresponded with "], \
    "bruder" : ["brother of", "sister of", "brother or sister of"], \
    "bruder (?)" : ["possibly brother of", "possibly sister of", "possibly brother or sister of"], \
    "bruder (vermutlich)" : ["possibly brother of", "possibly sister of", "possibly brother or sister of"], \
    "bruder ?": ["possibly brother of", "possibly sister of", "possibly brother or sister of"], \
    "bruder [?]" : ["possibly brother of", "possibly sister of", "possibly brother or sister of"], \
    "bruder von" : ["brother of"], \
    "bruder?": ["possibly brother of", "possibly sister of", "possibly brother or sister of"], \
    "cousin" : ["cousin of"], \
    "cousin zweiten grades" : ["second cousin of"], \
    "cousine zweiten grades" : ["second cousin of"], \
    "cousine" : ["cousin of"], \
    "dessen diener" : ["master of", "mistress of", "master or mistress of"], \
    "diener" : ["master of", "mistress of", "master or mistress of"], \
    "dienstherr" : ["master was"], \
    "dienstherrin" : ["mistress was"], \
    "dienstmagd" : ["master of", "mistress of", "master or mistress of"], \
    "doktorand" : ["PhD supervisor of"], \
    "doktorandin" : ["PhD supervisor of"], \
    "doktormutter" : ["PhD student of"], \
    "doktorvater" : ["PhD student of"], \
    "ehefrau" : ["husband of"], \
    "ehefrau (1.ehe)" : ["husband of (his first marriage)"], \
    "ehefrau 1" : ["husband of (his first marriage)"], \
    "ehefrau i." : ["husband of (his first marriage)"], \
    "ehefrau in erster ehe" : ["husband of (his first marriage)"], \
    "ehefrau (2.ehe)" : ["husband of (his second marriage)"], \
    "ehefrau 2" : ["husband of (his second marriage)"], \
    "ehefrau ii." : ["husband of (his second marriage)"], \
    "ehefrau in zweiter ehe" : ["husband of (his second marriage)"], \
    "ehefrau (3.ehe)" : ["husband of (his third marriage)"], \
    "ehefrau 3.ehe" : ["husband of (his third marriage)"], \
    "ehefrau in dritter ehe" : ["husband of (his third marriage)"], \
    "ehefrau von" : ["husband of"], \
    "ehefrau, 1.ehe" : ["husband of (his first marriage)"], \
    "ehefrau, 2.ehe" : ["husband of (his second marriage)"], \
    "ehefrau, 3.ehe" : ["husband of (his third marriage)"], \
    "ehefrau, 4.ehe" : ["husband of (his fourth marriage)"], \
    "ehefrau, 5.ehe" : ["husband of (his fifth marriage)"], \
    "ehefrau, erste ehe" : ["husband of (his first marriage)"], \
    "ehefrau?" : ["possibly husband of"], \
    "ehemann" : ["wife of"], \
    "ehemann (1.ehe)" : ["wife of (her first marriage)"], \
    "ehemann (2.ehe)" : ["wife of (her second marriage)"], \
    "ehemann (3.ehe)" : ["wife of (her third marriage)"], \
    "ehemann [?]" : ["possibly wife of"], \
    "ehemann 1.ehe" : ["wife of (her first marriage)"], \
    "ehemann 2.ehe" : ["wife of (her second marriage)"], \
    "ehemann in 2.ehe" : ["wife of (her second marriage)"], \
    "ehemann in erster ehe" : ["wife of (her first marriage)"], \
    "ehemann in zweiter ehe" : ["wife of (her second marriage)"], \
    "ehemann von" : ["wife of"], \
    "ehemann, 1.ehe" : ["wife of (her first marriage)"], \
    "ehemann, 2.ehe" : ["wife of (her second marriage)"], \
    "ehemann, 3.ehe" : ["wife of (her third marriage)"], \
    "ehemann, zweite ehe" : ["wife of (her second marriage)"], \
    "ehemann?" : ["possibly wife of"], \
    "ehepartner" : ["husband of", "wife of", "husband or wife of"], \
    "ehepartnerin" : ["husband of"], \
    "enge freundin" : ["close friend of"], \
    "enger freund" : ["close friend of"], \
    "enkel" : ["grandfather of", "grandmother of", "grandparent of"], \
    "enkelin" : ["grandfather of", "grandmother of", "grandparent of"], \
    "enkelsohn" : ["grandfather of", "grandmother of", "grandparent of"], \
    "enkeltochter" : ["grandfather of", "grandmother of", "grandparent of"], \
    "erzieher" : ["tutor was"], \
    "erzieher von" : ["tutor was"], \
    "erzieherin" : ["tutor was"], \
    "eventuelle identität" : ["possibly identified with"], \
    "evtl.identität" : ["possibly identified with"], \
    "ex-ehefrau" : ["former husband of"], \
    "ex-ehemann" : ["former wife of"], \
    "familie" : ["member of this family"], \
    "familie?" : ["possibly member of this family"], \
    "familienangehöriger" : ["to this family belonged"], \
    "familienmitglied" : ["to this family belonged"], \
    "förderer" : ["benefactor was"], \
    "frau" : ["husband of"], \
    "freund" : ["friend of"], \
    "freundin" : ["friend of"], \
    "freundschaft" : ["friend of"], \
    "freundschaft mit" : ["friend of"], \
    "frühere Ehefrau" : ["former husband of"], \
    "früherer Ehemann" : ["former wife of"], \
    "gatte" : ["wife of"], \
    "gattin" : ["husband of"], \
    "gegner" : ["opponent of"], \
    "gehilfe" : ["assisted by"], \
    "geliebte" : ["romantic partner of"], \
    "geliebter" : ["romantic partner of"], \
    "geschäftspartner" : ["partner of"], \
    "geschäftspartnerin" : ["partner of"], \
    "geschiedene ehefrau" : ["former husband of"], \
    "geschiedener ehemann" : ["former wife of"], \
    "gönner" : ["benefactor was"], \
    "großcousin" : ["second cousin of"], \
    "großcousine" : ["second cousin of"], \
    "großmutter" : ["grandson of", "granddaughter of", "grandchild of"], \
    "großmutter mütterlicherseits" : ["grandson (daughter's son) of", "granddaughter (daughter's daughter) of", "grandchild (daughter's son or daughter) of"], \
    "großmutter väterlicherseits" : ["grandson (son's son) of", "granddaughter (son's daughter) of", "grandchild (son's son or daughter) of"], \
    "großneffe" : ["great-uncle of", "great-aunt of", "great-uncle or great-aunt of"], \
    "großnichte" : ["great-uncle of", "great-aunt of", "great-uncle or great-aunt of"], \
    "großonkel" : ["great-nephew of", "great-niece of", "great-nephew or great-niece of"], \
    "großtante" : ["great-nephew of", "great-niece of", "great-nephew or great-niece of"], \
    "großvater" : ["grandson of", "granddaughter of", "grandchild of"], \
    "großvater mütterlichseits" : ["grandson (daughter's son) of", "granddaughter (daughter's daughter) of", "grandchild (daughter's son or daughter) of"], \
    "großvater väterlicherseits" : ["grandson (son's son) of", "granddaughter (son's daughter) of", "grandchild (son's son or daughter) of"], \
    "großvater?" : ["possibly grandson of", "possibly granddaughter of", "possibly grandchild of"], \
    "halbbruder" : ["half-brother of", "half-sister of", "half-brother or half-sister of"], \
    "halbschwester" : ["half-brother of", "half-sister of", "half-brother or half-sister of"], \
    "hauslehrer" : ["tutor was"], \
    "hochschullehrer" : ["student was"], \
    "hofdame" : ["lady-in-waiting was"], \
    "hofmaler" : ["court artist was"], \
    "identisch?" : ["possibly identified with"], \
    "identische person (?)" : ["possibly identified with"], \
    "identische person" : ["possibly identified with"], \
    "identität fraglich" : ["possibly identified with"], \
    "identität nicht geklärt" : ["possibly identified with"], \
    "identität nicht sichergeklärt" : ["possibly identified with"], \
    "identität ungeklärt" : ["possibly identified with"], \
    "identität unklar" : ["possibly identified with"], \
    "identität unsicher" : ["possibly identified with"], \
    "identität wahrscheinlich" : ["possibly identified with"], \
    "identität?" : ["possibly identified with"], \
    "illegitimer sohn" : ["illegitimate father of"], \
    "jugendfreund" : ["friend of (in youth)"], \
    "jugendfreundin" : ["friend of (in youth)"], \
    "jugendliebe" : ["romantic partner of (in youth)"], \
    "jüngere schwester" : ["older brother of", "older sister of", "older brother or sister of"], \
    "jüngerer bruder" : ["older brother of", "older sister of", "older brother or sister of"], \
    "jüngste schwester" : ["older brother of", "older sister of", "older brother or sister of"], \
    "jüngster bruder" : ["older brother of", "older sister of", "older brother or sister of"], \
    "jüngste tochter" : ["father of (youngest daughter)", "mother of (youngest daughter)", "father or mother of (youngest daughter)"], \
    "jüngster sohn" : ["father of (youngest son)", "mother of (youngest son)", "father or mother of (youngest son)"], \
    "kamerad" : ["friend of"], \
    "kind" : ["father of", "mother of", "father or mother of"], \
    "klassenkamerad" : ["classmate of"], \
    "kollege" : ["colleague of"], \
    "kollegin" : ["colleague of"], \
    "kompagnon" : ["partner of"], \
    "kontrahend" : ["opponent of"], \
    "korrespondent" : ["corresponded with"], \
    "korrespondentin" : ["corresponded with"], \
    "korrespondenzpartner" : ["corresponded with"], \
    "korrespondenz-partner" : ["corresponded with"], \
    "korrespondenzpartnerin" : ["corresponded with"], \
    "kunde" : ["customer was"], \
    "kusine" : ["cousin of"], \
    "lebensabschnittsgefährte" : ["romantic partner of"], \
    "lebensabschnittsgefährtin" : ["romantic partner of"], \
    "lebensgefährte" : ["romantic partner of"], \
    "lebensgefährtin" : ["romantic partner of"], \
    "lebenspartner" : ["romantic partner of"], \
    "lebenspartnerin" : ["romantic partner of"], \
    "lehnsherr" : ["vasall of"], \
    "lehrer" : ["student of"], \
    "lehrerin" : ["student of"], \
    "lehrherr" : ["apprentice of"], \
    "lehrjunge" : ["apprentice was"], \
    "lehrling" : ["apprentice was"], \
    "lehrmeister" : ["apprentice of"], \
    "leibarzt" : ["personal physician was"], \
    "leiblicher Vater" : ["illegitimate son of", "illegitimate daughter of", "illegitimate son or daughter of"], \
    "letzte Ehefrau" : ["husband of (his last marriage)"], \
    "liaison" : ["romantic partner of"], \
    "liebesbeziehung" : ["romantic partner of"], \
    "liebhaber" : ["romantic partner of"], \
    "liebhaberin" : ["romantic partner of"], \
    "malerkollege" : ["colleague of"], \
    "mallehrer" : ["student of"], \
    "mätresse" : ["romantic partner of"], \
    "mäzen" : ["benefactor was"], \
    "mäzenin" : ["benefactor was"], \
    "meister" : ["apprentice of"], \
    "meisterschüler" : ["teacher of"], \
    "mentor" : ["mentee of"] , \
    "militärischer vorgesetzter" : ["subordinate to (military)"], \
    "mitarbeiter" : ["worked under"], \
    "mitarbeiter" : ["worked under"], \
    "mitschüler" : ["fellow pupil of" ], \
    "mitschülerin" : ["fellow pupil of" ], \
    "mitstreiter" : ["ally of"], \
    "mögliche identität" : ["possibly identified with"], \
    "möglicherw. identisch" : ["possibly identified with"], \
    "möglicherweise" : ["possibly identified with"], \
    "möglicherweise identisch" : ["possibly identified with"], \
    "möglicherweise identische person" : ["possibly identified with"], \
    "mörder" : ["murdered by"], \
    "mordopfer" : ["murderer of"], \
    "mündel" : ["guardian of"], \
    "muse" : ["romantic partner of"], \
    "mutmaßl. ehemann" : ["possibly wife of"], \
    "mutmaßl. vater" : ["possibly son of", "possibly daughter of", "possibly son or daughter of"], \
    "mutmaßlich" : ["possibly identified with"], \
    "mutmaßlicher vater" : ["possibly son of", "possibly daughter of", "possibly son or daughter of"], \
    "mutter" : ["son of", "daughter of", "son or daughter of"], \
    "mutter (vermutl.)" : ["possibly son of", "possibly daughter of", "possibly son or daughter of"], \
    "mutter (vermutlich)" : ["possibly son of", "possibly daughter of", "possibly son or daughter of"], \
    "mutter von" : ["son of", "daughter of", "son or daughter of"], \
    "nachfahr" : ["ancestor of"], \
    "nachfahre" : ["ancestor of"], \
    "nachfolger" : ["predecessor of"], \
    "nachfolgerin" : ["predecessor of"], \
    "nachkomme" : ["ancestor of"], \
    "neffe" : ["uncle of", "aunt of", "uncle or aunt of"], \
    "nichte" : ["uncle of", "aunt of", "uncle or aunt of"], \
    "oheim" : ["nephew of", "niece of", "nephew or niece of"], \
    "onkel" : ["nephew of", "niece of", "nephew or niece of"], \
    "onkel?" : ["possibly nephew of", "possibly niece of", "possibly nephew or niece of"], \
    "opa" : ["grandson of", "granddaughter of", "grandchild of"], \
    "opfer" : ["victim was"], \
    "pächter" : ["landlord of"], \
    "partner" : ["partner of"], \
    "partnerin" : ["partner of"], \
    "pate" : ["godson of", "goddaughter of", "godchild of"], \
    "patenkind" : ["godfather of", "godmother of", "godparent of"], \
    "patenonkel" : ["godson of", "goddaughter of", "godchild of"], \
    "patensohn" : ["godfather of", "godmother of", "godparent of"], \
    "patentante" : ["godson of", "goddaughter of", "godchild of"], \
    "patentochter" : ["godfather of", "godmother of", "godparent of"], \
    "patient" : ["physician of"], \
    "patientin" : ["physician of"], \
    "patin" : ["godson of", "goddaughter of", "godchild of"], \
    "pflegemutter" : ["foster-son of", "foster-daughter of", "foster-child of"], \
    "pflegesohn" : ["foster-father of", "foster-mother of", "foster-parent of"], \
    "pflegetochter" : ["foster-father of", "foster-mother of", "foster-parent of"], \
    "pflegevater" : ["foster-son of", "foster-daughter of", "foster-child of"], \
    "prof." : ["student of"], \
    "professor" : ["student of"], \
    "schüler" : ["teacher of"], \
    "schülerin" : ["teacher of"], \
    "schulfreund" : ["friend of (at school)"], \
    "schulfreundin" : ["friend of (at school)"], \
    "schwager" : ["brother-in-law of", "sister-in-law of", "brother- or sister-in-law of"], \
    "schwägerin" : ["brother-in-law of", "sister-in-law of", "brother- or sister-in-law of"], \
    "schwester" : ["brother of", "sister of", "brother or sister of"], \
    "schwester (mutmaßlich)" : ["possibly brother of", "possibly sister of", "possibly brother or sister of"], \
    "schwester (vermutlich)" : ["possibly brother of", "possibly sister of", "possibly brother or sister of"], \
    "schwester?" : ["possibly brother of", "possibly sister of", "possibly brother or sister of"], \
    "schwiegermutter" : ["son-in-law of", "daughter-in-law of", "son- or daughter-in-law of"], \
    "schwiegersohn" : ["father-in-law of", "mother-in-law of", "father- or mother-in-law of"], \
    "schwiegertochter" : ["father-in-law of", "mother-in-law of", "father- or mother-in-law of"], \
    "schwiegervater" : ["son-in-law of", "daughter-in-law of", "son- or daughter-in-law of"], \
    "schwiegervater (1. ehe)" : ["son-in-law of (his first marriage)", "daughter-in-law of (her first marriage)", "son- or daughter-in-law of (first marriage)"], \
    "schwiegervater (1. ehe)" : ["son-in-law of (his second marriage)", "daughter-in-law of (her second marriage)", "son- or daughter-in-law of (second marriage)"], \
    "schwiegervater 1. ehe" : ["son-in-law of (his first marriage)", "daughter-in-law of (her first marriage)", "son- or daughter-in-law of (first marriage)"], \
    "schwiegervater 2. ehe" : ["son-in-law of (his second marriage)", "daughter-in-law of (her second marriage)", "son- or daughter-in-law of (second marriage)"], \
    "sekretär" : ["secretary was"], \
    "sekretärin" : ["secretary was"], \
    "sohn" : ["father of", "mother of", "father or mother of"], \
    "sohn (?)" : ["possibly father of", "possibly mother of", "possibly father or mother of"], \
    "sohn (1.ehe)" : ["father of (father's first marriage)", "mother of (mother's first marriage)", "father or mother of (first marriage)"], \
    "sohn (2.ehe)" : ["father of (father's second marriage)", "mother of (mother's second marriage)", "father or mother of (second marriage)"], \
    "sohn (vermutl.)" : ["possibly father of", "possibly mother of", "possibly father or mother of"], \
    "sohn (vermutlich)" : ["possibly father of", "possibly mother of", "possibly father or mother of"], \
    "sohn ?" : ["possibly father of", "possibly mother of", "possibly father or mother of"], \
    "sohn [?]" : ["possibly father of", "possibly mother of", "possibly father or mother of"], \
    "sohn 1.ehe" : ["father of (father's first marriage)", "mother of (mother's first marriage)", "father or mother of (first marriage)"], \
    "sohn 2.ehe" : ["father of (father's second marriage)", "mother of (mother's second marriage)", "father or mother of (second marriage)"], \
    "sohn aus 1.ehe" : ["father of (father's first marriage)", "mother of (mother's first marriage)", "father or mother of (first marriage)"], \
    "sohn aus 2.ehe" : ["father of (father's second marriage)", "mother of (mother's second marriage)", "father or mother of (second marriage)"], \
    "sohn aus 3.ehe" : ["father of (father's third marriage)", "mother of (mother's third marriage)", "father or mother of (third marriage)"], \
    "sohn aus der 1.ehe" : ["father of (father's first marriage)", "mother of (mother's first marriage)", "father or mother of (first marriage)"], \
    "sohn aus der 2.ehe" : ["father of (father's second marriage)", "mother of (mother's second marriage)", "father or mother of (second marriage)"], \
    "sohn aus ehe 1" : ["father of (father's first marriage)", "mother of (mother's first marriage)", "father or mother of (first marriage)"], \
    "sohn aus ehe 2" : ["father of (father's second marriage)", "mother of (mother's second marriage)", "father or mother of (second marriage)"], \
    "sohn aus erster ehe" : ["father of (father's first marriage)", "mother of (mother's first marriage)", "father or mother of (first marriage)"], \
    "sohn aus zweiter ehe" : ["father of (father's second marriage)", "mother of (mother's second marriage)", "father or mother of (second marriage)"], \
    "sohn, 1.ehe" : ["father of (father's first marriage)", "mother of (mother's first marriage)", "father or mother of (first marriage)"], \
    "sohn, 2.ehe" : ["father of (father's second marriage)", "mother of (mother's second marriage)", "father or mother of (second marriage)"], \
    "sohn, unehelich" : ["illegitimate father of", "illegitimate mother of", "illegitimate father or mother of"], \
    "sohn, vermutlich" : ["possibly father of", "possibly mother of", "possibly father or mother of"], \
    "sohn?" : ["possibly father of", "possibly mother of", "possibly father or mother of"], \
    "stammvater" : ["descendant of"], \
    "stiefbruder" : ["step-brother of", "step-sister of", "step-brother or step-sister of"], \
    "stiefmutter" : ["step-son of", "step-daughter of", "step-son or step-daughter of"], \
    "stiefschwester" : ["step-brother of", "step-sister of", "step-brother or step-sister of"], \
    "stiefsohn" : ["step-father of", "step-mother of", "step-father or step-mother of"], \
    "stieftochter" : ["step-father of", "step-mother of", "step-father or step-mother of"], \
    "stiefvater" : ["step-son of", "step-daughter of", "step-son or step-daughter of"], \
    "student" : ["student was"], \
    "studentin" : ["student was"], \
    "studienfreund" : ["friend of (at university)"], \
    "studienkollege" : ["fellow student of"], \
    "tante" : ["nephew of", "niece of", "nephew or niece of"], \
    "taufpate" : ["godson of", "goddaughter of", "godchild of"], \
    "taufpatin" : ["godson of", "goddaughter of", "godchild of"], \
    "teilhaber" : ["partner of"], \
    "tocher" : ["father of", "mother of", "father or mother of"], \
    "tochter" : ["father of", "mother of", "father or mother of"], \
    "tochter (?)" : ["possibly father of", "possibly mother of", "possibly father or mother of"], \
    "tochter (vermutlich)" : ["possibly father of", "possibly mother of", "possibly father or mother of"], \
    "tochter [?]" : ["possibly father of", "possibly mother of", "possibly father or mother of"], \
    "tochter 1.ehe" : ["father of (father's first marriage)", "mother of (mother's first marriage)", "father or mother of (first marriage)"], \
    "tochter 2.ehe" : ["father of (father's second marriage)", "mother of (mother's second marriage)", "father or mother of (second marriage)"], \
    "tochter aus 1.ehe" : ["father of (father's first marriage)", "mother of (mother's first marriage)", "father or mother of (first marriage)"], \
    "tochter aus 2.ehe" : ["father of (father's second marriage)", "mother of (mother's second marriage)", "father or mother of (second marriage)"], \
    "tochter aus 3.ehe" : ["father of (father's third marriage)", "mother of (mother's third marriage)", "father or mother of (third marriage)"], \
    "tochter aus der 1.ehe" : ["father of (father's first marriage)", "mother of (mother's first marriage)", "father or mother of (first marriage)"], \
    "tochter aus ehe 1" : ["father of (father's first marriage)", "mother of (mother's first marriage)", "father or mother of (first marriage)"], \
    "tochter aus erster ehe" : ["father of (father's first marriage)", "mother of (mother's first marriage)", "father or mother of (first marriage)"], \
    "tohter aus zweiter ehe" : ["father of (father's second marriage)", "mother of (mother's second marriage)", "father or mother of (second marriage)"], \
    "tochter, 1.ehe" : ["father of (father's first marriage)", "mother of (mother's first marriage)", "father or mother of (first marriage)"], \
    "tochter, 2.ehe" : ["father of (father's second marriage)", "mother of (mother's second marriage)", "father or mother of (second marriage)"], \
    "tochter, unehelich" : ["illegitimate father of", "illegitimate mother of", "illegitimate father or mother of"], \
    "unehel.sohn" : ["illegitimate father of", "illegitimate mother of", "illegitimate father or mother of"], \
    "uneheliche tochter" : ["illegitimate father of", "illegitimate mother of", "illegitimate father or mother of"], \
    "unehelicher sohn" : ["illegitimate father of", "illegitimate mother of", "illegitimate father or mother of"], \
    "unklare verwandschaft" : ["related to"], \
    "unklares verwandschaftsverhältnis" : ["related to"], \
    "urenkel" : ["great-grandfather of", "great-grandmother of", "great-grandparent of"], \
    "ur-enkel" : ["great-grandfather of", "great-grandmother of", "great-grandparent of"], \
    "urenkelin" : ["great-grandfather of", "great-grandmother of", "great-grandparent of"], \
    "urenkelsohn" : ["great-grandfather of", "great-grandmother of", "great-grandparent of"], \
    "urenkeltochter" : ["great-grandfather of", "great-grandmother of", "great-grandparent of"], \
    "urgroßenkel" : ["great-grandfather of", "great-grandmother of", "great-grandparent of"], \
    "urgroßenkelin" : ["great-grandfather of", "great-grandmother of", "great-grandparent of"], \
    "urgroßmutter" : ["great-grandson of", "great-granddaughter of", "great-grandchild of"], \
    "urgroßvater" : ["great-grandson of", "great-granddaughter of", "great-grandchild of"], \
    "urgroßneffe" : ["great-great-uncle of", "great-great-aunt of", "great-great-uncle or aunt of"], \
    "urgroßnichte" : ["great-great-uncle of", "great-great-aunt of", "great-great-uncle or aunt of"], \
    "urgroßonkel" : ["great-grand-nephew of", "great-grand-niece of", "great-grand-nephew or niece of"], \
    "urgroßtante" : ["great-grand-nephew of", "great-grand-niece of", "great-grand-nephew or niece of"], \
    "ururenkel" : ["great-great-grandfather of", "great-great-grandmother of", "great-great-grandparent of"], \
    "ur-urenkel" : ["great-great-grandfather of", "great-great-grandmother of", "great-great-grandparent of"], \
    "ur-ur-enkel" : ["great-great-grandfather of", "great-great-grandmother of", "great-great-grandparent of"], \
    "ururenkelin" : ["great-great-grandfather of", "great-great-grandmother of", "great-great-grandparent of"], \
    "ururgroßenkel" : ["great-great-grandfather of", "great-great-grandmother of", "great-great-grandparent of"], \
    "ururgroßmutter": ["great-great-grandson of", "great-great-granddaughter of", "great-great-grandchild of"], \
    "ururgroßvater": ["great-great-grandson of", "great-great-granddaughter of", "great-great-grandchild of"], \
    "ur-urgroßmutter": ["great-great-grandson of", "great-great-granddaughter of", "great-great-grandchild of"], \
    "ur-ur-großmutter": ["great-great-grandson of", "great-great-granddaughter of", "great-great-grandchild of"], \
    "ururgroßvater": ["great-great-grandson of", "great-great-granddaughter of", "great-great-grandchild of"], \
    "ur-urgroßvater": ["great-great-grandson of", "great-great-granddaughter of", "great-great-grandchild of"], \
    "ur-ur-großvater": ["great-great-grandson of", "great-great-granddaughter of", "great-great-grandchild of"], \
    "ururenkel" : ["great-great-great-grandfather of", "great-great-great-grandmother of", "great-great-great-grandparent of"], \
    "urururgroßmutter": ["great-great-great-grandson of", "great-great-great-granddaughter of", "great-great-great-grandchild of"], \
    "urururgroßvater": ["great-great-great-grandson of", "great-great-great-granddaughter of", "great-great-great-grandchild of"], \
    "vater" : ["son of", "daughter of", "son or daughter of"], \
    "vater (?)" : ["possibly son of", "possibly daughter of", "possibly son or daughter of"], \
    "vater (vermutlich)" : ["possibly son of", "possibly daughter of", "possibly son or daughter of"], \
    "vater ?" : ["possibly son of", "possibly daughter of", "possibly son or daughter of"], \
    "vater [?]" : ["possibly son of", "possibly daughter of", "possibly son or daughter of"], \
    "vater der 1.ehefrau" : ["son-in-law of (his first marriage)"], \
    "vater der 2.ehefrau" : ["son-in-law of (his second marriage)"], \
    "vater der 3.ehefrau" : ["son-in-law of (his third marriage)"], \
    "vater?" : ["possibly son of", "possibly daughter of", "possibly son or daughter of"], \
    "verheiratet" : ["husband of", "wife of", "spouse of"], \
    "verheiratet mit" : ["husband of", "wife of", "spouse of"], \
    "verlobte" : ["fiancé of"], \
    "verlobter" : ["fiancée of"], \
    "vermutlich" : ["possibly identified with"], \
    "vermutlich bruder" : ["possibly brother of", "possibly sister of", "possibly brother or sister of"], \
    "vermutlich cousin" : ["possibly cousin of"], \
    "vermutlich ehemann" : ["possibly wife of"], \
    "vermutlich sohn" : ["possibly father of", "possibly mother of", "possibly father or mother of"], \
    "vermutlich vater" : ["possibly son of", "possibly daughter of", "possibly son or daughter of"], \
    "vertraute" : ["close friend of"], \
    "vertrauter" : ["close friend of"], \
    "verwandt" : ["related to"], \
    "verwandte" : ["related to"], \
    "verwandter" : ["related to"], \
    "vetter" : ["cousin of"], \
    "vorfahr" : ["descendant of"], \
    "vorfahre" : ["descendant of"], \
    "vorfahren" : ["descendant of"], \
    "vorgänger" : ["successor to"], \
    "vorgängerin" : ["successor to"], \
    "vorgesetzter" : ["worked under"], \
    "vormund" : ["ward of"], \
    "weggefährte" : ["ally of"], \
    "witwe" : ["former husband of"], \
    "womöglich schwester" : ["possibly brother of", "possibly sister of", "possibly brother or sister of"], \
    "zeichenlehrer" : ["drawing teacher was"], \
    "zeitweise ehefrau" : ["husband of"], \
    "zusammenarbeit" : ["collaborated with"], \
    "zusammenarbeit mit" : ["collaborated with"], \
    "zwillingsbruder" : ["twin brother of", "twin sister of", "twin brother or sister of"], \
    "zwillingsschwester" : ["twin brother of", "twin sister of", "twin brother or sister of"], \
    }
    if relation in gnd_person_relations:
        relation_list = gnd_person_relations[relation]
        if len(relation_list) == 1:
            relation_new = relation_list[0]
        else:
            if sex == "male":
                relation_new = relation_list[0]
            elif sex == "female": 
                relation_new = relation_list[1]
            else:
                relation_new = relation_list[2]
    else:
        if relation_type == "bezf":
            relation_new = "related toxxx (" + relation + ")"
        if relation_type == "bezb":
            relation_new = "professional relation to (" + relation + ")"
        if relation_type == "beza": 
            relation_new = "other relationship to (" + relation + ")"
    return(relation_new)



# 1. Ehefrau (dates) / 1. Ehefrau dates
# 1. Ehefrau, geb. Name
# 2. Ehefrau (dates) / 2. Ehefrau dates / 2. Ehefrau, dates
# 2. Ehefrau, geb. Name
# 2. Ehemann (dates) / 2. Ehemann dates
# 3. Ehefrau (dates) / 3. Ehefrau dates
# 3. Ehefrau, geb. 
# 3 Ehemann (dates) / 3. Ehemann dates
# ehefrau (dates) / ehefrau dates
# ehemann (dates) / ehemann dates, ehemann, dates
# erste ehefrau dates
# großmutter, geb. 
#mutter (dates) [= rather dates of life]
# mutter, geb. 
# schwiegersohn dates
# schwiegertochter, geb.
#schwiegervater dates
#sohn (dates) [rather dates of life, not many]
#tochter (dates)
# tochter, dates
# vater (dates)
# often vater, job


def relation_correspondence(relation, sex):
# This function produces the corresponding term of relationship to a given term. 
# Up to now, it only covers relationships between persons - relationships between persons and organisations are to be added
# The function takes a relationship phrase from one person record ('A') and the sex from another person record ('B') and formulates a relationship phrase for 'B'

    corresponding_relationship_list = { \
    "acquaintance of" : ["acquaintance of"], \
    "administrator of" : ["administrated by"], \
    "adopted daughter of" : ["adoptive father of", "adoptive mother of", "adoptive father or mother of"], \
    "adopted son of" : ["adoptive father of", "adoptive mother of", "adoptive father or mother of"], \
    "adopted son or daughter of" : ["adoptive father of", "adoptive mother of", "adoptive father or mother of"], \
    "adoptive father of" : ["adopted son of", "adopted daughter of", "adopted son or daughter of"], \
    "adoptive father or mother of" : ["adopted son of", "adopted daughter of", "adopted son or daughter of"], \
    "adoptive mother of" : ["adopted son of", "adopted daughter of", "adopted son or daughter of"], \
    "advisor of" : ["advised by"], \
    "ally of" : ["ally of"], \
    "ancestor of" : ["descendant of"], \
    "appointed by" : ["appointee of"], \
    "appointee of" : ["appointed by"], \
    "apprentice of" : ["apprentice was"], \
    "apprentice was" : ["apprentice of"], \
    "artist to" : ["artist was"], \
    "artist was" : ["artist to"], \
    "assistant of" : ["assisted by"], \
    "assisted by" : ["assistant of"], \
    "associate of" : ["associate of"], \
    "associated with" : ["associated with"], \
    "aunt of" : ["nephew of", "niece of", "nephew or niece of"], \
    "benefactor was" : ["benefactor of"], \
    "biography by" : ["biographer of"], \
    "bride of" : ["bridegroom of"], \
    "bridegroom of" : ["bride of"], \
    "brother of" : ["brother of", "sister of", "brother or sister of"], \
    "brother or sister of" : ["brother of", "sister of", "brother or sister of"], \
    "brother- or sister-in-law of" : ["brother-in-law of", "sister-in-law of", "brother- or sister-in-law of"], \
    "brother-in-law of" : ["brother-in-law of", "sister-in-law of", "brother- or sister-in-law of"], \
    "classmate of" : ["classmate of"], \
    "client of" : ["client was"], \
    "client was" : ["client of"], \
    "close friend of" : ["close friend of"], \
    "collaborated with" : ["collaborated with"], \
    "colleague of" : ["colleague of"], \
    "confessor of" : ["confessor was"], \
    "confessor was" : ["confessor of"], \
    "consort of" : ["consort was"], \
    "consort was" : ["consort of"], \
    "corresponded with" : ["corresponded with"], \
    "counselled by" : ["counsellor was"], \
    "court artist to" : ["court artist was"], \
    "court artist was" : ["court artist to"], \
    "cousin of" : ["cousin of"], \
    "crowned" : ["crowned by"], \
    "crowned by" : ["crowned"], \
    "customer was" : ["customer of"], \
    "daughter of" : ["father of", "mother of", "father or mother of"], \
    "daughter-in-law of" : ["father-in-law of", "mother-in-law of", "father- or mother-in-law of"], \
    "daughter-in-law of (her fifth marriage)" : ["father-in-law of (her fifth marriage)", "mother-in-law of (her fifth marriage)", "father- or mother-in-law of (her fifth marriage)"], \
    "daughter-in-law of (her first marriage)" : ["father-in-law of (her first marriage)", "mother-in-law of (her first marriage)", "father- or mother-in-law of (her first marriage)"], \
    "daughter-in-law of (her fourth marriage)" : ["father-in-law of (her fourth marriage)", "mother-in-law of (her fourth marriage)", "father- or mother-in-law of (her fourth marriage)"], \
    "daughter-in-law of (her second marriage)" : ["father-in-law of (her second marriage)", "mother-in-law of (her second marriage)", "father- or mother-in-law of (her second marriage)"], \
    "daughter-in-law of (her third marriage)" : ["father-in-law of (her third marriage)", "mother-in-law of (her third marriage)", "father- or mother-in-law of (her third marriage)"], \
    "descendant of" : ["ancestor of"], \
    "director of" : ["directed by"], \
    "distinguished from" : ["distinguished from"], \
    "domestic partner of" : ["domestic partner of"], \
    "donor of" : ["donor was"], \
    "donor was" : ["donor of"], \
    "drawing teacher was" : ["drawing teacher of"], \
    "employee of" : ["employee was"], \
    "employee was" : ["employee of"], \
    "father or mother of (fifth son)" : ["fifth son of"], \
    "father or mother of (first son)" : ["first son of"], \
    "father or mother of (fourth son)" : ["fourth son of"], \
    "father or mother of (second son)" : ["second son of"], \
    "father or mother of (third son)" : ["third son of"], \
    "father of" : ["son of", "daughter of", "son or daughter of"], \
    "father of (father's first marriage)" : ["son of (first marriage)", "daughter of (first marriage)", "son or daughter (first marriage)"], \
    "father of (father's second marriage)" : ["son of (second marriage)", "daughter of (second marriage)", "son or daughter (second marriage)"], \
    "father of (father's third marriage)" : ["son of (third marriage)", "daughter of (third marriage)", "son or daughter (third marriage)"], \
    "father of (fifth daughter)" : ["fifth daughter of"], \
    "father of (fifth son)" : ["fifth son of"], \
    "father of (first child)" : ["first child of"], \
    "father of (first daughter)" : ["first daughter of"], \
    "father of (first son)" : ["first son of"], \
    "father of (fourth daughter)" : ["fourth daughter of"], \
    "father of (fourth son)" : ["fourth son of"], \
    "father of (second daughter)" : ["second daughter of"], \
    "father of (second son)" : ["second son of"], \
    "father of (third daughter)" : ["third daughter of"], \
    "father of (third son)" : ["third son of"], \
    "father of (youngest daughter)" : ["youngest daughter of"], \
    "father of (youngest son)" : ["youngest son of"], \
    "father or mother of" : ["son of", "daughter of", "son or daughter of"], \
    "father or mother of (fifth daughter)" : ["fifth daughter of"], \
    "father or mother of (first child)" : ["first child of"], \
    "father or mother of (first daughter)" : ["first daugther of"], \
    "father or mother of (first marriage)" : ["son of (from first marriage)", "daughter of (from first marriage)", "son or daughter of (from first marriage)"], \
    "father or mother of (fourth daughter)" : ["fourth daughter of"], \
    "father or mother of (second daughter)" : ["second daughter of"], \
    "father or mother of (second marriage)" : ["son of (from second marriage)", "daughter of (from second marriage)", "son or daughter of (from second marriage)"], \
    "father or mother of (third daughter)" : ["third daughter of"], \
    "father or mother of (third marriage)" : ["son of (from third marriage)", "daughter of (from third marriage)", "son or daughter of (from third marriage)"], \
    "father or mother of (youngest daughter)" : ["youngest daughter of"], \
    "father or mother of (youngest son)" : ["youngest son of"], \
    "father- or mother-in-law of" : ["son-in-law of", "daughter-in-law of", "son- or daughter-in-law of"], \
    "father-in-law of" : ["son-in-law of", "daughter-in-law of", "son- or daughter-in-law of"], \
    "fellow pupil of " : ["fellow pupil of"], \
    "fellow student of" : ["fellow student of"], \
    "fiancé of" : ["fiancée of"], \
    "fiancée of" : ["fiancé of"], \
    "former husband of" : ["former wife of"], \
    "former wife of" : ["former husband of"], \
    "formerly identified with" : ["formerly identified with"], \
    "foster-child of" : ["foster-father of", "foster-mother of", "foster-parent of"], \
    "foster-daughter of" : ["foster-father of", "foster-mother of", "foster-parent of"], \
    "foster-father of" : ["foster-son of", "foster-daughter of", "foster-child of"], \
    "foster-mother of" : ["foster-son of", "foster-daughter of", "foster-child of"], \
    "foster-parent of" : ["foster-son of", "foster-daughter of", "foster-child of"], \
    "foster-son of" : ["foster-father of", "foster-mother of", "foster-parent of"], \
    "founder of" : ["foster-father of", "foster-mother of", "foster-parent of"], \
    "friend of" : ["friend of"], \
    "friend of (at school)" : ["friend of (at school)"], \
    "friend of (in youth)" : ["friend of (in youth)"], \
    "godchild of" : ["godfather of", "godmother of", "godparent of"], \
    "goddaughter of" : ["godfather of", "godmother of", "godparent of"], \
    "godfather of" : ["godson of", "goddaughter of", "godchild of"], \
    "godmother of" : ["godson of", "goddaughter of", "godchild of"], \
    "godparent of" : ["godson of", "goddaughter of", "godchild of"], \
    "godson of" : ["godfather of", "godmother of", "godparent of"], \
    "grandchild (daughter's son or daughter) of" : ["maternal grandfather", "maternal grandmother", "maternal grandparent"], \
    "grandchild (son's son or daughter) of" : ["paternal grandfather", "paternal grandmother", "paternal grandparent"], \
    "grandchild of" : ["grandfather of", "grandmother of", "grandparent of"], \
    "granddaughter (daughter's daughter) of" : ["maternal grandfather", "maternal grandmother", "maternal grandparent"], \
    "granddaughter (son's daughter) of" : ["paternal grandfather", "paternal grandmother", "paternal grandparent"], \
    "granddaughter of" : ["grandfather of", "grandmother of", "grandparent of"], \
    "grandfather of" : ["grandson of", "granddaughter of", "grandchild of"], \
    "grandmother of" : ["grandson of", "granddaughter of", "grandchild of"], \
    "grandparent of" : ["grandson of", "granddaughter of", "grandchild of"], \
    "grandson (daughter's son) of" : ["maternal grandfather", "maternal grandmother", "maternal grandparent"], \
    "grandson (son's son) of" : ["paternal grandfather", "paternal grandmother", "paternal grandparent"], \
    "grandson of" : ["grandfather of", "grandmother of", "grandparent of"], \
    "great-aunt of" : ["grand-nephew of", "grand-niece of", "grand-nephew or grand-niece of"], \
    "great-grandchild of" : ["great-grandfather of", "great-grandmother of", "great-grandparent of"], \
    "great-granddaughter of" : ["great-grandfather of", "great-grandmother of", "great-grandparent of"], \
    "great-grandfather of" : ["great-grandson of", "great-granddaughter of", "great-grandchild of"], \
    "great-grandmother of" : ["great-grandson of", "great-granddaughter of", "great-grandchild of"], \
    "great-grand-nephew of" : ["great-great-uncle of", "great-great-aunt of", "great-great-uncle or aunt of"], \
    "great-grand-nephew or niece of" : ["great-great-uncle of", "great-great-aunt of", "great-great-uncle or aunt of"], \
    "great-grand-niece of" : ["great-great-uncle of", "great-great-aunt of", "great-great-uncle or aunt of"], \
    "great-grandparent of" : ["great-grandson of", "great-granddaughter of", "great-grandchild of"], \
    "great-grandson of" : ["great-grandfather of", "great-grandmother of", "great-grandparent of"], \
    "great-great-aunt of" : ["great-grand-nephew of", "great-grand-niece of", "great-grand-nephew or niece of"], \
    "great-great-grandchild of" : ["great-great-grandfather of", "great-great-grandmother of", "great-great-grandparent of"], \
    "great-great-granddaughter of" : ["great-great-grandfather of", "great-great-grandmother of", "great-great-grandparent of"], \
    "great-great-grandfather of" : ["great-great-grandson of", "great-great-granddaughter of", "great-great-grandchild of"], \
    "great-great-grandmother of" : ["great-great-grandson of", "great-great-granddaughter of", "great-great-grandchild of"], \
    "great-great-grandparent of" : ["great-great-grandson of", "great-great-granddaughter of", "great-great-grandchild of"], \
    "great-great-grandson of" : ["great-great-grandfather of", "great-great-grandmother of", "great-great-grandparent of"], \
    "great-great-great-grandchild of" : ["great-great-great-grandfather of", "great-great-great-grandmother of", "great-great-great-grandparent of"], \
    "great-great-great-granddaughter of" : ["great-great-great-grandfather of", "great-great-great-grandmother of", "great-great-great-grandparent of"], \
    "great-great-great-grandfather of" : ["great-great-great-grandson of", "great-great-great-granddaughter of", "great-great-great-grandchild of"], \
    "great-great-great-grandmother of" : ["great-great-great-grandson of", "great-great-great-granddaughter of", "great-great-great-grandchild of"], \
    "great-great-great-grandparent of" : ["great-great-great-grandson of", "great-great-great-granddaughter of", "great-great-great-grandchild of"], \
    "great-great-great-grandson of" : ["great-great-great-grandfather of", "great-great-great-grandmother of", "great-great-great-grandparent of"], \
    "great-great-uncle of" : ["great-grand-nephew of", "great-grand-niece of", "great-grand-nephew or niece of"], \
    "great-great-uncle or aunt of" : ["great-grand-nephew of", "great-grand-niece of", "great-grand-nephew or niece of"], \
    "great-nephew of" : ["great-uncle of", "great-aunt of", "great-uncle or great-aunt of"], \
    "great-nephew or great-niece of" : ["great-uncle of", "great-aunt of", "great-uncle or great-aunt of"], \
    "great-niece of" : ["great-uncle of", "great-aunt of", "great-uncle or great-aunt of"], \
    "great-uncle of" : ["grand-nephew of", "grand-niece of", "grand-nephew or grand-niece of"], \
    "great-uncle or great-aunt of" : ["grand-nephew of", "grand-niece of", "grand-nephew or grand-niece of"], \
    "guardian of" : ["ward of"], \
    "half-brother of" : ["half-brother of", "half-sister of", "half-brother or half-sister of"], \
    "half-brother or half-sister of" : ["half-brother of", "half-sister of", "half-brother or half-sister of"], \
    "half-sister of" : ["half-brother of", "half-sister of", "half-brother or half-sister of"], \
    "husband of" : ["wife of"], \
    "husband of (his fifth marriage)" : ["fifth wife of"], \
    "husband of (his first marriage)" : ["first wife of"], \
    "husband of (his fourth marriage)" : ["fourth wife of"], \
    "husband of (his last marriage)" : ["last wife of"], \
    "husband of (his second marriage)" : ["second wife of"], \
    "husband of (his third marriage)" : ["third wife of"], \
    "husband or wife of" : ["husband or wife of"], \
    "husband or wife of (first marriage)" : ["first husband or wife of"], \
    "husband or wife of (second marriage)" : ["second husband or wife of"], \
    "illegitimate daughter of" : ["illegitimate father of", "illegitimate mother of", "illegitimate father or mother of"], \
    "illegitimate father of" : ["illegitimate son of", "illegitimate daughter of", "illegitimate son or daughter of"], \
    "illegitimate father or mother of" : ["illegitimate son of", "illegitimate daughter of", "illegitimate son or daughter of"], \
    "illegitimate mother of" : ["illegitimate son of", "illegitimate daughter of", "illegitimate son or daughter of"], \
    "illegitimate son of" : ["illegitimate father of", "illegitimate mother of", "illegitimate father or mother of"], \
    "illegitimate son or daughter of" : ["illegitimate father of", "illegitimate mother of", "illegitimate father or mother of"], \
    "influenced" : ["influenced by"], \
    "influenced by" : ["influenced"], \
    "lady-in-waiting was" : ["lady-in-waiting of"], \
    "landlord of" : ["tenant of"], \
    "leader of" : ["lead by"], \
    "master of" : ["master was"], \
    "master or mistress of" : ["master of mistress was"], \
    "master or mistress was" : ["master of mistress of"], \
    "master was" : ["master of"], \
    "meaning overlaps with" : ["meaning overlaps with"], \
    "member of this family" : ["family of"], \
    "mentee of" : ["mentor of"], \
    "mistress of" : ["mistress was"], \
    "mistress was" : ["mistress of"], \
    "mother of" : ["son of", "daughter of", "son or daughter of"], \
    "mother of (fifth daughter)" : ["fifth daughter of"], \
    "mother of (fifth son)" : ["fifth son of"], \
    "mother of (first child)" : ["first child of"], \
    "mother of (first daughter)" : ["first daughter of"], \
    "mother of (first son)" : ["first son of"], \
    "mother of (fourth daughter)" : ["fourth daughter of"], \
    "mother of (fourth son)" : ["fourth son of"], \
    "mother of (mother's first marriage)" : ["son of (first marriage)", "daughter of (first marriage)", "son or daughter of (first marriage)"], \
    "mother of (mother's second marriage)" : ["son of (second marriage)", "daughter of (second marriage)", "son or daughter of (second marriage)"], \
    "mother of (mother's third marriage)" : ["son of (third marriage)", "daughter of (third marriage)", "son or daughter of (third marriage)"], \
    "mother of (second daughter)" : ["second daughter of"], \
    "mother of (second son)" : ["second son of"], \
    "mother of (third daughter)" : ["third daughter of"], \
    "mother of (third son)" : ["third son of"], \
    "mother of (youngest daughter)" : ["youngest daughter of"], \
    "mother of (youngest son)" : ["youngest son of"], \
    "mother-in-law of" : ["son-in-law of", "daughter-in-law of", "son- or daughter-in-law of"], \
    "murdered by" : ["murderer of"], \
    "murderer of" : ["murdered by"], \
    "nephew of" : ["uncle of", "aunt of", "uncle or aunt of"], \
    "nephew or niece of" : ["uncle of", "aunt of", "uncle or aunt of"], \
    "niece of" : ["uncle of", "aunt of", "uncle or aunt of"], \
    "older brother of" : ["younger brother of", "younger sister of", "younger brother or sister of"], \
    "older brother or sister of" : ["younger brother of", "younger sister of", "younger brother or sister of"], \
    "older sister of" : ["younger brother of", "younger sister of", "younger brother or sister of"], \
    "opponent of" : ["opponent of"], \
    "owner of" : ["owner was"], \
    "partner of" : ["partner of"], \
    "patron of" : ["patron was"], \
    "patron was" : ["patron of"], \
    "performed with" : ["performed with"], \
    "personal physician was" : ["physician of"], \
    "PhD student of" : ["PhD supervisor of"], \
    "PhD supervisor of" : ["PhD student of"], \
    "physician of" : ["personal physician was"], \
    "possibly brother of" : ["possibly brother of", "possibly sister of", "possibly brother of sister of"], \
    "possibly brother or sister of" : ["possibly brother of", "possibly sister of", "possibly brother of sister of"], \
    "possibly cousin of" : ["possibly cousin of"], \
    "possibly daughter of" : ["possibly father of", "possibly mother of", "possibly father or mother of"], \
    "possibly father of" : ["possibly son of", "possibly daughter of", "possibly son or daughter of"], \
    "possibly father or mother of" : ["possibly son of", "possibly daughter of", "possibly son or daughter of"], \
    "possibly grandchild of" : ["possibly grandfather of", "possibly grandmother of", "possibly grandparent of"], \
    "possibly granddaughter of" : ["possibly grandfather of", "possibly grandmother of", "possibly grandparent of"], \
    "possibly grandson of" : ["possibly grandfather of", "possibly grandmother of", "possibly grandparent of"], \
    "possibly husband of" : ["possibly wife of"], \
    "possibly identified with" : ["possibly identified with"], \
    "possibly member of this family" : ["possibly family of"], \
    "possibly mother of" : ["possibly son of", "possibly daughter of", "possibly son or daughter of"], \
    "possibly nephew of" : ["possibly uncle of", "possibly aunt of", "possibly uncle or aunt of"], \
    "possibly nephew or niece of" : ["possibly uncle of", "possibly aunt of", "possibly uncle or aunt of"], \
    "possibly niece of" : ["possibly uncle of", "possibly aunt of", "possibly uncle or aunt of"], \
    "possibly related to" : ["possibly related to"], \
    "possibly sister of" : ["possibly brother of", "possibly sister of", "possibly brother of sister of"], \
    "possibly son of" : ["possibly father of", "possibly mother of", "possibly father or mother of"], \
    "possibly son or daughter of" : ["possibly father of", "possibly mother of", "possibly father or mother of"], \
    "possibly wife of" : ["possibly husband of"], \
    "predecessor of" : ["successor to"], \
    "related to" : ["related to"], \
    "relative by marriage of" : ["relative by marriage of"], \
    "romantic partner of" : ["romantic partner of"], \
    "romantic partner of (in youth)]" : ["romantic partner of"], \
    "second cousin of" : ["second cousin of"], \
    "secretary was" : ["secretary of"], \
    "sister of" : ["brother of", "sister of", "brother or sister of"], \
    "sister-in-law of" : ["brother-in-law of", "sister-in-law of", "brother- or sister-in-la of"], \
    "son of" : ["father of", "mother of", "father or mother of"], \
    "son or daughter of" : ["father of", "mother of", "father or mother of"], \
    "son- or daughter-in-law of" : ["father-in-law of", "mother-in-law of", "father- or mother-in-law of"], \
    "son- or daughter-in-law of (first marriage)" : ["father-in-law (first marriage)", "mother-in-law (first marriage)", "father- or mother-in-law (first marriage)"], \
    "son- or daughter-in-law of (second marriage)" : ["father-in-law (second marriage)", "mother-in-law (second marriage)", "father- or mother-in-law (second marriage)"], \
    "son- or daughter-in-law of (third marriage)" : ["father-in-law (third marriage)", "mother-in-law (third marriage)", "father- or mother-in-law (third marriage)"], \
    "son-in-law of" : ["father-in-law of", "mother-in-law of", "father- or mother-in-law of"], \
    "son-in-law of (his fifth marriage)" : ["father-in-law (fifth marriage)", "mother-in-law (fifth marriage)", "father- or mother-in-law (fifth marriage)"], \
    "son-in-law of (his first marriage)" : ["father-in-law (first marriage)", "mother-in-law (first marriage)", "father- or mother-in-law (first marriage)"], \
    "son-in-law of (his fourth marriage)" : ["father-in-law (fourth marriage)", "mother-in-law (fourth marriage)", "father- or mother-in-law (fourth marriage)"], \
    "son-in-law of (his second marriage)" : ["father-in-law (second marriage)", "mother-in-law (second marriage)", "father- or mother-in-law (second marriage)"], \
    "son-in-law of (his third marriage)" : ["father-in-law (third marriage)", "mother-in-law (third marriage)", "father- or mother-in-law (third marriage)"], \
    "spouse of" : ["spouse of"], \
    "step-brother of" : ["step-brother of", "step-sister of", "step-brother or step-sister of"], \
    "step-brother or step-sister of" : ["step-brother of", "step-sister of", "step-brother or step-sister of"], \
    "step-daughter of" : ["step-father of", "step-mother of", "step-father or step-mother of"], \
    "step-father of" : ["step-son of", "step-daughter of", "step-son or step-daughter of"], \
    "step-father or step-mother of" : ["step-son of", "step-daughter of", "step-son or step-daughter of"], \
    "step-mother of" : ["step-son of", "step-daughter of", "step-son or step-daughter of"], \
    "step-sister of" : ["step-brother of", "step-sister of", "step-brother or step-sister of"], \
    "step-son of" : ["step-father of", "step-mother of", "step-father or step-mother of"], \
    "step-son or step-daughter of" : ["step-father of", "step-mother of", "step-father or step-mother of"], \
    "student of" : ["student was"], \
    "student was" : ["student of"], \
    "subordinate to (military)" : ["military superior of"], \
    "successor to" : ["predecessor of"], \
    "superior of" : ["worked under"], \
    "teacher of" : ["teacher was"], \
    "to this family belonged" : ["family of"], \
    "tutor was" : ["tutor of"], \
    "twin brother of" : ["twin brother of", "twin sister of", "twin brother or twin sister of"], \
    "twin brother or sister of" : ["twin brother of", "twin sister of", "twin brother or twin sister of"], \
    "twin sister of" : ["twin brother of", "twin sister of", "twin brother or twin sister of"], \
    "uncle of" : ["nephew of", "niece of", "nephew or niece of"], \
    "uncle or aunt of" : ["nephew of", "niece of", "nephew or niece of"], \
    "friend of (at university)" : ["friend of (at university)"], \
    "vasall of" : ["liege lord of"], \
    "victim was" : ["victim of"], \
    "ward of" : ["guardian of"], \
    "wife of" : ["husband of"], \
    "wife of (her fifth marriage)" : ["fifth husband of"], \
    "wife of (her first marriage)" : ["first husband of"], \
    "wife of (her fourth marriage)" : ["fourth husband of"], \
    "wife of (her second marriage)" : ["second husband of"], \
    "wife of (her third marriage)" : ["third husband of"], \
    "worked under" : ["superior of"], \
    "worked with" : ["worked with"], \
    "worker was" : ["worked for"], \
    "younger brother of" : ["older brother of", "older sister of", "older brother or sister of"], \
    "younger brother or sister of" : ["older brother of", "older sister of", "older brother or sister of"], \
    "younger sister of" : ["older brother of", "older sister of", "older brother or sister of"], \
    }

    if relation in relation_correspondence:
        corresponding_relation_list = relation_correspondence[relation]
        if len(corresponding_relation_list = 1):
            corresponding_relation = corresponding_relation_list[0]
        else:
            if sex == "male":
                corresponding_relation = corresponding_relation_list[0]
            elif sex == "female": 
                corresponding_relation = corresponding_relation_list[1]
            else:
                corresponding_relation = corresponding_relation_list[2]
    return(corresponding_relation)

