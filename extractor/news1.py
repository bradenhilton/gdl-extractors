"""Extractors for https://www.news1.kr"""

import json
import re
import urllib
from http import HTTPStatus

from gallery_dl import exception, text
from gallery_dl.extractor.common import Extractor, Message

BASE_PATTERN = r"(?:https?://)?www\.news1\.kr"


class News1Extractor(Extractor):
    """Base class for news1 article extractors"""

    category = "bntnews"
    root = "https://www.news1.kr"

    def _get_best_image_url(self, url):
        if "?url=" in url:
            parsed_url = urllib.parse.urlparse(url)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            url = urllib.parse.unquote(query_params["url"][0])

        new_url = re.sub(r"/thumbnails/(.*)/thumb_[0-9]+x(?:[0-9]+)?(\.[^/.]*)$", r"/\1/original\2", url)

        new_url = (
            new_url.replace("main_thumb.jpg", "original.jpg")
            .replace("article.jpg", "original.jpg")
            .replace("no_water.jpg", "original.jpg")
            .replace("photo_sub_thumb.jpg", "original.jpg")
            .replace("section_top.jpg", "original.jpg")
            .replace("high.jpg", "original.jpg")
        )

        return re.sub(r"/+dims/.*$", "", new_url)

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


class News1ArticleExtractor(News1Extractor):
    """Extractor for articles on www.news1.kr"""

    subcategory = "article"
    filename_fmt = "{filename}.{extension}"
    directory_fmt = ("{category}", "{article_id}")
    archive_fmt = "{filename}_{num}"
    pattern = BASE_PATTERN + r"/(?:[^/]+/)*(\d+)"
    example = "https://www.news1.kr/photos/123456789"

    def __init__(self, match):
        News1Extractor.__init__(self, match)
        self.article_id = match.group(1)
        self.post_url = match.group(0)

    def metadata(self, page):
        json_data = json.loads(text.extr(page, '<script type="application/ld+json">', "</script>"))
        if isinstance(json_data, list):
            json_data = json_data[0]
        return {
            "title": text.unescape(json_data.get("headLine")),
            "author": json_data.get("author", [])[0].get("name", "").replace(" 기자", ""),
            "date": text.parse_datetime(
                json_data.get("datePublished"),
                format="%Y-%m-%dT%H:%M:%S%z",
            ),
            "article_id": self.article_id,
            "post_url": json_data.get("mainEntityOfPage"),
        }

    def items(self):
        page = self._call(self.post_url)
        data = self.metadata(page)

        article_content = text.extr(page, '<div class="row justify-content-center">', "</main>")
        urls = [
            self._get_best_image_url(text.extr(image, 'src="', '"'))
            for figure in text.extract_iter(article_content, "<figure", "</figure>")
            for image in text.extract_iter(figure, "<img", ">")
        ]

        yield Message.Directory, data

        for data["num"], url in enumerate(urls, 1):
            image = {"url": url}
            data["image"] = image
            data["filename"] = re.search(r"/photos/\d{4}/(?:\d{1,2}/){2}(\d+)/", text.unquote(url)).group(1)
            data["extension"] = text.ext_from_url(text.unquote(url))
            yield Message.Url, url, data
