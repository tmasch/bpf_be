"""
Testing of classes
"""
import pytest
from dotenv import load_dotenv
from beanie import WriteRules

import classes
import db_actions
#def test_frame_

load_dotenv()

def test_frame_json():
    """ Class Frame, Test of to_json method """
    frame=classes.Frame()
    # frame.id="abc"
    s=frame.to_json()
    print(s)
    assert isinstance(s,str)

@pytest.mark.asyncio
async def test_external_reference():
    await db_actions.initialise_beanie()
    er=classes.ExternalReference(name="test")
    er.model_dump()

@pytest.mark.asyncio
async def test_person():
    await db_actions.initialise_beanie()
    p=classes.Person(name="asdf")
    p.model_dump()
    await p.save()

@pytest.mark.asyncio
async def test_entity_connection():
    await db_actions.initialise_beanie()
    p=classes.Person(name="test")
    ec=classes.EntityConnection(name="test")
    ec.person=p
    ec.model_dump()
    await ec.save(link_rule=WriteRules.WRITE)


@pytest.mark.asyncio
async def test_entity_and_connections():
    await db_actions.initialise_beanie()
    eac=classes.EntityAndConnections(name="test")

    p=classes.Person(name="test")
    eac.person=p
    eac.model_dump()
    p1=classes.Person(name="t1")
    ec1=classes.EntityConnection(name="t1")
    ec1.person=p1
    eac.connected_persons.append(ec1)

    p2=classes.Person(name="t2")
    ec2=classes.EntityConnection(name="t2")
    ec2.person=p2
    eac.connected_persons.append(ec2)

    eac.model_dump()
    await eac.save(link_rule=WriteRules.WRITE)

@pytest.mark.asyncio
async def test_role():
    await db_actions.initialise_beanie()
    r=classes.Role(name="test")

    eac=classes.EntityAndConnections(name="test")

    p=classes.Person(name="test")
    eac.person=p
    eac.model_dump()
    p1=classes.Person(name="t1")
    ec1=classes.EntityConnection(name="t1")
    ec1.person=p1
    eac.connected_persons.append(ec1)

    p2=classes.Person(name="t2")
    ec2=classes.EntityConnection(name="t2")
    ec2.person=p2
    eac.connected_persons.append(ec2)
    classes.Role.model_validate(r)
    r.entity_and_connections=eac
    r.model_dump()
    await r.save(link_rule=WriteRules.WRITE)


@pytest.mark.asyncio
async def test_bibliograpic_information():
    await db_actions.initialise_beanie()
    bi=classes.BibliographicInformation(title="test")
    r=classes.Role(name="test")

    eac=classes.EntityAndConnections(name="test")

    p=classes.Person(name="test")
    eac.person=p
    eac.model_dump()
    p1=classes.Person(name="t1")
    ec1=classes.EntityConnection(name="t1")
    ec1.person=p1
    eac.connected_persons.append(ec1)

    p2=classes.Person(name="t2")
    ec2=classes.EntityConnection(name="t2")
    ec2.person=p2
    eac.connected_persons.append(ec2)
    r.entity_and_connections=eac

    bi.persons.append(r)
    classes.BibliographicInformation.model_validate(bi)
    bi.model_dump()
    await bi.save(link_rule=WriteRules.WRITE)




