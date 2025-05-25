import { useState } from "react"

interface JsonViewProps {
  track: any
  parsedData: any
}

type DataSource = "track" | "song" | "song-measures"

export function JsonView({ track, parsedData }: JsonViewProps) {
  const [dataSource, setDataSource] = useState<DataSource>("track")

  const currentData =
    dataSource === "track"
      ? track
      : dataSource === "song-measures"
      ? parsedData.measures
      : parsedData
  const jsonString = JSON.stringify(currentData, null, 2)
  const isLongJson = jsonString.length > 1000

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          JSON Data Viewer
        </h3>

        {/* Data Source Selector */}
        <div className="flex items-center gap-2">
          <label className="text-sm text-gray-600 dark:text-gray-400">
            Data Source:
          </label>
          <select
            value={dataSource}
            onChange={(e) => setDataSource(e.target.value as DataSource)}
            className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="track">Track JSON Data</option>
            <option value="song">Song JSON Data</option>
            <option value="song-measures">Song Measures JSON Data</option>
          </select>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {dataSource === "track"
                ? `Showing JSON data for current track (${
                    track.name || "Unnamed Track"
                  })`
                : "Showing complete song JSON data including all tracks"}
            </p>
            {isLongJson && (
              <div className="flex items-center gap-1 text-xs text-amber-600 dark:text-amber-400">
                <svg
                  className="w-3 h-3"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                    clipRule="evenodd"
                  />
                </svg>
                <span>
                  Large JSON ({Math.round(jsonString.length / 1000)}k chars) -
                  Using text view
                </span>
              </div>
            )}
          </div>
        </div>

        <div className="p-4">
          <div className="overflow-auto max-h-[600px]">
            {isLongJson ? (
              <pre className="text-xs text-gray-900 dark:text-gray-100 font-mono whitespace-pre-wrap">
                {jsonString}
              </pre>
            ) : (
              <CollapsibleJsonTree data={currentData} />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

interface CollapsibleJsonTreeProps {
  data: any
  depth?: number
  parentKey?: string
}

function CollapsibleJsonTree({
  data,
  depth = 0,
  parentKey,
}: CollapsibleJsonTreeProps) {
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({})

  const toggleCollapse = (key: string) => {
    setCollapsed((prev) => ({
      ...prev,
      [key]: !prev[key],
    }))
  }

  const renderValue = (
    value: any,
    key: string,
    currentDepth: number
  ): JSX.Element => {
    const fullKey = parentKey ? `${parentKey}.${key}` : key
    const isCollapsed = collapsed[fullKey]

    if (value === null) {
      return <span className="text-gray-500 italic">null</span>
    }

    if (typeof value === "boolean") {
      return (
        <span className="text-blue-600 dark:text-blue-400">
          {value.toString()}
        </span>
      )
    }

    if (typeof value === "number") {
      return <span className="text-green-600 dark:text-green-400">{value}</span>
    }

    if (typeof value === "string") {
      return <span className="text-red-600 dark:text-red-400">"{value}"</span>
    }

    if (Array.isArray(value)) {
      if (value.length === 0) {
        return <span className="text-gray-500">[]</span>
      }

      return (
        <div>
          <button
            onClick={() => toggleCollapse(fullKey)}
            className="inline-flex items-center text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
          >
            {isCollapsed ? (
              <svg
                className="w-3 h-3 mr-1"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                  clipRule="evenodd"
                />
              </svg>
            ) : (
              <svg
                className="w-3 h-3 mr-1"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            )}
            <span className="text-gray-600 dark:text-gray-400">
              [{value.length}]
            </span>
          </button>

          {!isCollapsed && (
            <div className="ml-4 mt-1">
              {value.map((item: any, index: number) => (
                <div
                  key={index}
                  className="mb-1"
                  style={{ marginLeft: `${currentDepth * 12}px` }}
                >
                  <span className="text-gray-600 dark:text-gray-400 mr-2">
                    {index}:
                  </span>
                  {renderValue(item, `${index}`, currentDepth + 1)}
                </div>
              ))}
            </div>
          )}
        </div>
      )
    }

    if (typeof value === "object") {
      const keys = Object.keys(value)
      if (keys.length === 0) {
        return <span className="text-gray-500">{"{}"}</span>
      }

      return (
        <div>
          <button
            onClick={() => toggleCollapse(fullKey)}
            className="inline-flex items-center text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
          >
            {isCollapsed ? (
              <svg
                className="w-3 h-3 mr-1"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                  clipRule="evenodd"
                />
              </svg>
            ) : (
              <svg
                className="w-3 h-3 mr-1"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            )}
            <span className="text-gray-600 dark:text-gray-400">
              {"{"}
              {keys.length}
              {"}"}
            </span>
          </button>

          {!isCollapsed && (
            <div className="ml-4 mt-1">
              {keys.map((objKey: string) => (
                <div
                  key={objKey}
                  className="mb-1"
                  style={{ marginLeft: `${currentDepth * 12}px` }}
                >
                  <span className="text-purple-600 dark:text-purple-400 mr-2">
                    "{objKey}":
                  </span>
                  {renderValue(value[objKey], objKey, currentDepth + 1)}
                </div>
              ))}
            </div>
          )}
        </div>
      )
    }

    return <span className="text-gray-500">{String(value)}</span>
  }

  return (
    <div className="font-mono text-xs text-gray-900 dark:text-gray-100">
      {typeof data === "object" && data !== null ? (
        Array.isArray(data) ? (
          <div>
            {data.map((item: any, index: number) => (
              <div key={index} className="mb-2">
                <span className="text-gray-600 dark:text-gray-400 mr-2">
                  {index}:
                </span>
                {renderValue(item, `${index}`, depth)}
              </div>
            ))}
          </div>
        ) : (
          <div>
            {Object.entries(data).map(([key, value]) => (
              <div key={key} className="mb-2">
                <span className="text-purple-600 dark:text-purple-400 mr-2">
                  "{key}":
                </span>
                {renderValue(value, key, depth)}
              </div>
            ))}
          </div>
        )
      ) : (
        renderValue(data, "root", depth)
      )}
    </div>
  )
}
