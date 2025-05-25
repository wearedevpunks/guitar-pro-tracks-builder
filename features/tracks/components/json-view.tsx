interface JsonViewProps {
  track: any
}

export function JsonView({ track }: JsonViewProps) {
  return (
    <div>
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Track JSON Data
      </h3>
      
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
        <div className="overflow-auto max-h-[600px]">
          <pre className="text-xs text-gray-900 dark:text-gray-100 font-mono whitespace-pre-wrap">
            {JSON.stringify(track, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  )
}