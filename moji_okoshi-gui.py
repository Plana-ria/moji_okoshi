import whisper
from datetime import timedelta
import sys
import time
import tkinter
from tkinter import filedialog
from time import sleep
import asyncio
import os

import tqdm

from inaSpeechSegmenter import Segmenter
from pydub import AudioSegment

idir = '~/'

root = tkinter.Tk()
root.title("文字起こし")
root.geometry("400x550")
root.resizable(0, 0)


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
        
        # load audio and pad/trim it to fit 30 seconds
        audio = whisper.load_audio(".temp.wav")
        audio = whisper.pad_or_trim(audio)

        # make log-Mel spectrogram and move to the same device as the model
        mel = whisper.log_mel_spectrogram(audio).to(model.device)

        # detect the spoken language
        #_, probs = model.detect_language(mel)
        #print(f"Detected language: {max(probs, key=probs.get)}")

        # decode the audio
        options = whisper.DecodingOptions(language="ja")
        result = whisper.decode(model, mel, options)

        start = str(timedelta(seconds=int(segment[1]+time_log))).split(':')
        end = str(timedelta(seconds=int(segment[2]+time_log))).split(':')
            
        text += '{:02}:{:02}:{:02}'.format(int(start[0]),int(start[1]),int(start[2]))+"〜"+'{:02}:{:02}:{:02}'.format(int(end[0]),int(end[1]),int(end[2])) + ": "+result.text+"\n"
        
        """
        for data in result["segments"]:
            start = str(timedelta(seconds=int(data['start']+time_log))).split(':')
            
            if len(result["segments"]) == data['id']+1:
                end = str(timedelta(seconds=int(segment[2]+time_log))).split(':')
            else:
                end = str(timedelta(seconds=int(data['end']+time_log))).split(':')
            
            text += '{:02}:{:02}:{:02}'.format(int(start[0]),int(start[1]),int(start[2]))+"〜"+'{:02}:{:02}:{:02}'.format(int(end[0]),int(end[1]),int(end[2])) + ": "+data['text']+"\n"
        """
        time_log = segment[2]
        del newAudio

    f = open(name.rsplit(".",1)[0]+'.txt', 'w')
    f.write(text)
    f.close()
    os.remove('.temp.wav')

    t2 = time.time()
    log['state'] = 'normal'
    log.insert(tkinter.END, "\n"+"処理時間: "+str(timedelta(seconds=t2-t1))+" s")
    log.insert(tkinter.END, "\n"+"Output: "+name.rsplit(".",1)[0]+'.txt')
    log['state'] = 'disabled'




def check():
    global text_box
    data1 =text_box.get( 0., tkinter.END ).split("\n")
    data2 = []
    for i, s in enumerate(data1):
        if s!="" and (s not in data2):
            data2.append(s)
        
    text_box.delete(0., tkinter.END)
    for i, add in enumerate(data2):
        if i != 0:
            text_box.insert(tkinter.END, "\n"+add)
        else:
            text_box.insert(tkinter.END, add)

def select():
    global idir
    sleep(0.5)
    filetype = [("音楽",["*.mp3","*.wav","*.m4a","*.webm"]), ("すべて","*")]
    file_paths = tkinter.filedialog.askopenfilename(filetypes = filetype, initialdir = idir, multiple=True)

    for file_path in file_paths:
        text_box.insert(tkinter.END, "\n"+file_path)
    check()
    #idir = '~/'


def start():
    button_start['state'] = 'disabled'
    asyncio.new_event_loop().run_in_executor(None, task)

def task():
    while True:
        button_file['state'] = 'disabled'
        text_box['state'] = 'disabled'
        data1 = text_box.get( 0., tkinter.END ).split("\n")
        if data1[0]=='':
            log['state'] = 'normal'
            log.insert(tkinter.END, "\n"+'finished')
            log['state'] = 'disabled'
            text_box['state'] = 'normal'
            button_file['state'] = 'normal'
            break

        text_box['state'] = 'normal'
        text_box.delete(0., tkinter.END)
        for i, add in enumerate(data1[1:]):
            if i != 0:
                text_box.insert(tkinter.END, "\n"+add)
            else:
                text_box.insert(tkinter.END, add)
        
        button_file['state'] = 'normal'
        
        try:
            log['state'] = 'normal'
            log.insert(tkinter.END, "\n\n"+'Start: '+data1[0])
            log['state'] = 'disabled'
            moji_okoshi(data1[0])
            log['state'] = 'normal'
            log.insert(tkinter.END, "\n"+'End: '+data1[0])
            log['state'] = 'disabled'
        except:
            log['state'] = 'normal'
            log.insert(tkinter.END, "\n"+'Error: '+data1[0],"error")
            log['state'] = 'disabled'
    button_start['state'] = 'normal'

def exit():
    sys.exit()
    root.destroy()


label = tkinter.Label(text="文字起こし", font=("MSゴシック", "45", "bold"), foreground='#000000')
label.pack()

button_file = tkinter.Button(text='ファイルを選択', width=1000, command=select)
button_file.pack()

text_box = tkinter.Text(width=1000, height=20)
text_box.pack()

button_start = tkinter.Button(text='文字起こし開始', width=1000, command=start)
button_start.pack()

log = tkinter.Text(width=1000,height=10)
log.pack()


log.insert(tkinter.END, 'APP START')
log.tag_config("error", foreground="red") # background="red", 
log['state'] = 'disabled'

button_end = tkinter.Button(text='終了', width=1000,command=exit)
button_end.pack()

root.mainloop()