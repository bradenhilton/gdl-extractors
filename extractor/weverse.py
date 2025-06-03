"""Extractors for https://weverse.io/"""

import binascii
import hashlib
import hmac
import time
import urllib.parse
import uuid
from collections import OrderedDict
from http import HTTPStatus

from gallery_dl import exception, text
from gallery_dl.cache import cache
from gallery_dl.extractor.common import Extractor, Message

BASE_PATTERN = r"^(?:https?://)?(?:m\.)?weverse\.io/([^/?#]+)"
MEMBER_ID_PATTERN = r"/([a-f0-9]+)"
POST_ID_PATTERN = r"/(\d-\d+)"


class WeverseExtractor(Extractor):
    """Base class for weverse extractors"""

    category = "weverse"
    filename_fmt = "{category}_{id}.{extension}"
    archive_fmt = "{category}_{post_id}_{id}"
    cookies_domain = ".weverse.io"
    cookies_names = ("we2_access_token", "we2_refresh_token")
    root = "https://weverse.io"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.community_keyword = match.group(1)

    def _init(self):
        self.embeds = self.config("embeds", default=True)
        self.videos = self.config("videos", default=True)
        self.api = WeverseAPI(self)

    def items(self):
        self.login()

        post = self.post()
        data = self.metadata(post)

        if post.get("attachment"):
            files = self._extract_post(post)
        elif post.get("extension"):
            if isinstance(self, WeverseMomentExtractor):
                files = self._extract_moment(post)
            else:
                files = self._extract_media(post["extension"])
        else:
            # Text only
            return None

        yield Message.Directory, data
        for file in files:
            file.update(data)
            url = file.pop("url")
            yield Message.Url, url, file

    def _extract_image(self, image):
        url = image["url"]
        return {
            "id": image["photoId"],
            "url": url,
            "width": image["width"],
            "height": image["height"],
            "extension": text.ext_from_url(url),
        }

    def _extract_video(self, video):
        video_id = video["videoId"]
        if isinstance(self, WeverseMediaExtractor):
            master_id = video.get("uploadInfo", {}).get("videoId") or video["infraVideoId"]
            best_video = self.get_best_video(
                self.api.get_media_video_list(video_id, master_id),
            )
        else:
            best_video = self.get_best_video(self.api.get_post_video_list(video_id))
        url = best_video["source"]
        return {
            "id": video_id,
            "url": url,
            "width": best_video["encodingOption"]["width"],
            "height": best_video["encodingOption"]["height"],
            "extension": text.ext_from_url(url),
        }

    def _extract_embed(self, embed):
        return {
            "id": embed["youtubeVideoId"],
            "extension": None,
            "url": f"ytdl:{embed['videoPath']}",
        }

    def _extract_post(self, post):
        attachments = post["attachment"]
        if not attachments:
            yield None

        # The order of attachments in the API response can differ to the order
        # of attachments on the site
        attachment_order = text.extract_iter(post["body"], 'id="', '"')
        for index, attachment_id in enumerate(attachment_order, 1):
            file = {
                "num": index,
            }
            attachment = attachments.get("photo", {}).get(attachment_id) or attachments.get("video", {}).get(
                attachment_id
            )
            if "photoId" in attachment:
                file.update(self._extract_image(attachment))
            else:
                file.update(self._extract_video(attachment))
            yield file

    def _extract_moment(self, post):
        extension = post["extension"]
        moment = extension.get("moment") or extension.get("momentW1")
        if not moment:
            yield None

        if "photo" in moment:
            file = self._extract_image(moment["photo"])
        else:
            if not self.videos:
                yield None
            file = self._extract_video(moment["video"])
        file["num"] = 1

        yield file

    def _extract_media(self, extension):
        if "image" in extension:
            for index, photo in enumerate(extension["image"]["photos"], 1):
                file = self._extract_image(photo)
                file["num"] = index
                yield file
        elif "video" in extension:
            if not self.videos:
                yield None
            file = self._extract_video(extension["video"])
            yield file
        else:
            if not (self.embeds and self.videos):
                yield None
            file = self._extract_embed(extension["youtube"])
            file["num"] = 1
            yield file

    def get_best_video(self, videos):
        return max(
            videos,
            key=lambda video: video["encodingOption"]["width"] * video["encodingOption"]["height"],
        )

    def metadata(self, post):
        published_at = text.parse_timestamp(post["publishedAt"] / 1000)
        data = {
            "date": published_at,
            "post_url": post.get("shareUrl", self.url),
            "post_id": post["postId"],
            "post_type": post["postType"],
            "section_type": post["sectionType"],
        }

        if "hideFromArtist" in post:
            data["hide_from_artist"] = post["hideFromArtist"]

        if "membershipOnly" in post:
            data["membership_only"] = post["membershipOnly"]

        if post.get("tags", []):
            data["tags"] = post["tags"]

        if "author" in post:
            author = {
                "id": post["author"]["memberId"],
                "name": post["author"]["profileName"],
                "profile_type": post["author"]["profileType"],
            }
            if "artistOfficialProfile" in post["author"]:
                artist_profile = post["author"]["artistOfficialProfile"]
                author["name"] = artist_profile["officialName"]
            data["author"] = author

        if "community" in post:
            community = {
                "id": post["community"]["communityId"],
                "name": post["community"]["communityName"],
                "artist_code": post["community"]["artistCode"],
            }
            data["community"] = community

        extension = post["extension"]
        media_info = extension.get("mediaInfo", {})
        if media_info:
            categories = [
                {
                    "id": category["id"],
                    "type": category["type"],
                    "title": category["title"],
                }
                for category in media_info["categories"]
            ]
            data.update(
                {
                    "title": media_info["title"],
                    "media_type": media_info["mediaType"],
                    "categories": categories,
                },
            )

        moment = next(
            (extension[key] for key in ("moment", "momentW1") if key in extension),
            None,
        )
        if moment:
            expire_at = text.parse_timestamp(moment["expireAt"] / 1000)
            data["expire_at"] = expire_at

        return data

    def post(self):
        return {}

    def _is_access_token_valid(self, access_token=None):
        validate_res = self.api.validate_access_token(access_token)
        return all(
            [
                int(validate_res.get("expiresIn", 0)) >= 3600,  # noqa: PLR2004
                not validate_res.get("refreshRequired", True),
            ]
        )

    def _refresh_access_token(self, source, access_token=None, refresh_token=None):
        if access_token:
            self.log.info("Validating access token (%s)", source)
            if self._is_access_token_valid(access_token):
                return {self.cookies_names[0]: access_token}
            if refresh_token:
                self.log.info("Refreshing access token (%s)", source)
                res = self.api.refresh_access_token(access_token, refresh_token)
                if "accessToken" in res and "refreshToken" in res:
                    return {self.cookies_names[0]: res["accessToken"], self.cookies_names[1]: res["refreshToken"]}
        return {}

    def login(self):
        if self.cookies_check(self.cookies_names):
            return

        username, password = self._get_auth_info()
        if any([username, password]):
            self.log.warning("""\
It is no longer possible to log in with a username and password due to reCAPTCHA.
Please use cookies or set 'access_token' to the 'we2_access_token' cookie value and/or
'refresh_token' to the 'we2_refresh_token' cookie value under 'extractor.weverse' in your config.""")

        self.cookies_update(self._login_impl())

    @cache(maxage=3 * 86400)
    def _login_impl(self):
        access_token_cookie = self.cookies.get(self.cookies_names[0], domain=self.cookies_domain)
        refresh_token_cookie = self.cookies.get(self.cookies_names[1], domain=self.cookies_domain)
        new_cookies = self._refresh_access_token(
            source="cookie", access_token=access_token_cookie, refresh_token=refresh_token_cookie
        )
        if new_cookies != {}:
            return new_cookies

        access_token_config = self.config("access_token")
        refresh_token_config = self.config("refresh_token")
        new_cookies = self._refresh_access_token(
            source="config", access_token=access_token_config, refresh_token=refresh_token_config
        )
        if new_cookies != {}:
            return new_cookies

        self.log.warning("""\
Unable to refresh access token. Please login to the site again and/or re-export cookies
or update 'access_token' and/or 'refresh_token' under 'extractor.weverse' in your config.
Proceeding without authentication.
""")
        return {}


class WeversePostExtractor(WeverseExtractor):
    """Extractor for a weverse community post"""

    subcategory = "post"
    directory_fmt = ("{category}", "{community[name]}", "{author[id]}", "{post_id}")
    pattern = rf"{BASE_PATTERN}/(?:artist|fanpost){POST_ID_PATTERN}"
    example = "https://weverse.io/abcdef/artist/1-123456789"

    def __init__(self, match):
        WeverseExtractor.__init__(self, match)
        self.post_id = match.group(2)

    def post(self):
        return self.api.get_post(self.post_id)


class WeverseMemberExtractor(WeverseExtractor):
    """Extractor for all posts from a weverse community member"""

    subcategory = "member"
    pattern = rf"{BASE_PATTERN}/profile{MEMBER_ID_PATTERN}$"
    example = "https://weverse.io/abcdef/profile/a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5"

    def __init__(self, match):
        WeverseExtractor.__init__(self, match)
        self.member_id = match.group(2)

    def items(self):
        self.login()

        data = {"_extractor": WeversePostExtractor}
        posts = self.api.get_member_posts(self.member_id)
        for post in posts:
            yield Message.Queue, post["shareUrl"], data


class WeverseFeedExtractor(WeverseExtractor):
    """Extractor for a weverse community feed"""

    subcategory = "feed"
    pattern = rf"{BASE_PATTERN}/(feed|artist)$"
    example = "https://weverse.io/abcdef/feed"

    def __init__(self, match):
        WeverseExtractor.__init__(self, match)
        self.feed_name = match.group(2)

    def items(self):
        self.login()

        data = {"_extractor": WeversePostExtractor}
        posts = self.api.get_feed_posts(self.community_keyword, self.feed_name)
        for post in posts:
            yield Message.Queue, post["shareUrl"], data


class WeverseMomentExtractor(WeverseExtractor):
    """Extractor for a weverse community artist moment"""

    subcategory = "moment"
    pattern = rf"{BASE_PATTERN}/moment{MEMBER_ID_PATTERN}/post{POST_ID_PATTERN}"
    example = "https://weverse.io/abcdef/moment/a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5/post/1-123456789"

    def __init__(self, match):
        WeverseExtractor.__init__(self, match)
        self.post_id = match.group(3)

    def post(self):
        return self.api.get_post(self.post_id)


class WeverseMomentsExtractor(WeverseExtractor):
    """Extractor for all moments from a weverse community artist"""

    subcategory = "moments"
    pattern = rf"{BASE_PATTERN}/moment{MEMBER_ID_PATTERN}$"
    example = "https://weverse.io/abcdef/moment/a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5"

    def __init__(self, match):
        WeverseExtractor.__init__(self, match)
        self.member_id = match.group(2)

    def items(self):
        self.login()

        data = {"_extractor": WeverseMomentExtractor}
        moments = self.api.get_member_moments(self.member_id)
        for moment in moments:
            yield Message.Queue, moment["shareUrl"], data


class WeverseMediaExtractor(WeverseExtractor):
    """Extractor for a weverse community media post"""

    subcategory = "media"
    directory_fmt = ("{category}", "{community[name]}", "media", "{post_id}")
    pattern = rf"{BASE_PATTERN}/media{POST_ID_PATTERN}"
    example = "https://weverse.io/abcdef/media/1-123456789"

    def __init__(self, match):
        WeverseExtractor.__init__(self, match)
        self.post_id = match.group(2)

    def post(self):
        return self.api.get_post(self.post_id)


class WeverseMediaTabExtractor(WeverseExtractor):
    """Extractor for the media tab of a weverse community"""

    subcategory = "media-tab"
    pattern = rf"{BASE_PATTERN}/media(?:/(all|membership|new))?$"
    example = "https://weverse.io/abcdef/media"

    def __init__(self, match):
        WeverseExtractor.__init__(self, match)
        self.tab_name = match.group(2) or "all"

    def items(self):
        self.login()

        data = {"_extractor": WeverseMediaExtractor}
        if self.tab_name == "new":
            get_media = self.api.get_latest_community_media
        elif self.tab_name == "membership":
            get_media = self.api.get_membership_community_media
        else:
            get_media = self.api.get_all_community_media
        medias = get_media(self.community_keyword)
        for media in medias:
            yield Message.Queue, media["shareUrl"], data


class WeverseMediaCategoryExtractor(WeverseExtractor):
    """Extractor for media by category of a weverse community"""

    subcategory = "media-category"
    pattern = rf"{BASE_PATTERN}/media/category/(\d+)"
    example = "https://weverse.io/abcdef/media/category/1234"

    def __init__(self, match):
        WeverseExtractor.__init__(self, match)
        self.media_category = match.group(2)

    def items(self):
        self.login()

        data = {"_extractor": WeverseMediaExtractor}
        medias = self.api.get_media_by_category_id(self.media_category)
        for media in medias:
            yield Message.Queue, media["shareUrl"], data


class WeverseAPI:
    """Interface for the Weverse API"""

    BASE_API_URL = "https://global.apis.naver.com"
    WMD_API_URL = f"{BASE_API_URL}/weverse/wevweb"
    VOD_API_URL = f"{BASE_API_URL}/rmcnmv/rmcnmv"

    ACCOUNT_BASE_API_URL = "https://accountapi.weverse.io"

    APP_ID = "be4d79eb8fc7bd008ee82c8ec4ff6fd4"
    SECRET = "1b9cb6378d959b45714bec49971ade22e6e24e42"  # noqa: S105

    def __init__(self, extractor):
        self.extr = extractor
        self.device_id = extractor.cookies.get("we2_device_id", domain=extractor.cookies_domain) or str(uuid.uuid4())
        root = extractor.root
        self.base_headers = {
            "Accept": "application/json",
            "Origin": root,
            "Referer": f"{root}/",
        }

    def _auth_header(self, access_token=None):
        token_cookie = self.extr.cookies.get(self.extr.cookies_names[0], domain=self.extr.cookies_domain)
        token = access_token or token_cookie
        if token:
            return {"Authorization": f"Bearer {token}"}
        return {}

    def _headers(self):
        return {**self.base_headers, **self._auth_header(), "WEV-device-Id": self.device_id}

    def _token_headers(self, access_token=None):
        return {
            **self.base_headers,
            **self._auth_header(access_token),
            "X-ACC-APP-SECRET": "5419526f1c624b38b10787e5c10b2a7a",
            "X-ACC-SERVICE-ID": "weverse",
            "X-ACC-TRACE-ID": str(uuid.uuid4()),
        }

    def _endpoint_with_params(self, endpoint, params):
        params_delimiter = "?"
        if "?" in endpoint:
            params_delimiter = "&"
        return f"{endpoint}{params_delimiter}{urllib.parse.urlencode(query=params)}"

    def _message_digest(self, endpoint, params, timestamp):
        key = self.SECRET.encode()
        url = self._endpoint_with_params(endpoint, params)
        message = f"{url[:255]}{timestamp}".encode()
        hash_digest = hmac.new(key, message, hashlib.sha1).digest()
        return binascii.b2a_base64(hash_digest).rstrip().decode()

    def _apply_no_auth(self, endpoint, params):
        if not endpoint.endswith("/preview"):
            endpoint += "/preview"
        params.update({"fieldSet": "postForPreview"})
        return endpoint, params

    def _is_text_only(self, post):
        for key in ("attachment", "extension"):
            if post.get(key, {}):
                return False
        if "summary" in post:
            s = post["summary"]
            if s.get("videoCount", 0) + s.get("photoCount", 0) > 0:
                return False
        return True

    def get_in_key(self, video_id):
        endpoint = f"/video/v1.2/vod/{video_id}/inKey"

        return self._call_wmd(endpoint, method="POST")["inKey"]

    def get_community_id(self, community_keyword):
        endpoint = "/community/v1.0/communityIdUrlPathByUrlPathArtistCode"
        params = {"keyword": community_keyword}
        return self._call_wmd(endpoint, params)["communityId"]

    def get_post(self, post_id):
        endpoint = f"/post/v1.0/post-{post_id}"
        params = {"fieldSet": "postV1"}
        headers = self._headers()
        if not headers.get("Authorization"):
            endpoint, params = self._apply_no_auth(endpoint, params)
        return self._call_wmd(endpoint, params, headers=headers)

    def get_media_video_list(self, video_id, master_id):
        in_key = self.get_in_key(video_id)
        url = f"{self.VOD_API_URL}/vod/play/v2.0/{master_id}"
        params = {"key": in_key}
        res = self._call(url, params=params)
        return res["videos"]["list"]

    def get_post_video_list(self, video_id):
        endpoint = f"/cvideo/v1.0/cvideo-{video_id}/playInfo"
        params = {"videoId": video_id}
        res = self._call_wmd(endpoint, params)
        return res["playInfo"]["videos"]["list"]

    def get_member_posts(self, member_id):
        endpoint = f"/post/v1.0/member-{member_id}/posts"
        params = {
            "fieldSet": "postsV1",
            "filterType": "DEFAULT",
            "limit": 20,
            "sortType": "LATEST",
        }
        return self._pagination(endpoint, params)

    def get_feed_posts(self, community_keyword, feed_name):
        community_id = self.get_community_id(community_keyword)
        endpoint = f"/post/v1.0/community-{community_id}/{feed_name}TabPosts"
        params = {
            "fieldSet": "postsV1",
            "limit": 20,
            "pagingType": "CURSOR",
        }
        return self._pagination(endpoint, params)

    def get_latest_community_media(self, community_keyword):
        community_id = self.get_community_id(community_keyword)
        endpoint = f"/media/v1.0/community-{community_id}/more"
        params = {
            "fieldSet": "postsV1",
            "filterType": "RECENT",
        }
        return self._pagination(endpoint, params)

    def get_membership_community_media(self, community_keyword):
        community_id = self.get_community_id(community_keyword)
        endpoint = f"/media/v1.0/community-{community_id}/more"
        params = {
            "fieldSet": "postsV1",
            "filterType": "MEMBERSHIP",
        }
        return self._pagination(endpoint, params)

    def get_all_community_media(self, community_keyword):
        community_id = self.get_community_id(community_keyword)
        endpoint = f"/media/v1.0/community-{community_id}/searchAllMedia"
        params = {
            "fieldSet": "postsV1",
            "sortOrder": "DESC",
        }
        return self._pagination(endpoint, params)

    def get_media_by_category_id(self, category_id):
        endpoint = f"/media/v1.0/category-{category_id}/mediaPosts"
        params = {
            "fieldSet": "postsV1",
            "sortOrder": "DESC",
        }
        return self._pagination(endpoint, params)

    def get_member_moments(self, member_id):
        endpoint = f"/post/v1.0/member-{member_id}/posts"
        params = {
            "fieldSet": "postsV1",
            "filterType": "MOMENT",
            "limit": 1,
        }
        return self._pagination(endpoint, params)

    def validate_access_token(self, access_token=None):
        headers = self._token_headers(access_token)
        if headers.get("Authorization"):
            url = f"{self.ACCOUNT_BASE_API_URL}/api/v1/token/validate"
            return self._call(url, headers=headers)
        return {}

    def refresh_access_token(self, access_token=None, refresh_token=None):
        headers = self._token_headers(access_token)
        token = refresh_token or self.extr.cookies.get(self.extr.cookies_names[1], domain=self.extr.cookies_domain)
        if headers.get("Authorization") and token:
            url = f"{self.ACCOUNT_BASE_API_URL}/api/v1/token/refresh"
            data = {"refreshToken": token}
            return self._call(url, method="POST", headers=headers, json=data)
        return {}

    def _call(self, url, **kwargs):
        try:
            while True:
                return self.extr.request(url, **kwargs).json()
        except exception.HttpError as exc:
            if exc.response.status_code == HTTPStatus.UNAUTHORIZED:
                raise exception.AuthenticationError from None
            if exc.response.status_code == HTTPStatus.FORBIDDEN:
                msg = "Access token is invalid or Post requires membership"
                raise exception.AuthorizationError(msg) from None
            if exc.response.status_code == HTTPStatus.NOT_FOUND:
                raise exception.NotFoundError(self.extr.subcategory) from None
            self.extr.log.debug(exc)
            return None

    def _call_wmd(self, endpoint, params=None, headers=None, **kwargs):
        if params is None:
            params = {}
        params.update(
            {
                "appId": self.APP_ID,
                "language": "en",
                "os": "WEB",
                "platform": "WEB",
                "wpf": "pc",
            },
        )
        # The param order is important for the message digest
        params = OrderedDict(sorted(params.items()))
        timestamp = int(time.time() * 1000)
        message_digest = self._message_digest(endpoint, params, timestamp)
        params.update(
            {
                "wmsgpad": timestamp,
                "wmd": message_digest,
            },
        )
        return self._call(
            f"{self.WMD_API_URL}{endpoint}",
            params=params,
            headers=headers or self._headers(),
            **kwargs,
        )

    def _pagination(self, endpoint, params=None, headers=None):
        headers = headers or self._headers()
        if not headers.get("Authorization"):
            raise exception.AuthenticationError
        if params is None:
            params = {}
        while True:
            res = self._call_wmd(endpoint, params, headers=headers)
            for post in res["data"]:
                if not self._is_text_only(post):
                    yield post
            np = res.get("paging", {}).get("nextParams", {})
            if "after" not in np:
                return
            params["after"] = np["after"]
