from PyQt5 import QtGui, QtWidgets, QtCore
import os
import sys

sys.path.append('packages')
import sf2_loader as rs
import textwrap
import mido_fix as mido
import random
import json

with open('packages/config.json', encoding='utf-8') as f:
    globals().update(json.load(f))


def set_font(font, dpi):
    if dpi != 96.0:
        font.setPointSize(int(font.pointSize() * (96.0 / dpi)))
    return font


class Dialog(QtWidgets.QMainWindow):

    def __init__(self,
                 caption,
                 directory,
                 filter=None,
                 default_filename=None,
                 mode=0):
        super().__init__()
        if mode == 0:
            self.filename = QtWidgets.QFileDialog.getOpenFileName(
                self, caption=caption, directory=directory, filter=filter)
        elif mode == 1:
            self.directory = QtWidgets.QFileDialog.getExistingDirectory(
                self, caption=caption, directory=directory)
        elif mode == 2:
            self.filename = QtWidgets.QFileDialog.getSaveFileName(
                self,
                caption,
                os.path.join(directory, default_filename),
                filter=filter)


class Button(QtWidgets.QPushButton):

    def __init__(self,
                 *args,
                 color='light grey',
                 function=None,
                 x=None,
                 y=None,
                 font=None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet(f'background-color: {color}')
        if function is not None:
            self.clicked.connect(function)
        if x is not None and y is not None:
            self.move(x, y)
        if font is None:
            font = QtGui.QFont('Consolas', 10)
        self.setFont(set_font(font, dpi))
        self.adjustSize()

    def place(self, x, y):
        self.move(x, y)


class Label(QtWidgets.QLabel):

    def __init__(self,
                 *args,
                 color='light grey',
                 x=None,
                 y=None,
                 font=None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet(f'background-color: {color}')
        if x is not None and y is not None:
            self.move(x, y)
        if font is None:
            font = QtGui.QFont('Consolas', 10)
        self.setFont(set_font(font, dpi))
        self.adjustSize()

    def place(self, x, y):
        self.move(x, y)

    def configure(self, text):
        self.setText(text)
        self.adjustSize()


class Timer(QtCore.QTimer):

    def __init__(self, time, function):
        super().__init__()
        self.setSingleShot(True)
        self.timeout.connect(function)
        self.start(time)


class Slider(QtWidgets.QSlider):

    def __init__(self,
                 *args,
                 value=None,
                 function=None,
                 x=None,
                 y=None,
                 range=[0, 100],
                 width=200,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.setRange(*range)
        self.setFixedWidth(width)
        if value is not None:
            self.setValue(value)
        if function is not None:
            self.valueChanged.connect(function)
        if x is not None and y is not None:
            self.move(x, y)

    def place(self, x, y):
        self.move(x, y)

    def change(self, value):
        self.blockSignals(True)
        self.setValue(value)
        self.blockSignals(False)


class CheckBox(QtWidgets.QCheckBox):

    def __init__(self,
                 *args,
                 value=None,
                 function=None,
                 x=None,
                 y=None,
                 font=None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        if value is not None:
            self.setChecked(value)
        if function is not None:
            self.clicked.connect(function)
        if x is not None and y is not None:
            self.move(x, y)
        if font is None:
            font = QtGui.QFont('Consolas', 10)
        self.setFont(set_font(font, dpi))
        self.adjustSize()

    def place(self, x, y):
        self.move(x, y)


class Root(QtWidgets.QMainWindow):

    def __init__(self, dpi=None):
        super().__init__()
        self.dpi = dpi
        self.init_parameters()
        self.init_main_window()
        self.init_choose_file_region()
        self.init_playback_control_region()
        self.init_music_function_region()
        self.init_message_region()
        self.init_synth_control_region()
        self.init_playlist_region()
        self.apply_synth_settings()
        self.show()
        try:
            self.choose_midi(current_midi_file='resources/demo.mid',
                             update_path=False)
            self.choose_soundfont(current_soundfont_file='resources/gm.sf2',
                                  update_path=False)
        except:
            pass

    def update_last_path(self, path):
        current_path = os.path.dirname(path)
        if current_path != self.last_path:
            with open('last_path.txt', 'w', encoding='utf-8') as f:
                f.write(current_path)
            self.last_path = current_path

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ingore()

    def dropEvent(self, event):
        current_path = [i.toLocalFile() for i in event.mimeData().urls()]
        self.drop_file_path = current_path
        if self.drop_file_path:
            current_file = self.drop_file_path[0]
            if os.path.isfile(current_file):
                extension = os.path.splitext(current_file)[1][1:]
                if extension.lower() == 'mid':
                    self.choose_midi(current_midi_file=current_file)
                elif extension.lower() in ['sf2', 'sf3', 'dls']:
                    self.choose_soundfont(current_soundfont_file=current_file)

    def init_parameters(self):
        self.current_midi_file = None
        self.current_soundfont_file = None
        self.current_midi_file_read = None
        self.current_midi_object = None
        self.paused = False
        self.already_load = False
        self.synth_volume = default_synth_volume
        self.current_sf2 = rs.sf2_player()
        self.current_second = 0
        self.bar_move_id = None
        self.change_bpm_id = None
        self.bpm_outer_change = False
        self.drop_file_path = []
        self.last_path = ''
        if os.path.exists('last_path.txt'):
            with open('last_path.txt', encoding='utf-8') as f:
                self.last_path = f.read()

    def init_main_window(self):
        self.setWindowTitle('SfPlayer')
        self.setMinimumSize(900, 520)
        self.setAcceptDrops(True)
        self.setStyleSheet('background-color: white;')
        self.notebook = QtWidgets.QTabWidget(self)
        self.notebook.move(0, 0)
        self.notebook.resize(900, 520)
        self.current_font = QtGui.QFont('Consolas', 10)
        self.notebook.setFont(set_font(self.current_font, self.dpi))
        self.playback_frame = QtWidgets.QFrame()
        self.synth_control_frame = QtWidgets.QFrame()
        self.music_function_frame = QtWidgets.QFrame()
        self.playlist_frame = QtWidgets.QFrame()
        self.notebook.addTab(self.playback_frame, 'Playback')
        self.notebook.addTab(self.synth_control_frame, 'Synth Settings')
        self.notebook.addTab(self.music_function_frame, 'Music Functions')
        self.notebook.addTab(self.playlist_frame, 'Playlist')

    def init_choose_file_region(self):
        self.choose_midi_button = Button(self.playback_frame,
                                         text='Choose MIDI File',
                                         color='light grey',
                                         function=self.choose_midi)
        self.choose_midi_button.place(x=50, y=50)
        self.choose_soundfont_button = Button(self.playback_frame,
                                              text='Choose SoundFont File',
                                              function=self.choose_soundfont,
                                              x=50,
                                              y=120)
        self.current_midi_label = Label(self.playback_frame, text='Not chosen')
        self.current_midi_label.place(x=220, y=52)
        self.current_soundfont_label = Label(self.playback_frame,
                                             text='Not chosen')
        self.current_soundfont_label.place(x=220, y=122)

    def init_playback_control_region(self):
        self.play_button = Button(self.playback_frame,
                                  text='Play',
                                  function=self.play_midi)
        self.play_button.place(x=50, y=300)
        self.pause_button = Button(self.playback_frame,
                                   text='Pause',
                                   function=self.pause_midi)
        self.pause_button.place(x=200, y=300)
        self.unpause_button = Button(self.playback_frame,
                                     text='Unpause',
                                     function=self.unpause_midi)
        self.unpause_button.place(x=350, y=300)
        self.stop_button = Button(self.playback_frame,
                                  text='Stop',
                                  function=self.stop_midi)
        self.stop_button.place(x=500, y=300)
        self.player_bar = Slider(parent=self.playback_frame,
                                 orientation=QtCore.Qt.Horizontal,
                                 width=600,
                                 range=[0, 1000],
                                 x=50,
                                 y=230,
                                 function=self.player_bar_click)
        self.player_bar_time = Label(self.playback_frame,
                                     text='00:00:00 / 00:00:00')
        self.player_bar_time.place(x=670, y=230)

    def init_music_function_region(self):
        self.detect_key_button = Button(self.music_function_frame,
                                        text='Detect Key',
                                        function=self.detect_key)
        self.detect_key_button.place(x=50, y=50)
        self.detect_key_label = Label(self.music_function_frame, text='')
        self.detect_key_label.place(x=160, y=50)

        self.channel_label = Label(self.music_function_frame, text='Channel')
        self.channel_label.place(x=500, y=20)
        self.instrument_label = Label(self.music_function_frame,
                                      text='Instrument')
        self.instrument_label.place(x=650, y=20)
        self.custom_play_listbox = QtWidgets.QListWidget(
            self.music_function_frame)
        self.instrument_listbox = QtWidgets.QListWidget(
            self.music_function_frame)
        self.instrument_listbox.setEnabled(False)
        for k in range(16):
            self.custom_play_listbox.insertItem(k, f'Channel {k+1}')
        self.custom_play_listbox.move(500, 50)
        self.custom_play_listbox.setFixedSize(120, 310)
        self.custom_play_listbox.clicked.connect(
            self.show_current_program_and_bank)
        self.whole_instruments = list(rs.mp.database.INSTRUMENTS.keys())
        self.whole_instruments_with_number = [
            f'{i+1}  {each}' for i, each in enumerate(self.whole_instruments)
        ]
        for i, j in rs.mp.database.drum_set_dict.items():
            self.whole_instruments_with_number[
                i - 1] = f'{self.whole_instruments_with_number[i-1]} / {j}'
        self.instrument_listbox.move(650, 50)
        self.instrument_listbox.setFixedSize(150, 310)
        self.program_box = QtWidgets.QComboBox(self.music_function_frame)
        self.program_box.setFixedWidth(250)
        self.program_box.setCurrentText(self.whole_instruments_with_number[0])
        self.program_box.addItems(self.whole_instruments_with_number)
        self.program_box.move(500, 380)
        self.bank_box = QtWidgets.QComboBox(self.music_function_frame)
        self.bank_box.setFixedWidth(100)
        self.bank_box.setCurrentText('0')
        self.bank_box.setFixedWidth(100)
        self.bank_box.addItems([str(i) for i in range(129)])
        self.bank_box.move(770, 380)
        self.program_label = Label(self.music_function_frame, text='Program')
        self.bank_label = Label(self.music_function_frame, text='Bank')
        self.program_label.place(x=500, y=410)
        self.bank_label.place(x=770, y=410)
        self.program_box.activated.connect(self.change_program)
        self.bank_box.activated.connect(self.change_bank)

        self.export_audio_button = Button(self.music_function_frame,
                                          text='Export As Audio',
                                          function=self.export_audio)
        self.export_audio_button.place(x=50, y=100)

        self.modulation_before_label = Label(self.music_function_frame,
                                             text='From Mode')
        self.modulation_before_label.place(x=50, y=250)
        self.modulation_before_entry = QtWidgets.QLineEdit(
            self.music_function_frame)
        self.modulation_before_entry.setFixedWidth(100)
        self.modulation_before_entry.move(150, 250)
        self.modulation_after_label = Label(self.music_function_frame,
                                            text='to Mode')
        self.modulation_after_label.place(x=280, y=250)
        self.modulation_after_entry = QtWidgets.QLineEdit(
            self.music_function_frame)
        self.modulation_after_entry.setFixedWidth(100)
        self.modulation_after_entry.move(350, 250)
        self.modulation_play_button = Button(self.music_function_frame,
                                             text='Play Modulation',
                                             function=self.play_modulation)
        self.modulation_play_button.place(x=50, y=300)
        self.play_reverse_button = Button(self.music_function_frame,
                                          text='Play Reverse',
                                          function=self.play_reverse)
        self.play_reverse_button.place(x=50, y=150)
        self.play_reverse_piano_key_button = Button(
            self.music_function_frame,
            text='Play Reverse Piano Key',
            function=self.play_reverse_piano_key)
        self.play_reverse_piano_key_button.place(x=50, y=200)

        self.play_negative_harmony_button = Button(
            self.music_function_frame,
            text='Play Negative Harmony',
            function=self.play_negative_harmony)
        self.play_negative_harmony_button.place(x=50, y=400)
        self.key_label = Label(self.music_function_frame, text='key')
        self.key_label.place(x=220, y=400)
        self.key_entry = QtWidgets.QLineEdit(self.music_function_frame)
        self.key_entry.setFixedWidth(100)
        self.key_entry.move(260, 400)
        self.shift_key_entry = QtWidgets.QLineEdit(self.music_function_frame)
        self.shift_key_entry.setFixedWidth(100)
        self.shift_key_entry.move(200, 350)
        self.shift_key_play_button = Button(self.music_function_frame,
                                            text='Play Shift Key',
                                            function=self.play_shift_key)
        self.shift_key_play_button.place(x=50, y=350)

    def init_message_region(self):
        self.msg = Label(self, text='Currently no actions', x=50, y=480)
        self.msg.setFixedWidth(800)

    def init_synth_control_region(self):
        self.init_volume_bar()
        self.init_bpm_bar()
        self.init_reverb_button()
        self.init_reverb_parameters_bar()
        self.init_chorus_button()
        self.init_chorus_parameters_bar()
        self.init_midi_cc_bar()
        self.init_pitch_bend_bar()

    def init_playlist_region(self):
        self.playlist_choose_path_button = Button(
            self.playlist_frame,
            text='Choose path',
            function=self.choose_playlist_path)
        self.playlist_choose_path_button.place(x=50, y=50)
        self.playlist_path_label = Label(self.playlist_frame,
                                         text='Not chosen')
        self.playlist_path_label.place(x=220, y=52)
        self.playlist_msg_label = Label(self.playlist_frame, text='')
        self.playlist_msg_label.place(x=50, y=100)
        self.playlist_play_random_files_button = Button(
            self.playlist_frame,
            text='Play a random MIDI file',
            function=self.playlist_play_random_file)
        self.playlist_play_random_files_button.place(x=50, y=150)
        self.playlist_current_file_label = Label(self.playlist_frame, text='')
        self.playlist_current_file_label.place(x=230, y=150)
        self.current_playlist_path = None
        self.playlist_files = []

    def init_volume_bar(self):
        self.current_volume_percentage = self.get_setting('gain') * 10
        self.volume_slider_label = Label(
            self.synth_control_frame,
            text=f'Volume  {self.current_volume_percentage}%')
        self.volume_slider_label.place(x=50, y=50)
        self.set_move_volume_bar = Slider(parent=self.synth_control_frame,
                                          orientation=QtCore.Qt.Horizontal,
                                          x=200,
                                          y=50,
                                          value=self.current_volume_percentage,
                                          function=self.change_move_volume_bar)

    def change_move_volume_bar(self, e):
        self.current_volume_percentage = e
        self.volume_slider_label.setText(f'Volume  {float(e)}%')
        self.volume_slider_label.adjustSize()
        self.change_setting('gain', self.current_volume_percentage / 10)
        self.synth_volume = self.current_volume_percentage / 10

    def init_bpm_bar(self):
        self.current_bpm = 120
        self.bpm_slider_label = Label(self.synth_control_frame,
                                      text=f'BPM  {self.current_bpm}')
        self.bpm_slider_label.place(x=50, y=100)
        self.set_move_bpm_bar = Slider(parent=self.synth_control_frame,
                                       range=[0, 1000],
                                       orientation=QtCore.Qt.Horizontal,
                                       width=200,
                                       value=self.current_bpm,
                                       function=self.change_move_bpm_bar)
        self.set_move_bpm_bar.place(x=200, y=100)

    def change_move_bpm_bar(self, e):
        self.current_bpm = e
        self.bpm_slider_label.setText(f'BPM  {self.current_bpm}')
        self.bpm_slider_label.adjustSize()
        if hasattr(self.current_sf2.synth, 'player'):
            if self.bpm_outer_change:
                self.bpm_outer_change = False
            else:
                self.current_sf2.set_tempo(self.current_bpm)

    def init_midi_cc_bar(self):
        self.midi_cc_list = [f'{i}  {j}' for i, j in midi_cc.items()]
        self.cc_box = QtWidgets.QComboBox(self.synth_control_frame)
        self.cc_box.setCurrentText(self.midi_cc_list[0])
        self.cc_box.setFixedWidth(170)
        self.cc_box.addItems(self.midi_cc_list)
        self.cc_box.move(680, 20)
        self.midi_channel_list = [i for i in range(16)]
        self.channel_box = QtWidgets.QComboBox(self.synth_control_frame)
        self.channel_box.setFixedWidth(100)
        self.channel_box.setCurrentText('0')
        self.channel_box.addItems([str(i) for i in self.midi_channel_list])
        self.channel_box.move(680, 50)
        self.midi_cc_label = Label(self.synth_control_frame, text='CC')
        self.midi_cc_label.place(x=860, y=20)
        self.midi_channel_label = Label(self.synth_control_frame,
                                        text='Channel')
        self.midi_channel_label.place(x=790, y=50)
        self.cc_box.activated.connect(self.show_current_cc)
        self.channel_box.activated.connect(self.show_current_channel_msg)

        current_cc = self.get_current_cc()
        self.midi_cc_slider_label = Label(self.synth_control_frame,
                                          text=f'MIDI CC  {current_cc}')
        self.midi_cc_slider_label.place(x=420, y=50)
        self.set_move_midi_cc_bar = Slider(
            parent=self.synth_control_frame,
            range=[0, 127],
            orientation=QtCore.Qt.Horizontal,
            width=150,
            value=current_cc,
            function=self.change_move_midi_cc_bar)
        self.set_move_midi_cc_bar.place(x=520, y=50)

    def get_current_cc(self):
        return self.current_sf2.synth.get_cc(
            int(self.channel_box.currentText()),
            self.midi_cc_list.index(self.cc_box.currentText()))

    def show_current_channel_msg(self, e):
        self.show_current_cc()
        self.show_current_pitch_bend()

    def show_current_cc(self, e=None):
        current_cc = self.get_current_cc()
        self.midi_cc_slider_label.setText(f'MIDI CC  {current_cc}')
        self.midi_cc_slider_label.adjustSize()
        self.set_move_midi_cc_bar.change(current_cc)

    def change_move_midi_cc_bar(self, e):
        current_midi_cc = int(e)
        self.midi_cc_slider_label.setText(f'MIDI CC  {current_midi_cc}')
        self.midi_cc_slider_label.adjustSize()
        self.current_sf2.synth.cc(
            int(self.channel_box.currentText()),
            self.midi_cc_list.index(self.cc_box.currentText()),
            current_midi_cc)

    def init_pitch_bend_bar(self):
        current_pitch_bend = self.get_current_pitch_bend()
        self.pitch_bend_slider_label = Label(
            self.synth_control_frame,
            text=f'Pitch Bend  {current_pitch_bend}%')
        self.pitch_bend_slider_label.place(x=420, y=100)
        self.set_move_pitch_bend_bar = Slider(
            self.synth_control_frame,
            range=[-100, 100],
            orientation=QtCore.Qt.Horizontal,
            width=250,
            value=current_pitch_bend,
            function=self.change_move_pitch_bend_bar)
        self.set_move_pitch_bend_bar.place(x=550, y=100)

    def get_current_pitch_bend(self):
        current_pitch_bend = self.current_sf2.synth.get_pitch_bend(
            int(self.channel_box.currentText()))
        current_pitch_bend = int(((current_pitch_bend - 8191) / 8191) * 100)
        return current_pitch_bend

    def show_current_pitch_bend(self):
        current_pitch_bend = self.get_current_pitch_bend()
        self.pitch_bend_slider_label.setText(
            f'Pitch Bend  {current_pitch_bend}%')
        self.set_move_pitch_bend_bar.change(current_pitch_bend)

    def change_move_pitch_bend_bar(self, e):
        current_pitch_bend = float(e)
        current_pitch_bend_value = round((current_pitch_bend / 100) * 8191)
        self.pitch_bend_slider_label.setText(
            f'Pitch Bend  {int(current_pitch_bend)}%')
        self.pitch_bend_slider_label.adjustSize()
        self.current_sf2.synth.pitch_bend(int(self.channel_box.currentText()),
                                          current_pitch_bend_value)

    def init_reverb_button(self):
        self.reverb_button = CheckBox(self.synth_control_frame,
                                      text='Reverb',
                                      value=0,
                                      function=self.change_reverb)
        self.reverb_button.place(x=50, y=150)

    def change_reverb(self):
        if self.reverb_button.isChecked():
            self.change_setting('reverb.active', 1)
        else:
            self.change_setting('reverb.active', 0)

    def init_reverb_parameters_bar(self):
        self.reverb_sliders_text = ['' for i in range(4)]
        self.reverb_parameters = ['damp', 'level', 'room-size', 'width']
        self.reverb_parameters_min_values = [0, 0, 0, 0]
        self.reverb_parameters_max_values = [1, 1, 1, 100]
        self.reverb_parameters_range_max = [100, 100, 100, 100]
        self.reverb_parameters_precision = [0.01, 0.01, 0.01, 0.5]
        self.reverb_parameters_digit = [
            len(str(i).split('.')[1]) if isinstance(i, float) else 0
            for i in self.reverb_parameters_precision
        ]
        self.current_reverb_values = [
            self.get_setting(f'reverb.{i}') for i in self.reverb_parameters
        ]
        for k, each in enumerate(self.reverb_sliders_text):
            digit = self.reverb_parameters_digit[k]
            self.reverb_sliders_text[
                k] = f'Reverb {self.reverb_parameters[k].capitalize()}  {self.current_reverb_values[k]:.{digit}f}'
        self.reverb_slider_labels = [
            Label(self.synth_control_frame, text=k)
            for k in self.reverb_sliders_text
        ]
        self.reverb_slider_labels[0].place(x=50, y=200)
        self.reverb_slider_labels[1].place(x=450, y=200)
        self.reverb_slider_labels[2].place(x=50, y=250)
        self.reverb_slider_labels[3].place(x=450, y=250)
        self.set_move_reverb_bars = [
            Slider(parent=self.synth_control_frame,
                   range=[
                       self.reverb_parameters_min_values[k] /
                       self.reverb_parameters_precision[k],
                       self.reverb_parameters_max_values[k] /
                       self.reverb_parameters_precision[k]
                   ],
                   orientation=QtCore.Qt.Horizontal,
                   width=200,
                   value=self.current_reverb_values[k] *
                   (self.reverb_parameters_range_max[k] /
                    self.reverb_parameters_max_values[k]),
                   function=lambda e, k=k: self.change_move_reverb_bar(e, k))
            for k in range(len(self.reverb_parameters))
        ]
        self.set_move_reverb_bars[0].place(x=220, y=200)
        self.set_move_reverb_bars[1].place(x=600, y=200)
        self.set_move_reverb_bars[2].place(x=220, y=250)
        self.set_move_reverb_bars[3].place(x=600, y=250)

    def change_move_reverb_bar(self, e, ind):
        digit = self.reverb_parameters_digit[ind]
        self.current_reverb_values[ind] = round(
            e * self.reverb_parameters_precision[ind], digit)
        self.reverb_slider_labels[ind].setText(
            f'Reverb {self.reverb_parameters[ind].capitalize()}  {self.current_reverb_values[ind]:.{digit}f}'
        )
        self.reverb_slider_labels[ind].adjustSize()
        self.change_setting(f'reverb.{self.reverb_parameters[ind]}',
                            self.current_reverb_values[ind])

    def init_chorus_button(self):
        self.chorus_button = CheckBox(parent=self.synth_control_frame,
                                      text='Chorus',
                                      value=0,
                                      function=self.change_chorus)
        self.chorus_button.place(x=50, y=300)

    def change_chorus(self):
        if self.chorus_button.isChecked():
            self.change_setting('chorus.active', 1)
        else:
            self.change_setting('chorus.active', 0)

    def init_chorus_parameters_bar(self):
        self.chorus_sliders_text = ['' for i in range(4)]
        self.chorus_parameters = ['depth', 'level', 'nr', 'speed']
        self.chorus_parameters_min_values = [0, 0, 0, 0.1]
        self.chorus_parameters_max_values = [256, 10, 99, 5]
        self.chorus_parameters_range_max = [256, 100, 99, 50]
        self.chorus_parameters_precision = [1.0, 0.1, 1, 0.1]
        self.current_chorus_values = [
            self.get_setting(f'chorus.{i}') for i in self.chorus_parameters
        ]
        self.chorus_parameters_digit = [
            len(str(i).split('.')[1]) if isinstance(i, float) else 0
            for i in self.chorus_parameters_precision
        ]
        for k, each in enumerate(self.chorus_sliders_text):
            digit = self.chorus_parameters_digit[k]
            self.chorus_sliders_text[
                k] = f'Chorus {self.chorus_parameters[k].capitalize()}  {self.current_chorus_values[k]:.{digit}f}'
        self.chorus_slider_labels = [
            Label(self.synth_control_frame, text=k)
            for k in self.chorus_sliders_text
        ]
        self.chorus_slider_labels[0].place(x=50, y=350)
        self.chorus_slider_labels[1].place(x=450, y=350)
        self.chorus_slider_labels[2].place(x=50, y=400)
        self.chorus_slider_labels[3].place(x=450, y=400)
        self.set_move_chorus_bars = [
            Slider(parent=self.synth_control_frame,
                   range=[
                       self.chorus_parameters_min_values[k] /
                       self.chorus_parameters_precision[k],
                       self.chorus_parameters_max_values[k] /
                       self.chorus_parameters_precision[k]
                   ],
                   orientation=QtCore.Qt.Horizontal,
                   width=200,
                   value=self.current_chorus_values[k] *
                   (self.chorus_parameters_range_max[k] /
                    self.chorus_parameters_max_values[k]),
                   function=lambda e, k=k: self.change_move_chorus_bar(e, k))
            for k in range(len(self.chorus_parameters))
        ]
        self.set_move_chorus_bars[0].place(x=200, y=350)
        self.set_move_chorus_bars[1].place(x=600, y=350)
        self.set_move_chorus_bars[2].place(x=200, y=400)
        self.set_move_chorus_bars[3].place(x=600, y=400)

    def change_move_chorus_bar(self, e, ind):
        digit = self.chorus_parameters_digit[ind]
        self.current_chorus_values[ind] = round(
            e * self.chorus_parameters_precision[ind], digit)
        self.chorus_slider_labels[ind].setText(
            f'Chorus {self.chorus_parameters[ind].capitalize()}  {self.current_chorus_values[ind]:.{digit}f}'
        )
        self.chorus_slider_labels[ind].adjustSize()
        self.change_setting(f'chorus.{self.chorus_parameters[ind]}',
                            self.current_chorus_values[ind])

    def apply_synth_settings(self):
        self.change_setting('cpu-cores', cpu_cores)
        self.change_setting('gain', self.synth_volume)
        self.change_setting('reverb.active',
                            int(self.reverb_button.isChecked()))
        for i, each in enumerate(self.reverb_parameters):
            self.change_setting(f'reverb.{each}',
                                self.current_reverb_values[i])
        self.change_setting('chorus.active',
                            int(self.chorus_button.isChecked()))
        for i, each in enumerate(self.chorus_parameters):
            self.change_setting(f'chorus.{each}',
                                self.current_chorus_values[i])

    def change_program(self, e):
        current_ind = self.custom_play_listbox.currentIndex().row()
        current_instrument = self.program_box.currentText()
        self.current_sf2.synth.program_change(
            current_ind,
            self.whole_instruments_with_number.index(current_instrument))

    def change_bank(self, e):
        current_ind = self.custom_play_listbox.currentIndex().row()
        current_bank = int(self.bank_box.currentText())
        self.current_sf2.synth.bank_select(current_ind, current_bank)
        current_instrument = self.program_box.currentText()
        self.current_sf2.synth.program_change(
            current_ind,
            self.whole_instruments_with_number.index(current_instrument))

    def show_current_program_and_bank(self, e):
        current_ind = self.custom_play_listbox.currentIndex().row()
        current_sfid, current_bank, current_program = self.current_sf2.synth.program_info(
            current_ind)
        if current_sfid != 0:
            self.program_box.setCurrentText(
                str(self.whole_instruments_with_number[current_program]))
            self.bank_box.setCurrentText(str(current_bank))

    def player_bar_move(self):
        if self.current_sf2.get_status() == 3:
            self.player_bar_reset()
            return
        self.current_second += 1
        if self.current_second >= self.current_midi_length:
            self.current_second = self.current_midi_length
            current_ratio = (self.current_second /
                             self.current_midi_length) * 1000
            self.player_bar.change(current_ratio)
            self.player_bar_set_time(self.current_second)
            self.player_bar_reset()
        else:
            current_ratio = (self.current_second /
                             self.current_midi_length) * 1000
            self.player_bar.change(current_ratio)
            self.player_bar_set_time(self.current_second)
            self.bar_move_id = Timer(1000, self.player_bar_move)

    def player_bar_set_time(self, time):
        self.player_bar_time.setText(
            f'{self.second_to_time_label(time)} / {self.total_length}')

    def player_bar_click(self, event):
        if self.bar_move_id:
            if self.current_sf2.get_status() == 3:
                self.player_bar_reset()
                return
            current_ratio = event / 1000
            if current_ratio > 1:
                current_ratio = 1
            elif current_ratio < 0:
                current_ratio = 0
            new_time = self.current_midi_length * current_ratio
            self.current_second = new_time
            self.player_bar.change(current_ratio * 1000)
            self.player_bar_set_time(self.current_second)
            new_ticks = int(
                mido.second2tick(self.current_second,
                                 self.current_midi_object.ticks_per_beat,
                                 self.current_sf2.get_current_tempo()))
            self.current_sf2.set_pos(new_ticks)

    def player_bar_reset(self):
        if self.current_sf2.get_status() != 3:
            self.bar_move_id = Timer(1000, self.player_bar_move)
            return
        self.bar_move_id = None
        self.player_bar.change(0)
        self.current_second = 0
        self.player_bar_set_time(self.current_second)

    def show_msg(self, text=''):
        self.msg.setText(text)
        self.msg.adjustSize()

    def choose_playlist_path(self):
        current_path = Dialog(caption='choose path',
                              directory=self.last_path,
                              filter='',
                              mode=1).directory
        if current_path:
            self.current_playlist_path = current_path
            self.playlist_path_label.configure(
                text=textwrap.fill(current_path, width=90))
            self.playlist_msg_label.configure(text='Searching MIDI files ...')
            self.update()
            self.playlist_files = self.get_all_midi_files(
                self.current_playlist_path)
            self.playlist_msg_label.configure(
                text=f'found {len(self.playlist_files)} MIDI files')

    def get_all_midi_files(self, path):
        result = []
        for each in os.listdir(path):
            current_path = os.path.join(path, each)
            if os.path.isfile(current_path):
                if os.path.splitext(each)[1].lower() == '.mid':
                    result.append(current_path)
            else:
                result.extend(self.get_all_midi_files(current_path))
        return result

    def playlist_play_random_file(self):
        if self.playlist_files:
            current_file = random.choice(self.playlist_files)
            self.playlist_current_file_label.configure(
                text=textwrap.fill(current_file, width=90))
            self.choose_midi(current_midi_file=current_file)
            self.play_midi()

    def choose_midi(self,
                    event=None,
                    current_midi_file=None,
                    update_path=True):
        if current_midi_file is None:
            current_midi_file = Dialog(
                caption="Choose MIDI File",
                directory=self.last_path,
                filter='MIDI files (*.mid);; All Files (*)').filename[0]
        if current_midi_file:
            self.current_midi_file = current_midi_file
            self.current_midi_file_read = None
            self.current_midi_label.setText(
                textwrap.fill(self.current_midi_file, width=90))
            self.current_midi_label.adjustSize()
            current_path = os.path.dirname(self.current_midi_file)
            self.already_load = False
            if update_path:
                self.update_last_path(self.current_midi_file)

    def second_to_time_label(self, second):
        current_hour = int(second / 3600)
        current_minute = int((second - 3600 * current_hour) / 60)
        current_second = int(
            (second - 3600 * current_hour - 60 * current_minute))
        result = f'{current_hour:02d}:{current_minute:02d}:{current_second:02d}'
        return result

    def choose_soundfont(self,
                         event=None,
                         current_soundfont_file=None,
                         update_path=True):
        if current_soundfont_file is None:
            current_soundfont_file = Dialog(
                caption="Choose SoundFont File",
                directory=self.last_path,
                filter='SoundFont files (*.sf2 *.sf3 *.dls);; All Files (*)'
            ).filename[0]
        if current_soundfont_file:
            try:
                self.current_sf2.load(current_soundfont_file)
                self.current_soundfont_file = current_soundfont_file
                self.current_soundfont_label.setText(
                    textwrap.fill(self.current_soundfont_file, width=90))
                self.current_soundfont_label.adjustSize()
                if update_path:
                    self.update_last_path(self.current_soundfont_file)
            except:
                self.show_msg('Invalid SoundFont file')

    def start_play(self, midi_file):
        try:
            if self.current_sf2.playing:
                self.current_sf2.stop()
            if load_sf2_mode == 1:
                self.current_sf2.synth.delete()
                self.current_sf2 = rs.sf2_player(self.current_soundfont_file)
                self.apply_synth_settings()
            self.current_sf2.play_midi_file(midi_file)
            self.init_after_play()
        except Exception as OSError:
            self.show_msg(
                'Error: The loaded SoundFont file does not contain all the required banks or presets of the MIDI file'
            )
            return
        self.show_msg(f'Start playing')

    def init_player_bar(self, midi_file):
        if (self.current_midi_object is None) or (not self.already_load):
            try:
                self.current_midi_object = mido.MidiFile(midi_file, clip=True)
            except IOError:
                current_riff_midi_file = rs.mp.riff_to_midi(midi_file)
                with open('riff.mid', 'wb') as f:
                    f.write(current_riff_midi_file.getbuffer())
                self.current_midi_file = 'riff.mid'
                self.current_midi_object = mido.MidiFile('riff.mid', clip=True)
            self.current_midi_length = self.current_midi_object.length
            self.total_length = self.second_to_time_label(
                self.current_midi_length)
            self.already_load = True
        if self.bar_move_id:
            self.bar_move_id.stop()
            self.change_bpm_id.stop()
            self.change_instrument_id.stop()
        self.player_bar.change(0)
        self.current_second = 0
        self.player_bar_set_time(0)
        self.bar_move_id = Timer(1000, self.player_bar_move)

    def init_after_play(self):
        self.update_bpm()
        self.update_instrument()

    def update_bpm(self):
        self.current_bpm = self.current_sf2.get_current_bpm()
        self.bpm_slider_label.setText(f'BPM  {self.current_bpm}')
        self.bpm_outer_change = True
        self.set_move_bpm_bar.setValue(self.current_bpm)
        self.change_bpm_id = Timer(100, self.update_bpm)

    def update_instrument(self):
        self.instrument_listbox.setEnabled(True)
        self.instrument_listbox.clear()
        for k in range(16):
            if self.current_sf2.synth.program_info(k)[0] != 0:
                current_instrument = self.current_sf2.synth.channel_info(k)[3]
                if not current_instrument:
                    current_instrument = 'None'
            else:
                current_instrument = 'None'
            self.instrument_listbox.insertItem(k, current_instrument)
        self.instrument_listbox.setEnabled(True)
        self.change_instrument_id = Timer(100, self.update_instrument)

    def play_midi(self):
        if self.current_midi_file and self.current_soundfont_file:
            if self.current_sf2.playing:
                self.current_sf2.stop()
            self.paused = False
            self.init_player_bar(self.current_midi_file)
            self.start_play(self.current_midi_file)

    def pause_midi(self):
        if not self.paused:
            if self.current_sf2.playing:
                self.paused = True
                self.show_msg(f'Pause playing')
                self.current_sf2.pause()
            if self.bar_move_id:
                self.bar_move_id.stop()
                self.change_bpm_id.stop()
                self.change_instrument_id.stop()
                self.bar_move_id = None

    def unpause_midi(self):
        if self.paused:
            self.paused = False
            self.show_msg(f'Continue playing')
            self.current_sf2.unpause()
            self.bar_move_id = Timer(1000, self.player_bar_move)

    def stop_midi(self):
        if self.current_sf2.playing:
            self.paused = False
            self.show_msg(f'Stop playing')
            self.current_sf2.stop()
        if self.bar_move_id:
            self.bar_move_id.stop()
            self.change_bpm_id.stop()
            self.change_instrument_id.stop()
        self.bar_move_id = None
        self.player_bar.change(0)
        self.current_second = 0
        self.player_bar_set_time(self.current_second)

    def export_audio(self):
        file_name = Dialog(caption="Export as audio",
                           directory=self.last_path,
                           filter='All files (*)',
                           default_filename='Untitled.wav',
                           mode=2).filename[0]
        if not file_name:
            return
        self.show_msg(f'Start exporting {file_name}')
        self.msg.repaint()
        if self.current_soundfont_file:
            current_sf2 = rs.sf2_loader(self.current_soundfont_file)
        else:
            self.show_msg('Please choose a SoundFont file')
            return
        try:
            current_sf2.export_midi_file(
                self.current_midi_file,
                name=file_name,
                format=os.path.splitext(file_name)[1][1:])
        except Exception as OSError:
            self.show_msg(
                'Error: The loaded SoundFont file does not contain all the required banks or presets of the MIDI file'
            )
            return
        self.show_msg(f'Finish exporting {file_name}')

    def play_modulation(self):
        if self.current_midi_file and self.current_soundfont_file:
            try:
                before_mode = rs.mp.S(self.modulation_before_entry.text())
                after_mode = rs.mp.S(self.modulation_after_entry.text())
            except:
                self.show_msg('Error: Invalid mode')
                return
            try:
                modulation_piece = rs.mp.read(
                    self.current_midi_file).modulation(before_mode, after_mode)
            except:
                self.show_msg('Invalid modulation')
                return
            rs.mp.write(modulation_piece, name='modulation.mid')
            self.already_load = False
            self.init_player_bar('modulation.mid')
            self.start_play('modulation.mid')
            self.already_load = False

    def play_negative_harmony(self):
        current_key = self.key_entry.text()
        try:
            current_piece = rs.mp.read(self.current_midi_file)
            for i in range(len(current_piece.tracks)):
                if current_piece.channels and current_piece.channels[i] == 9:
                    continue
                if len(current_piece.tracks[i]) == 0:
                    continue
                current_piece.tracks[i] = rs.mp.alg.negative_harmony(
                    rs.mp.scale(current_key, 'major'), current_piece.tracks[i])
            current_name = f'{os.path.splitext(os.path.split(self.current_midi_file)[1])[0]}_negative_harmony.mid'
            rs.mp.write(current_piece, name=current_name)
            self.already_load = False
            self.init_player_bar(current_name)
            self.start_play(current_name)
            self.already_load = False
        except:
            pass

    def detect_key(self):
        if not self.current_midi_file_read:
            self.current_midi_file_read = rs.mp.read(self.current_midi_file)
        current_key = rs.mp.alg.detect_scale(
            self.current_midi_file_read.quick_merge(), most_appear_num=3)
        current_key = textwrap.fill(current_key, width=40)
        self.detect_key_label.configure(text=current_key)

    def play_reverse(self):
        if not self.current_midi_file_read:
            self.current_midi_file_read = rs.mp.read(self.current_midi_file)
        rs.mp.write(self.current_midi_file_read.reverse(), name='temp.mid')
        self.already_load = False
        self.init_player_bar('temp.mid')
        self.start_play('temp.mid')
        self.already_load = False

    def play_reverse_piano_key(self):
        if not self.current_midi_file_read:
            self.current_midi_file_read = rs.mp.read(self.current_midi_file)
        rs.mp.write(reverse_piano_keys(self.current_midi_file_read),
                    name='temp.mid')
        self.already_load = False
        self.init_player_bar('temp.mid')
        self.start_play('temp.mid')
        self.already_load = False

    def play_shift_key(self):
        current_shift = self.shift_key_entry.text()
        if current_shift:
            try:
                current_shift = int(current_shift)
            except:
                self.show_msg(f'Error: shift key number must be an integer')
                return
            if not self.current_midi_file_read:
                self.current_midi_file_read = rs.mp.read(
                    self.current_midi_file)
            try:
                shift_key_file = self.current_midi_file_read + current_shift
                rs.mp.write(shift_key_file, name='temp.mid')
            except:
                return
            self.already_load = False
            self.init_player_bar('temp.mid')
            self.start_play('temp.mid')
            self.already_load = False

    def get_setting(self, parameter):
        return self.current_sf2.synth.get_setting(f'synth.{parameter}')

    def change_setting(self, parameter, value):
        self.current_sf2.synth.setting(f'synth.{parameter}', value)


def reverse_piano_keys(obj):
    temp = rs.mp.copy(obj)
    for k in temp.tracks:
        for i, each in enumerate(k.notes):
            if type(each) == rs.mp.note:
                reverse_note = rs.mp.degree_to_note(87 - (each.degree - 21) +
                                                    21)
                reverse_note.channel = each.channel
                reverse_note.duration = each.duration
                reverse_note.volume = each.volume
                k.notes[i] = reverse_note
    return temp


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    dpi = (app.screens()[0]).logicalDotsPerInch()
    root = Root(dpi=dpi)
    app.exec()
