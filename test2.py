from moviepy.editor import AudioFileClip
import re



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

input_mp3 = ".\Downloads\Stick_Figure_–_Wisdom_(Full_Album).mp3"
# Define the filename of your MP3 file
def export_subclips(input_mp3:str,sub_files_info:list):

    # Define the start times, durations, and titles for the sub-MP3 files
    # Format: (timestamp, title, duration, start_time)

    # Iterate through sub_files_info and export each sub-MP3 file
    for idx, (x,title, duration, start_time) in enumerate(sub_files_info, start=1):
        duration = int(duration)
        start_time = int(start_time)
        title = remove_prefix(title)
        
        # Create a subclip from the original MP3 file
        subclip = AudioFileClip(input_mp3).subclip(start_time, start_time + duration)
        
        # Define the filename for the sub-MP3 file
        if title != None and title != "":
            output_mp3 = f".\Downloads\{title}.mp3"
        else:
            output_mp3 = f".\Downloads\Track_{str(idx)}.mp3"
        
        # Export the sub-MP3 file with the specified title
        subclip.write_audiofile(output_mp3,codec='mp3' ,verbose=False)
