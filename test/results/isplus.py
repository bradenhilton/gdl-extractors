from extractor import isplus

BASE_URL_PATTERN = r"^https://isplus\.com/data/isp/image/"
FILE_EXTENSIONS = r"\.(?:gif|jpe?g|png|webp)$"


__tests__ = (
    {
        "#url": "https://isplus.com/article/view/isp202503100405",
        "#comment": "a current (at time of writing) article",
        "#category": ("", "isplus", "article"),
        "#class": isplus.IsplusArticleExtractor,
        "#pattern": rf"{BASE_URL_PATTERN}\d{{4,}}/\d{{2}}/\d{{2}}/isp\d+{FILE_EXTENSIONS}",
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
        "#pattern": rf"{BASE_URL_PATTERN}\d{{4,}}/\d{{2}}/\d{{2}}/isp\d+{FILE_EXTENSIONS}",
        "#count": 1,
        "date": "dt:2018-11-05 07:21:29",
        "post_id": "isp201811050264",
        "post_url": "https://isplus.com/article/view/isp201811050264",
    },
)
