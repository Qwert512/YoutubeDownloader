import os,configparser
config = configparser.ConfigParser(allow_no_value=True)
cfg = configparser.ConfigParser()
def create_config():
    #prepares the workspace of the script
    if os.path.exists("links.txt") == False:
            #checks if the links file exists
            links_txt = open("links.txt","w")
            #and if it doesnt, it creates one
    try:
        cfg.read('config.txt')
        reset_str = cfg['misc']['reset']
        reset = {'true': True, 'false': False}.get(reset_str.lower(), False)
        #check if reset is wanted by the user
        
        if reset == True or os.path.getsize('config.txt') == 0:
            #if reset is wanted or the file is empty, delete it so a clean one will be made
            os.remove("config.txt")
    except:
        KeyError

    if os.path.exists("config.txt") == False:
        #if no config file is present, create one!

        config.add_section('video')
        config.set('video', 'resolution', '6')
        config.set('video', '#resolution: 0 = audio only, 1 = 144p, 2 = 240p, 3 = 360p, 4 = 480p,')
        config.set('video', '#5 = 720p, 6 = 1080p, 7 = 1440p, 8 = 4k, 9 = 8k, 10 = max quality')
        config.set('video', '#only for links/playlist mode')

        config.add_section('audio')
        config.set('audio', 'abr', '0')
        config.set('audio', '#audio bitrate (abr): 1 = 48kbps, 2 = 50kbps, 3 = 70kbps, 4 = 128kbps, ')
        config.set('audio', '#5 = 160kbps, 10 = max quality')
        config.set('audio', '#only for links/playlist mode')


        config.add_section('misc')
        config.set('misc', 'config_everywhere', 'False')
        config.set('misc', '#if config everywhere is set to true, the settings above ')
        config.set('misc', '#will be applied to every video, so way less manual input is reqired')
        config.set('misc', 'reset', 'False')
        config.set('misc', '#set this to true to reset everything when executing the program the next time')
        
        with open("config.txt","w") as file:
            config.write(file)
#if __name__ == "__main__":
#schaut ob ichs ausführe