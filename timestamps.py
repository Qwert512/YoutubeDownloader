import re, os
from json import loads
from pytube import YouTube
from googleapiclient.discovery import build

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

def formt_timestamps(url: str, input_mp3: str=None) -> list:
    video = YouTube(url)
    desc = get_description(video)
    #audio_clip = AudioFileClip(input_mp3)
    #length_secs = audio_clip.duration
    length_secs = video.length
    timestamps_with_description = re.findall(r'(\d+:\d+(?::\d+)?)\s*(.*)', desc)
    timestamps_with_duration = []

    for i in range(len(timestamps_with_description)):
        timestamp = timestamps_with_description[i][0]
        description = timestamps_with_description[i][1]
        if i == len(timestamps_with_description)-1:
            next_timestamp_secs = length_secs
        else:
            next_timestamp = timestamps_with_description[i+1][0]
            next_timestamp_secs = timestamp_to_secs(timestamp=next_timestamp)
        timestamp_secs = timestamp_to_secs(timestamp=timestamp)
        duration_timestamp = float(next_timestamp_secs)-float(timestamp_secs)
        timestamps_with_duration.append((str(timestamp),str(description),str(duration_timestamp),str(timestamp_secs)))
    
    return(timestamps_with_duration)

def scrape_comments(video_id:str,api_key:str):
    #build a resource for youtube
    resource = build('youtube', 'v3', developerKey=api_key)
    #create a request to get 20 comments on the video
    request = resource. commentThreads().list(
                                part="snippet",
                                videoId=video_id,
                                maxResults= 100,   #get 20 comments
                                order="relevance")  #top comments.
    #execute the request
    response =request.execute()

    #get first 10 items for from 20 comments 
    items = response["items"][:100]
    possible_setlists = []
    # print("------------------------------------------------------------------------------------------------------")
    for item in items:
        item_info = item["snippet"]
        
        #the top level comment can have sub reply comments
        comment_info = item_info["topLevelComment"]["snippet"]
        if comment_info["textDisplay"].count("t=") >2:
            possible_setlists.append(comment_info["textDisplay"])
            # print("Comment By:", comment_info["authorDisplayName"])
            # print("Coment Text:" ,comment_info["textDisplay"])
            # print("Likes on Comment :", comment_info["likeCount"])
            # print("Comment Date: ", comment_info['publishedAt'])
            # print("================================\n")
    return(possible_setlists)

def extract_timestamps_comment(comment_text:str):
    # Regular expressions to extract timestamp and description
    pattern1_matches = re.findall(r'<a.*?>(.*?)</a>\s*(.*?)<br>', comment_text)
    pattern2_matches = re.findall(r'(\d+.*?)<a.*?>(.*?)</a>', comment_text)
    r'(\d+:\d+(?::\d+)?)</a>\s*(.*?)<br>'
    print("pattern_1: "+str(len(pattern1_matches))+", pattern_2: "+str(len(pattern2_matches)))
    # Determine which pattern produces more matches
    if len(pattern1_matches) != len(pattern2_matches):
        best_matches = pattern1_matches if len(pattern1_matches) > len(pattern2_matches) else pattern2_matches
        flip_tuple = False if best_matches == pattern1_matches else True
    elif len(pattern1_matches) != 0:
        # If lengths are equal and not 0, compare the first element of the tuple
        pattern1_length = len(pattern1_matches[0][0]) + len(pattern1_matches[0][1])
        pattern2_length = len(pattern2_matches[0][0]) + len(pattern2_matches[0][1])
        best_matches = pattern1_matches if pattern1_length >= pattern2_length else pattern2_matches
        flip_tuple = False if best_matches == pattern1_matches else True
    else:
        # If both lengths are 0, return an empty list
        return []

    # Export timestamp and text pairs into tuples
    timestamp_text_tuples = []
    for match in best_matches:
        if flip_tuple:
            timestamp_text_tuples.append((match[1], match[0]))
        else:
            timestamp_text_tuples.append((match[0], match[1]))
    return timestamp_text_tuples

def url_to_id(url:str) -> str:
    # Regular expression pattern to match YouTube video IDs
    patterns = [
        r'(?:https?://)?(?:www\.)?youtu\.?be(?:\.com)?/(?:watch\?v=)?([^&#\n?]+)',  # Matches youtube.com and youtu.be URLs
        r'(?:https?://)?(?:www\.)?youtube(?:-nocookie)?\.com/(?:[^/\n?]+/)?(?:[^/\n?]+/)?(?:watch(?:_popup)?(?:\.php)?(?:\?.*?&)?v=|v/|embed/|e/|user/(?:[^/\n?]+/)+(?:[^/\n?]+/)?)([^&#\n?]+)',  # Matches various types of youtube.com URLs
    ]

    # Iterate over patterns and try to find a match
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None
