#pylint: disable=C0114,C0116
import pytest
#import pytest_asyncio
from dotenv import load_dotenv
from rich import print
from beanie import WriteRules

#import classes
import bpf.db_actions as db_actions
import bpf.parsing.parse_manifests as parse_manifests
import bpf.get_external_data as get_external_data

load_dotenv()


@pytest.mark.asyncio
async def test_get_metadata_value_by_label():
    await db_actions.initialise_beanie()
    uri="https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb00027407/manifest"
    manifest= await get_external_data.get_web_data_as_json(uri)
    metadata=manifest["metadata"]
    v=parse_manifests.get_metadata_value_by_label(metadata,"Standort")
    assert v[0] == "München, Bayerische Staatsbibliothek -- 4 Inc.c.a. 364 m"
    v=parse_manifests.get_metadata_value_by_label(metadata,"Identifikator")
    print(v)

@pytest.mark.asyncio
async def test_parse_bibliographic_ids_bsb():
    await db_actions.initialise_beanie()
    uri="https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb00027407/manifest"
    manifest= await get_external_data.get_web_data_as_json(uri)
    metadata=manifest["metadata"]
    bids=parse_manifests.parse_bibliographic_ids_bsb(metadata)
    print(bids)

@pytest.mark.asyncio
async def test_parse_manifest_herbarius():
    await db_actions.initialise_beanie()
    uri="https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb00027407/manifest"
    manifest= await get_external_data.get_web_data_as_json(uri)
    meta=parse_manifests.parse_manifests_bsb(manifest)
    await meta.save(link_rule=WriteRules.WRITE)
