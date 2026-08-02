import os

IS_CI = "CI" in os.environ and "GITHUB_ACTIONS" in os.environ


def ci_skip(reason):
    return reason if IS_CI else None


def ci_sleep(ci_duration, extractor):
    return ci_duration if IS_CI else extractor.request_interval
