from extractor import news1

IMAGE_URL_PATTERN = r"(?i)https://(?:image|i\d+n)\.news1\.kr/system/photos/\d+/\d+/\d+/\d+/original\.jpg"


__tests__ = (
    {
        "#url": "https://www.news1.kr/photos/6909559",
        "#category": ("", "news1", "article"),
        "#class": news1.News1ArticleExtractor,
        "#pattern": IMAGE_URL_PATTERN,
        "#count": 1,
        "title": "트와이스 다현, 유혹",
        "author": "권현진",
        "date": "dt:2024-10-03 11:48:20",
        "article_id": "6909559",
        "post_url": "https://www.news1.kr/photos/6909559",
        "filename": "6909559",
    },
    {
        "#url": "https://www.news1.kr/entertain/movie/5557784",
        "#category": ("", "news1", "article"),
        "#class": news1.News1ArticleExtractor,
        "#pattern": IMAGE_URL_PATTERN,
        "#count": 7,
        "title": "박정민에 웃고, 故이선균에 울고…희비공존한 제29회 개막식(종합)",
        "author": "정유진",
        "article_id": "5557784",
        "post_url": "https://www.news1.kr/entertain/movie/5557784",
    },
    {
        "#url": "https://www.news1.kr/photos/2734432",
        "#category": ("", "news1", "article"),
        "#class": news1.News1ArticleExtractor,
        "#pattern": IMAGE_URL_PATTERN,
        "#count": 1,
        "title": "드림캐쳐 지유, 미모 갑 '여신'",
        "author": "권현진",
        "article_id": "2734432",
        "post_url": "https://www.news1.kr/photos/2734432",
        "filename": "2734432",
    },
    {
        "#url": "https://www.news1.kr/photos/6155497",
        "#category": ("", "news1", "article"),
        "#class": news1.News1ArticleExtractor,
        "#pattern": IMAGE_URL_PATTERN,
        "#count": 1,
        "title": "조유리, 요염한 눈빛",
        "article_id": "6155497",
        "post_url": "https://www.news1.kr/photos/6155497",
        "filename": "6155497",
    },
)
