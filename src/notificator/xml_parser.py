import logging
from typing import BinaryIO

from defusedxml.minidom import parseString

logger = logging.getLogger("xmlParser")


def xml_parser(file: BinaryIO, content_length: int) -> list[str]:
    body = file.read(content_length)
    logger.info(body)

    dom_tree = parseString(body)
    videos = dom_tree.getElementsByTagName("entry")

    if len(videos) == 1:
        title = videos[0].getElementsByTagName("title")[0].childNodes[0].data
        link = videos[0].getElementsByTagName("link")[0].getAttribute("href")
        channel_id = videos[0].getElementsByTagName("yt:channelId")[0].childNodes[0].data
        logger.info("Finished parsing: " + title + " " + link + " " + channel_id)
        return [link, title, channel_id]
    return ["no <entry> element in DOM", "", ""]
