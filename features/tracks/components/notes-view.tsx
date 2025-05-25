interface NotesViewProps {
  track: any
}

export function NotesView({ track }: NotesViewProps) {
  if (!track.measures || track.measures.length === 0) {
    return (
      <div className="text-center text-gray-500 dark:text-gray-400 py-12">
        <p>No measures data available for notes view</p>
      </div>
    )
  }

  // Collect all notes with measure and beat context
  const allNotes: Array<{
    note: any
    measureIndex: number
    beatIndex: number
    noteIndex: number
  }> = []

  track.measures.forEach((measure: any, measureIndex: number) => {
    measure.beats?.forEach((beat: any, beatIndex: number) => {
      beat.notes?.forEach((note: any, noteIndex: number) => {
        allNotes.push({ note, measureIndex, beatIndex, noteIndex })
      })
    })
  })

  return (
    <div>
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        All Notes ({allNotes.length})
      </h3>
      
      {allNotes.length === 0 ? (
        <div className="text-center text-gray-500 dark:text-gray-400 py-12">
          <p>No notes found in this track</p>
        </div>
      ) : (
        <div className="grid gap-2">
          {allNotes.map(({ note, measureIndex, beatIndex, noteIndex }, index) => (
            <div key={index} className="bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700 p-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="text-sm font-mono bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 px-2 py-1 rounded">
                    M{measureIndex + 1}.B{beatIndex + 1}.N{noteIndex + 1}
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-600 dark:text-gray-400">String:</span>
                    <span className="font-medium text-gray-900 dark:text-white">{note.string || 'N/A'}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Fret:</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {note.fret !== undefined ? note.fret : 'N/A'}
                    </span>
                  </div>
                </div>
                
                {/* Additional note properties */}
                <div className="flex gap-2 text-xs text-gray-500 dark:text-gray-400">
                  {Object.entries(note)
                    .filter(([key]) => !['string', 'fret'].includes(key))
                    .map(([key, value]) => (
                      <span key={key} className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                        {key}: {JSON.stringify(value)}
                      </span>
                    ))
                  }
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}