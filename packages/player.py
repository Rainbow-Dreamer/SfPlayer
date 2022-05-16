import textwrap

with open('packages/config.py', encoding='utf-8') as f:
    exec(f.read())


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


class Root(TkinterDnD.Tk):

    def __init__(self):
        super(Root, self).__init__()
        self.init_parameters()
        self.init_main_window()
        self.init_choose_file_region()
        self.init_playback_control_region()
        self.init_music_function_region()
        self.init_message_region()
        self.init_synth_control_region()
        try:
            self.choose_midi('resources/demo.mid')
            self.choose_soundfont('resources/gm.sf2')
        except:
            pass

    def init_parameters(self):
        self.current_midi_file = None
        self.current_soundfont_file = None
        self.current_midi_file_read = None
        self.current_midi_object = None
        self.paused = False
        self.already_load = False
        self.current_path = '.'
        self.synth_volume = default_synth_volume
        self.current_sf2 = rs.sf2_player()
        self.change_setting('gain', self.synth_volume)
        self.change_setting('cpu-cores', cpu_cores)
        self.current_second = 0
        self.bar_move_id = None
        self.change_bpm_id = None
        self.bpm_outer_change = False

    def init_main_window(self):
        self.minsize(900, 520)
        self.title('SfPlayer')
        self.configure(bg='white')

        style = ttk.Style()
        style.configure('TLabel', background='white')
        style.configure('TCheckbutton', background='white')
        style.configure('TScale', background='white')
        style.configure('TFrame', background='white')
        style.configure('Custom.TNotebook.Tab', padding=[20, 4])

        self.notebook = ttk.Notebook(self,
                                     height=520,
                                     width=900,
                                     style='Custom.TNotebook')
        self.notebook.place(x=0, y=0)

        self.playback_frame = ttk.Frame(self, height=520, width=900)
        self.playback_frame.place(x=0, y=0)

        self.music_function_frame = ttk.Frame(self, height=520, width=900)
        self.music_function_frame.place(x=0, y=0)

        self.synth_control_frame = ttk.Frame(self, height=520, width=900)
        self.synth_control_frame.place(x=0, y=0)

        self.playback_frame.drop_target_register(DND_FILES)
        self.playback_frame.dnd_bind('<<Drop>>', self.drag_files)

        self.notebook.add(self.playback_frame, text='Playback')
        self.notebook.add(self.synth_control_frame, text='Synth Settings')
        self.notebook.add(self.music_function_frame, text='Music Functions')

    def init_choose_file_region(self):
        self.choose_midi_button = ttk.Button(self.playback_frame,
                                             text='Choose MIDI File',
                                             command=self.choose_midi)
        self.choose_midi_button.place(x=50, y=50)
        self.choose_soundfont_button = ttk.Button(
            self.playback_frame,
            text='Choose SoundFont File',
            command=self.choose_soundfont)
        self.choose_soundfont_button.place(x=50, y=120)
        self.current_midi_label = ttk.Label(self.playback_frame,
                                            text='Not chosen')
        self.current_soundfont_label = ttk.Label(self.playback_frame,
                                                 text='Not chosen')
        self.current_midi_label.place(x=220, y=52)
        self.current_soundfont_label.place(x=220, y=122)

    def init_playback_control_region(self):
        self.play_button = ttk.Button(self.playback_frame,
                                      text='Play',
                                      command=self.play_midi)
        self.play_button.place(x=50, y=300)
        self.pause_button = ttk.Button(self.playback_frame,
                                       text='Pause',
                                       command=self.pause_midi)
        self.pause_button.place(x=200, y=300)
        self.unpause_button = ttk.Button(self.playback_frame,
                                         text='Unpause',
                                         command=self.unpause_midi)
        self.unpause_button.place(x=350, y=300)
        self.stop_button = ttk.Button(self.playback_frame,
                                      text='Stop',
                                      command=self.stop_midi)
        self.stop_button.place(x=500, y=300)
        self.player_bar = ttk.Progressbar(self.playback_frame,
                                          orient=HORIZONTAL,
                                          length=600,
                                          mode='determinate')
        self.player_bar.place(x=50, y=230)

        self.player_bar_time = ttk.Label(self.playback_frame,
                                         text='00:00:00 / 00:00:00')
        self.player_bar_time.place(x=670, y=230)
        self.player_bar.bind('<Button-1>', self.player_bar_click)
        self.player_bar.bind('<B1-Motion>', self.player_bar_click)

        self.split_channels = IntVar()
        self.split_channels.set(0)
        self.split_channels_button = ttk.Checkbutton(
            self.playback_frame,
            text='Split Channels',
            variable=self.split_channels,
            takefocus=False)
        self.split_channels_button.place(x=50, y=370)

    def init_music_function_region(self):
        self.detect_key_button = ttk.Button(self.music_function_frame,
                                            text='Detect Key',
                                            command=self.detect_key)
        self.detect_key_button.place(x=50, y=50)
        self.detect_key_label = ttk.Label(self.music_function_frame, text='')
        self.detect_key_label.place(x=160, y=50)

        self.channel_label = ttk.Label(self.music_function_frame,
                                       text='Channel')
        self.channel_label.place(x=500, y=20)
        self.instrument_label = ttk.Label(self.music_function_frame,
                                          text='Instrument')
        self.instrument_label.place(x=630, y=20)
        self.custom_play_listbox = Listbox(self.music_function_frame,
                                           exportselection=False,
                                           activestyle='none')
        self.instrument_listbox = Listbox(self.music_function_frame,
                                          exportselection=False,
                                          activestyle='none',
                                          state=DISABLED,
                                          disabledforeground='black')
        for k in range(16):
            self.custom_play_listbox.insert(END, f'Channel {k+1}')
        self.custom_play_listbox.place(x=500, y=50, width=100, height=300)
        self.custom_play_listbox.bind('<<ListboxSelect>>',
                                      self.show_current_program_and_bank)
        self.whole_instruments = list(rs.mp.instruments.keys())
        self.whole_instruments_with_number = [
            f'{i+1}  {each}' for i, each in enumerate(self.whole_instruments)
        ]
        for i, j in rs.mp.drum_set_dict.items():
            self.whole_instruments_with_number[
                i - 1] = f'{self.whole_instruments_with_number[i-1]} / {j}'
        self.instrument_listbox.place(x=630, y=50, width=150, height=300)
        self.program_text = StringVar()
        self.program_text.set(self.whole_instruments_with_number[0])
        self.program_box = ttk.Combobox(
            self.music_function_frame,
            width=30,
            textvariable=self.program_text,
            values=self.whole_instruments_with_number)
        self.program_box.place(x=500, y=370)
        self.bank_text = IntVar()
        self.bank_text.set(0)
        self.bank_box = ttk.Combobox(self.music_function_frame,
                                     width=10,
                                     textvariable=self.bank_text,
                                     values=[i for i in range(129)])
        self.bank_box.place(x=750, y=370)
        self.program_label = ttk.Label(self.music_function_frame,
                                       text='Program')
        self.bank_label = ttk.Label(self.music_function_frame, text='Bank')
        self.program_label.place(x=500, y=400)
        self.bank_label.place(x=750, y=400)
        self.program_box.bind('<<ComboboxSelected>>', self.change_program)
        self.bank_box.bind('<<ComboboxSelected>>', self.change_bank)

        self.export_audio_button = ttk.Button(self.music_function_frame,
                                              text='Export As Audio',
                                              command=self.export_audio)
        self.export_audio_button.place(x=50, y=100)

        self.modulation_before_label = ttk.Label(self.music_function_frame,
                                                 text='From Mode')
        self.modulation_before_label.place(x=50, y=250)
        self.modulation_before_entry = ttk.Entry(self.music_function_frame,
                                                 width=20)
        self.modulation_before_entry.place(x=150, y=250)
        self.modulation_after_label = ttk.Label(self.music_function_frame,
                                                text='to Mode')
        self.modulation_after_label.place(x=50, y=300)
        self.modulation_after_entry = ttk.Entry(self.music_function_frame,
                                                width=20)
        self.modulation_after_entry.place(x=150, y=300)
        self.modulation_play_button = ttk.Button(self.music_function_frame,
                                                 text='Play Modulation',
                                                 command=self.play_modulation)
        self.modulation_play_button.place(x=50, y=350)
        self.play_reverse_button = ttk.Button(self.music_function_frame,
                                              text='Play Reverse',
                                              command=self.play_reverse)
        self.play_reverse_button.place(x=50, y=150)
        self.play_reverse_piano_key_button = ttk.Button(
            self.music_function_frame,
            text='Play Reverse Piano Key',
            command=self.play_reverse_piano_key)
        self.play_reverse_piano_key_button.place(x=50, y=200)

    def init_message_region(self):
        self.msg = ttk.Label(self, text='Currently no actions')
        self.msg.place(x=50, y=480)

    def init_synth_control_region(self):
        self.init_volume_bar()
        self.init_bpm_bar()
        self.init_reverb_button()
        self.init_reverb_parameters_bar()
        self.init_chorus_button()
        self.init_chorus_parameters_bar()
        self.init_midi_cc_bar()
        self.init_pitch_bend_bar()

    def init_volume_bar(self):
        self.volume_slider = StringVar()
        self.current_volume_percentage = self.get_setting('gain') * 10
        self.volume_slider.set(f'Volume  {self.current_volume_percentage}%')
        self.volume_slider_label = ttk.Label(self.synth_control_frame,
                                             textvariable=self.volume_slider)
        self.volume_slider_label.place(x=50, y=50)
        self.set_move_volume_bar = ttk.Scale(
            self.synth_control_frame,
            from_=0,
            to=100,
            orient=HORIZONTAL,
            length=200,
            value=self.current_volume_percentage,
            command=lambda e: self.change_move_volume_bar(e),
            takefocus=False)
        self.set_move_volume_bar.place(x=200, y=50)

    def change_move_volume_bar(self, e):
        self.current_volume_percentage = round(float(e) * 2) / 2
        self.volume_slider.set(f'Volume  {self.current_volume_percentage}%')
        self.change_setting('gain', self.current_volume_percentage / 10)
        self.synth_volume = self.current_volume_percentage / 10

    def init_bpm_bar(self):
        self.bpm_slider = StringVar()
        self.current_bpm = 120
        self.bpm_slider.set(f'BPM  {self.current_bpm}')
        self.bpm_slider_label = ttk.Label(self.synth_control_frame,
                                          textvariable=self.bpm_slider)
        self.bpm_slider_label.place(x=50, y=100)
        self.set_move_bpm_bar = ttk.Scale(
            self.synth_control_frame,
            from_=0,
            to=1000,
            orient=HORIZONTAL,
            length=200,
            value=self.current_bpm,
            command=lambda e: self.change_move_bpm_bar(e),
            takefocus=False)
        self.set_move_bpm_bar.place(x=200, y=100)

    def change_move_bpm_bar(self, e):
        self.current_bpm = int(float(e))
        self.bpm_slider.set(f'BPM  {self.current_bpm}')
        if hasattr(self.current_sf2.synth, 'player'):
            if self.bpm_outer_change:
                self.bpm_outer_change = False
            else:
                self.current_sf2.set_tempo(self.current_bpm)

    def init_midi_cc_bar(self):
        self.midi_cc_list = [f'{i}  {j}' for i, j in midi_cc.items()]
        self.midi_cc_text = StringVar()
        self.midi_cc_text.set(self.midi_cc_list[0])
        self.cc_box = ttk.Combobox(self.synth_control_frame,
                                   width=20,
                                   textvariable=self.midi_cc_text,
                                   values=self.midi_cc_list,
                                   takefocus=False)
        self.cc_box.place(x=670, y=20)
        self.midi_channel_list = [i for i in range(16)]
        self.midi_channel_text = IntVar()
        self.midi_channel_text.set(0)
        self.channel_box = ttk.Combobox(self.synth_control_frame,
                                        width=10,
                                        textvariable=self.midi_channel_text,
                                        values=self.midi_channel_list,
                                        takefocus=False)
        self.channel_box.place(x=670, y=50)
        self.midi_cc_label = ttk.Label(self.synth_control_frame, text='CC')
        self.midi_cc_label.place(x=850, y=20)
        self.midi_channel_label = ttk.Label(self.synth_control_frame,
                                            text='Channel')
        self.midi_channel_label.place(x=780, y=50)
        self.cc_box.bind('<<ComboboxSelected>>', self.show_current_cc)
        self.channel_box.bind('<<ComboboxSelected>>',
                              self.show_current_channel_msg)

        self.midi_cc_slider = StringVar()
        current_cc = self.get_current_cc()
        self.midi_cc_slider.set(f'MIDI CC  {current_cc}')
        self.midi_cc_slider_label = ttk.Label(self.synth_control_frame,
                                              textvariable=self.midi_cc_slider)
        self.midi_cc_slider_label.place(x=420, y=50)
        self.set_move_midi_cc_bar = ttk.Scale(
            self.synth_control_frame,
            from_=0,
            to=127,
            orient=HORIZONTAL,
            length=150,
            value=current_cc,
            command=lambda e: self.change_move_midi_cc_bar(e),
            takefocus=False)
        self.set_move_midi_cc_bar.place(x=510, y=50)

    def get_current_cc(self):
        return self.current_sf2.synth.get_cc(
            self.midi_channel_text.get(),
            self.midi_cc_list.index(self.midi_cc_text.get()))

    def show_current_channel_msg(self, e):
        self.show_current_cc()
        self.show_current_pitch_bend()

    def show_current_cc(self, e=None):
        current_cc = self.get_current_cc()
        self.midi_cc_slider.set(f'MIDI CC  {current_cc}')
        self.set_move_midi_cc_bar.set(current_cc)

    def change_move_midi_cc_bar(self, e):
        current_midi_cc = int(float(e))
        self.midi_cc_slider.set(f'MIDI CC  {current_midi_cc}')
        self.current_sf2.synth.cc(
            self.midi_channel_text.get(),
            self.midi_cc_list.index(self.midi_cc_text.get()), current_midi_cc)

    def init_pitch_bend_bar(self):
        self.pitch_bend_slider = StringVar()
        current_pitch_bend = self.get_current_pitch_bend()
        self.pitch_bend_slider.set(f'Pitch Bend  {current_pitch_bend}%')
        self.pitch_bend_slider_label = ttk.Label(
            self.synth_control_frame, textvariable=self.pitch_bend_slider)
        self.pitch_bend_slider_label.place(x=420, y=100)
        self.set_move_pitch_bend_bar = ttk.Scale(
            self.synth_control_frame,
            from_=-100,
            to=100,
            orient=HORIZONTAL,
            length=250,
            value=current_pitch_bend,
            command=lambda e: self.change_move_pitch_bend_bar(e),
            takefocus=False)
        self.set_move_pitch_bend_bar.place(x=550, y=100)

    def get_current_pitch_bend(self):
        current_pitch_bend = self.current_sf2.synth.get_pitch_bend(
            self.midi_channel_text.get())
        current_pitch_bend = int(((current_pitch_bend - 8191) / 8191) * 100)
        return current_pitch_bend

    def show_current_pitch_bend(self):
        current_pitch_bend = self.get_current_pitch_bend()
        self.pitch_bend_slider.set(f'Pitch Bend  {current_pitch_bend}%')
        self.set_move_pitch_bend_bar['value'] = current_pitch_bend

    def change_move_pitch_bend_bar(self, e):
        current_pitch_bend = float(e)
        current_pitch_bend_value = round((current_pitch_bend / 100) * 8191)
        self.pitch_bend_slider.set(f'Pitch Bend  {int(current_pitch_bend)}%')
        self.current_sf2.synth.pitch_bend(self.midi_channel_text.get(),
                                          current_pitch_bend_value)

    def init_reverb_button(self):
        self.has_reverb = IntVar()
        self.has_reverb.set(0)
        self.reverb_button = ttk.Checkbutton(self.synth_control_frame,
                                             text='Reverb',
                                             variable=self.has_reverb,
                                             command=self.change_reverb,
                                             takefocus=False)
        self.reverb_button.place(x=50, y=150)

    def change_reverb(self):
        if self.has_reverb.get():
            self.change_setting('reverb.active', 1)
        else:
            self.change_setting('reverb.active', 0)

    def init_reverb_parameters_bar(self):
        self.reverb_sliders = [StringVar() for i in range(4)]
        self.reverb_parameters = ['damp', 'level', 'room-size', 'width']
        self.reverb_parameter_int = []
        self.reverb_parameters_min_values = [0, 0, 0, 0]
        self.reverb_parameters_max_values = [1, 1, 1, 100]
        self.current_reverb_values = [
            self.get_setting(f'reverb.{i}') for i in self.reverb_parameters
        ]
        for k, each in enumerate(self.reverb_sliders):
            current_ratio = 100 / self.reverb_parameters_max_values[k]
            if current_ratio == 1:
                digit = 1
            else:
                digit = 2
            if self.reverb_parameters[k] in self.reverb_parameter_int:
                digit = 0
            each.set(
                f'Reverb {self.reverb_parameters[k].capitalize()}  {self.current_reverb_values[k]:.{digit}f}'
            )
        self.reverb_slider_labels = [
            ttk.Label(self.synth_control_frame, textvariable=k)
            for k in self.reverb_sliders
        ]
        self.reverb_slider_labels[0].place(x=50, y=200)
        self.reverb_slider_labels[1].place(x=450, y=200)
        self.reverb_slider_labels[2].place(x=50, y=250)
        self.reverb_slider_labels[3].place(x=450, y=250)
        self.set_move_reverb_bars = [
            ttk.Scale(self.synth_control_frame,
                      from_=self.reverb_parameters_min_values[k] *
                      (100 / self.reverb_parameters_max_values[k]),
                      to=100,
                      orient=HORIZONTAL,
                      length=200,
                      value=self.current_reverb_values[k] *
                      (100 / self.reverb_parameters_max_values[k]),
                      command=lambda e, k=k: self.change_move_reverb_bar(e, k),
                      takefocus=False)
            for k in range(len(self.reverb_parameters))
        ]
        self.set_move_reverb_bars[0].place(x=200, y=200)
        self.set_move_reverb_bars[1].place(x=600, y=200)
        self.set_move_reverb_bars[2].place(x=200, y=250)
        self.set_move_reverb_bars[3].place(x=600, y=250)

    def change_move_reverb_bar(self, e, ind):
        current_ratio = 100 / self.reverb_parameters_max_values[ind]
        if current_ratio == 1:
            digit = 1
        else:
            digit = 2
        if self.reverb_parameters[ind] in self.reverb_parameter_int:
            self.current_reverb_values[ind] = int(float(e) / current_ratio)
            digit = 0
        else:
            self.current_reverb_values[ind] = round(
                (round(float(e) * 2) / 2) / current_ratio, digit)
        self.reverb_sliders[ind].set(
            f'Reverb {self.reverb_parameters[ind].capitalize()}  {self.current_reverb_values[ind]:.{digit}f}'
        )
        self.change_setting(f'reverb.{self.reverb_parameters[ind]}',
                            self.current_reverb_values[ind])

    def init_chorus_button(self):
        self.has_chorus = IntVar()
        self.has_chorus.set(0)
        self.chorus_button = ttk.Checkbutton(self.synth_control_frame,
                                             text='Chorus',
                                             variable=self.has_chorus,
                                             command=self.change_chorus,
                                             takefocus=False)
        self.chorus_button.place(x=50, y=300)

    def change_chorus(self):
        if self.has_chorus.get():
            self.change_setting('chorus.active', 1)
        else:
            self.change_setting('chorus.active', 0)

    def init_chorus_parameters_bar(self):
        self.chorus_sliders = [StringVar() for i in range(4)]
        self.chorus_parameters = ['depth', 'level', 'nr', 'speed']
        self.chorus_parameter_int = ['nr']
        self.chorus_parameters_min_values = [0, 0, 0, 0.1]
        self.chorus_parameters_max_values = [256, 10, 99, 5]
        self.current_chorus_values = [
            self.get_setting(f'chorus.{i}') for i in self.chorus_parameters
        ]
        for k, each in enumerate(self.chorus_sliders):
            current_ratio = 100 / self.chorus_parameters_max_values[k]
            if current_ratio == 1:
                digit = 1
            else:
                digit = 2
            if self.chorus_parameters[k] in self.chorus_parameter_int:
                digit = 0
            each.set(
                f'Chorus {self.chorus_parameters[k].capitalize()}  {self.current_chorus_values[k]:.{digit}f}'
            )
        self.chorus_slider_labels = [
            ttk.Label(self.synth_control_frame, textvariable=k)
            for k in self.chorus_sliders
        ]
        self.chorus_slider_labels[0].place(x=50, y=350)
        self.chorus_slider_labels[1].place(x=450, y=350)
        self.chorus_slider_labels[2].place(x=50, y=400)
        self.chorus_slider_labels[3].place(x=450, y=400)
        self.set_move_chorus_bars = [
            ttk.Scale(self.synth_control_frame,
                      from_=self.chorus_parameters_min_values[k] *
                      (100 / self.chorus_parameters_max_values[k]),
                      to=100,
                      orient=HORIZONTAL,
                      length=200,
                      value=self.current_chorus_values[k] *
                      (100 / self.chorus_parameters_max_values[k]),
                      command=lambda e, k=k: self.change_move_chorus_bar(e, k),
                      takefocus=False)
            for k in range(len(self.chorus_parameters))
        ]
        self.set_move_chorus_bars[0].place(x=200, y=350)
        self.set_move_chorus_bars[1].place(x=600, y=350)
        self.set_move_chorus_bars[2].place(x=200, y=400)
        self.set_move_chorus_bars[3].place(x=600, y=400)

    def change_move_chorus_bar(self, e, ind):
        current_ratio = 100 / self.chorus_parameters_max_values[ind]
        if current_ratio == 1:
            digit = 1
        else:
            digit = 2
        if self.chorus_parameters[ind] in self.chorus_parameter_int:
            self.current_chorus_values[ind] = int(float(e) / current_ratio)
            digit = 0
        else:
            self.current_chorus_values[ind] = round(
                (round(float(e) * 2) / 2) / current_ratio, digit)

        self.chorus_sliders[ind].set(
            f'Chorus {self.chorus_parameters[ind].capitalize()}  {self.current_chorus_values[ind]:.{digit}f}'
        )
        self.change_setting(f'chorus.{self.chorus_parameters[ind]}',
                            self.current_chorus_values[ind])

    def apply_synth_settings(self):
        self.change_setting('gain', self.synth_volume)
        self.change_setting('reverb.active', self.has_reverb.get())
        for i, each in enumerate(self.reverb_parameters):
            self.change_setting(f'reverb.{each}',
                                self.current_reverb_values[i])
        self.change_setting('chorus.active', self.has_chorus.get())
        for i, each in enumerate(self.chorus_parameters):
            self.change_setting(f'chorus.{each}',
                                self.current_chorus_values[i])

    def change_program(self, e):
        current_ind = self.custom_play_listbox.index(ANCHOR)
        current_instrument = self.program_text.get()
        self.current_sf2.synth.program_change(
            current_ind,
            self.whole_instruments_with_number.index(current_instrument))

    def change_bank(self, e):
        current_ind = self.custom_play_listbox.index(ANCHOR)
        current_bank = self.bank_text.get()
        self.current_sf2.synth.bank_select(current_ind, current_bank)
        current_instrument = self.program_text.get()
        self.current_sf2.synth.program_change(
            current_ind,
            self.whole_instruments_with_number.index(current_instrument))

    def show_current_program_and_bank(self, e):
        current_ind = self.custom_play_listbox.index(ANCHOR)
        current_sfid, current_bank, current_program = self.current_sf2.synth.program_info(
            current_ind)
        if current_sfid != 0:
            self.program_box.set(
                self.whole_instruments_with_number[current_program])
            self.bank_box.set(current_bank)

    def drag_files(self, e):
        if not (e.data[0] == '{' and e.data[-1] == '}'):
            current_file = e.data
        else:
            current_file = e.data[1:-1]
        if os.path.isfile(current_file):
            extension = os.path.splitext(current_file)[1][1:]
            if extension.lower() == 'mid':
                self.choose_midi(current_file)
            elif extension.lower() in ['sf2', 'sf3', 'dls']:
                self.choose_soundfont(current_file)

    def player_bar_move(self):
        if self.current_sf2.get_status() == 3:
            self.player_bar_reset()
            return
        self.current_second += 1
        if self.current_second >= self.current_midi_length:
            self.current_second = self.current_midi_length
            current_ratio = (self.current_second /
                             self.current_midi_length) * 100
            self.player_bar['value'] = current_ratio
            self.player_bar_set_time(self.current_second)
            self.after(1000, self.player_bar_reset)
        else:
            current_ratio = (self.current_second /
                             self.current_midi_length) * 100
            self.player_bar['value'] = current_ratio
            self.player_bar_set_time(self.current_second)
            self.bar_move_id = self.after(1000, self.player_bar_move)

    def player_bar_set_time(self, time):
        self.player_bar_time.configure(
            text=f'{self.second_to_time_label(time)} / {self.total_length}')

    def player_bar_click(self, event):
        if self.bar_move_id:
            if self.current_sf2.get_status() == 3:
                self.player_bar_reset()
                return
            current_ratio = event.x / 600
            if current_ratio > 1:
                current_ratio = 1
            elif current_ratio < 0:
                current_ratio = 0
            new_time = self.current_midi_length * current_ratio
            self.current_second = new_time
            self.player_bar['value'] = current_ratio * 100
            self.player_bar_set_time(self.current_second)
            new_ticks = int(
                mido.second2tick(self.current_second,
                                 self.current_midi_object.ticks_per_beat,
                                 self.current_sf2.get_current_tempo()))
            self.current_sf2.set_pos(new_ticks)

    def player_bar_reset(self):
        if self.current_sf2.get_status() != 3:
            self.bar_move_id = self.after(1000, self.player_bar_move)
            return
        self.bar_move_id = None
        self.player_bar['value'] = 0
        self.current_second = 0
        self.player_bar_set_time(self.current_second)

    def show(self, text=''):
        self.msg.configure(text=text)
        self.msg.update()

    def choose_midi(self, current_midi_file=None):
        if current_midi_file is None:
            current_midi_file = filedialog.askopenfilename(
                title="Choose MIDI File",
                filetypes=(('MIDI files', "*.mid"), ("All files", "*.*")))
        if current_midi_file:
            self.current_midi_file = current_midi_file
            self.current_midi_file_read = None
            self.current_midi_label.configure(
                text=textwrap.fill(self.current_midi_file, width=90))
            self.current_path = os.path.dirname(self.current_midi_file)
            self.already_load = False

    def second_to_time_label(self, second):
        current_hour = int(second / 3600)
        current_minute = int((second - 3600 * current_hour) / 60)
        current_second = int(
            (second - 3600 * current_hour - 60 * current_minute))
        result = f'{current_hour:02d}:{current_minute:02d}:{current_second:02d}'
        return result

    def choose_soundfont(self, current_soundfont_file=None):
        if current_soundfont_file is None:
            current_soundfont_file = filedialog.askopenfilename(
                title="Choose SoundFont File",
                filetypes=(('SoundFont files', "*.sf2;*.sf3;*.dls"),
                           ("All files", "*.*")))
        if current_soundfont_file:
            try:
                self.current_sf2.load(current_soundfont_file)
                self.current_soundfont_file = current_soundfont_file
                self.current_path = os.path.dirname(
                    self.current_soundfont_file)
                self.current_soundfont_label.configure(
                    text=textwrap.fill(self.current_soundfont_file, width=90))
                self.current_soundfont_label.update()
            except:
                self.show('Invalid SoundFont file')

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
            self.show(
                'Error: The loaded SoundFont file does not contain all the required banks or presets of the MIDI file'
            )
            return
        self.show(f'Start playing')

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
            self.after_cancel(self.bar_move_id)
            self.after_cancel(self.change_bpm_id)
            self.after_cancel(self.change_instrument_id)
        self.player_bar['value'] = 0
        self.current_second = 0
        self.player_bar_set_time(0)
        self.bar_move_id = self.after(1000, self.player_bar_move)

    def init_after_play(self):
        self.update_bpm()
        self.update_instrument()

    def update_bpm(self):
        self.current_bpm = self.current_sf2.get_current_bpm()
        self.bpm_slider.set(f'BPM  {self.current_bpm}')
        self.bpm_outer_change = True
        self.set_move_bpm_bar.set(self.current_bpm)
        self.change_bpm_id = self.after(100, self.update_bpm)

    def update_instrument(self):
        self.instrument_listbox.configure(state=NORMAL)
        self.instrument_listbox.delete(0, END)
        for k in range(16):
            if self.current_sf2.synth.program_info(k)[0] != 0:
                current_instrument = self.current_sf2.synth.channel_info(k)[3]
                if not current_instrument:
                    current_instrument = 'None'
            else:
                current_instrument = 'None'
            self.instrument_listbox.insert(END, current_instrument)
        self.instrument_listbox.configure(state=DISABLED)
        self.change_instrument_id = self.after(100, self.update_instrument)

    def play_midi(self):
        if self.current_midi_file and self.current_soundfont_file:
            if self.current_sf2.playing:
                self.current_sf2.stop()
            self.init_player_bar(self.current_midi_file)
            self.start_play(self.current_midi_file)

    def pause_midi(self):
        if self.current_sf2.playing:
            self.paused = True
            self.show(f'Pause playing')
            self.current_sf2.pause()
        if self.bar_move_id:
            self.after_cancel(self.bar_move_id)
            self.after_cancel(self.change_bpm_id)
            self.after_cancel(self.change_instrument_id)
            self.bar_move_id = None

    def unpause_midi(self):
        if self.paused:
            self.paused = False
            self.show(f'Continue playing')
            self.current_sf2.unpause()
        self.bar_move_id = self.after(1000, self.player_bar_move)

    def stop_midi(self):
        if self.current_sf2.playing:
            self.paused = False
            self.show(f'Stop playing')
            self.current_sf2.stop()
        if self.bar_move_id:
            self.after_cancel(self.bar_move_id)
            self.after_cancel(self.change_bpm_id)
            self.after_cancel(self.change_instrument_id)
        self.bar_move_id = None
        self.player_bar['value'] = 0
        self.current_second = 0
        self.player_bar_set_time(self.current_second)

    def export_audio(self):
        file_name = filedialog.asksaveasfile(title="Export as audio",
                                             defaultextension='.wav',
                                             filetypes=(("All files",
                                                         "*.*"), ),
                                             initialfile='Untitled.wav')
        if not file_name:
            return
        file_name = file_name.name
        self.show(f'Start exporting {file_name}')
        if self.current_soundfont_file:
            current_sf2 = rs.sf2_loader(self.current_soundfont_file)
        else:
            self.show('Please choose a SoundFont file')
            return
        try:
            current_sf2.export_midi_file(
                self.current_midi_file,
                split_channels=self.split_channels.get(),
                name=file_name,
                format=os.path.splitext(file_name)[1][1:])
        except Exception as OSError:
            self.show(
                'Error: The loaded SoundFont file does not contain all the required banks or presets of the MIDI file'
            )
            return
        self.show(f'Finish exporting {file_name}')

    def play_modulation(self):
        if self.current_midi_file and self.current_soundfont_file:
            try:
                before_mode = rs.mp.S(self.modulation_before_entry.get())
                after_mode = rs.mp.S(self.modulation_after_entry.get())
            except:
                self.show('Error: Invalid mode')
                return
            modulation_piece = rs.mp.read(
                self.current_midi_file,
                split_channels=self.split_channels.get()).modulation(
                    before_mode, after_mode)
            rs.mp.write(modulation_piece, name='modulation.mid')
            self.already_load = False
            self.init_player_bar('modulation.mid')
            self.start_play('modulation.mid')
            self.already_load = False

    def detect_key(self):
        if not self.current_midi_file_read:
            self.current_midi_file_read = rs.mp.read(
                self.current_midi_file,
                split_channels=self.split_channels.get())
        current_key = rs.mp.detect_scale(
            self.current_midi_file_read.quick_merge(), most_appear_num=3)
        self.detect_key_label.configure(text=str(current_key))

    def play_reverse(self):
        if not self.current_midi_file_read:
            self.current_midi_file_read = rs.mp.read(
                self.current_midi_file,
                split_channels=self.split_channels.get())
        rs.mp.write(self.current_midi_file_read.reverse(), name='temp.mid')
        self.already_load = False
        self.init_player_bar('temp.mid')
        self.start_play('temp.mid')
        self.already_load = False

    def play_reverse_piano_key(self):
        if not self.current_midi_file_read:
            self.current_midi_file_read = rs.mp.read(
                self.current_midi_file,
                split_channels=self.split_channels.get())
        rs.mp.write(reverse_piano_keys(self.current_midi_file_read),
                    name='temp.mid')
        self.already_load = False
        self.init_player_bar('temp.mid')
        self.start_play('temp.mid')
        self.already_load = False

    def get_setting(self, parameter):
        return self.current_sf2.synth.get_setting(f'synth.{parameter}')

    def change_setting(self, parameter, value):
        self.current_sf2.synth.setting(f'synth.{parameter}', value)


root = Root()
root.mainloop()
