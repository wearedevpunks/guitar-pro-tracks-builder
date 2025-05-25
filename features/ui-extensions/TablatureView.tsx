import React from "react"
import { midiToNoteName } from "../tracks/converters"

export interface TabNote {
  fret: string | number
  technique?: string // e.g., "P.M.", "H", "P"
  isMeasureSeparator?: boolean
}

export interface TablatureViewProps {
  /**
   * Either stringNames (already converted, e.g. ["E2", ...]) or stringMidiValues (MIDI numbers) must be provided.
   * If both are provided, stringNames takes precedence.
   */
  stringNames?: string[]
  stringMidiValues?: number[]
  tabLines: TabNote[][] // tabLines[stringIndex][position] = TabNote
}

export const TablatureView: React.FC<TablatureViewProps> = ({
  stringNames,
  stringMidiValues,
  tabLines,
}) => {
  // Require either stringNames or stringMidiValues
  let labels: string[] = []
  if (stringNames && stringNames.length === tabLines.length) {
    labels = stringNames
  } else if (stringMidiValues && stringMidiValues.length === tabLines.length) {
    labels = stringMidiValues.map(midiToNoteName)
  } else {
    // Neither provided or length mismatch: render nothing
    if (process.env.NODE_ENV !== "production") {
      // eslint-disable-next-line no-console
      console.error(
        "TablatureView: You must provide either stringNames or stringMidiValues, matching tabLines.length."
      )
    }
    return null
  }

  // Build technique lines (above each string)
  const techniqueLines = tabLines.map((line) =>
    line.map((note) => (note.isMeasureSeparator ? "|" : note.technique || " "))
  )

  // Build fret lines (main tab)
  const fretLines = tabLines.map((line) =>
    line.map((note) => (note.isMeasureSeparator ? "|" : note.fret ?? "-"))
  )

  return (
    <div className="bg-gray-900 text-gray-100 rounded-lg p-4 font-mono overflow-x-auto border border-gray-700">
      <pre className="text-xs leading-5">
        {tabLines.map((_, i) => (
          <React.Fragment key={i}>
            {/* Technique line */}
            <span style={{ color: "#a3a3a3" }}>
              {techniqueLines[i].join(" ")}
            </span>
            {"\n"}
            {/* String line */}
            <span style={{ color: "#facc15" }}>{labels[i]}</span>
            {"|"}
            {fretLines[i].join(" ")}
            {"\n"}
          </React.Fragment>
        ))}
      </pre>
    </div>
  )
}
