"""Tests that describe the EXPECTED behaviour for open defects.

They are marked xfail(strict=True): they fail today because the bug exists.
When a bug is fixed the test starts passing, strict mode turns that into a
failure, and the xfail marker must be removed. See README "Defects found".
"""
import pytest

VALID_BH = {"name": "BH-01", "latitude": -6.3, "longitude": 107.1, "total_depth": 10}


def _post_raw(client, url, raw_json):
    return client.post(url, data=raw_json, content_type="application/json")


@pytest.mark.xfail(strict=True, reason="BUG-01: NaN total_depth is accepted")
def test_bh12_nan_total_depth_returns_400(client):
    r = _post_raw(client, "/api/boreholes",
                  '{"name":"A","latitude":1,"longitude":1,"total_depth":NaN}')
    assert r.status_code == 400


@pytest.mark.xfail(strict=True, reason="BUG-02: Infinity total_depth is accepted")
def test_bh13_infinite_total_depth_returns_400(client):
    r = _post_raw(client, "/api/boreholes",
                  '{"name":"A","latitude":1,"longitude":1,"total_depth":Infinity}')
    assert r.status_code == 400


@pytest.mark.xfail(strict=True, reason="BUG-03: NaN sample depth is accepted")
def test_sm09_nan_sample_depth_returns_400(client):
    client.post("/api/boreholes", json=VALID_BH)
    r = _post_raw(client, "/api/boreholes/1/samples", '{"depth":NaN,"soil_type":"clay"}')
    assert r.status_code == 400


@pytest.mark.xfail(strict=True, reason="BUG-04: form accepts 'nan' as total depth")
def test_ui03_form_rejects_nan_depth(client):
    r = client.post("/", data={"name": "F", "latitude": "1",
                               "longitude": "1", "total_depth": "nan"})
    assert "saved" not in r.get_data(as_text=True)


@pytest.mark.xfail(strict=True, reason="BUG-05: duplicate borehole names are allowed")
def test_bh14_duplicate_name_returns_409(client):
    client.post("/api/boreholes", json=VALID_BH)
    assert client.post("/api/boreholes", json=VALID_BH).status_code == 409


@pytest.mark.xfail(strict=True, reason="BUG-06: no maximum length on borehole name")
def test_bh15_overlong_name_returns_400(client):
    r = client.post("/api/boreholes", json={**VALID_BH, "name": "x" * 5000})
    assert r.status_code == 400


@pytest.mark.xfail(strict=True, reason="BUG-07: soil_type is case-sensitive")
def test_sm11_soil_type_is_case_insensitive(client):
    client.post("/api/boreholes", json=VALID_BH)
    r = client.post("/api/boreholes/1/samples", json={"depth": 1, "soil_type": "Clay"})
    assert r.status_code == 201
