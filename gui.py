#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 14 11:38:29 2021

@author: bojan
"""

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import transcription
import midi
import musicxml
from utilities import load_wav
import os
import shutil

class Scorpiano():
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("main_window.glade")
        
        self.window = self.builder.get_object("Main")
        self.window.connect("delete-event", Gtk.main_quit)
        
        btn_load_audio = self.builder.get_object("LoadAudio")
        btn_load_audio.connect("clicked", self.load_audio)
        
        btn_transcribe = self.builder.get_object("Transcribe")
        btn_transcribe.connect("clicked", self.transcribe)
        
        file_menu_load_audio = self.builder.get_object("LoadAudioFileMenu")
        file_menu_load_audio.connect("activate", self.load_audio)
    
        file_menu_quit = self.builder.get_object("QuitFileMenu")
        file_menu_quit.connect("activate", self.destroy)
        
        file_menu_export_png = self.builder.get_object("ExportPNGFileMenu")
        file_menu_export_png.connect("activate", self.export_png)
        
        file_menu_export_xml = self.builder.get_object("ExportMusicXMLFileMenu")
        file_menu_export_xml.connect("activate", self.export_mxl)
        
        file_menu_export_midi = self.builder.get_object("ExportMIDIFileMenu")
        file_menu_export_midi.connect("activate", self.export_midi)
        
        action_menu_transcribe = self.builder.get_object("TranscribeActionMenu")
        action_menu_transcribe.connect("activate", self.transcribe)
        
        self.time_sig_text_box = self.builder.get_object("TimeSignatureTextBox")
        self.time_sig_text_box.get_buffer().set_text("4/4")
        
        self.min_beat_text_box = self.builder.get_object("MinBeatDurTextBox")
        self.min_beat_text_box.get_buffer().set_text("0.25")
        
        self.min_distance_text_box = self.builder.get_object("MinDistanceNotesTextBox")
        self.min_distance_text_box.get_buffer().set_text("0.1")
        
        self.wav = self.fs = None
        self.notes = self.beats = self.tempo = None
        self.update = True
        
    def destroy(self, widget):
        self.window.destroy()
        Gtk.main_quit()
        
    def show(self):
        self.window.show_all()
    
    def load_audio(self, widget):
        dialog = Gtk.FileChooserDialog(title="Please choose a wav audio file", 
                                       parent=self.window,
                                       action=Gtk.FileChooserAction.OPEN
                                       )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )
        
        self.add_filters_load(dialog)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            file_path = dialog.get_filename()
            self.fs, self.wav = load_wav(file_path)
            self.update = True
        dialog.destroy()
    
    def add_filters_load(self, dialog):
        filter_wav = Gtk.FileFilter()
        filter_wav.set_name("wav files")
        filter_wav.add_mime_type("audio/wav")
        dialog.add_filter(filter_wav)
    
    def transcribe(self, widget):
        if self.wav is None:
            self.msg_no_audio()
        else:
            time_sig_buffer = self.time_sig_text_box.get_buffer()
            time_sig = time_sig_buffer.get_text(time_sig_buffer.get_start_iter(),
                                                time_sig_buffer.get_end_iter(),
                                                True)
            min_beat_buffer = self.min_beat_text_box.get_buffer()
            min_beat = float(min_beat_buffer.get_text(  min_beat_buffer.get_start_iter(),
                                                        min_beat_buffer.get_end_iter(),
                                                        True))
            min_dist_buffer = self.min_distance_text_box.get_buffer()
            min_dist = float(min_dist_buffer.get_text(min_dist_buffer.get_start_iter(),
                                                      min_dist_buffer.get_end_iter(),
                                                      True))
            self.notes, self.beats, self.tempo = transcription.transcribe(self.wav, self.fs,
                                                           min_beat_dur=min_beat,
                                                           min_distance_notes=min_dist)
            transcription.generate_score(self.notes, self.beats, self.tempo,
                                         "scorpiano_temp/score",
                                         time_sig)
            image = self.builder.get_object("Image")
            image.set_from_file("scorpiano_temp/score.png")
            self.update = False
    
    def export_png(self, widget):
        if self.wav is None:
            self.msg_no_audio()
        else:
            dialog = Gtk.FileChooserDialog(title="Export as PNG", 
                                           parent=self.window,
                                           action=Gtk.FileChooserAction.SAVE
                                           )
            dialog.add_buttons(
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_SAVE,
                Gtk.ResponseType.ACCEPT,
            )
            
            dialog.set_do_overwrite_confirmation(True)
            self.add_filters_png(dialog)
            
            dialog.set_current_name("Score.png")
            response = dialog.run()
            if response == Gtk.ResponseType.ACCEPT:
                file_path = dialog.get_filename()
                shutil.copyfile("scorpiano_temp/score.png", file_path)
            dialog.destroy()
    
    def add_filters_png(self, dialog):
        filter_png = Gtk.FileFilter()
        filter_png.set_name("png files")
        filter_png.add_mime_type("image/png")
        dialog.add_filter(filter_png)
    
    def export_mxl(self, widget):
        if self.wav is None:
            self.msg_no_audio()
        else:
            dialog = Gtk.FileChooserDialog(title="Export as MusicXML", 
                                           parent=self.window,
                                           action=Gtk.FileChooserAction.SAVE
                                           )
            dialog.add_buttons(
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_SAVE,
                Gtk.ResponseType.ACCEPT,
            )
            
            dialog.set_do_overwrite_confirmation(True)
            self.add_filters_mxl(dialog)
            
            dialog.set_current_name("Score.mxl")
            response = dialog.run()
            if response == Gtk.ResponseType.ACCEPT:
                file_path = dialog.get_filename()
                if self.update:
                    self.transcribe(None)
                midi.generate_midi(self.notes, self.beats, self.tempo, "scorpiano_temp/audio.mid")
                musicxml.midi2musicXML("scorpiano_temp/audio.mid", file_path)
                
            dialog.destroy()
    
    def add_filters_mxl(self, dialog):
        filter_mxl = Gtk.FileFilter()
        filter_mxl.set_name("musicxml files")
        filter_mxl.add_mime_type("application/vnd.recordare.musicxml+xml")
        dialog.add_filter(filter_mxl)
    
    def export_midi(self, widget):
        if self.wav is None:
            self.msg_no_audio()
        else:
            dialog = Gtk.FileChooserDialog(title="Export as MIDI", 
                                           parent=self.window,
                                           action=Gtk.FileChooserAction.SAVE
                                           )
            dialog.add_buttons(
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_SAVE,
                Gtk.ResponseType.ACCEPT,
            )
            
            dialog.set_do_overwrite_confirmation(True)
            self.add_filters_midi(dialog)
            
            dialog.set_current_name("Audio.mid")
            response = dialog.run()
            if response == Gtk.ResponseType.ACCEPT:
               file_path = dialog.get_filename()
               if self.update:
                   self.transcribe(None)
               midi.generate_midi(self.notes, self.beats, self.tempo, file_path)
                
            dialog.destroy()
    
    def add_filters_midi(self, dialog):
        filter_midi = Gtk.FileFilter()
        filter_midi.set_name("midi files")
        filter_midi.add_mime_type("audio/midi")
        dialog.add_filter(filter_midi)
    
    def msg_no_audio(self):
        dialog = Gtk.MessageDialog(
                                    transient_for=self.window,
                                    flags=0,
                                    message_type=Gtk.MessageType.INFO,
                                    buttons=Gtk.ButtonsType.CLOSE,
                                    text="Please load audio file",
                                    )
        dialog.run()
        dialog.destroy()

if __name__== "__main__":
    try:
        os.makedirs("scorpiano_temp")
    except FileExistsError:
        pass
    main_window = Scorpiano()
    main_window.show()
    Gtk.main()
    shutil.rmtree("scorpiano_temp")