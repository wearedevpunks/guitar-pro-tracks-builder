"use client"

import { useQuery } from "@tanstack/react-query"
import { getSongByIdApiSongsSongIdGet } from "@/integrations/backend/api"
import { LoadingSpinner } from "./components/loading-spinner"
import { ErrorMessage } from "./components/error-message"
import { SongDetails } from "./components/song-details"

interface SongContainerProps {
  songId: string
}

export function SongContainer({ songId }: SongContainerProps) {
  const {
    data: song,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["song", songId],
    queryFn: async () => {
      const response = await getSongByIdApiSongsSongIdGet({
        path: { song_id: songId },
      })

      if (!response.data?.success || !response.data.song_id) {
        throw new Error(response.data?.message || "Song not found")
      }

      return response.data
    },
    retry: 1,
  })

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (error) {
    return (
      <ErrorMessage
        message="Failed to load song details"
        onRetry={() => refetch()}
      />
    )
  }

  if (!song) {
    return <ErrorMessage message="Song not found" onRetry={() => refetch()} />
  }

  return <SongDetails song={song} />
}
