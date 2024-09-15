"""Extractors for https://www.topstarnews.net/"""

import re
from http import HTTPStatus

from gallery_dl import exception, text
from gallery_dl.extractor.common import Extractor, Message

BASE_PATTERN = r"(?:https?://)?www\.topstarnews\.net"


class TopstarnewsExtractor(Extractor):
    """Base class for topstarnews extractors"""

    category = "topstarnews"
    root = "https://www.topstarnews.net"

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


class TopstarnewsArticleExtractor(TopstarnewsExtractor):
    """Extrator for articles on www.topstarnews.net"""

    subcategory = "article"
    filename_fmt = "{filename}.{extension}"
    directory_fmt = ("{category}", "{post_id}")
    archive_fmt = "{post_id}_{filename}"
    pattern = BASE_PATTERN + r"/news/articleView\.html\?idxno=(\d+)"
    example = "https://www.topstarnews.net/news/articleView.html?idxno=12345"

    def __init__(self, match):
        TopstarnewsExtractor.__init__(self, match)
        self.post_id = match.group(1)
        self.post_url = f"{self.root}/news/articleView.html?idxno={self.post_id}"

    def metadata(self, page):
        data = {
            "title": text.extr(page, "<title>", "</title>")
            .strip()
            .replace(" [HD포토]", "")
            .replace(" - 최규석 기자 - 톱스타뉴스", ""),
            "date": (
                text.parse_datetime(
                    text.rextract(
                        page,
                        ' property="article:published_time" content="',
                        '"',
                    )[0],
                )
                or text.parse_datetime(
                    text.extr(
                        page,
                        '<i class="fa fa-clock-o fa-fw"></i>',
                        "</li>",
                    )
                    .strip()
                    .split(" ", maxsplit=1)[1],
                    format="%Y.%m.%d %H:%M",
                    utcoffset=9,
                )
            ),
            "author": text.extr(
                page,
                '<i class="fa fa-user-o fa-fw"></i>',
                "</li>",
            ).strip(),
            "views": text.parse_int(
                text.extr(page, '<i class="fa fa-desktop fa-fw"></i>', "</li>").strip().split(" ", maxsplit=1)[1],
            ),
            "post_id": self.post_id,
            "post_url": self.url,
        }
        if ' name="keywords" content="' in page:
            data["tags"] = text.extr(page, ' name="keywords" content="', '"').split(",")
        return data

    def items(self):
        page = self._call(self.url)
        page = re.sub(r"\s+", " ", page)

        data = self.metadata(page)

        yield Message.Directory, data

        article_body = text.extr(page, ' itemprop="articleBody">', '<div id="article-sns2"')

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