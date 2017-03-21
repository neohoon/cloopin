#!/usr/bin/env python
"""
    NOTE

"""
########################################################################################################################

activate_this = "../../bin/activate_this.py"
execfile(activate_this, dict(__file__=activate_this))

########################################################################################################################

import os
import sys
import argparse
import logging
from django.utils.encoding import smart_str  # , smart_unicode
from shutil import copyfile
from pycaption import CaptionConverter, WebVTTReader, SRTWriter
from os import remove as removefile

from ivupdate import read_ivsearch_models, youtube_dl_subtitle_only, postprocessing_youtube_srt, save_srt_to_db

########################################################################################################################

DEBUG = 0
VIR_ENV_BIN_DIR = os.environ['HOME'] + "/Workspace/venv.cloopin/bin"
DJANGO_DIR = os.environ['HOME'] + "/Workspace/venv.cloopin/cloopin"

SUBTITLE_VTT_DIR = 'Subtitles.vtt/'
SUBTITLE_SRT_DIR = 'Subtitles.srt/'


global logger

########################################################################################################################
########################################################################################################################
########################################################################################################################


def check_num_of_videos(video_db, display=True):
    num_videos = len(video_db.objects.all())
    if display:
        print "\n # The total number of videos in DB : {0}\n".format(num_videos)
    return num_videos


def check_num_of_subtitles(video_db, filename, display=False):
    fid = open(filename, 'w')
    idx = 1
    for video in video_db.objects.all():
        try:
            string = "[{:<5d}] : {:5d} - ({:<5d}) : {}".format(idx, video.pk, len(video.subtitle_set.all()),
                                                               video.title.encode('utf-8'))
        except Exception as e:
            print e
        fid.writelines(string + "\n")
        if display:
            print string
        idx += 1
    fid.close()


def write_video_info(video_db, filename, display=False):
    fid = open(filename, 'w')
    for video in video_db.objects.all():
        try:
            string = "{} |$| {} |$| {} |$| {}".format(video.url, video.vid, video.title.encode('utf-8'),
                                                      video.creator.encode('utf-8'))
        except Exception as e:
            print e
        fid.writelines(string + "\n")
        if display:
            print string
    fid.close()


def write_video_db(video_db, filename, display=True):

    fid = open(filename, 'w')
    max_pk = video_db.objects.latest('pk').pk

    for k in range(1, max_pk+1):
        video = video_db.objects.filter(pk=k)
        if video.exists():
            string = "{:6d} |$| {} |$| {:.20} |$| {}".format(k+1, video[0].url, video[0].creator.encode('utf-8'),
                                                             video[0].title.encode('utf-8'))
        else:
            string = "{:6d} |$| ".format(k+1)
        fid.writelines(string + "\n")
        if display:
            print string
    fid.close()


def download_subtitles(video_info_filename):
    global logger
    logger.info(" # download_subtitles...")

    if not os.path.exists(SUBTITLE_VTT_DIR):
        os.makedirs(SUBTITLE_VTT_DIR)
    if not os.path.exists(SUBTITLE_SRT_DIR):
        os.makedirs(SUBTITLE_SRT_DIR)
    # num_lines = sum(1 for line in open(video_info_filename))
    with open(video_info_filename) as fp:
        idx = 0
        for line in fp:
            try:
                logger.info("   > {:d}-th video processing...".format(idx + 1))
                video_url = line.split("|$|")[0].strip()
                video_vid = line.split("|$|")[1].strip()
                vtt_filename   = SUBTITLE_VTT_DIR + video_vid + ".en.vtt"
                srt_filename   = SUBTITLE_SRT_DIR + video_vid + ".en.srt"
                srt_filename_p = SUBTITLE_SRT_DIR + video_vid + "_en.srt"
                if not os.path.exists(vtt_filename):
                    youtube_dl_subtitle_only(video_url, video_vid)
                    copyfile(video_vid + ".en.vtt", SUBTITLE_VTT_DIR + video_vid + ".en.vtt")
                    removefile(video_vid + ".en.vtt")

                # Convert vtt to srt...
                if not os.path.exists(srt_filename):
                    converter = CaptionConverter()
                    converter.read(unicode(open(vtt_filename, 'r').read(), "utf-8"), WebVTTReader())
                    open(srt_filename, 'w').write(smart_str(converter.write(SRTWriter())))
                if not os.path.exists(srt_filename_p):
                    postprocessing_youtube_srt(srt_filename, srt_filename_p)
            except Exception as e:
                logger.info(e)

            idx += 1


def update_subtitle_db(video_db, subtitle_db):

    global logger

    print(" ? Do you really want to delete subtitle DB(yes/no) ? "),
    ans = sys.stdin.read().lower().strip()
    if not ans == 'yes':
        print(" exit...\n")
        exit()
    subtitle_db.objects.all().delete()

    idx = 1
    for filename in os.listdir(SUBTITLE_SRT_DIR):
        logger.info("    > {:d} updating the Subtitle DB with {}".format(idx, filename))
        if filename[-7:] == "_en.srt":
            video_vid = filename[0:-7]
            video_pk = video_db.objects.filter(vid=video_vid).values('pk')[0]['pk']
            save_srt_to_db(SUBTITLE_SRT_DIR + filename, video_pk, video_db, subtitle_db)
        idx += 1


########################################################################################################################
########################################################################################################################
########################################################################################################################


if __name__ == "__main__":

    global logger

    if len(sys.argv) == 1:
        sys.argv.append("--help")

    parser = argparse.ArgumentParser(description="DB information")
    parser.add_argument("--num_videos", dest="num_videos", action='store_true', help="Number of videos", default=False)
    parser.add_argument("--num_subtitles", help="Number of subtitles", default=None)
    parser.add_argument("--write_video_info", help="Write video info", default=None)
    parser.add_argument("--write_video_db", help="Write video DB", default=None)
    parser.add_argument("--dl_subtitles", help="Download subtitles. Input argument is video info filename",
                        default=None)
    parser.add_argument("--update_subtitle_db", dest="update_subtitle_db", action="store_true",
                        help="Update subtitle DB with video information", default=None)

    parser.add_argument("--pp_subtitles", dest="pp_subtitles", action='store_true', help="Postprocessing subtitles",
                        default=False)
    # parser.add_argument("--merge_subtitles", dest="merge_subtitles", action='store_true', help="Merge subtitles",
    #                     default=False)
    # parser.add_argument("--q_keyword", help="Search term", default="makeup")
    # parser.add_argument("--q_keyword", help="Search term", default="makeup")
    # parser.add_argument("--max_channel_results", help="Max channel results", default=0)
    # parser.add_argument("--max_video_results", help="Max video results", default=25)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    log_handler = logging.FileHandler(__file__.split("/")[-1].split(".")[0] + ".log")
    log_handler.setLevel(logging.DEBUG)
    log_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(log_handler)

    model_db = read_ivsearch_models(DJANGO_DIR)
    video_db = model_db[0]
    subtitle_db = model_db[1]

    if args.num_videos:
        check_num_of_videos(video_db)

    if args.num_subtitles:
        check_num_of_subtitles(video_db, args.num_subtitles, display=True)

    if args.write_video_info:
        write_video_info(video_db, args.write_video_info, display=True)

    if args.write_video_db:
        write_video_db(video_db, args.write_video_db, display=True)

    if args.dl_subtitles:
        download_subtitles(args.dl_subtitles)

    if args.update_subtitle_db:
        update_subtitle_db(video_db, subtitle_db)

    # if args.merge_subtitles:
    #     merge_subtitles(args.merge_subtitles)
