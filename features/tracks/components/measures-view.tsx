interface MeasuresViewProps {
  track: any
}

export function MeasuresView({ track }: MeasuresViewProps) {
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