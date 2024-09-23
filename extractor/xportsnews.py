"""Extractors for https://www.xportsnews.com/"""

import json
from http import HTTPStatus

from gallery_dl import exception, text
from gallery_dl.extractor.common import Extractor, Message

BASE_PATTERN = r"(?:https?://)?www\.xportsnews\.com"


class XportsnewsExtractor(Extractor):
    """Base class for xportsnews article extractors"""

    category = "xportsnews"
    root = "https://www.xportsnews.com"

    def _call(self, url, params=None):
        if params is None:
            params = {}
        while True:
            response = self.request(url, params=params, fatal=None, allow_redirects=False)
            if response.status_code < HTTPStatus.MULTIPLE_CHOICES:
                return response.text
            if response.status_code == HTTPStatus.UNAUTHORIZED:
                raise exception.AuthenticationError from None
            if response.status_code == HTTPStatus.FORBIDDEN:
                raise exception.AuthorizationError from None
            if response.status_code == HTTPStatus.NOT_FOUND:
                raise exception.NotFoundError(self.subcategory) from None
            self.log.debug(response.text)
            msg = "Request failed"
            raise exception.StopExtraction(msg)


class XportsnewsArticleExtractor(XportsnewsExtractor):
    """Extractor for articles on www.xportsnews.com"""

    subcategory = "article"
    filename_fmt = "{article_id}_{filename}.{extension}"
    directory_fmt = ("{category}", "{article_id}")
    archive_fmt = "{article_id}_{filename}_{num}"
    pattern = BASE_PATTERN + r"/article/(\d+)"
    example = "https://www.xportsnews.com/article/12345678910"

    def __init__(self, match):
        XportsnewsExtractor.__init__(self, match)
        self.article_id = match.group(1)
        self.post_url = match.group(0)

    def metadata(self, page):
        json_data = json.loads(text.extr(page, '<script type="application/ld+json">', "</script>"))
        return {
            "title": text.unescape(json_data.get("headline")),
            "author": json_data.get("author", {}).get("name"),
            "date": text.parse_datetime(
                json_data.get("datePublished"),
                format="%Y-%m-%dT%H:%M:%S%z",
            ),
            "article_id": self.article_id,
            "post_url": json_data.get("mainEntityOfPage", {}).get("@id"),
        }

    def items(self):
        page = self._call(self.post_url)
        data = self.metadata(page)

        article_content = text.extr(page, '<div class="news_contents">', '<ul class="another_ats">')
        urls = [text.extr(image, "src='", "'") for image in text.extract_iter(article_content, "<img", ">")]

        yield Message.Directory, data

        for data["num"], url in enumerate(urls, 1):
            image = {"url": url}
            data["image"] = image
            text.nameext_from_url(text.unquote(url), data)
            yield Message.Url, url, data
