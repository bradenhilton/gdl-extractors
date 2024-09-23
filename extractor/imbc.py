"""Extractors for https://imbc.com"""

import re
from http import HTTPStatus

from gallery_dl import exception, text
from gallery_dl.extractor.common import Extractor, Message


class ImbcExtractor(Extractor):
    category = "imbc"
    filename_fmt = "{filename}.{extension}"

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

    def metadata(self, page):
        return {
            "title": text.unescape(text.extr(page, "<title>", "</title>")),
            "article_id": self.article_id,
            "post_url": text.extr(page, 'proptery="og:url" content="', '"'),
        }


class ImbcAdenewsArticleExtractor(ImbcExtractor):
    """Extractors for articles on adenews.imbc.com"""

    subcategory = "adenews-article"
    root = "https://adenews.imbc.com"
    directory_fmt = ("{category}", "{subcategory}", "{article_id}")
    archive_fmt = "{category}_{subcategory}_{article_id}_{filename}"
    pattern = r"(?:https?://)?adenews\.imbc\.com/M/Detail/(\d+)"
    example = "https://adenews.imbc.com/M/Detail/12345"

    def __init__(self, match):
        ImbcExtractor.__init__(self, match)
        self.article_id = match.group(1)

    def items(self):
        page = self._call(self.url)
        data = self.metadata(page)
        data["post_url"] = f"{self.root}/M/Detail/{self.article_id}"
        data["date"] = text.parse_datetime(
            text.extr(text.extr(page, '<div class="date">', "</div>"), "<span>", "</span>"),
            format="%Y-%m-%d %H:%M",
            utcoffset=9,
        )

        article_content = text.extr(page, "<!-- 기사 상세 Start -->", "<!-- 네이티브 End -->")
        urls = [
            text.ensure_http_scheme(text.extr(image, 'src="', '"'))
            for image in text.extract_iter(article_content, "<img", ">")
        ]

        yield Message.Directory, data

        for data["num"], url in enumerate(urls, 1):
            image = {"url": url}
            data["image"] = image
            text.nameext_from_url(url, data)
            yield Message.Url, url, data


class ImbcEnewsArticleExtractor(ImbcExtractor):
    """Extractors for articles on enews.imbc.com"""

    subcategory = "enews-article"
    root = "https://enews.imbc.com"
    directory_fmt = ("{category}", "{subcategory}", "{article_id}")
    archive_fmt = "{category}_{subcategory}_{article_id}_{filename}"
    pattern = r"(?:https?://)?enews\.imbc\.com/News/RetrieveNewsInfo/(\d+)"
    example = "https://enews.imbc.com/News/RetrieveNewsInfo/12345"

    def __init__(self, match):
        ImbcExtractor.__init__(self, match)
        self.article_id = match.group(1)

    def items(self):
        page = self._call(self.url)
        data = self.metadata(page)
        data["date"] = text.parse_datetime(
            re.sub(r"Z$", "", text.extr(page, 'property="article:published_time" content="', '"')),
            format="%Y-%m-%dT%H:%M:%S",
            utcoffset=9,
        )

        article_content = text.extr(page, "<!-- 기사 본문 내용 Start -->", "<!-- 기사 본문 내용 End -->")
        urls = [
            text.ensure_http_scheme(text.extr(image, 'src="', '"'))
            for image in text.extract_iter(article_content, "<img", ">")
        ]

        yield Message.Directory, data

        for data["num"], url in enumerate(urls, 1):
            image = {"url": url}
            data["image"] = image
            text.nameext_from_url(url, data)
            yield Message.Url, url, data


class ImbcImnewsArticleExtractor(ImbcExtractor):
    """Extractors for articles on imnews.imbc.com"""

    subcategory = "imnews-article"
    root = "https://imnews.imbc.com"
    directory_fmt = (
        "{category}",
        "{subcategory}",
        "{article_id}",
    )
    archive_fmt = "{category}_{subcategory}_{article_id}_{filename}"
    pattern = r"(?:https?://)?imnews\.imbc\.com/news/\d+/\w+/article/(\d+_\d+).html"
    example = "https://imnews.imbc.com/news/2024/enter/article/12345_67890.html"

    def __init__(self, match):
        ImbcExtractor.__init__(self, match)
        self.article_id = match.group(1)

    def items(self):
        page = self._call(self.url)
        data = self.metadata(page)
        data["date"] = text.parse_datetime(
            text.extr(page, 'property="article:published_time" content="', '"'), format="%Y-%m-%dT%H:%M:%S%z"
        )

        article_content = text.extr(
            page,
            "<!-- // 전체재생 레이어 -->",
            "<!-- iMBC 연예 데이블 본문 바로 밑 -->",
        )
        urls = [
            text.ensure_http_scheme(text.extr(image, 'src="', '"'))
            for image in text.extract_iter(article_content, "<img", ">")
        ]

        yield Message.Directory, data

        for data["num"], url in enumerate(urls, 1):
            image = {"url": url}
            data["image"] = image
            text.nameext_from_url(url, data)
            yield Message.Url, url, data
