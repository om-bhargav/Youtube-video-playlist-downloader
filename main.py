import tkinter as tk
from pytubefix import YouTube,Playlist
import os
import re
import subprocess
from threading import Thread
import sys

def resource_path(relative_path):
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

loading_window = None 
def show_loading(text="Downloading..."):
    global loading_win
    loading_win = tk.Toplevel(app)
    loading_win.title("Please wait")
    loading_win.geometry("300x120")
    # disable close button
    loading_win.protocol("WM_DELETE_WINDOW", lambda: None)

    # make it modal (optional but recommended)
    loading_win.transient(app)
    loading_win.grab_set()
    loading_win.resizable(False, False)

    tk.Label(
        loading_win,
        text=text,
        font=("calibri", 14)
    ).pack(expand=True, pady=30)


def stop_loading():
    global loading_win
    if(loading_win):
        loading_win.destroy()
        loading_win = None


def download_video(stream,path=None):
    video = stream.streams.filter(file_extension='mp4', res="720p").first()
    stream.title = re.sub(r"[^a-zA-Z0-9\s]","",stream.title)
    if(not video):
        video = stream.streams.get_highest_resolution()
    audio = stream.streams.filter(only_audio=True).first()
    video.download(filename="tmp.mp4")
    audio.download(filename="tmp.aac")
    if(path):
        path = os.path.join(path,stream.title+".mp4")
    else:
        path = stream.title+".mp4"
    ffmpeg = resource_path("ffmpeg/bin/ffmpeg.exe")
    subprocess.run([
      ffmpeg,
      "-y",
      "-i", "tmp.mp4",
      "-i", "tmp.aac",
      "-map", "0:v:0",
      "-map", "1:a:0",
      "-c", "copy",
      "-shortest",
      path
    ], check=True)
    os.remove("tmp.mp4")
    os.remove("tmp.aac")

def download():
    url = var1.get()
    if url.strip() == "":
        print("Url Not Found!")
        return

    show_loading(
        "Downloading Video..." if var.get() == 1 else "Downloading Playlist..."
    )
    def task():
        try:
            if(var.get()==1):
                video = YouTube(url)
                download_video(video)
            elif(var.get()==2):
                playlist = Playlist(url)
                if(not os.path.exists(playlist.title)):
                    os.mkdir(playlist.title)
                for i in playlist.video_urls:
                    download_video(YouTube(i,use_oauth=False),playlist.title)
            else:
                return
        except Exception as e:
            print("Error Occoured!")
        finally:
            app.after(0,stop_loading)
            app.after(0, lambda: var1.set(""))
    
    Thread(target=task,daemon=True).start()
app = tk.Tk()
app.title("Youtube Video Downloader")
app.geometry("700x800")
app.resizable(False,False)
heading = tk.Label(app,text="Download Any Youtube Video You Want!",font="calibri 20 bold")
heading.pack(pady=20)
var1 = tk.Variable(app)
subHeading = tk.Label(app,text="Enter Youtube Url:",font="calibri 18 bold")
subHeading.pack(pady=5)
textBox = tk.Entry(app,textvariable=var1,font="calibri 16")
var = tk.IntVar()
option1 = tk.Radiobutton(app,text="Video",variable=var,value=1,font="15")
option1.pack()
option2 = tk.Radiobutton(app,text="Playlist",variable=var,value=2,font="15")
option2.pack()
textBox.pack(ipadx=30,pady=5)
btn = tk.Button(app,text="Download",font="30",foreground="white",background="black",command=download)
btn.pack(pady=5,ipadx=100,ipady=5)
app.mainloop()