# -*- coding: utf-8 -*-
"""
Strict Melody Comparison Algorithm
Much more discriminative - focuses on exact melodic patterns
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

def extract_contour(intervals):
    """Extract contour: -1 (down), 0 (same), 1 (up)"""
    return [np.sign(i) for i in intervals]

def normalize_sequence(seq):
    """Normalize to mean=0, std=1"""
    if len(seq) == 0:
        return np.array([])
    arr = np.array(seq, dtype=float)
    if np.std(arr) == 0:
        return arr - np.mean(arr)
    return (arr - np.mean(arr)) / np.std(arr)

def exact_contour_match(contour1, contour2):
    """
    Strict contour matching - requires exact directional patterns
    Uses sliding window to find best local match
    """
    if len(contour1) == 0 or len(contour2) == 0:
        return 0.0
    
    # Convert to numpy arrays
    c1 = np.array(contour1)
    c2 = np.array(contour2)
    
    # Try both directions (in case one is reversed)
    max_match = 0.0
    
    # Use shorter sequence as pattern
    if len(c1) <= len(c2):
        pattern = c1
        target = c2
    else:
        pattern = c2
        target = c1
    
    # Sliding window to find best match
    pattern_len = len(pattern)
    target_len = len(target)
    
    if pattern_len > target_len:
        # If pattern is longer, use DTW
        alignment = dtw(c1.reshape(-1, 1), c2.reshape(-1, 1), keep_internals=True)
        dist = alignment.distance
        max_possible = max(len(c1), len(c2)) * 2
        match_score = max(0, 100 * (1 - dist / max_possible))
        return match_score
    
    # Slide pattern over target
    for i in range(target_len - pattern_len + 1):
        window = target[i:i + pattern_len]
        matches = np.sum(pattern == window)
        match_ratio = matches / pattern_len
        max_match = max(max_match, match_ratio)
    
    return max_match * 100

def interval_correlation(intervals1, intervals2):
    """
    Calculate correlation between interval sequences
    High correlation = similar melodic movement patterns
    """
    if len(intervals1) < 3 or len(intervals2) < 3:
        return 0.0
    
    # Normalize intervals
    norm1 = normalize_sequence(intervals1)
    norm2 = normalize_sequence(intervals2)
    
    # Use DTW to align, then calculate correlation on aligned sequences
    alignment = dtw(norm1.reshape(-1, 1), norm2.reshape(-1, 1), keep_internals=True)
    
    # Get aligned indices
    idx1 = alignment.index1
    idx2 = alignment.index2
    
    # Extract aligned values
    aligned1 = norm1[idx1]
    aligned2 = norm2[idx2]
    
    # Calculate correlation
    if len(aligned1) > 1:
        corr, _ = pearsonr(aligned1, aligned2)
        if np.isnan(corr):
            corr = 0
    else:
        corr = 0
    
    # Convert to 0-100 scale (only positive correlations count)
    score = max(0, corr) * 100
    return score

def exact_interval_match(intervals1, intervals2):
    """
    Count exact interval matches using sliding window
    Very strict - intervals must match exactly (within 1 semitone)
    """
    if len(intervals1) == 0 or len(intervals2) == 0:
        return 0.0
    
    # Use shorter as pattern
    if len(intervals1) <= len(intervals2):
        pattern = intervals1
        target = intervals2
    else:
        pattern = intervals2
        target = intervals1
    
    pattern_len = len(pattern)
    target_len = len(target)
    
    if pattern_len > target_len:
        return 0.0
    
    max_matches = 0
    
    # Slide pattern over target
    for i in range(target_len - pattern_len + 1):
        window = target[i:i + pattern_len]
        # Count intervals that match within 1 semitone
        matches = sum(1 for p, w in zip(pattern, window) if abs(p - w) <= 1)
        max_matches = max(max_matches, matches)
    
    match_ratio = max_matches / pattern_len
    return match_ratio * 100

def pitch_class_histogram_similarity(midi_seq1, midi_seq2):
    """
    Compare pitch class usage (what notes are used)
    Uses histogram intersection
    """
    if len(midi_seq1) == 0 or len(midi_seq2) == 0:
        return 0.0
    
    # Create pitch class histograms (0-11)
    hist1 = np.zeros(12)
    hist2 = np.zeros(12)
    
    for note in midi_seq1:
        hist1[note % 12] += 1
    for note in midi_seq2:
        hist2[note % 12] += 1
    
    # Normalize
    hist1 = hist1 / np.sum(hist1)
    hist2 = hist2 / np.sum(hist2)
    
    # Histogram intersection (strict)
    intersection = np.sum(np.minimum(hist1, hist2))
    
    return intersection * 100

def melodic_range_similarity(midi_seq1, midi_seq2):
    """
    Compare melodic range (ambitus)
    """
    if len(midi_seq1) == 0 or len(midi_seq2) == 0:
        return 0.0
    
    range1 = max(midi_seq1) - min(midi_seq1)
    range2 = max(midi_seq2) - min(midi_seq2)
    
    if range1 == 0 or range2 == 0:
        return 0.0
    
    # Similarity based on range ratio
    ratio = min(range1, range2) / max(range1, range2)
    return ratio * 100

def note_density_similarity(midi_seq1, midi_seq2):
    """
    Compare note density (number of notes)
    """
    len1 = len(midi_seq1)
    len2 = len(midi_seq2)
    
    if len1 == 0 or len2 == 0:
        return 0.0
    
    ratio = min(len1, len2) / max(len1, len2)
    return ratio * 100

def StrictMelodyScore(ref_file_txt, test_file_midi):
    """
    Strict melody comparison with much higher discrimination
    
    Scoring components (all must score well for high overall score):
    - 25% Exact contour matching (directional patterns)
    - 25% Interval correlation (melodic movement similarity)
    - 20% Exact interval matching (precise melodic jumps)
    - 15% Pitch class histogram (note usage)
    - 10% Melodic range similarity
    - 5% Note density similarity
    
    Returns: similarity score 0-100
    """
    
    # Load sequences
    test_sqnc = Midi2Sqnc(test_file_midi)
    
    with open(ref_file_txt, 'r', encoding='utf-8') as f:
        ref_sqnc = ((f.readline())[0:-2]).split(',')
        ref_sqnc = [int(x) for x in ref_sqnc if x]
    
    print(f"\n{'='*60}")
    print(f"STRICT MELODY COMPARISON")
    print(f"{'='*60}")
    print(f"Reference sequence length: {len(ref_sqnc)}")
    print(f"Test sequence length: {len(test_sqnc)}")
    
    if len(ref_sqnc) < 2 or len(test_sqnc) < 2:
        print("Error: Sequences too short for comparison")
        return 0.0
    
    # Extract features
    ref_intervals = extract_intervals(ref_sqnc)
    test_intervals = extract_intervals(test_sqnc)
    
    ref_contour = extract_contour(ref_intervals)
    test_contour = extract_contour(test_intervals)
    
    # Calculate component scores
    print(f"\n{'Component Scores:':-^60}")
    
    contour_score = exact_contour_match(ref_contour, test_contour)
    print(f"Exact contour match:        {contour_score:6.2f}/100")
    
    correlation_score = interval_correlation(ref_intervals, test_intervals)
    print(f"Interval correlation:       {correlation_score:6.2f}/100")
    
    exact_match_score = exact_interval_match(ref_intervals, test_intervals)
    print(f"Exact interval matching:    {exact_match_score:6.2f}/100")
    
    pitch_score = pitch_class_histogram_similarity(ref_sqnc, test_sqnc)
    print(f"Pitch class similarity:     {pitch_score:6.2f}/100")
    
    range_score = melodic_range_similarity(ref_sqnc, test_sqnc)
    print(f"Melodic range similarity:   {range_score:6.2f}/100")
    
    density_score = note_density_similarity(ref_sqnc, test_sqnc)
    print(f"Note density similarity:    {density_score:6.2f}/100")
    
    # Weighted combination with stricter weighting
    final_score = (
        0.25 * contour_score +
        0.25 * correlation_score +
        0.20 * exact_match_score +
        0.15 * pitch_score +
        0.10 * range_score +
        0.05 * density_score
    )
    
    # Apply penalty for very different lengths
    length_ratio = min(len(ref_sqnc), len(test_sqnc)) / max(len(ref_sqnc), len(test_sqnc))
    if length_ratio < 0.5:
        length_penalty = length_ratio * 0.5  # Up to 50% penalty
        final_score *= (0.5 + length_penalty)
        print(f"\nLength penalty applied: {(1 - (0.5 + length_penalty)) * 100:.1f}%")
    
    print(f"\n{'='*60}")
    print(f"FINAL SIMILARITY SCORE: {final_score:6.2f}/100")
    print(f"{'='*60}\n")
    
    return final_score
