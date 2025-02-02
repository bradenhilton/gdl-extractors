"""Extractors for https://post.naver.com/"""

import json
import re
from http import HTTPStatus

from gallery_dl import exception, text
from gallery_dl.extractor.common import Extractor, Message

BASE_PATTERN = r"(?:https?://)?(?:m\.)?post\.naver\.com"


class NaverpostExtractor(Extractor):
    """Base class for naver post extractors"""

    category = "naverpost"
    root = "https://post.naver.com"

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

    def _pagination(self, url, params=None):
        if params is None:
            params = {}
        while True:
            res = self._call(url, params)
            # The value of `html` in the response contains escaped single quotes,
            # which would raise a JSONDecodeError exception
            res = json.loads(res.replace(r"\'", "'"))
            endpoints = text.extract_iter(
                res["html"],
                '<div class="text_area">\n<a href="',
                '"',
            )
            urls = [self.root + endpoint for endpoint in endpoints]
            yield from urls
            if "nextFromNo" not in res:
                return
            params["fromNo"] = res["nextFromNo"]


class NaverpostPostExtractor(NaverpostExtractor):
    """Extractor for posts on post.naver.com"""

    subcategory = "post"
    filename_fmt = "{volume_no}_{num}.{extension}"
    directory_fmt = ("{category}", "{author}", "{volume_no}")
    archive_fmt = "{volume_no}_{num}"
    pattern = BASE_PATTERN + r"/viewer/postView\.(naver|nhn)\?volumeNo=(\d+)(?:&.+)?"
    example = "https://post.naver.com/viewer/postView.naver?volumeNo=12345"

    def __init__(self, match):
        NaverpostExtractor.__init__(self, match)
        self.page_ext = match.group(1)
        self.volume_no = match.group(2)
        self.post_url = f"https://post.naver.com/viewer/postView.{self.page_ext}?volumeNo={self.volume_no}"

    def metadata(self, page):
        return {
            "title": text.unescape(text.extr(page, "<title>", "</title>").strip().split(" : ")[0]),
            "description": text.unescape(
                text.extr(page, ' property="og:description" content="', '"').strip(),
            ),
            "author": text.extr(page, ' property="og:author" content="', '"'),
            "date": text.parse_datetime(
                text.extr(page, ' property="og:createdate" content="', '"'),
                format="%Y.%m.%d. %H:%M:%S",
                utcoffset=9,
            ),
            "volume_no": self.volume_no,
            "views": text.parse_int(
                (
                    text.extr(page, '<span class="post_view">', " ")
                    or text.extr(page, '<span class="se_view" style="">', " ")
                ).replace(",", ""),
            ),
            "url": self.post_url,
        }

    def items(self):
        page = self._call(self.post_url)
        data = self.metadata(page)

        # Get image URLs from img elements whose class list contains either `img_attachedfile`
        # or `se_mediaImage` and `__se_img_el` and whose data-src URL ends with `type=w\d+`
        urls = (
            text.extr(image, ' data-src="', '"').split("?", maxsplit=1)[0]
            for image in text.extract_iter(page, "<img", ">")
            if ("img_attachedfile" in image)
            or ("se_mediaImage" in image and "__se_img_el" in image)
            and re.search(r'data-src=".+type=w\d+"', image)
        )

        yield Message.Directory, data

        for data["num"], url in enumerate(urls, 1):
            image = {"url": url}
            data["image"] = image
            text.nameext_from_url(text.unquote(url), data)
            yield Message.Url, url, data


class NaverpostUserExtractor(NaverpostExtractor):
    """Extractor for all posts from a user on post.naver.com"""

    subcategory = "user"
    pattern = BASE_PATTERN + r"/my\.naver\?memberNo=(\d+)"
    example = "https://post.naver.com/my.naver?memberNo=12345"

    def __init__(self, match):
        NaverpostExtractor.__init__(self, match)
        self.member_no = match.group(1)

    def items(self):
        data = {"_extractor": NaverpostPostExtractor}
        endpoint = self.root + "/async/my.naver"
        params = {"memberNo": self.member_no}
        posts = self._pagination(endpoint, params)
        for url in posts:
            yield Message.Queue, url, data
