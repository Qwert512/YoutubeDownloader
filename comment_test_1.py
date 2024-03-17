from googleapiclient.discovery import build
#credentials 
video_id= "MCJ5A_0iq08"
api_key = "AIzaSyAzkLcbTqYfW8KHY5lZQlVdPeCzI4D8xIc"

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
    print("------------------------------------------------------------------------------------------------------")
    for item in items:
        item_info = item["snippet"]
        
        #the top level comment can have sub reply comments
        comment_info = item_info["topLevelComment"]["snippet"]
        #if comment_info["textDisplay"].count("t=") >2:
        possible_setlists.append(comment_info["textDisplay"])
        print("Comment By:", comment_info["authorDisplayName"])
        print("Coment Text:" ,comment_info["textDisplay"])
        print("Likes on Comment :", comment_info["likeCount"])
        print("Comment Date: ", comment_info['publishedAt'])
        print("================================\n")
    return(possible_setlists)

scrape_comments(video_id=video_id,api_key=api_key)
