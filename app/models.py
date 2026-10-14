"""Validation rules for borehole and sample data."""

SOIL_TYPES = {"clay", "silt", "sand", "gravel", "peat", "fill"}


class ValidationError(ValueError):
    pass


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_depth(value, field="depth"):
    if not _is_number(value):
        raise ValidationError(f"{field} must be a number")
    if value < 0:
        raise ValidationError(f"{field} must not be negative")
    return float(value)


def validate_borehole(data):
    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValidationError("name is required")

    lat = data.get("latitude")
    lon = data.get("longitude")
    if not _is_number(lat):
        raise ValidationError("latitude must be a number")
    if not -90 <= lat <= 90:
        raise ValidationError("latitude out of range")
    if not _is_number(lon):
        raise ValidationError("longitude must be a number")
    if not -180 <= lon <= 180:
        raise ValidationError("longitude out of range")

    total = validate_depth(data.get("total_depth"), "total_depth")
    if total == 0:
        raise ValidationError("total_depth must be greater than 0")

    return {
        "name": name.strip(),
        "latitude": float(lat),
        "longitude": float(lon),
        "total_depth": total,
    }


def validate_sample(data, total_depth):
    depth = validate_depth(data.get("depth"))
    if depth > total_depth:
        raise ValidationError("depth must not exceed borehole total_depth")

    soil = data.get("soil_type")
    if soil not in SOIL_TYPES:
        raise ValidationError("soil_type is not supported")

    n_value = data.get("n_value")
    if n_value is not None:
        if isinstance(n_value, bool) or not isinstance(n_value, int):
            raise ValidationError("n_value must be an integer")
        if not 0 <= n_value <= 100:
            raise ValidationError("n_value out of range (0-100)")

    return {"depth": depth, "soil_type": soil, "n_value": n_value}
