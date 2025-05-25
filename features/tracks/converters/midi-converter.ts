/**
 * Convert MIDI note number to note name with octave
 * @param midiNote MIDI note number (0-127)
 * @returns Note name with octave (e.g., "C4", "F#3")
 */
export function midiToNoteName(midiNote: number): string {
  const noteNames = [
    "C",
    "C#",
    "D",
    "D#",
    "E",
    "F",
    "F#",
    "G",
    "G#",
    "A",
    "A#",
    "B",
  ]
  const octave = Math.floor(midiNote / 12) - 1
  const noteIndex = midiNote % 12
  return `${noteNames[noteIndex]}${octave}`
}

/**
 * Convert note name to MIDI note number
 * @param noteName Note name with octave (e.g., "C4", "F#3")
 * @returns MIDI note number (0-127)
 */
export function noteNameToMidi(noteName: string): number {
  const noteMap: Record<string, number> = {
    C: 0,
    "C#": 1,
    DB: 1,
    D: 2,
    "D#": 3,
    EB: 3,
    E: 4,
    F: 5,
    "F#": 6,
    GB: 6,
    G: 7,
    "G#": 8,
    AB: 8,
    A: 9,
    "A#": 10,
    BB: 10,
    B: 11,
  }

  const match = noteName.match(/^([A-G][#B]?)(\d+)$/)
  if (!match) {
    throw new Error(`Invalid note name: ${noteName}`)
  }

  const [, note, octaveStr] = match
  const octave = parseInt(octaveStr, 10)
  const noteValue = noteMap[note.toUpperCase()]

  if (noteValue === undefined) {
    throw new Error(`Invalid note: ${note}`)
  }

  return (octave + 1) * 12 + noteValue
}
