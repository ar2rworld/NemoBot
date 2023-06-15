import logging
import os
import time

from requests import Session
from requests_html import HTMLSession
from telegram import Update
from telegram.ext import ContextTypes

from src.decorators.admin_only import admin_only
from src.errors.error_codes import MISSING_MESSAGE_OR_TEXT
from src.socials_interactions.linkedin2 import linkedin
from src.socials_interactions.twitter2 import twitter_post

error_logger = logging.getLogger("errorLogger")


def dec(s: str) -> dict:
    d = {}
    for i in s.split("&"):
        t = i.split("=")
        d[t[0]] = t[1]
    return d


def get_div_attribute_value(line: str, string: str) -> str:
    value_index = line.index(string)
    value_start = line[line.index(string) :].index('"') + 1 + value_index
    value_end = line[value_start:].index('"')
    value = line[value_start : value_start + value_end]
    return value


def find_tags(html: str, tag: str = "", tag_type: str = "") -> list[dict]:
    tags = []
    for line in html.split("\n"):
        if "<" + tag in line and tag_type in line:
            try:
                name = get_div_attribute_value(line, "name")
                value = get_div_attribute_value(line, "value")
                tags.append({"name": name, "value": value})
            except ValueError as v:
                error_logger.error(v)
    return tags


def find_value(s: str, key: str) -> str:
    try:
        st = s.index(key) + len(key) + 2
        end = s[st:].index(",") - 1
        # print(s[st:st+end])
        return s[st : st + end].replace("'", "").replace("\\ ", "")[1:]
    except ValueError as v_e:
        error_logger.error(f"Substring not found, probably smt went wrong also in findValue():\n{v_e}")
        raise v_e
    except Exception as e:
        error_logger.error(f"Error occured in findValue():\n{e}")
        raise e


def find_to_parameter(html: str) -> str:
    # in js page
    string = '"to":'
    for line in html.split("\n"):
        if string in line:
            # print(line)
            s = line.index(string) + len(string) + 1
            return line[s : s + line[s:].index('"')]
    return ""


def login_vk() -> tuple[HTMLSession, str]:
    s3 = HTMLSession()
    i = 0
    to = ""
    for i in range(20):
        time.sleep(i)
        r3 = s3.get("https://vk.com/")
        d = {}
        for tag in find_tags(r3.text, "input", "hidden"):
            d[tag["name"]] = tag["value"]
        # You email/phone and password
        d["email"] = os.getenv("VK_EMAIL")
        d["pass"] = os.getenv("VK_PASS")
        if i == 0:
            to = find_to_parameter(r3.text)
        d["to"] = to
        url = "https://login.vk.com/?act=login"
        r3 = s3.post(url, data=d)
        # print(r3.headers)
        has_sid = "remixsid" in r3.headers["Set-Cookie"]
        # print('remixsid : ', has_sid)
        if has_sid:
            uid = find_value(r3.text, "uid")
            return s3, uid
        to = find_to_parameter(s3.get("https://vk.com/im").text.replace("\\", ""))
    return HTMLSession(), ""


# loginVK()


def make_post(session: Session, uid: str, hash_string: str, message: str = "testing") -> str:
    post = (
        "act=post&to_id="
        + uid
        + "&type=all&friends_only=&best_friends_only=&close_comments=0"
        + "&mute_notifications=0&mark_as_ads=0&official=&signed=&hash="
        + hash_string
        + "&from=&fixed=461&update_admin_tips=0&al=1"
    )
    data_post = dec(post)
    data_post["Message"] = message
    r0 = session.post("https://vk.com/al_wall.php?act=post", data=data_post)
    return r0.text


@admin_only
async def post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.text is None:
        raise ValueError(MISSING_MESSAGE_OR_TEXT)
    if len(update.message.text.split(" ")) > 1:
        error_logger = context.application.bot_data["errorLogger"]
        message = update.message.text
        first_token = message.split(" ")[1]
        out = ""
        if "-" in first_token:
            second_space = message.index(" ", message.index(" ") + 1)
            message = message[second_space:]
            if "li" in first_token:
                out += linkedin(message) + "\n"
            if "vk" in first_token:
                s, uid = login_vk()
                if not s or not uid:
                    error_logger.error("Did not get a vk session or uid")
                else:
                    s.get(
                        "https://oauth.vk.com/authorize?client_id=7888891&display=page&redirect_uri=https://vk.com/ar2r.life&scope=8192&response_type=token&v=5.131&state=123456"
                    )
                    my_page_url = "https://vk.com/id" + uid
                    req_my_page = s.get(my_page_url)
                    post_hash = find_value(req_my_page.text, "post_hash")
                    await update.message.chat.send_message(f"logged in: {uid}")
                    if s is not None:
                        out += make_post(s, uid, post_hash, message) + "\n"
            if "tw" in first_token:
                twitter_post(message)
            await update.message.chat.send_message(out + "worked!")
        else:
            await update.message.chat.send_message("-[li][vk][tw] <message> required!")
    else:
        await update.message.chat.send_message("You are not my architector")
