from extractor import dispatch

IMAGE_URL_PATTERN = r"(?i)https://dispatch\.cdnser\.be/cms-content/uploads/\d+/\d+/\d+/.*\.(?:gif|jpe?g|png|webp)"


__tests__ = (
    {
        "#url": "https://www.dispatch.co.kr/2305635",
        "#category": ("", "dispatch", "article"),
        "#class": dispatch.DispatchArticleExtractor,
        "#pattern": IMAGE_URL_PATTERN,
        "#count": 5,
        "title": '[현장포토] "고당도 스윗"...제이, 하트 플러팅',
        "date": "dt:2024-09-14 01:29:29",
    },
)
