import { useState } from "react"
import { useMutation } from "@tanstack/react-query"
import { SongGetResponse, songExportVideo } from "@/integrations/backend/api"
import { ExportSongDialog } from "./export-song-dialog"

interface SongDetailsProps {
  song: SongGetResponse
  onEditSong: () => void
}

export function SongDetails({ song, onEditSong }: SongDetailsProps) {
  const [showExportDialog, setShowExportDialog] = useState(false)
  const [countInMeasures, setCountInMeasures] = useState(2)
  const [useDynamicColors, setUseDynamicColors] = useState(true)

  const exportVideoMutation = useMutation({
    mutationFn: async () => {
      if (!song.song_id) {
        throw new Error("Song ID is missing. Cannot export.")
      }

      // Create an AbortController for timeout management
      const controller = new AbortController()

      // Set a 10-minute timeout for video export
      const timeoutId = setTimeout(() => {
        controller.abort()
      }, 10 * 60 * 1000) // 10 minutes

      try {
        const response = await songExportVideo({
          body: {
            song_id: song.song_id,
            output_format: "mp4",
            resolution: [1920, 1080],
            fps: 30,
            count_in_measures: countInMeasures,
            use_dynamic_colors: useDynamicColors,
          },
          // Pass the abort signal to the fetch request
          signal: controller.signal,
        })

        clearTimeout(timeoutId)

        if (!response.data?.success || !response.data?.video_file) {
          throw new Error(response.data?.message || "Export failed")
        }

        return response.data
      } catch (error) {
        clearTimeout(timeoutId)

        // Handle timeout error specifically
        if (error instanceof Error && error.name === "AbortError") {
          throw new Error(
            "Export operation timed out after 10 minutes. Please try again with a shorter song or contact support."
          )
        }

        throw error
      }
    },
    onSuccess: (data) => {
      // Create download link
      const downloadUrl = `/api/files/${data.video_file!.provider}/${
        data.video_file!.reference
      }`

      // Trigger download
      const link = document.createElement("a")
      link.href = downloadUrl
      link.download = `song-${song.song_id}-export.mp4`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      // Show success message with details
      alert(
        `Export successful! Video duration: ${data.duration_seconds}s with ${data.total_measures} measures.`
      )
      setShowExportDialog(false)
    },
    onError: (error) => {
      console.error("Export failed:", error)
      // Error will be displayed in the dialog, no need for alert here
    },
  })

  const handleExportSong = () => {
    exportVideoMutation.mutate()
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
            Export Video
          </button>
        </div>
      </div>

      <ExportSongDialog
        song={song}
        isOpen={showExportDialog}
        isExporting={exportVideoMutation.isPending}
        countInMeasures={countInMeasures}
        onCountInMeasuresChange={setCountInMeasures}
        useDynamicColors={useDynamicColors}
        onUseDynamicColorsChange={setUseDynamicColors}
        onClose={() => setShowExportDialog(false)}
        onConfirm={handleExportSong}
        error={exportVideoMutation.error}
      />
    </div>
  )
}
