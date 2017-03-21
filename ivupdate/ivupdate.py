#!/usr/bin/env python
"""
    NOTE
    * YouTube search tips
      > Ref: http://www.labnol.org/internet/youtube-search/19261/
      > to search video, channel, or playlist only, just add ", video, channel, or playlist" after search keywords.
      > to exclude video, channel, or playlist, just add ", -video, -channel, or -playlist" after search keywords.
    * youtube search order attribute doesn't work with channel only search or channel_id.
      I had to remove order attribute in YouTube search.
    * In YouTube video search with channel_id, max number of search results is "32", NOT "50.
    * In YouTube video search with channel_id, nextPageToken doesn't exist if query attribute exists.
      Thus, query attribute MIGHT not be defined in channel_id based video search.

    WHAT TO DO

"""
########################################################################################################################

import os
import sys
import argparse
from os import system as shell
import cv2
from pycaption import CaptionConverter, WebVTTReader, SRTWriter
import pysrt
import logging
from django.utils.encoding import smart_str     # , smart_unicode
from datetime import date

import UtilityModel as UtilityModel
import UtilityYouTube as UtilityYouTube
import MyUtility as MyUtility
from MyUtility import to_str, to_unicode

import VideoTextRecognition
import pickle


########################################################################################################################

DEBUG = 0
VIR_ENV_BIN_DIR = os.environ['HOME'] + "/Workspace/venv.cloopin/bin"
DJANGO_DIR = os.environ['HOME'] + "/Workspace/venv.cloopin/cloopin"

SUBTITLE_VTT_REPO = "/Subtitle.vtt"
SUBTITLE_SRT_REPO = "/Subtitle.srt"

FRAME_SKIP_SEC = 5

gLogger = None

########################################################################################################################


def prt(string):
    global DEBUG
    if DEBUG:
        print string


def run_virtual_env(folder):
    activate_this = folder + "/activate_this.py"
    execfile(activate_this, dict(__file__=activate_this))


def read_ivsearch_models(folder):
    sys.path.append(folder)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cloopin.settings")
    import django
    from django.core.wsgi import get_wsgi_application
    if django.get_version() >= '1.6':
        django.setup()
    get_wsgi_application()
    from ivsearch.models import Video, Subtitle, VidText
    return Video, Subtitle, VidText


def postprocessing_youtube_srt(srt_in_filename, srt_out_filename):

    subs = pysrt.open(srt_in_filename)
    idx = 0
    while idx + 1 < len(subs):
        if isinstance(subs[idx].text, list):
            subs[idx].text = "".join(subs[idx].text)
        if isinstance(subs[idx+1].text, list):
            subs[idx+1].text = "".join(subs[idx+1].text)
        prt(str(idx) + " : " + smart_str(subs[idx].text))
        prt(str(idx+1) + " : " + smart_str(subs[idx+1].text))
        if not subs[idx].text:
            del subs[idx]
        elif to_str(subs[idx].text).split("\n")[-1] == to_str(subs[idx+1].text).split("\n")[0]:
            prt(str(subs[idx].start) + " ~ " + smart_str(subs[idx].end))
            prt(str(subs[idx+1].start) + " ~ " + smart_str(subs[idx+1].end))
            wgt = 1. / (subs[idx+1].text.count("\n") + 1.)
            subs[idx].end.seconds = \
                int((1 - wgt) * subs[idx+1].start.seconds +
                    wgt * (subs[idx+1].end.seconds + 60 * (subs[idx+1].start.minutes - subs[idx+1].end.minutes)))
            subs[idx+1].start = subs[idx].end
            subs[idx+1].text = to_str(subs[idx+1].text).split("\n")[1::]
            prt(str(idx) + " : " + smart_str(subs[idx].text))
            prt(str(idx+1) + " : " + smart_str(subs[idx+1].text))
            prt(str(subs[idx].start) + " ~ " + smart_str(subs[idx].end))
            prt(str(subs[idx+1].start) + " ~ " + smart_str(subs[idx+1].end))
        else:
            idx += 1
    prt("")

    idx = 0
    while idx + 2 < len(subs):
        end_info = subs[idx].start + pysrt.SubRipTime(0,0,5,0)
        end_time = subs[idx].end
        while idx + 2 < len(subs):
            try:
                if subs[idx+1].start < end_info:
                    subs[idx].text = to_unicode(to_str(subs[idx].text) + " \n " + to_str(subs[idx+1].text))
                    end_time = subs[idx+1].end
                    del subs[idx+1]
                else:
                    break
            except Exception as e:
                print e
        subs[idx].end = end_time
        idx += 1

    subs.save(srt_out_filename, encoding='utf-8')


def merge_all_scripts(srt_in_filename, srt_out_filename):
    subs = pysrt.open(srt_in_filename)
    with open(srt_out_filename, 'w') as fid:
        for k in range(len(subs)):
            fid.write(subs[k].text.encode('utf-8') + " ")
    fid.close()


# ----------------------------------------------------------------------------------------------------------------------


def extract_texts_in_video(filename):
    print filename
    return filename


def youtube_dl_subtitle_only(video_url, srt_filename):

    options  = " -o " + srt_filename + ".%\(ext\)s "
    options += " --write-sub --sub-format srt --skip-download "
    shell("youtube-dl " + options + video_url + " >youtube_dl.log 2>&1")
    if check_string_in_file('youtube_dl.log', "WARNING: video doesn't have subtitles"):
        options  = " -o " + srt_filename + ".%\(ext\)s "
        options += " --write-auto-sub --sub-lang en --skip-download "
        shell("youtube-dl " + options + video_url + " >> youtube_dl.log 2>&1")


def check_string_in_file(filename, string):

    file_text = file(filename)
    for line in file_text:
        if string in line:
            return True
    return False


# ----------------------------------------------------------------------------------------------------------------------
def run_subtitle_processing(video_url, out_filename_core):

    global gLogger

    shell("rm output.* 2>/dev/null")

    # set youtube-dl options..
    options  = " -o " + out_filename_core + ".%\(ext\)s "
    options += " --write-sub --sub-format srt -k --skip-download "
    shell("youtube-dl " + options + video_url + " >youtube_dl.log 2>&1")

    # Name video and audio files...
    if check_string_in_file('youtube_dl.log', "WARNING: video doesn't have subtitles"):
        gLogger.info("   > Downloading auto-generated subtitle...")
        sub_type = 1
    else:
        sub_type = 2
    options  = " -o " + out_filename_core + ".%\(ext\)s "
    options += " --write-auto-sub --sub-lang en --skip-download "
    shell("youtube-dl " + options + video_url + " >> youtube_dl.log 2>&1")

    # Name subtitle file...
    try:
        log_str = list(open('youtube_dl.log', 'r'))
        vtt_filename = log_str[[i for i, s in enumerate(log_str) if 'Writing video subtitles to' in s][0]].split(":")[1].strip()
    except Exception as e:
        gLogger.info(" @ Error in reading youtube_dl.log")
        gLogger.info(e)
        return

    srt_filename = ".".join(vtt_filename.split(".")[:-1]) + ".srt"
    merge_srt_filename = '.'.join(srt_filename.split('.')[:-1]) + ".merge." + srt_filename.split('.')[-1]

    # Convert vtt to srt...
    gLogger.info("   > Converting subtitle from vtt to srt...")
    converter = CaptionConverter()
    converter.read(unicode(open(vtt_filename, 'r').read(), "utf-8"), WebVTTReader())
    open(srt_filename, 'w').write(smart_str(converter.write(SRTWriter())))

    # Post-processing youtube srt...
    gLogger.info("   > Post-processing subtitle...")
    postprocessing_youtube_srt(srt_filename, srt_filename)
    merge_all_scripts(srt_filename, merge_srt_filename)

    return vtt_filename, srt_filename, merge_srt_filename, 'en', sub_type


# ----------------------------------------------------------------------------------------------------------------------
def run_img_text_processing(video, in_vid_file_core):

    global gLogger

    in_vid_file = UtilityYouTube.download_youtube_video(video.url, in_vid_file_core, logger=gLogger)

    if not os.path.exists(in_vid_file):
        print(" @ Error: input video file not found {}".format(in_vid_file))
        sys.exit()

    try:
        video_stream = cv2.VideoCapture(in_vid_file)
        fps, width, height, tot_frame_num = MyUtility.get_video_stream_info(video_stream)
        out_vid_file = '.'.join(in_vid_file.split('.')[:-1]) + ".avi"
        video_writer = cv2.VideoWriter(out_vid_file, cv2.VideoWriter_fourcc(*'XVID'), 0.4, (2*width, height), 1)
    except Exception as e:
            print e
            sys.exit()

    # Loop
    frame_num = 0

    videoText = VideoTextRecognition.VideoTextRecognition(fps, width, height, tot_frame_num)
    videoInfoDB = VideoTextRecognition.VideoInfoDB(width, height, fps, tot_frame_num)
    video_text_db_list = []

    while cv2.waitKey(1) != ord('q'):

        flag, org_img = video_stream.read()
        if not flag:
            break
        frame_sec = int(frame_num / videoText.fps)

        print(" # {:d} frame in {:d} sec".format(frame_num, frame_sec)),

        if frame_num % int(videoText.fps * FRAME_SKIP_SEC) == 0:
            print("- text extraction...")
            videoText.extract_text_from_video(org_img, frame_num, frame_sec)
            for img_text in videoText.vid_text_list[-1].img_text_list:
                video_text_db_list.append(videoText.ImgText(img_text, frame_num, frame_sec))
            video_writer.write(videoText.overlay_all_texts(org_img, frame_num, frame_sec))
        else:
            print("")

        frame_num += 1

        if frame_num == tot_frame_num:
            print(" # End of video\n")
            break

    video_writer.release()

    # return vid_text_filename, width, height, fps, frame_num
    return "output", width, height, fps, frame_num


########################################################################################################################
#   LOCAL FUNCTIONS
########################################################################################################################

########################################################################################################################

def main(arg):

    global gLogger

    run_virtual_env(VIR_ENV_BIN_DIR)

    video_db, subtitle_db, img_text_db = read_ivsearch_models(DJANGO_DIR)

    if False:
        if arg.max_channel == 0:
            video_list = UtilityYouTube.youtube_search_by_video(arg.q_keyword, int(arg.max_video), logger=gLogger)
        else:
            video_list = UtilityYouTube.youtube_search_by_channel(arg.q_keyword, int(arg.max_channel),
                                                                  int(arg.max_video), video_db=video_db.objects,
                                                                  logger=gLogger)
        pickle.dump([video_list], open( arg.function_name + ".video_list.pkl", 'wb'), pickle.HIGHEST_PROTOCOL)
    else:
        video_list = pickle.load(open(arg.function_name + ".video_list.pkl", "rb"))[0]

    # UtilityModel.delete_duplicated_items_in_video_model(video_db)
    # UtilityModel.check_duplicated_items_in_video_model(video_db)

    # ------------------------------------------------------------------------------------------------------------------
    '''
    for k in range(0,len(video_list)):

        gLogger.info(" # %d-th video information processing with %s..." % (k+1, video_list[k].title))
        UtilityModel.update_or_create_video_db(video_list[k], video_db)
    '''

    # ------------------------------------------------------------------------------------------------------------------

    if arg.subtitle_on:
        for k in range(0,len(video_list)):

            gLogger.info(" # %d-th subtitle information processing with %s..." % (k+1, video_list[k].title))

            video_pk = video_db.objects.filter(url=video_list[k].url)[0].pk
            tar_video = video_db.objects.filter(pk=video_pk)

            if not tar_video[0].sub_on:

                subtitle_db.objects.filter(video=video_pk).delete()

                sub_type = UtilityYouTube.check_subtitle_type(video_list[k].url)

                if sub_type == 0:
                    gLogger.info("   > Even automatic generated subtitle does not exist.")
                    gLogger.info("     - DB update with sub_on = False")
                    tar_video.update(sub_on=True, sub_type=sub_type, sub_date=date.today())
                else:
                    gLogger.info("   > Subtitle processing...")
                    vtt_filename, srt_filename, merge_srt_filename, sub_lan, sub_type = \
                        run_subtitle_processing(tar_video[0].url, "yt." + tar_video[0].vid)
                    tar_video.update(sub_on=True,
                                     sub_type=sub_type,
                                     sub_lan=sub_lan,
                                     sub_date=date.today(),
                                     sub_script=open(merge_srt_filename, 'r').read()
                                     )
                    gLogger.info("   > Saving video subtitles to subtitle DB...")
                    UtilityModel.save_to_subtitle_db(srt_filename, video_pk, video_db, subtitle_db)
                    shell("mv " +       vtt_filename + " ./" + SUBTITLE_VTT_REPO)
                    shell("mv " +       srt_filename + " ./" + SUBTITLE_SRT_REPO)
                    shell("mv " + merge_srt_filename + " ./" + SUBTITLE_SRT_REPO)

    # ------------------------------------------------------------------------------------------------------------------
    if arg.vid_text_on:
        for k in range(0,len(video_list)):

            gLogger.info(" # %d-th image text information processing with %s..." % (k+1, video_list[k].title))

            video_pk = video_db.objects.filter(url=video_list[k].url)[0].pk
            tar_video = video_db.objects.filter(pk=video_pk)
            if tar_video[0].img_text_on:
                gLogger.info("   > Image text information was already created.")
            else:
                gLogger.info("   > Image text processing...")
                img_text_filename, width, height, fps, frame_num = run_img_text_processing(video_list[k])
                tar_video.update(img_text_on=True, width=width, height=height, fps= fps, frame_num=frame_num )
                UtilityModel.save_to_img_text_db(img_text_filename, video_pk, video_db, img_text_db)

########################################################################################################################

if __name__ == "__main__":

    function_name = __file__.split('/')[-1][:-3]
    gLogger = MyUtility.configure_logger('.'.join(__file__.split("/")[-1].split(".")[:-1]) + ".log", function_name,
                                         level=logging.DEBUG)

    gLogger.info(" # {} launched...".format(function_name))
    sys.argv.extend(["--q_keyword", "makeup cosmetics", "--max_channel", "100", "--max_video", "100", "--subtitle"])
    if len(sys.argv) == 1:
        sys.argv.append("--help")

    parser = argparse.ArgumentParser(description="in-video search DB update")
    parser.add_argument("--q_keyword", help="Search term", default="makeup")
    parser.add_argument("--max_channel", help="Max channel number", default=0)
    parser.add_argument("--max_video", help="Max video number", default=25)
    parser.add_argument("--subtitle", dest="subtitle_on", action='store_true', help="Run subtitle processing",
                        default=False)
    parser.add_argument("--vid_text", dest="vid_text_on", action='store_true', help="Run video text processing",
                        default=False)
    args = parser.parse_args()

    args.function_name = function_name

    main(args)

