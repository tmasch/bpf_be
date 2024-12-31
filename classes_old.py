class InvalidDateException(Exception):
    """
    \todo
    """


class InvalidMonthException(Exception):
    """
    \todo
    """

class InvalidDayException(Exception):
    """
    \todo
    """

class InvalidDateStringException(Exception):
    """
    \todo
    """

class InvalidDateRangeException(Exception):
    """
    \todo
    """

class PersonAgainstDuplication(BaseModel):
    """
    \todo
    """
# I have these classes here and not in 'classes' because they are only needed in these functions.
    preview : Optional[str] = ""
#    id : Optional[str] = ""
    person_type1 : Optional[list[str]]  = []

class OrgAgainstDuplication(BaseModel):
    """
    \todo
    """
    preview : Optional[str] = ""
#    id : Optional[str] = ""
    org_type1 : Optional[list[str]]  = []

class PlaceAgainstDuplication(BaseModel):
    """
    \todo
    """
    preview : Optional[str] = ""
#    id : Optional[str] = ""
    place_type1 : Optional[list[str]]  = []


# class Record(BaseModel):
#     """
# \todo
#     """
#     type : str = ""
#     identifier : str = ""
#     metadata : Optional[Metadata] = ""
#     book : Optional[BookDb] = ""
#     organisation : Optional[OrganisationDb] = ""
#     person : Optional[Person] = ""
#     pages : Optional[PagesDb] = ""
#     place : Optional[PlaceDb] = ""






# class ConnectedEntityDbDisplay(BaseModel):
#     """
# This class is for the links of persons, organisations and places to book records
#     """
# #    id : Optional[str] = ""
#     role : Optional[str] = ""
#     preview : Optional[str] = ""




# class PersonImport(BaseModel):
#     """
#     Person class for importing
#     """
#     external_id : Optional[list[ExternalId]] = []
#     internal_id : Optional[str] = ""
#     internal_id_person_type1 : Optional[list[str]] = []
#     internal_id_person_type1_comment : Optional[str] = ""
#     name_preferred : Optional[str] = ""
#     name_variant : Optional[list[str]] = []
#     sex : Optional[str] = ""
#     dates_from_source : Optional[list[DateImport]] = []
#     datestring : Optional[str] = ""
#     date_start : Optional[tuple] = ()
#     date_end : Optional[tuple] = ()
#     date_aspect : Optional[str] = ""
#     connected_persons : Optional[list[ConnectedEntity]] = []
#     connected_organisations : Optional[list[ConnectedEntity]] = []
#     connected_locations : Optional[list[ConnectedEntity]] = []
#     comments : Optional[str] = ""
#     preview : Optional[str] = ""


# class Organisation(Document):
#     """
#  This class is used for references to organisations (publishing houses) in book records. 
#  id is the id of the place in authority files (currently, the GND), name the name given the source
#  and role either "pub" for the publisher, or "prt" for the printer
#  If an organisation is both, there will be two different record for it. 
#     """
# #    id : Optional[str] = ""
#     external_id : Optional[list[ExternalReference]] = []
#     internal_id : Optional[str] = ""
#     internal_id_org_type1 : Optional[list[str]] = []
#     internal_id_org_type1_needed : Optional[str] = ""
#     internal_id_org_type1_comment : Optional[str] = ""
#     name_preferred : Optional[str] = ""
#     name_variant : Optional[list[str]] = []
#     dates_from_source : Optional[list[DateImport]] = []
# #    connected_persons : Optional[list[ConnectedEntity]] = []
#  #   connected_organisations : Optional[list[ConnectedEntity]] = []
#  #   connected_locations : Optional[list[ConnectedEntity]] = []
#     comments : Optional[str] = ""
#     preview : Optional[str] = ""
#     id_name : Optional[str] = ""
#     internal_id : Optional[str] = ""
#     internal_id_preview : Optional[str] = ""
#     internal_id_org_type1 : Optional[list[str]] = []
#     internal_id_org_type1_needed : Optional[str] = ""
#     internal_id_org_type1_comment : Optional[str] = ""
#     name : Optional[str] = ""
# #    role : Optional[str] = ""
# #    chosen_candidate : Optional[int] = ""
#     #potential_candidates : Optional[list[Organisation]] = []
#     new_authority_id : Optional[str] = ""
# #    id : Optional[str] = ""
#     type : Optional[str] = ""  # Is always "Organisation"
#     org_type1: Optional[list[str]] = []
#     # Types 1 are: "Printer", "Collection", "Group of Persons"
#     org_type2: Optional[list[str]] = []
#     # Type 21 is a subtype only needed if type1 is "Group of Persons",
#     #  it would be e.g. 'Guild', 'Monastery', 'Ruling Body'
#     class Settings:
#         union_doc = Union
#     # def __init__(self,name):
#     #     super.__init__()
#     #     self.name=name



# #@dataclass
# class PersonDb(Document):
#     """
# This class is for entering Person authority records into the database. 
# It contains all needed fields (or better, will do so), so many will remain empty. 
# I hope it will be possible to delete empty fields when turning it into a dict object. 
# If not, one should probably have different classes for different 
#     """
#     id : Optional[str] = ""
#     type : Optional[str] = "" # Is always 'Person'
#     person_type1 : Optional[list[str]] = []
#     # Types 1 are: "Author", "Printer", "Artist", "Depicted Person"
#     person_type2 : Optional[list[str]] = []
#     # Type 2 is a subtype only needed if type1 is "depicted Person"
#     person_type3 : Optional[list[str]] = []
#     # Type 3 is a subtype only needed if typ2 is "Saint"
#     external_id : Optional[list[ExternalId]] = []
#     name_preferred : Optional[str] = ""
#     name_variant : Optional[list[str]] = []
#     sex : Optional[str] = ""
#     dates_from_source : Optional[list[DateImport]] = []
#     # This is only provisional - there will be some functions to turn the dates
#     # from import into standardised dates
#     connected_persons : Optional[list[ConnectedEntity]] = []
#     connected_organisations : Optional[list[ConnectedEntity]] = []
#     connected_locations : Optional[list[ConnectedEntity]] = []
#     comments : Optional[str] = ""
#     # At least two fields are still missing, they are not needed at this step but
#     #  will be needed for records of the type1 "depicted Person":
#     # 'Office' and 'Profession' (one would preferably give an office (in the widest sense)
#     #  together with a term, and, if the person held no office, a profession)
#     class Settings:
#         union_doc = Union



# class OrganisationImport(BaseModel):
#     """
#  This class is used for importing data on organisations from authority records such as the GND
#     """
#     external_id : Optional[list[ExternalReference]] = []
#     internal_id : Optional[str] = ""
#     internal_id_org_type1 : Optional[list[str]] = []
#     internal_id_org_type1_needed : Optional[str] = ""
#     internal_id_org_type1_comment : Optional[str] = ""
#     name_preferred : Optional[str] = ""
#     name_variant : Optional[list[str]] = []
#     dates_from_source : Optional[list[DateImport]] = []
#     connected_persons : Optional[list[ConnectedEntity]] = []
#     connected_organisations : Optional[list[ConnectedEntity]] = []
#     connected_locations : Optional[list[ConnectedEntity]] = []
#     comments : Optional[str] = ""
#     preview : Optional[str] = ""

# class Organisation(Document):
#     """
#  This class is used for references to organisations (publishing houses) in book records. 
#  id is the id of the place in authority files (currently, the GND), name the name given the source
#  and role either "pub" for the publisher, or "prt" for the printer
#  If an organisation is both, there will be two different record for it. 
#     """
# #    id : Optional[str] = ""
#     external_id : Optional[list[ExternalReference]] = []
#     internal_id : Optional[str] = ""
#     internal_id_org_type1 : Optional[list[str]] = []
#     internal_id_org_type1_needed : Optional[str] = ""
#     internal_id_org_type1_comment : Optional[str] = ""
#     name_preferred : Optional[str] = ""
#     name_variant : Optional[list[str]] = []
#     dates_from_source : Optional[list[DateImport]] = []
# #    connected_persons : Optional[list[ConnectedEntity]] = []
#  #   connected_organisations : Optional[list[ConnectedEntity]] = []
#  #   connected_locations : Optional[list[ConnectedEntity]] = []
#     comments : Optional[str] = ""
#     preview : Optional[str] = ""
#     id_name : Optional[str] = ""
#     internal_id : Optional[str] = ""
#     internal_id_preview : Optional[str] = ""
#     internal_id_org_type1 : Optional[list[str]] = []
#     internal_id_org_type1_needed : Optional[str] = ""
#     internal_id_org_type1_comment : Optional[str] = ""
#     name : Optional[str] = ""
# #    role : Optional[str] = ""
# #    chosen_candidate : Optional[int] = ""
#     #potential_candidates : Optional[list[Organisation]] = []
#     new_authority_id : Optional[str] = ""
# #    id : Optional[str] = ""
#     type : Optional[str] = ""  # Is always "Organisation"
#     org_type1: Optional[list[str]] = []
#     # Types 1 are: "Printer", "Collection", "Group of Persons"
#     org_type2: Optional[list[str]] = []
#     # Type 21 is a subtype only needed if type1 is "Group of Persons",
#     #  it would be e.g. 'Guild', 'Monastery', 'Ruling Body'
#     external_id : Optional[list[ExternalReference]] = []
#     name_preferred : Optional[str] = ""
#     name_variant : Optional[list[str]] = []
#     dates_from_source : Optional[list[DateImport]] = []
#     # This is only provisional - there will be some functions to turn the dates
#     #  from import into standardised dates
# #    connected_persons : Optional[list[ConnectedEntity]] = []
# #    connected_organisations : Optional[list[ConnectedEntity]] = []
# #    connected_locations : Optional[list[ConnectedEntity]] = []
#     comments : Optional[str] = ""
#     class Settings:
#         union_doc = Union



# class PlaceImport(BaseModel):
#     """
#  This class is used for importing data on places from authority records such as the GND    
#     """
#     external_id : Optional[list[ExternalReference]] = []
#     internal_id : Optional[str] = ""
#     internal_id_place_type1 : Optional[list[str]] = []
#     internal_id_place_type1_comment : Optional[str] = ""
#     # I will need that field later, when I extend the search for matching types also do
#     # name searches in Iconobase
#     name_preferred : Optional[str] = ""
#     name_variant : Optional[list[str]] = []
#     coordinates : Optional[list[Coordinates]] = []
#     dates_from_source : Optional[list[DateImport]] = []
#     connected_persons : Optional[list[ConnectedEntity]] = []
#     connected_organisations : Optional[list[ConnectedEntity]] = []
#     connected_locations : Optional[list[ConnectedEntity]] = []
#     comments : Optional[str] = ""
#     preview : Optional[str] = ""

# class Place(Document):
#     """
#  This class is used for references to places (virtually alwys towns) in book records.
#  id is the id of the place in authority files (currently, the GND), name the name given the source
#  and role either "mfp" for the place of printing, or "pup" for the place of publishing. 
#  If a place is both, there will be two different record for it. 
#     """
#     external_id : Optional[list[ExternalReference]] = []
#     internal_id : Optional[str] = ""
#     internal_id_place_type1 : Optional[list[str]] = []
#     internal_id_place_type1_comment : Optional[str] = ""
#     # I will need that field later, when I extend the search for matching types also do
#     # name searches in Iconobase
#     name_preferred : Optional[str] = ""
#     name_variant : Optional[list[str]] = []
#     coordinates : Optional[list[Coordinates]] = []
#     dates_from_source : Optional[list[DateImport]] = []
# #    connected_persons : Optional[list[ConnectedEntity]] = []
# #    connected_organisations : Optional[list[ConnectedEntity]] = []
# #    connected_locations : Optional[list[ConnectedEntity]] = []
#     comments : Optional[str] = ""
#     preview : Optional[str] = ""
# #    id : Optional[str] = ""
# #    id_name : Optional[str] = ""
#     internal_id : Optional[str] = ""
#     internal_id_preview : Optional[str] = ""
#     internal_id_place_type1 : Optional[list[str]] = []
#     internal_id_place_type1_needed : Optional[str] = ""
#     internal_id_place_type1_comment : Optional[str] = ""
#     name : Optional[str] = ""
# #    role : Optional[str] = ""
# #    chosen_candidate : Optional[int] = ""
# #    potential_candidates : Optional[list[PlaceImport]] = []
#     new_authority_id : Optional[str] = ""
# #    id : Optional[str] = ""
#     type : Optional[str] = "" # Is always "Place"
#     place_type1 : Optional[list[str]] = []
#     # Types 1 are: "Region - historical", "Region - modern", "Town - historical",
#     # "Town - modern", "Building", "Building-part"
#     # There should be only one place_type1 per record, but I keep it as list for the sake of
#     # consistency
#     external_id : Optional[list[ExternalReference]] = []
#     name_preferred : Optional[str] = ""
#     name_variant : Optional[list[str]] = []
#     coordinates : Optional[list[Coordinates]] = []
#     dates_from_source : Optional[list[DateImport]] = []
#     # This is only provisional - there will be some functions to turn the dates from import into
#     # standardised dates
# #    connected_persons : Optional[list[ConnectedEntity]] = []
# #    connected_organisations : Optional[list[ConnectedEntity]] = []
# #    connected_locations : Optional[list[ConnectedEntity]] = []
#     comments : Optional[str] = ""
#     class Settings:
#         union_doc = Union


# class OrganisationDb(Document):
#     """
# This class is for entering Organisation authority records into the database. 
#     """
#     id : Optional[str] = ""
#     type : Optional[str] = ""  # Is always "Organisation"
#     org_type1: Optional[list[str]] = []
#     # Types 1 are: "Printer", "Collection", "Group of Persons"
#     org_type2: Optional[list[str]] = []
#     # Type 21 is a subtype only needed if type1 is "Group of Persons",
#     #  it would be e.g. 'Guild', 'Monastery', 'Ruling Body'
#     external_id : Optional[list[ExternalReference]] = []
#     name_preferred : Optional[str] = ""
#     name_variant : Optional[list[str]] = []
#     dates_from_source : Optional[list[DateImport]] = []
#     # This is only provisional - there will be some functions to turn the dates
#     #  from import into standardised dates
#     connected_persons : Optional[list[ConnectedEntity]] = []
#     connected_organisations : Optional[list[ConnectedEntity]] = []
#     connected_locations : Optional[list[ConnectedEntity]] = []
#     comments : Optional[str] = ""
#     class Settings:
#         union_doc = Union


# class PlaceDb(Document):
#     """
# This class is for entering Place authority records into the database
#     """
#     id : Optional[str] = ""
#     type : Optional[str] = "" # Is always "Place"
#     place_type1 : Optional[list[str]] = ""
#     # Types 1 are: "Region - historical", "Region - modern", "Town - historical",
#     # "Town - modern", "Building", "Building-part"
#     # There should be only one place_type1 per record, but I keep it as list for the sake of
#     # consistency
#     external_id : Optional[list[ExternalReference]] = []
#     name_preferred : Optional[str] = ""
#     name_variant : Optional[list[str]] = []
#     coordinates : Optional[list[Coordinates]] = []
#     dates_from_source : Optional[list[DateImport]] = []
#     # This is only provisional - there will be some functions to turn the dates from import into
#     # standardised dates
#     connected_persons : Optional[list[ConnectedEntity]] = []
#     connected_organisations : Optional[list[ConnectedEntity]] = []
#     connected_locations : Optional[list[ConnectedEntity]] = []
#     comments : Optional[str] = ""
#     class Settings:
#         union_doc = Union







# class PersonAndConnections(Document):
#     id : str = ""
#     comment : Optional[str] = ""
#     person : Link[Person] = None
#     connected_persons : Optional[List[Link[ConnectedEntity]]] = []
# #    connected_places : Optional[list[Link[ConnectedEntity]]] = []
# #    connected_organisations : Optional[list[Link[ConnectedEntity]]] = []
#     class Settings:
#         union_doc = Union

# class SelectionCandidate(BaseModel):
#     chosen_candidate : Optional[int] = 0
#     person : Optional[Person] = None
#     person_candidates : Optional[list[Person]] = []
#     place : Optional[Place] = None
#     place_candidates : Optional[list[Place]] = []
#     organisation : Optional[Organisation] = None
#     organisation_candidates : Optional[list[Organisation]] = []

# class MakingProcess(BaseModel):
#     """
#     Making process
#     """
#     process_number : Optional[int] = 0
#     process_type : Optional[str] = ""
#     process_qualifier : Optional[str] = ""
#     person : Optional[Person] = None
#     place : Optional[Place] = None
#     date : Optional[DateImport] = None



# class ConnectedRecord(BaseModel):
#     """
# Class for linked Persons, Organsations, Places
#     """
#     id : Optional[str] = ""
#     role : Optional[str] = ""
#     name : Optional[str] = "" # This field is only a stopgap measure, if
#     person : Optional[Link[Person]] = None
#     organisation : Optional[Link[OrganisationDb]] = None
#     place : Optional[Link[PlaceDb]] = None


# class BookDbDisplay(BaseModel):
#     """
# This class is for displaying (and perhaps later also for editing) book records from the database
#     """
#     id : Optional[str] = ""
#     type : Optional[str] = "Book"
#     bibliographic_id : Optional[list[ExternalReference]] = []
#     persons : Optional[list [ConnectedEntityDbDisplay]] = []
#     organisations : Optional[list [ConnectedEntityDbDisplay]] = []
#     places : Optional[list [ConnectedEntityDbDisplay]] = []
#     title: Optional[str] = ""
#     volume_number : Optional[str] = ""
#     part_title : Optional[str] = ""
#     printing_date : Optional[str] = "" # Has to be later replaced with a date object
#     date_string : Optional[str] = ""
#     date_start : Optional[tuple] = ()
#     date_end : Optional[tuple] = ()
#     preview : Optional[str] = ""
#     # This preview is to be shown in lists of titles
#     # - I am not sure if it will be needed long-term

# class PreviewListDb(BaseModel):
#     """
# This class is for displaying preview and id of all manuscripts and books in Iconobase.
# It is made only as a provisional measure for display purposes, but a similar function could 
# be used to access all manuscripts and books still in the ingest process
#     """
#     id : Optional[str] = ""
#     type : Optional[str] = ""
#     preview : Optional[str] = ""
#     name_preferred : Optional[str] = ""
#     title : Optional[str] = ""



# class LinkToRepositoryDisplay(BaseModel):
#     """
# This class is used for displaying (and later also editing) the link between manuscripts 
# and repositories into the database. 
# It can probably be later also used for the link between artworks and repositories
#     """
#     number : Optional[int] = 0
#     #This is only needed if several former locations are added later so that they can
#     # show in a sensible order (probably back in time)
#     place_id : Optional[str] = ""
#     current : Optional[bool] = True
#     collection : Optional[bool] = True
#     # This field will be set to 'true' if the place has the type "Organisation"
#     # and the type_org1 "Collection", it will be set to 'false' if the place has the type 'Place'
#     # The purpose of this field is to simplify searches.
#     id_preferred : Optional[str] = "" # Inventory number of shelf mark
#     id_variant : Optional[list[str]] = []
#     preview : Optional[str]


# class ManuscriptDbDisplay(BaseModel):
#     """
# This class is for displaying (and perhaps later also for editing) manuscript records 
# from the database
#     """
#     id : Optional[str] = ""
#     type : Optional[str] = "Manuscript" # is always "Manuscript"
#     repository : Optional[list[LinkToRepositoryDisplay]] = []
#     preview : Optional[str] = ""
#     # This preview is to be shown in lists of titles - I
#  am not sure if it will be needed long-term


# class PersonDbDisplay(BaseModel):
#     """
# This class is for displaying (and perhaps later also for editing) person records from the database
#     """
#     id : Optional[str] = ""
#     type : Optional[str] = "" # Is always 'Person'
#     person_type1 : Optional[list[str]] = []
#     # Types 1 are: "Author", "Printer", "Artist", "Depicted Person"
#     person_type2 : Optional[list[str]] = []
#     # Type 2 is a subtype only needed if type1 is "depicted Person"
#     person_type3 : Optional[list[str]] = []
#     # Type 3 is a subtype only needed if typ2 is "Saint"
#     external_id : Optional[list[ExternalId]] = []
#     name_preferred : Optional[str] = ""
#     name_variant : Optional[list[str]] = []
#     sex : Optional[str] = ""
#     dates_from_source : Optional[list[DateImport]] = []
#     # This is only provisional - there will be some functions to turn the
#     # dates from import into standardised dates
#     connected_persons : Optional[list[ConnectedEntity]] = []
#     connected_organisations : Optional[list[ConnectedEntity]] = []
#     connected_locations : Optional[list[ConnectedEntity]] = []
#     comments : Optional[str] = ""

# class OrgDbDisplay(BaseModel):
#     """
# This class is for displaying (and perhaps later also for editing) Organisation 
# authority records from the database. 
#     """
#     id : Optional[str] = ""
#     type : Optional[str] = ""  # Is always "Organisation"
#     org_type1: Optional[list[str]] = [] # Types 1 are: "Printer", "Collection", "Group of Persons"
#     org_type2: Optional[list[str]] = []
#     # Type 21 is a subtype only needed if type1 is "Group of Persons",
#     # it would be e.g. 'Guild', 'Monastery', 'Ruling Body'
#     external_id : Optional[list[ExternalReference]] = []
#     name_preferred : Optional[str] = ""
#     name_variant : Optional[list[str]] = []
#     dates_from_source : Optional[list[DateImport]] = []
#     # This is only provisional - there will be some functions to turn the dates
#     # from import into standardised dates
#     connected_persons : Optional[list[ConnectedEntity]] = []
#     connected_organisations : Optional[list[ConnectedEntity]] = []
#     connected_locations : Optional[list[ConnectedEntity]] = []
#     comments : Optional[str] = ""

# class PlaceDbDisplay(BaseModel):
#     """
# This class is for displaying (and perhaps later also editing) Place authority records 
# from the database
#     """
#     id : Optional[str] = ""
#     type : Optional[str] = "" # Is always "Place"
#     place_type1 : Optional[list[str]] = ""
#     # Types 1 are: "Region - historical", "Region - modern", "Town - historical",
#     #  "Town - modern", "Building", "Building-part"
#     # There should be only one place_type1 per record, but I keep it as list for
#     # the sake of consistency
#     external_id : Optional[list[ExternalReference]] = []
#     name_preferred : Optional[str] = ""
#     name_variant : Optional[list[str]] = []
#     coordinates : Optional[list[Coordinates]] = []
#     dates_from_source : Optional[list[DateImport]] = []
#     # This is only provisional - there will be some functions to turn the
#     # dates from import into standardised dates
#     connected_persons : Optional[list[ConnectedEntity]] = []
#     connected_organisations : Optional[list[ConnectedEntity]] = []
#     connected_locations : Optional[list[ConnectedEntity]] = []
#     comments : Optional[str] = ""


class Entity(Document):
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
    gnd_id : Optional[str] = ""
#    id_name : Optional[str] = ""
    stub : Optional[bool] = True
    attributes : Optional[list[Attribute]] = []
#    internal_id : Optional[str] = ""
#    internal_id_person_type1 : Optional[list[str]] = []
#    internal_id_person_type1_needed : Optional[str] = ""
#    internal_id_person_type1_comment : Optional[str] = ""
#    internal_id_preview : Optional[str] = ""
    name : Optional[str] = ""
    new_authority_id : Optional[str] = ""
    external_id : Optional[list[ExternalReference]] = []
    internal_id : Optional[str] = ""
#    internal_id_person_type1 : Optional[list[str]] = []
#    internal_id_person_type1_comment : Optional[str] = ""
    name_preferred : Optional[str] = ""
    name_variant : Optional[list[str]] = []
#    sex : Optional[str] = ""
    dates_from_source : Optional[list[DateImport]] = []
    datestring : Optional[str] = ""
    date_start : Optional[tuple] = ()
    date_end : Optional[tuple] = ()
    date_aspect : Optional[str] = ""
    #model_config = ConfigDict(arbitrary_types_allowed=True)
#    id : Optional[str] = ""
#    role : Optional[str] = ""
#    chosen_candidate : Optional[int] = ""
#    potential_candidates : Optional[list[Person]] = []
#    connected_persons : Optional[list[ConnectedEntity]] = []
#    connected_organisations : Optional[list[ConnectedEntity]] = []
#    connected_locations : Optional[list[ConnectedEntity]] = []
    comments : Optional[str] = ""
    preview : Optional[str] = ""
#    id : Optional[str] = ""
    type : Optional[str] = "" # Is always 'Person'
#    properties : Optional[dict] = {}
#    person_type1 : Optional[list[str]] = []
    # Types 1 are: "Author", "Printer", "Artist", "Depicted Person"
#    person_type2 : Optional[list[str]] = []
    # Type 2 is a subtype only needed if type1 is "depicted Person"
#    person_type3 : Optional[list[str]] = []
    # Type 3 is a subtype only needed if typ2 is "Saint"
#    external_id : Optional[list[ExternalId]] = []
#    name_preferred : Optional[str] = ""
#    name_variant : Optional[list[str]] = []
#    sex : Optional[str] = ""
#    dates_from_source : Optional[list[DateImport]] = []
    # This is only provisional - there will be some functions to turn the dates
    # from import into standardised dates
#    connected_persons : Optional[list[ConnectedEntity]] = []
#    connected_organisations : Optional[list[ConnectedEntity]] = []
#    connected_locations : Optional[list[ConnectedEntity]] = []
#    comments : Optional[str] = ""
    # At least two fields are still missing, they are not needed at this step but
    #  will be needed for records of the type1 "depicted Person":
    # 'Office' and 'Profession' (one would preferably give an office (in the widest sense)
    #  together with a term, and, if the person held no office, a profession)
#    id : Optional[str] = ""
#    type : Optional[str] = "" # Is always 'Person'
#    person_type1 : Optional[list[str]] = []
    # Types 1 are: "Author", "Printer", "Artist", "Depicted Person"
#    person_type2 : Optional[list[str]] = []
 #   # Type 2 is a subtype only needed if type1 is "depicted Person"
 #   person_type3 : Optional[list[str]] = []
    # Type 3 is a subtype only needed if typ2 is "Saint"
#    external_id : Optional[list[ExternalId]] = []
#    name_preferred : Optional[str] = ""
#    name_variant : Optional[list[str]] = []
#    sex : Optional[str] = ""
#    dates_from_source : Optional[list[DateImport]] = []
    # This is only provisional - there will be some functions to turn the
    # dates from import into standardised dates
#    connected_persons : Optional[list[ConnectedEntity]] = []
#    connected_organisations : Optional[list[ConnectedEntity]] = []
#    connected_locations : Optional[list[ConnectedEntity]] = []
#    comments : Optional[str] = ""
    class Settings:
        union_doc = Union
