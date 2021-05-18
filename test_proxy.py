"""
Testing of format.py functions.
"""

import proxy
import utils
import pytest

HOSTNAME = "https://data.aussda.at"
TEST_DATASET = "doi:10.11587/BQVSOW"

# @pytest.fixture
def oai_ddi_file():
    from pyDataverse.api import NativeApi

    api = NativeApi(base_url=HOSTNAME)

    resp = api.get_dataset_export(pid=TEST_DATASET, export_format="oai_ddi")
    assert resp.status_code == 200


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


def test_oai_only_valid():
    url = "api/access/datafile/216/metadata/ddi"
    assert proxy.place_request(url, None) == None
