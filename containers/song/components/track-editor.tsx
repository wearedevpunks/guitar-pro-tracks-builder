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

interface TrackDetailsProps {
  track: any
  trackIndex: number
}

function TrackDetails({ track, trackIndex }: TrackDetailsProps) {
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

      {/* Measures */}
      {track.measures && track.measures.length > 0 ? (
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

                {/* Show other measure properties */}
                {Object.keys(measure).filter(key => !['beats', 'timeSignature', 'keySignature'].includes(key)).length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      <pre className="whitespace-pre-wrap">
                        {JSON.stringify(
                          Object.fromEntries(
                            Object.entries(measure).filter(([key]) => !['beats', 'timeSignature', 'keySignature'].includes(key))
                          ),
                          null,
                          2
                        )}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="text-center text-gray-500 dark:text-gray-400 py-8">
          <p>No measures data available for this track</p>
        </div>
      )}
    </div>
  )
}