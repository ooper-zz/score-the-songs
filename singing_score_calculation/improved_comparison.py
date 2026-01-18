# -*- coding: utf-8 -*-
"""
Improved Melody Comparison Algorithm
Focuses on melodic contour and interval patterns rather than absolute pitch
"""

import numpy as np
from music21 import converter
from dtw import dtw
from scipy.spatial.distance import euclidean

def Midi2Sqnc(filepath):
    """Extract MIDI note sequence from file"""
    s = converter.parse(filepath)
    sqnc = []
    for nt in s.recurse():
        if 'Note' in nt.classes:
            sqnc.append(nt.pitch.midi)
    return sqnc

def extract_melodic_contour(midi_sequence):
    """
    Extract melodic contour (up/down/same pattern)
    Returns normalized interval sequence
    """
    if len(midi_sequence) < 2:
        return []
    
    intervals = []
    for i in range(1, len(midi_sequence)):
        diff = midi_sequence[i] - midi_sequence[i-1]
        intervals.append(diff)
    
    return intervals

def extract_pitch_class_sequence(midi_sequence):
    """
    Extract pitch class sequence (ignoring octaves)
    Maps to 0-11 (C, C#, D, D#, E, F, F#, G, G#, A, A#, B)
    """
    return [note % 12 for note in midi_sequence]

def normalize_sequence(sequence):
    """Normalize sequence to mean=0, std=1"""
    if len(sequence) == 0:
        return np.array([])
    arr = np.array(sequence, dtype=float)
    if np.std(arr) == 0:
        return arr - np.mean(arr)
    return (arr - np.mean(arr)) / np.std(arr)

def dtw_distance_euclidean(seq1, seq2):
    """Calculate DTW distance using euclidean distance"""
    if len(seq1) == 0 or len(seq2) == 0:
        return float('inf')
    
    x = np.array(seq1).reshape(-1, 1)
    y = np.array(seq2).reshape(-1, 1)
    
    # Calculate DTW distance
    alignment = dtw(x, y, keep_internals=True)
    dist = alignment.distance
    path_length = len(alignment.index1)
    
    # Normalize by path length
    normalized_dist = dist / path_length if path_length > 0 else float('inf')
    return normalized_dist

def contour_similarity(intervals1, intervals2):
    """
    Compare melodic contours (direction of movement)
    Returns similarity score 0-100
    """
    if len(intervals1) == 0 or len(intervals2) == 0:
        return 0.0
    
    # Normalize intervals to -1 (down), 0 (same), 1 (up)
    def normalize_direction(intervals):
        return [np.sign(i) for i in intervals]
    
    dir1 = normalize_direction(intervals1)
    dir2 = normalize_direction(intervals2)
    
    # Use DTW to align sequences
    x = np.array(dir1).reshape(-1, 1)
    y = np.array(dir2).reshape(-1, 1)
    
    alignment = dtw(x, y, keep_internals=True)
    dist = alignment.distance
    
    # Convert distance to similarity (0-100)
    max_possible_dist = max(len(dir1), len(dir2)) * 2  # max difference is 2 per step
    similarity = max(0, 100 * (1 - dist / max_possible_dist))
    
    return similarity

def interval_pattern_similarity(intervals1, intervals2):
    """
    Compare actual interval sizes (melodic jumps)
    Returns similarity score 0-100
    """
    if len(intervals1) == 0 or len(intervals2) == 0:
        return 0.0
    
    # Normalize intervals
    norm1 = normalize_sequence(intervals1)
    norm2 = normalize_sequence(intervals2)
    
    # Calculate DTW distance
    dist = dtw_distance_euclidean(norm1, norm2)
    
    # Convert to similarity score (0-100)
    # Lower distance = higher similarity
    similarity = max(0, 100 * np.exp(-dist / 2))
    
    return similarity

def rhythm_similarity(midi_seq1, midi_seq2):
    """
    Compare rhythm patterns (note density)
    Returns similarity score 0-100
    """
    len1 = len(midi_seq1)
    len2 = len(midi_seq2)
    
    if len1 == 0 or len2 == 0:
        return 0.0
    
    # Compare note densities
    ratio = min(len1, len2) / max(len1, len2)
    
    return ratio * 100

def pitch_class_similarity(midi_seq1, midi_seq2):
    """
    Compare pitch class distributions (what notes are used)
    Returns similarity score 0-100
    """
    pc1 = extract_pitch_class_sequence(midi_seq1)
    pc2 = extract_pitch_class_sequence(midi_seq2)
    
    if len(pc1) == 0 or len(pc2) == 0:
        return 0.0
    
    # Create histograms of pitch class usage
    hist1 = np.zeros(12)
    hist2 = np.zeros(12)
    
    for pc in pc1:
        hist1[pc] += 1
    for pc in pc2:
        hist2[pc] += 1
    
    # Normalize
    hist1 = hist1 / len(pc1)
    hist2 = hist2 / len(pc2)
    
    # Calculate correlation
    correlation = np.corrcoef(hist1, hist2)[0, 1]
    
    # Handle NaN case
    if np.isnan(correlation):
        correlation = 0
    
    # Convert to 0-100 scale
    similarity = (correlation + 1) / 2 * 100
    
    return similarity

def ImprovedMelodyScore(ref_file_txt, test_file_midi):
    """
    Improved melody comparison focusing on melodic similarity
    
    Scoring components:
    - 30% Melodic contour (up/down patterns)
    - 30% Interval patterns (size of melodic jumps)
    - 20% Pitch class distribution (what notes are used)
    - 20% Rhythm similarity (note density)
    
    Returns: similarity score 0-100
    """
    
    # Load sequences
    test_sqnc = Midi2Sqnc(test_file_midi)
    
    with open(ref_file_txt, 'r', encoding='utf-8') as f:
        ref_sqnc = ((f.readline())[0:-2]).split(',')
        ref_sqnc = [int(x) for x in ref_sqnc if x]
    
    print(f"\nReference sequence length: {len(ref_sqnc)}")
    print(f"Test sequence length: {len(test_sqnc)}")
    
    if len(ref_sqnc) < 2 or len(test_sqnc) < 2:
        print("Error: Sequences too short for comparison")
        return 0.0
    
    # Extract features
    ref_intervals = extract_melodic_contour(ref_sqnc)
    test_intervals = extract_melodic_contour(test_sqnc)
    
    # Calculate component scores
    contour_score = contour_similarity(ref_intervals, test_intervals)
    print(f"Contour similarity: {contour_score:.2f}/100")
    
    interval_score = interval_pattern_similarity(ref_intervals, test_intervals)
    print(f"Interval pattern similarity: {interval_score:.2f}/100")
    
    pitch_score = pitch_class_similarity(ref_sqnc, test_sqnc)
    print(f"Pitch class similarity: {pitch_score:.2f}/100")
    
    rhythm_score = rhythm_similarity(ref_sqnc, test_sqnc)
    print(f"Rhythm similarity: {rhythm_score:.2f}/100")
    
    # Weighted combination
    final_score = (
        0.30 * contour_score +
        0.30 * interval_score +
        0.20 * pitch_score +
        0.20 * rhythm_score
    )
    
    print(f"\nFinal similarity score: {final_score:.2f}/100")
    
    return final_score
