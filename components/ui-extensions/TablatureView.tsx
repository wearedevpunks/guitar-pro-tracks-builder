import { useState } from "react"
import { midiToNoteName } from "@/features/tracks/converters"

export interface TabNote {
  fret: number | string // number for frets, "-" for empty, "|" for measure separator
  technique?: string // "P.M.", "H", "P", "B", "S", etc.
  isMeasureSeparator?: boolean
  duration?: string // "quarter", "eighth", "half", etc.
  tuplet?: { enters: number; times: number } // tuplet information
  legato?: boolean
  accent?: boolean
  heavy_accent?: boolean
  velocity?: number
  muted?: boolean
  ghost?: boolean
  harmonic?: boolean
  palm_mute?: boolean
  staccato?: boolean
  let_ring?: boolean
  vibrato?: boolean
  tied?: boolean
  bend_value?: number | null
  slide_type?: string | null
  value?: number // MIDI note value
}

interface TablatureViewProps {
  stringMidiValues: number[] // MIDI values for each string tuning
  tabLines: TabNote[][] // Array of tab lines, one per string
  tempo?: number
  timeSignature?: string
}

export function TablatureView({
  stringMidiValues,
  tabLines,
  tempo,
  timeSignature
}: TablatureViewProps) {
  const [viewMode, setViewMode] = useState<'horizontal' | 'wrapped'>('horizontal')
  const [measuresPerRow, setMeasuresPerRow] = useState(4)

  const stringNames = stringMidiValues.map(midi => midiToNoteName(midi))
  const stringCount = stringMidiValues.length

  // Calculate positions for wrapping
  const measurePositions: number[] = []
  if (tabLines[0]) {
    tabLines[0].forEach((note, index) => {
      if (note.isMeasureSeparator) {
        measurePositions.push(index)
      }
    })
  }

  const renderTabNote = (note: TabNote, index: string, stringIndex?: number, noteIndex?: number, allNotes?: TabNote[][]) => {
    if (note.isMeasureSeparator) {
      return (
        <div key={index} className="flex items-center px-1">
          <div className="w-px h-12 bg-gray-400 dark:bg-gray-500"></div>
        </div>
      )
    }

    const isPlayed = note.fret !== "-" && note.fret !== ""
    
    // Determine note color based on properties
    const getNoteColor = () => {
      if (note.muted) return 'bg-gray-500'
      if (note.ghost) return 'bg-gray-400 opacity-60'
      if (note.harmonic) return 'bg-yellow-500'
      if (note.palm_mute) return 'bg-orange-500'
      if (note.let_ring) return 'bg-green-500'
      if (note.tied) return 'bg-purple-500'
      if (note.tuplet) return 'bg-cyan-500'
      return 'bg-blue-500'
    }
    
    // Build technique display
    const getTechniques = () => {
      const techniques: string[] = []
      if (note.palm_mute) techniques.push('P.M.')
      if (note.harmonic) techniques.push('H')
      if (note.staccato) techniques.push('.')
      if (note.let_ring) techniques.push('L.R.')
      if (note.vibrato) techniques.push('~')
      if (note.bend_value) techniques.push(`B${note.bend_value}`)
      if (note.slide_type) techniques.push('S')
      if (note.technique) techniques.push(note.technique)
      return techniques.join(' ')
    }

    // Check if this note is part of a tuplet and should show tuplet bracket
    const shouldShowTupletBracket = () => {
      if (!note.tuplet || stringIndex === undefined || noteIndex === undefined || !allNotes) return false
      
      // Show bracket only on the first string for this beat position
      if (stringIndex !== 0) return false
      
      // Find if this is the start of a tuplet group
      const tupletStart = noteIndex
      let tupletCount = 0
      
      // Count consecutive notes with the same tuplet
      for (let i = tupletStart; i < allNotes[0].length && tupletCount < note.tuplet.enters; i++) {
        const currentNote = allNotes[0][i]
        if (currentNote?.tuplet?.enters === note.tuplet.enters && 
            currentNote?.tuplet?.times === note.tuplet.times && 
            !currentNote.isMeasureSeparator) {
          tupletCount++
        } else {
          break
        }
      }
      
      return tupletCount === note.tuplet.enters
    }
    
    return (
      <div key={index} className="relative flex items-center justify-center min-w-[32px] h-12">
        {/* String line */}
        <div className="absolute w-full h-px bg-gray-300 dark:bg-gray-600 top-1/2 transform -translate-y-1/2 z-0"></div>
        
        {/* Tuplet bracket (only shown on first string) */}
        {shouldShowTupletBracket() && note.tuplet && (
          <div className="absolute -top-8 left-0 right-0 z-30">
            <div className="flex items-center justify-center">
              {/* Tuplet bracket */}
              <div 
                className="relative border-t border-l border-r border-red-500"
                style={{ 
                  width: `${note.tuplet.enters * 32}px`,
                  height: '8px'
                }}
              >
                {/* Tuplet number */}
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 text-xs font-bold text-red-600 dark:text-red-400 bg-white dark:bg-gray-800 px-1 rounded">
                  {note.tuplet.enters}:{note.tuplet.times}
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Note or empty space */}
        {isPlayed ? (
          <div className="relative z-10 group">
            {/* Fret number */}
            <div className={`
              ${getNoteColor()} text-white text-xs font-mono rounded-full w-6 h-6 
              flex items-center justify-center relative z-20 transition-all
              ${note.accent ? 'ring-2 ring-red-400' : ''}
              ${note.heavy_accent ? 'ring-2 ring-red-600 ring-offset-1' : ''}
              ${note.ghost ? 'opacity-60' : ''}
            `}>
              {note.fret}
            </div>
            
            {/* Technique markers */}
            {getTechniques() && (
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 text-xs font-mono text-purple-600 dark:text-purple-400 whitespace-nowrap bg-white dark:bg-gray-800 px-1 rounded">
                {getTechniques()}
              </div>
            )}
            
            {/* Duration marker */}
            {note.duration && (
              <div className="absolute -bottom-4 left-1/2 transform -translate-x-1/2 text-xs text-gray-500">
                {getDurationSymbol(note.duration)}
              </div>
            )}
            
            {/* Velocity indicator */}
            {note.velocity && note.velocity !== 79 && (
              <div className="absolute -right-2 -top-1 text-xs text-gray-400 font-mono">
                {note.velocity}
              </div>
            )}
            
            {/* Special effects indicators */}
            {note.tied && (
              <div className="absolute -left-3 top-1/2 transform -translate-y-1/2 text-purple-600">⌐</div>
            )}
          </div>
        ) : (
          <div className="w-2 h-2 bg-gray-200 dark:bg-gray-700 rounded-full relative z-10"></div>
        )}
      </div>
    )
  }

  const renderHorizontalView = () => (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => setViewMode(viewMode === 'horizontal' ? 'wrapped' : 'horizontal')}
            className="px-3 py-1 text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors"
          >
            {viewMode === 'horizontal' ? 'Wrap Rows' : 'Horizontal'}
          </button>
          
          {viewMode === 'wrapped' && (
            <div className="flex items-center gap-2">
              <label className="text-xs text-gray-600 dark:text-gray-400">Measures per row:</label>
              <select
                value={measuresPerRow}
                onChange={(e) => setMeasuresPerRow(Number(e.target.value))}
                className="px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800"
              >
                <option value={2}>2</option>
                <option value={4}>4</option>
                <option value={6}>6</option>
                <option value={8}>8</option>
              </select>
            </div>
          )}
        </div>
        
        {/* Tempo and Time Signature */}
        <div className="flex items-center gap-4 text-sm">
          {tempo && (
            <div className="flex items-center gap-1">
              <span className="text-gray-600 dark:text-gray-400">♩ =</span>
              <span className="font-mono text-gray-900 dark:text-white">{tempo}</span>
            </div>
          )}
          {timeSignature && (
            <div className="flex flex-col items-center leading-none">
              <span className="text-xs font-mono text-gray-900 dark:text-white">{timeSignature.split('/')[0]}</span>
              <span className="text-xs font-mono text-gray-900 dark:text-white">{timeSignature.split('/')[1]}</span>
            </div>
          )}
        </div>
      </div>

      {/* Tablature */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 overflow-x-auto">
        {viewMode === 'horizontal' ? (
          <div className="min-w-max">
            {/* String lines */}
            {Array.from({ length: stringCount }).map((_, stringIndex) => (
              <div key={stringIndex} className="flex items-center mb-4 last:mb-0">
                {/* String label */}
                <div className="w-8 text-right mr-4 text-sm font-mono text-gray-600 dark:text-gray-400 flex-shrink-0">
                  {stringNames[stringIndex]}
                </div>
                
                {/* Tab notes */}
                <div className="flex items-center">
                  {tabLines[stringIndex]?.map((note, noteIndex) => 
                    renderTabNote(note, `horizontal-${stringIndex}-${noteIndex}`, stringIndex, noteIndex, tabLines)
                  )}
                </div>
              </div>
            ))}
            
            {/* Measure numbers */}
            <div className="flex mt-4">
              <div className="w-8 mr-4 flex-shrink-0"></div>
              <div className="flex">
                {measurePositions.map((position, measureIndex) => (
                  <div
                    key={measureIndex}
                    style={{ 
                      marginLeft: measureIndex === 0 ? '0' : 
                        `${(position - (measurePositions[measureIndex - 1] || 0)) * 32 - 32}px` 
                    }}
                    className="text-xs text-gray-500 dark:text-gray-400 text-center min-w-[32px]"
                  >
                    {measureIndex + 1}
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          renderWrappedView()
        )}
      </div>
    </div>
  )

  const renderWrappedView = () => {
    const rows: TabNote[][][] = []
    let currentRow: TabNote[][] = Array(stringCount).fill(0).map(() => [])
    let notesInCurrentRow = 0
    let measuresInCurrentRow = 0

    // Split tab lines into rows
    const maxNotes = Math.max(...tabLines.map(line => line.length))
    
    for (let noteIndex = 0; noteIndex < maxNotes; noteIndex++) {
      for (let stringIndex = 0; stringIndex < stringCount; stringIndex++) {
        const note = tabLines[stringIndex][noteIndex]
        if (note) {
          currentRow[stringIndex].push(note)
        }
      }
      
      notesInCurrentRow++
      
      // Check if this is a measure separator
      const isMeasureSeparator = tabLines[0][noteIndex]?.isMeasureSeparator
      if (isMeasureSeparator) {
        measuresInCurrentRow++
        
        if (measuresInCurrentRow >= measuresPerRow) {
          rows.push(currentRow)
          currentRow = Array(stringCount).fill(0).map(() => [])
          notesInCurrentRow = 0
          measuresInCurrentRow = 0
        }
      }
    }
    
    // Add remaining notes to last row
    if (notesInCurrentRow > 0) {
      rows.push(currentRow)
    }

    return (
      <div className="space-y-12">
        {rows.map((row, rowIndex) => (
          <div key={rowIndex} className="relative">
            {/* Row separator line (except for first row) */}
            {rowIndex > 0 && (
              <div className="absolute -top-6 left-0 right-0 border-t border-gray-300 dark:border-gray-600"></div>
            )}
            
            {/* Row number indicator */}
            <div className="absolute -left-8 top-1/2 transform -translate-y-1/2 text-xs font-mono text-gray-400 dark:text-gray-500 bg-white dark:bg-gray-800 px-1">
              {rowIndex + 1}
            </div>
            
            {/* Tablature content */}
            <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
              <div className="min-w-max">
                {/* String lines for this row */}
                {Array.from({ length: stringCount }).map((_, stringIndex) => (
                  <div key={stringIndex} className="flex items-center mb-4 last:mb-0">
                    {/* String label */}
                    <div className="w-8 text-right mr-4 text-sm font-mono text-gray-600 dark:text-gray-400 flex-shrink-0 font-medium">
                      {stringNames[stringIndex]}
                    </div>
                    
                    {/* Tab notes for this row */}
                    <div className="flex items-center">
                      {row[stringIndex]?.map((note, noteIndex) => 
                        renderTabNote(note, `${rowIndex}-${stringIndex}-${noteIndex}`, stringIndex, noteIndex, row)
                      )}
                    </div>
                  </div>
                ))}
                
                {/* Measure numbers for this row */}
                <div className="flex mt-4 pt-2 border-t border-gray-200 dark:border-gray-600">
                  <div className="w-8 mr-4 flex-shrink-0"></div>
                  <div className="flex items-center gap-4">
                    {/* Calculate measure numbers for this row */}
                    {(() => {
                      const measuresInThisRow: number[] = []
                      let measureCount = 0
                      
                      row[0]?.forEach((note) => {
                        if (note.isMeasureSeparator) {
                          measureCount++
                          measuresInThisRow.push(rowIndex * measuresPerRow + measureCount)
                        }
                      })
                      
                      return measuresInThisRow.map((measureNum, index) => (
                        <div key={index} className="text-xs font-mono text-gray-500 dark:text-gray-400 bg-white dark:bg-gray-700 px-2 py-1 rounded border">
                          M{measureNum}
                        </div>
                      ))
                    })()}
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  return renderHorizontalView()
}

function getDurationSymbol(duration: string): string {
  const symbols: Record<string, string> = {
    'whole': '𝅝',
    'half': '𝅗𝅥',
    'quarter': '♩',
    'eighth': '♫',
    'sixteenth': '♬',
    'thirty-second': '♬'
  }
  return symbols[duration] || '♩'
}