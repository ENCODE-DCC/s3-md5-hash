from functions.initial_md5_hash import app


def test_initial_md5_hash() -> None:
    data = app.lambda_handler({"event": "test"}, "")
    assert 0 <= data["stock_price"] > 0 <= 100
