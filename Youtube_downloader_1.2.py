#made by Qwert512 on github
#version: 1.2.0
from pytube import YouTube, Playlist
import requests,  os,  json,  ffmpeg,  shutil, configparser, asyncio, time
from subprocess import call, check_output
import create_config, util
import numpy as np
import warnings
from moviepy.editor import VideoFileClip, AudioFileClip
warnings.filterwarnings("ignore", category=DeprecationWarning)
#setup routine
#required modules
index_total = int()
index_download = int()
index_convert = int()
index_merge = int()
flag = 1

download_done = bool()
convert_done = bool()
merge_done = bool()


def config():
    config = configparser.ConfigParser()
    config.read('config.txt')
    global cfg_resolution
    global cfg_abr
    global cfg_everywhere
    cfg_resolution = int(config['video']['resolution'])
    cfg_abr = int(config['audio']['abr'])
    cfg_everywhere_str = config["misc"]["config_everywhere"]
    cfg_everywhere = {'true': True, 'false': False}.get(cfg_everywhere_str.lower(), False)

async def get_link_user():
    link = input("Enter the link of YouTube video you want to download:  ") #fetch user input for the youtube video link
    return link

class Video:
    tmp_dir = './Downloads_tmp/' 
    download_dir = './Downloads/'
    file_dir = os.path.realpath(__file__)[:-len(os.path.basename(__file__))][:-1]

    def __init__(self, link:str, abr:int, resolution:int, index:int):
        self.link = link
        self.abr = abr
        self.resolution = resolution
        self.yt = YouTube(self.link)
        self.index = index
        self.a_itag = int()
        self.v_itag = int()
    
    async def preparation(self): 
        details = await util.showdetails(self.yt)
        print(details)

        streams = set()
    
        for stream in self.yt.streams.filter(type = "video"):
            if stream.resolution != None:
                streams.add(stream.resolution)
        resolutions = []

        for i in streams:
            res = int(i[:-1])
            resolutions.append(res)
        resolutions.sort()

        for u in range(len(resolutions)):
            if resolutions[u] == 2160:
                resolutions[u] = "4K"
            elif resolutions[u] == 4320:
                resolutions[u] = "8K"
            else:
                resolutions[u] = str(resolutions[u])+"p"
        l = 0
        if self.resolution == None:
            print("Pick one of the resolution below: ")
            print("0: audio only")

            for v in resolutions:  
                l += 1
                print(str(l)+": "+v)

            num = int(input(""))

        else:
            num = self.resolution

        if num < 0:
            num = 0
        elif num > l:
            num = l
        num -= 1
        aud_only = False

        if num < 0:
            aud_only = True
        resolution = resolutions[num]

        if resolution == "4K":
            resolution = "2160p"
        elif resolution == "8K":
            resolution = "4320p"

        correct_streams = self.yt.streams.filter(resolution=resolution,  mime_type="video/mp4")


        
        if len(correct_streams) == 0:
            #check if there is no stream fitting all criteria and just ignore container type
            correct_streams = self.yt.streams.filter(resolution=resolution)

        for fallback in correct_streams:
            v_itag = fallback.itag
            vid_type = fallback.subtype
            #fallback solution (just takes one)
        
        codecs = ["avc", "vp9", "av0"]
        for codec in codecs:
            for stream in correct_streams:
                tla = stream.codecs[0][0:3]
                if tla == codec:
                    v_itag = stream.itag
                    vid_type = stream.subtype
                #avc1 or H.264
  
        if aud_only == True: 
            v_itag = -1
            vid_type = "audio"
        v_itag = int(v_itag)
        self.v_itag = v_itag
        self.vid_type = vid_type
        self.aud_only = aud_only


        #audio itag

        streams = set()
        #define streams as an empty set
        for stream in self.yt.streams.filter(type="audio"):
        #filter for audio streams
            streams.add(stream.abr)
            #then add the audiobitrate attribute of the stream object to the set

        bitrates = []
        #define the bitrates array to hold all the audio bitrates from above, as the set is pretty unusable
        for i in streams:
            #loop through the set
            rate = int(i[:-4])
            #then remove the kbps ending and convert the number to int for further usage
            bitrates.append(rate)
            #then add the number to the array
        bitrates.sort()
        #before sorting it from lowest to highest
        for u in range(len(bitrates)):
            #looping through the sorted bitrates and adding back the "kbps" ending
            bitrates[u] = str(bitrates[u])+"kbps"
        print("\nPick one of the bitrates below:")
        #then list the availible audiobitrates with an index before
        o = 0
        for k in range(len(bitrates)):
            o+= 1
            print(str(o)+": "+bitrates[k])
        if self.abr == None:
            rate = int(input(""))
        else:
            rate = self.abr
        print("\n")
        #then ask for user input in form of an index shifted by one
        rate -= 1
        #convert the index to the corresponding array index
        if rate < 0:
            rate = 0
        if rate > len(bitrates)-1:
            rate = len(bitrates)-1
        #filter faulty user input out
        output = self.yt.streams.filter(abr=bitrates[rate])[0]
        #get the first availible audio stream with a fitting audio bitrate
        tag = output.itag
        #then get the corresponding itag attribute from the stream object (unique identifier of the stream)
        aud_type = output.subtype
        #then get the cooresponding subtype attribute from the stream object,  for further use in conversion,  path related tasks etc.

        tag = int(tag)
        #convert the itag to int as that datatype is required in further processing
        self.a_itag = tag
        self.aud_type = aud_type
        #return the itag and datatype

    async def download(self):
        await self.preparation()
        if self.aud_only == False:
            self.vid_stream = self.yt.streams.get_by_itag(self.v_itag)
            self.vid_name = (self.download_dir+self.vid_stream.default_filename[:-len(self.vid_type)]+"mp4").replace(" ",  "_")
            self.tmp_vid_name = (self.tmp_dir+"v_"+self.vid_stream.default_filename).replace(" ",  "_")  
            self.cln_vid_name = self.vid_stream.default_filename.replace(" ",  "_")

        self.aud_stream = self.yt.streams.get_by_itag(self.a_itag)
        self.aud_name = (self.download_dir+self.aud_stream.default_filename[:-len(self.vid_type)]+"mp3").replace(" ",  "_")
        self.tmp_aud_name = (self.tmp_dir+"a_"+self.aud_stream.default_filename).replace(" ",  "_")
        self.cln_aud_name = self.aud_stream.default_filename.replace(" ",  "_")
        if self.aud_only == False:
            print(self.vid_stream)

        print(self.aud_stream)

        if self.aud_only == True:
            self.filesize = await util.get_filesize(self.yt,  self.aud_only,  self.a_itag,  self.a_itag)
        else:
            self.filesize = await util.get_filesize(self.yt,  self.aud_only,  self.v_itag,  self.a_itag)
    
        #Starting download
        print("Downloading approximately "+self.filesize+"...")
        if self.aud_only == False:
            self.vid_stream.download(self.tmp_dir)
            try:
                os.rename(self.file_dir+self.tmp_dir[1:]+self.vid_stream.default_filename,self.file_dir+self.tmp_dir[1:]+"v_"+(self.vid_stream.default_filename.replace(" ","_")))
            except:
                FileExistsError
        self.aud_stream.download(self.tmp_dir)
        try:
            os.rename(self.tmp_dir+self.aud_stream.default_filename,self.tmp_dir+"a_"+(self.aud_stream.default_filename.replace(" ","_")))
        except:
            FileExistsError
        print("Download completed.")
        print("Resolution: "+str(self.resolution))
    
    async def convert(self):

        print("\nConverting...")
        a_inname = self.tmp_dir+"a_"+self.cln_aud_name
        a_outname = self.tmp_dir+self.cln_aud_name[:-len(self.aud_type)] + "mp3"
        if os.path.exists(a_outname):
            os.remove(a_outname)
        if self.aud_only==False:
            v_inname = self.tmp_dir+"v_"+self.cln_vid_name
            v_outname = self.tmp_dir+self.cln_vid_name[:-len(self.vid_type)] + "mp4"
            if os.path.exists(v_outname):
                os.remove(v_outname)
            

        if self.aud_type != "mp3":
            audio_clip = AudioFileClip(a_inname)
            # Write the audio clip to a .mp3 file
            audio_clip.write_audiofile(a_outname, codec='mp3')
            os.remove(self.tmp_dir+"a_"+self.cln_aud_name)
        elif self.aud_type == "mp3":
            os.rename(a_inname,  a_outname)


        if self.aud_only == False and self.vid_type != "mp4":
            video_clip = VideoFileClip(v_inname)
            # Write the audio clip to a .mp3 file
            video_clip.write_videofile(v_outname, codec='mp4')
            os.remove(self.tmp_dir+"v_"+self.cln_vid_name)
        elif(self.vid_type == "mp4" and self.aud_only==False):
            os.rename(v_inname,v_outname)
        print("Converting completed.")
        

    async def merge(self):
        video_name = self.tmp_dir+self.cln_aud_name[:-len(self.aud_type)] + "mp4"
        audio_name = self.tmp_dir+self.cln_aud_name[:-len(self.aud_type)] + "mp3"
        if self.aud_only:
            if os.path.exists(audio_name):
                os.remove(audio_name)
            os.rename(audio_name,  self.aud_name)
            
        else:   
            # else:
            #     command = "ffmpeg -i "+self.file_dir+self.tmp_vid_name[1:]+" -i "+self.file_dir+self.tmp_aud_name[1:]+" -c:v copy -c:a copy -hide_banner -loglevel error "+self.file_dir+self.vid_name[1:]
            #     call(command,  shell = True)
            
            video_clip = VideoFileClip(video_name)
            audio_clip = AudioFileClip(audio_name)

            # Set audio for the video clip
            video_clip = video_clip.set_audio(audio_clip)

            # Write the merged clip to an output file
            output_path = self.vid_name
            video_clip.write_videofile(output_path)

            os.remove(video_name)
            os.remove(audio_name)

        
        print("Merging completed.")

    async def cleanup(self):
        pass



create_config.create_config()
config()

vids = []
vid_index = 0
links =  []
link_index = 0



async def link():
    global vids, vid_index, links, link_index
    while True:
        if os.path.getsize("links.txt") != 0:
            #cheks if the links file contains writing
            with open("links.txt") as file:
                lines = file.readlines()
                lines = [line.rstrip() for line in lines]
                #as the links file contains content, it gets cleaned
                for u in lines:
                #then loop through all the links
                    if "playlist" in u:
                        #if a clean playlist link is detected: 
                        #download the playlist with config settings
                        print("Do you want to download the entire playlist? (y/n)")
                        ans = input()
                        if ans == "y" or "Y":
                            p = Playlist(u)
                            for i in p.video_urls:
                                links.append(i)
                    else:
                        links.append(u)
                    #and run the download and merge function with the link and the config settings from above
            file = open("links.txt",  "w")
            #after processing all the videos, open the links file in write mode
            file.truncate(0)
        else:
            link_inpt = await get_link_user()
            if "playlist" in link_inpt:
                #if a clean playlist link is detected: 
                #download the playlist with config settings
                print("Do you want to download the entire playlist? (y/n)")
                ans = input()
                if ans == "y" or "Y":
                    p = Playlist(link_inpt)
                    for i in p.video_urls:
                        links.append(i)
            else:
                links.append(link_inpt)
        await asyncio.sleep(0.2)
    
async def vid():
    global vids, vid_index, links, link_index, flag
    vid_index=1
    #just for testing
    while True:
        if len(links) > 0:
            print(links[0])
            vids.append(Video(links[0], None,None, vid_index))
            print("downloading manaual")
            print(vids)
            print(links)
            links.pop(0)

        await asyncio.sleep(0.1)
async def run():
    while True:
        if len(vids) > 0:
            print("running")
            await vids[0].download()
            await vids[0].convert()
            await vids[0].merge()
            vids.pop(0)
            print("done")
            print(links)
            print(vids)
        await asyncio.sleep(0.2)

loop = asyncio.get_event_loop()
loop.create_task(link())
loop.create_task(vid())
loop.create_task(run())
loop.run_forever()
