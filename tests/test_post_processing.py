from overload.post_processing import find_and_replace_image_urls
import pytest

@pytest.mark.parametrize(("given","result"),(
    ("![id](1)","![testing](/image/1)"),
    ("hello![id](1)hello","hello![testing](/image/1)hello"),
    ("![name](test.png)","![testing](/image/1)"),
    ("hello![name](test.png)hello","hello![testing](/image/1)hello"),
    ("![id](3)","![This image is not available.](/image/1)"),
    ("![name](notreal.png)","![This image is not available.](/image/1)"),
    ("![Placeholder](https://placehold.co/600x400)","![Placeholder](https://placehold.co/600x400)")
))
def test_find_and_replace_image_urls(given,result,app):
    with app.app_context(), app.test_request_context():
        assert find_and_replace_image_urls(given) == result