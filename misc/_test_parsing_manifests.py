import json
import asyncio
import src.parsing.parse_manifests as parse_manifests
import src.db_actions as db_actions
import pytest
import pytest_asyncio

def test_parse_bsb_ink():
    f = open(r"testdata\manifests\bsb_ink_1.json", "r")
    mock_json = json.load(f)
    asyncio.run(db_actions.initialise_beanie())
    m = parse_manifests.parse_manifests_bsb(mock_json)
    print("Printing Test Result")
    print(m.repository)
    print(m.shelfmark)
    assert m.numberOfImages == 318
    assert m.type == "Manifest"
    assert m.shelfmark == "4 Inc.c.a. 364 m"
    assert m.repository[0].name == "München, Bayerische Staatsbibliothek "

def test_parse_bsb_ms_1():
    f = open(r"testdata\manifests\bsb_ms_1.json", "r")
    mock_json = json.load(f)
    asyncio.run(db_actions.initialise_beanie())
    m = parse_manifests.parse_manifests_bsb(mock_json)
    print("Printing Test Result")
    print(m.repository)
    print(m.shelfmark)
    assert m.numberOfImages == 208
    assert m.type == "Manifest"
    assert m.shelfmark == "Th.ex.o.455#2"
    assert m.repository[0].name == "Bamberg, Staatsbibliothek "



def test_parse_bsb_vd16_1():
    f = open(r"testdata\manifests\bsb_vd16_1.json", "r")
    mock_json = json.load(f)
    asyncio.run(db_actions.initialise_beanie())
    m = parse_manifests.parse_manifests_bsb(mock_json)
    print("Printing Test Result")
    print(m.repository)
    print(m.shelfmark)
    assert m.numberOfImages == 208
    assert m.type == "Manifest"
    assert m.shelfmark == "Th.ex.o.455#2"
    assert m.repository[0].name == "Bamberg, Staatsbibliothek "

def test_parse_bsb_vd17_1():
    f = open(r"testdata\manifests\bsb_vd17_1.json", "r")
    mock_json = json.load(f)
    asyncio.run(db_actions.initialise_beanie())
    m = parse_manifests.parse_manifests_bsb(mock_json)
    print("Printing Test Result")
    print(m.repository)
    print(m.shelfmark)
    assert m.numberOfImages == 208
    assert m.type == "Manifest"
    assert m.shelfmark == "Th.ex.o.455#2"
    assert m.repository[0].name == "Bamberg, Staatsbibliothek "



def test_parse_ecodices_1():
    f = open(r"testdata\manifests\ecodices_1.json", "r")
    mock_json = json.load(f)
    asyncio.run(db_actions.initialise_beanie())
    m = parse_manifests.parse_manifests_bsb(mock_json)
    print("Printing Test Result")
    print(m.repository)
    print(m.shelfmark)
    assert m.numberOfImages == 208
    assert m.type == "Manifest"
    assert m.shelfmark == "Th.ex.o.455#2"
    assert m.repository[0].name == "Bamberg, Staatsbibliothek "
