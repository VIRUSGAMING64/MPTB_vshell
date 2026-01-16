from modules.downup.video_core import VidDownloader

def insta_downloader(url,user,bot,chat_id,progress,args):
    VidDownloader(bot,user,chat_id,progress,args).download_video(url)

def youtube_downloader(url,user,bot,chat_id,progress,args):
    VidDownloader(bot,user,chat_id,progress,args).download_video(url)

def face_downloader(url,user,bot,chat_id,progress,args):
    VidDownloader(bot,user,chat_id,progress,args).download_video(url)

def generic_downloader(url,user,bot,chat_id,progress,args):
    VidDownloader(bot,user,chat_id,progress,args).download_video(url)