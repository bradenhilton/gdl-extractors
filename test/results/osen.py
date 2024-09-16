from extractor import osen

IMAGE_URL_PATTERN = r"(?i)https://file\.osen\.co\.kr/article/\d+/\d+/\d+/.*\.(?:gif|jpe?g|png|webp)"


__tests__ = (
    {
        "#url": "https://www.osen.co.kr/article/G1112319784",
        "#category": ("", "osen", "article"),
        "#class": osen.OsenArticleExtractor,
        "#pattern": IMAGE_URL_PATTERN,
        "#count": 1,
        "title": "(여자)아이들 미연 '사랑스럽게'",
        "date": "dt:2024-04-18 16:32:00",
    },
)
