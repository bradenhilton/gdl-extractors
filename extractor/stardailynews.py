"""Extractors for https://www.stardailynews.co.kr/"""

import re
from http import HTTPStatus

from gallery_dl import exception, text
from gallery_dl.extractor.common import Extractor, Message

BASE_PATTERN = r"(?:https?://)?www\.stardailynews\.co\.kr"


class StardailynewsExtractor(Extractor):
    """Base class for stardailynews extractors"""

    category = "stardailynews"
    root = "https://www.stardailynews.co.kr"

    def _call(self, url, params=None):
        if params is None:
            params = {}
        while True:
            response = self.request(url, params=params)
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


class StardailynewsArticleExtractor(StardailynewsExtractor):
    """Extrator for articles on www.stardailynews.co.kr"""

    subcategory = "article"
    filename_fmt = "{filename}.{extension}"
    directory_fmt = ("{category}", "{post_id}")
    archive_fmt = "{post_id}_{filename}"
    pattern = BASE_PATTERN + r"/news/articleView\.html\?idxno=(\d+)"
    example = "https://www.stardailynews.co.kr/news/articleView.html?idxno=12345"

    def __init__(self, match):
        StardailynewsExtractor.__init__(self, match)
        self.post_id = match.group(1)
        self.post_url = f"{self.root}/news/articleView.html?idxno={self.post_id}"

    def metadata(self, page):
        return {
            "title": text.extr(page, "<title>", "</title>")
            .strip()
            .replace(" < 포토 < 포토 · 동영상 < 기사본문 - 스타데일리뉴스", "")
            .replace(" ::", ""),
            "date": (
                text.parse_datetime(
                    text.extr(
                        page,
                        ' property="article:published_time" content="',
                        '"',
                    ),
                )
            ),
            "post_id": self.post_id,
            "post_url": self.post_url,
        }

    def items(self):
        page = self._call(self.url)
        page = re.sub(r"\s+", " ", page)

        data = self.metadata(page)

        yield Message.Directory, data

        article_body = text.extr(page, 'itemprop="articleBody"', "</article>")

        images = [
            text.extr(figure, "<img", ">")
            for figure in text.extract_iter(article_body, ' data-type="photo"', "</figure>")
        ]

        for data["num"], image in enumerate(images, start=1):
            url = text.extr(image, ' src="', '"')
            if " data-org=" in image:
                url = text.extr(image, ' data-org="', '"')
            data["image_url"] = url
            text.nameext_from_url(text.unquote(url), data)
            yield Message.Url, url, data
