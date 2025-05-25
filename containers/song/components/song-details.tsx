import { SongGetResponse } from "@/integrations/backend/api"

interface SongDetailsProps {
  song: SongGetResponse
}

export function SongDetails({ song }: SongDetailsProps) {
  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Song Details
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            {song.message}
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <div className="space-y-4">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Song Information
              </h2>
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-300">Song ID:</span>
                  <span className="font-mono text-sm text-gray-900 dark:text-white">
                    {song.song_id}
                  </span>
                </div>
                {song.tab_id && (
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-300">Tab ID:</span>
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
                  <span className="text-gray-600 dark:text-gray-300">Provider:</span>
                  <span className="font-mono text-sm text-gray-900 dark:text-white">
                    {song.file_reference.provider}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600 dark:text-gray-300">Reference:</span>
                  <p className="font-mono text-sm text-gray-900 dark:text-white break-all mt-1">
                    {song.file_reference.reference}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="mt-8 flex gap-4">
          <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            Edit Song
          </button>
          <button className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
            Open in Track Builder
          </button>
        </div>
      </div>
    </div>
  )
}