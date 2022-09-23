import os,configparser
config = configparser.ConfigParser
if os.path.exists("links.txt") == False:
        #checks if the links file exists
        links_txt = open("links.txt","w")
        #and if it doesnt, it creates one
if os.path.exists("config.txt") == False:

    config.add_section('video')
        config.add_section('video')

    config.set('postgresql', 'host', 'localhost')
    with open("config.txt") as cfg:
        cfg.write(
            
        )