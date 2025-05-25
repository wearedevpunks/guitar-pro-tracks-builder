interface StringsViewProps {
  track: any
}

export function StringsView({ track }: StringsViewProps) {
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