import re

def extract_timestamps_and_descriptions(text):
  pattern1_matches = re.findall(r'(\d+:\d+(?::\d+)?)\s*(.*)', text)

  timestamp_text_tuples = []
  timestamps = []
  content = []
  for match in pattern1_matches:
    timestamp_text_tuples.append((match[0], match[1]))
    timestamps.append(match[0])

  all_lines = str.splitlines(text)
  for i in all_lines:
     for u in timestamps:
        if u in i:
           content.append(i.replace(u,""))
           break
  
  timestamp_text_tuples = []

  for n in range(len(timestamps)):
     timestamp_text_tuples.append((timestamps[n],content[n].replace("#","")))

  return timestamp_text_tuples
  # Skip header lines (assuming lines before "Tracklist:")

# Test the function with sample text


text_1 = """
Stick Figure / Set in Stone (Full Album)\n\nTracklist:\n01. Fire on the Horizon   0:05 - 5:34\n02. In this Love    5:34 - 9:49\n03. Sound of the Sea    9:49 - 15:16\n04. Choice is yours    15:16 - 20:23\n05. Mind Block    20:23 - 24:41\n06. Sentenced    24:41 - 28:55\n07. Out the Door    28:55 - 33:31\n08. Weary Eyes    33:31 - 37:14\n09. Smokin` Love    37:14 - 40:50\n10. Shadow    40:50 - 44:43\n11. One of those Days    44:43 - 49:05\n12. All my Love    49:05 - 53:21\n13. Sunshine and Rain    53:21 - 55:50\n14. Smiles on Faces    55:50 - 1:00:08\n\nBuy the album on iTunes - https://itunes.apple.com/us/album/set-in-stone/id1045767173 \nBuy / listen to the album on Bandcamp - https://stickfigure.bandcamp.com/\nFollow Stick Figure online\nhttp://www.stickfiguremusic.com/\nhttps://www.facebook.com/stickfiguremusic
"""
text_2 = """
Stick Figure – Wisdom (Full Album)\nNew album 'Wisdom' - https://ineffable.to/WISDOM \n\n00:00:00 - Old Sunrise\n00:05:22 - Paradise\n00:09:32 - Way of Life (feat. Slightly Stoopid)\n00:13:46 - Edge of the Ocean\n00:18:42 - Stepping Stones\n00:22:55 - Fall into the Sun\n00:27:12 - Showdown (feat. Collie Buddz)\n00:31:37 - Soul of the World (feat. Barrington Levy)\n00:35:07 - Smoke Signals\n00:39:31 - Here Comes the Sound\n00:42:57 - Sound System\n00:46:25 - Satisfaction Feeling\n00:50:43 - Higher (feat. Slightly Stoopid)\n00:54:58 - Falling Stars\n\nSacred Sands Summer Tour 2024: \n7/11 - Albuquerque, NM - https://6xxb.short.gy/stickalbuquerque \n7/13 - San Diego, CA - https://6xxb.short.gy/sticksandiego1\n7/14 - San Diego, CA - https://6xxb.short.gy/sticksandiego2\n7/16 - Los Angeles, CA - https://6xxb.short.gy/sticklosangeles\n7/18 - Bend, OR - https://6xxb.short.gy/stickbend \n7/20 - Tacoma, WA - https://6xxb.short.gy/sticktacoma \n7/24 - Morrison, CO - https://6xxb.short.gy/stickredrocks1\n7/25 - Morrison, CO - https://6xxb.short.gy/stickredrocks2 \n7/27 - Colorado TBA \n7/30 - Chicago, IL - https://6xxb.short.gy/stickchicago \n8/1 - Thornville, OH - https://6xxb.short.gy/stickeverwild \n8/3 - Mansfield, MA - https://6xxb.short.gy/stickmansfield \n8/6 - Virginia Beach, VA - https://6xxb.short.gy/stickvirginiabeach \n8/8 - Charleston, SC - https://6xxb.short.gy/stickcharleston \n8/10 - West Palm Beach, FL - https://6xxb.short.gy/stickwestpalmbeach \n8/12 - Key West, FL - https://6xxb.short.gy/stickkeywest\n\nhttp://www.stickfigure.com\r\nhttps://www.facebook.com/stickfiguremusic\r\nhttp://www.twitter.com/StickFigureDub\r\nhttp://www.soundcloud.com/stickfigure\r\nhttps://www.instagram.com/stickfiguremusic
"""
text_3 = """
Sticky Fingers website : https://stickyfingerstheband.com/\nSticky Fingers merch : https://sticky-fingers-uk.myshopify.com/\n\nTracklist\n1. How To Fly (0:00)\n2. These Girls (3:11)\n3. Lazerhead (6:32)\n4. Velvet Skies ft. Lyall Moloney (12:24)\n5. Australia Street (17:14)\n6. Gold Snafu (20:50)\n7. Bootleg Rascal (24:30)\n8. Caress Your Soul (28:14)\n9. Another Episode (31:04)\n10. Liquorlip Loaded Gun (35:58)\n11. Cool & Calm (41:07)\n12. Rum Rage (44:24) \n13. Sunsick Moon (48:33)\n14. Change (52:07)\n15. Cyclone (56:24)\n\n\nFollow Sticky Fingers\nhttps://www.facebook.com/stickyfingersmusic\nhttps://www.instagram.com/stickyfingersband/\nhttps://www.youtube.com/channel/UCRC74iukYTRgzOZhlQq1f7A\n\nWe don't own the rights of the uploaded songs, contact us if you want us to delete a video\nrascalmusic1995@gmail.com
"""
text_4="""
KBong - 'Easy To Love You' Full Album 🌠\nShop KBong Merch ➡️ https://kbongmerch.myshopify.com/\n\n1. Easy To Love You (feat. The Movement) 0:00\n2. Good Lovin 4:15\n3. Middle Of The Ocean (feat. Stic
k Figure) 8:23\n4. Heavy As Gold 12:52\n5. Music And The Message 17:01\n6. Long Distance Lover 22:00\n7. Need A Ride 26:24\n8. Travelin On 31:01\n9. Open My Eyes 36:39\n10. Lovelight 41:19\n11. One More Song (feat. Johnny Cosmic) 45:34\n12. Awake (feat. Raging Fyah) 50:06\n\nMerch, Tour Dates + More\nhttps://kbongmusic.com\n\nKBong Social Links\nhttps://facebook.com/kbongmusic\nhttp://twitter.com/kbongmusic\nhttp://youtube.com/kbongmusic\nhttps://instagram.com/kbongmusic\n\nProduced By : Johnny Cosmic\n#KBong #EasyToLoveYou
"""

examples = [text_1,text_2,text_3,text_4]
for i in examples:
    i = i.replace("\n","#\n")
    extracted_data = extract_timestamps_and_descriptions(i)
    print(extracted_data)
    print("\n")