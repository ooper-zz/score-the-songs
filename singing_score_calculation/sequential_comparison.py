# -*- coding: utf-8 -*-
"""
Sequential Melody Comparison Algorithm
Focuses on actual melodic sequence similarity, not just shared patterns
"""

import numpy as np
from music21 import converter
from dtw import dtw
from scipy.stats import pearsonr

def Midi2Sqnc(filepath):
    """Extract MIDI note sequence from file"""
    s = converter.parse(filepath)
    sqnc = []
    for nt in s.recurse():
        if 'Note' in nt.classes:
            sqnc.append(nt.pitch.midi)
    return sqnc

def extract_intervals(midi_sequence):
    """Extract interval sequence (melodic jumps)"""
    if len(midi_sequence) < 2:
        return []
    return [midi_sequence[i] - midi_sequence[i-1] for i in range(1, len(midi_sequence))]

def normalize_sequence(seq):
    """Normalize to mean=0, std=1"""
    if len(seq) == 0:
        return np.array([])
    arr = np.array(seq, dtype=float)
    if np.std(arr) == 0:
        return arr - np.mean(arr)
    return (arr - np.mean(arr)) / np.std(arr)

def dtw_similarity(seq1, seq2):
    """
    Calculate DTW distance and convert to similarity score
    Lower distance = higher similarity
    """
    if len(seq1) < 2 or len(seq2) < 2:
        return 0.0
    
    # Normalize sequences
    norm1 = normalize_sequence(seq1)
    norm2 = normalize_sequence(seq2)
    
    # Calculate DTW distance
    alignment = dtw(norm1, norm2, keep_internals=True)
    distance = alignment.distance
    
    # Normalize by sequence length
    avg_len = (len(seq1) + len(seq2)) / 2
    normalized_distance = distance / avg_len
    
    # Convert to similarity score (0-100)
    # Very strict exponential scoring to amplify small differences
    # d=0.4 -> 100, d=0.45 -> 85, d=0.5 -> 60, d=0.6 -> 30, d=0.7+ -> <10
    if normalized_distance < 0.45:
        score = 100 - (normalized_distance / 0.45) * 15  # 85-100 range
    elif normalized_distance < 0.55:
        score = 85 - ((normalized_distance - 0.45) / 0.10) * 45  # 40-85 range
    elif normalized_distance < 0.70:
        score = 40 - ((normalized_distance - 0.55) / 0.15) * 30  # 10-40 range
    else:
        score = max(0, 10 - (normalized_distance - 0.70) * 20)  # 0-10 range
    
    return score, normalized_distance

def interval_correlation(intervals1, intervals2):
    """
    Calculate Pearson correlation of interval sequences
    Measures if melodies move in similar ways
    """
    if len(intervals1) < 10 or len(intervals2) < 10:
        return 0.0
    
    # Use DTW to align sequences first
    alignment = dtw(np.array(intervals1), np.array(intervals2), keep_internals=True)
    
    # Get aligned sequences
    path = alignment.index1, alignment.index2
    aligned1 = [intervals1[i] for i in path[0]]
    aligned2 = [intervals2[i] for i in path[1]]
    
    # Calculate correlation
    if len(aligned1) < 10:
        return 0.0
    
    try:
        r, p = pearsonr(aligned1, aligned2)
        if p > 0.05:  # Not statistically significant
            return 0.0
        # Convert correlation to 0-100 score
        # Lowered threshold to better discriminate
        if r > 0.5:
            return ((r - 0.5) / 0.5) * 100  # 0-100 for r=0.5 to 1.0
        elif r > 0.3:
            return ((r - 0.3) / 0.2) * 30  # 0-30 for r=0.3 to 0.5
        else:
            return 0.0
    except:
        return 0.0

def contour_similarity(seq1, seq2):
    """
    Compare melodic contours (up/down/same patterns)
    More forgiving than exact intervals
    """
    if len(seq1) < 2 or len(seq2) < 2:
        return 0.0
    
    # Extract contours
    contour1 = [np.sign(seq1[i] - seq1[i-1]) for i in range(1, len(seq1))]
    contour2 = [np.sign(seq2[i] - seq2[i-1]) for i in range(1, len(seq2))]
    
    # Use DTW on contours
    alignment = dtw(np.array(contour1), np.array(contour2), keep_internals=True)
    distance = alignment.distance
    
    # Normalize
    avg_len = (len(contour1) + len(contour2)) / 2
    normalized_distance = distance / avg_len
    
    # Convert to score (contours should match closely for derivatives)
    if normalized_distance < 0.2:
        return 100
    elif normalized_distance < 0.5:
        return 100 - ((normalized_distance - 0.2) / 0.3) * 70  # 30-100
    else:
        return max(0, 30 - (normalized_distance - 0.5) * 30)

def pitch_range_similarity(seq1, seq2):
    """
    Compare pitch ranges - derivatives should have similar ranges
    """
    if len(seq1) == 0 or len(seq2) == 0:
        return 0.0
    
    range1 = max(seq1) - min(seq1)
    range2 = max(seq2) - min(seq2)
    
    if range1 == 0 or range2 == 0:
        return 0.0
    
    ratio = min(range1, range2) / max(range1, range2)
    return ratio * 100

def SequentialMelodyScore(ref_txt, test_midi):
    """
    Sequential melody comparison focusing on actual melodic similarity
    Not fooled by shared patterns or common scales
    """
    print("\n" + "="*60)
    print("SEQUENTIAL MELODY COMPARISON")
    print("="*60)
    
    # Load sequences
    with open(ref_txt, 'r') as f:
        ref_sqnc = [int(x) for x in f.read().strip().rstrip(',').split(',') if x.strip()]
    
    test_sqnc = Midi2Sqnc(test_midi)
    
    print(f"Reference sequence length: {len(ref_sqnc)}")
    print(f"Test sequence length: {len(test_sqnc)}")
    
    if len(ref_sqnc) < 10 or len(test_sqnc) < 10:
        print("Sequences too short for comparison")
        return 0.0
    
    # Extract intervals
    ref_intervals = extract_intervals(ref_sqnc)
    test_intervals = extract_intervals(test_sqnc)
    
    print(f"\n---------------------Component Scores:----------------------")
    
    # 1. DTW on raw pitch sequences (40%)
    pitch_score, pitch_dist = dtw_similarity(ref_sqnc, test_sqnc)
    print(f"Pitch sequence DTW (d={pitch_dist:.3f}): {pitch_score:6.2f}/100")
    
    # 2. DTW on interval sequences (30%)
    interval_score, interval_dist = dtw_similarity(ref_intervals, test_intervals)
    print(f"Interval sequence DTW (d={interval_dist:.3f}): {interval_score:6.2f}/100")
    
    # 3. Interval correlation (20%)
    corr_score = interval_correlation(ref_intervals, test_intervals)
    print(f"Interval correlation (r>0.5):  {corr_score:6.2f}/100")
    
    # 4. Contour similarity (10%)
    contour_score = contour_similarity(ref_sqnc, test_sqnc)
    print(f"Contour similarity:             {contour_score:6.2f}/100")
    
    # 5. Pitch range similarity (5%)
    range_score = pitch_range_similarity(ref_sqnc, test_sqnc)
    print(f"Pitch range similarity:         {range_score:6.2f}/100")
    
    # Weighted combination - interval DTW is the key discriminator
    final_score = (
        0.25 * pitch_score +      # Pitch sequence alignment
        0.50 * interval_score +   # PRIMARY - melodic movement patterns (amplified)
        0.15 * corr_score +       # Statistical correlation
        0.05 * contour_score +    # General direction (too forgiving)
        0.05 * range_score
    )
    
    print(f"\n{'='*60}")
    print(f"FINAL SIMILARITY SCORE: {final_score:6.2f}/100")
    print(f"{'='*60}\n")
    
    return final_score
