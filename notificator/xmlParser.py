import xml.dom.minidom
import logging

logging.basicConfig(filename="xmlBody.log", filemode="w", level=logging.INFO)


def xmlParser(file, content_length):
  try:
    print('Starting parsing')
    body = file.read(content_length)

    logging.info(body)

    DOMTree = xml.dom.minidom.parseString(body)
    videos = DOMTree.getElementsByTagName("entry")

    if len(videos) == 1:
      title = videos[0].getElementsByTagName("title")[0].childNodes[0].data
      link = videos[0].getElementsByTagName("link")[0].getAttribute("href")
      channelId = videos[0].getElementsByTagName("yt:channelId")[0].childNodes[0].data
      print('Finished parsing')
      return (link, title, channelId)
    else:
      return ('no <entry> element in DOM',)
  except Exception as e:
    print("Error occured while xml parsing:\n", e)
    return (f"Error occured while xml parsing:\n{e}", )
  