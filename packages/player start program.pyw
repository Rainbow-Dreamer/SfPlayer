from PyQt5 import QtGui, QtWidgets, QtCore
import os
import sys

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
with open('packages/player.py', encoding='utf-8') as f:
    exec(f.read())
