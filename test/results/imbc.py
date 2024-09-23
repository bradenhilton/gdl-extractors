from extractor import imbc

IMAGE_URL_PATTERN = (
    r"(?i)https://talkimg\.imbc\.com/TVianUpload/tvian/TViews/image/\d+/\d+/\d+/.+\.(?:gif|jpe?g|png|webp)"
)


__tests__ = (
    {
        "#url": "https://adenews.imbc.com/M/Detail/431009",
        "#category": ("", "imbc", "adenews-article"),
        "#class": imbc.ImbcAdenewsArticleExtractor,
        "#pattern": IMAGE_URL_PATTERN,
        "#count": 40,
        "title": "[움짤] 아이브 안유진, 숨 참고 럽럽~",
        "date": "dt:2024-09-22 17:11:00",
    },
    {
        "#url": "https://enews.imbc.com/News/RetrieveNewsInfo/431009",
        "#category": ("", "imbc", "enews-article"),
        "#class": imbc.ImbcEnewsArticleExtractor,
        "#pattern": IMAGE_URL_PATTERN,
        "#count": 40,
        "title": "[움짤] 아이브 안유진, 숨 참고 럽럽~",
        "date": "dt:2024-09-22 17:11:00",
    },
    {
        "#url": "https://imnews.imbc.com/news/2024/enter/article/6639093_36473.html",
        "#category": ("", "imbc", "imnews-article"),
        "#class": imbc.ImbcImnewsArticleExtractor,
        "#pattern": IMAGE_URL_PATTERN,
        "#count": 40,
        "title": "[움짤] 아이브 안유진, 숨 참고 럽럽~",
        "date": "dt:2024-09-22 17:11:52",
    },
)
