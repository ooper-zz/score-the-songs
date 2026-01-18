# -*- coding: utf-8 -*-
"""
Ultra-Strict Melody Comparison Algorithm
Maximum discrimination between similar and different melodies
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

def longest_common_subsequence(seq1, seq2, tolerance=0):
    """
    Find longest common subsequence with tolerance
    Very strict - requires exact or near-exact matches
    """
    m, n = len(seq1), len(seq2)
    
    # Create DP table
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if abs(seq1[i-1] - seq2[j-1]) <= tolerance:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    lcs_length = dp[m][n]
    max_possible = max(m, n)
    
    return (lcs_length / max_possible) * 100 if max_possible > 0 else 0

def exact_pattern_match(pattern, target, max_gap=2):
    """
    Find exact pattern matches in target with minimal gaps
    Returns percentage of pattern that matches consecutively
    """
    if len(pattern) == 0 or len(target) == 0:
        return 0.0
    
    best_match = 0
    
    for i in range(len(target) - len(pattern) + 1):
        matches = 0
        gaps = 0
        
        for j in range(len(pattern)):
            if i + j < len(target):
                if pattern[j] == target[i + j]:
                    matches += 1
                else:
                    gaps += 1
                    if gaps > max_gap:
                        break
        
        match_ratio = matches / len(pattern)
        best_match = max(best_match, match_ratio)
    
    return best_match * 100

def interval_sequence_correlation(intervals1, intervals2):
    """
    Strict correlation - only counts if correlation is very high
    """
    if len(intervals1) < 5 or len(intervals2) < 5:
        return 0.0
    
    # Normalize
    norm1 = normalize_sequence(intervals1)
    norm2 = normalize_sequence(intervals2)
    
    # Use DTW to align
    alignment = dtw(norm1.reshape(-1, 1), norm2.reshape(-1, 1), keep_internals=True)
    
    # Get aligned indices
    idx1 = alignment.index1
    idx2 = alignment.index2
    
    # Extract aligned values
    aligned1 = norm1[idx1]
    aligned2 = norm2[idx2]
    
    # Calculate correlation
    if len(aligned1) > 1:
        corr, pval = pearsonr(aligned1, aligned2)
        if np.isnan(corr) or pval > 0.05:  # Require statistical significance
            corr = 0
    else:
        corr = 0
    
    # Only positive correlations count, and apply stricter threshold
    if corr < 0.5:  # Require at least moderate correlation
        return 0
    
    # Scale from 0.5-1.0 to 0-100
    score = ((corr - 0.5) / 0.5) * 100
    return score

def melodic_motif_similarity(intervals1, intervals2):
    """
    Find repeated melodic motifs (3-5 note patterns)
    Checks if similar short patterns appear in both melodies
    """
    if len(intervals1) < 3 or len(intervals2) < 3:
        return 0.0
    
    # Extract all 3-note motifs
    motifs1 = []
    motifs2 = []
    
    for i in range(len(intervals1) - 2):
        motifs1.append(tuple(intervals1[i:i+3]))
    
    for i in range(len(intervals2) - 2):
        motifs2.append(tuple(intervals2[i:i+3]))
    
    if not motifs1 or not motifs2:
        return 0.0
    
    # Find matching motifs (exact or within 1 semitone per note)
    matches = 0
    for m1 in motifs1:
        for m2 in motifs2:
            if all(abs(a - b) <= 1 for a, b in zip(m1, m2)):
                matches += 1
                break
    
    # Normalize by number of motifs
    match_ratio = matches / len(motifs1)
    
    return match_ratio * 100

def pitch_class_overlap(midi_seq1, midi_seq2):
    """
    Strict pitch class overlap - requires significant shared notes
    """
    if len(midi_seq1) == 0 or len(midi_seq2) == 0:
        return 0.0
    
    # Get unique pitch classes
    pc1 = set([note % 12 for note in midi_seq1])
    pc2 = set([note % 12 for note in midi_seq2])
    
    # Calculate Jaccard similarity (intersection / union)
    intersection = len(pc1 & pc2)
    union = len(pc1 | pc2)
    
    if union == 0:
        return 0.0
    
    jaccard = intersection / union
    
    # Require at least 50% overlap
    if jaccard < 0.5:
        return 0
    
    # Scale from 0.5-1.0 to 0-100
    score = ((jaccard - 0.5) / 0.5) * 100
    return score

def UltraStrictMelodyScore(ref_file_txt, test_file_midi):
    """
    Ultra-strict melody comparison with maximum discrimination
    
    Scoring components (all weighted heavily toward exact matches):
    - 30% Longest common subsequence (exact interval matches)
    - 25% Interval sequence correlation (requires r > 0.5, p < 0.05)
    - 20% Exact pattern matching (consecutive matches)
    - 15% Melodic motif similarity (3-note patterns)
    - 10% Pitch class overlap (Jaccard > 0.5)
    
    Returns: similarity score 0-100
    """
    
    # Load sequences
    test_sqnc = Midi2Sqnc(test_file_midi)
    
    with open(ref_file_txt, 'r', encoding='utf-8') as f:
        ref_sqnc = ((f.readline())[0:-2]).split(',')
        ref_sqnc = [int(x) for x in ref_sqnc if x]
    
    print(f"\n{'='*60}")
    print(f"ULTRA-STRICT MELODY COMPARISON")
    print(f"{'='*60}")
    print(f"Reference sequence length: {len(ref_sqnc)}")
    print(f"Test sequence length: {len(test_sqnc)}")
    
    if len(ref_sqnc) < 3 or len(test_sqnc) < 3:
        print("Error: Sequences too short for comparison")
        return 0.0
    
    # Extract features
    ref_intervals = extract_intervals(ref_sqnc)
    test_intervals = extract_intervals(test_sqnc)
    
    ref_contour = extract_contour(ref_intervals)
    test_contour = extract_contour(test_intervals)
    
    # Calculate component scores
    print(f"\n{'Component Scores:':-^60}")
    
    # LCS of intervals (exact matches)
    lcs_score = longest_common_subsequence(ref_intervals, test_intervals, tolerance=1)
    print(f"Longest common subsequence: {lcs_score:6.2f}/100")
    
    # Correlation (strict)
    correlation_score = interval_sequence_correlation(ref_intervals, test_intervals)
    print(f"Interval correlation (r>0.5): {correlation_score:6.2f}/100")
    
    # Exact pattern matching
    pattern_score = exact_pattern_match(ref_contour, test_contour, max_gap=2)
    print(f"Exact pattern matching:     {pattern_score:6.2f}/100")
    
    # Melodic motifs
    motif_score = melodic_motif_similarity(ref_intervals, test_intervals)
    print(f"Melodic motif similarity:   {motif_score:6.2f}/100")
    
    # Pitch class overlap
    pc_score = pitch_class_overlap(ref_sqnc, test_sqnc)
    print(f"Pitch class overlap (J>0.5): {pc_score:6.2f}/100")
    
    # Weighted combination - prioritize motif and pitch class as they're most reliable
    final_score = (
        0.25 * lcs_score +
        0.15 * correlation_score +  # Reduced weight - can be unreliable with length differences
        0.15 * pattern_score +
        0.30 * motif_score +  # Increased - very reliable for melody matching
        0.15 * pc_score  # Increased - reliable indicator
    )
    
    # Apply length penalty only for very different lengths
    length_ratio = min(len(ref_sqnc), len(test_sqnc)) / max(len(ref_sqnc), len(test_sqnc))
    if length_ratio < 0.5:  # Only penalize if less than 50% match
        length_penalty = (length_ratio - 0.5) / 0.5  # Up to 100% penalty
        final_score *= (1 + length_penalty)
        print(f"\nLength penalty applied: {-length_penalty * 100:.1f}%")
    
    # Apply minimum threshold - but only penalize if multiple critical components are zero
    # Don't penalize if just correlation is zero (can happen with length differences)
    critical_zeros = sum([
        lcs_score == 0,
        pattern_score == 0,
        motif_score == 0,
        pc_score == 0
    ])
    
    if critical_zeros > 1:  # Only penalize if 2+ critical components are zero
        zero_penalty = critical_zeros * 0.10  # 10% penalty per zero component
        final_score *= (1 - zero_penalty)
        print(f"Zero component penalty: {zero_penalty * 100:.1f}%")
    
    print(f"\n{'='*60}")
    print(f"FINAL SIMILARITY SCORE: {final_score:6.2f}/100")
    print(f"{'='*60}\n")
    
    return final_score
