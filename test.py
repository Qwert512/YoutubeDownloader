from json import loads
from pytube import YouTube
import re

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

video = YouTube("https://www.youtube.com/watch?v=DqQr64kZzAM")
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

# the return list ist build like this: 
# [(Timestamp,Description,Duration_secs,start_secs)]
for i in timestamps_with_duration:
    print(i)
