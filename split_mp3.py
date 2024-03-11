from moviepy.editor import AudioFileClip
import re, os
from json import loads
from pytube import YouTube


def get_description(video: YouTube) -> str:
    i: int = video.watch_html.find('"shortDescription":"')
    desc: str = '"'
    i += 20  # excluding the `"shortDescription":"`
    while True:
        letter = video.watch_html[i]
        desc += letter  # letter can be added in any case
        i += 1
        if letter == '\\':
            desc += video.watch_html[i]
            i += 1
        elif letter == '"':
            break
    return loads(desc)

def timestamp_to_secs(timestamp: str) -> int:
    parts = timestamp.split(':')
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    elif len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    else:
        return 0


def remove_prefix(x):
    filter_characters = "-_: "
    # Define the regex pattern to find the first character not in filter_characters
    pattern = r'[^' + re.escape(filter_characters) + ']'

    # Find the index of the first character not in filter_characters
    match = re.search(pattern, x)
    if match:
        index = match.start()
        return x[index:]
    else:
        return x  # No characters found that aren't in filter_characters



def formt_timestamps(video: YouTube) -> list:
    desc = get_description(video)
    length_secs = video.length
    timestamps_with_description = re.findall(r'(\d+:\d+(?::\d+)?)\s*(.*)', desc)
    timestamps_with_duration = []

    for i in range(len(timestamps_with_description)-1):
        timestamp = timestamps_with_description[i][0]
        description = timestamps_with_description[i][1]
        if i == len(timestamps_with_description)-1:
            next_timestamp_secs = int(length_secs)
        else:
            next_timestamp = timestamps_with_description[i+1][0]
            next_timestamp_secs = timestamp_to_secs(timestamp=next_timestamp)
        timestamp_secs = timestamp_to_secs(timestamp=timestamp)
        duration_timestamp = int(next_timestamp_secs)-int(timestamp_secs)
        timestamps_with_duration.append((str(timestamp),str(description),str(duration_timestamp),str(timestamp_secs)))
    
    return(timestamps_with_duration)

def export_subclips(input_mp3:str,sub_files_info:list):

    # Define the start times, durations, and titles for the sub-MP3 files
    # Format: (timestamp, title, duration, start_time)

    # Iterate through sub_files_info and export each sub-MP3 file
    name = input_mp3.replace('.\\Downloads\\','')
    name = name.replace('.mp3','')
    try:
        os.mkdir(".\\Downloads\\"+name)
    except:
        pass
    for idx, (x,title, duration, start_time) in enumerate(sub_files_info, start=1):
        duration = int(duration)
        start_time = int(start_time)
        title = remove_prefix(title)
        
        # Create a subclip from the original MP3 file
        subclip = AudioFileClip(input_mp3).subclip(start_time, start_time + duration)
        
        # Define the filename for the sub-MP3 file
        if title != None and title != "":
            output_mp3 = f".\Downloads\{name}\{title}.mp3"
        else:
            output_mp3 = f".\Downloads\{name}\Track_{str(idx)}.mp3"
        
        # Export the sub-MP3 file with the specified title
        subclip.write_audiofile(output_mp3,codec='mp3' ,verbose=False)

input_mp3 = ".\Downloads\Stick_Figure_–_Wisdom_(Full_Album).mp3"
url = "https://www.youtube.com/watch?v=DqQr64kZzAM"
video = YouTube(url)
timestamps = formt_timestamps(video)
export_subclips(input_mp3,timestamps)