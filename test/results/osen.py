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
    {
        "#url": "https://osen.co.kr/article/G1112452170",
        "#category": ("", "osen", "article"),
        "#class": osen.OsenArticleExtractor,
        "#pattern": IMAGE_URL_PATTERN,
        "#count": 1,
        "title": "에스타 윈터, 미소와 함께 퇴장",
        "date": "dt:2024-11-06 11:38:00",
    },
)
