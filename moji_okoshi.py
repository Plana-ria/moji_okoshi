import whisper
from datetime import timedelta
import sys
import time
import os

from inaSpeechSegmenter import Segmenter
from pydub import AudioSegment


model = whisper.load_model("large")

def moji_okoshi(name):
    

    t1 = time.time()
    text = ""
    time_log = 0.0

    seg = Segmenter(vad_engine='smn', detect_gender=False)
    segmentation = seg(name)
    print(segmentation)
    
    for segment in segmentation:
        # 区間の開始時刻の単位を秒からミリ秒に変換
        start_time = segment[1] * 1000
        end_time = segment[2] * 1000

        # 分割結果をwavに出力
        newAudio = AudioSegment.from_file(name, format=name.rsplit(".",1)[1])
        newAudio = newAudio[start_time:end_time]
        newAudio.export(".temp.wav", format="wav")

        result = model.transcribe(".temp.wav")

        for data in result["segments"]:
            start = str(timedelta(seconds=int(data['start']+time_log))).split(':')
            
            if len(result["segments"]) == data['id']+1:
                end = str(timedelta(seconds=int(segment[2]+time_log))).split(':')
            else:
                end = str(timedelta(seconds=int(data['end']+time_log))).split(':')
            
            text += '{:02}:{:02}:{:02}'.format(int(start[0]),int(start[1]),int(start[2]))+"〜"+'{:02}:{:02}:{:02}'.format(int(end[0]),int(end[1]),int(end[2])) + ": "+data['text']+"\n"

        time_log = segment[2]
        del newAudio

    t2 = time.time()

    f = open(name.rsplit(".",1)[0]+'.txt', 'w')
    f.write(text)
    f.close()

    print("実行時間: "+str(t2-t1)+" s")

moji_okoshi(sys.argv[1])
os.remove('.temp.wav')