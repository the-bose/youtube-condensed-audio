#!/usr/bin/env python
import os
import shutil
import configparser
import pysrt
import ffmpeg
from pytube import YouTube, Caption

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
    # Downloads audio and subs
    #
    try:
        shutil.rmtree("cache")
    except:
        pass
    finally:
        os.makedirs("cache/slices")
        os.makedirs("cache/final_slices")

    try:
        index=0
        yt = YouTube(cfg.link)
        title = yt.title
        streams = yt.streams.filter(only_audio=True)
        captions = yt.captions
        for cap in captions:
            if "auto-generated" not in str(cap):
                caption = cap
                break

        print("Downloading video : ", title)
        streams[0].download(output_path="cache", filename=str(index))

        print("Downloading subtitles...")
        with open("cache/"+str(index)+".srt", "w") as f:
            f.write(caption.generate_srt_captions())

        print("Slicing video's audio...")
        slice_audio(index)

        print("Combining all files...")
        combine_all(index, title)

        print("CONDENSED AUDIO CREATED SUCCESSFULLY")
    except Exception as e:
        print("ERROR IN SETTING UP")
        print(e)
        print("TRY AGAIN OR CHECK THE VIDEO URL...")
    finally:
        shutil.rmtree("cache")

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

def combine_all(final_index, file_name):
    #
    # Combines all the output audio and sets speed
    #
    try:
        old_file = "cache/final_slices/"+str(final_index)+".mp3"
        file_name = "".join(_ for _ in file_name if _.isalnum())+".mp3"
        (
            ffmpeg
            .input(old_file)
            .filter("atempo", cfg.speed)
            .output(file_name)
            .run(quiet=True)
        )
    except Exception as e:
        print("ERROR IN COMBINING FINAL AUDIO", e)

if __name__ == "__main__":
    configure()
    main()
