#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Improved Melody Comparison Tool v2
Better UI and more accurate melody extraction
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from mp3towav import easymp3towav
from improved_comparison import ImprovedMelodyScore, Midi2Sqnc
from PIL import Image, ImageTk
import os
import subprocess
import threading

class MelodyComparatorV2:
    def __init__(self, root):
        self.root = root
        self.root.title('Melody Comparison Tool - Suno Validator')
        self.root.geometry('900x800')
        self.root.configure(bg='#1a1a2e')
        
        self.reference_file = None
        self.test_file = None
        self.reference_midi = None
        self.test_midi = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Create canvas with scrollbar
        canvas = tk.Canvas(self.root, bg='#1a1a2e', highlightthickness=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1a1a2e')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Main container with padding
        main_frame = tk.Frame(scrollable_frame, bg='#1a1a2e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Title
        title = tk.Label(main_frame, text='🎵 Melody Comparison Tool', 
                        font=('Arial', 32, 'bold'), fg='#00d4ff', bg='#1a1a2e')
        title.pack(pady=(0, 10))
        
        subtitle = tk.Label(main_frame, text='Verify how well Suno matches your melody DNA', 
                           font=('Arial', 14), fg='#a0a0a0', bg='#1a1a2e')
        subtitle.pack(pady=(0, 30))
        
        # Reference file section
        ref_frame = tk.Frame(main_frame, bg='#16213e', relief=tk.FLAT, borderwidth=0)
        ref_frame.pack(pady=15, fill=tk.X)
        
        ref_inner = tk.Frame(ref_frame, bg='#16213e')
        ref_inner.pack(padx=25, pady=25, fill=tk.X)
        
        tk.Label(ref_inner, text='📁 Reference Melody', 
                font=('Arial', 18, 'bold'), fg='#00d4ff', bg='#16213e').pack(anchor='w', pady=(0, 10))
        
        tk.Label(ref_inner, text='Your original generated melody', 
                font=('Arial', 11), fg='#7f8c8d', bg='#16213e').pack(anchor='w', pady=(0, 15))
        
        self.ref_label = tk.Label(ref_inner, text='No file selected', 
                                 font=('Arial', 13), fg='#ecf0f1', bg='#16213e',
                                 wraplength=700, justify='left')
        self.ref_label.pack(anchor='w', pady=(0, 15))
        
        tk.Button(ref_inner, text='Select Reference File', 
                 font=('Arial', 14, 'bold'), command=self.select_reference,
                 bg='#00d4ff', fg='#1a1a2e', padx=30, pady=15,
                 relief=tk.FLAT, cursor='hand2',
                 activebackground='#00a8cc', activeforeground='#1a1a2e').pack(anchor='w')
        
        # Test file section
        test_frame = tk.Frame(main_frame, bg='#16213e', relief=tk.FLAT, borderwidth=0)
        test_frame.pack(pady=15, fill=tk.X)
        
        test_inner = tk.Frame(test_frame, bg='#16213e')
        test_inner.pack(padx=25, pady=25, fill=tk.X)
        
        tk.Label(test_inner, text='🎼 Test Melody', 
                font=('Arial', 18, 'bold'), fg='#ff6b6b', bg='#16213e').pack(anchor='w', pady=(0, 10))
        
        tk.Label(test_inner, text='Suno\'s generated output', 
                font=('Arial', 11), fg='#7f8c8d', bg='#16213e').pack(anchor='w', pady=(0, 15))
        
        self.test_label = tk.Label(test_inner, text='No file selected', 
                                  font=('Arial', 13), fg='#ecf0f1', bg='#16213e',
                                  wraplength=700, justify='left')
        self.test_label.pack(anchor='w', pady=(0, 15))
        
        tk.Button(test_inner, text='Select Test File', 
                 font=('Arial', 14, 'bold'), command=self.select_test,
                 bg='#ff6b6b', fg='#1a1a2e', padx=30, pady=15,
                 relief=tk.FLAT, cursor='hand2',
                 activebackground='#ee5a52', activeforeground='#1a1a2e').pack(anchor='w')
        
        # Compare button - MUCH BIGGER
        button_frame = tk.Frame(main_frame, bg='#1a1a2e')
        button_frame.pack(pady=30)
        
        self.compare_btn = tk.Button(button_frame, text='⚡ Compare Melodies', 
                                    font=('Arial', 20, 'bold'), 
                                    command=self.start_comparison,
                                    bg='#4ecdc4', fg='#1a1a2e', 
                                    padx=60, pady=25, 
                                    relief=tk.FLAT, cursor='hand2',
                                    state=tk.DISABLED,
                                    activebackground='#45b7af', activeforeground='#1a1a2e')
        self.compare_btn.pack()
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', length=400)
        
        # Result display
        self.result_label = tk.Label(main_frame, text='', 
                                     font=('Arial', 28, 'bold'), 
                                     fg='#4ecdc4', bg='#1a1a2e')
        self.result_label.pack(pady=20)
        
        # Status bar
        self.status_label = tk.Label(main_frame, text='Ready to compare melodies', 
                                     font=('Arial', 11), 
                                     fg='#7f8c8d', bg='#1a1a2e')
        self.status_label.pack(pady=10)
    
    def select_reference(self):
        filepath = filedialog.askopenfilename(
            title='Select Reference Melody File',
            filetypes=[('Audio Files', '*.mp3 *.wav'), ('All Files', '*.*')]
        )
        if filepath:
            self.reference_file = filepath
            filename = os.path.basename(filepath)
            self.ref_label.config(text=f'✓ {filename}')
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
            self.test_label.config(text=f'✓ {filename}')
            self.status_label.config(text=f'Test file loaded: {filename}')
            self.check_ready()
    
    def check_ready(self):
        if self.reference_file and self.test_file:
            self.compare_btn.config(state=tk.NORMAL)
            self.status_label.config(text='Ready to compare! Click the button above.')
    
    def start_comparison(self):
        """Start comparison in a separate thread"""
        thread = threading.Thread(target=self.compare_melodies, daemon=True)
        thread.start()
    
    def convert_to_midi(self, audio_file):
        """Convert audio file to MIDI using aubio with melody focus"""
        self.status_label.config(text='Converting to MIDI...')
        self.root.update()
        
        # Convert MP3 to WAV if needed
        if audio_file.endswith('.mp3'):
            wav_file = audio_file[:-4] + '.wav'
            if not os.path.exists(wav_file):
                easymp3towav(audio_file)
            audio_file = wav_file
        
        # Convert WAV to MIDI using aubio with pitch tracking
        midi_file = audio_file[:-4] + '.mid'
        
        try:
            # Use aubiopitch for better melody extraction (tracks dominant pitch)
            pitch_file = audio_file[:-4] + '_pitch.txt'
            
            # Extract dominant pitch with optimized parameters for melody
            cmd = f'aubiopitch -i "{audio_file}" -u freq > "{pitch_file}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0 and not os.path.exists(pitch_file):
                raise Exception(f"aubiopitch failed: {result.stderr}")
            
            # Convert pitch to MIDI using music21
            from music21 import stream, note, midi as m21midi
            import math
            
            s = stream.Stream()
            
            # Read the pitch file and filter for melody
            if os.path.exists(pitch_file):
                pitches = []
                with open(pitch_file, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            try:
                                time_sec = float(parts[0])
                                freq = float(parts[1])
                                
                                # Only use frequencies in melodic range (80-1000 Hz)
                                if 80 <= freq <= 1000:
                                    pitches.append((time_sec, freq))
                            except (ValueError, IndexError):
                                continue
                
                # Clean up pitch file
                os.remove(pitch_file)
                
                # Filter out rapid fluctuations (keep stable pitches)
                if len(pitches) > 0:
                    stable_pitches = []
                    i = 0
                    while i < len(pitches):
                        time_sec, freq = pitches[i]
                        
                        # Look ahead to find stable pitch regions
                        stable_count = 1
                        avg_freq = freq
                        
                        for j in range(i + 1, min(i + 5, len(pitches))):
                            next_freq = pitches[j][1]
                            # If within 2 semitones, consider it stable
                            if abs(12 * math.log2(next_freq / freq)) < 2:
                                stable_count += 1
                                avg_freq += next_freq
                        
                        # Only keep if stable for at least 2 frames
                        if stable_count >= 2:
                            avg_freq /= stable_count
                            midi_note = int(69 + 12 * math.log2(avg_freq / 440.0))
                            if 0 <= midi_note <= 127:
                                n = note.Note(midi_note)
                                n.offset = time_sec
                                n.quarterLength = 0.5  # Longer notes
                                stable_pitches.append(n)
                        
                        i += stable_count
                    
                    # Add to stream
                    for n in stable_pitches:
                        s.append(n)
            
            # Write MIDI file
            if len(s.notes) > 0:
                mf = m21midi.translate.music21ObjectToMidiFile(s)
                mf.open(midi_file, 'wb')
                mf.write()
                mf.close()
            else:
                raise Exception("No stable melody detected in audio file")
                
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
            self.progress.pack(pady=10)
            self.progress.start(10)
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
            self.result_label.config(text=f'Score: {score:.1f}/100')
            
            # Interpretation with stricter thresholds
            if score >= 75:
                interpretation = 'Excellent match! 🎵'
                color = '#4ecdc4'
            elif score >= 55:
                interpretation = 'Good match! 👍'
                color = '#f39c12'
            elif score >= 35:
                interpretation = 'Moderate similarity'
                color = '#e67e22'
            else:
                interpretation = 'Low similarity'
                color = '#e74c3c'
            
            self.result_label.config(fg=color)
            self.status_label.config(text=interpretation)
            
            messagebox.showinfo('Comparison Complete', 
                              f'Similarity Score: {score:.1f}/100\n\n{interpretation}\n\n'
                              f'Check terminal for detailed breakdown.')
            
        except Exception as e:
            messagebox.showerror('Error', f'Comparison failed: {str(e)}')
            self.status_label.config(text='Error occurred')
        finally:
            self.progress.stop()
            self.progress.pack_forget()
            self.compare_btn.config(state=tk.NORMAL)

def main():
    root = tk.Tk()
    app = MelodyComparatorV2(root)
    root.mainloop()

if __name__ == '__main__':
    main()
