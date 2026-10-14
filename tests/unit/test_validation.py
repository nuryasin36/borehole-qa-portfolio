import pytest

from app.models import ValidationError, validate_depth, validate_sample


@pytest.mark.parametrize("value, expected", [(0, 0.0), (1.5, 1.5), (10, 10.0)])
def test_validate_depth_accepts_valid_values(value, expected):
    assert validate_depth(value) == expected


@pytest.mark.parametrize("value", [-0.1, -5, "5", None, True])
def test_validate_depth_rejects_invalid_values(value):
    with pytest.raises(ValidationError):
        validate_depth(value)


def test_sample_depth_equal_to_total_is_allowed():
    sample = validate_sample({"depth": 10, "soil_type": "clay"}, total_depth=10)
    assert sample["depth"] == 10.0


def test_sample_deeper_than_borehole_is_rejected():
    with pytest.raises(ValidationError, match="must not exceed"):
        validate_sample({"depth": 12, "soil_type": "clay"}, total_depth=10)


def test_sample_unknown_soil_type_is_rejected():
    with pytest.raises(ValidationError, match="soil_type"):
        validate_sample({"depth": 2, "soil_type": "unobtainium"}, total_depth=10)


@pytest.mark.parametrize("n_value", [-1, 101, 5.5, "10"])
def test_sample_n_value_out_of_range_is_rejected(n_value):
    with pytest.raises(ValidationError):
        validate_sample(
            {"depth": 2, "soil_type": "sand", "n_value": n_value}, total_depth=10
        )
