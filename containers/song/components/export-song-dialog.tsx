import { SongGetResponse } from "@/integrations/backend/api"

interface ExportSongDialogProps {
  song: SongGetResponse
  isOpen: boolean
  isExporting: boolean
  onClose: () => void
  onConfirm: () => void
}

export function ExportSongDialog({
  song,
  isOpen,
  isExporting,
  onClose,
  onConfirm,
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
              Export Song
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
              Are you sure you want to export this song? This will generate a
              downloadable file with the song data.
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
                "Export Song"
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
