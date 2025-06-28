import mido
import re
from pathlib import Path

# Load mapping tables
CHORDS = {
    'Q': 72,   # C5
    'W': 74,   # D5
    'E': 76,   # E5
    'R': 77,   # F5
    'T': 79,   # G5
    'Y': 81,   # A5
    'U': 83    # B5
}

MELODY = {
    'A': 60,  # C4
    'S': 62,  # D4
    'D': 64,  # E4
    'F': 65,  # F4
    'G': 67,  # G4
    'H': 69,  # A4
    'J': 71   # B4
}

BASS = {
    'Z': 36,  # C2
    'X': 38,  # D2
    'C': 40,  # E2
    'V': 41,  # F2
    'B': 43,  # G2
    'N': 45,  # A2
    'M': 47   # B2
}

# Configuration
ticks_per_beat = 480
base_bpm       = 120
original_secs  = 79             # original length in seconds
target_secs    = 3 * 60 + 55    # desired length in seconds (3:55)

delay_factor = target_secs / original_secs
tempo = int(mido.bpm2tempo(base_bpm) * delay_factor)

dur_ticks = ticks_per_beat // 4

# Read the token sequence from a text file
# sequence.txt can have tokens separated by '-' or newlines
sequence_path = Path("raw_sequence.txt")
if not sequence_path.exists():
    raise FileNotFoundError(f"Sequence file not found: {sequence_path}")
raw_text = sequence_path.read_text(encoding="utf-8").strip()

# Split on hyphens or any line breaks
tokens = re.split(r'[-\r\n]+', raw_text)
# Filter out any empty tokens
tokens = [t for t in tokens if t]

# Create MIDI file
mid = mido.MidiFile(ticks_per_beat=ticks_per_beat)
track = mido.MidiTrack()
mid.tracks.append(track)

# Set tempo
track.append(mido.MetaMessage('set_tempo', tempo=tempo))

# Build events from tokens
for token in tokens:
    notes_on = []
    for k in token:
        if k in CHORDS:
            notes_on.append(CHORDS[k])
        if k in MELODY:
            notes_on.append(MELODY[k])
        if k in BASS:
            notes_on.append(BASS[k])

    # Note on events
    for note in notes_on:
        track.append(mido.Message('note_on', note=note, velocity=64, time=0))

    # Note off events
    first_off = True
    for note in notes_on:
        track.append(
            mido.Message(
                'note_off', note=note, velocity=64,
                time=(dur_ticks if first_off else 0)
            )
        )
        first_off = False

# Save MIDI file
output_file = 'output_slowdown_fixed.mid'
mid.save(output_file)
print(f"Wrote {output_file} ({target_secs}s target at ~{base_bpm/delay_factor:.2f} BPM eq.)")
