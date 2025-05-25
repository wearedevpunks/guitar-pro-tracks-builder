import { SongContainer } from "@/containers/song"

interface SongPageProps {
  params: {
    id: string
  }
}

export default function SongPage({ params }: SongPageProps) {
  const { id } = params

  return <SongContainer songId={id} />
}
