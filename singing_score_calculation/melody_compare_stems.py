#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Melody Comparison with Stem Separation
Uses Demucs to isolate melody/vocals before comparison
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from mp3towav import easymp3towav
from strict_comparison import StrictMelodyScore, Midi2Sqnc
import os
import subprocess
import threading
import shutil

class StemMelodyComparator:
    def __init__(self, root):
        self.root = root
        self.root.title('Melody Comparison - Suno Validator (with Stem Separation)')
        self.root.geometry('800x700')
        self.root.configure(bg='#1a1a2e')
        self.root.resizable(True, True)
        
        self.reference_file = None
        self.test_file = None
        self.reference_midi = None
        self.test_midi = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main container
        main = tk.Frame(self.root, bg='#1a1a2e')
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(main, text='🎵 Melody Comparison Tool', 
                font=('Arial', 28, 'bold'), fg='#00d4ff', bg='#1a1a2e').pack(pady=(0, 5))
        
        tk.Label(main, text='With AI Stem Separation for Better Accuracy', 
                font=('Arial', 12), fg='#a0a0a0', bg='#1a1a2e').pack(pady=(0, 20))
        
        # Reference section
        ref_frame = tk.LabelFrame(main, text='  Reference (Your Melody)  ', 
                                 font=('Arial', 14, 'bold'), fg='#00d4ff', bg='#16213e',
                                 relief=tk.FLAT, padx=20, pady=15)
        ref_frame.pack(fill=tk.X, pady=10)
        
        self.ref_label = tk.Label(ref_frame, text='No file selected', 
                                 font=('Arial', 11), fg='#ecf0f1', bg='#16213e',
                                 wraplength=650, justify='left')
        self.ref_label.pack(pady=(0, 10))
        
        tk.Button(ref_frame, text='📁 Select Reference File', 
                 font=('Arial', 13, 'bold'), command=self.select_reference,
                 bg='#00d4ff', fg='#1a1a2e', padx=25, pady=12,
                 relief=tk.FLAT, cursor='hand2').pack()
        
        # Test section
        test_frame = tk.LabelFrame(main, text='  Test (Suno Output)  ', 
                                  font=('Arial', 14, 'bold'), fg='#ff6b6b', bg='#16213e',
                                  relief=tk.FLAT, padx=20, pady=15)
        test_frame.pack(fill=tk.X, pady=10)
        
        self.test_label = tk.Label(test_frame, text='No file selected', 
                                  font=('Arial', 11), fg='#ecf0f1', bg='#16213e',
                                  wraplength=650, justify='left')
        self.test_label.pack(pady=(0, 10))
        
        tk.Button(test_frame, text='📁 Select Test File', 
                 font=('Arial', 13, 'bold'), command=self.select_test,
                 bg='#ff6b6b', fg='#1a1a2e', padx=25, pady=12,
                 relief=tk.FLAT, cursor='hand2').pack()
        
        # COMPARE BUTTON
        compare_frame = tk.Frame(main, bg='#1a1a2e')
        compare_frame.pack(pady=25)
        
        self.compare_btn = tk.Button(compare_frame, text='⚡ COMPARE MELODIES ⚡', 
                                    font=('Arial', 18, 'bold'), 
                                    command=self.start_comparison,
                                    bg='#4ecdc4', fg='#1a1a2e', 
                                    padx=50, pady=20, 
                                    relief=tk.RAISED, bd=3,
                                    cursor='hand2',
                                    state=tk.DISABLED)
        self.compare_btn.pack()
        
        # Progress info
        self.progress_label = tk.Label(main, text='', 
                                      font=('Arial', 10, 'italic'), 
                                      fg='#95a5a6', bg='#1a1a2e')
        self.progress_label.pack(pady=5)
        
        # Result
        self.result_label = tk.Label(main, text='', 
                                     font=('Arial', 24, 'bold'), 
                                     fg='#4ecdc4', bg='#1a1a2e')
        self.result_label.pack(pady=15)
        
        # Status
        self.status_label = tk.Label(main, text='Select both files to begin', 
                                     font=('Arial', 10), 
                                     fg='#7f8c8d', bg='#1a1a2e')
        self.status_label.pack(pady=5)
    
    def select_reference(self):
        filepath = filedialog.askopenfilename(
            title='Select Reference Melody',
            filetypes=[('Audio Files', '*.mp3 *.wav'), ('All Files', '*.*')]
        )
        if filepath:
            self.reference_file = filepath
            filename = os.path.basename(filepath)
            self.ref_label.config(text=f'✓ {filename}')
            self.status_label.config(text=f'Reference: {filename}')
            self.check_ready()
    
    def select_test(self):
        filepath = filedialog.askopenfilename(
            title='Select Test Melody (Suno)',
            filetypes=[('Audio Files', '*.mp3 *.wav'), ('All Files', '*.*')]
        )
        if filepath:
            self.test_file = filepath
            filename = os.path.basename(filepath)
            self.test_label.config(text=f'✓ {filename}')
            self.status_label.config(text=f'Test: {filename}')
            self.check_ready()
    
    def check_ready(self):
        if self.reference_file and self.test_file:
            self.compare_btn.config(state=tk.NORMAL, bg='#45b7af')
            self.status_label.config(text='✓ Ready! Click COMPARE MELODIES button', fg='#4ecdc4')
    
    def start_comparison(self):
        thread = threading.Thread(target=self.compare_melodies, daemon=True)
        thread.start()
    
    def separate_stems(self, audio_file):
        """Use Demucs to separate vocals/melody from accompaniment"""
        self.progress_label.config(text='Separating melody from accompaniment (this may take 30-60 seconds)...')
        self.root.update()
        
        # Convert MP3 to WAV if needed
        if audio_file.endswith('.mp3'):
            wav_file = audio_file[:-4] + '.wav'
            if not os.path.exists(wav_file):
                easymp3towav(audio_file)
            audio_file = wav_file
        
        # Create output directory
        output_dir = os.path.dirname(audio_file)
        base_name = os.path.splitext(os.path.basename(audio_file))[0]
        
        try:
            # Get path to demucs in venv
            venv_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            demucs_path = os.path.join(venv_dir, 'venv', 'bin', 'demucs')
            
            # Run Demucs to separate stems (vocals only, faster)
            cmd = f'"{demucs_path}" --two-stems=vocals -n mdx_extra "{audio_file}" -o "{output_dir}/demucs_output"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Demucs failed: {result.stderr}")
            
            # Find the vocals file
            vocals_path = os.path.join(output_dir, 'demucs_output', 'mdx_extra', base_name, 'vocals.wav')
            
            if not os.path.exists(vocals_path):
                raise Exception("Vocals stem not found")
            
            return vocals_path
            
        except Exception as e:
            messagebox.showerror('Stem Separation Error', 
                               f'Failed to separate stems: {str(e)}\n\n'
                               'Make sure demucs is installed correctly.')
            return None
    
    def convert_to_midi(self, audio_file):
        """Convert audio to MIDI with melody focus"""
        midi_file = audio_file[:-4] + '.mid'
        
        try:
            pitch_file = audio_file[:-4] + '_pitch.txt'
            cmd = f'aubiopitch -i "{audio_file}" -u freq > "{pitch_file}"'
            subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            from music21 import stream, note, midi as m21midi
            import math
            
            s = stream.Stream()
            
            if os.path.exists(pitch_file):
                pitches = []
                with open(pitch_file, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            try:
                                time_sec = float(parts[0])
                                freq = float(parts[1])
                                # Wider range for vocals
                                if 80 <= freq <= 1500:
                                    pitches.append((time_sec, freq))
                            except:
                                continue
                
                os.remove(pitch_file)
                
                if len(pitches) > 0:
                    stable_pitches = []
                    i = 0
                    while i < len(pitches):
                        time_sec, freq = pitches[i]
                        stable_count = 1
                        avg_freq = freq
                        
                        # More aggressive stability filtering for cleaner melody
                        for j in range(i + 1, min(i + 7, len(pitches))):
                            next_freq = pitches[j][1]
                            if abs(12 * math.log2(next_freq / freq)) < 1.5:
                                stable_count += 1
                                avg_freq += next_freq
                        
                        if stable_count >= 3:  # Require more stability
                            avg_freq /= stable_count
                            midi_note = int(69 + 12 * math.log2(avg_freq / 440.0))
                            if 0 <= midi_note <= 127:
                                n = note.Note(midi_note)
                                n.offset = time_sec
                                n.quarterLength = 0.5
                                stable_pitches.append(n)
                        
                        i += stable_count
                    
                    for n in stable_pitches:
                        s.append(n)
            
            if len(s.notes) > 0:
                mf = m21midi.translate.music21ObjectToMidiFile(s)
                mf.open(midi_file, 'wb')
                mf.write()
                mf.close()
            else:
                raise Exception("No melody detected")
                
            return midi_file
            
        except Exception as e:
            messagebox.showerror('Error', f'Conversion failed: {str(e)}')
            return None
    
    def compare_melodies(self):
        try:
            self.result_label.config(text='Processing...')
            self.compare_btn.config(state=tk.DISABLED, bg='#4ecdc4')
            self.root.update()
            
            # Separate stems for reference
            self.status_label.config(text='Separating reference melody...')
            self.root.update()
            ref_vocals = self.separate_stems(self.reference_file)
            if not ref_vocals:
                return
            
            # Separate stems for test
            self.status_label.config(text='Separating test melody...')
            self.root.update()
            test_vocals = self.separate_stems(self.test_file)
            if not test_vocals:
                return
            
            # Convert to MIDI
            self.progress_label.config(text='Converting isolated melodies to MIDI...')
            self.status_label.config(text='Converting reference...')
            self.root.update()
            self.reference_midi = self.convert_to_midi(ref_vocals)
            if not self.reference_midi:
                return
            
            self.status_label.config(text='Converting test...')
            self.root.update()
            self.test_midi = self.convert_to_midi(test_vocals)
            if not self.test_midi:
                return
            
            # Compare
            self.progress_label.config(text='')
            self.status_label.config(text='Analyzing melodies...')
            self.root.update()
            
            ref_sqnc = Midi2Sqnc(self.reference_midi)
            ref_txt = self.reference_midi + '.txt'
            with open(ref_txt, 'w') as f:
                f.write(','.join(map(str, ref_sqnc)) + ',\n')
            
            self.status_label.config(text='Calculating score...')
            self.root.update()
            
            score = StrictMelodyScore(ref_txt, self.test_midi)
            
            self.result_label.config(text=f'Score: {score:.1f}/100')
            
            # Stricter thresholds
            if score >= 70:
                interpretation = 'Excellent match! 🎵'
                color = '#4ecdc4'
            elif score >= 50:
                interpretation = 'Good match! 👍'
                color = '#f39c12'
            elif score >= 30:
                interpretation = 'Moderate similarity'
                color = '#e67e22'
            else:
                interpretation = 'Low/No similarity'
                color = '#e74c3c'
            
            self.result_label.config(fg=color)
            self.status_label.config(text=interpretation, fg=color)
            
            # Cleanup demucs output
            try:
                output_dir = os.path.dirname(self.reference_file)
                demucs_dir = os.path.join(output_dir, 'demucs_output')
                if os.path.exists(demucs_dir):
                    shutil.rmtree(demucs_dir)
            except:
                pass
            
            messagebox.showinfo('Complete', 
                              f'Score: {score:.1f}/100\n{interpretation}\n\nCheck terminal for detailed breakdown.')
            
        except Exception as e:
            messagebox.showerror('Error', f'Failed: {str(e)}')
            self.status_label.config(text='Error occurred', fg='#e74c3c')
        finally:
            self.progress_label.config(text='')
            self.compare_btn.config(state=tk.NORMAL, bg='#45b7af')

def main():
    root = tk.Tk()
    app = StemMelodyComparator(root)
    root.mainloop()

if __name__ == '__main__':
    main()
