"""Extractors for https://www.osen.co.kr/"""

from http import HTTPStatus

from gallery_dl import exception, text
from gallery_dl.extractor.common import Extractor, Message

BASE_PATTERN = r"(?:https?://)?(?:www\.)?osen\.co\.kr"


class OsenExtractor(Extractor):
    """Base class for osen article extractors"""

    category = "osen"
    root = "https://www.osen.co.kr"

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


class OsenArticleExtractor(OsenExtractor):
    """Extractor for articles on www.osen.co.kr"""

    subcategory = "article"
    filename_fmt = "{article_id}_{filename}.{extension}"
    directory_fmt = ("{category}", "{article_id}")
    archive_fmt = "{article_id}_{filename}_{num}"
    pattern = BASE_PATTERN + r"/article/(G\d+)"
    example = "https://www.osen.co.kr/article/G12345678910"

    def __init__(self, match):
        OsenExtractor.__init__(self, match)
        self.article_id = match.group(1)
        self.post_url = match.group(0)

    def metadata(self, page):
        return {
            "title": text.unescape(text.extr(page, ' property="og:title" content="', '"')).replace("[사진]", ""),
            "description": text.unescape(text.extr(page, ' property="og:description" content="', '"')),
            "date": text.parse_datetime(
                text.extr(page, ' property="article:published_time" content="', '"'),
                format="%Y-%m-%dT%H:%M%z",
            ),
            "article_id": self.article_id,
            "post_url": text.extr(page, ' property="og:url" content="', '"'),
        }

    def items(self):
        page = self._call(self.post_url)
        data = self.metadata(page)

        article_content = text.extr(page, 'id="articleBody"', '<span class="copyright"')

        urls = [text.extr(image, 'src="', '"') for image in text.extract_iter(article_content, "<img ", ">")]

        yield Message.Directory, data

        for data["num"], url in enumerate(urls, 1):
            image = {"url": url}
            data["image"] = image
            text.nameext_from_url(text.unquote(url), data)
            yield Message.Url, url, data
