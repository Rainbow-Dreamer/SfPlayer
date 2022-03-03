with open('packages/config.py', encoding='utf-8') as f:
    exec(f.read())


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

    def init_main_window(self):
        self.minsize(850, 520)
        self.title('SfPlayer')
        self.configure(bg='white')

        style = ttk.Style()
        style.configure('TLabel', background='white')
        style.configure('TCheckbutton', background='white')
        style.configure('TScale', background='white')
        style.configure('TFrame', background='white')
        style.configure('Custom.TNotebook.Tab', padding=[20, 4])

        self.notebook = ttk.Notebook(self,
                                     height=600,
                                     width=850,
                                     style='Custom.TNotebook')
        self.notebook.place(x=0, y=0)

        self.playback_frame = ttk.Frame(self, height=600, width=850)
        self.playback_frame.place(x=0, y=0)

        self.music_function_frame = ttk.Frame(self, height=600, width=850)
        self.music_function_frame.place(x=0, y=0)

        self.synth_control_frame = ttk.Frame(self, height=600, width=850)
        self.synth_control_frame.place(x=0, y=0)

        self.playback_frame.drop_target_register(DND_FILES)
        self.playback_frame.dnd_bind('<<Drop>>', self.drag_files)

        self.notebook.add(self.playback_frame, text='Playback')
        self.notebook.add(self.music_function_frame, text='Music Functions')
        self.notebook.add(self.synth_control_frame, text='Synth Settings')

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
            variable=self.split_channels)
        self.split_channels_button.place(x=50, y=370)

    def init_music_function_region(self):
        self.detect_key_button = ttk.Button(self.music_function_frame,
                                            text='Detect Key',
                                            command=self.detect_key)
        self.detect_key_button.place(x=50, y=50)
        self.detect_key_label = ttk.Label(self.music_function_frame, text='')
        self.detect_key_label.place(x=180, y=50)

        self.custom_instrument_label = ttk.Label(self.music_function_frame,
                                                 text='Custom Instruments')
        self.custom_instrument_label.place(x=50, y=200)
        self.custom_instrument_text = ttk.Entry(self.music_function_frame,
                                                width=40)
        self.custom_instrument_text.place(x=50, y=230)
        self.custom_play_button = ttk.Button(self.music_function_frame,
                                             text='Custom Play',
                                             command=self.custom_play)
        self.custom_play_button.place(x=230, y=190)

        self.export_audio_button = ttk.Button(self.music_function_frame,
                                              text='Export As Audio',
                                              command=self.export_audio)
        self.export_audio_button.place(x=50, y=120)

        self.modulation_before_label = ttk.Label(self.music_function_frame,
                                                 text='From Mode')
        self.modulation_before_label.place(x=50, y=300)
        self.modulation_before_entry = ttk.Entry(self.music_function_frame,
                                                 width=20)
        self.modulation_before_entry.place(x=150, y=300)
        self.modulation_after_label = ttk.Label(self.music_function_frame,
                                                text='to Mode')
        self.modulation_after_label.place(x=320, y=300)
        self.modulation_after_entry = ttk.Entry(self.music_function_frame,
                                                width=20)
        self.modulation_after_entry.place(x=400, y=300)
        self.modulation_play_button = ttk.Button(self.music_function_frame,
                                                 text='Play Modulation',
                                                 command=self.play_modulation)
        self.modulation_play_button.place(x=580, y=295)

    def init_message_region(self):
        self.msg = ttk.Label(self, text='Currently no actions')
        self.msg.place(x=50, y=470)

    def init_synth_control_region(self):
        self.init_volume_bar()
        self.init_bpm_bar()
        self.has_reverb = IntVar()
        self.has_reverb.set(0)
        self.reverb_button = ttk.Checkbutton(self.synth_control_frame,
                                             text='Reverb',
                                             variable=self.has_reverb,
                                             command=self.change_reverb)
        self.reverb_button.place(x=50, y=250)

    def init_volume_bar(self):
        self.volume_slider = StringVar()
        self.current_volume_percentage = self.get_setting('gain') * 10
        self.volume_slider.set(f'Volume  {self.current_volume_percentage}%')
        self.volume_slider_label = ttk.Label(self.synth_control_frame,
                                             textvariable=self.volume_slider)
        self.volume_slider_label.place(x=50, y=100)
        self.set_move_volume_bar = ttk.Scale(
            self.synth_control_frame,
            from_=0,
            to=100,
            orient=HORIZONTAL,
            length=500,
            value=self.current_volume_percentage,
            command=lambda e: self.change_move_volume_bar(e),
            takefocus=False)
        self.set_move_volume_bar.place(x=200, y=100)

    def init_bpm_bar(self):
        self.bpm_slider = StringVar()
        self.current_bpm = 120
        self.bpm_slider.set(f'BPM  {self.current_bpm}')
        self.bpm_slider_label = ttk.Label(self.synth_control_frame,
                                          textvariable=self.bpm_slider)
        self.bpm_slider_label.place(x=50, y=150)
        self.set_move_bpm_bar = ttk.Scale(
            self.synth_control_frame,
            from_=0,
            to=1000,
            orient=HORIZONTAL,
            length=500,
            value=self.current_bpm,
            command=lambda e: self.change_move_bpm_bar(e),
            takefocus=False)
        self.set_move_bpm_bar.place(x=200, y=150)

    def change_move_volume_bar(self, e):
        self.current_volume_percentage = round(float(e) * 5) / 5
        self.volume_slider.set(f'Volume  {self.current_volume_percentage}%')
        self.change_setting('gain', self.current_volume_percentage / 10)
        self.synth_volume = self.current_volume_percentage / 10

    def change_move_bpm_bar(self, e):
        self.current_bpm = int(float(e))
        self.bpm_slider.set(f'BPM  {self.current_bpm}')
        if hasattr(self.current_sf2.synth, 'player'):
            self.current_sf2.set_tempo(self.current_bpm)

    def change_reverb(self):
        if self.has_reverb.get():
            self.change_setting('reverb.active', 1)
        else:
            self.change_setting('reverb.active', 0)

    def drag_files(self, e):
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
                initialdir=self.current_path,
                title="Choose MIDI File",
                filetypes=(('MIDI files', "*.mid"), ("All files", "*.*")))
        if current_midi_file:
            self.current_midi_file = current_midi_file
            self.current_midi_file_read = None
            self.current_midi_label.configure(text=self.current_midi_file)
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
                initialdir=self.current_path,
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
                    text=self.current_soundfont_file)
                self.current_soundfont_label.update()
            except:
                self.show('Invalid SoundFont file')

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
        self.player_bar['value'] = 0
        self.current_second = 0
        self.player_bar_set_time(0)
        self.bar_move_id = self.after(1000, self.player_bar_move)

    def play_midi(self):
        if self.current_midi_file and self.current_soundfont_file:
            if self.current_sf2.playing:
                self.current_sf2.stop()
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()

            self.init_player_bar(self.current_midi_file)

            try:
                if load_sf2_mode == 1:
                    self.current_sf2 = rs.sf2_player(
                        self.current_soundfont_file)
                    self.change_setting('gain', self.synth_volume)
                self.current_sf2.play_midi_file(self.current_midi_file)
            except Exception as OSError:
                import traceback
                print(traceback.format_exc())
                self.show(
                    'Error: The loaded SoundFont file does not contain all the required banks or presets of the MIDI file'
                )
                return
            self.show(f'Start playing')

    def pause_midi(self):
        if self.current_sf2.playing:
            self.paused = True
            self.show(f'Pause playing')
            self.current_sf2.pause()
        pygame.mixer.music.pause()
        if self.bar_move_id:
            self.after_cancel(self.bar_move_id)
            self.bar_move_id = None

    def unpause_midi(self):
        if self.paused:
            self.paused = False
            self.show(f'Continue playing')
            self.current_sf2.unpause()
        pygame.mixer.music.unpause()
        self.bar_move_id = self.after(1000, self.player_bar_move)

    def stop_midi(self):
        if self.current_sf2.playing:
            self.paused = False
            self.show(f'Stop playing')
            self.current_sf2.stop()
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        if self.bar_move_id:
            self.after_cancel(self.bar_move_id)
        self.bar_move_id = None
        self.player_bar['value'] = 0
        self.current_second = 0
        self.player_bar_set_time(self.current_second)

    def export_audio(self):
        file_name = filedialog.asksaveasfile(initialdir=self.current_path,
                                             title="Export as audio",
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

    def custom_play(self):
        if self.current_midi_file and self.current_soundfont_file:

            if self.current_sf2.playing:
                self.current_sf2.stop()
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()

            current_midi_file = rs.mp.read(
                self.current_midi_file,
                split_channels=self.split_channels.get())
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
            rs.mp.write(current_midi_file, name='temp.mid')
            self.init_player_bar('temp.mid')
            try:
                if load_sf2_mode == 1:
                    self.current_sf2 = rs.sf2_player(
                        self.current_soundfont_file)
                    self.change_setting('gain', self.synth_volume)
                self.current_sf2.play_midi_file('temp.mid')
            except Exception as OSError:
                self.show(
                    'Error: The loaded SoundFont file does not contain all the required banks or presets of the MIDI file'
                )
                return
            self.show(f'Start playing')

    def play_modulation(self):
        if self.current_midi_file and self.current_soundfont_file:
            try:
                before_mode = rs.mp.S(self.modulation_before_entry.get())
                after_mode = rs.mp.S(self.modulation_after_entry.get())
                modulation_piece = rs.mp.read(
                    self.current_midi_file,
                    split_channels=self.split_channels.get()).modulation(
                        before_mode, after_mode)
                rs.mp.write(modulation_piece, name='modulation.mid')
                self.init_player_bar('modulation.mid')
            except:
                self.show('Error: Invalid mode')
                return
            try:
                if self.current_sf2.playing:
                    self.current_sf2.stop()
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                if load_sf2_mode == 1:
                    self.current_sf2 = rs.sf2_player(
                        self.current_soundfont_file)
                    self.change_setting('gain', self.synth_volume)
                self.current_sf2.play_midi_file('modulation.mid')
            except Exception as OSError:
                self.show(
                    'Error: The loaded SoundFont file does not contain all the required banks or presets of the MIDI file'
                )
                return
            self.show(f'Start playing')

    def detect_key(self):
        if not self.current_midi_file_read:
            self.current_midi_file_read = rs.mp.read(
                self.current_midi_file,
                split_channels=self.split_channels.get())
        current_key = rs.mp.detect_scale(
            self.current_midi_file_read.quick_merge())
        self.detect_key_label.configure(text=str(current_key))

    def get_setting(self, parameter):
        return self.current_sf2.synth.get_setting(f'synth.{parameter}')

    def change_setting(self, parameter, value):
        self.current_sf2.synth.setting(f'synth.{parameter}', value)


root = Root()
root.mainloop()
