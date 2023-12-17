from util import get_urls_list, get_prediction, init_mongo


def test_get_urls_list():
    eval_date = "2021-09-09"

    photos_col = init_mongo()
    urls = get_urls_list(photos_col, eval_date)

    assert len(urls) == 1935


def test_prediction():
    url = "https://bit.ly/2YdEW0Q"

    with open(".token", "r") as f:
        token = f.read()

    prediction, prob = get_prediction(token, url)
    assert prediction == "2"
    assert float(prob) > 0.9
