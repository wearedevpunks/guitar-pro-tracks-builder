import { useState } from "react"

interface TrackEditorProps {
  parsedData: any // Will be properly typed when we know the parsed data structure
  onClose: () => void
}

export function TrackEditor({ parsedData, onClose }: TrackEditorProps) {
  const [selectedTrack, setSelectedTrack] = useState<number | null>(null)

  const handleTrackSelect = (trackIndex: number) => {
    setSelectedTrack(selectedTrack === trackIndex ? null : trackIndex)
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-[98vw] h-[98vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
          <div>
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">
              Track Visualizer
            </h1>
            <p className="text-sm text-gray-600 dark:text-gray-300">
              Guitar Pro Track Analysis & Measures
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5 text-gray-600 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden flex">
          {parsedData ? (
            <>
              {/* Left Sidebar - Track List */}
              <div className="w-80 border-r border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 overflow-y-auto">
                <div className="p-4">
                  {/* Song Info */}
                  <div className="mb-6">
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">Song Info</h2>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div className="bg-white dark:bg-gray-800 p-2 rounded">
                        <span className="text-gray-600 dark:text-gray-400">Tracks:</span>
                        <div className="font-bold text-blue-600 dark:text-blue-400">
                          {parsedData.tracks?.length || 0}
                        </div>
                      </div>
                      <div className="bg-white dark:bg-gray-800 p-2 rounded">
                        <span className="text-gray-600 dark:text-gray-400">Tempo:</span>
                        <div className="font-bold text-green-600 dark:text-green-400">
                          {parsedData.tempo || 'N/A'}
                        </div>
                      </div>
                      <div className="bg-white dark:bg-gray-800 p-2 rounded">
                        <span className="text-gray-600 dark:text-gray-400">Time:</span>
                        <div className="font-bold text-purple-600 dark:text-purple-400">
                          {parsedData.timeSignature || 'N/A'}
                        </div>
                      </div>
                      <div className="bg-white dark:bg-gray-800 p-2 rounded">
                        <span className="text-gray-600 dark:text-gray-400">Measures:</span>
                        <div className="font-bold text-orange-600 dark:text-orange-400">
                          {parsedData.measureCount || 'N/A'}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Track List */}
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">Tracks</h2>
                    <div className="space-y-2">
                      {parsedData.tracks?.map((track: any, index: number) => (
                        <button
                          key={index}
                          onClick={() => handleTrackSelect(index)}
                          className={`w-full text-left p-3 rounded-lg border transition-colors ${
                            selectedTrack === index
                              ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-700'
                              : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700'
                          }`}
                        >
                          <div className="flex items-center justify-between mb-1">
                            <h3 className="font-medium text-gray-900 dark:text-white text-sm">
                              {track.name || `Track ${index + 1}`}
                            </h3>
                            <span className="text-xs text-gray-500 dark:text-gray-400">
                              {track.measures?.length || 0} measures
                            </span>
                          </div>
                          <p className="text-xs text-gray-600 dark:text-gray-400">
                            {track.instrument || 'Unknown'} • {track.strings || 'N/A'} strings
                          </p>
                          <div className="flex justify-between mt-1 text-xs text-gray-500 dark:text-gray-400">
                            <span>Ch: {track.channel || 'N/A'}</span>
                            <span>Notes: {track.noteCount || 'N/A'}</span>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Main Content - Track Details */}
              <div className="flex-1 overflow-y-auto">
                {selectedTrack !== null && parsedData.tracks?.[selectedTrack] ? (
                  <TrackDetails track={parsedData.tracks[selectedTrack]} trackIndex={selectedTrack} />
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center text-gray-500 dark:text-gray-400">
                      <div className="mb-4">
                        <svg className="mx-auto h-16 w-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                        </svg>
                      </div>
                      <p className="text-lg font-medium mb-2">Select a Track</p>
                      <p className="text-sm">
                        Choose a track from the left panel to view its measures and details
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="flex items-center justify-center w-full">
              <div className="text-center text-gray-500 dark:text-gray-400">
                <div className="mb-4">
                  <svg className="mx-auto h-16 w-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                  </svg>
                </div>
                <p className="text-lg font-medium mb-2">No Track Data Available</p>
                <p className="text-sm">
                  The parsed track data will be displayed here once available
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end p-4 border-t border-gray-200 dark:border-gray-700 flex-shrink-0">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-300 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-400 dark:hover:bg-gray-500 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

type VisualizationType = 'measures' | 'strings' | 'notes' | 'json'

interface TrackDetailsProps {
  track: any
  trackIndex: number
}

function TrackDetails({ track, trackIndex }: TrackDetailsProps) {
  const [activeView, setActiveView] = useState<VisualizationType>('strings')

  const tabs = [
    { id: 'strings' as const, label: 'Strings', icon: '🎸' },
    { id: 'measures' as const, label: 'Measures', icon: '📏' },
    { id: 'notes' as const, label: 'Note Details', icon: '🎵' },
    { id: 'json' as const, label: 'JSON', icon: '📋' }
  ]

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          {track.name || `Track ${trackIndex + 1}`}
        </h2>
        <div className="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-gray-400">
          <span>Instrument: {track.instrument || 'Unknown'}</span>
          <span>Strings: {track.strings || 'N/A'}</span>
          <span>Channel: {track.channel || 'N/A'}</span>
          <span>Notes: {track.noteCount || 'N/A'}</span>
        </div>
      </div>

      {/* Visualization Tabs */}
      <div className="mb-6">
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveView(tab.id)}
                className={`whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${
                  activeView === tab.id
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                <span>{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Visualization Content */}
      <div className="min-h-[400px]">
        {activeView === 'strings' && <GuitarStringsView track={track} />}
        {activeView === 'measures' && <MeasuresView track={track} />}
        {activeView === 'notes' && <NotesView track={track} />}
        {activeView === 'json' && <JsonView track={track} />}
      </div>
    </div>
  )
}

interface ViewProps {
  track: any
}

function GuitarStringsView({ track }: ViewProps) {
  const stringCount = track.strings || 6
  const stringNames = ['E', 'A', 'D', 'G', 'B', 'E'] // Standard guitar tuning
  
  if (!track.measures || track.measures.length === 0) {
    return (
      <div className="text-center text-gray-500 dark:text-gray-400 py-12">
        <p>No measures data available for strings visualization</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Strings Tablature View
        </h3>
        
        <div className="overflow-x-auto">
          <div className="min-w-max">
            {/* String lines */}
            <div className="relative">
              {Array.from({ length: stringCount }).map((_, stringIndex) => {
                const stringNumber = stringIndex + 1
                const stringName = stringNames[stringIndex] || `S${stringNumber}`
                
                return (
                  <div key={stringIndex} className="flex items-center mb-4">
                    {/* String label */}
                    <div className="w-8 text-right mr-4 text-sm font-mono text-gray-600 dark:text-gray-400">
                      {stringName}
                    </div>
                    
                    {/* String line with fret numbers */}
                    <div className="flex-1 relative">
                      <div className="h-px bg-gray-300 dark:bg-gray-600 absolute top-3 left-0 right-0"></div>
                      <div className="flex">
                        {track.measures.map((measure: any, measureIndex: number) => (
                          <div key={measureIndex} className="flex border-r border-gray-200 dark:border-gray-700">
                            {measure.beats?.map((beat: any, beatIndex: number) => {
                              const noteOnString = beat.notes?.find((note: any) => note.string === stringNumber)
                              return (
                                <div key={beatIndex} className="w-12 h-6 flex items-center justify-center relative">
                                  {noteOnString ? (
                                    <div className="bg-blue-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center font-mono relative z-10">
                                      {noteOnString.fret !== undefined ? noteOnString.fret : '?'}
                                    </div>
                                  ) : (
                                    <div className="w-6 h-6 flex items-center justify-center">
                                      <div className="w-1 h-1 bg-gray-300 dark:bg-gray-600 rounded-full"></div>
                                    </div>
                                  )}
                                </div>
                              )
                            }) || (
                              <div className="w-12 h-6 flex items-center justify-center">
                                <div className="w-1 h-1 bg-gray-300 dark:bg-gray-600 rounded-full"></div>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
            
            {/* Measure numbers */}
            <div className="flex mt-4">
              <div className="w-8 mr-4"></div>
              <div className="flex-1">
                <div className="flex">
                  {track.measures.map((_: any, measureIndex: number) => (
                    <div key={measureIndex} className="border-r border-gray-200 dark:border-gray-700">
                      <div className="text-xs text-gray-500 dark:text-gray-400 text-center p-2">
                        M{measureIndex + 1}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function MeasuresView({ track }: ViewProps) {
  if (!track.measures || track.measures.length === 0) {
    return (
      <div className="text-center text-gray-500 dark:text-gray-400 py-12">
        <p>No measures data available for this track</p>
      </div>
    )
  }

  return (
    <div>
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Measures ({track.measures.length})
      </h3>
      <div className="grid gap-4">
        {track.measures.map((measure: any, measureIndex: number) => (
          <div key={measureIndex} className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-medium text-gray-900 dark:text-white">
                Measure {measureIndex + 1}
              </h4>
              <div className="flex gap-2 text-xs text-gray-500 dark:text-gray-400">
                {measure.timeSignature && (
                  <span>Time: {measure.timeSignature}</span>
                )}
                {measure.keySignature !== undefined && (
                  <span>Key: {measure.keySignature}</span>
                )}
              </div>
            </div>

            {/* Beats/Notes in measure */}
            {measure.beats && measure.beats.length > 0 && (
              <div>
                <h5 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Beats ({measure.beats.length})
                </h5>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-2">
                  {measure.beats.map((beat: any, beatIndex: number) => (
                    <div key={beatIndex} className="bg-gray-50 dark:bg-gray-700 rounded p-2 text-xs">
                      <div className="font-medium text-gray-900 dark:text-white mb-1">
                        Beat {beatIndex + 1}
                      </div>
                      {beat.notes && beat.notes.length > 0 && (
                        <div className="space-y-1">
                          {beat.notes.map((note: any, noteIndex: number) => (
                            <div key={noteIndex} className="flex justify-between text-gray-600 dark:text-gray-400">
                              <span>String {note.string || 'N/A'}</span>
                              <span>Fret {note.fret !== undefined ? note.fret : 'N/A'}</span>
                            </div>
                          ))}
                        </div>
                      )}
                      {beat.duration && (
                        <div className="mt-1 text-gray-500 dark:text-gray-500">
                          Duration: {beat.duration}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

function NotesView({ track }: ViewProps) {
  if (!track.measures || track.measures.length === 0) {
    return (
      <div className="text-center text-gray-500 dark:text-gray-400 py-12">
        <p>No measures data available for notes view</p>
      </div>
    )
  }

  // Collect all notes with measure and beat context
  const allNotes: Array<{
    note: any
    measureIndex: number
    beatIndex: number
    noteIndex: number
  }> = []

  track.measures.forEach((measure: any, measureIndex: number) => {
    measure.beats?.forEach((beat: any, beatIndex: number) => {
      beat.notes?.forEach((note: any, noteIndex: number) => {
        allNotes.push({ note, measureIndex, beatIndex, noteIndex })
      })
    })
  })

  return (
    <div>
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        All Notes ({allNotes.length})
      </h3>
      
      {allNotes.length === 0 ? (
        <div className="text-center text-gray-500 dark:text-gray-400 py-12">
          <p>No notes found in this track</p>
        </div>
      ) : (
        <div className="grid gap-2">
          {allNotes.map(({ note, measureIndex, beatIndex, noteIndex }, index) => (
            <div key={index} className="bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700 p-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="text-sm font-mono bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 px-2 py-1 rounded">
                    M{measureIndex + 1}.B{beatIndex + 1}.N{noteIndex + 1}
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-600 dark:text-gray-400">String:</span>
                    <span className="font-medium text-gray-900 dark:text-white">{note.string || 'N/A'}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Fret:</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {note.fret !== undefined ? note.fret : 'N/A'}
                    </span>
                  </div>
                </div>
                
                {/* Additional note properties */}
                <div className="flex gap-2 text-xs text-gray-500 dark:text-gray-400">
                  {Object.entries(note)
                    .filter(([key]) => !['string', 'fret'].includes(key))
                    .map(([key, value]) => (
                      <span key={key} className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                        {key}: {JSON.stringify(value)}
                      </span>
                    ))
                  }
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function JsonView({ track }: ViewProps) {
  return (
    <div>
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Track JSON Data
      </h3>
      
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
        <div className="overflow-auto max-h-[600px]">
          <pre className="text-xs text-gray-900 dark:text-gray-100 font-mono whitespace-pre-wrap">
            {JSON.stringify(track, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  )
}