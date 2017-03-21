from django.db import models
from datetime import date


class Video(models.Model):

    host = models.CharField(max_length=64, default="YouTube", blank=False)
    url = models.URLField(max_length=256, default="", blank=False)
    vid = models.CharField(max_length=256, default="", blank=False)

    title = models.CharField(max_length=256, blank=True)
    genre = models.CharField(max_length=64, blank=True)
    thumbnail = models.URLField(max_length=1024, blank=True)

    creator = models.CharField(max_length=256, blank=True)
    creator_id = models.CharField(max_length=256, blank=True)

    sub_on = models.BooleanField(default=False)
    sub_script = models.TextField(blank=True)
    sub_lan = models.TextField(blank=True, max_length=2)        # ISO 639.2-1 Code.
    sub_type = models.IntegerField(default=1)                   # 0: No, 1: Auto, 2: Manual
    sub_date = models.DateField(default=date.today)

    vid_text_on = models.BooleanField(default=False)
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    fps = models.FloatField(default=0)
    frame_num = models.IntegerField(default=0)
    vid_text_date = models.DateField(default=date.today)

    def __str__(self):
        return self.title + " by " + self.creator


class Subtitle(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    script = models.TextField(max_length=1023, blank=True)
    time_start = models.IntegerField(default=0)
    time_end = models.IntegerField(default=0)

    def __str__(self):
        return self.video.title + " ( " + str(self.time_start) + " ~ " + str(self.time_end) + " ) "


class VidText(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    script = models.TextField(max_length=1023, blank=True)
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    frame_num = models.IntegerField(default=0)
    time_start = models.IntegerField(default=0)
    time_end = models.IntegerField(default=0)

    def __str__(self):
        return self.video.title + " : " + str(self.frame_num)