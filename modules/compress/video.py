import os
import time
import subprocess as subp
from threading import Thread
import gc

ffmpeg_threads       = os.getenv("ffmpeg_threads", 1)
ffmpeg_preset        = os.getenv("preset","fast")
ffmpeg_frame_threads = os.getenv("ffmpeg_freme_threads", 1)
numa                 = os.getenv("numa",":numa-pools=none") 
class VideoCompressor():
    def __init__(self,filename = None,callback = None,args = [],parse_end=False):
        self.base_cmd = f'ffmpeg -threads {ffmpeg_threads} -i "$in$" -c:v libx265 -preset {ffmpeg_preset} -x265-params frame-threads={ffmpeg_frame_threads}{numa} "$out$"'
        self.out = '$out$'  
        self.inp = '$in$'
        self.stop = False
        self.callback = callback
        self.name = None
        self.args = args    
        self.ended = True
        self.parse_ended = parse_end
        self.set_file(filename)


    def compress(self):
        if self.name == None:
            return False
        
        self.ended = False
        th = Thread(target = self.stat_update)
        th.start()
        try:
            subp.run(self.base_cmd, shell=True)
        except Exception as e:
            print(f"video compress error [{e}]")    

        gc.collect()
        self.stop = True
        self.ended = True
        return True

    def set_file(self,filename):
        if not os.path.isfile(filename):
            return False
        self.name = filename
        self.base_cmd=self.base_cmd.replace(self.inp,filename)
        self.base_cmd=self.base_cmd.replace(self.out, filename + ".comp.mp4")
        print("=======================",self.base_cmd,"=======================")
        self.inp = filename
        self.out = filename + ".comp.mp4"
        return True

    def stat_update(self):
        total = 0
        part = 0
        while True:       
            time.sleep(3)
            if self.stop:
                break
                
            if os.path.exists(self.inp):
                total = os.path.getsize(self.inp)
            if os.path.exists(self.out):
                part  = os.path.getsize(self.out)
            
            percent = 0
            if total > 0:
                percent = part / total * 100
                
            if self.callback != None:
                if self.parse_ended :
                    self.callback(total,part,self.ended,*self.args)
                else:
                    self.callback(total,part,*self.args)
                    
        if self.callback != None:
            if os.path.exists(self.inp):
                total = os.path.getsize(self.inp)
            if os.path.exists(self.out):
                part  = os.path.getsize(self.out)

            if self.parse_ended :
                self.callback(total,part,self.ended,*self.args)
            else:
                self.callback(total,part,*self.args)