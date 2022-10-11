from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import os
import sys

sys.path.append('packages')
import mido_fix
import pygame
import py
import pydub
import fractions
from tkinterdnd2 import DND_FILES, TkinterDnD
import sf2_loader as rs
from ast import literal_eval
with open('packages/player.py', encoding='utf-8') as f:
    exec(f.read())
