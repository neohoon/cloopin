from urllib import quote as quote
from urllib2 import urlopen as urlopen
from bs4 import BeautifulSoup
from pafy import new as pafy__new
import UtilityModel as UtilityModel
from os import system as shell
import MyUtility
import requests


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


# ----------------------------------------------------------------------------------------------------------------------
def get_youtube_view_count(vid):

    # https://www.googleapis.com/youtube/v3/videos?
    #   id=7lCDEYXw3mM
    #   &key=AIzaSyAWbrlhdFPDDVrNRnONzg5mnQyVOhGNV-A
    #   &part=snippet,contentDetails,statistics,status

    req_url = "https://www.googleapis.com/youtube/v3/videos?id=" + vid + "&key=" + DEVELOPER_KEY + "&part=statistics"
    r = requests.get(req_url)
    if r.status_code == 200:
        return int(r.json()['items'][0]['statistics']['viewCount'].encode('utf-8'))
    return -1


# ----------------------------------------------------------------------------------------------------------------------
def check_subtitle_type(video_url):

    options = " --list-subs "
    shell("youtube-dl " + options + video_url + " >youtube_dl.log 2>&1")
    log_str = list(open('youtube_dl.log', 'r'))
    subtitle_on = True
    if [i for i, s in enumerate(log_str) if 'WARNING: video doesn\'t have subtitles' in s]:
        subtitle_on = False
    auto_on = True
    if [i for i, s in enumerate(log_str) if 'WARNING: Couldn\'t find automatic captions' in s]:
        auto_on = False

    if not subtitle_on:
        if not auto_on:
            return 0
        else:
            return 1
    return 2


# ----------------------------------------------------------------------------------------------------------------------
def download_youtube_video(url, out_filename_core, logger=None):

    shell("rm " + out_filename_core + ".* 2>/dev/null")

    options  = " -o output.%\(ext\)s "
    options += " -f bestvideo[ext=mp4]+bestaudio[ext=mp3]/best[ext!=webm] -k "
    if logger: logger.info("   > Downloading video...")
    shell("youtube-dl " + options + url + " >youtube_dl.log 2>&1")

    log_str = list(open('youtube_dl.log', 'r'))
    return log_str[[i for i, s in enumerate(log_str) if 'Destination' in s if 'download' in s][0]].split(":")[1].strip()


# ----------------------------------------------------------------------------------------------------------------------
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
    video_list = []
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
        video_list = []
        channels = []
        playlists = []
        # Add each result to the appropriate list,
        # and then display the lists of matching videos, channels, and playlists.
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                video_list.append("%s (%s)" % (search_result["snippet"]["title"], search_result["id"]["videoId"]))
            elif search_result["id"]["kind"] == "youtube#channel":
                channels.append("%s (%s)" % (search_result["snippet"]["title"], search_result["id"]["channelId"]))
            elif search_result["id"]["kind"] == "youtube#playlist":
                playlists.append("%s (%s)" % (search_result["snippet"]["title"], search_result["id"]["playlistId"]))
        print "Videos:\n", "\n".join(video_list), "\n"
        print "Channels:\n", "\n".join(channels), "\n"
        print "Playlists:\n", "\n".join(playlists), "\n"
        '''
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                video = UtilityModel.Video()
                video.title = search_result['snippet']['title'].encode('utf-8')
                video.creator = search_result['snippet']['channelTitle'].encode('utf-8')
                video.creatorId = search_result['snippet']['channelId'].encode('utf-8')
                video.vid = search_result['id']['videoId'].encode('utf-8')
                video.thumbnail = search_result['snippet']['thumbnails']['default']['url'].encode('utf-8')
                video.url = "https://www.youtube.com/watch?v=" + video.vid
                video.genre = query
                video_info = pafy__new(video.url)
                if video_info.viewcount > min_view_count:
                    video_list.append(video)
    return video_list


# ----------------------------------------------------------------------------------------------------------------------
def youtube_search_by_channel(query='Google', max_channel_results=25, max_video_results=25, min_view_count=1000,
                              video_db=None, logger=None):
    """
    :param query:
    :param max_channel_results:
    :param max_video_results:
    :param min_view_count:
    :param video_db:
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
    while len(channel_list) < max_channel_results and channel_cond:

        # Call the search.list method to retrieve results matching the specified query term.
        channel_query = query + ", channel"
        remained_channel = max_channel_results - len(channel_list)
        requested_channel = 50 if remained_channel > 50 else remained_channel
        channel_search = youtube.search().list(q=channel_query, part="id,snippet", pageToken=channel_next_token,
                                               maxResults=requested_channel).execute()
        replied_channel = len(channel_search['items'])
        for channel_result in channel_search.get("items", []):
            if channel_result["id"]["kind"] == "youtube#channel":
                channel_list.append({'id': channel_result['snippet']['channelId'].encode('utf-8'),
                                     'title': channel_result['snippet']['channelTitle'].encode('utf-8')})
        logger.info(" # YouTube channel search with " + channel_query + " : " + str(remained_channel) + " -> " +
                    str(requested_channel) + " -> " + str(replied_channel) + " -> " + str(len(channel_list)))
        channel_next_token = channel_search.get('nextPageToken')
        if channel_next_token is None:
            channel_cond = False
        '''
        video_list = []
        channels = []
        playlists = []
        # Add each result to the appropriate list,
        # and then display the lists of matching videos, channels, and playlists.
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                video_list.append("%s (%s)" % (search_result["snippet"]["title"], search_result["id"]["videoId"]))
            elif search_result["id"]["kind"] == "youtube#channel":
                channels.append("%s (%s)" % (search_result["snippet"]["title"], search_result["id"]["channelId"]))
            elif search_result["id"]["kind"] == "youtube#playlist":
                playlists.append("%s (%s)" % (search_result["snippet"]["title"], search_result["id"]["playlistId"]))
        print "Videos:\n", "\n".join(video_list), "\n"
        print "Channels:\n", "\n".join(channels), "\n"
        print "Playlists:\n", "\n".join(playlists), "\n"
        '''
    video_list = []
    for channel_info in channel_list:
        video_next_token = None
        video_cond = True
        init_videos = len(video_list)
        while (len(video_list) - init_videos) < max_video_results and video_cond:

            channel_id = channel_info['id']
            channel_title = channel_info['title']
            video_query = query + ", video"

            remained_videos = max_video_results - (len(video_list) - init_videos)
            requested_videos = 50 if remained_videos > 50 else remained_videos
            video_response = youtube.search().list(channelId=channel_id, part="id,snippet", pageToken=video_next_token,
                                                   maxResults=requested_videos).execute()
            replied_videos = len(video_response['items'])
            if replied_videos == 0:
                break

            db_skip_count = 0
            view_skip_count = 0
            for video_result in video_response.get("items", []):
                if video_result["id"]["kind"] == "youtube#video":
                    video = UtilityModel.ModelVideo(
                                host='YouTube',
                                vid=video_result['id']['videoId'].encode('utf-8'),
                                url="https://www.youtube.com/watch?v=" + video_result['id']['videoId'].encode('utf-8'),
                                title=video_result['snippet']['title'].encode('utf-8'),
                                genre=query,
                                thumbnail=video_result['snippet']['thumbnails']['default']['url'].encode('utf-8'),
                                creator=video_result['snippet']['channelTitle'].encode('utf-8'),
                                creator_id=video_result['snippet']['channelId'].encode('utf-8'))
                    '''
                    if video_db:
                        if video_db.filter(vid=video.vid).exists():
                            db_skip_count += 1
                            continue
                    '''
                    try:
                        if get_youtube_view_count(video.vid) > min_view_count:
                            video_list.append(video)
                        else:
                            view_skip_count += 1
                    except Exception as e:
                        logger.info(" @ Error in pafy__new: " + video.url)
                        logger.info(e)
                        view_skip_count += 1
            logger.info(" # YouTube video search in \"" + channel_title + "\" with " + video_query + " : " +
                        str(remained_videos) + " -> " + str(requested_videos) + " -> " + str(replied_videos) +
                        " -> DB skip : " + str(db_skip_count) + ", view skip : " + str(view_skip_count) +
                        ", video : " + str(len(video_list) - init_videos) + " -> " + str(len(video_list)))

            video_next_token = video_response.get('nextPageToken')
            if video_next_token is None:
                video_cond = False

    return video_list


def main__youtube_search_by_keyword():
    argparser.add_argument("--q", help="Search term", default="Google")
    argparser.add_argument("--max-results", help="Max results", default=25)
    args = argparser.parse_args()

    try:
        video_list = youtube_search_by_channel(args.q, args.max_results)
        for k in range(len(video_list)):
            print("%s by %s : %s" % (video_list[k]['title'], video_list[k]['creator'], video_list[k]['url']))
    except HttpError, e:
        print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)


########################################################################################################################
########################################################################################################################
########################################################################################################################

if __name__ == "__main__":

    main__youtube_search_by_keyword()
