#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Melody Comparison Tool - Compact Layout
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from mp3towav import easymp3towav
from sequential_comparison import SequentialMelodyScore, Midi2Sqnc
import os
import subprocess
import threading

class SimpleMelodyComparator:
    def __init__(self, root):
        self.root = root
        self.root.title('Melody Comparison - Suno Validator (Use Pre-Stemmed Files)')
        self.root.geometry('800x650')
        self.root.configure(bg='#1a1a2e')
        self.root.resizable(True, True)
        
        self.reference_file = None
        self.test_file = None
        self.reference_midi = None
        self.test_midi = None
        self.stem_reference = tk.BooleanVar(value=False)
        self.stem_test = tk.BooleanVar(value=False)
        self.stem_quality = tk.StringVar(value='fast')  # 'fast' or 'quality'
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main container
        main = tk.Frame(self.root, bg='#1a1a2e')
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(main, text='🎵 Melody Comparison Tool', 
                font=('Arial', 28, 'bold'), fg='#00d4ff', bg='#1a1a2e').pack(pady=(0, 5))
        
        tk.Label(main, text='For pre-stemmed vocals/melody files', 
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
        
        # Stemming options
        stem_frame = tk.LabelFrame(main, text='  Optional AI Stem Separation  ', 
                                  font=('Arial', 12, 'bold'), fg='#a0a0a0', bg='#1a1a2e',
                                  relief=tk.FLAT, padx=15, pady=10)
        stem_frame.pack(pady=15, fill=tk.X)
        
        tk.Label(stem_frame, text='Isolate melody from full mix',
                font=('Arial', 9, 'italic'), fg='#7f8c8d', bg='#1a1a2e').pack(anchor='w', pady=(0, 5))
        
        tk.Checkbutton(stem_frame, 
                      text='🎵 Stem Reference File',
                      variable=self.stem_reference,
                      font=('Arial', 10),
                      fg='#ecf0f1', bg='#1a1a2e',
                      selectcolor='#16213e',
                      activebackground='#1a1a2e',
                      activeforeground='#00d4ff',
                      cursor='hand2').pack(anchor='w', pady=2)
        
        tk.Checkbutton(stem_frame, 
                      text='🎼 Stem Test File (Suno output)',
                      variable=self.stem_test,
                      font=('Arial', 10),
                      fg='#ecf0f1', bg='#1a1a2e',
                      selectcolor='#16213e',
                      activebackground='#1a1a2e',
                      activeforeground='#00d4ff',
                      cursor='hand2').pack(anchor='w', pady=2)
        
        # Quality selection
        quality_frame = tk.Frame(stem_frame, bg='#1a1a2e')
        quality_frame.pack(anchor='w', pady=(8, 0))
        
        tk.Label(quality_frame, text='Model:', font=('Arial', 9), 
                fg='#a0a0a0', bg='#1a1a2e').pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Radiobutton(quality_frame, text='⚡ Fast (~15-30s)', 
                      variable=self.stem_quality, value='fast',
                      font=('Arial', 9), fg='#ecf0f1', bg='#1a1a2e',
                      selectcolor='#16213e', activebackground='#1a1a2e',
                      cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        tk.Radiobutton(quality_frame, text='🎯 High Quality (~60-120s)', 
                      variable=self.stem_quality, value='quality',
                      font=('Arial', 9), fg='#ecf0f1', bg='#1a1a2e',
                      selectcolor='#16213e', activebackground='#1a1a2e',
                      cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        # COMPARE BUTTON - Large and prominent
        compare_frame = tk.Frame(main, bg='#1a1a2e')
        compare_frame.pack(pady=20)
        
        self.compare_btn = tk.Button(compare_frame, text='⚡ COMPARE MELODIES ⚡', 
                                    font=('Arial', 18, 'bold'), 
                                    command=self.start_comparison,
                                    bg='#4ecdc4', fg='#1a1a2e', 
                                    padx=50, pady=20, 
                                    relief=tk.RAISED, bd=3,
                                    cursor='hand2',
                                    state=tk.DISABLED)
        self.compare_btn.pack()
        
        # Progress indicator
        self.progress_label = tk.Label(main, text='', 
                                      font=('Arial', 12, 'italic'), 
                                      fg='#f39c12', bg='#1a1a2e')
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
            self.status_label.config(text='✓ Ready! Click COMPARE MELODIES button above', fg='#4ecdc4')
    
    def start_comparison(self):
        thread = threading.Thread(target=self.compare_melodies, daemon=True)
        thread.start()
    
    def separate_stems(self, audio_file):
        """Use Demucs to separate vocals/melody from accompaniment"""
        import shutil
        
        filename = os.path.basename(audio_file)
        self.status_label.config(text=f'Separating {filename}...')
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
            
            # Choose model based on quality setting
            if self.stem_quality.get() == 'quality':
                model = 'mdx_extra'  # High quality, slower
                self.progress_label.config(text=f'🎼 Separating melody (high quality)...\nThis takes 60-120 seconds, please wait...')
            else:
                model = 'htdemucs'  # Fast, good quality
                self.progress_label.config(text=f'🎼 Separating melody (fast)...\nThis takes 15-30 seconds, please wait...')
            
            self.root.update()
            
            # Run Demucs to separate stems (vocals only)
            cmd = f'"{demucs_path}" --two-stems=vocals -n {model} "{audio_file}" -o "{output_dir}/demucs_output"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            # Find the vocals file (check if it exists, demucs progress goes to stderr so returncode isn't reliable)
            vocals_path = os.path.join(output_dir, 'demucs_output', model, base_name, 'vocals.wav')
            
            if not os.path.exists(vocals_path):
                # Only raise error if file wasn't created
                raise Exception(f"Vocals stem not found. Demucs output: {result.stderr[:500]}")
            
            self.progress_label.config(text='✓ Stem separation complete')
            self.root.update()
            return vocals_path
            
        except Exception as e:
            print(f"Stem separation failed: {str(e)}")
            self.progress_label.config(text=f'⚠ Stemming failed - using original file', fg='#e67e22')
            self.root.update()
            return audio_file  # Return original file if stemming fails
    
    def convert_to_midi(self, audio_file):
        """Convert audio to MIDI with melody focus"""
        if audio_file.endswith('.mp3'):
            wav_file = audio_file[:-4] + '.wav'
            if not os.path.exists(wav_file):
                easymp3towav(audio_file)
            audio_file = wav_file
        
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
                                if 80 <= freq <= 1000:
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
                        
                        for j in range(i + 1, min(i + 5, len(pitches))):
                            next_freq = pitches[j][1]
                            if abs(12 * math.log2(next_freq / freq)) < 2:
                                stable_count += 1
                                avg_freq += next_freq
                        
                        if stable_count >= 2:
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
            print(f"Conversion failed: {str(e)}")
            self.status_label.config(text=f'Conversion failed: {str(e)}', fg='#e74c3c')
            return None
    
    def compare_melodies(self):
        import shutil
        
        try:
            self.result_label.config(text='Processing...')
            self.compare_btn.config(state=tk.DISABLED, bg='#4ecdc4')
            self.root.update()
            
            # Optionally separate stems
            ref_audio = self.reference_file
            test_audio = self.test_file
            
            print(f"\n{'='*60}")
            print(f"Stem reference: {self.stem_reference.get()}")
            print(f"Stem test: {self.stem_test.get()}")
            print(f"{'='*60}\n")
            
            if self.stem_reference.get():
                self.status_label.config(text='Separating reference melody...')
                self.root.update()
                ref_audio = self.separate_stems(self.reference_file)
            
            if self.stem_test.get():
                self.status_label.config(text='Separating test melody...')
                self.root.update()
                test_audio = self.separate_stems(self.test_file)
            
            self.status_label.config(text='Converting reference...')
            self.root.update()
            self.reference_midi = self.convert_to_midi(ref_audio)
            if not self.reference_midi:
                return
            
            self.status_label.config(text='Converting test...')
            self.root.update()
            self.test_midi = self.convert_to_midi(test_audio)
            if not self.test_midi:
                return
            
            self.status_label.config(text='Analyzing...')
            self.root.update()
            
            ref_sqnc = Midi2Sqnc(self.reference_midi)
            ref_txt = self.reference_midi + '.txt'
            with open(ref_txt, 'w') as f:
                f.write(','.join(map(str, ref_sqnc)) + ',\n')
            
            self.status_label.config(text='Calculating score...')
            self.root.update()
            
            score = SequentialMelodyScore(ref_txt, self.test_midi)
            
            # Determine match level (DTW-based scoring)
            if score >= 60:
                match_level = 'STRONG MATCH'
                interpretation = 'Strong derivative detected'
                color = '#4ecdc4'
            elif score >= 50:
                match_level = 'MATCH'
                interpretation = 'Likely derivative'
                color = '#f39c12'
            elif score >= 35:
                match_level = 'UNCERTAIN'
                interpretation = 'Inconclusive - manual review needed'
                color = '#e67e22'
            else:
                match_level = 'NO MATCH'
                interpretation = 'Different melodies'
                color = '#e74c3c'
            
            self.result_label.config(text=f'{match_level}: {score:.1f}/100')
            
            self.result_label.config(fg=color)
            self.status_label.config(text=interpretation, fg=color)
            self.progress_label.config(text='✓ Complete - Check terminal for details', fg='#4ecdc4')
            
            # Cleanup demucs output if stemming was used
            if self.stem_reference.get() or self.stem_test.get():
                try:
                    # Clean up from reference file directory
                    if self.stem_reference.get():
                        output_dir = os.path.dirname(self.reference_file)
                        demucs_dir = os.path.join(output_dir, 'demucs_output')
                        if os.path.exists(demucs_dir):
                            shutil.rmtree(demucs_dir)
                    
                    # Clean up from test file directory
                    if self.stem_test.get():
                        output_dir = os.path.dirname(self.test_file)
                        demucs_dir = os.path.join(output_dir, 'demucs_output')
                        if os.path.exists(demucs_dir):
                            shutil.rmtree(demucs_dir)
                except:
                    pass
            
        except Exception as e:
            print(f"Comparison failed: {str(e)}")
            self.status_label.config(text=f'Error: {str(e)}', fg='#e74c3c')
            self.progress_label.config(text='', fg='#e74c3c')
        finally:
            self.compare_btn.config(state=tk.NORMAL, bg='#45b7af')

def main():
    root = tk.Tk()
    app = SimpleMelodyComparator(root)
    root.mainloop()

if __name__ == '__main__':
    main()
