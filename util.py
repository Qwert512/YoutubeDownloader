import asyncio
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
    
    size_total = str(size1 + size2)
    #then the two sizes are combined
    length = len(size_total)
    #then the length of the size in bytes is taken, 
    #so it can be displayed more nicely in for example MB


    if length < 4:
        size_total = size_total+" B"
    elif length < 7 and length > 3:
        size_total = size_total[:length-3]+" KB"
    elif length < 10 and length > 6:
        size_total = size_total[:length-6]+" MB"
    elif length < 13 and length > 9:
        size_total = size_total[:length-9]+" GB"
    elif length < 16 and length > 12:
        size_total = size_total[:length-12]+" TB"
        #here the formatting is done
    return size_total
    #now the formatted size is returned

async def showdetails(yt):
    information = str()
    information += ("\nTitle: "+yt.title)
    #title of the video

    channel = yt.author
    information += ("\nChannel: "+ channel)
    #Channel title

    views_raw = yt.views
    #get the views 
    views = str()
    views_raw = format(views_raw,  ',')
    #then format them with commas for each three digits
    views = views_raw.replace(",",  ".")
    #then because im european, replace the commas with dots
    information += ("\nNumber of views: "+views)

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
    information += ("\nLength of video: "+  length+ "\n")
    return(information)
    
