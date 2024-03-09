from moviepy.editor import AudioFileClip

def convert_webm_to_mp3(input_file, output_file):
    # Load the .webm audio file
    audio_clip = AudioFileClip(input_file)

    # Write the audio clip to a .mp3 file
    audio_clip.write_audiofile(output_file, codec='mp3')

# Example usage
if __name__ == "__main__":
    input_file = "Downloads_tmp/a_Wood_That_Doesnt_Burn.mp4"
    output_file = "output_file.mp3"

    convert_webm_to_mp3(input_file, output_file)