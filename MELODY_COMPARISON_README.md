# Melody Comparison Tool - Suno Validator

A DTW-based melody comparison tool for validating Suno AI's melody adherence.

## Features

- **Sequential DTW Algorithm**: Compares melodic sequences using Dynamic Time Warping
- **AI Stem Separation**: Optional Demucs integration (fast/quality modes)
- **Clear Match Levels**: STRONG MATCH, MATCH, UNCERTAIN, NO MATCH
- **No Modal Dialogs**: Clean UI with status updates only
- **Detailed Terminal Output**: Component breakdowns for analysis

## Quick Start

```bash
./run_melody_compare.sh
```

Or use the alias (after opening new terminal):
```bash
melody-compare
```

## Match Level Thresholds

- **60+**: STRONG MATCH - Strong derivative detected
- **50-59**: MATCH - Likely derivative
- **35-49**: UNCERTAIN - Manual review needed
- **<35**: NO MATCH - Different melodies

## Test Results

- **Perfect match** (same file): 100.00/100
- **Derivative**: 52.95/100 → MATCH ✓
- **Non-match**: 31.42/100 → NO MATCH ✓

## Algorithm Components

1. **Pitch Sequence DTW** (25%) - Raw pitch alignment
2. **Interval Sequence DTW** (50%) - Melodic movement patterns (primary discriminator)
3. **Interval Correlation** (15%) - Statistical similarity (r>0.5)
4. **Contour Similarity** (10%) - Up/down patterns
5. **Pitch Range** (5%) - Vocal/melodic range similarity

## Stem Separation Options

- **Fast Mode** (~15-30s): htdemucs model
- **Quality Mode** (~60-120s): mdx_extra model

Check boxes to stem reference file, test file, or both.

## Files

- `melody_compare_simple.py` - Main UI application
- `sequential_comparison.py` - DTW-based scoring algorithm
- `run_melody_compare.sh` - Launch script
- `ultra_strict_comparison.py` - Previous pattern-based algorithm (not used)

## Technical Details

The algorithm uses exponential DTW scoring to amplify small differences in melodic distance:
- d=0.45 → 85-100 points
- d=0.55 → 40-85 points
- d=0.70 → 10-40 points
- d>0.70 → <10 points

This creates clear separation between derivatives and non-matches.

## Dependencies

- Python 3.13
- aubio (melody extraction)
- music21 (MIDI processing)
- dtw-python (Dynamic Time Warping)
- demucs (optional stem separation)
- pydub, numpy, scipy

Install with:
```bash
pip install -r requirements.txt
```

## Credits

Original pitch detection system by Xue Qinliang and team.
Melody comparison algorithm and UI by Cascade AI.
