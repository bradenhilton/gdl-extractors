from extractor import topstarnews

BASE_URL_PATTERN = r"^https://cdn\.topstarnews\.net/news/photo/"
FILE_EXTENSIONS = r"\.(?:gif|jpe?g|png|webp)$"


__tests__ = (
    {
        "#url": "https://www.topstarnews.net/news/articleView.html?idxno=15543685",
        "#comment": "a current (at time of writing) article",
        "#category": ("", "topstarnews", "article"),
        "#class": topstarnews.TopstarnewsArticleExtractor,
        "#pattern": rf"{BASE_URL_PATTERN}\d+/[\d_]+_org{FILE_EXTENSIONS}",
        "#count": 1,
        "date": "dt:2024-09-11 10:54:00",
        "title": "레드벨벳 웬디, ‘리본 하트 해달랬더니 근육 몽몽이가 돼버린 와니’ (웬디의 영스트리트 출근길)",
        "tags": ["웬디", "WENDY", "영스트리트", "출근", "퇴근", "프리뷰"],
        "author": "최규석",
        "post_id": "15543685",
        "post_url": "https://www.topstarnews.net/news/articleView.html?idxno=15543685",
    },
    {
        "#url": "https://www.topstarnews.net/news/articleView.html?idxno=30789",
        "#comment": "an old article",
        "#category": ("", "topstarnews", "article"),
        "#class": topstarnews.TopstarnewsArticleExtractor,
        "#pattern": rf"{BASE_URL_PATTERN}first/\d+/[a-z\d_]+{FILE_EXTENSIONS}",
        "#count": 1,
        "date": "dt:2012-04-24 06:45:00",
        "title": "걸스데이(Girls Day) 혜리, '남자들은 다 똑같아!' 깜찍한 무대 …MBC MUSIC 쇼 챔피언 생방송 현장",
        "author": "최규석",
        "post_id": "30789",
        "post_url": "https://www.topstarnews.net/news/articleView.html?idxno=30789",
    },
)
