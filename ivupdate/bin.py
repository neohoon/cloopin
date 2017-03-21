import pysrt

subs = pysrt.open("contents/output.en.srt")

idx = 0
while idx + 1 < len(subs):
    print str(idx) + " : " + str(subs[idx].text)
    print str(idx+1) + " : " + str(subs[idx+1].text)
    if not subs[idx].text:
        del subs[idx]
    elif subs[idx].text.split("\n")[-1] == subs[idx+1].text.split("\n")[0]:
        print str(subs[idx].start) + " ~ " + str(subs[idx].end)
        print str(subs[idx+1].start) + " ~ " + str(subs[idx+1].end)
        wgt = 1. / (subs[idx+1].text.count("\n") + 1.)
        subs[idx].end.seconds = \
            int((1 - wgt) * subs[idx+1].start.seconds +
                wgt * (subs[idx+1].end.seconds + 60 * (subs[idx+1].start.minutes - subs[idx+1].end.minutes)))
        subs[idx+1].start = subs[idx].end
        subs[idx+1].text = subs[idx+1].text.split("\n")[1::]
        print str(idx) + " : " + str(subs[idx].text)
        print str(idx+1) + " : " + str(subs[idx+1].text)
        print str(subs[idx].start) + " ~ " + str(subs[idx].end)
        print str(subs[idx+1].start) + " ~ " + str(subs[idx+1].end)
        idx += 1
    else:
        idx += 1
    print
subs.save("output_en.srt", encoding='utf-8')


