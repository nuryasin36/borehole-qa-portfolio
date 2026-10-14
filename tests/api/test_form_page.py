"""Server-rendered form checks that don't need a browser."""


def test_ui04_html_in_name_is_escaped(client):
    r = client.post(
        "/",
        data={"name": "<script>alert(1)</script>", "latitude": "1",
              "longitude": "1", "total_depth": "5"},
    )
    html = r.get_data(as_text=True)
    assert "&lt;script&gt;" in html
    assert "<script>alert(1)</script>" not in html
