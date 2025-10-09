Iconobase - Classes

# Abbreviations

r: repeatable
nr: non-repeatable
o: obligatory

"o" means that the record cannot be saved at all of this field is missing or (for Boolean fields) that they have a default value. 
There will be more criteria for validating records that are ready to be made public. 


# Ancillary classes

In the following, these classes are merely listed like attributes of other classes. I am not sure if they would be connected directly or also with an Edge. With a potential exception in ExternalReference, the Edge would contain no information apart from the IDs of both elements, and the obligatory fields relationA and relationB. 

## Date

This class is used for all indications of dates - all references to "date" as a format refer to it and not to an out-of-the-box date function. 

![Create](./class_diagrams/Date.png)

The field 'active' would be set to 'true' if the start and end dates for a person do not denote the lifespan but rather activity (or attestation in archival records etc.). It is only needed for artists: if an Artwork has no date, it would be dated according to the date of the artist - if the artist's dates are lifespan dates it wold be somthing like start date + 20 years until end date; if they are dates of activity, it would be start date until end date. 

Date_string is the field that is displayed, whilst date_start and date_end are used for filtering. 

All three fields are to be stored, to allow for some flexibility (e.g., if we have an artwork by someone who died in 1599, one might still give as date_string 'late 16th century' but set the date_end to the artist's death). 

date_start and date_end could be in any format for expressing dates (e.g., in some datetime format). However, I had great difficulties with dates BC using Pymongo, and hence simple tuples of integers for year, month, and day seemed to be the savest option. Perhaps this might be easier with Beanie. 

In most cases, the timespan has a start and an end, but there may be also strings with an open end in connecitons between Artworks/Manuscripts and Collection (e.g., "since 1821"). 

If one has an Edge between the Date and the object it is connected to, the relations would be something like "has date" and "date of". 


## ExternalReference

This classe is used for references to external authority files (e.g. GND, GW, Getty ULAN). 

![Create](./class_diagrams/ExternalReference.png)

In theory, one could omit the attribute 'URI' and create the URI every time out of a base URI stored somewhere for this type of authority file and the ID, but I am not sure if it is worth it (although it might simplify changes, should the URI syntax for a specific resource change). The other attributes are the name of the resource (for display) and the ID of this object within the resource. 

The attribute 'number' is used for displaying all ExternalReference instances connected to a specific object into a desired order - currently, I only see a reason why someone might want to do so with bibliographical references for books (many early 16th-century books were once regarded as incunables and have hence a GW record - however, the record normally only says something like 'not an incunable, see VD16 instead', and hence the VD16 record would be most useful and should be put first). 

If one has an Edge between the ExternalReference and the object it is connected to, the relations would be something like 'external reference' and "external reference for". In this case, one could put make the number an attribute of the Edge, as is the case with other such numbers. 



## Bibliography

This class will be used for bibliographical references in modern research literature, not for historical books. 
ToDo!

# Authority records

## Person

This record is for any person (Artists, Authors, etc., Depicted figures), hence the great number of possible connections. 

![Create](./class_diagrams/Person.png)

**Attributes:**

- type: 
  - There must be at least a basic type (probably one of the following: "Author", "Printer", "Artist", "Depicted Person").
  - If the type is "Depicted Person", there must be at least one of the following: "Biblical Figure", "Saint", "Historical Figure", "Mythological Figure", "Literary Figure"
  - Possible, there are further necessary types, e.g. for "Saint" "Martyr", "Confessor", "Virgin" etc., or for Mythological Figure "Graeco-Roman", "Egyptian" etc.
  - One Person can have a number of types on every level, and every type determines which attributes and connections will be needed. 


**Edge between Person and Heading:**

This could be used, for instance, for indicating professions. 


**Edge between Person and Text:**

Here, two very different relations are possible. firstly the author of / author of a text as given in the diagram, but also:
Text mentioning figure / mentioned in (for literary figures, e.g. to connect Gulliver to Gulliver's Travels)


**Edge between Person and Book:**

This means the author in the biblical record of a concrete edition of a book, not the author of a text as used in iconographical descriptions. 
In addition to author of / author was, several other relations are possible:
editor of / editor was
printer of / printer was
publisher of / publisher was


**Edge between Person and MakingProcess:**

Note the cardinality, every MakingProcess contains only one Person.

**Edge between Person and Family :**
I am not sure how to use this (it would be helpful for coats-of-arms, but it is a rather vague concept, e.g., do people also belong to the family of the in-laws? what is a family, and what is a branch of a family?). 

**Edge between Person and Office (EdgePersonOffice):**

Offices held by the person. In case of several Offices one would probably sort them chronologically in the UI (or use numberA and mumberB in the Edge)


**Edge between Person and Organisation (EdgePersonOrganisation):**

In addition to has member / member of, many other relations are possible, e.g.:
founded by / founder of
has director / director of (unless 'Office is used for that')
has benefactor / benefactor of
etc. 


**Edge between Person and Place (EdgePersonPlace):**

In addition to born in / place of birth, several other relationships are possible, e.g.:
died in / place of death
active in / place of activity
buried in / place of burial
The date field would be needed for "active in" or similar relationships. 


**Edge between Person and Person (EdgePersonPerson):**

In addition to father of / son of, a great number of other family relations are possible, e.g.
husband of / wife of
etc. etc.

**Edge between Person and Iconography (EdgePersonIconography)**

In addition to portrayed in / portrayed person, other relationships are possible - they depend on the type of iconography selected, e.g.
portrayed in / portrayed person (for portraits)
shown in / acting person (for narrative scenes)
allegory of / connected allegory (for allegorical images)
emblem about / connected emblem (for emblems)
arms of / arms (for heraldry)

The attributes given on the Edge are the standard attributes for everything connected to iconography. Since they go in directions, one could also write them onto the arrows. 

The attribute copy_variants determines if any variants (i.e., Criteria and Options) linked to the Person record should be made available in this Iconography record. 


**Edge between Person and Option (EdgePersonOption)**

This works similar to EdgePersonIconography, but it connects not to the 'whole' iconography but only to a variant (e.g., for an additional figure)

**Edge between Person and Criterion**

It is possible to save Criteria not only with Iconographies, but also with Persons (and other records connected to Iconographies, though it will be only really current for Persons and Personifications). If on Iconography is connectedwith this Person, one could link (all or some) criteria of the Person to the specific Iconography. This procedure has been forgotten when I described the creation of Iconographic records in README. !!!!

**Edge between Person and Cycle (EdgePersonCycle)**

This Edge works similar to the Edge between Person and Iconography, but in this case the Person would be the common 'Theme' of a cycle (e.g., "Labours of Hercules"). I have to think more about how to do that (especially, if there should be a node between the Cycle and the Person)


**Additional criteria for creating links:**

- Only Persons with the type "Author" or "Literary Figure" can be linked to Texts. 
- Only Persons with the type "Author" or "Printer" can be linked to Books
- Only Persons with the type "Artist" or "Printer" can be linked to Making Processes ("Printer" only to specific Making Processes). 
- Only Persons with the type "Depicted Person" can be linked to Iconography, Option, Criterion, and Cycle 
 

**Additional criteria for validation for saving record:**

- none
  

**Additional criteria for validation for publishing record:**

- A Person with the type "Historical Person" needs a Date and furthermore must be linked to either an Office or a Profession (Heading) plus a Place. 
- A Person with the type "Depicted Person" needs a sex (can also be unknown)
- A Person with the type "Literary Person" needs a Text. 
- A Person needs to be linked to a Book, a Text (as author etc.), a Making Process, or an Iconography (or Option or Cycle). 



## Family

This class is primarily an addition to the class Person. Its main purpose is to be able to search for all images connected with members of a specific family (largely noble families with many portrayed members), even if they are not all linked together by Person-Person relations. One can furthermore connect it to iconographies that are specific for whole families (typically heraldry) or for image cycles whose topic is members of a certain family. It would probably also be used for fictional families. 

Currently, there is no provision to connect Families to MakingProcesses (e.g. made by Embriachi family) - I hesistate since such family workshops hardly ran over more than 2-3 generations and just only a small part in the history of a family (although probably in many cases the only part relevant here). On the other, how to do it else? Having a 'Family workshop' with a specific lifetime connected to a family? At a first glance, this could be smoother. The resulting Edge between Family and Organisation could also be used for connecting e.g. the organisation "Medici Family Collection" to the Medici Family. I have to think about it. 

![Create](./class_diagrams/Family.png)


**Attributes:**

- date: this means the date when the family is important for the purposes of this database (otherwise, one would have to start with Adam, naturally)


**Edge between Family and Text:**

This would be only used for fictional families. 


**Edge between Family and Heading:**

It may make sense to use this link to group together types of families, e.g. ruling families, or lower nobility, but I am not sure how much sense this would make. 


**Edge between Family and Place (EdgeFamilyPlace):**

This could be used either simply to allocate families to countries, or to give a typical family seat, if there be one. Several such connections are possible, and they could be limited by dates (I am not sure about the practicalities)


**Edge between Family and Office (EdgeFamilyOffice):**

This would be used to connect families of rulers with the office, e.g. the Wittelsbach family to Dukes/Electors/Kings of Bavaria. It could also be used for families that regularly held non-hereditary offices (e.g. the Wittelsbach also as Archbishops of Cologne in the Baroque Age), but this may get a bit too much. 


**Edge between Family and Iconography (EdgeFamilyIconography):**
**Edge between Family and Option (EdgeFamilyOption):**

The Edge to Iconography would be used with different relationships for different types of iconography, heraldry would be the typical use, however, some other relationships might also be possible:

portrait of members / family of portrayed persons (for a group portrait). 

The Edge to Option would function similarly, but it is hard to think of real use-cases, so I primarily included it for the sake of consistency. 

The attribute copy_variants determines if any variants (i.e., Criteria and Options) linked to the Family record should be made available in this Iconography record. 


**Edge between Family and Cycle (EdgeFamilyCycle):**

This Edge would be used for regularly, e.g. for ciycles of family portraits, or for cycles of history paintings showing achievements of members of a family. 


**Additional criteria for creating links:**

- none
 

**Additional criteria for validation for saving record:**

- none
  

**Additional criteria for validation for publishing record:**

- a Family probably should have a connection to a Place. 
- a Family needs to be connected to a Person or an Iconography/Option/Cycle. 


## Office

Like Family, this is primarily an addition to the class Person. It helps to search for images connected to persons who had the same office, e.g. all Bishops of Augsburg. An Office is defined as a 'job' within an 'organisation' (or in case of political authorities, with a place). Typically, there is only one holder of an Office at a time, although there would be exceptions (e.g., Roman consuls - I a not sure if canon of a Cathedral would count as office since there is a higher, but limited, number, but perhaps it should). 

![Create](./class_diagrams/Office.png)

**Attributes:**

- date: This would denote the time when the office existed, but I am not sure how important this information really is (I mainly left the field here for the sake of consistency). If it is used, it should allow for timespans that have no end date. 

**Edge between Office and Office:**

This Edge could be used to indicate which Office was replaced by another (e.g. Duke of Bavaria by Elector of Bavaria). I am not sure how necessary it is, and it is certainly sometimes subjective. 

**Edge between Office and Cycle (EdgeOfficeCycle):**

This is meant e.g. for portrait series of all bishops of a certain see. Perhaps, one would need also here connections to Iconography and Option, but I currently have problems finding a use case. 

**Additional criteria for validation for saving record:**

- none
  

**Additional criteria for validation for publishing record:**

- an Office must be connected to either an Organisation or a Place (Place meaning here Region - historical or Town). 
- an Office needs to be connected to a Person or an Iconography/Option/Cycle. 
- each EdgePersonOffice must contain a date - to allow sorting of office-holders. 




## Organisation 

This record is for two different types of organisations, firstly Collections and secondly what could be called Groups of Members. It may make sense to have here two different types of records, but they also may overlap (e.g., an Abbey may have a library or an art collection) - although one could have different Group of Persons and Collection records and cross-reference them, as one wold cross-reference between an Abbey as Organisation and the Buildings of an Abbey. 

![Create](./class_diagrams/Organisation.png)

**Attributes:**
- type:
  - There must be at least a type "Collection" or a type "Group of Members" (I hope I find a better name), and there can also be both. 
  - If there is a type "Collection", there must also be a type "Museum", "Library", "Archive" (pershaps), "Private Collection", "Dealer", or "Auction House". These are mutually exclusive, and they determine the way other attributes are displayed in the UI. 
  - The name_variant field would also include former names. Currently, there is no way to indicate the time of name changes, but this is not really the job of Iconobase. 
  
**Edge between Organisation and Heading**
This is not yet really developed, one might want to connect, e.g., all civic militias (which are important in Dutch art, e.g., Rembrandt's Nightwatch to heading such as 'military units')

**Edge between Organisation and Person (EdgePersonOrganisation)**
In addition to has member / member of, many other relations are possible, e.g.:
founded by / founder of
has director / director of (unless 'Office is used for that')
has benefactor / benefactor of
etc. 


**Edge between Organisation and Office (EdgeOfficeOrganisation)**
This is used if a role in an organisation seems to be so prominent that it would be defined as 'Office', a good example might be "Abbot of Aldersbach". I am not yet really sure on how to count the connections. 


**Edge between Organisation and Place (EdgeOganisationPlace)**

In addition to located in / located here, some other relations are possible, e.g.:
owns this building / building of (e.g., for the connection between "Aldersbach Abbey" and the monastic buildings at Aldersbach)


**Edge between Organisation and Organisation (EdgeOrganisationOrganisation)**

This is still a vague idea, it could, for instance, link different organisations together, e.g. "Aldersbach Abbey" and the "Cistercian Order". 


**Edge between Organisation and Iconography (EdgeOrganisationIconography)**

In addition to shows members of / portrayed persons belong to (used for group portraits of members of an organisation), a number of other relations, each for different types of iconography, would be possible, e.g. 
action of members of this organisation / organisation the acting figures belong to (for narrative scenes)
allegory of / organisation shown in this allegory (for allegorical images)
emblem about / organisation alluded to in this emblem (for emblems)
coat of arms of / organisation bearing these arms (for heraldic images)

The attributes given on the Edge are the standard attributes for everything connected to iconography. Since they go in directions, one could also write them onto the arrows. 

The attribute copy_variants determines if any variants (i.e., Criteria and Options) linked to the Organisation record should be made available in this Iconography record (is rather unlikely to happen for Organisations). 




**Edge between Organisation and Option (EdgeOrganisationOption)**

This works similar to EdgeOrganisationIconography, but it connects not to the 'whole' iconography but only to a variant (this will be rarey used for Organisations, it is rather here to keep it parallel to Persons)

**Edge between Organisation and Criterion**

This Edge is primarily incuded to have a parallel with an Edge for Persons. 

**Edge between Organisation and Cycle (EdgeOrganisationCycle)**

This Edge works similar to the Edge between Organisation and Iconography, but in this case the Organisation would be the common 'Theme' of a cycle (e.g., "Events from the History of Aldersbach Abbey"). I have to think more about how to do that (especially, if there should be a node between the Cycle and the Organisation)


**Edge between Artwork and Collection (EdgeArtworkCollection)**
**Edge between Manuscript and Collection (EdgeManuscriptCollection)**
**Edge between Copy and Collection (EdgeCopyCollection)**

These three Edges have the same structure. 
- EdgeArtworkCollection is used for Artworks that are neither Multiples (as prints are) nor kept in manuscripts
- EdgeManuscriptCollection is used for complete Manuscripts
- EdgeCopyCollection is used for individual copies of multiples (irrespective if they are single objects, e.g., single-leaf prints, or parts of books)


- current indicates whether the Artwork or Manuscript is still deemed to be in the Collection or not. It is by default 'True' if the Collection is a Library, a Museum, or a Private Collection, and 'False' if the Collection is a Dealer or an Auction House. 
- inventory_number_preferred and inventory_number_other (the latter repetible) need different names in the front-end depending on the type of the Collection. 
  - "shelf mark" if the Collection is a Library (or an Archive, if I create this category)
  - "inventory number" if the Collection is a Museum or a Private Collection
  - "lot number" if the Collection is an Auction House
  - "catalogue number" if the Collection is a Dealer (only in this case one would need the field catalogue for the number of the catalogue in a series of catalogues of this dealer). 
- date means different things according to the type of Collection (this must be reflected in the FE, but I am not sure if this would be used for searches)
  - for Archives, Libraries, Museums, and Private Collections it means the time-span the object is or was in this collection (if known)
  - for Auction Houses it means the date of the Auction
  - for Dealers it means the date given in the catalogue. 
  
  It must be possible to have several different Edges between the same Artwork (or Manuscript) and the same Collection (e.g., quite a few manuscripts have been auctioned several times by Sotheby's)

- 

**Additional criteria for creating links:**

- For EdgeOrganisationPlace, the different relations go only together with specific types of Place, e.g. "located in" only with a Town or a Region, and "owns this building" only with a Building or a Building-Part
- For EdgeOrganisationIconography, the different relations go only together with specific types of iconography. 
- The three links with "Collection" can only be used if the Organisation has "Collection" amongst its types. 
 

**Additional criteria for validation for saving record:**

- The types of the Organisation contain "Collection" plus a type of a collection and/or "Group of Members"
- 

**Additional criteria for validation for publishing record:**

- The Organisation must be connected to another record. 

## Place

A Place can be anything from a country down to a composite object containing several Artworks (e.g., a multi-part altarpiece). Like Text records, places are hierarchically organised, each Place normally being connected to one and only one parent place. 

![Create](./class_diagrams/Place.png)

**Attributes:**
- type: Here, types are mutually exclusive (e.g., Town, Building, etc.), hence type is non-repetible
- coordinates: I suggested here feour different non-repetible attributes - one could also pack them into a separate class. The coordinates are given in two variants in the GND, once as degrees - minutes - seconds, once as decimal fractions. If one still wants to import both, one would need either a separate, repetible, class for the coordinates, or eight non-repetible attributes. The first set would need tuples of integers, the second floats. 
- date: I am not sure if this would be used here, it could be used to indicate when buildings or building-parts existed (will in most cases be open-ended). Other dates would be shown in the Edge

**Edge between Place and Person (EdgePersonPlace):**

In addition to born in / place of birth, several other relationships are possible, e.g.:
died in / place of death
active in / place of activity
buried in / place of burial
The date field would be needed for "active in" or similar relationships. 
 
**Edge between Place and Family (EdgePlaceFamily):**

As most things connected to the class Family, this is still vague. It could be used to connect families with their main places of activity, or perhaps also places of origin. 

**Edge between Place and Office:**

An Office must be connected either to an Organisation (e.g., Abbot of St Gallen Abbey) or to a Place (e.g., King of France). 
In case one would want to record also other connections, e.g., the seat of the office, e.g. Bonn for the Archbishop of Cologne, one might need here a date field in the Edge, but I think this is an overkill. 

**Edge between Organisation and Place (EdgeOganisationPlace):**

This link will be needed in two constellations: 
- Organisations that are groups of members could be connected the Towns or Historical Regions where they were based. 
- Organisations that are collections could be connected to the Towns or Modern regions where they would be found. 
In addition to located in / located here, some other relations are possible, e.g.:
owns this building / building of (e.g., for the connection between "Aldersbach Abbey" and the monastic buildings at Aldersbach). 



**Edge between Place and Place (EdgePlacePlace):**

Every place has to be connected to a parent place (e.g., a building to a town). Naturally, this will not be possible for the top parent (e.g. "Earth" or "Universe", should one allow for extraterrestrial places). In virtually all places, there will be one and only one parent. The only exception would be records of the type 'Town' - they could be connected to one record of the type 'Modern Region' and one or more records of the type 'Historical Region' (e.g., Bonn would be linked to the modern region "Nordrhein-Westfalen", but probably to the Historical Region "Mittelrhein"). The former is used to locations of artworks, the latter for places of origin. In some cases, there might be several Historical Regions, e.g., the "Byzantium" and "Ottoman Empire" for Constantinople. (It might be possible that 'Historical Regions' might also have several other 'Historical Regions' as parents). 

**Edge between Place and Artwork (EdgePlaceArtwork):**

This Edge is used to connect Artworks to the Place where they are (or were). The current field indicates if they are still there; additionally, dates can be given (not sure if the latter are really needed, but a date field is a standard features of the Edge, anyway). 

**Edge between Place and Iconography (EdgePlaceIconography):**

There are several relationships possible, depending on the Type of Iconography and the Type of Place, e.g.

for Iconography "Topographical View" and Place "Historical Region": 

view / view of

map / map of

for Iconography "Topographical View" and Place "Town": 

view / view of

plan / plan of

for Iconography "Topographical View" and Place "Building", "Building" or "Building part": 

exterior / exterior of

interior / interior of

reconstruction / reconstruction of

elevation / elevation of

plan / plan of

for Iconography "Narrative Scene" 
action happening here / place of action (Here is a problem: this would only indicate where an action took place, not if the place is really shown there, the latter would be rather under EdgePlaceOption)

The attribute copy_variants determines if any variants (i.e., Criteria and Options) linked to the Place record should be made available in this Iconography record. 



**Edge between Place and Option (EdgePlaceOption):**

This is in principle similar to EdgePlaceIconograhy. It will probably be largely used if a building or a building part can feature in a narrative scene or not (e.g., if the Meta Romuli appears in the Crucifixion of St Peter)


**Edge between Place and Criterion:**

This would function in general like the link between Person and Criterion - however, I am not sure if it would really be used. 


**Edge between Place and Cycle (EdgePlaceCycle):**

This Edge works similar to the Edge between Place and Iconography, but in this case the Place would be the common 'Theme' of a cycle (e.g., "Events happened in Florence"). I have to think more about how to do that (especially, if there should be a node between the Cycle and the Place). 

**Edge between Place and Heading:**

I am not sure about how this Edge could be used. Perhaps, one might group differenttypes of buildings or building parts together, e.g. Franciscan Churches, Libraries, or Pulpits. 



**Additional criteria for creating links:**

Most links only make sense with certain types of Place records: 

- Persons / Families / Offices: only types "Historical Region" and "Town"
- Organisations: 
  - for located in: "Historical Region", "Modern Region", and "Town"
  - for owned the building: "Building Group", "Building"
- Places: only the following connections for 'has part' are possible:
  - "Historical Region" : "Historical Region", "Town"
  - "Modern Region" : "Modern Region", "Town"
  - "Town" : "Building", "Building Group", "Composite Artwork" [the latter used e.g. for monuments]
  - "Building Group" : "Building"
  - "Building" : "Building Part", "Composite Artwork"
  - "Building Part" : "Building Part", "Composite Artwork"
  - "Composite Artwork" : "Composite Artwork" (e.g. wings of a large altarpiece)
- MakingProcesses : "Historical Region", "Town"
- Artworks: "Town", "Building Complex", "Building", "Building Part", "Composite Artwork"


**Additional criteria for validation for saving record:**

- none
  

**Additional criteria for validation for publishing record:**

- The Place must be 'part of' a parent place. 
  - If the Place is connected with an Artwork or an Organisation with the type "Collection", it must be connected to a upwards through "Modern Regions". 
  - If it is connected with a Person, a Family, an Office, an Organisation that is not a collection, a Book, an Iconography, an Option, a Criterion, or a MakingProcess, it must be connected upwards through "Historical Regions"
- In addtion, the Place must be connected to at least another node. 


## NaturalObject

This class is primarily used for plants and animals. Like the Place and Text classes, it is stacked hierarchically, from large units (e.g., 'Insects' down to species, or even named individual animals). 

Describing animals and plants will bring a number of problems. Firstly, they appear in art in two very different contexts. In most cases, only a small number of species appear (e.g., animals in fables, or as attributes), but in some large quantities (perhaps some 2000 plants in some 16th-century herbals). In the former situation, the animals are either not named at all, or with rather generic names ('a fox'), the the latter, they typically come with specific names that are in practially all cases not the scientific names used today; often, dictionaries offer identification, but these can be wrong (what only specialist could determine). 
Secondly, there is a traditional biological systematic that is both complex and counter-intuitive (especially regarding botany), and a modern systematic ('cladistic') that is even more complex. Either of them would overwhelm Iconobase, yet the great number of animals and plants necessitates some structuring. Hence, one would probably use a somewhat simplified system with only few levels of hierarchy (e.g. Chordate > Mammal > Carnivore > Lion). 

![Create](./class_diagrams/NaturalObject.png)

**Attributes:**

- type: Here should be relatively few types, not the entire biological hierarchy: 
  - group (for anything genus or above)
  - species (also for subspecies, variant as far as there are any relevant images)
  - species old name (used for historical names of species appearing in labels)
  - breed (used e.g. for dogs, horses)
  - individuum (used e.g. for portraits of race-horses or dogs)

- name_preferred: for the types group and species, this is normally a scientific binomial name
- name_translated: for the types group and species, one could use this field to give a preferred vernacular name I(probably, both the Latin and the vernacular name would be displayed together)
- references: for some common animals, there might be references in Iconclass I(but there are only few); furthermore, one could make references to scientific databases, although I am not sure to which ones. 

**Edge between Natural Objects (EdgeNaturalObjectNaturalObject):**
There are several possible relationships, depending on the type of the two Objects: 
has part / part of: for group > group, group > species, species > species, species > breed
formerly named / today named: for species > species old name
individuum / belongs to: for species > individuum, breed > individuum

The cardinality 'upwards' is normally "1". "0" only appears for the very top levels (e.g., record "Animals"). Cardinalities of higher than "1" would only be needed in exceptional cases, e.g., if a "species old name" can be attributed to several modern species. If it is worth introducing this complication (since Text and Place records normally have here cardinality "1" I am not sure)

**Edge between Natural Object and Iconography (EdgeNaturalObjectIconography):**

This Edge would probably be not used for records of the type 'group' (I reckon that one would rather have e.g. a 'species' record for 'not-further-defined snake'). 

There could be different relationships

view / view of
skeleton / skeleton of
detail / detail of (e.g., fruits, teeth etc.)
group / group of 
with other species / view of (with other species)
shown in / acting animal (for Narrative Scenes)
in emblem / acting animal (for Emblems)
as attribute / object from nature as attribute (for Image with no narrative content / Allegorical Scene) (This is rare, more commonly, this would appear in connection with Options, see below)


**Edge between Natural Object and Option (EdgeNaturalObjectOption):**

There would be similar relationships as above (with something like 'additional' added). 
Here, probably the relationship "as attribute / object from nature as attribute" would be the standard. It would be used for not only for Options of Criteria connected to Image with no narrative content and Allegorical scene, but also for Options of Criteria connected to Persons and Personifications. 

**Edge between Natural Object and Heraldic Object:**

Since Objects in Heraldry will need some special treatment, I will use a separate class for them that will be cross-referenced to the normal Object classes, as here. 
In most cases, the cardinality will be 0..1 -- 0..1, but there are sometimes several Heraldic Objects for a Natural Object (e.g., Bear and Bear's claw), and who knows if the opposite might not also happen sometimes.

**Additional criteria for creating links:**

- links 'downwards' within the group of Natural Objects will only be possible between certain types. 
  - groups can link to groups and species
  - species can link to species, species old name, breed, and individual
  - breed can linke to individual

All records can be linked to Iconography and Object records - with exception of records of the type group (for 'any snake' in an image one would attach to the group record snake a fictive species record 'any snake'). This restriction prboably also applies for links to Heraldic Objects, but not to Cycle records. 


**Additional criteria for validation for saving record:**

- none
  

**Additional criteria for validation for publishing record:**

- The record must be linked to a parent record (unless it is already e.g. 'Animals'). 
- The record must be linkedto an Iconography, Option, Cycle or HeraldicObject record. 



## Text

This class is used for texts as such, their physical copies are rather described in the classes Book and Manuscript. They are needed in three circumstances: firstly, they indicate the textual source for an iconography, secondly, they identify the passage of a text into which a certain Artwork is placed as illustration, and thirdly, they identify quotations used as inscriptions. 

Like Place, instances of this class are stacked hierarchically - apart from the highest level, each instance of Text is connected to one and only one parent text. 

![Create](./class_diagrams/Text.png)

**Attributes:**

- type: The type shows the hierarchical position of the node, hence it is not repetible. There would be probably the following types: 
  - "Text": At the top of the hierarchy, meaning a book, or otherwise an independent text. Is the only type that does not have a link to a parent text. May have a link to one or more persons
  - "Chapter": A subsection of a text that is typically marked as such, e.g. by a chapter heading or a number
  - "Passage": A subsection of a text that forms a narrative unit but is not marked by a heading. 
  - "Quotation"
- numbering: This string would contain information on th place of a Text within a larger Text, it would be used for display, not for sorting. its format would depend very much on the type of the text, e.g. "Chapter 2", "Mt. 2:3-15". Because of the needed flexibility, it probably makes little sense to divide this into several subfields. However, one would probably need some help for putting in information to achieve consistency. The ordering of text records within a parent text is done through the EdgeTextText. 
- name_preferred: This would contain the title of a book or chapter, or the content of a quotation, in the original language (for Bibles in Latin, I assume), and for Texts of the type passage a made-up English heading. In a Text of the type Chapter that has a numbering, the name_preferred is not obligatory. 
- name_translated: Translation of the name_preferred into English (if one wants to be multi-lingual, one could probably have several name_translated fields in several languagues)
- date: It could beused for Texts of the type Text to give the date when a text was first published, but I am not sure if this is really needed. 
- duplicate: Normally, every Artwork can only be the illustration of one Text - however, but a Text marked Duplicate can be connected additionally (this may be used for liturgical books)

**Edge between Text and Text (EdgeTextText):**
A Text of the type chapter, passage, or quotation, has the cardinality 1 for connection with a parent Text, but a Text of the type text has no parent Text, and hence the cardinality is here 0. 

The number is used for ordering the child Text (since the 'numbering') in the child Text records is a string. This element is placed in the Edge parallel to the "numberA" and "numberB" in other Edges - since the numbering is going here in one direction only, one could also make it an attribute of the child Text 

**Edge between Person and Text:**

This is used for two very different relationships: 

The first is about a (normally real-life) person regarded as responsible for the making of the text. Apart from wrote / written by, also the following relationships are possible. 

compiled / compiled by

translated / translated by

The second is for persons that are the inventions of an author (typical example: Don Quixote) or were largely embellished in this text (e.g., Alexander the Great in the Alexander Romance), and it would also be used for figures from the Bible. They would be either attached to the whole text, or only to the chapters or passages that are relevant, e.g., Abraham would be probably only linked to Genesis or parts from Genesis. 

Here, the relationship would be: 

person from / comes from

(one might have slightly different wording for persons whose live was only embellished by a text). 



**Edge between Text and Heading:**

I am not sure if this is needed, and what for. 

**Edge between Text and Manuscript:**
**Edge between Text and Book:**

These two Edges could be used to show for every text the illustrated manuscripts and books kept in Iconobase. However, strictly speaking, this information could be inferred via the connections between Manuscript and Artwork, and Artwork and Text (or Book and Artwork, and Artwork and Text), hence I am not sure if it has to be (a) created manually (b) created automatically and then stored so that it could be edited manually, or (c) created automatically for search processes only. 

**Edge between Text and Artwork:**

Here, the cardinality from Artwork to Text is normally 0..1 (an Artwork may can only illustrate one Text, the text written next to it). However, there can be additional connections to texts with duplicate as True, hence 0..n in this situation. 

**Edge between Text and Iconography (EdgeTextIconography):**
**Edge between Text and Option (EdgeTextOption):**

This Edge is used for two different scenarios
- with the Text being the literary source of the iconography (relation source of / source as shown in the digram)
- with the Text (normally a Text with the type "Quotation") being actually quoted as part of the Iconography (this will happen more often wiht Option records) (relation quoted in / quotes)


**Additional criteria for creating links:**
- Links between Texts and Texts: The following "part of" connections are possible. One should not that "Chapters" are not hierarchically higher than "Passages". In the Bible, for instance, one might have a "Passage" "Story of Abraham" comprising some 10 chapters of Genesis. 
  - "Texts" can be linked to "Chapters", "Passages", and "Quotations"
  - "Chapters" can be linked to "Chapters", "Passages", and "Quotations"
  - "Passages" can be linked to "Chapters", "Passages", and "Quotations"
  - I am not sure if "Quotations" would be at the end, or if they could be linked to other "Quotations"
  

- Links between Texts and Persons: 
  - If the person is responsible for the production of the text, there must be the type 'Author'
  - If the person appears in the text, there must be the type 'Literary Figure' or 'Biblical Figure'


- Links between Text and Iconography. I am not sure if this should be restricted to certain types of Iconography, especially "Narrative scene". 


**Additional criteria for validation for publishing record:**

- The Text must be 'part of' a parent Text (unless it has the type "Text")  
- In addtion, the Text must be connected to at least another node. 

## Action

This class is used for describing actions, it is normally connected to Iconographies of the type 'Narrative Scene' or "Emblem", occassionally it might also be connected to Option or even Cycle records. 

![Create](./class_diagrams/Action.png)

**Attributes:**
- types: Currently, I do not think that one needs to divide Action records into individual types. 
- references: Potential sources for external references would be Iconclass or Getty vocabularies. 

**Edge between Actions (EdgeActionAction):**

Action records are not as strictly hierarchical as Place, Text, or NaturalObject records, but in some places there might be subtypes of Actions (e.g., the action 'Beheading' could have the subtypes 'Beheading as Martyrdom', "Beheading as (organised) execution, 'Beheading as (unorganised) murder"). An alternative would be to classify only the subtypes as true actions, and the more abstract higher types as headings. 

**Edge between Heading and Action (EdgeHeadingAction):**

The Heading can signify general themes (e.g., liturgy, teaching, execution of justice) but also tools used for this action. 

**Edge between Action and Criterion:**

This is useful for recording different variants of an action, it would need to be inherited through 'copy_variant'. To use the bloodthirsty example from above, one could perhaps ask here, if a sword, and axe, or a guillotine is used. If there are Actions that are children of Actions, there is naturally a risk of the inheritance becoming chaotic. 


**Additional criteria for creating links:**
- Actions could only be linked to Iconographies including actions, thus e..g Narrative Scene or Emblem, but not Portrait. 
  
**Additional criteria for saving record:**
none

**Additional criteria for validation for publishing record:**
- The record must be connected to another Action record or to a Heading
- The record must be connected to an Iconography or an Option, or a Cycle


## Book 

This record is for Books that contain printed illustrations - hence, there are probably a number of copies with the same illustration (not for modern bibliographical references). 

![Create](./class_diagrams/Book.png)

**Attributes:** 

parent title and volume number are only to be used for multi-volume works, and I am not sure what to do here. 
It would be the most correct solution to have a separate record for the parent title and to connect it to the individual volumes. However, this methods is probably an overkill here. 
One might even copy everything into one title phrase, I am not sure. 

all_catalogued? would True by default. If for some reason only a part of the images have been entered into the database (e.g., only the big images, not decorative borders with figures), it has to be set to False, and a description of what has and what has not been entered added to the all_catalogued?_comments field. 

I reckon dates will always be non-repeatable (or not???), and I cannot think why one would need two different dates here. (There might be conflicting indications of dates, but they might better go into a comment field)

**Edge between Book and Person:**

In addition to author was / author of, also the following Relations are possible:
editor was / editor of
printer was / printer of
publisher was / publisher of

**Edge between Book and Place:**

In addition to published in / place of publication of, also the following Relation is possible:
printed in / place of printing of

**Manuscript:**

This connection is for the case that a copy of a printed book has painted decorations. In some cases one would simply catalogue it as a 'manuscript', but in other cases one might one to refer to the original book (e.g., if the paintings are actually overpaintings of the printed illustrations and copy their compositions, as not rare in French luxury books). This is not be used very often. 

**Edge between Book and Artwork (EdgeBookArtwork):**

The sequence number is the number of the Artwork within the Book. If there were only one Artwork per page, it could be the canvas number of the IIIF manifest, but if there are several images on a page, it would need a suffix so that the images appear in correct narrative order. This could be a tuple of two integers, a float with the image number on the page after the decimal point, or a string consisting of the canvas number and a letter - but this may be harder for sorting. 
The cardinality from Artwork to the Edge is 0..1 - by definition, a re-impression of an image in a different book is a different Artwork (since other connections from Artworks to Edges denoting Locations would be 0..n, it might be easier to also set 0..n here, too)


**Additional criteria for validation for publishing record:**

- At least one Artwork must be connected to the Book. 
- A connection between Artwork and Book is only possible if the Artwork has a Medium suitable for Books (e.g., "Engraving", "Woodcut"), e.g. not "Mural Painting". Probably, connections to Book objects should only be suggested for Artworks with appropriate Media. 
- 
## Manuscript

This record is a parallel to the 'Book' record, but is for objects that only exist once, thus either manuscripts or copies of printed books with some unique decoration (e.g., painted decoration, binding). Since these items are identified by their location, not by author, title, place and date of printing, the Manuscript records are simpler than the Book records. 

![Create](./class_diagrams/Manuscript.png)

**Attributes**:

- The type could indicate if it is a Manuscript, or unique decoration in a printed book. This is primarily relevant for display purposes, it would be confusing to call a printed book with a painting on the first page a manuscript. Both options are mutually exclusive, hence the attribute is marked as non repetible - however, in other cases, the type would be repetible, and it doesn't harm to have it here as repetible, too. 
- ExternalReference is here primilary for the planned International Standard Manuscript Number. 
- The fields common_name_preferred and common_name_variant will only be used for some very prominent manuscripts that are known not only under the shelfmark (as usual), but also under a name, e.g. "Lindisfarne Gospels"
- all_catalogued? functions as with Books. 

**Edge between Manuscript and Artwork (EdgeManuscriptArtwork):**

This functions similar to the Edge between Book and Artwork (see above). 
New is the attribute "current?" - it indicates if the Artwork is still part of the Manuscript or has been cut out (alas, too common)
The cardinality from Artwork to the Edge is now not 0..1 but 0..n - there are cases of images cut out from one manuscript and glued into another; but I assume that this cardinality would be probably 0..n by default, see above under Book. 

**Edge between Book and Collection (EdgeManuscriptCollection):**

This Edge is the same as the Edge between Artworks and Collections. 



**Additional criteria for creating links:**
- An EdgeManuscriptArtwork can only be established if the Artwork has a Medium appropriate for a Manuscript (e.g. "Illumination", not "Mural Painting")

**Additional criteria for validation for saving record:**

- If there is more than one EdgeManuscriptArtwork, not more than one may have current as True. 
- If there is more than one EdgeManuscriptCollection, not more than one may have current as True. 

**Additional criteria for validation for publishing record:**

- At least one Artwork must be connected to the Manuscript.
- The Manuscript must be connected to at least one Organisation of the type "Collection". 
- If the Collection is a Library or an Archive, there must be an inventory_number_current. 
- If the Collection is an Auction House, there must be a date (or a dummy for date not known??)


## Inscription

I am still somewhat uncertain about this record. In general, I would only record inscriptions if this gives relevant information (e.g., having "SCS GEORGIUS" next to an image of St George doesn't tell us much, one could then tick the qualifier 'inscription' next to the Iconography and would not have to bother transcribe the text. On the other hand, such transcriptions, even if not relevant from other perspectives, could make sense for single-leaf prints because they can help with the identification.) 
Some inscriptions are regular parts of iconographies (e.g., Apostles holdings scrolls with passages of the Creed, whereas others appear only once). Hence, it looks as if Inscription records should be connected both with Iconography and (more commonly) Option records, but also with Image records. If Inscriptions are quotations (this would normally the case in this situation), a link to the Text would be made. In this case, one would not transcribe the text, since it may be slightly different in every occurrence - if one wanted the wording, one would have to add a separate Inscription node to the Image record. 

When thinking of it, I wonder if one should not restrict Inscription to connections to Image record and connect Iconography and Option records directly with the text instead. 

![Create](./class_diagrams/Inscription.png)

**Attributes:**

- text: This is the field that would normally be filled, it has the text in original language but in normalised spelling (e.g., without abbreviations)
- text_diplomatic: This would be the field for exact ('diplomatic') transcriptions, if desired (I wouldn't use them, but some people might want to). This would probably need Unicode (I have no idea if Unicode is now the standard, anyway)
- text_translated: For a translation of the text, if desired
- lemma: by default False, set to True if one Iconography of the connected Image is of the type "Emblem" (can be undone manually, if needed). 

**Edges:**
To be added later, when I have worked out what to do. 

**Additional criteria for creating links:**

A link to a Text is only possible if the Text has the type "Quotation". This would mean that is actually quoted in the Text record. 


**Additional criteria for validation for saving record:**

There must be either a link to a Text record, or the text field must be filled (or as condition for publishing?)

**Additional criteria for validation for publishing record:**

The record must be connected to an Image record (or, if I use that, to an Iconography record)

## Iconography

This record is the central record on subject-matter of an Image, and as such it has numerous connections: firstly to Object records describing the depicted Objects (Persons, Places, etc.), secondly to Criterion records describing potential variations, and thirdly to Image records. 

![Create](./class_diagrams/Iconography.png)

**Attributes:**

- type: in this case (and contrary to, e.g., Person records), here the type is non-repeatable. 
- references: This refers primarily to Iconclass notations. One could also refer here to Warburg or Princeton Index URIs.

**Edge between Iconography and Person (EdgePersonIconography):**
**Edge between Iconography and Family (EdgeFamilyIconography):**
**Edge between Iconography and Organisation (EdgeOrganisationIconography):**
**Edge between Iconography and Place (EdgePlaceIconography):**
**Edge between Iconography and Natural Object (EdgeNaturalObjectIconography):**
**Edge between Iconography and Text (EdgeTextIconography):**
**Edge between Iconography and Action (EdgeActionIconography):**
**Edge between Iconography and Artwork (EdgeArtworkIconography):**

These Edges connect the Iconography record to records for the Objects shown in the Iconography. All Edges are explained with the respective Objects. Several more such Edges will be added later. 

**Edge between Iconography and Criterion (EdgeIconographyCriterion):**

This Edge connects the Iconography record with a Criterion record that specifies an element where variants occur, e.g., a specific attribute that may be present or not. 
Its only attribute, the number, is a means to bring the Criterion records into a meaningful order. 

**Edge between Iconography and Image (EdgeImageIconography):**
see above

**Additional criteria for creating links:**

Links to Object records can only be made if the Object is appropriate for the type of the Iconography record, e.g., a Portrait record can only be linked to Person and Organisation records (portrait and group portrait), not to Places or Actions. 


**Additional criteria for validation for saving record:**

none

**Additional criteria for validation for publishing record:**

- the record must be linked to at least one Object record. 
- the record must be linked to at least one Iconography record. 
- according to some preliminary discussions with the editors of Iconclass: if the record has no Iconclass ID in external references, an automatic message will be sent to Iconclass. If Iconclass assigns a notation to this iconography, this ID will be sent to Iconobase (if possible, it should be added to the record automatically, otherwise manually). 

# Group Records

This small group of records that contain shared information for a (normally small) group of individual records. 

## Matrix

In book illustrations, often the same Matrix (typically a woodblock or a copperplate) are used repeatedly, sometimes with different iconographic significance. 
The Matrix record has two purposes: 
- it contains the MakingProcess records that are connected to the Matrix and hence shared by all re-uses of it. 
- it contains a list of all sections of Text Artworks using this Matrix illustrate, and a list of al Iconographies the connected Image records display. Its purpose is that this information can then copied quickly into records for a new use of this Matrix, if it illustrates the same text and/or has the same iconographic significance. 

Normally, these records will be created, updated and linked automatically through the Process Identifying re-used printing matrices. 

![Create](./class_diagrams/Matrix.png)

**Attributes:**
The attributes have been copied from the Artwork record, but this may be more than actually needed. 
- medium: I kept it as repeatable, but in this case there will only be one Medium. 
- name_preferred, name_variant: I really doubt if there are any individual book illustrations with a common name, so I wonder if these fields would ever be needed. 

**Edge between Matrix and MakingProcess (EdgeMatrixMakingProcess):**

This functions like EdgeArtworkMakingProcess (below). 
There will be normally three MakingProcess items attached (though some might not have any data and hence will not be saved), one for the design, one for the making of the matrix, and the third for the first known printing (in practical terms this would normally mean the first printing already recorded in Iconobase. The latter is necessary because it normally provides a place and a date, whilst especially the production of woodcuts often has neither). 

**Edge between Matrix and Text:**

This is like the Edge between Artwork and Text (see below). However, here, the cardinality must be 0..n - a matrix can be printed as illustrations of different texts. 

**Edge between Matrix and Iconography:** 

This is like the EdgeImageIconography (see below)

**Additional criteria for creating links:**

An Artwork can only linked to a Matrix if the medium of the Matrix is also the medium (or one of the media) of the Artwork. 
A Matrix can only be linked to MakingProcesses that are appropriate for its medium. 

**Additional criteria for validation for saving record:**

The MakingProcess record may not contradict one another (see below for Artwork records). 

**Additional criteria for validation for publishing record:**


- A Matrix record can only be published with it has at least one MakingProcess connected to the original making of the Matrix (i.e., excluding types such as "destroyed" or 'reconstructed', but including 'first printed') that is linked to a place and at least one MakingProcess that has a Date field (it could be the same MakingProcess). 

## Cycle

A Cycle is a group of Images that belong to Artworks made to belong together (though not necessary by the same making processes) and that have a common iconographic theme (e.g., tapestries of the Labours of Hercules). 

![Create](./class_diagrams/Cycle.png)

**Attributes:**
- medium: a list of all media of the Artworks of the connected Images, deduplicated (normally, all have the same medium, anyway.)
- name_preferred, name_variant: once again, this is only used in the case the whole cycle has a commonly quoted name, e.g. "Triumph of Caesar", or "Raphael Cartoons". 

**Edge between Cycle and MakingProcess (EdgeCycleMakingProcess):**

This is the same as the EdgeArtworkMakingProcess (see below). I am not sure how it will be used, the simplest thing would be to have here all MakingProcess information that is shared by all members of the group. One could, however, also give information relevant only for some members of the cycle - in this case, the boolean 'partial' in the Edge would be True (one could also add it to the MakingProcess node in this case.)

**Edge between Cycle and Whereabouts (EdgeManuscriptCycle, EdgeBookCycle, EdgeCycleCollection, EdgePlaceCycle):**

These Edges function in the same way as the corresponding Edges of the Artwork node. They would probably contain whereabouts information shared by all members of the cycle, details have to be sorted out. 
The only addition is the boolean 'partial' that could be used to indicate if a Cycle is split over several locations (one could also forego it and only indicate the former locations where all used to be together, I ahve to think about it). 

**Edge between Cycle and Themes (EdgePersonCYcleTheme, EdgeFamilyCycleTheme, EdgeOfficeCycleTheme, EdgeOrganisationCycleTheme, EdgePlaceCycleTheme):**

These Edges connect the Cycle to the Object that is depicted, e.g. if the cycle is scenes from the Life of Christ it would be connected to Christ, if it is portraits of all Bohemian Kings, it would be connected to Office. Probably, there would be an element between the Themes and Cycle, e.g. to define if something is a cycle of the Infancy of Christ, a cycle on the Passion, etc. I wonder if one would put a 'theme' as an attribute into the Cycle record, or connect to the Persons, Organisations etc. Heading records with headings such as "Cycles - Infancy", and only these to the individual cycles, or find again another solution. 
NB: OrganisationTheme and PlaceTheme nodes are simply Organisation and Place nodes - only, I have them elsewhere in the diagram, and I didn't want it to become too confusing. 

**Edge between Cycle and Image (EdgeImageCycle):**

see below under Image. 

**Additional criteria for creating links:**

Most of the links would not be created from scratch - rather, one would select a number of records and create a cycle of out them, so that MakingProcesses, whereabouts etc. would be taken from the individual Artwork records. Hence, only combinations already appearing there would be used here, and hence the criteria for creating links would be fulfilled: 
- MakingProcess records have to be appropriate for at least one of the media given
- Whereabouts (Place, Collection (=Organisation), Manuscript, Book) records hav to be appropriate for at least one of the media given. 

**Additional criteria for validation for saving record:**

  - The MakingProcess records may not contradict each other (if 'partial') in the Edge (as shown here, or in the MakingProcess record) is used and set to True, it does not count as contradiction. 
  - Only one connection to whereabouts (Place, Collection (=Organisation), Manuscript, Book) with the attributes current True may be given (exception: if all have the attribute partial True)

**Additional criteria for validation for publishing record:**

Only cycles connected to at least one Image record will be published. 



# Individual Records

## Artwork

The Artwork record describes the Artwork as physical Object, hence primarily what it is made of (Medium), by whom, where and when it was made (MakingProcess), and where it is (Place, Manuscript, Book). 

![Create](./class_diagrams/Artwork.png)

**Attributes:**

- ingest_id: This is the ID of the ingest process during which the record was created. I am not sure if it should be kept after the record has been published, but this might not do harm. 
- published: default False, set to True when the record is complete, validated, and made available for public searches. If ingest_id is deleted after publication, this field is not necessary. 
- medium: the material and technique of the artwork - it defines the appropriate types of MakingProcess objects and furthermore, to which locations (Manuscript, Book, Collection, Place) the artwork can be linked
- name_preferred: In contrast to authority records, this field is not required, it is only used in two cases: 
  - if there is a common name for the Artwork (e.g., Mona Lisa)
  - if there are images depicting this Artwork so that the Artwork record has to be connected to an Iconography record (e.g., an engraving after the Hercules Farnese)

**Edge between Artwork and MakingProcess (EdgeArtworkMakingProcess):**

This Edge currently only contains the number of the MakingProcess, making sure that these processes are listed in the correct order (e.g., starting with 'design'). Since every MakingProcess is connected to one and only one Artwork, one could likewise keep the Edge empty and store this information as attribute of MakingProcess - I suggest here this solution to be consistent with other Edges. 
The Edge between a Matrix and a MakingProcess record functions in the same way. 
I am not sure if relationships are really needed here; if so, I could make some up. 

**Edge between Artwork and Matrix:**

This Edge is only used for printed book illustrations, it contains the Artwork Record to the Matrix record for the printing matrix. This means that the MakingProcess records linked the Matrix record will be treated for displaying and searching like MakingProcess records linked directly to the Artwork record. 
Some printers combined images from more than one Matrix. In these (rare, but not extremely rare) cases, one Artwork would be combined with several Matrix records. 

**Edge between Artwork and Artwork:**

This Edge is used in two situations:
- if one Artwork is a copy of another Artwork, with the relationship copy/copy of as indicated in the diagram. 
- if one Artwork was produced as part of the making of another Artwork. In this case, different relationships are possible, e.g.: 
preparatory drawing / preparatory drawing for
oil sketch / oil sketch for
modello  / modello for
ricordo / ricordo for

**Edge between Place and Artwork (EdgePlaceArtwork):**
**Edge between Collection and Artwork (EdgeArtworkCollection):**
**Edge between Manuscript and Artwork (EdgeManuscriptArtwork):**
**Edge between Book and Artwork (EdgeBookArtwork):**

These four Edges are used to indicate where the Artwork is located - in a Place (e.g., in a church building), in a Collection (e.g., Museum or Dealer), or within a manuscript or within a book. 
Depending of the type of location, they have different properties, e.g. the locations in books and manuscripts contains page numbers, the location in collections inventory numbers, etc. These Edges have been explained in greater detail above. 

**Edge between Artwork and Text:**

This Edge is used to indicate, which passage of a text is illustrated by the Artwork (this has nothing ot do with the iconography, but it means basically the passage of text the Artwork is in, e.g., a Crucifixion may be in a book of the Life of Christ, or in the Canon of a Missal, etc.). For details, especially the cardinality, see above. 

**Edge between Artwork and Iconography (EdgeArtworkIconography):**
**Edge between Artwork and Option (EdgeArtworkOption):**
**Edge between Artwork and Cycle (EdgeARtworkCycle):**

These three Edges are ony used if the Artwork is in turn the iconography for other Artworks (e.g., an engraving showing the Hercules Farnese). Of them, EdgeArtworkCycle will be needed very rarely, and for EdgeArtworkOption I cannot think of a use case, so I primarily added them for consistency (I didn't add a connection to Criterion because I think that this could really be ruled out)

There might be an alternative set of relationships for EdgeArtworkIconography:
reconstruction / reconstruction of 

**Edge between Artwork and Image (EdgeArtworkImage):**

This Edge currently contains two elements:
-  number: number oof the Images, making sure that the Images are listed in a sensible order (e.g., starting with an overview, and then perhaps from bottom left to top right in case of a big fresco, or so). 
- preferred: true if this is the Image the photo connected with should be shown as result of a search for the Artwork (normally an overview photo) 
Since every Image is connected to one and only one Artwork, one could likewise keep the Edge empty and store this information as attribute of Image - I suggest here this solution to be consistent with other Edges. 

**Additional criteria for creating links:**

- Links to MakingProcesses can only be made ife the type of the MakingProcess aligns with one of the medium attributes of the Artwork (e.g., a Fresco cannot be 'sculpted'). 
- Links to locations (i.e. Places, Organisations (=Collections), Manuscripts and Books) can ony be made according if the location aligns with one of the medium attributes of the Artwork (e.g., a printed book image can only be linked with a Book, a fresco cannot linked with a Manuscript, etc.)
- Links to Iconography, Option, and Cycle can only be made if the Artwork has a name_preferred. 


**Additional criteria for validation for saving record:**

The validation is here rather complex because it has to check combinations of linked records for contradictions. 

- The MakingProcesses must not contradict one another. This means that it is not possible to have two MakingProcesses of the same type, with the qualifier 'no comments' and partial as False (what would mean that the same Artwork was wholly painted by two different people). It is, however, possible to have one 'no comments' and one 'formerly attributed', or several 'attributed'. For printed book illustrations, this includes the MakingProcesses linked to the Matrix record. 

- The locations must not contradict one another. If it has more than two links to locations (Places, Organisations (= Collections), Manuscripts, Books), all but one must have the attribute current as False. A record linked to a Book must not have any other link to a location (this woud be under 'copy')

**Additional criteria for validation for publishing record:**

- An Artwork record can only be published with it has at least one MakingProcess connected to the original making of the Artwork (i.e., excluding types such as "destroyed" or 'reconstructed') that is linked to a place and at least one MakingProcess that has a Date field (it could be the same MakingProcess). 
- An Artwork record can ony be published if it has at least one location (Place, Organisation (= Collection) or Manuscript, not Book), or if one of the related Copy records has a link to a Collection (the latter constellation would be used for printed material that is not part of a book). There is no need for a lcoation that has the attribute current as true, in many cases one only has former locations. 



## MakingProcess

Instances of this Class always appear linked to an Artwork record. Its purpose is to describe one step in the production of the artwork, thus one activity done by one person and/or in one place at one time. 
When an Artwork record is created, one or more MakingProcess records are created, with types describing all steps typically needed to create an artwork in this medium (e.g., only one ('painting') for a fresco, but three ('designing', 'engraving', 'printing') for an engraving). Other processes could be added, if needed. 

![Create](./class_diagrams/MakingProcess.png)

**Attributes:**

- type: this describe the type of process, e.g. designing, painting, restoring, destroying. This is selected automatically depending on the Medium of the artwork, or selected from list (the list contains only those types that are relevant for the Medium of this Artwork)
- qualifier and qualifier_comments: indicating a securely the process described here took place. This is selected from a list, the default would be 'no comments', other entries might be 'attributed', 'follower of', or 'former attribution'. This can be described in greater detail in qualifier_comments
- partial: indicating if this working process touched all the Artwork or only a part of it (for situations of collaboration, e.g. Virgin by Rubens surrounded with flowers by Breughel)
- partial_detail: this field is only relevant when partial is True - one could indicate here which part is connected to this MakingProcess, e.g. "flowers"

**Edge between Artwork and MakingProcess (EdgeArtworkMakingProcess):**
see under Artwork

**Edge between Matrix and MakingProcess (EdgeMatrixMakingProcess):**

This works like the EdgeArtworkMakingProcess, see under Artwork


**Additional criteria for creating links:**
- A MakingProcess can only be linked to one Person or to one Organisation. 
- A MakingProcess can only be linked to a Person of the type 'Artist' (or, for some MakingProcesses, only 'Printer'). 
- A MakingProcess can ony linked to an Organisation of the type 'Group of Members' (One might also think of having a new Organisation type 'Workshop' and restrict the links to it, but I am not sure ife this is necessary)
- A MakingProcess can only be linked to a Place of the type 'Historical Region' or 'Town'

**Additional criteria for validation for saving record:**

- A MakingProcess record that has neither a link to a Person, Organisation, or Place nor a date cannot be saved. Such records will be created regularly when all MakingProcesses relevant for the Medium of the Artwork are created, but not all of them are filled in - what is often the case (e.g., if one only knows the designer of a woodcut, not the blockcutter). In this case, the 'empty' records will be abandonned without an error message.  

## Image

The Image record describe what can be seen on a photo of the Artwork record, hence primarily the Iconography. 

![Create](./class_diagrams/Image.png)

**Attributes:**
detail: indicates if the Image is a detail of the complete artwork or shows it in its entirety. 
position: indicates the part of the artwork shown, e.g. "top left" or "NW corner, upper row". A controlled vocabulary probably does not make sense. Normally, this would be empty if detail is 'false', but perhaps not always, I am not totally sure. 

**Edge between Artwork and Image (EdgeArtworkImage):**
see above


**Edge between Image and Image:**
This Edge is probably used for two different scenarios. 
- Several Artworks for together one 'Iconographic Unit' (e.g. an altarpiece showing the Asssumption of the Virgin, and the smaller painting above Christ welcoming Her to heaven). Since it is not foreseen (and this would probably cause chaos) to link one Image to several Artworks - each would have an Image, and they would be linked with such a function. If the Image appears in a search, related images will shown together (2 questions: should one also have a bool attribute for Image indicating that the Image shows only a part of the whole 'iconographic unit'? Should one solve this (pretty rare, but extant) problem otherwise?)
 - If Images are typological or similar relationships, this will be expressed in a rather complicated way through the Iconography records (or rather, through specific Options of the Iconography). The question is if one should additionally link them diretly through this Edge (manually? or should this be inserted automatically?)
  
  **Edge between Image and Copy (EdgeImageCopy):**
  
  This works like the EdgeArtworkImage, but numbering is not necessary since there is no sensible way in which the copies should be ordered. 

  **Edge between Image and Iconography (EdgeImageIconography):**
- preferred: This means that this is the Image that should appear in a search for the connected iconography. For every combination of Artwork and Iconography, only one connection can be preferred. 
- number: The number in which the iconographie are listed in the Image record (makes only sense in that direction)
- qualifier and qualifier_comments: Indicates how certain the connection is. This would be selected from a list, with the default 'no comments', and other options e.g. 'according to source texts', 'tentative'. If needed, this may be explained in qualifier_comments.
- options: A list of the IDs of all the Options of the selected Iconography that are pertinent for the Image

**Edge between Image and Cycle (EdgeImageCycle):**
This Edge connects the Image to a Cycle, i.e., a series of Images that are made to function as a unity and that have a common topic (simple example, Stations of the Cross in a certain church). I have not fully worked out what to do with the Cycles, but I assume that the only information needed on the Edge is a sequence number (so that the Images within a CYcle could be ordered correctly and, where it is indicated, a number for display (would be used if the Images bear these numbers))

**Edge between Image and Inscription:**
I am not yet sure what to do with inscriptions, but it is probably best not to repeat inscription records and create a new one for each Image. 


**Additional criteria for creating links:**
Every Image may only have one EdgeImageCopy that is 'preferred'. 
Every Iconography may only be connected to one Image of an Artwork with EdgeImageIconography that is 'preferred'. 
In either case, this would be ensured automatically: the first Edge is preferred True, all following Edges are preferred False, and if one of them is manually set to preferred True, all others are set to preferred False. 

**Additional criteria for validation for saving record:**

none

**Additional criteria for validation for publishing record:**

The Image needs to be connected to at least one Copy that is in turn connected to at least on Photo record. 

## Copy

The Copy record is needed for Artworks that are 'multiples', of which several copies exist (e.g., woodcuts). In this case, the link to the whereabouts of the Artwork is not given in the Artwork record but here. In contrast to the four Edges that can be used to connect Artworks to their whereabouts, here only one type is needed, EdgeCopyCollection. 

Originally, I left out this node in all other cases and connected the Image node directly to the Photo node. However, it may be best to have the same structure in all cases and so to include a Copy node without any connection. 

![Create](./class_diagrams/Copy.png)

**Edge between Image and Copy (EdgeImageCopy):**

see above

**Edge between Copy and Photo (EdgeImagecopy):**
works like EdgeImagecopy

**Edge between Copy and Collection (EdgeCopyCollection):**
works like EdgeArtworkCollection


**Additional criteria for creating links:**

Links to Organisations (= Collections) are only possible if the medium of the Artwork connected to this Copy record fits with a multiple (e.g., 'woodcut' but not 'fresco'). In this case, the Image record cannot have links to Place or Organisation records. 

**Additional criteria for validation for saving record:**

There must not be more than one Edge to a Collection with current as True. 

**Additional criteria for validation for publishing record:**

The record must be connected to a Photo record. 
As stated under Artwork Record - an Artwork Record can only be published if either it or a connected Copy record is connected to a Collection, a Place, or a Manuscript. 

## Photo

The Photo records give information on the actual photograph shown in the database. As given here, it is relatively simple and rather geared towards born-digital images. Should Iconobase to be used for digital collections of historical photographs, there might be more informatioin necessary (material of negative, technique of printing etc.) Since I have no clue about historical photography, I cannot suggest such a structure. 
There is a principal question if all photos should be stored locally, or if for photos on library and museum websites only links should be stored (the IIIF standard allows for links to specific parts of an image). I would prefer the first solution. Another possibility for book illustrations would be to save the whole pages, and to use IIIF or a similar concept to display only details in the records. 

![Create](./class_diagrams/Photo.png)

**Attributes:**

- filename: the name of the file (if needed with path) of the actual photograph
- uri: in case of photographs taken from websites, the uri of the website (for two reasons: in case of book illustrations, the photo file would only show the cropped image, and this would show the full page - in case of museum websites, there might be more metadata on the website.)
- max_download_size: can be zero, if no download permitted
- creative_commons_statement: one of the standardised conditions (normally CC0 - I reckon that modern copyright law does not permit more restrictive statements in most cases)
- creditline: public information about provider of image
- rights_internal: information about image rights for internal use only (e.g., contact details of photographer)
- date: date of the photo campaign (if one wants to indicate it). If there is a date for a linked Campaign it may not be necessary to give a date here (unless the campaign went on for many years, and one wants to be more specific)

**Edge to Person/Edge to Campaign:**
If a Person is linked to a Campaign, it would be probably not needed to indicate the Person also here (or this could be done automatically)


**Additional criteria for creating links:**
none

**Additional criteria for validation for saving record:**
none

**Additional criteria for validation for publishing record:**



## Campaign 

The Campaign records join together photos made for a particular project (or photos kept in a particular collection). There might be use-cases for a rather elaborate record, but here I suggest keeping it simple. 

![Create](./class_diagrams/Campaign.png)

**Additional criteria for creating links:**

Links to a Person can only be created if the Person has the type "Photographer"
Links to an Organisation can only be created if the Organisation has the type "Collection"

**Additional criteria for validation for saving record:**
none (it may be that a campaign is linked to several persons or organisations. )

**Additional criteria for validation for publishing record:**

A campaign record can only be published if there are Photo records connected to it. 


