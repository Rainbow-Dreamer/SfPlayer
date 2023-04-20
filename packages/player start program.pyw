from PyQt5 import QtGui, QtWidgets, QtCore
import os
import sys

abs_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(abs_path)
sys.path.append(abs_path)
sys.path.append('packages')
import pygame
import py
import pydub
import fractions
import sf2_loader as rs
from ast import literal_eval
import textwrap
import mido_fix as mido
import random
import json
with open('packages/player.py', encoding='utf-8') as f:
    exec(f.read())
