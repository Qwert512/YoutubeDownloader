import timestamps
api_key = "AIzaSyAzkLcbTqYfW8KHY5lZQlVdPeCzI4D8xIc"
#url = "https://www.youtube.com/watch?v=9dCZ-9StrlU"
with open("video_examples.txt","r") as file:
    lines = file.readlines()

#id = timestamps.url_to_id(url=url)
for id in lines:
    id = id.strip()
    if id == None:
        print("Invalid video url")
    else:
        video_id= id

        #check description
        timestamps_description = timestamps.formt_timestamps(url="https://www.youtube.com/watch?v="+video_id)
        if len(timestamps_description) == 0:
            print("No timestamps found in description")
        else:
            print(timestamps_description)


        comments = timestamps.scrape_comments(video_id=video_id,api_key=api_key)
        if len(comments) == 0:
            print("No timestamps found in comments")
        else:
            setlist = timestamps.extract_timestamps_comment(comment_text=comments[0])
            print("Comment timestamps from "+id+": \n")
            print(comments[0]+"\n")
            print(setlist)
    print("\n")