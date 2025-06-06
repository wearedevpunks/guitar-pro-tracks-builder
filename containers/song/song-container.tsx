"use client"

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { songGet } from "@/integrations/backend/api"
import { LoadingSpinner } from "./components/loading-spinner"
import { ErrorMessage } from "./components/error-message"
import { SongDetails } from "./components/song-details"
import { TrackEditorFeature } from "@/features/tracks"

interface SongContainerProps {
  songId: string
}

export function SongContainer({ songId }: SongContainerProps) {
  const [isEditing, setIsEditing] = useState(false)

  const {
    data: song,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["song", songId],
    queryFn: async () => {
      const response = await songGet({
        path: { song_id: songId },
      })

      if (!response.data?.success || !response.data.song_id) {
        throw new Error(response.data?.message || "Song not found")
      }

      return response.data
    },
    retry: 1,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  const handleEditSong = () => {
    setIsEditing(true)
  }

  const handleCloseEditor = () => {
    setIsEditing(false)
  }

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

  if (isEditing) {
    return (
      <TrackEditorFeature
        parsedData={(song as any).parsed_data || null}
        onClose={handleCloseEditor}
      />
    )
  }

  return <SongDetails song={song} onEditSong={handleEditSong} />
}
