from .fsinfo import *

import base64


class file(fsinfo):
    def __init__(self, name ,bot = None ,gid= None,mode = "wb"):
        self.pointer  = 0
        self.root     = 0
        self.tmp_size = 0
        self.curr_id  = 0
        self.chunks   = []
        self.type     = FILE
        self.bot      = bot
        self.gid      = gid
        self.mode     = mode
        self.curr     = open("tmp",mode)
        
    def __dict__(self):
        return {
            "type":self.type,
            "name":self.name,
            "id:" :self.id,
            "size":self.size,
            "date":self.created_at,
            "chunks": self.chunks
        }

    def __str__(self):
        mess = f"{self.type},{self.name},{self.id},{self.created_at},{self.size}"
        for i in self.chunks:
            mess += f",{i}"
        return mess

    def chmod(self):
        self.mode = "rb" if self.mode == "wb" else "wb"

    def getFileOf(self,idx):
        return idx // self.max_size

    def _download(self, chunk_id):
        raise "not imp"

    def seek_read(self, newpos): #! arreglar esto si esta mal cuando no es inicio de archivo
        if newpos == 0:
            self.pointer = newpos
            return
        raise "error seek no implemented"

    def _read(self, file, size):
        fil = open(file, "rb")
        data = fil.read(size) 
        fil.close()
        return data

    def read(self,count): #! ESTA FUNCION TIENE ERRORES (creo)
        self.check()

        if self.mode != "rb":
            raise Exception("Mode error, try in another mode")

        if not isinstance(count, int):
            raise TypeError("count must be int")

        if count <= 0 or self.pointer >= self.size:
            return b""

        eor = min(self.pointer + count, self.size)
        data = b""

        while self.pointer < eor:
            act_file = self.getFileOf(self.pointer)
            if act_file < 0 or act_file >= len(self.chunks):
                break

            self._download(self.chunks[act_file])

            in_chunk_offset = self.pointer % self.max_size
            remaining = eor - self.pointer
            to_read = min(self.max_size - in_chunk_offset, remaining)

            with open("tmp", "rb") as fil:
                fil.seek(in_chunk_offset)
                piece = fil.read(to_read)

            if not piece:
                break

            data += piece
            self.pointer += len(piece)

            if len(piece) < to_read:
                break

        return data

    def write(self,reader):
        self.check()
        if self.mode != "wb":
            raise "Mode error, try in another mode"
        
        if self.tmp_size + len(reader) > self.max_size:
            res = self.max_size - self.tmp_size
            self.curr.write(reader[:res])
            self.curr.close()
            self.save_file("tmp")
            self.curr = open("tmp","wb")
            wdata = reader[res:]
            self.write(wdata)
            self.size += len(wdata)
            return

        self.curr.write(reader)
        self.tmp_size += len(reader)
        self.size += len((reader))

    def save_file(self,path):
        sent:pyrogram.types.Message = self.bot.send_document(
            chat_id=self.gid,
            document=path,
            caption=f"file:{self.name},part:{len(self.chunks)+1}"
        )
        self.chunks.append(sent.id)
        self.tmp_size = 0

    def get_size(self):
        self.check()

    def close(self):
        self.curr.close()
        if self.tmp_size > 0:
            self.save_file("tmp")
        self.save()

    def save(self):
        if self.tmp_size > 0:
            raise "temp file not saved yet"
        f=open("tmp.meta","wb")
        f.write(str(self).encode())
        f.close()
        self.id = self.bot.send_document(
            chat_id=self.gid,
            document="tmp.meta",
            caption=f"file:{self.name}.meta"
        ).id
