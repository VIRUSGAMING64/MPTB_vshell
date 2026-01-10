import os
import time
import subprocess as subp
from threading import Thread
import gc


class VideoCompressor():
    def __init__(self,filename = None,callback = None,args = [],parse_end=False):
        self.base_cmd = "ffmpeg -threads 1 -i $in$ -c:v libx265 -preset fast -x265-params frame-threads=1:numa-pools=none $out$"
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
            subp.run(self.base_cmd, shell=True, stdout=subp.DEVNULL, stderr=subp.DEVNULL)
        except Exception as e:
            print(f"video compress error [{e}]")    

        # Forzar recolección de basura
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
        self.inp = filename
        self.out = filename + ".comp.mp4"
        return True


    def stat_update(self):
        while True:       

            time.sleep(1)
            if self.stop:
                break

            total = os.path.getsize(self.inp)
            part  = os.path.getsize(self.out)
            percent = part / total * 100
            if self.callback != None:
                if self.parse_ended :
                    self.callback(total,part,self.ended,*self.args)
                else:
                    self.callback(total,part,*self.args)
                    
        if self.callback != None:
            if self.parse_ended :
                self.callback(total,part,self.ended,*self.args)
            else:
                self.callback(total,part,*self.args)