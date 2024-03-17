from pytube import YouTube
import timestamps
vid = YouTube("https://www.youtube.com/watch?v=bU_CrTrZDnY")
print(repr(timestamps.get_description(vid)))