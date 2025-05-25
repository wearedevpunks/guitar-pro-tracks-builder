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
          const note = beat.notes?.find((n: any) => n.string === stringNumber)
          if (note) {
            lines[s].push({
              fret: note.fret,
              technique: note.technique || note.effect || note.articulation,
              duration: beat.duration || note.duration,
              legato: note.legato || false,
              accent: note.accent || note.accentuated || false,
              velocity: note.velocity || beat.velocity
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
