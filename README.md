# Borehole Logging API – QA Portfolio

![tests](https://github.com/nuryasin36/borehole-qa-portfolio/actions/workflows/tests.yml/badge.svg)

A small geotechnical-style Flask API (boreholes and SPT samples) with a full QA layer: test plan, test cases, a three-level automated suite, and a defect log. Built as a portfolio project; it is not a copy of any commercial product.

## What this shows

- Test planning and test case design (equivalence partitioning, boundary values, error guessing)
- API testing of status codes, response bodies, and validation rules
- A test pyramid with pytest (unit, API) and Playwright (end-to-end)
- Defect reporting, with each open bug locked in by a `strict xfail` test
- CI on GitHub Actions

## How it was built

This project was built with an AI-assisted workflow. I used Claude to scaffold the application and draft tests, then reviewed, ran, and adjusted the test plan, test cases, and automation myself. Exploratory testing of edge cases (special float values, long strings, HTML input) produced the defects below.

## Project structure

```
app/            Flask API, validation rules, entry form
tests/unit/     validation functions in isolation
tests/api/      HTTP-level tests + known-defect tests
tests/e2e/      Playwright tests for the entry form
docs/           test plan and test cases
```

## Setup

```
python -m venv venv
venv\Scripts\activate          # Windows (Linux/macOS: source venv/bin/activate)
pip install -r requirements.txt
playwright install chromium
```

## Run

```
pytest                          # everything
pytest tests/unit tests/api     # no browser needed
pytest -m e2e                   # end-to-end only
python run.py                   # app at http://127.0.0.1:5000
```

Expected result today: all tests pass, and 7 tests show as `xfailed`. Those are the open defects.

## Defects found

| ID | Title | Severity | Steps to reproduce | Expected | Actual | Test |
| --- | --- | --- | --- | --- | --- | --- |
| BUG-01 | NaN accepted as total depth | High | POST `/api/boreholes` with raw JSON `"total_depth": NaN` | 400 | 201; response body contains `NaN`, which is not valid JSON | TC-BH-12 |
| BUG-02 | Infinity accepted as total depth | High | Same, with `"total_depth": Infinity` | 400 | 201 | TC-BH-13 |
| BUG-03 | NaN accepted as sample depth | High | POST `/api/boreholes/1/samples` with `"depth": NaN` | 400 | 201; NaN skips the depth-limit check | TC-SM-09 |
| BUG-04 | Form accepts `nan` as total depth | High | Enter `nan` in Total depth on `/` and save | Error shown | Borehole saved | TC-UI-03 |
| BUG-05 | Duplicate borehole names allowed | Medium | Create `BH-01` twice | 409 Conflict | Two boreholes with the same name | TC-BH-14 |
| BUG-06 | No length limit on borehole name | Low | Create a borehole with a 5,000-character name | 400 | 201 | TC-BH-15 |
| BUG-07 | Soil type is case-sensitive | Low | Add sample with `"soil_type": "Clay"` | Accepted as `clay` | 400 | TC-SM-11 |

**Root cause (BUG-01 to BUG-04):** `_is_number()` checks the type only, and both `NaN < 0` and `NaN > total_depth` evaluate to false, so NaN passes every range check. A fix is to reject non-finite values with `math.isfinite()`.

BUG-05 and BUG-07 also need a product decision: the expected behaviour above is my recommendation.

## Not covered yet

- Authentication (not implemented in the app)
- Persistent storage (in-memory by design)
- Performance testing
