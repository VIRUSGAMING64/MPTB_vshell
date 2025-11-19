"""
IS A TELEGRAM FUSE
TO USE AS FILE SAVER 
"""

from modules.gvar import *

if FUSE_GROUP_ID == None:
    fuse_off = 1
    try:
        os.mkdir("env")
    except Exception as e:
        pass
    
    os.chdir("env")
    fuse = os

else:
    pass