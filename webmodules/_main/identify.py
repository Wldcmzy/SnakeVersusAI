import uuid
import time
from typing import Dict
from .config import MAX_ACTIVE_TIME, PASS_URL, PASS_URL_PREFIX

class Cookie:
    def __init__(self, value = None):
        self.time = time.time()
        if not value:
            self.value = uuid.uuid4()
        else:
            self.value = value
    
    def update(self):
        self.time = time.time()
    
    def check_overdue(self):
        return int(time.time()) - self.time > MAX_ACTIVE_TIME

cookie_dict: Dict[str, Cookie] = {}

def check_cookie(username: str, cookie: Cookie) -> bool:
    if username not in cookie_dict: return False
    cookie = cookie_dict[username]
    if cookie.check_overdue():
        del cookie_dict[username]
        return False
    cookie.update()
    cookie_dict[username] = cookie
    return True

def identify(username: str, password: str) -> bool:
    return True

def judge_pass_url(url : str) -> bool:
    if url in PASS_URL: 
        return True
    for each in PASS_URL_PREFIX: 
        if url.startswith(each): 
            return True 
    return False



