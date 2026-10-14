from flask import Blueprint, current_app, jsonify, render_template, request

from app.models import ValidationError, validate_borehole, validate_sample

bp = Blueprint("main", __name__)


def _store():
    return current_app.extensions["store"]


def _next_id(kind):
    counters = _store()["counters"]
    counters[kind] += 1
    return counters[kind]


def _create_borehole(data):
    bid = _next_id("borehole")
    bh = {"id": bid, **data}
    _store()["boreholes"][bid] = bh
    return bh


@bp.errorhandler(ValidationError)
def handle_validation_error(err):
    return jsonify(error=str(err)), 400


def _coerce_form(raw):
    """Form values arrive as strings; convert numeric fields when possible."""
    out = dict(raw)
    for key in ("latitude", "longitude", "total_depth"):
        try:
            out[key] = float(raw[key])
        except (TypeError, ValueError):
            pass  # leave as-is, validation will report it
    return out


# ---------- Simple form page ----------

@bp.route("/", methods=["GET", "POST"])
def index():
    result = error = None
    if request.method == "POST":
        raw = {
            "name": request.form.get("name"),
            "latitude": request.form.get("latitude"),
            "longitude": request.form.get("longitude"),
            "total_depth": request.form.get("total_depth"),
        }
        try:
            result = _create_borehole(validate_borehole(_coerce_form(raw)))
        except ValidationError as err:
            error = str(err)
    return render_template("index.html", result=result, error=error)


# ---------- JSON API ----------

@bp.post("/api/boreholes")
def create_borehole():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="JSON object required"), 400
    return jsonify(_create_borehole(validate_borehole(data))), 201


@bp.get("/api/boreholes")
def list_boreholes():
    return jsonify(list(_store()["boreholes"].values()))


@bp.get("/api/boreholes/<int:bid>")
def get_borehole(bid):
    bh = _store()["boreholes"].get(bid)
    if bh is None:
        return jsonify(error="borehole not found"), 404
    return jsonify(bh)


@bp.post("/api/boreholes/<int:bid>/samples")
def create_sample(bid):
    bh = _store()["boreholes"].get(bid)
    if bh is None:
        return jsonify(error="borehole not found"), 404
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="JSON object required"), 400
    sample = validate_sample(data, bh["total_depth"])
    sid = _next_id("sample")
    record = {"id": sid, "borehole_id": bid, **sample}
    _store()["samples"][sid] = record
    return jsonify(record), 201


@bp.get("/api/boreholes/<int:bid>/samples")
def list_samples(bid):
    if bid not in _store()["boreholes"]:
        return jsonify(error="borehole not found"), 404
    return jsonify(
        [s for s in _store()["samples"].values() if s["borehole_id"] == bid]
    )


@bp.delete("/api/samples/<int:sid>")
def delete_sample(sid):
    if _store()["samples"].pop(sid, None) is None:
        return jsonify(error="sample not found"), 404
    return "", 204
