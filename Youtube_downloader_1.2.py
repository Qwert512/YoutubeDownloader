#made by Qwert512 on github
#version: 1.2.3
from pytube import YouTube, Playlist
import os, shutil, configparser, asyncio
import create_config, util, split_mp3
import warnings
from moviepy.editor import VideoFileClip, AudioFileClip
warnings.filterwarnings("ignore", category=DeprecationWarning)
#setup routine
#required modules

tmp_dir = './Downloads_tmp/' 
download_dir = './Downloads/'


class Config:
    def __init__(self):
        config_file = configparser.ConfigParser()
        config_file.read('config.txt')

        debug_str = config_file["misc"]["debug"]
        self.debug = {'true': True, 'false': False}.get(debug_str.lower(), False)
        self.cfg_resolution = int(config_file['video']['resolution'])
        self.cfg_abr = int(config_file['audio']['abr'])
        cfg_everywhere_str = config_file["misc"]["config_everywhere"]
        self.cfg_everywhere = {'true': True, 'false': False}.get(cfg_everywhere_str.lower(), False)
        autodownload_playlists_str = config_file["misc"]["autodownload_playlists"]
        self.autodownload_playlists = {'true': True, 'false': False}.get(autodownload_playlists_str.lower(), False)
        self.mode = config_file["misc"]["mode"]
        if self.mode not in ["simple", "music", "video"]:
            self.mode = "simple"

def cleanup():
    #do some cleanup stuff
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.mkdir(tmp_dir)

    #search for temp files
    rm_files = []
    files = os.listdir("./")
    for file in files:
        if "TEMP" in file:
            rm_files.append(file)
    for rm_file in rm_files:
        os.remove(rm_file)


async def get_link_user():
    link = input("Enter the link of YouTube video you want to download:  ") #fetch user input for the youtube video link
    return link

class Video:
    tmp_dir = './Downloads_tmp/' 
    download_dir = './Downloads/'
    file_dir = os.path.realpath(__file__)[:-len(os.path.basename(__file__))][:-1]

    def __init__(self, link:str, abr, resolution):
        self.link = link
        self.abr = abr
        self.resolution = resolution
        self.yt = YouTube(self.link)
        self.a_itag = int()
        self.v_itag = int()
    
    async def preparation(self): 
        if not os.path.exists(self.tmp_dir):
            os.makedirs(self.tmp_dir)
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
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
        if self.resolution is None:
            print("Pick one of the resolutions below:")
            print("0: audio only")

            for idx, v in enumerate(resolutions, start=1):  
                print(f"{idx}: {v}")

            num = int(input("Enter the number corresponding to your choice: ")) - 1
        else:
            num = int(self.resolution) - 1

        # Ensure the selected resolution index is within bounds
        l = len(resolutions)
        num = max(0, min(num, l - 1))
        num -= 1
        aud_only = num < 0
        if aud_only and self.abr == None:
            print("Audio only selected.")

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
        
        if self.abr == None:
            print("\nPick one of the bitrates below:")
            #then list the availible audiobitrates with an index before
            o = 0
            for k in range(len(bitrates)):
                o+= 1
                print(str(o)+": "+bitrates[k])
            rate = int(input(""))

        else:
            rate = self.abr
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

    async def download(self,config:Config):
        await self.preparation()
        if self.aud_only == False:
            self.vid_stream = self.yt.streams.get_by_itag(self.v_itag)
            self.vid_name = (self.download_dir+self.vid_stream.default_filename[:-len(self.vid_type)]+"mp4").replace(" ",  "_")
            self.tmp_vid_name = (self.tmp_dir+"v_"+self.vid_stream.default_filename).replace(" ",  "_")  
            self.cln_vid_name = self.vid_stream.default_filename.replace(" ",  "_")

        self.aud_stream = self.yt.streams.get_by_itag(self.a_itag)
        self.aud_name = (self.download_dir+self.aud_stream.default_filename[:-len(self.vid_type)]+".mp3").replace(" ",  "_")
        self.tmp_aud_name = (self.tmp_dir+"a_"+self.aud_stream.default_filename).replace(" ",  "_")
        self.cln_aud_name = self.aud_stream.default_filename.replace(" ",  "_")
        if config.debug:
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
        if config.debug:
            print("Download completed.")
    
    async def convert(self, config:Config):
        if config.debug:
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
            if config.debug:
                audio_clip.write_audiofile(a_outname, codec='mp3')
            else:
                audio_clip.write_audiofile(a_outname, codec='mp3', verbose=False)
            os.remove(self.tmp_dir+"a_"+self.cln_aud_name)
        elif self.aud_type == "mp3":
            os.rename(a_inname,  a_outname)


        if self.aud_only == False and self.vid_type != "mp4":
            video_clip = VideoFileClip(v_inname)
            # Write the audio clip to a .mp3 file
            if config.debug:
                video_clip.write_videofile(v_outname, codec='mp4')
            else:
                video_clip.write_videofile(v_outname, codec='mp4', verbose=False)
            os.remove(self.tmp_dir+"v_"+self.cln_vid_name)
        elif(self.vid_type == "mp4" and self.aud_only==False):
            os.rename(v_inname,v_outname)
        if config.debug:
            print("Converting completed.")
        

    async def merge(self, config:Config):
        video_name = self.tmp_dir+self.cln_aud_name[:-len(self.aud_type)] + "mp4"
        audio_name = self.tmp_dir+self.cln_aud_name[:-len(self.aud_type)] + "mp3"
        if self.aud_only:
            if config.debug:
                print("aud_name: "+self.aud_name)
                print("audio name: "+audio_name)
            if os.path.exists(self.aud_name):
                os.remove(self.aud_name)
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
            if config.debug:
                video_clip.write_videofile(output_path)
            else:
                video_clip.write_videofile(output_path, verbose=False)

            os.remove(video_name)
            os.remove(audio_name)

        if config.debug:
            print("Merging completed.")

        if config.mode == "music":
            input_mp3 = self.aud_name
            timestamps = split_mp3.formt_timestamps(self.yt,input_mp3)
            if len(timestamps) != 0:
                print(f"Possible album with {len(timestamps)} tracks detected. Do you want to split the album into individual tracks? (y/n)")
                ans = input()
                if ans.lower() == "y":
                    print("Splitting album...")
                    split_mp3.export_subclips(input_mp3=input_mp3,sub_files_info=timestamps)
                    print("done")

create_config.create_config()
config_object = Config()
cleanup()

vids = []
links =  []


async def link(config:Config):
    # When saving links, it will be encoded into the liunk, if user input is required
    # Automatic choice will be marked with a "a_" prefix, manual selection will be marked with a "m_" prefix
    global vids, links
    while True:
        if os.path.getsize("links.txt") != 0:
            # Check if the links file contains writing
            with open("links.txt") as file:
                lines = file.readlines()
                lines = [line.rstrip() for line in lines]
                # Clean the links file
                for u in lines:
                    # Loop through all the links
                    if "playlist" in u:
                        # if a clean playlist link is detected:
                        # download the playlist with config settings
                        if config.autodownload_playlists == False:
                            print("Do you want to download the entire playlist? (y/n)")
                            ans = input()
                            if ans.lower() == "y":
                                p = Playlist(u)
                                for i in p.video_urls:
                                    links.append("a_"+i)
                        else:
                            p = Playlist(u)
                            for i in p.video_urls:
                                links.append("a_"+i)
                    else:
                        links.append("a_"+u)
            open("links.txt", "w").close()
        else:
            if len(links) == 0 and len(vids) == 0:
                link_inpt = await get_link_user()
                if "playlist" in link_inpt:
                    # if a clean playlist link is detected:
                    # download the playlist with config settings
                    if config.autodownload_playlists == False:
                        print("Do you want to download the entire playlist? (y/n)")
                        ans = input()
                        if ans.lower() == "y":
                            p = Playlist(link_inpt)
                            for i in p.video_urls:
                                links.append("a_"+i)
                    else:
                        p = Playlist(link_inpt)
                        for i in p.video_urls:
                            links.append("a_"+i)
                else:
                    if config.cfg_everywhere == True:
                        links.append("a_"+link_inpt)
                    else:
                        links.append("m_"+link_inpt)
        await asyncio.sleep(0.2)
    
async def vid(config:Config):
    global vids, links
    #just for testing
    while True:
        if len(links) > 0:
            mode = links[0][:1]
            url = links[0][2:]
            if config.debug:
                print(links[0])
            if mode == "m":
                vids.append(Video(url, None,None))
                if config.debug:
                    print("downloading manaual")
            elif mode == "a":
                vids.append(Video(url, config.cfg_abr, config.cfg_resolution))
                if config.debug:
                    print("downloading automatic")
            if config.debug:
                print(vids)
                print(links)
            links.pop(0)

        await asyncio.sleep(0.1)

async def run(config:Config):
    while True:
        if len(vids) > 0:
            if config.debug:
                print("running")
            await vids[0].download(config=config)
            await vids[0].convert(config=config)
            await vids[0].merge(config=config)
            vids.pop(0)
            print("done")
            if config.debug:
                print(links)
                print(vids)
        
        await asyncio.sleep(0.2)

loop = asyncio.get_event_loop()
loop.create_task(link(config=config_object))
loop.create_task(vid(config=config_object))
loop.create_task(run(config=config_object))
loop.run_forever()
