from typing import List

HOST, PORT = '0.0.0.0', 37015

MAX_ACTIVE_TIME: int = int(5 * 60)

GLOBAL_INTERCEPT = True

PASS_URL: List[str] = (
    '/login', 
    '/regist',
)

PASS_URL_PREFIX: List[str] = (
    '/static/nologin',
)