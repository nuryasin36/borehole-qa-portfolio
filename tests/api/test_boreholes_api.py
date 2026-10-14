"""API tests for borehole and sample endpoints. IDs map to docs/test_cases.md."""
import pytest

VALID_BH = {"name": "BH-01", "latitude": -6.3, "longitude": 107.1, "total_depth": 10}


def _create_borehole(client, payload=None):
    return client.post("/api/boreholes", json=payload or VALID_BH)


# ---------- Boreholes ----------

def test_bh01_create_borehole_returns_201_and_id(client):
    r = _create_borehole(client)
    assert r.status_code == 201
    body = r.get_json()
    assert body["id"] == 1
    assert body["name"] == "BH-01"


@pytest.mark.parametrize("name", ["", "   "])
def test_bh02_bh03_blank_name_returns_400(client, name):
    r = _create_borehole(client, {**VALID_BH, "name": name})
    assert r.status_code == 400
    assert "name" in r.get_json()["error"]


@pytest.mark.parametrize("lat", [95, -90.1])
def test_bh04_latitude_out_of_range_returns_400(client, lat):
    assert _create_borehole(client, {**VALID_BH, "latitude": lat}).status_code == 400


@pytest.mark.parametrize("lat", [90, -90])
def test_bh05_latitude_boundaries_are_accepted(client, lat):
    assert _create_borehole(client, {**VALID_BH, "latitude": lat}).status_code == 201


def test_bh06_longitude_out_of_range_returns_400(client):
    assert _create_borehole(client, {**VALID_BH, "longitude": 181}).status_code == 400


@pytest.mark.parametrize("depth", [0, -1])
def test_bh07_bh08_zero_or_negative_total_depth_returns_400(client, depth):
    assert _create_borehole(client, {**VALID_BH, "total_depth": depth}).status_code == 400


def test_bh09_non_json_body_returns_400(client):
    r = client.post("/api/boreholes", data="not json", content_type="application/json")
    assert r.status_code == 400


def test_bh10_get_existing_borehole_returns_200(client):
    _create_borehole(client)
    r = client.get("/api/boreholes/1")
    assert r.status_code == 200
    assert r.get_json()["total_depth"] == 10.0


def test_bh11_get_unknown_borehole_returns_404(client):
    assert client.get("/api/boreholes/999").status_code == 404


# ---------- Samples ----------

def test_sm01_create_valid_sample_returns_201(client):
    _create_borehole(client)
    r = client.post(
        "/api/boreholes/1/samples",
        json={"depth": 3, "soil_type": "clay", "n_value": 12},
    )
    assert r.status_code == 201
    assert r.get_json()["borehole_id"] == 1


def test_sm02_sample_at_exact_total_depth_is_accepted(client):
    _create_borehole(client)
    r = client.post("/api/boreholes/1/samples", json={"depth": 10, "soil_type": "sand"})
    assert r.status_code == 201


def test_sm03_sample_deeper_than_borehole_returns_400(client):
    _create_borehole(client)
    r = client.post("/api/boreholes/1/samples", json={"depth": 12, "soil_type": "clay"})
    assert r.status_code == 400


def test_sm04_negative_sample_depth_returns_400(client):
    _create_borehole(client)
    r = client.post("/api/boreholes/1/samples", json={"depth": -1, "soil_type": "clay"})
    assert r.status_code == 400


def test_sm05_unknown_soil_type_returns_400(client):
    _create_borehole(client)
    r = client.post("/api/boreholes/1/samples", json={"depth": 1, "soil_type": "rock"})
    assert r.status_code == 400


@pytest.mark.parametrize("n_value, expected", [(0, 201), (100, 201), (-1, 400), (101, 400)])
def test_sm06_n_value_boundaries(client, n_value, expected):
    _create_borehole(client)
    r = client.post(
        "/api/boreholes/1/samples",
        json={"depth": 1, "soil_type": "sand", "n_value": n_value},
    )
    assert r.status_code == expected


@pytest.mark.parametrize("n_value", [5.5, "10"])
def test_sm07_non_integer_n_value_returns_400(client, n_value):
    _create_borehole(client)
    r = client.post(
        "/api/boreholes/1/samples",
        json={"depth": 1, "soil_type": "sand", "n_value": n_value},
    )
    assert r.status_code == 400


def test_sm08_sample_on_unknown_borehole_returns_404(client):
    r = client.post("/api/boreholes/999/samples", json={"depth": 1, "soil_type": "sand"})
    assert r.status_code == 404


def test_sm10_delete_sample_then_second_delete_returns_404(client):
    _create_borehole(client)
    client.post("/api/boreholes/1/samples", json={"depth": 1, "soil_type": "sand"})
    assert client.delete("/api/samples/1").status_code == 204
    assert client.delete("/api/samples/1").status_code == 404
