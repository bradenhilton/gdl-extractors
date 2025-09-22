from extractor import sbsprograms

IMAGE_URL_PATTERN = r"(?i)(?:https?://)(?:(?:photocloud|image\.cloud|image\.board|board)\.)?sbs\.co\.kr/(?:[^/]+/)*.*\.(?:gif|jpe?g|png|webp)"


__tests__ = (
    {
        "#url": "https://programs.sbs.co.kr/enter/gayo/visualboard/54795?cmd=view&board_no=461896",
        "#category": ("", "sbsprograms", "article"),
        "#class": sbsprograms.SbsprogramsArticleExtractor,
        "#pattern": IMAGE_URL_PATTERN,
        "#count": 14,
        "title": "[Comeback] LE SSERAFIM - Swan Song + EASY",
        "date": "dt:2024-02-26 08:00:24",
        "views": int,
    },
    {
        "#url": "https://programs.sbs.co.kr/fune/theshow/visualboard/58358?cmd=view&board_no=635",
        "#category": ("", "sbsprograms", "article"),
        "#class": sbsprograms.SbsprogramsArticleExtractor,
        "#comment": "THE SHOW",
        "#pattern": IMAGE_URL_PATTERN,
        "#count": 15,
        "title": "모두를 미소 짓게 만드는 스마일 히어로 예나의 행복 파워 듬뿍 담긴 발랄한 무대 YENA(최예나)",
        "date": "dt:2022-01-26 05:16:37",
        "views": int,
    },
    {
        "#url": "https://programs.sbs.co.kr/fune/theshow/visualboard/58358?cmd=view&page=1&board_no=312",
        "#category": ("", "sbsprograms", "article"),
        "#class": sbsprograms.SbsprogramsArticleExtractor,
        "#comment": "image.board.sbs.co.kr URLs",
        "#pattern": IMAGE_URL_PATTERN,
        "#count": 23,
        "title": "여기가 바로 스페인이고 더쇼가 누울 자리! 홀릴 것만 같은 마성의 탱고로 돌아온 카리스마 여신들 (여자)아이들",
        "date": "dt:2019-03-06 00:15:11",
        "views": int,
    },
    {
        "#url": "https://programs.sbs.co.kr/enter/gayo/visualboard/54795?cmd=view&page=1&board_no=460841",
        "#category": ("", "sbsprograms", "article"),
        "#class": sbsprograms.SbsprogramsArticleExtractor,
        "#comment": "Inkigayo",
        "#pattern": IMAGE_URL_PATTERN,
        "#count": 9,
        "title": "[미션포토] YENA(최예나) (2)",
        "date": "dt:2023-07-07 06:07:07",
        "views": int,
    },
    {
        "#url": "https://programs.sbs.co.kr/enter/2024sbsgayosummer/visualboard/83075?cmd=view&page=1&board_no=8687",
        "#category": ("", "sbsprograms", "article"),
        "#class": sbsprograms.SbsprogramsArticleExtractor,
        "#pattern": IMAGE_URL_PATTERN,
        "#count": 8,
        "title": "[현장포토] 잔나비X미연&민니 ((G)I-DLE) Special Stage",
        "date": "dt:2024-07-26 08:12:22",
        "views": int,
    },
)
