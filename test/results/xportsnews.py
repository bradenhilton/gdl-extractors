from extractor import xportsnews

IMAGE_URL_PATTERN = (
    r"(?i)https://image\.xportsnews\.com/contents/images/upload/article/\d+/\d+/\d+\.(?:gif|jpe?g|png|webp)"
)


__tests__ = (
    {
        "#url": "https://www.xportsnews.com/article/1907588",
        "#category": ("", "xportsnews", "article"),
        "#class": xportsnews.XportsnewsArticleExtractor,
        "#pattern": IMAGE_URL_PATTERN,
        "#count": 1,
        "title": "있지 유나 '곱게 땋은 머리'[엑's HD포토]",
        "date": "dt:2024-09-23 00:56:13",
    },
)
