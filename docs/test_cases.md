# Test Cases – Borehole Logging API

Precondition for every case: the application is running with an empty in-memory store. For sample cases, borehole `BH-01` (lat -6.3, lon 107.1, total_depth 10) exists with ID 1 unless stated otherwise.

Type: **U** = unit, **A** = API, **E** = end-to-end, **M** = manual check. Status reflects the latest run.

## Boreholes

| ID | Title | Steps / input | Expected result | Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-BH-01 | Create valid borehole | POST `/api/boreholes` with valid body | 201, body has `id` 1 and the submitted fields | A | Pass |
| TC-BH-02 | Empty name rejected | name = `""` | 400, error mentions `name` | A | Pass |
| TC-BH-03 | Whitespace-only name rejected | name = `"   "` | 400, error mentions `name` | A | Pass |
| TC-BH-04 | Latitude out of range | latitude = 95, then -90.1 | 400 | A | Pass |
| TC-BH-05 | Latitude boundaries | latitude = 90, then -90 | 201 | A | Pass |
| TC-BH-06 | Longitude out of range | longitude = 181 | 400 | A | Pass |
| TC-BH-07 | Zero total depth | total_depth = 0 | 400 | A | Pass |
| TC-BH-08 | Negative total depth | total_depth = -1 | 400 | A, U | Pass |
| TC-BH-09 | Malformed JSON | body = `not json` | 400, `JSON object required` | A | Pass |
| TC-BH-10 | Get existing borehole | GET `/api/boreholes/1` | 200, total_depth 10.0 | A | Pass |
| TC-BH-11 | Get unknown borehole | GET `/api/boreholes/999` | 404 | A | Pass |
| TC-BH-12 | NaN total depth | total_depth = `NaN` (raw JSON) | 400 | A | **Fail – BUG-01** |
| TC-BH-13 | Infinite total depth | total_depth = `Infinity` (raw JSON) | 400 | A | **Fail – BUG-02** |
| TC-BH-14 | Duplicate borehole name | Create `BH-01` twice | 409 Conflict | A | **Fail – BUG-05** |
| TC-BH-15 | Overlong name | name = 5,000 characters | 400 | A | **Fail – BUG-06** |

## Samples

| ID | Title | Steps / input | Expected result | Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-SM-01 | Create valid sample | POST `/api/boreholes/1/samples` depth 3, clay, N 12 | 201, `borehole_id` 1 | A | Pass |
| TC-SM-02 | Sample at exact total depth | depth = 10 | 201 | A, U | Pass |
| TC-SM-03 | Sample deeper than borehole | depth = 12 | 400 | A, U | Pass |
| TC-SM-04 | Negative sample depth | depth = -1 | 400 | A, U | Pass |
| TC-SM-05 | Unknown soil type | soil_type = `rock` | 400 | A, U | Pass |
| TC-SM-06 | N-value boundaries | N = 0, 100, -1, 101 | 201, 201, 400, 400 | A, U | Pass |
| TC-SM-07 | Non-integer N-value | N = 5.5, then `"10"` | 400 | A, U | Pass |
| TC-SM-08 | Sample on unknown borehole | POST `/api/boreholes/999/samples` | 404 | A | Pass |
| TC-SM-09 | NaN sample depth | depth = `NaN` (raw JSON) | 400 | A | **Fail – BUG-03** |
| TC-SM-10 | Delete sample twice | DELETE `/api/samples/1` twice | 204, then 404 | A | Pass |
| TC-SM-11 | Soil type with capital letter | soil_type = `Clay` | 201 (stored as `clay`) | A | **Fail – BUG-07** |

## Entry form (`/`)

| ID | Title | Steps / input | Expected result | Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-UI-01 | Submit valid borehole | Fill all fields with valid data, click Save | Success message shows the borehole name | E | Pass* |
| TC-UI-02 | Negative depth shows error | total_depth = -3, click Save | Error message mentions `negative` | E | Pass* |
| TC-UI-03 | `nan` depth rejected | total_depth = `nan`, click Save | Error message, borehole not saved | A | **Fail – BUG-04** |
| TC-UI-04 | HTML in name is escaped | name = `<script>alert(1)</script>` | Name shown as text, script not executed | A, M | Pass |

\* Run locally and in CI with Playwright.
