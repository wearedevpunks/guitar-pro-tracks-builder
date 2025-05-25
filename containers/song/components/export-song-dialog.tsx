import { SongGetResponse } from "@/integrations/backend/api"

interface ExportSongDialogProps {
  song: SongGetResponse
  isOpen: boolean
  isExporting: boolean
  countInMeasures: number
  onCountInMeasuresChange: (value: number) => void
  onClose: () => void
  onConfirm: () => void
  error?: Error | null
}

export function ExportSongDialog({
  song,
  isOpen,
  isExporting,
  countInMeasures,
  onCountInMeasuresChange,
  onClose,
  onConfirm,
  error,
}: ExportSongDialogProps) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="p-6">
          <div className="flex items-center mb-4">
            <div className="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-green-100 dark:bg-green-900">
              <svg
                className="h-6 w-6 text-green-600 dark:text-green-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </div>
          </div>

          <div className="text-center">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              Export Video
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
              Are you sure you want to export this song? This will generate a
              metronome video with visual timing cues for band practice.
            </p>

            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3 mb-6">
              <div className="text-xs text-gray-600 dark:text-gray-300">
                <strong>Song ID:</strong> {song.song_id}
              </div>
              {song.tab_id && (
                <div className="text-xs text-gray-600 dark:text-gray-300">
                  <strong>Tab ID:</strong> {song.tab_id}
                </div>
              )}
            </div>

            {/* Export Settings */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Count-in Measures
              </label>
              <div className="flex items-center gap-3">
                <input
                  type="number"
                  min="0"
                  max="8"
                  value={countInMeasures}
                  onChange={(e) => onCountInMeasuresChange(parseInt(e.target.value) || 0)}
                  disabled={isExporting}
                  className="w-20 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-white disabled:opacity-50 focus:ring-2 focus:ring-green-500 focus:border-green-500"
                />
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  measures of metronome before the song starts
                </span>
              </div>
            </div>

            {/* Error Display */}
            {error && (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3 mb-6">
                <div className="flex items-center">
                  <svg className="w-4 h-4 text-red-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                  <div className="text-sm text-red-700 dark:text-red-300">
                    <strong>Export Error:</strong> {error.message}
                  </div>
                </div>
                <div className="mt-2 text-xs text-red-600 dark:text-red-400">
                  Click "Export Video" to try again.
                </div>
              </div>
            )}
          </div>

          <div className="flex gap-3">
            <button
              onClick={onClose}
              disabled={isExporting}
              className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-600 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-500 transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={onConfirm}
              disabled={isExporting}
              className="flex-1 px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {isExporting ? (
                <>
                  <svg
                    className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  Exporting...
                </>
              ) : (
                "Export Video"
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
