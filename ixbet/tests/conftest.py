import json

import pytest
from _pytest.logging import LogCaptureFixture


# override caplog fixture to have json property
@pytest.fixture
def caplog(caplog):
    LogCaptureFixture.json = property(lambda c: [json.loads(m.replace('\'', '"')) for m in c.messages])
    return caplog


@pytest.fixture
def top_matches(shared_datadir):
    return json.loads((shared_datadir / 'top_matches.json').read_text())


@pytest.fixture
def coefs(shared_datadir):
    return json.loads((shared_datadir / 'coefs.json').read_text())
