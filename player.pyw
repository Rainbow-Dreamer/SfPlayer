from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import os
import sys

sys.path.append('packages')
import sf2_loader as rs
from ast import literal_eval


class Root(Tk):
    def __init__(self):
        super(Root, self).__init__()
        self.minsize(850, 600)
        self.title('SoundFont MIDI Player')
        self.choose_midi_button = ttk.Button(self,
                                             text='Choose MIDI File',
                                             command=self.choose_midi)
        self.choose_midi_button.place(x=50, y=100)
        self.choose_soundfont_button = ttk.Button(
            self, text='Choose SoundFont File', command=self.choose_soundfont)
        self.choose_soundfont_button.place(x=50, y=200)
        self.current_midi_file = None
        self.current_soundfont_file = None
        self.current_sf2 = None
        self.current_midi_label = ttk.Label(self, text='Not chosen')
        self.current_soundfont_label = ttk.Label(self, text='Not chosen')
        self.current_midi_label.place(x=200, y=102)
        self.current_soundfont_label.place(x=200, y=202)
        self.play_button = ttk.Button(self,
                                      text='Play',
                                      command=self.play_midi)
        self.play_button.place(x=50, y=300)
        self.pause_button = ttk.Button(self,
                                       text='Pause',
                                       command=self.pause_midi)
        self.pause_button.place(x=200, y=300)
        self.unpause_button = ttk.Button(self,
                                         text='Unpause',
                                         command=self.unpause_midi)
        self.unpause_button.place(x=350, y=300)
        self.stop_button = ttk.Button(self,
                                      text='Stop',
                                      command=self.stop_midi)
        self.stop_button.place(x=500, y=300)
        self.msg = ttk.Label(self, text='Currently no actions')
        self.msg.place(x=50, y=550)
        self.paused = False
        self.current_path = '.'
        self.custom_instrument_label = ttk.Label(self,
                                                 text='Custom Instruments')
        self.custom_instrument_label.place(x=50, y=400)
        self.custom_instrument_text = ttk.Entry(self, width=60)
        self.custom_instrument_text.place(x=50, y=430)
        self.custom_play_button = ttk.Button(self,
                                             text='Custom play',
                                             command=self.custom_play)
        self.custom_play_button.place(x=230, y=395)

    def show(self, text=''):
        self.msg.configure(text=text)
        self.msg.update()

    def choose_midi(self):
        current_midi_file = filedialog.askopenfilename(
            initialdir=self.current_path,
            title="Choose MIDI File",
            filetypes=(('MIDI files', "*.mid"), ("All files", "*.*")))
        if current_midi_file:
            self.current_midi_file = current_midi_file
            self.current_midi_label.configure(text=self.current_midi_file)
            self.current_path = os.path.dirname(self.current_midi_file)

    def choose_soundfont(self):
        current_soundfont_file = filedialog.askopenfilename(
            initialdir=self.current_path,
            title="Choose SoundFont File",
            filetypes=(('SoundFont files', "*.sf2;*.sf3;*.dls"), ("All files",
                                                                  "*.*")))
        if current_soundfont_file:
            self.current_soundfont_file = current_soundfont_file
            self.current_soundfont_label.configure(
                text=self.current_soundfont_file)
            self.current_soundfont_label.update()
            self.current_sf2 = rs.sf2_loader(self.current_soundfont_file)
            self.current_path = os.path.dirname(self.current_soundfont_file)

    def play_midi(self):
        if self.current_midi_file and self.current_soundfont_file:
            if rs.mp.pygame.mixer.get_busy():
                rs.mp.pygame.mixer.stop()
            self.show(f'Rendering MIDI file to audio, please wait ...')
            self.current_sf2.play_midi_file(self.current_midi_file)
            self.show(f'Start playing')

    def pause_midi(self):
        if rs.mp.pygame.mixer.get_busy():
            rs.mp.pygame.mixer.pause()
            self.paused = True
            self.show(f'Pause playing')

    def unpause_midi(self):
        if self.paused:
            rs.mp.pygame.mixer.unpause()
            self.paused = False
            self.show(f'Continue playing')

    def stop_midi(self):
        if rs.mp.pygame.mixer.get_busy():
            rs.mp.pygame.mixer.stop()
            self.paused = False
            self.show(f'Stop playing')

    def custom_play(self):
        if self.current_midi_file and self.current_soundfont_file:

            current_midi_file = rs.mp.read(self.current_midi_file,
                                           mode='all',
                                           to_piece=True)
            try:
                current_instruments = literal_eval(
                    f'[{self.custom_instrument_text.get()}]')
            except:
                self.show('invalid instruments')
                return
            if len(current_instruments) < len(current_midi_file):
                current_instruments += current_midi_file.instruments_numbers[
                    len(current_instruments):]
            current_midi_file.change_instruments(current_instruments)
            current_midi_file.clear_program_change()
            if rs.mp.pygame.mixer.get_busy():
                rs.mp.pygame.mixer.stop()
            self.show(f'Rendering MIDI file to audio, please wait ...')
            self.current_sf2.play_piece(current_midi_file)
            self.show(f'Start playing')


root = Root()
root.mainloop()
