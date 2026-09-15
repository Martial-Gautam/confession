"""Instagram Graph API (Instagram Login flavour): feed post/carousel + stories."""
import os
import time

import requests

API = "https://graph.instagram.com/v23.0"


def _call(method, path, **params):
    params["access_token"] = os.environ["IG_TOKEN"]
    r = requests.request(method, f"{API}/{path}", params=params, timeout=30)
    data = r.json()
    if "error" in data:
        raise RuntimeError(data["error"].get("message", data["error"]))
    return data


def _container(**params):
    return _call("POST", f"{os.environ['IG_USER_ID']}/media", **params)["id"]


def _wait(container_id, timeout=120):
    deadline = time.time() + timeout
    while time.time() < deadline:
        status = _call("GET", container_id, fields="status_code")["status_code"]
        if status == "FINISHED":
            return
        if status == "ERROR":
            raise RuntimeError(f"container {container_id} failed processing")
        time.sleep(3)
    raise TimeoutError(f"container {container_id} not ready after {timeout}s")


def _publish(container_id):
    _wait(container_id)
    return _call("POST", f"{os.environ['IG_USER_ID']}/media_publish", creation_id=container_id)["id"]


def post_feed(urls, caption):
    if len(urls) == 1:
        return _publish(_container(image_url=urls[0], caption=caption))
    children = [_container(image_url=u, is_carousel_item="true") for u in urls]
    for c in children:
        _wait(c)
    return _publish(_container(media_type="CAROUSEL", children=",".join(children), caption=caption))


def post_stories(urls):
    return [_publish(_container(media_type="STORIES", image_url=u)) for u in urls]
