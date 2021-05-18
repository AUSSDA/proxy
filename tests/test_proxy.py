"""
Testing of proxy.py functions.
"""

import proxy
import utils
import pytest
import requests

@pytest.fixture
def oai_ddi_test_file():
    test_dataset = "doi:10.11587/BQVSOW"
    return f"oai?verb=GetRecord&metadataPrefix=oai_ddi&identifier={test_dataset}"

@pytest.fixture
def validate_cessda():
    pass

def test_yield_num_mandatory_rules_mono():
    from collections import Counter

    rules = [r for r in utils.gen_rules()]
    assert len(rules) == 10


def test_yield_num_optional_rules_mono():
    from collections import Counter

    rules = [r for r in utils.gen_rules(constraint="Optional")]
    assert len(rules) == 12


def test_yield_num_mandatory_rules():
    from collections import Counter

    rules = [r for r in utils.gen_rules(profile="cdc25_profile.xml")]
    assert len(rules) == 22


def test_invalid_url():
    url = "api/access/datafile/216/metadata/ddi"
    assert proxy.place_request(url, None) == None


def test_valid_url():
    assert proxy.place_request(oai_ddi_test_file, None) == None

def test_valid_formatting():
    pass
