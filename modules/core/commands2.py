import requests
from modules.core.queues import *
from modules.gvar import *
import os
from modules.utils import *
import asyncio
import threading as th
from modules.fuse import *


def comp(message:Message):
    args = message.text


def ren(message:Message):
    args = message.text