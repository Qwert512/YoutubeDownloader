#made by Qwert512 on github
#version: 1.1.0
from pytube import YouTube, Playlist
import requests,  os,  json,  ffmpeg,  shutil, configparser, asyncio, time
from subprocess import call, check_output
import create_config
import numpy as np
import warnings
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
    global API_KEY 
    global cfg_resolution
    global cfg_abr
    global cfg_everywhere
    API_KEY = config['misc']['api_key']
    if API_KEY == 'Write your API key here':
        API_KEY = None
    cfg_resolution = int(config['video']['resolution'])
    cfg_abr = int(config['audio']['abr'])
    cfg_everywhere = bool(config["misc"]["config_everywhere"])

async def get_filesize(yt,  aud_only,  tag1:int,  tag2:int):
    stream1 = yt.streams.get_by_itag(tag1)
    stream2 = yt.streams.get_by_itag(tag2)
    #first set the two streams from the itags given in the function call
    #One of the streams is for audio, one for video
    #In case of audio only, both are the same and one will be removed later

    size1 = stream1.filesize_approx
    size2 = stream2.filesize_approx
    #then get the size for both 

    if aud_only == True:
        size2 = 0
        #if it is audio only, one of them will be removed
    
    size_tot = str(size1 + size2)
    #then the two sizes are combined
    length = len(size_tot)
    #then the length of the size in bytes is taken, 
    #so it can be displayed more nicely in for example MB


    if length < 4:
        size_tot = size_tot+" B"
    elif length < 7 and length > 3:
        size_tot = size_tot[:length-3]+" KB"
    elif length < 10 and length > 6:
        size_tot = size_tot[:length-6]+" MB"
    elif length < 13 and length > 9:
        size_tot = size_tot[:length-9]+" GB"
    elif length < 16 and length > 12:
        size_tot = size_tot[:length-12]+" TB"
        #here the formatting is done
    return size_tot
    #now the formatted size is returned

async def showdetails(yt):
    #Showing details
    print("")
    print("Title: ",  yt.title)
    #title of the video

    cid = yt.channel_id
    #gives the channel id (the part behind the https://www.youtube.com/c/)
    url = "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={cid}&key={api_key}".format(
        #api request containing the channel id (cid) and the google api key (API_KEY)
        cid=cid,  api_key=API_KEY
    )
    try:
        d = requests.get(url).json()
        channel_title = d['items'][0]['snippet']['channelTitle']
    except:
        if API_KEY == None:
            channel_title = "Missing API key"
        else:
            channel_title = "API key error"
    #makes an api request to the youtube v3 api by google and get the output in json form
    #then only get the channel name
    print("Channel: ",  channel_title)
    #now print it

    views_raw = yt.views
    #get the views 
    views = ""
    views_raw = format(views_raw,  ',')
    #then format them with commas for each three digits
    views = views_raw.replace(",  ",  ".")
    #then because im european, replace the commas with dots
    print("Number of views: ",  views)

    length_sec = yt.length
    #get the length in seconds and display it in hh:mm:ss
    hours = 0

    if length_sec > 3599:
        hours = length_sec // 3600
        length = str(hours)+":"
    else:
        length = ""
        #first, if the video is over one hour, divide the seconds by 
        #3600 and round it down, to get the full hours
        #then the full hours are added to the beginning of the final string
    
    minutes = (length_sec // 60) -(hours*60)
    seconds = length_sec - (minutes*60+hours*3600)
    #then do the same with the minutes, but remove the full hours
    length += str(minutes)+":"
    #then also add it

    if minutes != 0 and seconds // 10 == 0:
        length += str(0)
    length += str(seconds)
    #then add the rest seconds

    print("Length of video: ",  length)
    print("")
    #and print it

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
        
        await showdetails(self.yt)

#video itag

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

        print("Pick one of the resolution below: ")
        print("0: audio only")

        for v in resolutions:  
            l += 1
            print(str(l)+": "+v)

        if self.resolution == None:
            num = int(input(""))
        else:
            num = self.resolution

        if num < 0:
            num = 0
        if num > l:
            num = l
        num -= 1
        aud_only = False

        if num < 0:
            aud_only = True
        reso = resolutions[num]

        if reso == "4K":
            reso = "2160p"
        elif reso == "8K":
            reso = "4320p"

        max = self.yt.streams.filter(resolution=reso,  mime_type="video/mp4")


        try:
            max[0].itag
        except:
            max = self.yt.streams.filter(resolution=reso)

        for fall in max:
            v_itag = fall.itag
            vid_type = fall.subtype
            #fallback solution (just takes one)
        
        for avc in max:
            tla = avc.codecs[0]
            tla = tla[0:3]
            if tla == "avc":
                v_itag = avc.itag
                vid_type = avc.subtype
            #avc1 or H.264
        
        for vp in max:
            tla = vp.codecs[0]
            tla = tla[0:3]
            if tla == "vp9":
                v_itag = vp.itag
                vid_type = vp.subtype
                #vp9
        
        for av in max:
            tla = av.codecs[0]
            tla = tla[0:3]
            if tla == "av0":
                v_itag = av.itag
                vid_type = av.subtype
                #av1
        
        if aud_only == True: 
            v_itag = -1
            vid_type = "audio"
        v_itag = int(v_itag)
        self.v_itag = v_itag
        self.vid_type = vid_type
        self.aud_only = aud_only


        #audio itag

        #defining the function to get a specific stream id for the audio stream
        streams = set()
        #define streams as an empty set
        for stream in self.yt.streams.filter(type="audio"):
        #filter for audio streams
            streams.add(stream.abr)
            #then add the audiobitrate attribute of the stream object to the set

        bitrates = []
        #define the bitrates array to hald all the audio vitrates from above,  as the set is pretty unusable
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
        global index_download
        global download_done
        index_download = self.index
        download_done = False

        self.vid_stream = self.yt.streams.get_by_itag(self.v_itag)
        self.vid_name = (self.download_dir+self.vid_stream.default_filename[:-len(self.vid_type)]+"mp4").replace(" ",  "_")
        self.tmp_vid_name = (self.tmp_dir+self.vid_stream.default_filename[:-(len(self.vid_type)+1)]+".mp4").replace(" ",  "_")  
        self.cln_vid_name = self.vid_stream.default_filename.replace(" ",  "_")

        self.aud_stream = self.yt.streams.get_by_itag(self.a_itag)
        self.aud_name = (self.download_dir+self.aud_stream.default_filename[:-len(self.vid_type)]+".mp3").replace(" ",  "_")
        self.tmp_aud_name = (self.tmp_dir+self.aud_stream.default_filename[:-len(self.aud_type)]+"mp3").replace(" ",  "_")
        self.cln_aud_name = self.aud_stream.default_filename.replace(" ",  "_")
        if self.aud_only == False:
            print(self.vid_stream)

        print(self.aud_stream)

        if self.aud_only == True:
            self.filesize = await get_filesize(self.yt,  self.aud_only,  self.a_itag,  self.a_itag)
        else:
            self.filesize = await get_filesize(self.yt,  self.aud_only,  self.v_itag,  self.v_itag)
    
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
        download_done = True
    
    async def convert(self):
        
        global index_convert
        global convert_done
        index_convert = self.index
        convert_done = False

        print("\nConverting...")
        a_inname = self.tmp_dir+"a_"+self.cln_aud_name
        a_outname = self.tmp_dir+self.cln_aud_name[:-len(self.aud_type)] + "mp3"
        if os.path.exists(a_outname):
            os.remove(a_outname)
        v_inname = self.tmp_dir+"v_"+self.cln_vid_name
        v_outname = self.tmp_dir+self.cln_vid_name[:-len(self.vid_type)] + "mp4"
        if os.path.exists(v_outname):
            os.remove(v_outname)
            

        if self.aud_type != "mp3":
                #Define the convert method. It takes the in and output folders,  the filename,  filetype and the wanted output filetype
            conv_in = ffmpeg.input (a_inname)
            conv = ffmpeg.output (conv_in.audio,  a_outname)
            ffmpeg.run (conv,  quiet=False)
            #runs the conversion. quiet flag so the console doesnt get spammed,  as there is a LOT of debug in ffmpeg
            os.remove(self.tmp_dir+"a_"+self.cln_aud_name)
        elif self.aud_type == "mp3":
            os.rename(a_inname,  a_outname)


        if self.aud_only == False and self.vid_type != "mp4":
            conv_in = ffmpeg.input (v_inname)
            conv = ffmpeg.output (conv_in.video, v_outname)
            ffmpeg.run (conv,  quiet=False)
            #runs the conversion. quiet flag so the console doesnt get spammed,  as there is a LOT of debug in ffmpeg
            os.remove(self.tmp_dir+"v_"+self.cln_vid_name)
        elif(self.vid_type == "mp4"):
            os.rename(v_inname,v_outname)
        print("Converting completed.")
        
        convert_done = True

    async def merge(self):
        print("Merging...")


        if self.aud_only:
            if os.path.exists(self.aud_name):
                os.remove(self.aud_name)
            os.rename(self.tmp_aud_name,  self.aud_name)
            
            
        else:
            command = "ffmpeg -i "+self.file_dir+self.tmp_vid_name[1:]+" -i "+self.file_dir+self.tmp_aud_name[1:]+" -c:v copy -c:a copy -hide_banner -loglevel error "+self.file_dir+self.vid_name[1:]
            call(command,  shell = True)
            os.remove(self.tmp_vid_name)
            os.remove(self.tmp_aud_name)

        
        print("Merging completed.")

    async def cleanup(self):
        pass



create_config.create_config()
config()

vids = []
vid_index = 0
links =  [["link","cfg"]]
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
                                links[link_index] = i,"True"
                                link_index += 1
                    else:
                        links[link_index] = u,"True"
                        link_index += 1
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
                        links[link_index] = i,"True"
                        link_index += 1
            else:
                links[link_index] = link_inpt,str(cfg_everywhere)
                link_index += 1
        await asyncio.sleep(0.2)
    
async def vid():
    global vids, vid_index, links, link_index, flag
    while True:
        if link_index > vid_index:
            if bool(links[vid_index][1]):
                vids.append(Video(links[vid_index][0], cfg_abr, cfg_resolution, vid_index))
            else:
                vids[vid_index] = Video(links[vid_index][0], None,None, vid_index)
            vid_index += 1
            flag = 0
        await asyncio.sleep(0.1)
async def run():
    global flag
    if flag == 0:
        await vids[0].download()
        await vids[0].convert()
        await vids[0].merge()
        flag = 1
    await asyncio.sleep(0.2)

loop = asyncio.get_event_loop()
loop.create_task(link())
loop.create_task(vid())
loop.create_task(run())
loop.run_forever()


# TODO:
# O kommentieren
# O UI
# O Multitasking (downloaden während conversion,  conversion während merging) AsyncIO
# O Bei Qualitätsauswahl anzeigen wenn audio / video auf einmal verfügbar
# X mehr config möglichkeiten mit config parser
# O progress bars (evtl. merging) converting
# O Grafikkarte nutzen (+config option (amd/Nvidia/Intel)) https://youtu.be/m3e4ED6FY4U
# O Videocodec auswahl via config (MPEG-4(H.264/Nvenc/VCE) / VP9 / AV1 / Theora)
# O Videocontainer auswahl via config (mkv / mp4 / qtff / asf / avi / mxf / PS / TS / m2ts / evo / 3gp / 3g2 / f4v / ogg / webm)
# O Audiocodec auswahl via config (aac, mp3, opus, flac())
# O Audiocontainer auswahl via config
# O Codec / Containerkombination überprüfen und ggf korrigieren
