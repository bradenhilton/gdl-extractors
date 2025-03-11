from extractor import isplus

BASE_URL_PATTERN = r"^https://isplus\.com/data/isp/image/"
FILE_EXTENSIONS = r"\.(?:gif|jpe?g|png|webp)$"
URL_PATTERN = rf"{BASE_URL_PATTERN}\d{{4,}}/\d{{2}}/\d{{2}}/isp[A-Za-z0-9-]+{FILE_EXTENSIONS}"


__tests__ = (
    {
        "#url": "https://isplus.com/article/view/isp202503100405",
        "#comment": "a current (at time of writing) article",
        "#category": ("", "isplus", "article"),
        "#class": isplus.IsplusArticleExtractor,
        "#pattern": URL_PATTERN,
        "#count": 1,
        "date": "dt:2025-03-10 08:00:44",
        "post_id": "isp202503100405",
        "post_url": "https://isplus.com/article/view/isp202503100405",
    },
    {
        "#url": "https://isplus.com/article/view/isp201811050264",
        "#comment": "an older article",
        "#category": ("", "isplus", "article"),
        "#class": isplus.IsplusArticleExtractor,
        "#pattern": URL_PATTERN,
        "#count": 1,
        "date": "dt:2018-11-05 07:21:29",
        "post_id": "isp201811050264",
        "post_url": "https://isplus.com/article/view/isp201811050264",
    },
    {
        "#url": "https://isplus.com/article/view/isp202205020255",
        "#category": ("", "isplus", "article"),
        "#class": isplus.IsplusArticleExtractor,
        "#pattern": URL_PATTERN,
        "#count": 1,
        "date": "dt:2022-05-02 06:59:56",
        "post_id": "isp202205020255",
        "post_url": "https://isplus.com/article/view/isp202205020255",
    },
)
