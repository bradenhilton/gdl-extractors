from extractor import bntnews

IMAGE_URL_PATTERN = r"(?i)https://www\.bntnews\.co\.kr/data/bnt/image/\d+/\d+/\d+/.*\.(?:gif|jpe?g|png|webp)"


__tests__ = (
    {
        "#url": "https://www.bntnews.co.kr/article/view/bnt202409150018",
        "#category": ("", "bntnews", "article"),
        "#class": bntnews.BntnewsArticleExtractor,
        "#pattern": IMAGE_URL_PATTERN,
        "#count": 1,
        "title": "‘영탁쇼’ 영탁, 관객 사연에 눈시울 붉혔다",
        "author": "송미희",
        "date": "dt:2024-09-15 02:38:13",
    },
    {
        "#url": "https://www.bntnews.co.kr/Brand%20News/article/view/bnt202409120086",
        "#category": ("", "bntnews", "article"),
        "#class": bntnews.BntnewsArticleExtractor,
        "#pattern": IMAGE_URL_PATTERN,
        "#count": 2,
        "title": "이가자헤어비스, 싱가포르 ‘2024 KAO SALON ASIA EXPERIENCE 갈라쇼’ 무대 서다",
        "author": "정혜진",
        "date": "dt:2024-09-14 00:00:01",
    },
    {
        "#url": "https://www.bntnews.co.kr/Photo/article/view/bnt202409130107",
        "#category": ("", "bntnews", "article"),
        "#class": bntnews.BntnewsArticleExtractor,
        "#pattern": IMAGE_URL_PATTERN,
        "#count": 1,
        "title": "후쿠모토 타이세이 '팬심 자극하는 스윗한 보이스' (일본 전국 투어 콘서트 '욘모지) [포토]",
        "author": "김도윤",
        "date": "dt:2024-09-13 09:05:04",
    },
    {
        "#url": "https://img.bntnews.co.kr/Photo/article/view/bnt202409300099",
        "#category": ("", "bntnews", "article"),
        "#class": bntnews.BntnewsArticleExtractor,
        "#pattern": IMAGE_URL_PATTERN,
        "#count": 1,
        "title": "최예나 '다같이 신나게' [포토]",
        "author": "김치윤",
        "date": "dt:2024-09-30 07:55:59",
    },
)
