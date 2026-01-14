import tarfile

class Tar:
    base:tarfile.TarFile = None

    def __init__(self,name, mode = "a"):
        self.name = name
        self.mode = mode
        self.base = None
        self.open()

    def add(self,file):
        if self.base:
            self.base.add(file)

    def pop(self,file):
        if self.base:
            self.base.extract(file)

    def find(self,file):
        if self.base:
            try:
                self.base.getmember(file)
                return True
            except KeyError:
                return False
        return False

    def save(self,file):
        self.add(file)

    def open(self):
        if self.base is None:
            self.base = tarfile.open(self.name, self.mode)

    def close(self):
        if self.base:
            self.base.close()
            self.base = None
