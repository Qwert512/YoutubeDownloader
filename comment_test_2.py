import re

comment_text = """
Setlist<br>Intro <a href="https://www.youtube.com/watch?v=3gB6tthtkLU&amp;t=1">0:01</a><br>01. I&amp;I <a href="https://www.youtube.com/watch?v=3gB6tthtkLU&amp;t=373">06:13</a><br>02. Flames <a href="https://www.youtube.com/watch?v=3gB6tthtkLU&amp;t=529">08:49</a><br>03. Resist Not Evil <a href="https://www.youtube.com/watch?v=3gB6tthtkLU&amp;t=669">11:09</a><br>04. Criminal <a href="https://www.youtube.com/watch?v=3gB6tthtkLU&amp;t=781">13:01</a><br>05. Wrong Side Of The Law <a href="https://www.youtube.com/watch?v=3gB6tthtkLU&amp;t=1138">18:58</a><br>06. This Is Not A Marijuana Song <a href="https://www.youtube.com/watch?v=3gB6tthtkLU&amp;t=1490">24:50</a><br>07. Deliverance <a href="https://www.youtube.com/watch?v=3gB6tthtkLU&amp;t=1719">28:39</a><br>08. Rasta Love <a href="https://www.youtube.com/watch?v=3gB6tthtkLU&amp;t=1932">32:12</a><br>09. Hills <a href="https://www.youtube.com/watch?v=3gB6tthtkLU&amp;t=2215">36:55</a><br>10. Switch It Up <a href="https://www.youtube.com/watch?v=3gB6tthtkLU&amp;t=2511">41:51</a><br>11. Like Royalty <a href="https://www.youtube.com/watch?v=3gB6tthtkLU&amp;t=2843">47:23</a><br>12. No Guarantee <a href="https://www.youtube.com/watch?v=3gB6tthtkLU&amp;t=3093">51:33</a><br>13. Hail Ras Tafari <a href="https://www.youtube.com/watch?v=3gB6tthtkLU&amp;t=3407">56:47</a><br>14. Who Knows <a href="https://www.youtube.com/watch?v=3gB6tthtkLU&amp;t=3947">1:05:47</a><br>15. Kingston Be Wise <a href="https://www.youtube.com/watch?v=3gB6tthtkLU&amp;t=4294">1:11:34</a>"""

# Regular expression to extract timestamp and description
pattern = r'<a href="[^"]+">([^<]+)</a>\s*([^<]+)'

# Extract timestamps and descriptions
timestamps_descriptions = re.findall(pattern, comment_text)

# Convert the result to a list of tuples
timestamps_descriptions = [(timestamp.strip(), description.strip()) for timestamp, description in timestamps_descriptions]

print(timestamps_descriptions)
