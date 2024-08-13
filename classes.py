""""
This file contains class definitions
"""
from typing import Optional
from pydantic import BaseModel
import bson
#from datetime import date



class Frame(BaseModel):
    """
    Class frame
    """
    def __str__(self):
        t="Index: "+str(self.index)+"\n"
        return t
    def to_json(self):
        """ Returns class as json """
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)
    id : Optional[str] = ""
    index : Optional[int] = ""
    x_abs : Optional[int] = ""
    y_abs : Optional[int] = ""
    w_abs : Optional[int] = ""
    h_abs : Optional[int] = ""
    x_rel : Optional[float] = ""
    y_rel : Optional[float] = ""
    w_rel : Optional[float] = ""
    h_rel : Optional[float] = ""

class Image(BaseModel):
    """
    Image class
    """
    def __str__(self):
        t="Index: "+str(self.index)+"\n"
        return t
    index : Optional[int] = ""
    label_raw :  Optional[str] = ""
    label_volume : Optional[str] = ""
    label_prefix : Optional[str] = ""
    label_page : Optional[str] = ""
    width : Optional[int] = ""
    height : Optional[int] = ""
    baseurl : Optional[str] = ""
    format : Optional[str] = ""
    label : Optional[str] = ""
    frames : Optional[list[Frame]] = []

class ExternalId(BaseModel):
    """
This class is used for references to external IDs in bibliographic records and in authority 
files such as the GND. It contains the name of the repertory (e.g., VD16, GND), the ID of the 
book or person within the repertory and, if available, the URI of the entry. 
    """
    uri : Optional[str] = ""
    name : Optional[str] = ""
    id : Optional[str] = ""

class ConnectedEntity(BaseModel):
    """
    Class 
    """
    id : Optional[str] = ""
    external_id : Optional[list[ExternalId]] = []
    name : Optional[str] = ""
    connection_type : Optional[str] = ""
# In the GND; the role of a connected person must be given through an abbrevation
# that gives rather general information, e.g. "bezf" = "family relation";
# more detailed information can be given in a comment field
    connection_comment : Optional[str] = ""
    connection_time : Optional[str] = ""

class DateImport(BaseModel):
    """
This class is used for the import of dates of life or activity of persons. 
Currently, it is still saved in the database, but eventually it will be replaced with a 
class Date_person
    """
    datestring_raw : Optional[str] = ""
    date_comments : Optional[str] = ""
    datetype : Optional[str] = ""
    datestring : Optional[str] = ""
    date_start : Optional[tuple] = ()
    date_end : Optional[tuple] = ()
    date_aspect : Optional[str] = ""

class Date(BaseModel):
    """
    Date class
    """
    date_string : Optional[str] = ""
#    date_type : Optional[str] = ""
# The only current plan to use it is to determinate dates of life and dates of activity of a person.
#    I can probably omit the date_type and have a separate class for dates of persons
    date_start : Optional[tuple] = ()
    date_end : Optional[tuple] = ()


class PersonImport(BaseModel):
    """
    Person class for importing
    """
    external_id : Optional[list[ExternalId]] = []
    internal_id : Optional[str] = ""
    internal_id_person_type1 : Optional[list[str]] = []
    internal_id_person_type1_comment : Optional[str] = ""
    name_preferred : Optional[str] = ""
    name_variant : Optional[list[str]] = []
    sex : Optional[str] = ""
    dates_from_source : Optional[list[DateImport]] = []
    datestring : Optional[str] = ""
    date_start : Optional[tuple] = ()
    date_end : Optional[tuple] = ()
    date_aspect : Optional[str] = ""
    connected_persons : Optional[list[ConnectedEntity]] = []
    connected_organisations : Optional[list[ConnectedEntity]] = []
    connected_locations : Optional[list[ConnectedEntity]] = []
    comments : Optional[str] = ""
    preview : Optional[str] = ""


class Person(BaseModel):
    """
 This class is used for references to persons in book records. 
 id is the id of the person in authority files (currently, the GND), name the name given in the 
 source and role the person's role in making the book, according to standard bibliographical 
 abbreviations, e.g. "prt" for printer. If the person's ID (GND, ULAN etc.) is found to already 
 have a record in the database, internal_id and internal_id_preview are filled. If the person's 
 name is searched in the database, or if the person's ID or name is searched in an external 
 repository such as the GND,
 The results will be put into the field 'potential candidates'. 
 The user can pick one of them (or confirm if only one was found)
    """
    #model_config = ConfigDict(arbitrary_types_allowed=True)
    id : Optional[str] = ""
    id_name : Optional[str] = ""
    internal_id : Optional[str] = ""
    internal_id_person_type1 : Optional[list[str]] = []
    internal_id_person_type1_needed : Optional[str] = ""
    internal_id_person_type1_comment : Optional[str] = ""
    internal_id_preview : Optional[str] = ""
    name : Optional[str] = ""
    role : Optional[str] = ""
    chosen_candidate : Optional[int] = ""
    potential_candidates : Optional[list[PersonImport]] = []

class OrganisationImport(BaseModel):
    """
 This class is used for importing data on organisations from authority records such as the GND
    """
    external_id : Optional[list[ExternalId]] = []
    internal_id : Optional[str] = ""
    internal_id_org_type1 : Optional[list[str]] = []
    internal_id_org_type1_needed : Optional[str] = ""
    internal_id_org_type1_comment : Optional[str] = ""
    name_preferred : Optional[str] = ""
    name_variant : Optional[list[str]] = []
    dates_from_source : Optional[list[DateImport]] = []
    connected_persons : Optional[list[ConnectedEntity]] = []
    connected_organisations : Optional[list[ConnectedEntity]] = []
    connected_locations : Optional[list[ConnectedEntity]] = []
    comments : Optional[str] = ""
    preview : Optional[str] = ""

class Organisation(BaseModel):
    """
 This class is used for references to organisations (publishing houses) in book records. 
 id is the id of the place in authority files (currently, the GND), name the name given the source
 and role either "pub" for the publisher, or "prt" for the printer
 If an organisation is both, there will be two different record for it. 
    """
    id : Optional[str] = ""
    id_name : Optional[str] = ""
    internal_id : Optional[str] = ""
    internal_id_preview : Optional[str] = ""
    internal_id_org_type1 : Optional[list[str]] = []
    internal_id_org_type1_needed : Optional[str] = ""
    internal_id_org_type1_comment : Optional[str] = ""
    name : Optional[str] = ""
    role : Optional[str] = ""
    chosen_candidate : Optional[int] = ""
    potential_candidates : Optional[list[OrganisationImport]] = []

class Coordinates(BaseModel):
    """
This class is used for importing coordinates from the GND, it may be usable more 
generally for handling this date
    """
    west : Optional[str] = ""
    east : Optional[str] = ""
    north : Optional[str] = ""
    south : Optional[str] = ""

class PlaceImport(BaseModel):
    """
 This class is used for importing data on places from authority records such as the GND    
    """
    external_id : Optional[list[ExternalId]] = []
    internal_id : Optional[str] = ""
    internal_id_place_type1 : Optional[list[str]] = []
    internal_id_place_type1_comment : Optional[str] = ""
    # I will need that field later, when I extend the search for matching types also do
    # name searches in Iconobase
    name_preferred : Optional[str] = ""
    name_variant : Optional[list[str]] = []
    coordinates : Optional[list[Coordinates]] = []
    dates_from_source : Optional[list[DateImport]] = []
    connected_persons : Optional[list[ConnectedEntity]] = []
    connected_organisations : Optional[list[ConnectedEntity]] = []
    connected_locations : Optional[list[ConnectedEntity]] = []
    comments : Optional[str] = ""
    preview : Optional[str] = ""

class Place(BaseModel):
    """
 This class is used for references to places (virtually alwys towns) in book records.
 id is the id of the place in authority files (currently, the GND), name the name given the source
 and role either "mfp" for the place of printing, or "pup" for the place of publishing. 
 If a place is both, there will be two different record for it. 
    """
    id : Optional[str] = ""
    id_name : Optional[str] = ""
    internal_id : Optional[str] = ""
    internal_id_preview : Optional[str] = ""
    internal_id_place_type1 : Optional[list[str]] = []
    internal_id_place_type1_needed : Optional[str] = ""
    internal_id_place_type1_comment : Optional[str] = ""
    name : Optional[str] = ""
    role : Optional[str] = ""
    chosen_candidate : Optional[int] = ""
    potential_candidates : Optional[list[PlaceImport]] = []

class BibliographicId(BaseModel):
    """
Here, the name is the name of the repertory (e.g., VD16), the id the id of a book in the repertory
and the uri the uri of the record of the book in the repertory.
This class should be superseded everywhere by External_id, I keep it for the moment just to be sure
    """
    uri : Optional[str] = ""
    name : Optional[str] = ""
    id : Optional[str] = ""

class BibliographicInformation(BaseModel):
    """
    Class bibliograpic information
    """
#    model_config = ConfigDict(arbitrary_types_allowed=True)
    bibliographic_id : Optional[list[ExternalId]] = []
    persons : Optional[list [Person]] = []
    organisations : Optional[list [Organisation]] = []
    places : Optional[list [Place]] = []
    title: Optional[str] = ""
    volume_number : Optional[str] = ""
    part_title : Optional[str] = ""
    printing_date : Optional[str] = "" # This will be later replaced
    date_string : Optional[str] = ""
    date_start : Optional[tuple] = ()
    date_end : Optional[tuple] = ()
    printing_information : Optional[str] = ""

class MakingProcess(BaseModel):
    """
    Making process
    """
    process_number : Optional[int] = 0
    process_type : Optional[str] = ""
    process_qualifier : Optional[str] = ""
    person : Optional[Person] = None
    place : Optional[Place] = None
    date : Optional[DateImport] = None

class Metadata(BaseModel):
    """
    Metadata
    """
#    model_config = ConfigDict(arbitrary_types_allowed=True)
#    def __str__(self):
#        t="ID:"+self.id+"\n"
#        #t=t+"title: "+self.title+"\n"
#        t=t+"location: "+self.location+"\n"
#        t=t+"markxml: "+self.markxml+"\n"
#        t=t+"number of images: "+str(self.numberOfImages)+"\n"
#        t=t+"IIIF url"+self.iiifUrl
#        t=t+"Manifest"+self.manifest
#        return(t)
    type : Optional[str] = "Manifest"
    id : Optional[str] = ""
    material : Optional[str] = ""
    repository : Optional[list[Organisation]] = []
    shelfmark : Optional[str] = ""
    license : Optional[str] = ""
    bibliographic_id : Optional[list[ExternalId]] = []
    bibliographic_information : Optional[list[BibliographicInformation]] = []
    location : Optional[str] = ""
    markxml : Optional[str] = ""
    numberOfImages : Optional[int] = ""
    iiifUrl : Optional[str] = ""
    manifest : Optional[str] = ""
    images : Optional[list[Image]] = []
    title : Optional[str] = ""
    making_processes : Optional[list[MakingProcess]] = []



class PersonDb(BaseModel):
    """
This class is for entering Person authority records into the database. 
It contains all needed fields (or better, will do so), so many will remain empty. 
I hope it will be possible to delete empty fields when turning it into a dict object. 
If not, one should probably have different classes for different 
    """
    id : Optional[str] = ""
    type : Optional[str] = "" # Is always 'Person'
    person_type1 : Optional[list[str]] = []
    # Types 1 are: "Author", "Printer", "Artist", "Depicted Person"
    person_type2 : Optional[list[str]] = []
    # Type 2 is a subtype only needed if type1 is "depicted Person"
    person_type3 : Optional[list[str]] = []
    # Type 3 is a subtype only needed if typ2 is "Saint"
    external_id : Optional[list[ExternalId]] = []
    name_preferred : Optional[str] = ""
    name_variant : Optional[list[str]] = []
    sex : Optional[str] = ""
    dates_from_source : Optional[list[DateImport]] = []
    # This is only provisional - there will be some functions to turn the dates
    # from import into standardised dates
    connected_persons : Optional[list[ConnectedEntity]] = []
    connected_organisations : Optional[list[ConnectedEntity]] = []
    connected_locations : Optional[list[ConnectedEntity]] = []
    comments : Optional[str] = ""
    # At least two fields are still missing, they are not needed at this step but
    #  will be needed for records of the type1 "depicted Person":
    # 'Office' and 'Profession' (one would preferably give an office (in the widest sense)
    #  together with a term, and, if the person held no office, a profession)



class OrganisationDb(BaseModel):
    """
This class is for entering Organisation authority records into the database. 
    """
    id : Optional[str] = ""
    type : Optional[str] = ""  # Is always "Organisation"
    org_type1: Optional[list[str]] = []
    # Types 1 are: "Printer", "Collection", "Group of Persons"
    org_type2: Optional[list[str]] = []
    # Type 21 is a subtype only needed if type1 is "Group of Persons",
    #  it would be e.g. 'Guild', 'Monastery', 'Ruling Body'
    external_id : Optional[list[ExternalId]] = []
    name_preferred : Optional[str] = ""
    name_variant : Optional[list[str]] = []
    dates_from_source : Optional[list[DateImport]] = []
    # This is only provisional - there will be some functions to turn the dates
    #  from import into standardised dates
    connected_persons : Optional[list[ConnectedEntity]] = []
    connected_organisations : Optional[list[ConnectedEntity]] = []
    connected_locations : Optional[list[ConnectedEntity]] = []
    comments : Optional[str] = ""


class PlaceDb(BaseModel):
    """
This class is for entering Place authority records into the database
    """
    id : Optional[str] = ""
    type : Optional[str] = "" # Is always "Place"
    place_type1 : Optional[list[str]] = ""
    # Types 1 are: "Region - historical", "Region - modern", "Town - historical",
    # "Town - modern", "Building", "Building-part"
    # There should be only one place_type1 per record, but I keep it as list for the sake of
    # consistency
    external_id : Optional[list[ExternalId]] = []
    name_preferred : Optional[str] = ""
    name_variant : Optional[list[str]] = []
    coordinates : Optional[list[Coordinates]] = []
    dates_from_source : Optional[list[DateImport]] = []
    # This is only provisional - there will be some functions to turn the dates from import into
    # standardised dates
    connected_persons : Optional[list[ConnectedEntity]] = []
    connected_organisations : Optional[list[ConnectedEntity]] = []
    connected_locations : Optional[list[ConnectedEntity]] = []
    comments : Optional[str] = ""


class LinkToRepository(BaseModel):
    """
This class is used for entering the link between manuscripts and repositories into the database.
It can probably be later also used for the link between artworks and repositories
    """
    number : Optional[int] = 0
    #This is only needed if several former locations are added later so that they can
    # show in a sensible order (probably back in time)
    place_id : Optional[str] = ""
    current : Optional[bool] = True
    collection : Optional[bool] = True
    # This field will be set to 'true' if the place has the type "Organisation" and t
    # he type_org1 "Collection", it will be set to 'false' if the place has the type 'Place'
    # The purpose of this field is to simplify searches.
    id_preferred : Optional[str] = "" # Inventory number of shelf mark
    id_variant : Optional[list[str]] = []



class ManuscriptDb(BaseModel):
    """
This class is for entering Manuscript records into the database
    """
    id : Optional[str] = ""
    type : Optional[str] = "Manuscript" # is always "Manuscript"
    repository : Optional[list[LinkToRepository]] = []
    preview : Optional[str] = ""
    # This preview is to be shown in lists of titles
    # - I am not sure if it will be needed long-term

class BookConnectedEntityDb(BaseModel):
    """
This class is for the links of persons, organisations and places to book records
    """
    id : Optional[str] = ""
    role : Optional[str] = ""
    name : Optional[str] = "" # This field is only a stopgap measure, if


class BookDb(BaseModel):
    """
This class is for entering Book records into the database
    """
    id : Optional[str] = ""
    type : Optional[str] = "Book"
    bibliographic_id : Optional[list[ExternalId]] = []
    persons : Optional[list [BookConnectedEntityDb]] = []
    organisations : Optional[list [BookConnectedEntityDb]] = []
    places : Optional[list [BookConnectedEntityDb]] = []
    title: Optional[str] = ""
    volume_number : Optional[str] = ""
    part_title : Optional[str] = ""
    printing_date : Optional[str] = "" # Has to be later replaced with a date object
    date_string : Optional[str] = ""
    date_start : Optional[tuple] = ()
    date_end : Optional[tuple] = ()
    preview : Optional[str] = ""
    # This preview is to be shown in lists of titles
    # - I am not sure if it will be needed long-term


class PagesDb(BaseModel):
    """
This class is for entering a record that contains information that will be later 
needed for the individual Artwork and Photograph records
    """
    id: Optional[str] = ""
    book_record_id : Optional[str] = ""
    type : Optional[str] = "Pages"
    repository : Optional[str] = ""
    shelfmark : Optional[str] = ""
    license : Optional[str] = ""
    numberOfImages : Optional[int] = 0
    images : Optional[list[Image]] = []
    preview : Optional[str] = ""
    making_processes : Optional[list[MakingProcess]] = []

class PreviewListDb(BaseModel):
    """
This class is for displaying preview and id of all manuscripts and books in Iconobase.
It is made only as a provisional measure for display purposes, but a similar function could 
be used to access all manuscripts and books still in the ingest process
    """
    id : Optional[str] = ""
    type : Optional[str] = ""
    preview : Optional[str] = ""



class ConnectedEntityDbDisplay(BaseModel):
    """
This class is for the links of persons, organisations and places to book records
    """
    id : Optional[str] = ""
    role : Optional[str] = ""
    preview : Optional[str] = ""


class BookDbDisplay(BaseModel):
    """
This class is for displaying (and perhaps later also for editing) book records from the database
    """
    id : Optional[str] = ""
    type : Optional[str] = "Book"
    bibliographic_id : Optional[list[ExternalId]] = []
    persons : Optional[list [ConnectedEntityDbDisplay]] = []
    organisations : Optional[list [ConnectedEntityDbDisplay]] = []
    places : Optional[list [ConnectedEntityDbDisplay]] = []
    title: Optional[str] = ""
    volume_number : Optional[str] = ""
    part_title : Optional[str] = ""
    printing_date : Optional[str] = "" # Has to be later replaced with a date object
    date_string : Optional[str] = ""
    date_start : Optional[tuple] = ()
    date_end : Optional[tuple] = ()
    preview : Optional[str] = ""
    # This preview is to be shown in lists of titles
    # - I am not sure if it will be needed long-term

class LinkToRepositoryDisplay(BaseModel):
    """
This class is used for displaying (and later also editing) the link between manuscripts 
and repositories into the database. 
It can probably be later also used for the link between artworks and repositories
    """
    number : Optional[int] = 0
    #This is only needed if several former locations are added later so that they can
    # show in a sensible order (probably back in time)
    place_id : Optional[str] = ""
    current : Optional[bool] = True
    collection : Optional[bool] = True
    # This field will be set to 'true' if the place has the type "Organisation"
    # and the type_org1 "Collection", it will be set to 'false' if the place has the type 'Place'
    # The purpose of this field is to simplify searches.
    id_preferred : Optional[str] = "" # Inventory number of shelf mark
    id_variant : Optional[list[str]] = []
    preview : Optional[str]


class ManuscriptDbDisplay(BaseModel):
    """
This class is for displaying (and perhaps later also for editing) manuscript records 
from the database
    """
    id : Optional[str] = ""
    type : Optional[str] = "Manuscript" # is always "Manuscript"
    repository : Optional[list[LinkToRepositoryDisplay]] = []
    preview : Optional[str] = ""
    # This preview is to be shown in lists of titles - I am not sure if it will be needed long-term


class PersonDbDisplay(BaseModel):
    """
This class is for displaying (and perhaps later also for editing) person records from the database
    """
    id : Optional[str] = ""
    type : Optional[str] = "" # Is always 'Person'
    person_type1 : Optional[list[str]] = []
    # Types 1 are: "Author", "Printer", "Artist", "Depicted Person"
    person_type2 : Optional[list[str]] = []
    # Type 2 is a subtype only needed if type1 is "depicted Person"
    person_type3 : Optional[list[str]] = []
    # Type 3 is a subtype only needed if typ2 is "Saint"
    external_id : Optional[list[ExternalId]] = []
    name_preferred : Optional[str] = ""
    name_variant : Optional[list[str]] = []
    sex : Optional[str] = ""
    dates_from_source : Optional[list[DateImport]] = []
    # This is only provisional - there will be some functions to turn the
    # dates from import into standardised dates
    connected_persons : Optional[list[ConnectedEntity]] = []
    connected_organisations : Optional[list[ConnectedEntity]] = []
    connected_locations : Optional[list[ConnectedEntity]] = []
    comments : Optional[str] = ""

class OrgDbDisplay(BaseModel):
    """
This class is for displaying (and perhaps later also for editing) Organisation 
authority records from the database. 
    """
    id : Optional[str] = ""
    type : Optional[str] = ""  # Is always "Organisation"
    org_type1: Optional[list[str]] = [] # Types 1 are: "Printer", "Collection", "Group of Persons"
    org_type2: Optional[list[str]] = []
    # Type 21 is a subtype only needed if type1 is "Group of Persons",
    # it would be e.g. 'Guild', 'Monastery', 'Ruling Body'
    external_id : Optional[list[ExternalId]] = []
    name_preferred : Optional[str] = ""
    name_variant : Optional[list[str]] = []
    dates_from_source : Optional[list[DateImport]] = []
    # This is only provisional - there will be some functions to turn the dates
    # from import into standardised dates
    connected_persons : Optional[list[ConnectedEntity]] = []
    connected_organisations : Optional[list[ConnectedEntity]] = []
    connected_locations : Optional[list[ConnectedEntity]] = []
    comments : Optional[str] = ""

class PlaceDbDisplay(BaseModel):
    """
This class is for displaying (and perhaps later also editing) Place authority records 
from the database
    """
    id : Optional[str] = ""
    type : Optional[str] = "" # Is always "Place"
    place_type1 : Optional[list[str]] = ""
    # Types 1 are: "Region - historical", "Region - modern", "Town - historical",
    #  "Town - modern", "Building", "Building-part"
    # There should be only one place_type1 per record, but I keep it as list for
    # the sake of consistency
    external_id : Optional[list[ExternalId]] = []
    name_preferred : Optional[str] = ""
    name_variant : Optional[list[str]] = []
    coordinates : Optional[list[Coordinates]] = []
    dates_from_source : Optional[list[DateImport]] = []
    # This is only provisional - there will be some functions to turn the
    # dates from import into standardised dates
    connected_persons : Optional[list[ConnectedEntity]] = []
    connected_organisations : Optional[list[ConnectedEntity]] = []
    connected_locations : Optional[list[ConnectedEntity]] = []
    comments : Optional[str] = ""
