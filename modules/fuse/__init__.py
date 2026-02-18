"""
IS A TELEGRAM FUSE
TO USE AS FILE SAVER 
"""
from modules.fuse.file import *
from modules.fuse.folder import *
from modules.fuse.fsinfo import *

from modules.gvar import *
import os

fuse = os

try:
    os.mkdir("env")
except Exception as e:
    pass

FUSE_GROUP_ID = None
if FUSE_GROUP_ID == None:
    fuse_off = 1
else:
    try:
        pass
    except Exception as e:
        print(e)
        fuse = os