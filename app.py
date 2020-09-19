#!/usr/bin/env python
import configparser
import os
import re
import shutil

import ffmpeg
import pysrt
from pytube import Caption, Playlist, YouTube

import cfg


def configure():
    #
    # Reads config.txt file
    #
    config = configparser.ConfigParser()
    config.read("config.txt")

    cfg.link = config["parameters"]["link"]
    cfg.exclude_no_sub = config["parameters"]["exclude_no_sub"]
    cfg.speed = config["parameters"]["speed"]
    
    cfg.exclude_no_sub = True if cfg.exclude_no_sub.lower() == "true" else False
    cfg.speed = float(cfg.speed)

def main():
    #
    # Set up cache, check for video/playlist
    #
    try:
        shutil.rmtree("cache")
    except:
        pass
    finally:
        os.makedirs("cache/slices")
        os.makedirs("cache/final_slices")

    try:
        if "playlist" in cfg.link:
            title = playlist_processor()
        else:
            title = video_processor(cfg.link, 0)
        if(len(os.listdir("cache/final_slices"))):
            print("\nCombining all files...")
            combine_all(title)
    except Exception as e:
        print("AN EXCEPTION HAS OCCURRED")
        print(e)
    finally:
        shutil.rmtree("cache")
        input("Press any key to quit...")

def playlist_processor():
    #
    # Get each video from a playlist and process the video
    #
    try:
        playlist = Playlist(cfg.link)
        playlist._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")
        video_index = 0
        for video_url in playlist:
            print(f"\nProcessing video {video_index+1} of {len(playlist)}:")
            video_processor(video_url, video_index)
            video_index += 1
        return playlist.title()
    except Exception as e:
        print("ERROR SETTING UP PLAYLIST")
        print(e)
        print("CHECK THE PLAYLIST URL AND TRY AGAIN...")

def video_processor(video_link, index):
    #
    # Downloads audio and subs
    #
    try:
        yt = YouTube(video_link)
        title = yt.title
        streams = yt.streams.filter(only_audio=True)
        captions = yt.captions
        caption = None
        for cap in captions:
            if "auto-generated" not in str(cap):
                caption = cap
                break

        if caption == None:
            if cfg.exclude_no_sub:
                print("NOT DOWNLOADING (NO SUBS) : ", title)
                return yt.title

        print("Downloading video : ", title)
        streams[0].download(output_path="cache", filename=str(index))

        if caption == None:
            print("NO SUBTITLES FOUND FOR : ", title)
            move_audio(index)
        else:
            print("Downloading subtitles...")
            with open("cache/"+str(index)+".srt", "w", encoding="utf-8") as f:
                f.write(caption.generate_srt_captions())

            print("Slicing video's audio...")
            slice_audio(index)
        return yt.title
    except Exception as e:
        print("ERROR IN SETTING UP")
        print(e)
        print("TRY AGAIN OR CHECK THE VIDEO URL...")

def slice_audio(file_index):
    #
    # Slices and combines the file's audio based on the timestamps from the subs
    #
    try:
        audio_file = "cache/"+str(file_index)+".mp4"
        subs = pysrt.open("cache/"+str(file_index)+".srt")
        output_prefix = "cache/slices/"+str(file_index)+"-"
        slice_index = 0
        for sub in subs:
            print(" + Slicing subtitle {} of {}".format(slice_index+1, len(subs)), end="\r", flush=True)
            start_time = sub.start.to_time()
            end_time = sub.end.to_time()
            (
                ffmpeg
                .input(audio_file)
                .filter_('atrim', start=start_time, end=end_time)
                .filter_('asetpts', 'PTS-STARTPTS')
                .output(output_prefix+str(slice_index)+".mp3")
                .run(quiet=True)
            )
            slice_index+=1
        print("\n   + All subtitles sliced....")

        print(" + Combining slices...")
        slices_list_string = '|'.join(list(map(lambda x : output_prefix+str(x)+".mp3", range(slice_index))))
        (
            ffmpeg
            .input("concat:{}".format(slices_list_string))
            .output("cache/final_slices/"+str(file_index)+".mp3")
            .run(quiet=True)
        )

    except Exception as e:
        print("ERROR IN SLICING VIDEO", e)

def move_audio(file_index):
    #
    # Converts and moves file that has been downloaded without captions
    #
    (
        ffmpeg
        .input("cache/"+str(file_index)+".mp4")
        .output("cache/final_slices/"+str(file_index)+".mp3")
        .run(quiet=True)
    )

def combine_all(file_name):
    #
    # Combines all the output audio and sets speed
    #
    try:
        location = "cache/final_slices/"
        old_files = "|".join([location + _ for _ in os.listdir(location)])
        file_name = "".join(_ for _ in file_name if _.isalnum())+".mp3"
        (
            ffmpeg
            .input(f"concat:{old_files}")
            .filter("atempo", cfg.speed)
            .output(file_name)
            .run(quiet=True, overwrite_output=True)
        )
        print("CONDENSED AUDIO CREATED SUCCESSFULLY")
    except Exception as e:
        print("ERROR IN COMBINING FINAL AUDIO :", e)

if __name__ == "__main__":
    configure()
    main()
