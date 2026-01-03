import tarfile

class Tar:
    base:tarfile.TarFile = None

    def __init__(self,name, mode = "a"):
        self.name = name
        self.base = tarfile.TarFile(name, mode)
        self.mode = mode

    def add(self,file):
        self.base.add(file)

    def pop(self,file):
        self.base.extract(file)

    def find(self,file):
        pass

    def save(self,file):
        pass

    def open(self):
        pass

    def close(self):
        pass
