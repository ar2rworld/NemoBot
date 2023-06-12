import logging
import xml.dom.minidom

logger = logging.getLogger("xmlParser")


def xmlParser(file, content_length):
    try:
        body = file.read(content_length)
        logger.info(body)

        DOMTree = xml.dom.minidom.parseString(body)
        videos = DOMTree.getElementsByTagName("entry")

        if len(videos) == 1:
            title = videos[0].getElementsByTagName("title")[0].childNodes[0].data
            link = videos[0].getElementsByTagName("link")[0].getAttribute("href")
            channelId = videos[0].getElementsByTagName("yt:channelId")[0].childNodes[0].data
            logger.info("Finished parsing: " + title + " " + link + " " + channelId)
            return (link, title, channelId)
        else:
            return ("no <entry> element in DOM", "", "")
    except Exception as e:
        return (f"Error occured while xml parsing:\n{e}", "", "")
