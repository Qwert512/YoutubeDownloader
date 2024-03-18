import timestamps
api_key = "AIzaSyAzkLcbTqYfW8KHY5lZQlVdPeCzI4D8xIc"
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
        timestamps_description = timestamps.extract_timestamps_description(url="https://www.youtube.com/watch?v="+video_id)
        if len(timestamps_description) == 0:
            comments = timestamps.scrape_comments(video_id=video_id,api_key=api_key)
            if len(comments) == 0:
                print("No timestamps found")
            else:
                setlist = timestamps.extract_timestamps_comment(comment_text=comments[0])
                print(timestamps.format_timestamps(setlist,"https://www.youtube.com/watch?v="+video_id))
        else:
            print(timestamps.format_timestamps(timestamps_description,"https://www.youtube.com/watch?v="+video_id))


        
    print("\n")