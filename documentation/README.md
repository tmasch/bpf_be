Iconobase - Overview of Functions

# Table of contents


- [Table of contents](#table-of-contents)
- [General](#general)
	- [Record Types](#record-types)
		- [Individual records describe properties of one single artwork.](#individual-records-describe-properties-of-one-single-artwork)
		- ['Group records'](#group-records)
	- [Structure of Records (in theory)](#structure-of-records-in-theory)
	- [Structure of Records (attempt to apply this structure to MongoDB)](#structure-of-records-attempt-to-apply-this-structure-to-mongodb)
	- [Material stored outside the database:](#material-stored-outside-the-database)
- [General Structure](#general-structure)
	- [Ingest](#ingest)
	- [Ingest from local drive](#ingest-from-local-drive)
	- [Ingest from a museum](#ingest-from-a-museum)
	- [Ingest Photos from a library](#ingest-photos-from-a-library)
		- [Step 1: Downloading information on the Book or Manuscript](#step-1-downloading-information-on-the-book-or-manuscript)
		- [Step 2: Creating individual image records](#step-2-creating-individual-image-records)
		- [Step 3: Identifying re-used printing Matrices](#step-3-identifying-re-used-printing-matrices)
- [Creating Records](#creating-records)
	- [Connect](#connect)
		- [Connect simple](#connect-simple)
		- [Connect Iconography](#connect-iconography)
		- [Connect Place / Text](#connect-place--text)
	- [Create Iconography](#create-iconography)
	- [Create keyword and heading records](#create-keyword-and-heading-records)
	- [Create other Authority records](#create-other-authority-records)
- [Fill and Edit records](#fill-and-edit-records)
	- [Edit manually](#edit-manually)
	- [Bulk editing](#bulk-editing)
	- [Copy information](#copy-information)
	- [Merge individual records](#merge-individual-records)
	- [Complete information in Authority records](#complete-information-in-authority-records)
	- [Delete Authority Records](#delete-authority-records)
	- [Merge Authority Records](#merge-authority-records)
- [Search](#search)



*Generating png diagrams:*  
*Install plantweb using "pip install plantweb" or similar*  
*Run 'plantweb --format png plantumlfile'*


# General

## Record Types

There are three types of records

### Individual records describe properties of one single artwork. 

They consist of four records joined together with 1:n connections

- Artwork: the artwork as object, with information on medium, making processes, whereabouts, and illustrated text
- Image: a part of the artwork showing a specific scene, with information on iconography and image cycles
- Copy: only relevant for artworks that exist in multiple copies, e.g. prints, information on whereabouts of the copy from which the image is taken
- Photo: information on the photograph, also on downloading options


### 'Group records'
This group is not yet well developed, it should contain at least two - rather different - types of records

- Matrix: contains information (making processes, connected iconographies, connected illustrated texts) relevant for all artworks that are impressions of the same printing matrix. Only relevant for printed book illustrations. 

- Cycle: holds together a group of Images that were made together and have a joint iconographic significance (simple example. images of the Four Evangelists on a pulpit)


0.0.2 Authority Records
They consist of a larger number of records that can be linked to a greater number of Artwork (or Group) records, among them are

- Iconography
- Person
- Personification
- Animal/Plant
- Family
- Organisation (Collection, Monastery, Guild, etc.)
- Place
- Office
- Text
- Activity
- Element of a coat-of-arms (see below)
- General Keyword / Heading

Most of these records should be self-explanatory - with exception of the Office record. It is used to group depicted persons together. Each office record consists of a profession and an organisation or a place (e.g., King of England, Canon of Augsburg). Indicating an Office and a time would be a convenient way to locate a historical figure. 

Amnongst them, the Place and Text Authority Records normally come in hierarchically ordered groups, e.g.
Region > Town > Building > Building Part > Multi-part artwork
Text > Chapter > Passage > Quotation

Iconography records can contain variants. In this case, there is one or more criteria, each with several options that may or may not be mutually exclusive (e.g. criterion: "with sword", options "yes", "no", "uncertain", "to be determined"). The Iconography is hence determined by the indication of an Iconography record and a list the IDS of all selected options. It is also possible to have some Criteria that appear rarely, and that have only one Option with an ID, selectedif the Criterion applies. 

Similar systems of variants would probably used for records describing elements of coats-of-arms (e.g., for different tinctures or postures of heraldic lions). Hence, they should be separate from e.g. the record of the animal 'lion' (I thought of having similarly separate records for attributes and elements of emblems, but this may not be necessary)


## Structure of Records (in theory)

Records can have the following elements:

- Attributes (names, dates, comments etc.)
- External References
- Connections to other records (containing information on the type of relationship, numbers for displaying the connections in a logical order and alternative names for previews. Some of this information is relevant for both directions of the connection, other only for one direction)

## Structure of Records (attempt to apply this structure to MongoDB)

In practical terms, most of the records will be saved as 'Node' entities, with the connections saved as 'Edge' entities so that connections can be made or broken without having to change the 'Nodes'. 

The 'records' are dissoved into a system of 'Nodes' and 'Edges'. 

A 'Node' contains
- Attributes for names, comments, etc.(list of key-value pairs, the value being a list of strings)
- Dates (each consisting of a date string for display and a start and end date as tuples for searches)
- External references (each consisting of the name of an external resource such as the GND, the ID of the object in this resource, and the URI of the record of thisobject in the resource)


An 'Edge' contains:
- Links to two 'Nodes'
- Dates (are always relevant for both directions of the connection)=
- Attributes (as above) relevant for both directions of the connection
- Attributes (as above) relevant for connection to the first 'Node' only
- Attributes (as above) relevant for connection to the second 'Node' only


## Material stored outside the database:
- Image files for display/download, in a format that allows quick display on the web and zooming in
- Image files of printed book illustrations for identifying re-uses of matrices. They have to follow specific criteria (e.g., probably b/w, relatively low res). If VISE is used for these comparison (see below) they have to be indexed in a specific way, and it is probably necessary to have a main collection and some small temporary collections that are from time to time ingested in the main collection (necessitating major reindexing). 
- Lists of permitted media, connection types etc., stored in a config file for easy access. 

# General Structure
Some functions (largely search and display) can be used by anyone, others (ingest and edit) only by registered editors. 
It may be best to have one interface, with a numer of functions blocked for non-registered users. 
Changes by registered editors should be logged (primarily for training new editors)

The following types of functions are needed:

1 Ingest Artworks

2 Create records manually

3 Fill newly created records / Edit records

4 Search for records

5 Display records

6 Export data



## Ingest
[Contents](#table-of-contents)

This is the most common way for creating records - not only artwork records, but also group and authority records connected to them. 
In nearly all cases (perhaps with the exception of [Ingest from a Museum](#ingest-from-a-museum)), newly ingested Artwork records still lack essential information and need manual filling. Hence, they should be marked as 'in progress' - they should be suppress in public searches, but editors should be able to search for these records only (in order to edit and then make them public). 
Furthermore,  Authority records ingested in this process will probably need additional information and should likewise only released once they had been manually edited (probably first thing, before the individual records). 
Especially if several editors are working on the database, it makes sense to establish ingest processes. An editor would create a new process and ingest a number of images - probably not more than a few hundred - in this process. The individual records of these images can then be filled manually and published when ready. Once the last image (and the last authority record ingested in this process) have been published, the process can be closed. 

## Ingest from local drive
[Contents](#table-of-contents)

- A number of photographs are uploaded, and Individual records are created for them. 
- The user can specify the following information:
	- If the images represent different Artworks, or several Images of one Artwork, or several Copies of one Image, or several Photos of one Copy
	- Whereabouts (Collection of Place)
	- Medium
	- Making processes (only possible, once Medium has been specified, according to medium), each can have a process type, credibility of attribution, Person, Place, and Date
- If any of the selected Persons, Places, or Collections are already in the database, Edges between them and the record are created - otherwise, Authority records for them are being ingested or created, and Edges are established with them. 
- In rare cases (e.g., lost artworks that should be recorded because copies after them are in the database), it would also be possible to create these records without uploading an actual image. In this case, there would be no Photo record (and probably also no Copy record). 

![Create](./1%20Ingest/1-1%20Ingest%20Photos/ingest_photos.png)

## Ingest from a museum
[Contents](#table-of-contents)

This function has not yet been built in the prototype - it is largely 'Zukunftsmusik' since, as of 2025, only very few museum database have APIs. Since there is currently no standard similar to IIIF, this function would probably need considerable adjustment for every museum. 

It could work as follows:
- A search is executed in the Museum Database via the API
- The results are deduplicated with the contents of the database (probably via inventory number)
- The results are displayed for manual selection
- Full information on the selected results is downloaded via the API
- Individual records are created for every imported artwork. 
- The editor goes through the imported artworks one by one (it must be possible to interrupt and resume this process): 
	- For each artwork, a search for artists and places is done in the database and, when it fails, in external resources. The editor can select the appropriate match or, if necessary, import or create new authority records. 
	- For each artwork, the iconography records from the museum database are matched with the records in the database. The editor can confirm these matches (and supply missing data, e.g. about iconographic variants), change the iconography, or delete it and add it later. 


## Ingest Photos from a library
[Contents](#table-of-contents)

- This is the most complex scenario, consisting of two, for printed images of three steps. 
- Since the second and third step necessitate going through all images one by one, they can take considerable time, hence it must be possible to interrupt and resume these processes. 
- It may make sense to have a list of all manuscripts and books currently in this process, indicating what stage theyre in, and allowing the editors to start or resume work at the appropriate place. 

### Step 1: Downloading information on the Book or Manuscript
[Contents](#table-of-contents)

- Editor enters address of an IIIF manifest
- Information from the manifest is downloaded
- (printed books only) If the manifest contains a reference to a bibliographic database, the record from this database is downloaded; if not, the editor can supply such a reference; if there is no relevant bibliographic database, the user can manually create a record
- If the manifest or the bibliographical record contain references to Collections, Persons, and Places, a search for them is done in the database and, if it fails, in external resources (e.g., GND). The editor can select the appropriate match or, if necessary, manually search and ingest or create new authority records. 
- The editor can select the text illustrated here, medium and, once the appropriate Making Processes have been determined, enter Artists, Places, and Dates in these forms. 
- Texts, Artists and Places are likewise checked against the database or, if that fails, external resources, the editor can confirm matches, launch manual searches in external databases, or manually create new authority records. 
- If any authority records are found in external resources, they will be ingested automatically. 
- A new record is ingested automatically, if there was no record found in the database but one from external resources, and if there is a record in the database, but it is only a stub. 
- If any newly ingested record contains connections to other authority records (often the case), the connected records are either imported in full, or the information in the connection is merely used to create stubs. This will depend on the type of records (e.g., persons connected to other persons will be normally imported as stubs, but places connected to a collection as full records. In addition, if there is already a stub in the database, it would be upgraded to a full record since it is apparently relevant.**)
- The results are saved as a Manuscript or Book record and a provisional record (currently called 'Pages') that contains information on the individual canvasses of the IIIF manifest as well as the entered information on illustrated texts and making process. 
![Create](./1%20Ingest/1-3%20Ingest%20Books/1-3-1%20-%20Downloading%20Information/ingest_manifest.png)

### Step 2: Creating individual image records
[Contents](#table-of-contents)


- All pages of a digitised manuscript and book are downloaded, an algorithm identifies illustrations (this also includes straightening them as necessary). 
- An editor checks and corrects these identifications (probably first as an overview, to make sure that all pages with illustrations are selected, and then by manually going through all selected pages and checking all frames). This would also include manual adjusting
- If the IIIF-Manifest does not contain page numbers, they can be added at this stage by an editor. 
- For manuscripts, the result is the creation of an Artwork, Image, and Photo record for every miniature, largely based on information in the 'Pages' record. 
- For printed books, the result is the creation of an Artwork, Image, Copy, Photo and Matrix record for every illustration, largely based on information int the 'Pages' record. 
![Create](./1%20Ingest/1-3%20Ingest%20Books/1-3-2%20-%20Creating%20individual%20records/cut_out_images.png)

### Step 3: Identifying re-used printing Matrices
[Contents](#table-of-contents)

- This step is necessary for printed book illustrations (also for any printed book illustrations ingested not via this procedure but manually under [Ingest from local drive](#ingest-from-local-drive)). It does not yet exist in the prototype.
- The images are one by one matched with the special repository of (rather low-res) images of printed book illustrations. 
- Any match is shown to the editor. 
- If the editor confirms the match, relevant information from the Matrix record of the new image is copied into the Matrix record of the match (if there are any conflicts, the editor decides which version to use), then the Matrix record of the new image is deleted, and the new image is connected to the Matrix record of the match instead. 
- The editor can further copy one reference on an illustrated text and one or more references to iconographies in the Matrix record to the Artwork and Image records respectively of the new image. (For practical reasons, this can be done whether the match was confirmed or not, simply because it is a labour-saving device). 

![Create](./1%20Ingest/1-3%20Ingest%20Books/1-3-3%20-%20Identifying%20re-used%20matrices/identify_reused_matrices.png)


# Creating Records
[Contents](#table-of-contents)

- Individual records are created through the [Ingest](#ingest) procedure above. 
> Maybe such links are nice?
- Group records are produced partially through the Ingest process (Matrix record), partially through editing (Cycle record)
- Authority records connected directly to Artwork records (Persons, Institutions, Collections, Texts) will normally be created during the ingest processes. 
- Manual creation is typically necessary for Iconography records, furthermore for some types of records of Objects of depictions that cannot be ingested from outside databases (probably Personifications, Activities), for child records of the hierarchical Place and Text records - furthermore for any Object, for which no record is found in an external resource. 
- Manual creation will also be necessary for records representing general keywords or headings. 


## Connect
[Contents](#table-of-contents)

- Most of the information is expressed through connection to other records (e.g., an Artwork is linked to records for artists and whereabouts, an Image to records for Iconography, an Iconography to records for the depicted objects). 
- The way of creating these links in manually entering data is very much standardised, hence it is described at the beginning. 
- There are three different versions: the first applies to most records, the second to records for Places and Text that exist in hierarchial chains of Child record, the third for iconographies that may also offer variants to choose from. 

### Connect simple
[Contents](#table-of-contents)

- The user starts typing in the name of the record to be connected
- Once, enough letters are typed, a search for this string (with the record type necessary in this context) is made in the database (return preview only), the result is shown in the UI (if the search has yielded results, the option 'none of these' is always added, if there are no results, an option 'external search necessary' is returned, and by default selected automatically)
- If the user selects one of the search results, it will be connected to the records
- Since external searches take several seconds, it makes most sense if the user first will in all relevant search boxes for collections and selects search results (or 'none of these')
- At the end, a search in external databases can be launched for all lists of search options, where 'none of these'or 'external search necessary' has been ticked
- The user can then select records from these search results - those would then be ingested into the database
- Alternatively, the user could manually create new records and connect them (this would mean saving the view in which the work just took place, open a view to create a new record, save it, resume work on the original view, and select a connection with the newly made record.)

![Create](./00%20general/element_insert_object.png)


### Connect Iconography
[Contents](#table-of-contents)

- The connection to Iconography records functions similar to [Connect simple](#connect-simple), with the following differences:
- The search in the database does not only yield previews, but also lists of variants for every iconography (names of variants and short names of options)
- There is no external search - if an Iconography record is not found, it has to be created manually
- Once an Iconography record has been selected (a newly created record would be selected automatically), a list of all variants is displayed
- The user selects the appropriate option for every variant.
- An Edge between the Image and the selected Iconography record is saved. 
- The IDs of any selected Options are saved as part of this Edge

![Create](./2%20%20Create%20Records/2-0-2%20Connection%20to%20Iconography/connection_to_iconography.png)

### Connect Place / Text
[Contents](#table-of-contents)

- Amongst Place and Text records, only high-level records ("Town", "Book") are ingested and supplied with data. Lowever-level records typically only consist of a name and the Edges linking them upward and downward. 
- Hence, there is a simplified way of creating these records:
- When creating a link to a Place record (in [Ingest from local drive](#ingest-from-local-drive) or [Create Iconography](#create-iconography)) or to a Text record (in [Edit manually](#edit-manually) / [Bulk editing](#bulk-editing) or[Create Iconography](#create-iconography)), one would normally search for the 'Town' or the 'Book' record. If it is in the database, it would not be displayed alone, but with all child records. The editor could select an extant Child record or insert at any place the name of a new Child record (and select the level of this record, e.g. building, building-part etc., that in turn defines the relation between it and its parent record.). These records would be saved with no other content than the name and the Edges linking it to other records. It would also be possible to open the record in a separate view to add more information, if desired. 
- This is not yet fully thought through. Some child records, especially building records, but also major subdivisions of texts (e.g., Biblical Books) may very well have external authority records that could be ingested like other Authority records, and it may also make sense that one searches for them, not for the Town or Book records (which would be rather voluminous for e.g. the City of Rome, or the Bible). 
![Create](./00%20general/element_insert_object_place_text.png)



## Create Iconography
[Contents](#table-of-contents)

- First, the type of Iconography has to be selected (Portrait, Emblem, etc.)
- Based on this type, one can enter one or more connected objects in search boxes and select the connection they have with the iconography (e..g, 'portrait of', 'acting person', etc.). The connection to or ingest or creation of these Authority records is described in \documentation\00 general\element_insert_object and element_insert_object_place_text respectively. . 
- A name (and name variants or comments) are given manually (for some types of iconography, e.g. portraits, a name will be created automatically out of type and connected objects, which, however, can still be changed manually). 
- The Iconclass notation(s) for this iconography are entered, and hence a link to Iconclass built (all Iconography records without Iconclass notations will be sent to the Iconclass editorsto consider creating notations for these Iconographies). 
- If the iconography has variants (e.g., if an image of a saint appears with different attributes), these can be catalogued. It makes sense to have two forms for entering this data - one largely filled in with simple options 'yes', 'no', 'unclear', 'not yet determined', and another that has only the last two options complete, whilst the rest can be filled in freely. If an option in one of the variants needs connections to other Object records, they can be entered as described above. (It should also be possible to combine some variants, especially attributes, also with Object records, e.g., records of saints). In this case, once a connection to an Object record is made, one could decide whether the variants connected with this person should be available in this iconography record. This needs more thinking (e.g., should the variant records be copied to the Iconography record and then adjusted or should simply links to them be available? The latter would be more elegant but may create some dispaly problems). 
- At the end, the Iconography record is saved as a Node with Edges to all connected object records. If variants are defined, probably each variant, and each option within the variants, is a separate Node. 

![Create](./2%20%20Create%20Records/2-1%20Iconography/create_iconography.png)

## Create keyword and heading records
[Contents](#table-of-contents)

- These records are very simple - in most cases, one would merely enter a name and connections to one or two parent headings (in some situations, there might be some external authority record). 

## Create other Authority records
[Contents](#table-of-contents)

This would largely happen for Persons, Organisations, Places, and Texts for which there are no external authority records - and probably for all Offices, Personifications and Activities, since there are no authority records for such concepts (unless I find some, e.g. in the Getty Data). 
- Normally, such records would be manually created as part of in [Ingest](#ingest) or in [Create Iconography](#create-iconography). In this case, one would probably store the record one had been working on in the FE, open the view to create the new record, and then resume work on the earlier record. 
- In order to create a new Authority record, one first has to select the record type, then add at least one connection to another record (with relations defined by the record type), and give it a name. 

# Fill and Edit records
[Contents](#table-of-contents)

In virtually all cases (exceptions being perhaps [records ingested from museum databases](#ingest-from-a-museum) or records that have gone through the [re-used matrix search](#step-3-identifying-re-used-printing-matrices)), new individual records need manual editing. Most important for the database is iconographic information in the Image record (although very few photos may not need it); furthermore, the Artwork record needs information on Medium, Making Processes, Whereabouts, and, where applicable, illustrated texts. 
This can be supported by special searches that show e.g. only those images in the current ingest process that have no whereabouts or specific wherabouts. 
Depending on the material, there might be several ways of achieving this - which can also be combined. 
Later editing of records - which will be comparably rare, follows the same principles

## Edit manually
[Contents](#table-of-contents)

This way of proceeding is called for if either all images need very different metadata or all fields that do not need different metadata (e.g., whereabouts, making processes) have been filled in at the [Ingest](#ingest) or through [bulk editing](#bulk-editing). 
- One goes to the first image in the current ingest process that needs to be treated and opens the edit view. This view will combine all individual records together (Artwork, Image, Copy, Photograph) - if there are more Image records to an Artwork record, orsimilar for Copy and Photograph records, one can flip between them. 
- In this record, all necessary data can be entered: 
- In the Artwork record:
	- Select medium, then relevant making processes will appear
	- For any making process select reliability of attribution ("signed", "school of", etc.) and enter  Artist or Place, and Time (if an artist is entered, there is no need to enter a place, since the preferred place of activity of the artist will be entered by default - it could be overwritten if it is incorrect in this case). 
	- Additional making processes can be added (if consistent with the medium), the order of making processes adjusted. 
	- Enter whereabouts (either a Collection or a Place - if a Place, Child records could be added, see [Connected Place - Text](#connect-place--text)).
	- Additionally, former whereabouts can be added. 
	- Enter illustrated text, if appropriate (Child records could be added). 
	- For both whereabouts and illustrated texts it may be the case that a hierarchically high-up record had already entered earlier in the ingest process, e.g., the name of a book. In this case, all child records of this record would be displayed, and one could choose (or create) the right one for this image, e.g., if the Illustrated text is set to "Bible", it could be moved for an individual Artwork record to "Bible" > "Exodus" > "Opening initial".
	-In the Image record, one or more iconographic records can be added (normally, at least one will be added). 
	- First, select reliability ("no comments", "inscription", "tentative interpretation" etc.)
	- Search and select iconography record
	- If this iconography record has variants, select the correct options (by ticking)
	- any Records (Persons, Collections, Places, Texts, Iconographies) that do not exist yet can be ingested or manually created. To do so, the Individual records would be stored and reloaded once the new record(s) have been created. 
Then, this procedure is repeated at the next record. There could be a function that does not only save the record, but also makes it public, and another that save it, makes it public, and removes it from the current ingest process. These functions should include some checking of minimum standards for publication. 

## Bulk editing
[Contents](#table-of-contents)

This procedure is useful if some information (typically, it would be whereabouts or making processes) have to be added to a number of records. If one has ingested 100 photos from a church, one might e.g. mark all the ceiling paintings and link them to the same artist and date, or mark all images from the high altar and set them to the child place 'high altar'. This function will tpically be used for new images but could also make sense if e.g. it turns out that all miniatures from a manuscript need to be redated. 
- Select the images either in the current ingest process or in search results. 
- Open the edit screen. It will look like the edit screen from [Edit manually](#edit-manually), but all fields in which the individual records have divergent content will be greyed out. 
- In this case, there is only one Image, Copy, and Photograph section in the view, not several ones to move up and down, since all changes will apply to all records. 
- If any field is filled in or changed, these changes will apply to all records that have been marked. 
- If one tries to change a greyed-out field, one receives a warning - if one discards it, all the individual contents of this field will be replaced by the new content. 

## Copy information
[Contents](#table-of-contents)

This procedure is useful for Manuscripts and Books. Often, copy of the same text have very similar images at more or less the same places. If one such manuscript or book has been fully catalogued, and a second one is ingested, the following procedure could be used. 
- Select the manuscript or book record of the model and the manuscript and book record of the new material
- Open a view with a split screen that shows the first image connected to either manuscript or book record
- If necessary, move forward on either side until both series are in sync (if the first images of the new material have no counterpart in the model, one would manually assign to them the Iconography and Illustrated Text information).
- Once both books are in sync, the following options are available
	- Copy Illustrated Text and Iconography information (with variants) and move both sides one image on
	- Copy Illustrated Text and Iconography information, but select variants for the new image manually, and move both sides on image on
	- Copy only Illustrated Text or nothing at all, if there is not match, and enter the missing information manually
	- If the series are getting out of sync, move only one side (again, if a new image has no counterpart, one should supply information manually)
	- Should the editor notice that some information in the model is incorrect, it should be possible to correct it on the spot. 
Since this procedure can take some time (in some cases, there may be several hundred images), it must be possible to interrupt and resume it. 

![Create](./3%20Edit%20Records/3-3%20Copy%20Catalogue%20Information/copy_catalogue_information.png)

## Merge individual records
[Contents](#table-of-contents)

This can be necessary if a group of photos was imported as 'different Artworks', but some of them are actually Images belonging to one and the same Artwork, or Copies belonging to one and the same Image record, or Photos belonging to one and the same Copy record. 
- In this case, one has to mark all relevant records (either in a view of a current ingest, or in a search view), select and option 'merge' and indicate if the merging should place on Artwork, Image, or Copy level. 
- If the records that are to be merged contain conflicting information, one is asked, which information to keep in the merged record
- After the merger, e.g. all Images will be connected to one Artwork record. 

It would also be relatively simple to have a function that would atomise the record, i.e. clone the Artwork, Image and Copy records so many times that every Artwork record is only connected to one Image, Copy, and Photo record (also this could be done on different levels). 

With a combination of these two functions, one could probably do all merging and separating operations that might become necessary, albeit in an awkward way. Since I expect such operations to be very rare, this might be sufficient, but one might also built something more comfortable, that would show all Image, Copy, and Photo records belonging to an Artwork as a tree, on which elements could be moved around. 


## Complete information in Authority records
[Contents](#table-of-contents)

Authority records as ingested automatically from the GND or another source often lack some information that is needed for Iconobase. This information could either be added immediately after ingesting the new record or later, before the record is made public. 

It could mean two things: 
- Determining the type of an authority record (e.g., is a depicted person a historical figure, a mythological figure, etc.I)
- Creating links to other records - e.g., a 'historical figure' must be defined by a place, a date, and a profession, however vague (or, in many cases easier, by an office and dates), an artist must have a preferred place of activity, a town must belong to a region, and an animal species to larger groups. 
- If a place of activity is assigned to an artist, all Making processes with this artist and no link to a place are to be supplied with this place or activity as place. 
This would be done through manual editing. One would probably go through all unpublished Authority records in an Ingest process, open them and be prompted which information was still missing. 

## Delete Authority Records
[Contents](#table-of-contents)
This action would be needed very rarely in production node, more common would be a merger (see below). 
- Authority records cannot be deleted, if they still have meaningful connections. 
- There are three scenarios:
  - Record has no connections at all - it can be deleted
  - Record is only connected to stubs - it can be deleted together with the stubs
  - Record of type Place or Text is only connected to Parent record (and perhaps to stubs) - it can be deleted (together with the stubs, should there be any)
  - Record is not connected to any individual or group record but to one and only one other Authority record - it can be demoted to a stub, all stubs connected to it can be deleted
  - Record is connected to two or more authority records and/or to at least on individual or Group record - it cannot be deleted nor demoted to a stub
- If the record is deleted or demoted to a stub, all stubs connected to it are deleted, as are all Edges connecting to this record. 
- If the record cannot be deleted, a list of all connected records that prevent the deletion from happening, has to be sent to the UI. 

## Merge Authority Records
[Contents](#table-of-contents)
This action would normally be used (instead of deleting above) if it became obvious that two Authority records actually denote the same thing. 
- User selects two authority records, either with search on split screen, or searching one, copying its ID, searching the other, chose 'Merge' and enter the ID of the other record. 
- A merger is only possible between two records of the same record type (e.g. two persons)
- For all Attributes of record B:
  - If an Attribute that can be repeated (e.g., variant name) exists in record B but not in record A, it is copied to record A
  - If an Attrbute that cannot be repeated (e.g., preferred name, sex, geographical coordinates) exists in both records A and B, but with different values, the user has to decide which ones to take over
- For all Edges containing the ID of record B:
  - If record B has a connection to a record and record A has a connection to the same record with the same attributes, the connection of record B is deleted
  - if record B has a connection to a record to which record A has no connection, the ID of record B in the Edge is replaced with the ID or record A
  - if both record A nad B have connections to the same authority record, but with different attributes, the user has to decide which will be used for merged record (mixing and matching of attributes allowed) - of if both connections actually mean different things, and both are to be retained - e.g. if one connects an artist and a town as 'born in' and another as 'active in' (in any connection that is to be retained, all references to record B have to be replaced with references to record A.)
  - All connections +
  - The ID of record B is added as attribute 'former ID' or so to record A (this is needed for iconography records in case that there some outside resource referred to its ID, but it may make sense to do this always)
  - The Node for record B is being deleted (all Edges leading to it should have been deleted by the steps before)


# Search
- Virtually all searches go for some elements of Authority records (e.g. works by certain artists, works in certain locations, works showing certain iconographies). ONly a search for a museum inventory number or an auction lot number would go for the Edge between an Artwork record and an Authority record (a search for a manusript shelf mark would search for the Edge between two Authority records). There might be also searches for specific IDs of individual records used when editing the database. 
- If a search is for an Authority record, it can have two intended results:
  - Firstly, the Authority record as data. It would be rather use to browse from and and see if there are other relevant Authority records, and then to display the images connected to them. 
  - Secondly, the search could go for all individual records connected to the found Authority records. Two things have to be kept in mind:
    - There may be different connections, and not all of them relevant for the search (e.g., a search for portraits of Michelangelo should not turn out works by Michelangelo) - however, it may also be that a user wants to see more than one connection (e.g., all images showing Michelangelo, be their portraits or history paintings) or simply anything connected to a certain Authority record
    - Depending on the type of connection, there may be rather different paths. A search for works of art made by Michelangelo would, for instance to search for an Person named Michelangelo that has the type 'Artist', copy its ID, and look for Artwork records that have this ID in their Making processes. A search for Images of all Types featuring Michelangelo would search for a Person named Michelangelo that has the type 'Depicted Person' (one and the same record for Michelangelo would have both types, if both works by and images of him are in the database), search for all Iconography records related to this person record and then search all Image records connected to one of these Iconography records and then show search the connected Artwork record (with a preview image of taken from that Image and Photo records that are marked as 'Preferred' for the Iconography 'Michelangelo', if there are more). A still more complex example: One might search for saints that have as attribute a candle. Here, one would first search for the object 'candle' and search for all Iconography records this record is connected to. However, one has to filter them so that all records that are not linked to Persons with the attribute 'Saint' are excluded, and one has to filter the search for Image records to those that also contain the Option ID for the variant that a 'candle' is shown. 
    - This means that one will need a UI with a number of different search boxes, and that one needs a number of different searches - some of them with recursive elements, in the BFF. 
  - In the following, some examples of searches shall be demonstrated. 