"""Extractors for https://programs.sbs.co.kr/"""

import json
import re
from http import HTTPStatus
from urllib.parse import urlparse

from gallery_dl import exception, text
from gallery_dl.extractor.common import Extractor, Message

BASE_PATTERN = r"(?:https?://)?programs\.sbs\.co\.kr"


class SbsprogramsExtractor(Extractor):
    """Base class for sbs programs article extractors"""

    category = "sbsprograms"
    root = "https://programs.sbs.co.kr"

    def _decode_url(self, url):
        if re.match(r"^https?://", url):
            return url
        if re.match(r"^https?%3[aA]", url) or re.match(r"^[^/]*%2[fF]", url):
            return text.unquote(url)
        if re.match(r"^https?%253[aA]", url):
            return text.unquote(text.unquote(url))
        return url

    def _replace_patterns(self, url, patterns):
        for pattern, replacement in patterns:
            new_url = re.sub(pattern, replacement, url)
            if new_url != url:
                return new_url
        return url

    def _get_best_image_url(self, url):
        url = text.ensure_http_scheme(url)
        parsed_url = urlparse(url)
        if parsed_url.hostname.startswith("sbs.co.kr") and re.match(r"^img[0-9]*\.sbs\.co\.kr", url):
            patterns = [
                (r"(\/[0-9]+)_[0-9v]+\.([a-zA-Z0-9]*)$", r"\1.\2"),
                (r"(\/[^_]*)_[^/.]*(\.[^/.]*)$", r"\1_ori\2"),
            ]
            return self._replace_patterns(url, patterns)
        if parsed_url.hostname.startswith("photocloud.sbs.co.kr"):
            patterns = [
                (r"(://[^/]+/+)([^/]+/+)thumb/+([0-9a-f]{10,})-(?:[0-9]+|c[0-9]+x[0-9]+)\.", r"\1origin/edit/\2\3-p.")
            ]
            return self._replace_patterns(url, patterns)
        if parsed_url.hostname.startswith("image.cloud.sbs.co.kr"):
            patterns = [(r"_[0-9]*(\.[^/.]*)$", r"\1")]
            return self._replace_patterns(url, patterns)
        if parsed_url.hostname.startswith("image.board.sbs.co.kr"):
            patterns = [(r"-[0-9]+(\.[^/.]*)$", r"\1")]
            return self._replace_patterns(url, patterns)
        if parsed_url.hostname.startswith("board.sbs.co.kr"):
            patterns = [(r"^[a-z]+://[^/]+/+popup/+pc/+imageView\?(?:.*&)?imageUrl=([^&]+)(?:[&#].*)?$", r"\1")]
            return self._decode_url(self._replace_patterns(url, patterns))
        return url


class SbsprogramsArticleExtractor(SbsprogramsExtractor):
    """Extractor for articles on programs.sbs.co.kr"""

    subcategory = "article"
    filename_fmt = "{board_number}_{filename}.{extension}"
    directory_fmt = ("{category}", "{program_id}")
    archive_fmt = "{program_id}_{board_number}_{filename}_{num}"
    pattern = BASE_PATTERN + r"/[^/]+/([^/]+)/(?:[^/]+/)*(\d+)/?\?.*board_no=(\d+).*"
    example = "https://programs.sbs.co.kr/sbsm/theshow/visualboard/12345?cmd=view&board_no=836"

    def __init__(self, match):
        SbsprogramsExtractor.__init__(self, match)
        self.program_id = match.group(1)
        self.menu_id = match.group(2)
        self.board_number = match.group(3)
        self.post_url = match.group(0)

    def metadata(self, article):
        return {
            "title": article.get("TITLE"),
            "date": text.parse_datetime(article.get("REG_DATE"), format="%Y-%m-%d %H:%M:%S", utcoffset=9),
            "views": text.parse_int(article.get("CLICK_CNT")),
            "program_id": self.program_id,
            "board_number": self.board_number,
            "post_url": self.post_url,
        }

    def items(self):
        self.api = SbsprogramsAPI(self)

        board_codes = self.api.get_board_codes(self.program_id)
        article = self.api.get_article(self.board_number, board_codes.get(self.menu_id))
        data = self.metadata(article)

        article_content = article.get("CONTENT", "")
        urls = [
            self._get_best_image_url(text.extr(image, 'src="', '"'))
            for image in list(text.extract_iter(article_content, "<img", ">"))
        ]

        yield Message.Directory, data

        for data["num"], url in enumerate(urls, 1):
            image = {"url": url}
            data["image"] = image
            text.nameext_from_url(text.unquote(url), data)
            yield Message.Url, url, data


class SbsprogramsAPI:
    """Interface for the SBS Programs API"""

    API_URL = "https://static.apis.sbs.co.kr"
    BOARD_API_URL = "https://api.board.sbs.co.kr/bbs/V2.0/basic/board/detail"

    def __init__(self, extractor):
        self.extractor = extractor

    def get_article(self, board_number, board_code):
        endpoint = (
            f"/{board_number}?callback=boardViewCallback_{board_code}&action_type=callback&board_code={board_code}"
        )
        response = self._call(self.BOARD_API_URL + endpoint)
        return json.loads(re.search(r"boardViewCallback_.+\(({.+})\);", response).group(1)).get(
            "Response_Data_For_Detail"
        )

    def get_board_codes(self, program_id):
        endpoint = f"/program-api/1.0/menu/{program_id}"
        response = self._call(self.API_URL + endpoint)

        board_codes = {}
        menus = json.loads(response).get("menus", [])
        for menu in menus:
            all_menus = [menu, *menu.get("submenus", [])]
            for m in all_menus:
                if m.get("board_code"):
                    board_codes[m["mnuid"]] = m["board_code"]
        return board_codes

    def _call(self, url, params=None):
        if params is None:
            params = {}
        while True:
            response = self.extractor.request(url, params=params, fatal=None, allow_redirects=False)
            if response.status_code < HTTPStatus.MULTIPLE_CHOICES:
                return response.text
            if response.status_code == HTTPStatus.UNAUTHORIZED:
                raise exception.AuthenticationError from None
            if response.status_code == HTTPStatus.FORBIDDEN:
                raise exception.AuthorizationError from None
            if response.status_code == HTTPStatus.NOT_FOUND:
                raise exception.NotFoundError(self.extractor.subcategory) from None
            self.extractor.log.debug(response.text)
            msg = "Request failed"
            raise exception.StopExtraction(msg)
