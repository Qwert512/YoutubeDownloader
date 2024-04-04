import re, os
from json import loads
from pytube import YouTube
from googleapiclient.discovery import build
from moviepy.editor import AudioFileClip

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
    filter_characters = "-_: .1234567890"
    pattern = r'[^' + re.escape(filter_characters) + ']'

    # Find the first non-filter character from the front and back
    start_match = re.search(pattern, x)
    end_match = re.search(pattern, x[::-1])  # Search from the back

    if start_match:
        start_index = start_match.start()
    else:
        start_index = 0  # No non-filter characters found from the front

    if end_match:
        end_index = len(x) - end_match.start() - 1  # Adjust for reverse search
    else:
        end_index = len(x)  # No non-filter characters found from the back

    return x[start_index:end_index+1].strip()
    

def format_timestamps(timestamps_with_description:tuple,url: str, input_mp3: str="Null"):
    #converting the tuple to two lists to work on
    timestamps = []
    descriptions = []
    for n in timestamps_with_description:
        timestamps.append(n[0])
        descriptions.append(n[1])
    #getting legth of the video
    video = YouTube(url)
    timestamps_with_duration = []
    if input_mp3 == "Null":
        length_secs = video.length
        #if the precise length isnt availible, just get a close estimate
    else:
        audio_clip = AudioFileClip(input_mp3)
        length_secs = audio_clip.duration
    #the length isused for the last timestamp

    #First we convert every timestamp into a nice, cleaned HH:MM:SS Timestamp
    converted_timestamps = []
    for timestamp in timestamps:
        try:
        # Split the timestamp into minutes and seconds (optional hours)
            parts = timestamp.split(':')

            # Handle different formats (M:SS or MM:SS)
            if len(parts) == 2:  
                hours = '00'
                minutes, seconds = parts
            elif len(parts) == 3:  
                hours, minutes, seconds = parts
            else:
                raise ValueError(f"Invalid timestamp format: {timestamp}")

            # Zero-pad minutes and seconds if needed
            minutes = minutes.zfill(2)
            seconds = seconds.zfill(2)
            hours = hours.zfill(2)

            # Combine and return converted timestamp
            converted_timestamps.append(f"{hours}:{minutes}:{seconds}")
        except ValueError as e:
            print(f"Error converting timestamp: {timestamp} - {e}")

    timestamps = converted_timestamps
    #now the list contains timestamps in a uniform format

    #next step are the comments
    converted_descriptions = []
    patterns_to_remove = ["()","<br>","&#39;"]
    for k in descriptions:
        k = remove_prefix(k)
        for pattern in patterns_to_remove:
            k = k.replace(pattern,"")
        converted_descriptions.append(k.strip())
    descriptions = converted_descriptions

    for i in range(len(timestamps_with_description)):
        timestamp = timestamps[i]
        description = descriptions[i]
        if i == len(timestamps_with_description)-1:
            next_timestamp_secs = length_secs
        else:
            next_timestamp = timestamps[i+1]
            next_timestamp_secs = timestamp_to_secs(timestamp=next_timestamp)
        timestamp_secs = timestamp_to_secs(timestamp=timestamp)
        duration_timestamp = float(next_timestamp_secs)-float(timestamp_secs)
        timestamps_with_duration.append((str(timestamp),str(description),str(duration_timestamp),str(timestamp_secs)))
    
    return(timestamps_with_duration)


def extract_timestamps_description(url:str):
    video = YouTube(url)
    desc = get_description(video)
    pattern1_matches = re.findall(r'(\d+:\d+(?::\d+)?)\s*(.*)', desc)

    timestamp_text_tuples = []
    timestamps = []
    content = []
    for match in pattern1_matches:
        timestamp_text_tuples.append((match[0], match[1]))
        timestamps.append(match[0])

    all_lines = str.splitlines(desc)
    for i in all_lines:
        found_timestamp = False
        for u in timestamps:
            if u in i:
                content.append(i.replace(u, ""))
                break
    
    timestamp_text_tuples = []
    for n in range(len(timestamps)):
        timestamp_text_tuples.append((timestamps[n],content[n].replace("#","")))

    return timestamp_text_tuples

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

    #remove lines without timestamps from comment
    lines = comment_text.split("<br>")  # Split at line breaks
    #print(len(lines))
    filtered_lines = []
    for i, line in enumerate(lines):
        if "href=" in line and any(char in line for char in ":0123456789"):
            filtered_lines.append(line)

    comment_text = "<br>".join(filtered_lines)
    pattern1_matches = re.findall(r'<a.*?>(.*?)</a>\s*(.*?)(?:<br>|$)', comment_text)
    pattern2_matches = re.findall(r'(.*?)<a.*?>(.*?)</a>\s*(?:<br>)?', comment_text)

    #print("pattern_1: "+str(len(pattern1_matches))+", pattern_2: "+str(len(pattern2_matches)))
    # Determine which pattern produces more matches
    if len(pattern1_matches) != len(pattern2_matches):
        best_matches = pattern1_matches if len(pattern1_matches) > len(pattern2_matches) else pattern2_matches
        flip_tuple = False if best_matches == pattern1_matches else True
        if best_matches == pattern1_matches:
            #print("Choosing pattern 1")
            pass
        else:
            #print("Choosing pattern 2")
            pass
    elif len(pattern1_matches) != 0:
        # If lengths are equal and not 0, compare the first element of the tuple
        pattern1_length = len(pattern1_matches[0][0]) + len(pattern1_matches[0][1])
        pattern2_length = len(pattern2_matches[0][0]) + len(pattern2_matches[0][1])
        best_matches = pattern1_matches if pattern1_length >= pattern2_length else pattern2_matches
        flip_tuple = False if best_matches == pattern1_matches else True
        if best_matches == pattern1_matches:
            #print("Choosing pattern 1")
            pass
        else:
            #print("Choosing pattern 2")
            pass
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
    
    return "None"

def export_subclips(input_mp3:str,sub_files_info:list):

    # Define the start times, durations, and titles for the sub-MP3 files
    # Format: (timestamp, title, duration, start_time)

    # Iterate through sub_files_info and export each sub-MP3 file
    name = input_mp3.replace('./Downloads/','')
    name = name.replace('.mp3','')
    try:
        os.mkdir(".\\Downloads\\"+name)
    except:
        pass
    for idx, (x,title, duration, start_time) in enumerate(sub_files_info, start=1):
        duration = float(duration)
        start_time = float(start_time)
        
        # Create a subclip from the original MP3 file
        subclip = AudioFileClip(input_mp3).subclip(start_time, start_time + duration)
        
        # Define the filename for the sub-MP3 file
        if title != None and title != "":
            output_mp3 = f"./Downloads/{name}/{title}.mp3"
        else:
            output_mp3 = f"./Downloads/{name}/Track_{str(idx)}.mp3"
        
        # Export the sub-MP3 file with the specified title
        subclip.write_audiofile(output_mp3, verbose=False)