"""
This module contains a number of simple functions that standardise information about relationships taken from authority records. 
"""

encoding_list = {"Ö": "Ö", "ä": "ä", "ö": "ö", "ü": "ü", "é": "é"}


def gnd_person_person_relation(relation_original, sex, relation_type): 
# This function takes the German phrase for a relationship from the GND and gives an English phrase (in reverse, since the GND describes the connection of the 'far' person to the 'near' person, and I do it vice versa)
# Up to now, it only covers relationships between persons - relationships between persons and organisations are to be added
# The function takes the relationship phrase from the GND plus the sex of the 'near' person and returns one phrase for the relationship. 
# The abbreviated relation types from 
    relation = ""
    relation_new = ""
    relation_comments = ""
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
    "amtsvorgänger" : ["successor of"], \
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
    "faktor" : ["head of workshop ('faktor') was"], \
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
    "vorgänger" : ["successor of"], \
    "vorgängerin" : ["successor of"], \
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
    if relation_original != "":
        for old, new in encoding_list.items():
            if old in relation_original:
                relation_original = relation_original.replace(old, new)    
        relation = relation_original.lower()
        gnd_person_relations_replace = {". ": ".", "ehegatte" : "ehemann", "ehegattin" : "ehefrau", "gemahl" : "ehemann", "gemahlin" : "ehefrau", \
        "erste " : "1.", "erster " : "1.", "zweite " : "2.", "zweiter " : "2.", "dritte " : "3.", "dritter " : "3.", "vierte" : "4.", "vierter" : "4.", "gross" : "groß"}
        for old, new in gnd_person_relations_replace.items():
            relation = relation.replace(old, new)
    
    if relation != "" and relation in gnd_person_relations:
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
        relation_comments = relation_original      
        if relation_type == "bezf":
            relation_new = "related to" 
        elif relation_type == "bezb":
            relation_new = "professional relation to" 
        elif relation_type == "beza" or relation_type == "rela": 
            relation_new = "other relationship to"
    return(relation_new, relation_comments)



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

def gnd_person_org_relation(relation_original, sex, relation_type):
    relation_comment = ""
    for old, new in encoding_list.items():
        relation_original = relation_original.replace(old, new)    
    relation = relation_original.lower()
    gnd_person_org_relations = { \
        "1. vorsitzende" : ["chairwoman of"], \
        "1. vorsitzender" : ["chairman of"], \
        "2. vorsitzende" : ["deputy chairwoman of"], \
        "2. vorsitzender" : ["deputy chairman of"], \
        "absolvent" : ["graduate of"], \
        "absolventin" : ["graduate of"], \
        "abt" : ["abbot of"], \
        "äbtissin" : ["abbess of"], \
        "alumnus" : ["graduate of"], \
        "ausbildung" :  ["trained at"], \
        "begründer" : ["founder of"], \
        "berater" : ["advisor of"], \
        "beraterin" : ["advisor of"], \
        "beistzer" : ["owner of"], \
        "besitzerin" : ["owner of"], \
        "bibliothekar" : ["librarian to"], \
        "bischof" : ["bishop of"], \
        "chairman" : ["chairman of"], \
        "chordirektor" : ["choir master at"], \
        "chorleiter" : ["choir master at"], \
        "chorsänger" : ["chorister at"], \
        "co-founder" : ["co-founder of"], \
        "dean" : ["dean of"], \
        "dekan" : ["dean of"], \
        "deputy director" : ["deputy director of"], \
        "directeur" : ["director of"], \
        "director" : ["director of"], \
        "direktor" : ["director of"], \
        "direktorin" : ["director of"], \
        "diss." : ["doctorate at"], \
        "dissertation" : ["doctorate at"], \
        "doctoral candidate" : ["doctoral student at"], \
        "doctoral student" : ["doctoral student at"], \
        "doktorand" : ["doctoral student at"], \
        "doktorandin" : ["doctoral Student at"], \
        "dozent" : ["teacher at"], \
        "dozentin" : ["teacher at"], \
        "eigentümer" : ["owner of"], \
        "erzbischof" : ["archbishopf of"], \
        "faktor" : ["head of workshop ('faktor') of"], \
        "fellow" : ["fellow of"], \
        "firmengründer" : ["founder of"], \
        "founder" : ["founder of"], \
        "founding director" : ["founding director of"], \
        "gehilfe" : ["assistant at"], \
        "geschäftsführer" : ["chief clerk of"], \
        "gesellschafter" : ["partner of"], \
        "gesellschafterin" : ["partner of"], \
        "grue" : ["founder of"], \
        "gründer" : ["founder of"], \
        "gründerin" : ["founder of"], \
        "gründungsdirektor" : ["founding director of"], \
        "gründungsmitglied" : ["founding member of"], \
        "gymnasiallehrer" : ["teacher at"], \
        "gymnasialprofessor" : ["teacher at"], \
        "habilitation" : ["habilitation at"], \
        "häftling" : ["prisoner at"], \
        "herausgeber" : ["editor of"], \
        "hilfsprediger" : ["assistant preacher at"], \
        "hochschullehrer" : ["professor at"], \
        "hochschullehrerin" : ["professor at"], \
        "inhaber" : ["owner of"], \
        "inhaberin" : ["owner of"], \
        "kantor" : ["cantor at"], \
        "kanzler" : ["chancellor of"], \
        "kapellmeister" : ["head of music at"], \
        "kommandant" : ["commander of"], \
        "konrektor" : ["deputy director of"], \
        "lehre" : ["apprentice at"], \
        "lehrer" : ["teacher at"], \
        "lehrerin" : ["teacher at"], \
        "lehrkraft" : ["teacher at"], \
        "lehrling" : ["apprentice at"], \
        "lehrling und gehilfe" : ["apprentice and assistant at"], \
        "leiter" : ["director of"], \
        "leiterin" : ["director of"], \
        "leitung" : ["director of"], \
        "member" : ["member of"], \
        "minister" : ["minister at"], \
        "mitarbeiter" : ["collaborator at"], \
        "mitbegr." : ["co-founder of"], \
        "mitbegründer" : ["co-founder of"], \
        "mitbegründer" : ["co-foundress of"], \
        "mitglied" : ["member of"], \
        "mitgründer" : ["co-founder of"], \
        "mitgründer" : ["co-foundress of"], \
        "mitinhaber" : ["co-owner of"], \
        "mönch" : ["monk at"], \
        "nachfolgeinstitution" : ["successor of"], \
        "nachfolgeinstitution der druckerei" : ["successor of"], \
        "nachfolger" : ["predecessor of"], \
        "nachlass" : ["papers at"], \
        "nutzer" : ["user of"], \
        "oberin" : ["mother superior of"], \
        "oberlehrer" : ["senior teacher at"], \
        "obfrau" : ["chairwoman of"], \
        "obmann" : ["chairman of"], \
        "ordensgründer" : ["founder of"], \
        "ordensgründerin" : ["foundress of"], \
        "ordensmitglied" : ["member of"], \
        "ordentliches mitglied" : ["full member of"], \
        "papiermacher" : ["paper maker at"], \
        "partner" : ["partner at"], \
        "pastor" : ["minister at"], \
        "pfarrer" : ["rector at"], \
        "ph. d." : ["doctorate at"], \
        "ph. d. candidate" : ["doctoral student at"], \
        "ph. d. student" : ["doctoral student at"], \
        "ph.d." : ["doctorate at"], \
        "ph.d. candidate" : ["doctoral student at"], \
        "ph.d. student" : ["doctoral student at"], \
        "phd." : ["doctorate at"], \
        
        "phd. candidate" : ["doctoral student at"], \
        "phd. student" : ["doctoral student at"], \
        "präfekt" : ["prefect of"], \
        "praeses" : ["praeses of"], \
        "präsident" : ["president of"], \
        "president" : ["president of"], \
        "principal" : ["principal of"], \
        "prior" : ["prior of"], \
        "priorin" : ["prioress of"], \
        "prof." : ["professor at"], 
        "professor" : ["professor at"], \
        "professorin" : ["professor at"], \
        "professur" : ["professor at"], \
        "promotion" : ["doctorate at"], \
        "prorektor" : ["prorector (pro vice-chancellor) at"], \
        "provinzial" : ["provincial of"], \
        "rector" : ["rector at"], \
        "regens" : ["principal of"], \
        "rektor" : ["rector (vice-chancellor) at"], \
        "richter" : ["judge at"], \
        "sammler" : ["collector for"], \
        "sänger" : ["singer at"], \
        "sängerin" : ["singer at"], \
        "schauspieler" : ["actor at"], \
        "schauspielerin" : ["actress at"], \
        "schüler" : ["pupil at"], \
        "schülerin" : ["pupil at"], \
        "schulleiter" : ["headmaster of"], \
        "schulleiterin" : ["headmistress of"], \
        "stifter" : ["benefactor of"], \
        "stifterin" : ["benefactress of"], \
        "stud. jur.": ["law student at"], \
        "stud. med." : ["medical student at"], \
        "stud. kam." : ["student of economy at"], \
        "stud. phil" : ["student of philosphy at"], \
        "stud. theol" : ["divinity student at"], \
        "student" : ["student at"], \
        "studentin" : ["student at"], \
        "studienort" : ["student at"], \
        "studienstätte" : ["student at"], \
        "studium" : ["student at"], \
        "subprior" : ["sub-prior at"], \
        "superintendent" : ["superintendent at"], \
        "superior" : ["religious superior at"], \
        "tänzer" : ["dancer at"], \
        "tänzerin" : ["dancer at"], \
        "theaterdirektor" : ["director of"], \
        "universitätsverwandter" : ["affiliated to"], \
        "verleger" : ["owner"], \
        "vizekanzler" : ["vice-chancellor of"], \
        "vizepräsident" : ["vice-president of"], \
        "vizepräsidentin" : ["vice-president of"], \
        "vorgängerinstitution" : ["predecessor of"], \
        "vorgängerinstitution der druckerei" : ["predecessor of"], \
        "vorsitzende" : ["chairwoman of"], \
        "vorsitzender" : ["chairman of"], \
        "vorsteher" : ["head of"], \
        "weiterführender betrieb" : ["succeded by (organisation)"]
    }
    if relation in gnd_person_org_relations:
        relation_list = gnd_person_org_relations[relation]
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
        relation_comment = relation_original
        if relation_type == "affi":
            relation_new = "affiliated to"
        elif relation_type == "grue":
            relation_new = "founded by"
        elif relation_type == "korr": 
            relation_new = "corresponded with"
        elif relation_type == "mitg": 
            relation_new = "member of"
        elif relation_type == "rela": 
            relation_new = "related to"


    return(relation_new, relation_comment)


def gnd_person_place_relation(relation_original, sex, relation_type):
    #print("in module gnd_person_place_relation")
    #print("relation as imported:")
    #print(relation_original)
    connection_location_alternative1 = {"geburtsort:" : "geburtsort", "sterbeort:" : "sterbeort", "andersltd.:" : "andersltd.", "begr.:" : "begr.", "auch:" : "auch"}
    connection_location_alternative2 = ["abw ", "abweichend: ", "abweichend " , "abweichende ", "abweichender ", "alternativer ", \
                                        "anders lautender ", "andersl. ", "anderslaut. ", "anderslautend. ", "anderslautend ", "anderslautender ", \
                                        "anderslt. ", "andersltd. ", "anderstl. ", "anderstlautender "]
    connection_location_alternative3 = {"other geburtsort" :  "or", "other geburtsorte:" : "or", "other sterbeort" : "or", "adresse" : "", "begr." : "buried in", \
                                        "begraben in" : "buried in" , "bei " : "near ", "bestattet in" : "buried in", "eigentl." : "in reality", \
                                        "falscher geburtsort" : "not", "falscher sterbeort" : "not", "geburtsort nicht:" : "not", "geburtsort other" : "or", "geburtsort auch" : "or", 
                                        "other" : "or", "oder" : "or", "sterbeort other" : "or", "sterbeort auch" : "or", "sterbeort nicht:" : "not", "nicht:" : "not", 
                                        "vielm." : "rather"}
    connection_location_doubtful = {"?" : "possibly ", "Ang. unsicher" : "possibly", "fragwürdiger geburtsort" : "supposedly", \
                                    "fragwürdiger sterbeort" : "supposedly", "geburtsort fraglich" : "possibly",  "geburtsort unsicher" : "possibly", \
                                    "geburtsort vermutet" : "possibly", "geburtsort vermutl." : "possibly", "geburtsort vermutlich" : "possibly", "möglicher geburtsort" : "possibly", \
                                    "möglicher sterbeort" : "possibly", "mutmaßl. geburtsort" : "possibly",  \
                                    "mußmaßlicher geburtsort" : "possibly", "mutmaßlicher sterbeort" : "possibly", "mutmaßlicher wirkungsort" : "possibly",  \
                                    "sterbeort fraglich" : "possibly", "sterbeort nicht sicher" : "possibly", "sterbeort unsicher" : "possibly", \
                                    "sterbeort vermutlich" : "possibly", "vermuteter geburtsort" : "possibly", "vermutl." : "possibly", \
                                    "vermutl. geburtsort" : "possibly", "vermutl. sterbeort" : "possibly", "vermutl. wirkungsort" : "possibly", \
                                    "vermutlicher geburtsort" : "possibly", "vermutlicher sterbeort" : "possibly", "vermutlicher wirkungsort" : "possibly", "wahrsch. geburtsort" : "possibly", \
                                    "wahrscheinlicher geburtsort" : "possibly", "wahrscheinlicher sterbeort" : "possibly", "zuordnung nicht sicher" : "posssibly", 
                                    "zuordnung ungewiss" : "possibly", "angeblich" : "supposedly", "fraglich" : "possibly", "möglicherweise" : "possibly", "mußmaßlich" : "possibly","nicht gesichert" : "possibly","nicht sicher" : "possibly", \
                                    "unsicher" : "possibly", "vermutet" : "possibly", "vermutlich" : "possibly", "wahrscheinlich" : "possibly"}    

    gnd_person_place_relations = {
    "alterssitz" : ["retired to"], \
    "arbeitsort" : ["worked in"], \
    "architekt" : ["architect in"], \
    "arzt" : ["physician in"], \
    "aufgewachsen" : ["grown up in"], \
    "aufwachsen" : ["grown up in"], \
    "ausbildung" : ["trained in"], \
    "ausbildungs- oder studienort" : ["trained or studied in"], \
    "ausbildungsort" : ["trained in"], \
    "beerdigungsort" : ["buried in"], \
    "begräbnisort" : ["buried in"], \
    "beisetzungsort" : ["buried in"], \
    "bestattungsort" : ["buried in"], \
    "bishof" : ["bishop in"], \
    "bürgermeister" : ["mayor of"], \
    "diss." : ["did doctorate in"], \
    "dort aufgewachsen" : ["grown up in"], \
    "erscheinungsort" : ["publications in"], \
    "getauft" : ["baptised in"], \
    "gutsbesitzer" : ["landowner in"], \
    "gutsherr" : ["landowner in"], \
    "habil." : ["habilitation in"], \
    "habilitation" : ["habilitation in"], \
    "hauptlebensort" : ["lived chiefly in"], \
    "hauslehrer" : ["private tutor in"], \
    "heimatort" : ["home was"], \
    "herkunft" : ["came from"], \
    "herkunftsort" : ["came from"], \
    "hilfsprediger" : ["assistant preacher in"], \
    "hingerichtet" :  ["executed in"], \
    "kindheit" : ["childhood spent in"], \
    "kindheit und jugend" : ["grown up in"], \
    "lebensort" : ["lived in"], \
    "lehrer" : ["teacher in "], \
    "ort der promotion" : ["did doctorate in"], \
    "papiermühle" : ["at paper mill in"], \
    "pastor" : ["minister in"], \
    "pfarrer" : ["rector in"], \
    "promotion" : ["did doctorate in"], \
    "promotion und habil." : ["did doctorate and habilitation in"], 
    "promotionsort" : ["did doctorate in"], \
    "promotion und habilitation" : ["did doctorate and habilitation in"], \
    "schulbesuch" : ["went to school in"], \
    "schule" : ["went to school in"], \
    "schulort" : ["went to school in"], \
    "schulzeit" : ["went to school in"], \
    "stud." : ["studied in"], \
    "stud. med." : ["studied medicine in"], \
    "stud. theol." : ["studied divinity in"], \
    "student" : ["studied in"], \
    "student der rechte" : ["studied law in"], \
    "studien- u. wohnort" : ["studied and lived in"], \
    "studien- u.wohnort" : ["studied and lived in"], \
    "studien- und promotionsort" : ["studied and did doctorate in"], \
    "studien- und wohnort" : ["studied and lived in"], \
    "studienort" : ["studied in"], \
    "studienort und promotion" : ["studied and did doctorate in"], \
    "studienort, wohnort" : ["studied and lived in"], \
    "studium" : ["studied in"], \
    "studium und promotion" : ["studied and did doctorate in"], \
    "studiumsort" : ["studied in"], \
    "superintendent" : ["superintendent in"], \
    "taufe" : ["baptised in"], \
    "taufort" : ["baptised in"], \
    "volksschullehrer" : ["teacher in"], \
    "wohnort" : ["lived in"]
    }
    
    relation_prefix = ""
    relation_new = ""
    relation_comments = ""
    if relation_original:
        for old, new in encoding_list.items():
            relation_original = relation_original.replace(old, new)    
        print("commentary on relation that is to be parsed")
        print(relation_original)
        relation = relation_original.lower() #I need the original relation later
        for old, new in connection_location_alternative1.items():
            relation = relation.replace(old, new)
            print("relation change 1: " + relation)
        for term in connection_location_alternative2:
            relation = relation.replace(term, "other ")
            print("relation change 2 "+ relation)
        for old, new in connection_location_alternative3.items():
            if relation.startswith(old): # This means that there is a composite phrase, such giving e.g. an alternative birth place. In this case, the phrase is standardised, and it is moved to the comment field. 
                # The relation, by contrast, will be shown through the standard relation type
                print("The phrase "+ old + "was found at the start of " + relation + "and will be replaced with " + new)
                string_length = 0-(len(relation) - len(old))
                relation_comments = new + relation_original[string_length:] # Thus, the new relational term is added to the comment in its original capitalisation
                print("newly identified comments to relation")
                print(relation_comments)
                relation = ""
        for old, new in connection_location_doubtful.items(): # in this case, the relation is taken from the relation type, and a prefix (e.g., "supposedly") is added to it
            if old in relation:
                relation = relation.replace(old, new)
                relation_prefix = relation + " "
                relation = ""
        if relation[:5] == "auch ": # this means that the location given here has not only the main type but also an addition type
            print("relation starts with 'auch'")
            if relation_type == "ortg":
                if relation == "auch sterbeort":
                    relation_new = "born and died in"                  
                elif relation == "auch studien- u. wohnort" or relation == "auch studien- und wohnort":
                    relation_new = "born, studied, and lived in"
                elif relation == "auch studienort": 
                    relation_new =  "born and studied in"
                elif relation == "auch wohnort":
                    relation_new = "born and lived in"
            elif relation_type == "ortw":
                if relation == "auch sterbeort":
                    relation_new = "active and died in"
                elif relation == "auch studienort":
                    relation_new = "studied and active in"
            elif relation_type == "orts":
                if relation == "auch studienort":
                    relation_new = "studied and died in"
        else:
            if relation in gnd_person_place_relations:
                relation_new = gnd_person_place_relations[relation][0]
            elif relation_comments == "":
                relation_comments = relation_original # This is different from persons - I put the non-standard text strictly into a comments field
    if relation_new == "":
        if relation_type == "ortg":
            relation_new = "born in"
        elif relation_type == "orts":
            relation_new = "died in"
        elif relation_type == "ortw":
            relation_new = "active in"
        elif relation_type == "rela":
            relation_new = "related to"
    if relation_prefix:
        relation_new = relation_prefix + relation_new
    #print("results of module person_place_relation:")
    #print("type of relation: ")
    #print(relation_new)
    #print("comments: " + relation_comments)
    

    return(relation_new, relation_comments)
    
  

    """

    with comments:
    Abt (years)
    Abt years
    """


def gnd_org_person_relation(relation_original, sex, relation_type):
    # I have in this list different encodings of the ü, maybe that helps
    gnd_org_person_relations = { \
        "architekt" : ["architect was"], \
        "begründer" : ["founded by"], \
        "besitzer" : ["owned by"], \
        "chorleiter" : ["choir master was"], \
        "director" : ["director was"], \
        "dirigent" : ["conductor was"], \
        "drucker" : ["printer was"], \
        "eigentümer" : ["owned by"], \
        "eigentümer?" : ["possibly owned by"], \
        "eigentümerin" : ["owned by"], \
        "faktor" : ["head of workshop ('faktor') was"], \
        "firmenbegründer" : ["founded by"], \
        "firmengründer" : ["founded by"], \
        "firmeninhaber" : ["owned by"], \
        "früherer eigentümer" : ["formerly owned by"], \
        "geschäftsführer" : ["chief clerk was"], \
        "geschäftsführerin" : ["chief clerk was"], \
        "gesellschafter" : ["partner was"], \
        "gründer" : ["founded by"], \
        "gründer der offizin" : ["founded by"], \
        "inhaber" : ["owned by"], \
        "inhaberin" : ["owned by"], \
        "leiter" : ["director was"], \
        "leiterin" : ["director was"], \
        "leitung" : ["director was"], \
        "mitbegründer" : ["co-founded by"], \
        "miteigentümer" : ["co-owned by"], \
        "mitglied" : ["member was"], \
        "mitgründer" : ["co-founded by"], \
        "mitinhaber" : ["co-owned by"], \
        "mitinhaberin" : ["co-owned by"], \
        "nachfolger" : ["predecessor of"], \
        "namensgeber" : ["named after"], \
        "namensgeberin" : ["named after"], \
        "präsident" : ["president was"], \
        "president" : ["president was"], \
        "späterer eigentümer" : ["later owned by"], \
        "teilhaber" : ["partner was"], \
        "verlagsleiter" : ["owned by"], \
        "verleger" : ["owned by"], \
        "vorbesitzer" : ["formerly owned by"], \
        "vorgänger" : ["successor of"], \
        "vorsitzender" : ["chairman was"]   
    }
    relation = ""
    relation_new = ""
    relation_comment = ""
    if relation_original:
        for old, new in encoding_list.items():
            relation_original = relation_original.replace(old, new)    
        relation = relation_original.lower()
    
    if relation in gnd_org_person_relations:
        relation_list = gnd_org_person_relations[relation]
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
        relation_comment = relation_original
        match relation_type:
            case "arch":
                relation_new = "architect was"
            case "befr":
                relation_new = "formerly owned by"
            case "besi":
                relation_new = "owned by"
            case "bete":
                relation_new = "part of" # this is awkward, but I think that 'bete' can be both partner and someone who participated
            case "bezb" : 
                relation_new = "professional relation to"
            case "feie" :
                relation_new = "named after"
            case "grue" : 
                relation_new = "founded by"
            case "kuen" : 
                relation_new = "artist at"
            case "mitg":
                relation_new = "member was"
            case "musi":
                relation_new = "musician was"
            case "rela": 
                relation_new = "related to"
            case "saml": 
                relation_new = "collector was"
            case "spon":
                if sex == "male":
                    relation_new = "benefactor was"
                elif sex == "emale":
                    relation_new = "benefactress was"
                elif sex == "":
                    relation_new = "benefctor or benefactress was"
            case "stif":
                relation_new = "endowed by"
            case "them":
                relation_new = "is about"
            case "vbal":
                relation_new = "related to"
    return(relation_new, relation_comment)


def gnd_org_org_relation(relation_original, sex, relation_type):
    gnd_org_org_relations = {
        "anfangs" : ["originally part of"], \
        "aufgegangen in" : ["later incorporated into"], \
        "ausgegangen von" : ["split from"], \
        "daraus hervorgegangen" : ["successor of"], \
        "darin aufgegangen" : ["later incorporated into"], \
        "eingegangen in" : ["later incorporated into"], \
        "früher siehe" : ["formerly"], \
        "früher, siehe" : ["formerly"], \
        "hervorgegangen aus" : ["successor of"], \
        "indirekter nachfolger" : ["indirect predecessor of"], \
        "indirekter vorgänger" : ["indirect successor of"], \
        "inkorporiert" : ["parish incorporated into"], \
        "inkorporierte pfarre" : ["parish incorporated into"], \
        "später" : ["later"], \
        "später siehe" : ["later"], \
        "später, siehe" : ["later"], \
        "stiftspfarre" : ["parish incorporated into"], \
        "träger" : ["parent institution was"]      
      }
    relation = ""
    relation_new = ""
    relation_comment = ""
    print("ßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßß")
    print("determining an org > org relation")
    print("original relation: ")
    print(relation_original)
    print(relation_type)
    if relation_original:
        for old, new in encoding_list.items():
            relation_original = relation_original.replace(old, new)    
        relation = relation_original.lower()

    if relation == "früher": # this is apparently the only instance of the type and the comment forming a joint meaning
        if relation_type == "adue":
            relation_new = "formerly part of"
        elif relation_type == "rela":
            relation_new = "formerly"
    elif relation in gnd_org_org_relations:
        relation_new = gnd_org_org_relations[relation][0]
    else:
        relation_comment = relation
        match relation_type:
            case "adue":
                relation_new = "part of"
            case "affi":
                relation_new = "affiliated to"
            case "besi": 
                relation_new = "owned by"
            case "bete":
                relation_new = "partner of"
            case "grue":
                relation_new = "founded by"
            case "mitg":
                relation_new = "member of"
            case "nach":
                relation_new = "predecessor of"
            case "nazw":
                relation_new = "temporary name was"
            case "obpa":
                relation_new = "part of"
            case "rela":
                relation_new = "related to"
            case "spon":
                if sex == "male":
                    relation_new = "benefactor was"
                elif sex == "emale":
                    relation_new = "benefactress was"
                elif sex == "":
                    relation_new = "benefctor or benefactress was"
            case "stif":
                relation_new = "endowed by"
            case "them":
                relation_new = "is about"
            case "vbal":
                relation_new = "related to"
            case "vorg":
                relation_new = "successor to" 
    print("created new connection for org > org: ")
    print(relation_new)
    print(relation_comment)        
    return (relation_new, relation_comment)

def gnd_org_place_relation(relation_original, sex, relation_type):
    org_place_relations = {
        "anfangs" : ["originally in"], \
        "betriebsgewässer" : ["used river"], \
        "früherer ortssitz" : ["formerly in"], \
        "früherer sitz" : ["formerly in"], \
        "gründungsort" : ["founded in"], \
        "hauptsitz" : ["main seat was"], \
        "nebensitz" : ["secondary seat was"], \
        "sitz" : ["in"], \
        "sitz früher" : ["formerly in"], \
        "später" : ["later in"], \
        "späterer sitz" : ["later in"], \
        "standort" : ["in"], \
        "ursprünglicher sitz" : ["originally in"], \
        "vermutlicher sitz" : ["possibly in"], \
        "zeitweilig" : ["temporarily in"], 
        "zeitweise" : ["temporarily in"]   
    }
    relation = ""
    relation_new = ""
    relation_comment = ""
    if relation_original:
        for old, new in encoding_list.items():
            relation_original = relation_original.replace(old, new)    
        relation = relation_original.lower
    if relation == "früher":
        if relation_type == "orta":
            relation_new = "formerly in"
        elif relation_type == "geow":
            relation_new = "formerly responsible for"
    elif relation in org_place_relations:
        relation_new = org_place_relations[relation][0]
    else:
        relation_comment = relation_original
        "relation comment was not in list, now matching relation type"
        match relation_type:
            case "adue":
                relation_new = "part of"
            case "geoa": # I am not really sure what this means
                relation_new = "in"
            case "geow": # I think that most of these would be deleted later manually
                relation_new = "serves location"
            case "nach": # I have no clue why this is so common with place-names
                relation_new = "predecessor of"
            case "orta"|"ortb"|"ortg"|"orts"|"ortv": 
                relation_new = "in"
            case "rela"|"vbal":
                relation_new = "related to"
            case "them":
                relation_new = "is about"
            case "vorg":
                relation_new = "successor of"
        
    return(relation_new, relation_comment)


def gnd_place_person_relation(relation_original, sex, relation_type):
    place_person_relations = {
        "ausführung" : ["building executed by"], \
        "entwurf" : ["building designed by"], \
    }
    relation = ""
    relation_new = ""
    relation_comment = ""
    if relation_original:
        for old, new in encoding_list.items():
            relation_original = relation_original.replace(old, new)    
        relation = relation_original.lower
#        if relation == "früher":
#            if relation_type == "orta":
#                relation_new = "formerly in"
#            elif relation_type == "geow":
#                relation_new = "formerly responsible for"
    if relation in place_person_relations:
        relation_new = place_person_relations[relation][0]
    else:
        relation_comment = relation_original
        match relation_type:
            case "arch":
                relation_new = "architect was"
            case "bauh":
                relation_new = "built for"
            case "befr":
                relation_new = "formerly owned by"
            case "besi":
                relation_new = "owned by"
            case "bete":
                relation_new = "part of" # this is awkward, but I think that 'bete' can be both partner and someone who participated
            case "bilh":
                relation_new = "sculptor was" # I wonder if I shouldn't kick that out later since I do artists separately
            case "feie":
                relation_new = "built in honour of"
            case "kuen":
                relation_new = "artist was"
            case "obpa":
                relation_new = "part of"
            case "rela":
                relation_new = "related to"
            case "stif":
                relation_new = "endowed by"

    return(relation_new, relation_comment)


def gnd_place_org_relation(relation_original, sex, relation_type):
# Here, there are so few terms that it does not make sense to parse them, hence I will only parse the main abbreviations
    relation = ""
    relation_new = ""
    relation_comment = ""
    if relation_original:
        for old, new in encoding_list.items():
            relation_original = relation_original.replace(old, new)    

        relation_comment = relation_original
    match relation_type:
        case "arch":
            relation_new = "architect was"
        case "bauh":
            relation_new = "built for"
        case "befr":
            relation_new = "formerly owned by"
        case "besi":
            relation_new = "owned by"
        case "bete":
            relation_new = "part of" # this is awkward, but I think that 'bete' can be both partner and someone who participated
        case "bilh":
            relation_new = "sculptor was" # I wonder if I shouldn't kick that out later since I do artists separately
        case "kuen":
            relation_new = "artist was"
        case "rela":
            relation_new = "related to"
        case "stif":
            relation_new = "endowed by"

    return(relation_new, relation_comment)


def gnd_place_place_relation(relation_original, sex, relation_type):
    place_place_relations = {
        "aufgegangen in" : ["later incorporated into"], \
        "darin aufgegangen" : ["later incorporated into"], \
        "hauptort" : ["chief town of"], \
        "hauptstadt" : ["capital of"]
    }
    relation = ""
    relation_new = ""
    relation_comment = ""
    if relation_original:
        for old, new in encoding_list.items():
            relation_original = relation_original.replace(old, new)    
        relation = relation_original.lower
    if relation in place_place_relations:
        relation_new = place_place_relations[relation][0]
    else:
        relation_comment = relation_original
        match relation_type:
            case "adue":
                relation_new = "part of"
            case "geoa": # I am not really sure what this means
                relation_new = "in"
            case "geow": # I think that most of these would be deleted later manually
                relation_new = "serves location"
            case "nach": # I have no clue why this is so common with place-names
                relation_new = "formerly called"
            case "nazw":
                relation_new = "temporary name was"
            case "obpa":
                relation_new = "part of"
            case "orta"|"ortb"|"ortg"|"orts"|"ortv": 
                relation_new = "in"
            case "punk":
                relation_new = "begins or ends in"
            case "rela"|"vbal":
                relation_new = "related to"
            case "vorg":
                relation_new = "later named"


    return(relation_new, relation_comment)

    


def relation_correspondence(relation, sex):
# This function produces the corresponding term of relationship to a given term. 
# Up to now, it only covers relationships between persons - relationships between persons and organisations are to be added
# The function takes a relationship phrase from one person record ('A') and the sex from another person record ('B') and formulates a relationship phrase for 'B'

    corresponding_relationships = { \
    "abbess of" : ["abbess was"], \
    "abbot of" : ["abbot was"], \
    "acquaintance of" : ["acquaintance of"], \
    "active and died in" : ["place of activity and death of"], \
    "active in" : ["place of activity of"], \
    "actor at" : ["actor here was"], \
    "actress at" : ["actress here was"], \
    "administrator of" : ["administrated by"], \
    "adopted daughter of" : ["adoptive father of", "adoptive mother of", "adoptive father or mother of"], \
    "adopted son of" : ["adoptive father of", "adoptive mother of", "adoptive father or mother of"], \
    "adopted son or daughter of" : ["adoptive father of", "adoptive mother of", "adoptive father or mother of"], \
    "adoptive father of" : ["adopted son of", "adopted daughter of", "adopted son or daughter of"], \
    "adoptive father or mother of" : ["adopted son of", "adopted daughter of", "adopted son or daughter of"], \
    "adoptive mother of" : ["adopted son of", "adopted daughter of", "adopted son or daughter of"], \
    "advisor of" : ["advised by"], \
    "affiliated to" : ["affiliated was"], \
    "ally of" : ["ally of"], \
    "ancestor of" : ["descendant of"], \
    "appointed by" : ["appointee of"], \
    "appointee of" : ["appointed by"], \
    "apprentice at" : ["apprentice was"], \
    "apprentice of" : ["apprentice was"], \
    "apprentice was" : ["apprentice of"], \
    "apprentice and assistant at" : ["apprentice and assistant was"], \
    "archbishop of" : ["archbishop was"], \
    "architect in" : ["architect here was"], \
    "architect was" : ["architect of"], \
    "artist of" : ["artist was"], \
    "artist was" : ["artist of"], \
    "assistant at" : ["assistant was"], \
    "assistant of" : ["assisted by"], \
    "assisted by" : ["assistant of"], \
    "assistant preacher at" : ["assistant preacher was"], \
    "assistant preacher in" : ["assistant preacher here was"], \
    "associate of" : ["associate of"], \
    "associated with" : ["associated with"], \
    "at paper mill in" : ["worked at paper mill here"], \
    "aunt of" : ["nephew of", "niece of", "nephew or niece of"], \
    "baptised in" : ["place of baptism of"], \
    "benefactor of" : ["benefactor was"], \
    "benefactress of" : ["benefactress was"], \
    "benefactor was" : ["benefactor of"], \
    "benefactress was" : ["benefactress of"], \
    "biography by" : ["biographer of"], \
    "bishop in" : ["bishop here was"], \
    "bishop of" : ["bishop was"], 
    "born and died in" : ["place of birth and death of"], \
    "born, studied and lived in" : ["place of birth, residence, and death of"], \
    "born and lived in" : ["place of birth and residence of"], \
    "born and studied in" : ["place of birth and studies of"], \
    "born in" : ["place of birth of"], \
    "bride of" : ["bridegroom of"], \
    "bridegroom of" : ["bride of"], \
    "brother of" : ["brother of", "sister of", "brother or sister of"], \
    "brother or sister of" : ["brother of", "sister of", "brother or sister of"], \
    "brother- or sister-in-law of" : ["brother-in-law of", "sister-in-law of", "brother- or sister-in-law of"], \
    "brother-in-law of" : ["brother-in-law of", "sister-in-law of", "brother- or sister-in-law of"], \
    "built for" : ["had built"], \
    "built in honour of" : ["building in honour"], \
    "buried in" : ["place of burial of"], \
    "came from" : ["place of origin of"], \
    "cantor at" : ["cantor was"], \
    "capital of" : ["capital was"], \
    "chairman of" : ["chairman was"],
    "chairman was"  : ["chairman of"], \
    "chairwoman of" : ["chairwoman was"], \
    "chancellor of" : ["chancellor was"], \
    "chief clerk of" : ["chief clerk was"], \
    "chief clerk was" : ["chief clerk of"], \
    "chief town of" : ["chief town was"], \
    "childhood spent in" : ["childhood home of"], \
    "choir master of" : ["choir master was"], \
    "choir master was" : ["choir master of"], \
    "chorister at" : ["chorister was"], \
    "classmate of" : ["classmate of"], \
    "client of" : ["client was"], \
    "client was" : ["client of"], \
    "collector for" : ["collector was"], \
    "collector was" : ["collector for"], \
    "close friend of" : ["close friend of"], \
    "co-founder of" : ["co-founded by"], \
    "co-foundress of" : ["co-founded by"], \
    "co-founded by" : ["co-counder of", "co-foundress of", "co-founder or co-foundress of"], \
    "collaborated with" : ["collaborated with"], \
    "collaborator at" : ["collaborated with"], \
    "colleague of" : ["colleague of"], \
    "commander of" : ["commanded by"], \
    "confessor of" : ["confessor was"], \
    "confessor was" : ["confessor of"], \
    "conductor was" : ["conductor of"], \
    "consort of" : ["consort was"], \
    "consort was" : ["consort of"], \
    "co-owner of" : ["co-owned by"], \
    "co-owned by" : ["co-owner of"], \
    "corresponded with" : ["corresponded with"], \
    "counselled by" : ["counsellor was"], \
    "court artist to" : ["court artist was"], \
    "court artist was" : ["court artist to"], \
    "cousin of" : ["cousin of"], \
    "crowned" : ["crowned by"], \
    "crowned by" : ["crowned"], \
    "customer was" : ["customer of"], \
    "dancer at" : ["dancer was"], \
    "daughter of" : ["father of", "mother of", "father or mother of"], \
    "daughter-in-law of" : ["father-in-law of", "mother-in-law of", "father- or mother-in-law of"], \
    "daughter-in-law of (her fifth marriage)" : ["father-in-law of (her fifth marriage)", "mother-in-law of (her fifth marriage)", "father- or mother-in-law of (her fifth marriage)"], \
    "daughter-in-law of (her first marriage)" : ["father-in-law of (her first marriage)", "mother-in-law of (her first marriage)", "father- or mother-in-law of (her first marriage)"], \
    "daughter-in-law of (her fourth marriage)" : ["father-in-law of (her fourth marriage)", "mother-in-law of (her fourth marriage)", "father- or mother-in-law of (her fourth marriage)"], \
    "daughter-in-law of (her second marriage)" : ["father-in-law of (her second marriage)", "mother-in-law of (her second marriage)", "father- or mother-in-law of (her second marriage)"], \
    "daughter-in-law of (her third marriage)" : ["father-in-law of (her third marriage)", "mother-in-law of (her third marriage)", "father- or mother-in-law of (her third marriage)"], \
    "dean of" : ["dean was"], \
    "deputy chaimrman of" : ["deputy chairman was"], \
    "deputy chairwoman of" : ["deputy chairwoman was"], \
    "deputy director of" : ["deputy director was"], \
    "descendant of" : ["ancestor of"], \
    "did doctorate and habilitation in" : ["place of doctorate and habilitation of"], \
    "did doctorate in" : ["place of doctorate of"], \
    "died in" : ["place of death of"], \
    "director of" : ["director was"], \
    "director was" : ["director of"], \
    "distinguished from" : ["distinguished from"], \
    "divinity student at" : ["divinity student was"], \
    "doctoral student at" : ["doctoral student was"], \
    "doctorate at" : ["doctoral student was"], \
    "domestic partner of" : ["domestic partner of"], \
    "donor of" : ["donor was"], \
    "donor was" : ["donor of"], \
    "drawing teacher was" : ["drawing teacher of"], \
    "editor of" : ["editor was"], \
    "employee of" : ["employee was"], \
    "employee was" : ["employee of"], \
    "endowed by" : ["endowed"], \
    "executed in" : ["place of execution of"], \
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
    "fellow of" : ["fellow was"], \
    "fellow pupil of " : ["fellow pupil of"], \
    "fellow student of" : ["fellow student of"], \
    "fiancé of" : ["fiancée of"], \
    "fiancée of" : ["fiancé of"], \
    "former husband of" : ["former wife of"], \
    "former owner of" : ["formerly owned by"], \
    "former wife of" : ["former husband of"], \
    "formerly" : ["later"], \
    "formerly in" : ["former location of"], \
    "formerly identified with" : ["formerly identified with"], \
    "formerly owned by" : ["former owner of"], \
    "foster-child of" : ["foster-father of", "foster-mother of", "foster-parent of"], \
    "foster-daughter of" : ["foster-father of", "foster-mother of", "foster-parent of"], \
    "foster-father of" : ["foster-son of", "foster-daughter of", "foster-child of"], \
    "foster-mother of" : ["foster-son of", "foster-daughter of", "foster-child of"], \
    "foster-parent of" : ["foster-son of", "foster-daughter of", "foster-child of"], \
    "foster-son of" : ["foster-father of", "foster-mother of", "foster-parent of"], \
    "founded by" : ["founder of", "foundress of", "founder or foundress of"], \
    "founded in" : ["place of foundation of"], \
    "founder of" : ["founded by"], \
    "founding director of" : ["founding director was"], \
    "founding member of" : ["founding member was"], \
    "foundress of" : ["foundress was"], \
    "friend of" : ["friend of"], \
    "friend of (at school)" : ["friend of (at school)"], \
    "friend of (in youth)" : ["friend of (in youth)"], \
    "full member of" : ["full member was"], \
    "godchild of" : ["godfather of", "godmother of", "godparent of"], \
    "goddaughter of" : ["godfather of", "godmother of", "godparent of"], \
    "godfather of" : ["godson of", "goddaughter of", "godchild of"], \
    "godmother of" : ["godson of", "goddaughter of", "godchild of"], \
    "godparent of" : ["godson of", "goddaughter of", "godchild of"], \
    "godson of" : ["godfather of", "godmother of", "godparent of"], \
    "graduate of" : ["graduate was"], \
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
    "grown up in" : ["youth home of"], \
    "guardian of" : ["ward of"], \
    "habilitation at" : ["habilitation done by"], \
    "habilitation in" : ["place of habilitation of"], \
    "half-brother of" : ["half-brother of", "half-sister of", "half-brother or half-sister of"], \
    "half-brother or half-sister of" : ["half-brother of", "half-sister of", "half-brother or half-sister of"], \
    "half-sister of" : ["half-brother of", "half-sister of", "half-brother or half-sister of"], \
    "head of music at" : ["head of music was"], \
    "head of workshop ('faktor') was" : ["head of workshop ('faktor') for"], \
    "head of workshop ('faktor') of" : ["head of workshop ('faktor) for"], \
    "head of" : ["headed by"], \
    "headmaster of" : ["headmaster was"], \
    "headmistress of" : ["headmistress was"], \
    "home was" : ["home of"], \
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
    "in" : ["location of"], \
    "indirect predecessor of" : ["indirect successor of"], \
    "indirect successor of" : ["indirect predecessor of"], \
    "influenced" : ["influenced by"], \
    "influenced by" : ["influenced"], \
    "is about" : ["subject is"], \
    "judge at" : ["judge was"], \
    "lady-in-waiting was" : ["lady-in-waiting to"], \
    "landlord of" : ["tenant of"], \
    "landowner in" : ["landowner here was"], \
    "later" : ["formerly"], \
    "later in" : ["later location of"], \
    "later incorporated into" : ["later incorporating"], \
    "later owned by" : ["later owner of"], \
    "law student at" : ["law student was"], \
    "leader of" : ["lead by"], \
    "librarian to" : ["librarian was"], \
    "lived chiefly in" : ["main residence of"], \
    "lived in" : ["residence of"], 
    "main seat was" : ["main seat of"], \
    "master of" : ["master was"], \
    "master or mistress of" : ["master of mistress was"], \
    "master or mistress was" : ["master of mistress of"], \
    "master was" : ["master of"], \
    "mayor of" : ["mayor was"], \
    "meaning overlaps with" : ["meaning overlaps with"], \
    "medical student at" : ["medical student was"], \
    "member of" : ["member was"], \
    "member of this family" : ["family of"], \
    "member was" : ["member of"], \
    "mentee of" : ["mentor of"], \
    "minister at" : ["minister was"], \
    "minister in" : ["minister here was"], \
    "mistress of" : ["mistress was"], \
    "mistress was" : ["mistress of"], \
    "monk at" : ["monk was"], \
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
    "mother superior of" : ["mother superior was"], \
    "mother-in-law of" : ["son-in-law of", "daughter-in-law of", "son- or daughter-in-law of"], \
    "murdered by" : ["murderer of"], \
    "murderer of" : ["murdered by"], \
    "musician was" : ["musician at"], \
    "named after" : ["name used by "], \
    "nephew of" : ["uncle of", "aunt of", "uncle or aunt of"], \
    "nephew or niece of" : ["uncle of", "aunt of", "uncle or aunt of"], \
    "niece of" : ["uncle of", "aunt of", "uncle or aunt of"], \
    "older brother of" : ["younger brother of", "younger sister of", "younger brother or sister of"], \
    "older brother or sister of" : ["younger brother of", "younger sister of", "younger brother or sister of"], \
    "older sister of" : ["younger brother of", "younger sister of", "younger brother or sister of"], \
    "opponent of" : ["opponent of"], \
    "originally in" : ["original location of"], \
    "originally part of" : ["originally incorporated in"], \
    "owned by" : ["owner of"], \
    "owner of" : ["owned by"], \
    "parent institution was" : ["child institution was"], \
    "paper maker at" : ["paper maker was"], \
    "parish incorporated into" : ["incorporated parish was"], \
    "papers at" : ["papers kept here"], \
    "part of" : ["part was"], \
    "partner of" : ["partner of"], \
    "partner at" : ["partner was"], \
    "partner was" : ["partner at"], \
    "patron of" : ["patron was"], \
    "patron was" : ["patron of"], \
    "performed with" : ["performed with"], \
    "personal physician was" : ["physician of"], \
    "PhD student of" : ["PhD supervisor of"], \
    "PhD supervisor of" : ["PhD student of"], \
    "physician of" : ["personal physician was"], \
    "possibly active in" : ["possible place of activity of"], 
    "possibly born in" : ["possible place of birth of"], \
    "possibly brother of" : ["possibly brother of", "possibly sister of", "possibly brother of sister of"], \
    "possibly brother or sister of" : ["possibly brother of", "possibly sister of", "possibly brother of sister of"], \
    "possibly cousin of" : ["possibly cousin of"], \
    "possibly daughter of" : ["possibly father of", "possibly mother of", "possibly father or mother of"], \
    "possibly died in" : ["possible place of death of"], \
    "possibly father of" : ["possibly son of", "possibly daughter of", "possibly son or daughter of"], \
    "possibly father or mother of" : ["possibly son of", "possibly daughter of", "possibly son or daughter of"], \
    "possibly grandchild of" : ["possibly grandfather of", "possibly grandmother of", "possibly grandparent of"], \
    "possibly granddaughter of" : ["possibly grandfather of", "possibly grandmother of", "possibly grandparent of"], \
    "possibly grandson of" : ["possibly grandfather of", "possibly grandmother of", "possibly grandparent of"], \
    "possibly husband of" : ["possibly wife of"], \
    "possibly identified with" : ["possibly identified with"], \
    "possibly in" : ["possibly location of"], \
    "possibly member of this family" : ["possibly family of"], \
    "possibly mother of" : ["possibly son of", "possibly daughter of", "possibly son or daughter of"], \
    "possibly nephew of" : ["possibly uncle of", "possibly aunt of", "possibly uncle or aunt of"], \
    "possibly nephew or niece of" : ["possibly uncle of", "possibly aunt of", "possibly uncle or aunt of"], \
    "possibly niece of" : ["possibly uncle of", "possibly aunt of", "possibly uncle or aunt of"], \
    "possibly owned by" : ["possible owner of"], \
    "possibly related to" : ["possibly related to"], \
    "possibly sister of" : ["possibly brother of", "possibly sister of", "possibly brother of sister of"], \
    "possibly son of" : ["possibly father of", "possibly mother of", "possibly father or mother of"], \
    "possibly son or daughter of" : ["possibly father of", "possibly mother of", "possibly father or mother of"], \
    "possibly wife of" : ["possibly husband of"], \
    "physician in" : ["physician here was"], \
    "praeses of" : ["praeses was"], \
    "predecessor of" : ["successor of"], \
    "prefect of" : ["prefect was"], \
    "president of" : ["president was"], \
    "president was" : ["president of"], \
    "principal of" : ["principal was"], \
    "printer was" : ["printer to"], \
    "prior of" : ["prior was"], \
    "prioress of" : ["prioress was"], \
    "prisoner at" : ["prisoner was"], \
    "private tutor in" : ["private tutor here was"], \
    "professor at" : ["professor was"], \
    "prorector (pro vice-chancellor) at" : ["prorector (pro vice-chancellor was)"], \
    "provincial of" : ["provincial was"], \
    "publications in" : ["place of publications of"], \
    "pupil at" : ["pupil was"], \
    "rector (vice-chancellor) at" : ["rector (vice-chancellor) was"], \
    "rector at" : ["rector was"], \
    "rector in" : ["rector here was"], \
    "related to" : ["related to"], \
    "relative by marriage of" : ["relative by marriage of"], \
    "religious superior at" : ["religious superior was"], \
    "retired to" : ["place of retirement of"], \
    "romantic partner of" : ["romantic partner of"], \
    "romantic partner of (in youth)]" : ["romantic partner of"], \
    "second cousin of" : ["second cousin of"], \
    "secondary seat was" : ["secondary seat of"], \
    "secretary was" : ["secretary of"], \
    "sculptor was" : ["sculptor of"], \
    "senior teacher at" : ["senior teacher was"], \
    "serves location" : ["location served by"], \
    "singer at" : ["singer was"], \
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
    "split from" : ["formerly part was"], \
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
    "student at" : ["student was"], \
    "student of" : ["student was"], \
    "student was" : ["student of"], \
    "student of economy at" : ["student of economy was"], \
    "student of philosophy at" : ["student of philosophy was"], \
    "studied and did doctorate in" : ["place of studies and doctorate of"], \
    "studied and active in" : ["plae of studies and activity of"], \
    "studied and lived in" : ["place of studies and residence of"], \
    "studied divinity in" : ["place of divinity studies of"], \
    "studied in" : ["place of studies of"], \
    "studied law in" : ["place of law studies of"], \
    "studied medicine in" : ["place of medical studies of"], \
    "sub-prior at" : ["sub-prior was"], \
    "subordinate to (military)" : ["military superior of"], \
    "succeeded by (organisation)" : ["preceded by (person)"], \
    "successor of" : ["predecessor of"], \
    "superintendent at" : ["superintendent was"], \
    "superintendent in" : ["superintendent here was"], \
    "superior of" : ["worked under"], \
    "supposecly active in" : ["supposed plce of activity of"], \
    "supposedly born in" : ["suposed place of birth of"], \
    "supposedly died in" : ["supposed place of death of"], \
    "teacher of" : ["teacher was"], \
    "teacher in" : ["teacher here was"], \
    "teacher at" : ["teacher was"], \
    "temporary name was" : ["temporary name of"], \
    "temporarily in" : ["temporary locatin of"], \
    "to this family belonged" : ["family of"], \
    "trained at" : ["trainee was"], \
    "trained in" : ["place of training of"], \
    "trained or studied in" : ["place of training or studies of"], \
    "tutor was" : ["tutor of"], \
    "twin brother of" : ["twin brother of", "twin sister of", "twin brother or twin sister of"], \
    "twin brother or sister of" : ["twin brother of", "twin sister of", "twin brother or twin sister of"], \
    "twin sister of" : ["twin brother of", "twin sister of", "twin brother or twin sister of"], \
    "uncle of" : ["nephew of", "niece of", "nephew or niece of"], \
    "uncle or aunt of" : ["nephew of", "niece of", "nephew or niece of"], \
    "used river" : ["river used for"], \
    "user of" : ["user was"], \
    "friend of (at university)" : ["friend of (at university)"], \
    "vasall of" : ["liege lord of"], \
    "vice-chancellor of" : ["vice-chancellor was"], \
    "vice-president of" : ["vice-president was"], \
    "victim was" : ["victim of"], \
    "ward of" : ["guardian of"], \
    "went to school in" : ["place of school of"], \
    "wife of" : ["husband of"], \
    "wife of (her fifth marriage)" : ["fifth husband of"], \
    "wife of (her first marriage)" : ["first husband of"], \
    "wife of (her fourth marriage)" : ["fourth husband of"], \
    "wife of (her second marriage)" : ["second husband of"], \
    "wife of (her third marriage)" : ["third husband of"], \
    "worked under" : ["superior of"], \
    "worked in" : ["place of work of"], \
    "worked with" : ["worked with"], \
    "worker was" : ["worked for"], \
    "younger brother of" : ["older brother of", "older sister of", "older brother or sister of"], \
    "younger brother or sister of" : ["older brother of", "older sister of", "older brother or sister of"], \
    "younger sister of" : ["older brother of", "older sister of", "older brother or sister of"], \
    }

    if relation in corresponding_relationships:
        corresponding_relation_list = corresponding_relationships[relation]
        if len(corresponding_relation_list) == 1:
            corresponding_relation = corresponding_relation_list[0]
        else:
            if sex == "male":
                corresponding_relation = corresponding_relation_list[0]
            elif sex == "female": 
                corresponding_relation = corresponding_relation_list[1]
            else:
                corresponding_relation = corresponding_relation_list[2]
    else:
        corresponding_relation = "counterpart to " + relation
        print("yyyyyyyyyyyyyyyyyyyyyyyyyyyyy")
        print("person_relations: corresponding relation")
        print(corresponding_relation)
    return(corresponding_relation)
















































