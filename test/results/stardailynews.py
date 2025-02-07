from extractor import stardailynews

BASE_URL_PATTERN = r"^https://cdn\.stardailynews\.co\.kr/news/photo/\d{6}/(?:\d+_){2}\d+"
FILE_EXTENSIONS = r"\.(?:gif|jpe?g|png|webp)$"


__tests__ = (
    {
        "#url": "https://www.stardailynews.co.kr/news/articleView.html?idxno=472259",
        "#comment": "a current (at time of writing) article",
        "#category": ("", "stardailynews", "article"),
        "#class": stardailynews.StardailynewsArticleExtractor,
        "#pattern": rf"{BASE_URL_PATTERN}{FILE_EXTENSIONS}",
        "#count": 1,
        "date": "dt:2025-02-03 07:19:53",
        "title": "[S포토] 아이브 안유진, '쿨미녀'",
        "post_id": "472259",
        "post_url": "https://www.stardailynews.co.kr/news/articleView.html?idxno=472259",
    },
    {
        "#url": "https://www.stardailynews.co.kr/news/articleView.html?idxno=19",
        "#comment": "an old article",
        "#category": ("", "stardailynews", "article"),
        "#class": stardailynews.StardailynewsArticleExtractor,
        "#pattern": rf"{BASE_URL_PATTERN}{FILE_EXTENSIONS}",
        "#count": 1,
        "date": "dt:2011-01-31 22:49:09",
        "title": "명불허전 '아테나'인천대교 전투씬 !",
        "post_id": "19",
        "post_url": "https://www.stardailynews.co.kr/news/articleView.html?idxno=19",
    },
)
