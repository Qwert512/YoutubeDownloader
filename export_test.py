import os
from moviepy.editor import AudioFileClip
from moviepy.video.io import ffmpeg_audiowriter

def export_subclips(input_mp3:str):

    # Define the start times, durations, and titles for the sub-MP3 files
    # Format: (timestamp, title, duration, start_time)

    # Iterate through sub_files_info and export each sub-MP3 file
    name = "e"
    try:
        os.mkdir(".\\Downloads\\"+name)
    except:
        pass
    duration = 200
    start_time = 20
    
    # Create a subclip from the original MP3 file
    subclip = AudioFileClip(input_mp3).subclip(start_time, start_time + duration)
    
    # Define the filename for the sub-MP3 file
    output_mp3 = f"./Downloads/{name}/Track_{str(1)}.mp3"
    
    # Export the sub-MP3 file with the specified title
    subclip.write_audiofile(output_mp3, verbose=False, codec="copy")

input_mp3 = "Downloads\Stick_Figure_–_Wisdom_(Full_Album).mp3"
ffmpeg_audiowriter()
export_subclips(input_mp3)