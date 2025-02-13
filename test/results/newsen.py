from extractor import newsen

BASE_URL_PATTERN = r"^https://photo.newsen.com/news_photo/"
FILE_EXTENSIONS = r"\.(?:gif|jpe?g|png|webp)$"


__tests__ = (
    {
        "#url": "https://newsen.com/news_view.php?uid=202411010854493510",
        "#category": ("", "newsen", "article"),
        "#class": newsen.NewsenArticleExtractor,
        "#pattern": rf"{BASE_URL_PATTERN}\d+/\d+/\d+/\d+_\d{FILE_EXTENSIONS}",
        "#count": 1,
        "date": "dt:2024-10-31 23:54:56",
        "title": "드림캐쳐 수아 ‘러블리 핑크 공주’[포토엔HD]",
        "post_id": "202411010854493510",
        "post_url": "https://newsen.com/news_view.php?uid=202411010854493510",
    },
)
