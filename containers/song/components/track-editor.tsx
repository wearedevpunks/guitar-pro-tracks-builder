interface TrackEditorProps {
  parsedData: any // Will be properly typed when we know the parsed data structure
  onClose: () => void
}

export function TrackEditor({ parsedData, onClose }: TrackEditorProps) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-7xl h-[95vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <div>
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">
              Track Visualizer
            </h1>
            <p className="text-sm text-gray-600 dark:text-gray-300">
              Guitar Pro Track Data
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
        <div className="flex-1 overflow-hidden p-4">
          <div className="h-full bg-gray-50 dark:bg-gray-900 rounded-lg overflow-auto">
            {parsedData ? (
              <div className="p-6">
                <div className="grid gap-6">
                  {/* Track Overview */}
                  <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                      Track Overview
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                          {parsedData.trackCount || 'N/A'}
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">Tracks</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                          {parsedData.tempo || 'N/A'}
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">BPM</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                          {parsedData.timeSignature || 'N/A'}
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">Time Signature</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                          {parsedData.measureCount || 'N/A'}
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">Measures</div>
                      </div>
                    </div>
                  </div>

                  {/* Track List */}
                  {parsedData.tracks && (
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
                      <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                        Tracks
                      </h2>
                      <div className="space-y-3">
                        {parsedData.tracks.map((track: any, index: number) => (
                          <div key={index} className="border border-gray-200 dark:border-gray-700 rounded-lg p-3">
                            <div className="flex items-center justify-between">
                              <div>
                                <h3 className="font-medium text-gray-900 dark:text-white">
                                  {track.name || `Track ${index + 1}`}
                                </h3>
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                  {track.instrument || 'Unknown Instrument'} • {track.strings || 'N/A'} strings
                                </p>
                              </div>
                              <div className="text-right">
                                <div className="text-sm text-gray-600 dark:text-gray-400">
                                  Channel: {track.channel || 'N/A'}
                                </div>
                                <div className="text-sm text-gray-600 dark:text-gray-400">
                                  Notes: {track.noteCount || 'N/A'}
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Raw Data Viewer */}
                  <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                      Raw Parsed Data
                    </h2>
                    <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 overflow-auto max-h-96">
                      <pre className="text-xs text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                        {JSON.stringify(parsedData, null, 2)}
                      </pre>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-full">
                <div className="text-center text-gray-500 dark:text-gray-400">
                  <div className="mb-4">
                    <svg className="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end p-4 border-t border-gray-200 dark:border-gray-700">
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