# pylint: disable=C0115,C0303,W0212,C0116,C0302
""" "
This file contains class definitions
"""

# import json
from typing import Optional, List
import logging
import sys
from pydantic import BaseModel
from beanie import Document, UnionDoc, Link
# import inspect

logging.basicConfig(filename="general.log", level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler())
logger = logging.getLogger("asyncio")


def func_logger(func):
    """
    Logger for all function calls
    Place as annotation befor function definition
    """

    def inner(*args, **kwargs):
        caller = sys._getframe(1)
        caller_name = caller.f_globals["__name__"]
        module = sys.modules[func.__module__]
        logger.debug(
            "       DEBUG %s in %s from %s async called",
            func.__name__,
            module,
            caller_name,
        )
        ret = func(*args, **kwargs)
        # with {args, kwargs} returns {ret}
        logger.debug("       DEBUG  %s from %s done", func.__name__, caller_name)
        return ret

    return inner


def async_func_logger(func):
    """
    Logger for all function calls
    Place as annotation befor function definition
    """

    async def inner(*args, **kwargs):
        caller = sys._getframe(1)
        caller_name = caller.f_globals["__name__"]
        #        module=inspect.getmodule(func)
        module = sys.modules[func.__module__]
        logger.debug(
            "       DEBUG %s in %s from %s async called",
            func.__name__,
            module,
            caller_name,
        )
        ret = await func(*args, **kwargs)
        # with {args, kwargs} returns {ret}
        logger.debug("       DEBUG  %s from %s done", func.__name__, caller_name)
        return ret

    return inner


class Union(UnionDoc):
    class Settings:
        name = "all_collections"
        class_id = "_class_id"


class Attribute(BaseModel):
    """
    Used for most strings and list connected to Nodes and Edges
    the following keys are in use:

    for Node:
    type (can be used repeatedly for subtypes)
    name_preferred (to be used only once)
    name_variant
    sex
    comment
    raw (to be used for data imported from outside that has
    not yet checked in the database)

    for Edge (all only once):
    relationA/B
    numberA/B - Problem: that should be an int
    number (in case of a 1:n relation, e.g. numbers of pages
    sub-number (if there are several images on a page)
    previewA/B
    qualifier (e.g., 'attributed') - goes in both directions



    for Date (probably only once)
    date of activity > y/n
    (miaybe also some more in the future, otherwise replace it with logical field)
    """

    key: Optional[str] = ""
    value: Optional[str] = ""


class ExternalReference(BaseModel):
    """
    This class is used for references to external IDs in bibliographic records and in authority
    files such as the GND. It contains the name of the repertory (e.g., VD16, GND), the ID of the
    book or person within the repertory and, if available, the URI of the entry.
    """

    uri: Optional[str] = ""
    name: Optional[str] = ""
    id: Optional[str] = ""


class Date(BaseModel):
    """
    The date_string has a form for display, date_start and date_end the date for automatical searches.
    the Attribute field can be used for additional information, e.g. if it is the date of life of or
    activity of a person, and maybe it is also needed for some other features I cannot currently think about
    """

    def add_attribute(self, key, value):
        a = Attribute(key=key, value=value)
        self.attributes.append(a)

    def get_attribute(self, key):
        v = ""
        for a in self.attributes:
            if a.key == key:
                v = a.value
        return v

    attributes: Optional[list[Attribute]] = []
    date_string: Optional[str] = ""
    #    date_type : Optional[str] = ""
    # The only current plan to use it is to determinate dates of life and dates of activity of a person.
    #    I can probably omit the date_type and have a separate class for dates of persons
    date_start: Optional[tuple] = ()
    date_end: Optional[tuple] = ()


class Node(Document):
    """
    This class should be used for virtually all records
    (e.g. Artwork, Image, Copy, perhaps Photo, Manuscript, Book, Pages,
    Iconography, Person, Place, etc.)
    """

    def add_attribute(self, key, value):
        a = Attribute(key=key, value=value)
        self.attributes.append(a)

    def get_attribute(self, key):
        v = []
        for a in self.attributes:
            if a.key == key:
                v.append(a.value)
        return v

    attributes: Optional[list[Attribute]] = []
    stub: Optional[bool] = True
    external_id: Optional[List[ExternalReference]] = []
    dates: Optional[list[Date]] = []
    preview: Optional[str] = ""  # wird der gebraucht?

    #    linked_node : Optional[List[Link["Edge"]]] = []
    class Settings:
        union_doc = Union


class Edge(Document):
    """
    Connects different nodes
    """

    def add_attribute(self, key, value):
        a = Attribute(key=key, value=value)
        self.attributes.append(a)

    def get_attribute(self, key):
        v = []
        for a in self.attributes:
            if a.key == key:
                v.append(a.value)
        return v

    attributes: Optional[list[Attribute]] = []
    dates: Optional[list[Date]] = []
    nodeA: Optional[Link[Node]] = None
    nodeB: Optional[Link[Node]] = None

    class Settings:
        union_doc = Union


class NodePlus(Document):
    """
    A node with all connected edges. Problem: since the edge has the 'vectors' to both sides, they
    are both part of NodePlus, and so every display has to make sure that only the right one is
    being displayed.
    """

    node: Optional[Link[Node]] = None
    edges: Optional[List[Link[Edge]]] = []
    nodes_plus: Optional[List[Link["NodePlus"]]] = []
