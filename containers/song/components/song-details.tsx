import { useState } from "react"
import { SongGetResponse } from "@/integrations/backend/api"
import { ExportSongDialog } from "./export-song-dialog"

interface SongDetailsProps {
  song: SongGetResponse
  onEditSong: () => void
}

export function SongDetails({ song, onEditSong }: SongDetailsProps) {
  const [showExportDialog, setShowExportDialog] = useState(false)
  const [isExporting, setIsExporting] = useState(false)

  const handleExportSong = async () => {
    setIsExporting(true)
    try {
      // TODO: Implement export API call when backend endpoint is available
      // const response = await exportSong({ path: { song_id: song.song_id } })

      // Placeholder for now - simulate API call
      await new Promise((resolve) => setTimeout(resolve, 2000))

      alert(
        "Export functionality will be implemented when the backend export endpoint is available."
      )
    } catch (error) {
      console.error("Export failed:", error)
      alert("Export failed. Please try again.")
    } finally {
      setIsExporting(false)
      setShowExportDialog(false)
    }
  }
  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Song Details
          </h1>
          <p className="text-gray-600 dark:text-gray-300">{song.message}</p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <div className="space-y-4">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Song Information
              </h2>
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-300">
                    Song ID:
                  </span>
                  <span className="font-mono text-sm text-gray-900 dark:text-white">
                    {song.song_id}
                  </span>
                </div>
                {song.tab_id && (
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-300">
                      Tab ID:
                    </span>
                    <span className="font-mono text-sm text-gray-900 dark:text-white">
                      {song.tab_id}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {song.file_reference && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                File Information
              </h2>
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-300">
                    Provider:
                  </span>
                  <span className="font-mono text-sm text-gray-900 dark:text-white">
                    {song.file_reference.provider}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600 dark:text-gray-300">
                    Reference:
                  </span>
                  <p className="font-mono text-sm text-gray-900 dark:text-white break-all mt-1">
                    {song.file_reference.reference}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="mt-8 flex gap-4">
          <button
            onClick={onEditSong}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Edit Song
          </button>
          <button
            onClick={() => setShowExportDialog(true)}
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            Export Song
          </button>
        </div>
      </div>

      <ExportSongDialog
        song={song}
        isOpen={showExportDialog}
        isExporting={isExporting}
        onClose={() => setShowExportDialog(false)}
        onConfirm={handleExportSong}
      />
    </div>
  )
}
