from urllib import quote as quote
from urllib2 import urlopen as urlopen
from bs4 import BeautifulSoup
from pafy import new as pafy__new


class VideoInfo(object):
    title = None
    creator = None
    creatorId = None
    date = None
    vid = None
    thumbnail = None
    url = None
    genre = None

def youtube_search_by_web_key_word(key_word):
    query = quote(key_word)
    url = "https://www.youtube.com/results?search_query=" + query
    response = urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, "lxml")
    url_list = []
    for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
        url_list.append('https://www.youtube.com' + vid['href'])
    return url_list

########################################################################################################################

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps tab of
# https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "AIzaSyAWbrlhdFPDDVrNRnONzg5mnQyVOhGNV-A"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


def youtube_search_by_video(query='Google', max_results=25, min_view_count=1000, logger=None):
    """

    :param query:
    :param max_results:
    :param min_view_count:
    :param logger:
    :return list of video information dictionary:

    WHAT TO UPDATE

    The current version (160821) only handles the YouTube video search by youtube#video.
    In the near future, this MUST be upgraded to handle the youtube#channel.

    The current version (160821) only uses the search ordering from YouTube search results without any modification.
    In the near future, this MUST consider the view count in the list of the search results.

    """

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
    yt_next_token = None
    videos = []
    cond = True
    # search_order = 'viewCount'  # date / rating / relevance / title / videoCount / viewCount
    while max_results != 0 and cond:

        num_results = 50 if max_results > 50 else max_results
        max_results -= num_results

        video_query = query + ", video"
        logger.info(" # YouTube search: " + video_query + " - " + str(num_results))
        # Call the search.list method to retrieve results matching the specified query term.
        search_response = youtube.search().list(q=video_query, part="id,snippet", pageToken=yt_next_token,
                                                maxResults=num_results).execute()
        yt_next_token = search_response.get('nextPageToken')
        if yt_next_token is None:
            cond = False
        '''
        videos = []
        channels = []
        playlists = []
        # Add each result to the appropriate list,
        # and then display the lists of matching videos, channels, and playlists.
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                videos.append("%s (%s)" % (search_result["snippet"]["title"], search_result["id"]["videoId"]))
            elif search_result["id"]["kind"] == "youtube#channel":
                channels.append("%s (%s)" % (search_result["snippet"]["title"], search_result["id"]["channelId"]))
            elif search_result["id"]["kind"] == "youtube#playlist":
                playlists.append("%s (%s)" % (search_result["snippet"]["title"], search_result["id"]["playlistId"]))
        print "Videos:\n", "\n".join(videos), "\n"
        print "Channels:\n", "\n".join(channels), "\n"
        print "Playlists:\n", "\n".join(playlists), "\n"
        '''
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                video = VideoInfo()
                video.title = search_result['snippet']['title'].encode('utf-8')
                video.creator = search_result['snippet']['channelTitle'].encode('utf-8')
                video.creatorId = search_result['snippet']['channelId'].encode('utf-8')
                video.date = search_result['snippet']['publishedAt'].encode('utf-8')
                video.vid = search_result['id']['videoId'].encode('utf-8')
                video.thumbnail = search_result['snippet']['thumbnails']['default']['url'].encode('utf-8')
                video.url = "https://www.youtube.com/watch?v=" + video.vid
                video.genre = query
                video_info = pafy__new(video.url)
                if video_info.viewcount > min_view_count:
                    videos.append(video)
    return videos


def youtube_search_by_channel(query='Google', max_channel_results=25, max_video_results=25, min_view_count=1000,
                              video_db=None, logger=None):
    """

    :param query:
    :param max_channel_results:
    :param max_video_results:
    :param min_view_count:
    :param logger:
    :return list of video information dictionary:

    WHAT TO UPDATE

    The current version (160821) only handles the YouTube video search by youtube#video.
    In the near future, this MUST be upgraded to handle the youtube#channel.

    The current version (160821) only uses the search ordering from YouTube search results without any modification.
    In the near future, this MUST consider the view count in the list of the search results.

    """

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
    channel_next_token = None
    channel_cond = True
    channel_list = []
    # channel_search_order = 'viewCount'  # date / rating / relevance / title / videoCount / viewCount
    # video_search_order = 'viewCount'  # date / rating / relevance / title / videoCount / viewCount
    while max_channel_results != 0 and channel_cond:

        # Call the search.list method to retrieve results matching the specified query term.
        channel_query = query + ", channel"
        num_channel_results = 50 if max_channel_results > 50 else max_channel_results
        channel_search = youtube.search().list(q=channel_query, part="id,snippet", pageToken=channel_next_token,
                                               maxResults=num_channel_results).execute()
        num_channel_results = len(channel_search['items'])
        pre_max_channel_results = max_channel_results
        max_channel_results -= num_channel_results
        for channel_result in channel_search.get("items", []):
            if channel_result["id"]["kind"] == "youtube#channel":
                channel_list.append({'id': channel_result['snippet']['channelId'].encode('utf-8'),
                                     'title': channel_result['snippet']['channelTitle'].encode('utf-8')})
        logger.info(" # YouTube channel search with " + channel_query + " : " + str(pre_max_channel_results) + " = " +
                    str(num_channel_results) + " + " + str(max_channel_results) + " -> " + str(len(channel_list)))
        channel_next_token = channel_search.get('nextPageToken')
        if channel_next_token is None:
            channel_cond = False
        '''
        videos = []
        channels = []
        playlists = []
        # Add each result to the appropriate list,
        # and then display the lists of matching videos, channels, and playlists.
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                videos.append("%s (%s)" % (search_result["snippet"]["title"], search_result["id"]["videoId"]))
            elif search_result["id"]["kind"] == "youtube#channel":
                channels.append("%s (%s)" % (search_result["snippet"]["title"], search_result["id"]["channelId"]))
            elif search_result["id"]["kind"] == "youtube#playlist":
                playlists.append("%s (%s)" % (search_result["snippet"]["title"], search_result["id"]["playlistId"]))
        print "Videos:\n", "\n".join(videos), "\n"
        print "Channels:\n", "\n".join(channels), "\n"
        print "Playlists:\n", "\n".join(playlists), "\n"
        '''
    videos = []
    max_video_results_ = max_video_results
    for channel_info in channel_list:
        video_next_token = None
        video_cond = True
        max_video_results = max_video_results_
        while max_video_results != 0 and video_cond:

            channel_id = channel_info['id']
            channel_title = channel_info['title']
            video_query = query + ", video"

            num_video_results = 50 if max_video_results > 50 else max_video_results
            video_response = youtube.search().list(channelId=channel_id, part="id,snippet", pageToken=video_next_token,
                                                   maxResults=num_video_results).execute()
            num_video_results      = len(video_response['items'])
            pre_max_video_results  = max_video_results
            max_video_results     -= num_video_results
            video_next_token = video_response.get('nextPageToken')
            if video_next_token is None:
                video_cond = False

            db_skip_count = 0
            view_skip_count = 0
            for video_result in video_response.get("items", []):
                if video_result["id"]["kind"] == "youtube#video":
                    video = VideoInfo()
                    video.title = video_result['snippet']['title'].encode('utf-8')
                    video.creator = video_result['snippet']['channelTitle'].encode('utf-8')
                    video.date = video_result['snippet']['publishedAt'].encode('utf-8')
                    video.vid = video_result['id']['videoId'].encode('utf-8')
                    video.thumbnail = video_result['snippet']['thumbnails']['default']['url'].encode('utf-8')
                    video.url = "https://www.youtube.com/watch?v=" + video.vid
                    video.genre = query
                    if video_db:
                        if video_db.filter(vid=video.vid).exists():
                            db_skip_count += 1
                            continue
                    try:
                        video_info = pafy__new(video.url)
                        if video_info.viewcount > min_view_count:
                            videos.append(video)
                        else:
                            view_skip_count += 1
                    except Exception as e:
                        logger.info(" @ Error in pafy__new: " + video.url)
                        logger.info(e)
                        # videos.append(video)
            logger.info(" # YouTube video search in \"" + channel_title + "\" with " + video_query + " : " +
                        str(pre_max_video_results) + " = " + str(num_video_results) + " + " + str(max_video_results) +
                        " -> DB skip : " + str(db_skip_count) + ", view skip : " + str(view_skip_count) +
                        ", video : " + str(len(videos)))
            pass

    return videos


def main__youtube_search_by_keyword():
    argparser.add_argument("--q", help="Search term", default="Google")
    argparser.add_argument("--max-results", help="Max results", default=25)
    args = argparser.parse_args()

    try:
        videos = youtube_search_by_channel(args.q, args.max_results)
        for k in range(len(videos)):
            print("%s by %s : %s" % (videos[k]['title'], videos[k]['creator'], videos[k]['url']))
    except HttpError, e:
        print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)


########################################################################################################################
########################################################################################################################
########################################################################################################################

if __name__ == "__main__":

    main__youtube_search_by_keyword()
