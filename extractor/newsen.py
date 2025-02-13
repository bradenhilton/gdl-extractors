"""Extractors for https://newsen.com"""

import re
from http import HTTPStatus

from gallery_dl import exception, text
from gallery_dl.extractor.common import Extractor, Message

BASE_PATTERN = r"(?:https?://)?(?:m\.)?newsen\.com"


class NewsenExtractor(Extractor):
    """Base class for newsen extractors"""

    category = "newsen"
    root = "https://newsen.com"

    def _call(self, url, params=None):
        if params is None:
            params = {}
        while True:
            response = self.request(url, params=params, verify=False)
            response.encoding = response.apparent_encoding
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


class NewsenArticleExtractor(NewsenExtractor):
    """Extractor for articles on newsen.com"""

    subcategory = "article"
    filename_fmt = "{filename}.{extension}"
    directory_fmt = ("{category}", "{post_id}")
    archive_fmt = "{post_id}_{filename}"
    pattern = BASE_PATTERN + r"/news_view\.php\?uid=(\d+).*"
    example = "https://newsen.com/news_view.php?uid=123456789123456789"

    def __init__(self, match):
        NewsenExtractor.__init__(self, match)
        self.post_id = match.group(1)
        self.post_url = f"{self.root}/news_view.php?uid={self.post_id}"

    def metadata(self, page):
        return {
            "title": text.extr(page, "<title>", "</title>")
            .replace(" - 손에 잡히는 뉴스 눈에 보이는 뉴스 - 뉴스엔", "")
            .strip(),
            "date": (
                text.parse_datetime(
                    text.extr(
                        page,
                        ' property="article:published_time" content="',
                        '"',
                    ),
                    format="%Y-%m-%d %H:%M:%S",
                    utcoffset=9,
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

        article_body = text.extr(page, '<td class="article">', "</td>")

        image = text.extr(article_body, "<img id='artImg'", ">")
        data["num"] = 1
        url = text.ensure_http_scheme(text.extr(image, ' src="', '"'))
        data["image_url"] = url
        text.nameext_from_url(text.unquote(url), data)
        yield Message.Url, url, data
