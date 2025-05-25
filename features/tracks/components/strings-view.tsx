import { midiToNoteName } from "../converters"
import { TablatureView, TabNote } from "@/components/ui-extensions"

interface StringsViewProps {
  track: any
}

interface TuningInfo {
  stringNumber: number
  note: string
  midiValue: number
}

export function StringsView({ track }: StringsViewProps) {
  const stringCount = track.strings || track.string_count || 6

  // Get tuning from track data or use default
  const getTuningInfo = (): TuningInfo[] => {
    if (track.tuning && Array.isArray(track.tuning)) {
      return track.tuning.map((tuning: any) => ({
        stringNumber: tuning.string_number,
        note: midiToNoteName(tuning.value),
        midiValue: tuning.value,
      }))
    }
    // Default standard guitar tuning
    return []
  }

  const tuningInfo = getTuningInfo()
  const stringMidiValues =
    tuningInfo.length === stringCount
      ? tuningInfo.map((t) => t.midiValue)
      : undefined

  // Convert track data to tabLines for TablatureView
  function buildTabLines(track: any): TabNote[][] {
    // Initialize tab lines for each string
    const lines: TabNote[][] = Array(stringCount)
      .fill(0)
      .map(() => [])
    
    track.measures.forEach((measure: any) => {
      measure.beats?.forEach((beat: any) => {
        for (let s = 0; s < stringCount; s++) {
          const stringNumber = s + 1
          
          // Find note in any voice for this string
          let foundNote = null
          if (beat.voices && Array.isArray(beat.voices)) {
            for (const voice of beat.voices) {
              if (voice.notes && Array.isArray(voice.notes)) {
                foundNote = voice.notes.find((n: any) => n.string === stringNumber)
                if (foundNote) break
              }
            }
          }
          
          if (foundNote) {
            lines[s].push({
              fret: foundNote.fret,
              technique: foundNote.technique || foundNote.effect || foundNote.articulation,
              duration: beat.duration || foundNote.duration,
              legato: foundNote.legato || false,
              accent: foundNote.accent || false,
              heavy_accent: foundNote.heavy_accent || false,
              velocity: foundNote.velocity,
              muted: foundNote.muted || false,
              ghost: foundNote.ghost || false,
              harmonic: foundNote.harmonic || false,
              palm_mute: foundNote.palm_mute || false,
              staccato: foundNote.staccato || false,
              let_ring: foundNote.let_ring || false,
              vibrato: foundNote.vibrato || false,
              tied: foundNote.tied || false,
              bend_value: foundNote.bend_value,
              slide_type: foundNote.slide_type,
              value: foundNote.value
            })
          } else {
            lines[s].push({ 
              fret: "-",
              duration: beat.duration
            })
          }
        }
      })
      // Add measure separator
      for (let s = 0; s < stringCount; s++) {
        lines[s].push({ fret: "|", isMeasureSeparator: true })
      }
    })
    return lines
  }

  const tabLines = buildTabLines(track)

  if (!track.measures || track.measures.length === 0) {
    return (
      <div className="text-center text-gray-500 dark:text-gray-400 py-12">
        <p>No measures data available for strings visualization</p>
      </div>
    )
  }

  if (!stringMidiValues) {
    return (
      <div className="text-center text-red-500 dark:text-red-400 py-12">
        <p>Missing or invalid tuning information for this track.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Strings Tablature View
        </h3>
        <TablatureView
          stringMidiValues={stringMidiValues}
          tabLines={tabLines}
          tempo={track.tempo}
          timeSignature={track.timeSignature}
        />
      </div>
    </div>
  )
}
