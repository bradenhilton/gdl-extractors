"""Extractors for https://isplus.com/"""

import re
from http import HTTPStatus

from gallery_dl import exception, text
from gallery_dl.extractor.common import Extractor, Message

BASE_PATTERN = r"(?:https?://)?(?:www\.)?isplus\.com"


class IsplusExtractor(Extractor):
    """Base class for isplus extractors"""

    category = "isplus"
    root = "https://isplus.com"

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


class IsplusArticleExtractor(IsplusExtractor):
    """Extrator for articles on isplus.com"""

    subcategory = "article"
    filename_fmt = "{filename}_{num}.{extension}"
    directory_fmt = ("{category}", "{post_id}")
    archive_fmt = "{post_id}_{filename}_{num}"
    pattern = BASE_PATTERN + r"/article/view/(isp\d+)"
    example = "https://isplus.com/article/view/isp202501010000"

    def __init__(self, match):
        IsplusExtractor.__init__(self, match)
        self.post_id = match.group(1)
        self.post_url = f"{self.root}/article/view/{self.post_id}"

    def metadata(self, page):
        return {
            "date": (
                text.parse_datetime(
                    text.extr(
                        page,
                        ' name="article:published_time" content="',
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

        article_body = text.extr(page, ' id="article_body"', ' class="box banner"')

        images = [text.extr(figure, "<img", ">") for figure in text.extract_iter(article_body, "<figure", "</figure>")]

        for data["num"], image in enumerate(images, start=1):
            src = text.extr(image, ' src="', '"')
            url = re.sub(r"(\/data\/+isp\/+image\/+.*)\.[0-9]+x\.[0-9]+(\.[^/.]+)(?:[?#].*)?$", r"\1\2", src)
            data["image_url"] = url
            text.nameext_from_url(text.unquote(url), data)
            yield Message.Url, url, data
