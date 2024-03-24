import timestamps
api_key = "AIzaSyAzkLcbTqYfW8KHY5lZQlVdPeCzI4D8xIc"
with open("video_examples.txt","r") as file:
    lines = file.readlines()

video_id = timestamps.url_to_id(url=url).strip()
for id in lines:
    id = id.strip()
    if id == None:
        print("Invalid video url")
    else:
        video_id = timestamps.url_to_id(url=url).strip() 

        #check description
        timestamps_tuple = timestamps.extract_timestamps_description(url="https://www.youtube.com/watch?v="+video_id)
        if len(timestamps_tuple) == 0:
            comments = timestamps.scrape_comments(video_id=video_id,api_key=api_key)
            if len(comments) != 0:
                timestamps_tuple = timestamps.extract_timestamps_comment(comment_text=comments[0])
        if len(timestamps_tuple) != 0:
            print(timestamps.format_timestamps(timestamps_tuple,"https://www.youtube.com/watch?v="+video_id)) # type: ignore
        else:
            print("No timestamps found :C")   
    print("\n")