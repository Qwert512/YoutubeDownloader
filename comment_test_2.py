import re

with open("test.txt", "r") as file:
    comment = file.readline()
    matches = re.findall(r'<a.*?>(.*?)</a>\s*(.*?)<br>', comment)

    # Export timestamp and text pairs into tuples
    timestamp_text_tuples = [(match[0], match[1]) for match in matches]

    # Print the tuples
    for timestamp, text in timestamp_text_tuples:
        print(text)
