from pytube import YouTube
import requests,  os,  json,  ffmpeg,  shutil
from subprocess import check_output,  run


#required modules
API_KEY = "AIzaSyCAxlEjJXoDBi2xLP79vYG3qMonJ4OAsG0" #google api key for youtube v3 api
tmp_dir = './Downloads_tmp/'
download_dir = './Downloads/'
file_dir = os.path.realpath(__file__)[:-len(os.path.basename(__file__))][:-1]

#ask for the link from the user
def get_link_user():
    link = input("Enter the link of YouTube video you want to download:  ") #fetch user input for the youtube video link
    return link


def get_channel_id(yt):
    return yt.channel_id
    #gives the channel id (the part behind the https://www.youtube.com/c/)

def get_channel_title(cid):
    url = "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={cid}&key={api_key}".format(
        #api request containing the channel id (cid) and the google api key (API_KEY)
        cid=cid,  api_key=API_KEY
    )
    d = requests.get(url).json()
    return d['items'][0]['snippet']['channelTitle']
    #makes an api request to the youtube v3 api by google and get the output in json form
    #then only get the channel name

def num_audio_streams(file_path) -> int:
    command = ['ffprobe ',  "-loglevel",  "quiet",  '-show_streams',  
           '-print_format',  'json',  file_path]
    #Building a command for use in console
    output = check_output(command)
    #use the subprocess module to enter the command into a console and listen to the output
    parsed = json.loads(output)
    #then format the output to json
    streams = parsed['streams']
    audio_streams = list(filter((lambda x: x['codec_type'] == 'audio'),  streams))
    return len(audio_streams)
    #before fetching and returning the number of streams
    #as the file is confirmed to have one video stream,  if the file has 2 or more streams. At least one of them is an audio stream.

def convert(in_folder:str,  out_folder:str,  filename:str,  in_type:str,  out_type:str):
    #Define the convert method. It takes the in and output folders,  the filename,  filetype and the wanted output filetype
    conv_in = ffmpeg.input (in_folder+filename+in_type)
    conv = ffmpeg.output (conv_in,  out_folder+filename + out_type,  )
    ffmpeg.run (conv,  quiet=True)
    #runs the conversion. quiet flag so the console doesnt get spammed,  as there is a LOT of debug in ffmpeg

def convert_no_aud(in_folder:str,  out_folder:str,  filename:str,  in_type:str,  out_type:str):
    #Define the convert_no_aud method. It takes the in and output folders,  the filename,  filetype and the wanted output filetype
    conv_in = ffmpeg.input (in_folder+filename+in_type)
    conv = ffmpeg.output (conv_in.video,  out_folder+filename + out_type,  )
    #the stream.video options only passes the video stream into conversion and dropps the audio
    ffmpeg.run (conv,  quiet=True) 
    #runs the conversion/audio removal. quiet flag so the console doesnt get spammed,  as there is a LOT of debug in ffmpeg

def get_audio_itag(yt,  abr):
    #defining the function to get a specific stream id for the audio stream
    streams = set()
    #define streams as an empty set
    for stream in yt.streams.filter(type="audio"):
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
    print("Pick one of the bitrates below:")
    #then list the availible audiobitrates with an index before
    o = 0
    for k in range(len(bitrates)):
        o+= 1
        print(str(o)+": "+bitrates[k])
    if abr == None:
        rate = int(input(""))
    else:
        rate = abr
    #then ask for user input in form of an index shifted by one
    rate -= 1
    #convert the index to the corresponding array index
    if rate < 0:
        rate = 0
    if rate > len(bitrates)-1:
        rate = len(bitrates)-1
    #filter faulty user input out
    output = yt.streams.filter(abr=bitrates[rate])[0]
    #get the first availible audio stream with a fitting audio bitrate
    tag = output.itag
    #then get the corresponding itag attribute from the stream object (unique identifier of the stream)
    aud_type = output.subtype
    #then get the cooresponding subtype attribute from the stream object,  for further use in conversion,  path related tasks etc.

    tag = int(tag)
    #convert the itag to int as that datatype is required in further processing
    return(tag,  aud_type)
    #return the itag and datatype

def get_video_itag(yt,  resoluti):
    #defining the function to get a specific stream id for the video stream plus additional information
    streams = set()
    
    for stream in yt.streams.filter(type = "video"):
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

    if resoluti == None:
        num = int(input(""))
    else:
        num = resoluti

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

    max = yt.streams.filter(resolution=reso,  mime_type="video/mp4")


    try:
        s = max[0].itag
    except:
        max = yt.streams.filter(resolution=reso)

    for fall in max:
        itag = fall.itag
        vid_type = fall.subtype
        #fallback solution (just takes one)
    
    for avc in max:
        tla = avc.codecs[0]
        tla = tla[0:3]
        if tla == "avc":
            itag = avc.itag
            vid_type = avc.subtype
        #avc1 or H.264
    
    for vp in max:
        tla = vp.codecs[0]
        tla = tla[0:3]
        if tla == "vp9":
            itag = vp.itag
            vid_type = vp.subtype
            #vp9
    
    for av in max:
        tla = av.codecs[0]
        tla = tla[0:3]
        if tla == "av0":
            itag = av.itag
            vid_type = av.subtype
            #av1
    
    if aud_only == True: 
        itag = -1
        vid_type = "audio"
    itag = int(itag)
    return itag,  vid_type,  aud_only

def showdetails(yt):
    #Showing details
    print("")
    print("Title: ",  yt.title)
    #title of the video

    channel_id = get_channel_id(yt)
    channel_title = get_channel_title(channel_id)
    #get channel id (link) and convert it to a name
    print("Channel: ",  channel_title)
    #then print it

    views_raw = yt.views
    #get the views and organise them with dots and replace for example xx.32.xx with xx.032.xx
    views = ""
    views_raw = format(views_raw,  ',')
    views = views_raw.replace(",  ",  ".")
    print("Number of views: ",  views)

    length_sec = yt.length
    #get the length in seconds and display it in hh:mm:ss
    hours = 0

    if length_sec > 3599:
        hours = length_sec // 3600
        length = str(hours)+":"
    else:
        length = ""
    
    minutes = (length_sec // 60) -(hours*60)
    seconds = length_sec - (minutes*60+hours*3600)
    length += str(minutes)+":"

    if minutes != 0 and seconds // 10 == 0:
        length += str(0)
    length += str(seconds)

    print("Length of video: ",  length)
    print("")

def get_filesize(yt,  aud_only,  tag1:int,  tag2:int):
    #Streams
    stream1 = yt.streams.get_by_itag(tag1)
    stream2 = yt.streams.get_by_itag(tag2)

    #Sizes
    size1 = stream1.filesize_approx
    size2 = stream2.filesize_approx

    if aud_only == True:
        size2 = 0
    
    size_tot = str(size1 + size2)
    length = len(size_tot)


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
    return size_tot



def download_and_merge(link:str,  res,  abr):
    #creates the yt class containing all the information about the video
    yt = YouTube(link)
    #create an empty stream for further use in comparisons
    showdetails(yt)


    if res != 0:
        vid_itag,  vid_type,  aud_only = get_video_itag(yt,  res)
    else:
        aud_only = True
    
    aud_itag,  aud_type = get_audio_itag(yt,  abr)


    if aud_only == False:
        vid_stream = yt.streams.get_by_itag(vid_itag)
        vid_name = (download_dir+vid_stream.default_filename[:-len(vid_type)]+"mp4").replace(" ",  "_")
        tmp_vid_name = (download_dir+vid_stream.default_filename[:-(len(vid_type)+1)]+"_tmp"+".mp4").replace(" ",  "_")  
        cln_vid_name = vid_stream.default_filename.replace(" ",  "_")

    
    aud_stream = yt.streams.get_by_itag(aud_itag)
    aud_name = (download_dir+aud_stream.default_filename[:-len(vid_type)]+".mp3").replace(" ",  "_")
    tmp_aud_name = (tmp_dir+aud_stream.default_filename[:-len(aud_type)]+"mp3").replace(" ",  "_")
    cln_aud_name = aud_stream.default_filename.replace(" ",  "_")
    if aud_only == False:
        print(vid_stream)

    print(aud_stream)

    if aud_only == True:
        filesize = get_filesize(yt,  aud_only,  aud_itag,  aud_itag)
    else:
        filesize = get_filesize(yt,  aud_only,  vid_itag,  aud_itag)
    
    #Starting download
    print("Downloading approximately "+filesize+"...")

    if aud_only == False:
        vid_stream.download(download_dir)
        os.rename(download_dir+vid_stream.default_filename,download_dir+(vid_stream.default_filename.replace(" ","_")))

    aud_stream.download(tmp_dir)
    os.rename(tmp_dir+aud_stream.default_filename,tmp_dir+(aud_stream.default_filename.replace(" ","_")))
    print("Download completed.")

    print("\nConverting...")
    if aud_type != "mp3":
        convert(tmp_dir,  tmp_dir,  cln_aud_name[:-(len(aud_type)+1)],  "."+aud_type,  ".mp3")
        os.remove(tmp_dir+cln_aud_name)


    if aud_only == False and vid_type != "mp4":
        if num_audio_streams(download_dir+cln_vid_name) == 0:
            convert(download_dir,  download_dir,  cln_vid_name[:-(len(vid_type)+1)],  "."+vid_type,  ".mp4")
        else:
            convert_no_aud(download_dir,  download_dir ,  cln_vid_name[:-(len(vid_type)+1)],  "."+vid_type,  ".mp4")

        os.remove(download_dir+cln_vid_name)
    print("Converting completed.")
    print("Merging...")


    if aud_only:
        if os.path.exists(aud_name):
            os.remove(aud_name)
        os.rename(tmp_aud_name,  aud_name)
        
          
    else:
         command = "ffmpeg -i "+file_dir+vid_name[1:]+" -i "+file_dir+tmp_aud_name[1:]+" -c:v copy -c:a copy -hide_banner -loglevel error "+file_dir+tmp_vid_name[1:]
         run(command,check = True)
         os.remove(vid_name)
         os.rename(tmp_vid_name,  vid_name)

    
    shutil.rmtree(tmp_dir)
    print("Merging completed.")



if os.path.exists(tmp_dir):
    shutil.rmtree(tmp_dir)



if os.path.getsize("links.txt") != 0:
    with open("config.txt") as fp:
        for i,  line in enumerate(fp):
            if i == 0:
                res = line
                res = int(''.join(filter(str.isdigit,  res)))
            elif i == 1:
                abr = line
                abr = int(''.join(filter(str.isdigit,  abr)))
            elif i > 1:
                break
    with open("links.txt") as file:
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]
        for i in lines:
            download_and_merge(i,  res,  abr)
    file = open("links.txt",  "w")
    file.truncate(0)
    download_and_merge(get_link_user(),  None,  None)


elif os.path. getsize("links.txt") == 0:
    download_and_merge(get_link_user(),  None,  None)
#todo:
# O kommentieren
# O playlist runterladen
# O UI
# O Multitasking (downloaden während conversion,  conversion während merging) threading / Wenns sein muss "AsyncIO"
# O speed mode (yt.streams.get_highest_resolution())
# O Bei Qualitätsauswahl anzeigen wenn audio / video auf einmal verfügbar
# O mehr config möglichkeiten mit config parser
# O progress bars (evtl. merging) converting
# O Grafikkarte nutzen (+config option (amd/Nvidia/Intel)) https://youtu.be/m3e4ED6FY4U
# O setup.py (links.txt,  config erstellen etc)
# O Github release
# O Videocodec auswahl via config (MPEG-4(H.264/Nvenc/VCE) / VP9 / AV1 / Theora)
# O Videocontainer auswahl via config (mkv / mp4 / qtff / asf / avi / mxf / PS / TS / m2ts / evo / 3gp / 3g2 / f4v / ogg / webm)
# O Audiocodec auswahl via config (aac, mp3, opus, flac())
# O Audiocontainer auswahl via config
# O Codec / Containerkombination überprüfen und ggf korrigieren