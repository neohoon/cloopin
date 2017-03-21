#!/usr/bin/env python
"""
    NOTE
    WHAT TO DO

"""
########################################################################################################################

import pysrt

########################################################################################################################


########################################################################################################################


class ModelVideo(object):

    def __init__(self, host=None,
                 url=None, vid=None, title=None, genre=None, thumbnail=None,
                 creator=None, creator_id=None,
                 sub_on=False, sub_type=0, sub_lan=None, sub_script=None,
                 vid_text_on=False, width=0, height=0, fps=0., frame_num=0):

        self.host = host
        self.url = url

        self.vid = vid
        self.title = title
        self.genre = genre
        self.thumbnail = thumbnail

        self.creator = creator
        self.creator_id = creator_id

        self.sub_on = sub_on
        self.sub_type = sub_type
        self.sub_lan = sub_lan
        self.sub_script = sub_script

        self.vid_text_on = vid_text_on
        self.width = width
        self.height = height
        self.fps = fps
        self.frame_num = frame_num


# ----------------------------------------------------------------------------------------------------------------------
def update_or_create_video_db(video, video_db):

    tar_videos = video_db.objects.filter(url=video.url)

    if not tar_videos:
        video_db(host='YouTube',
                 url=video.url,
                 vid=video.vid,
                 title=video.title,
                 genre=video.genre,
                 thumbnail=video.thumbnail,
                 creator=video.creator,
                 creator_id=video.creator_id).save()
    else:
        for k in range(1,len(tar_videos)):
            video_db.objects.filter(pk=tar_videos[k].pk).delete()
        video_db.objects.filter(pk=tar_videos[0].pk).update(host='YouTube',
                                                            url=video.url,
                                                            vid=video.vid,
                                                            title=video.title,
                                                            genre=video.genre,
                                                            thumbnail=video.thumbnail,
                                                            creator=video.creator,
                                                            creator_id=video.creator_id)
    return video_db.objects.filter(url=video.url)[0].pk


# ------------------------------------------------------------------------------------------------------------------
def save_video_info_to_db(video_list, script_filename, video_db):
    if not video_db.objects.filter(url=video_list.url):
        scripts = open(script_filename, 'r').read()
        video_db(url=video_list.url,
                 host='YouTube',
                 title=video_list.title,
                 creator=video_list.creator,
                 vid=video_list.vid,
                 genre=video_list.genre,
                 thumbnail=video_list.thumbnail,
                 script=scripts,
                 ).save()


# ----------------------------------------------------------------------------------------------------------------------
def save_to_subtitle_db(srt_filename, video_pk, video_db, cap_db):
    subs = pysrt.open(srt_filename)
    for k in range(len(subs)):
        cap_db(video=video_db.objects.get(pk=video_pk),
               script=subs[k].text,
               time_start=convert_to_second(subs[k].start),
               time_end=convert_to_second(subs[k].end),
               ).save()


# ----------------------------------------------------------------------------------------------------------------------
def save_to_img_text_db(img_text_filename, video_pk, video_db, cap_db):
    subs = pysrt.open(img_text_filename)
    for k in range(len(subs)):
        cap_db(video=video_db.objects.get(pk=video_pk),
               script=subs[k].text,
               frame_num=subs[k].text,
               time_start=convert_to_second(subs[k].start),
               time_end=convert_to_second(subs[k].end),
               ).save()


# ----------------------------------------------------------------------------------------------------------------------
def convert_to_second(time_info):
    return (time_info.hours * 60 + time_info.minutes) * 60 + time_info.seconds


# ----------------------------------------------------------------------------------------------------------------------
def delete_duplicated_items_in_video_model(video_db):
    idx = 1
    while idx <= video_db.objects.last().pk:
        tar_video = video_db.objects.filter(pk=idx)
        if tar_video:
            tar_videos = video_db.objects.filter(url=tar_video[0].url)
            if tar_videos:
                for k in range(1,len(tar_videos)):
                    video_db.objects.filter(pk=tar_videos[k].pk).delete()
        idx += 1
    pass


# ----------------------------------------------------------------------------------------------------------------------
def check_duplicated_items_in_video_model(video_db):
    idx = 1
    while idx <= video_db.objects.last().pk:
        tar_video = video_db.objects.filter(pk=idx)
        if tar_video:
            tar_videos = video_db.objects.filter(url=tar_video[0].url)
            if len(tar_videos) > 1:
                for k in range(1, len(tar_videos)):
                    print(" @ Duplicated items: {:d} - {}".format(tar_videos[k].id,
                                                                  tar_videos[k].title.encode('utf-8')))
        idx += 1
    pass
