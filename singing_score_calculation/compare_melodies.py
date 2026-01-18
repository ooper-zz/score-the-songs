#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Melody Comparison Tool
Compare two MP3 files and get a melody similarity score
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from mp3towav import easymp3towav
from improved_comparison import ImprovedMelodyScore, Midi2Sqnc
from PIL import Image, ImageTk
import os
import subprocess

class MelodyComparator:
    def __init__(self, root):
        self.root = root
        self.root.title('Melody Comparison Tool')
        self.root.geometry('800x600')
        self.root.configure(bg='#2C3E50')
        
        self.reference_file = None
        self.test_file = None
        self.reference_midi = None
        self.test_midi = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text='Melody Comparison Tool', 
                        font=('Arial', 28, 'bold'), fg='white', bg='#2C3E50')
        title.pack(pady=20)
        
        subtitle = tk.Label(self.root, text='Compare your melody with Suno\'s output', 
                           font=('Arial', 14), fg='#ECF0F1', bg='#2C3E50')
        subtitle.pack(pady=5)
        
        # Reference file section
        ref_frame = tk.Frame(self.root, bg='#34495E', relief=tk.RAISED, borderwidth=2)
        ref_frame.pack(pady=20, padx=40, fill=tk.X)
        
        tk.Label(ref_frame, text='Reference Melody (Your Original)', 
                font=('Arial', 16, 'bold'), fg='#3498DB', bg='#34495E').pack(pady=10)
        
        self.ref_label = tk.Label(ref_frame, text='No file selected', 
                                 font=('Arial', 12), fg='white', bg='#34495E')
        self.ref_label.pack(pady=5)
        
        tk.Button(ref_frame, text='Select Reference File', 
                 font=('Arial', 14), command=self.select_reference,
                 bg='#3498DB', fg='white', padx=20, pady=10).pack(pady=10)
        
        # Test file section
        test_frame = tk.Frame(self.root, bg='#34495E', relief=tk.RAISED, borderwidth=2)
        test_frame.pack(pady=20, padx=40, fill=tk.X)
        
        tk.Label(test_frame, text='Test Melody (Suno\'s Output)', 
                font=('Arial', 16, 'bold'), fg='#E74C3C', bg='#34495E').pack(pady=10)
        
        self.test_label = tk.Label(test_frame, text='No file selected', 
                                  font=('Arial', 12), fg='white', bg='#34495E')
        self.test_label.pack(pady=5)
        
        tk.Button(test_frame, text='Select Test File', 
                 font=('Arial', 14), command=self.select_test,
                 bg='#E74C3C', fg='white', padx=20, pady=10).pack(pady=10)
        
        # Compare button
        self.compare_btn = tk.Button(self.root, text='Compare Melodies', 
                                    font=('Arial', 18, 'bold'), 
                                    command=self.compare_melodies,
                                    bg='#27AE60', fg='white', 
                                    padx=30, pady=15, state=tk.DISABLED)
        self.compare_btn.pack(pady=30)
        
        # Result display
        self.result_label = tk.Label(self.root, text='', 
                                     font=('Arial', 24, 'bold'), 
                                     fg='#F39C12', bg='#2C3E50')
        self.result_label.pack(pady=20)
        
        # Status bar
        self.status_label = tk.Label(self.root, text='Ready', 
                                     font=('Arial', 10), 
                                     fg='#95A5A6', bg='#2C3E50')
        self.status_label.pack(side=tk.BOTTOM, pady=10)
    
    def select_reference(self):
        filepath = filedialog.askopenfilename(
            title='Select Reference Melody File',
            filetypes=[('Audio Files', '*.mp3 *.wav'), ('All Files', '*.*')]
        )
        if filepath:
            self.reference_file = filepath
            filename = os.path.basename(filepath)
            self.ref_label.config(text=filename)
            self.status_label.config(text=f'Reference loaded: {filename}')
            self.check_ready()
    
    def select_test(self):
        filepath = filedialog.askopenfilename(
            title='Select Test Melody File (Suno Output)',
            filetypes=[('Audio Files', '*.mp3 *.wav'), ('All Files', '*.*')]
        )
        if filepath:
            self.test_file = filepath
            filename = os.path.basename(filepath)
            self.test_label.config(text=filename)
            self.status_label.config(text=f'Test file loaded: {filename}')
            self.check_ready()
    
    def check_ready(self):
        if self.reference_file and self.test_file:
            self.compare_btn.config(state=tk.NORMAL)
    
    def convert_to_midi(self, audio_file):
        """Convert audio file to MIDI using aubio"""
        self.status_label.config(text='Converting to MIDI...')
        self.root.update()
        
        # Convert MP3 to WAV if needed
        if audio_file.endswith('.mp3'):
            wav_file = audio_file[:-4] + '.wav'
            if not os.path.exists(wav_file):
                easymp3towav(audio_file)
            audio_file = wav_file
        
        # Convert WAV to MIDI using aubio
        midi_file = audio_file[:-4] + '.mid'
        
        try:
            # Use aubio's aubionotes for melody extraction with correct options
            # Extract notes to a text file first, then convert to MIDI
            notes_file = audio_file[:-4] + '_notes.txt'
            
            # Extract pitch information
            cmd = f'aubionotes "{audio_file}" > "{notes_file}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0 and not os.path.exists(notes_file):
                raise Exception(f"aubionotes failed: {result.stderr}")
            
            # Convert notes to MIDI using music21
            from music21 import stream, note, midi as m21midi
            
            s = stream.Stream()
            
            # Read the notes file
            if os.path.exists(notes_file):
                with open(notes_file, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            try:
                                time_sec = float(parts[0])
                                freq = float(parts[1])
                                
                                # Convert frequency to MIDI note
                                if freq > 0:
                                    import math
                                    midi_note = int(69 + 12 * math.log2(freq / 440.0))
                                    if 0 <= midi_note <= 127:
                                        n = note.Note(midi_note)
                                        n.offset = time_sec
                                        n.quarterLength = 0.25
                                        s.append(n)
                            except (ValueError, IndexError):
                                continue
                
                # Clean up notes file
                os.remove(notes_file)
            
            # Write MIDI file
            if len(s.notes) > 0:
                mf = m21midi.translate.music21ObjectToMidiFile(s)
                mf.open(midi_file, 'wb')
                mf.write()
                mf.close()
            else:
                raise Exception("No notes detected in audio file")
                
            return midi_file
            
        except Exception as e:
            messagebox.showerror('Conversion Error', 
                               f'Failed to convert to MIDI: {str(e)}\n\n'
                               'Make sure aubio is installed:\n'
                               'brew install aubio')
            return None
    
    def compare_melodies(self):
        try:
            self.result_label.config(text='Processing...')
            self.compare_btn.config(state=tk.DISABLED)
            self.root.update()
            
            # Convert reference to MIDI
            self.status_label.config(text='Converting reference file...')
            self.root.update()
            self.reference_midi = self.convert_to_midi(self.reference_file)
            if not self.reference_midi:
                return
            
            # Convert test to MIDI
            self.status_label.config(text='Converting test file...')
            self.root.update()
            self.test_midi = self.convert_to_midi(self.test_file)
            if not self.test_midi:
                return
            
            # Create template sequence file for reference
            self.status_label.config(text='Analyzing melodies...')
            self.root.update()
            
            ref_sqnc = Midi2Sqnc(self.reference_midi)
            ref_txt = self.reference_midi + '.txt'
            with open(ref_txt, 'w') as f:
                f.write(','.join(map(str, ref_sqnc)) + ',\n')
            
            # Compare using ImprovedMelodyScore
            self.status_label.config(text='Calculating similarity score...')
            self.root.update()
            
            score = ImprovedMelodyScore(ref_txt, self.test_midi)
            
            # Display result
            self.result_label.config(text=f'Similarity Score: {score:.2f}/100')
            
            # Interpretation
            if score >= 80:
                interpretation = 'Excellent match! 🎵'
                color = '#27AE60'
            elif score >= 60:
                interpretation = 'Good match! 👍'
                color = '#F39C12'
            elif score >= 40:
                interpretation = 'Moderate match'
                color = '#E67E22'
            else:
                interpretation = 'Low match'
                color = '#E74C3C'
            
            self.result_label.config(fg=color)
            self.status_label.config(text=interpretation)
            
            messagebox.showinfo('Comparison Complete', 
                              f'Similarity Score: {score:.2f}/100\n\n{interpretation}')
            
        except Exception as e:
            messagebox.showerror('Error', f'Comparison failed: {str(e)}')
            self.status_label.config(text='Error occurred')
        finally:
            self.compare_btn.config(state=tk.NORMAL)

def main():
    root = tk.Tk()
    app = MelodyComparator(root)
    root.mainloop()

if __name__ == '__main__':
    main()
