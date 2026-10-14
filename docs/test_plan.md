# Test Plan – Borehole Logging API

## 1. Objective
Verify that the Borehole Logging API and its entry form store only valid geotechnical data, return correct status codes and error messages, and protect data integrity for borehole and sample records.

## 2. Scope

**In scope**
- Borehole API: create, list, get by ID
- Sample API: create, list per borehole, delete
- Validation rules: name, coordinates, total depth, sample depth, soil type, SPT N-value
- Borehole entry form at `/` (server-rendered HTML)

**Out of scope**
- Authentication and authorization (not implemented)
- Persistence across restarts (data is in memory by design)
- Performance and load testing
- Browsers other than Chromium

## 3. Business rules under test

| Field | Rule |
| --- | --- |
| name | Required, not blank |
| latitude | Number, -90 to 90 inclusive |
| longitude | Number, -180 to 180 inclusive |
| total_depth | Number, greater than 0 |
| sample depth | Number, 0 to borehole total_depth inclusive |
| soil_type | One of: clay, silt, sand, gravel, peat, fill |
| n_value | Optional; integer, 0 to 100 inclusive |

## 4. Test approach

The suite follows the test pyramid:

- **Unit tests** (`tests/unit`): validation functions in isolation. Fast, run on every change.
- **API tests** (`tests/api`): HTTP requests through the Flask test client, checking status codes, response bodies, and error messages.
- **End-to-end tests** (`tests/e2e`): Playwright drives the entry form in Chromium as a real user would.

Test design techniques:
- **Equivalence partitioning:** valid vs invalid classes for each field (number vs string, known vs unknown soil type).
- **Boundary value analysis:** latitude ±90, N-value 0 and 100, sample depth equal to total depth.
- **Error guessing:** special float values (NaN, Infinity), very long strings, HTML injection, duplicate records.

Known defects are kept as `xfail(strict=True)` tests, so the suite stays green while the bug is open and alerts the team when a fix lands.

## 5. Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Invalid depth values reach reports | Wrong borehole logs sent to clients | Boundary and special-value tests on all depth fields |
| Samples attached to wrong or missing borehole | Broken sample register | 404 checks and borehole_id checks on sample endpoints |
| Form and API apply different rules | Data quality depends on entry channel | Same validation tested through both API and form |

## 6. Environment
- Python 3.11+, Flask 3, pytest 8, Playwright (Chromium)
- Local run on Windows and Linux; CI on GitHub Actions (Ubuntu)

## 7. Entry and exit criteria

**Entry:** application starts locally, business rules above are agreed.

**Exit:**
- All planned test cases executed
- No open High severity defects for a release (current state: open, see README)
- Every open defect logged with reproduction steps and linked to a test case

## 8. Deliverables
- This test plan
- `docs/test_cases.md`
- Automated suite in `tests/`
- Defect list in `README.md`
