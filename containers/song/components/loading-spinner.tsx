export function LoadingSpinner() {
  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-center min-h-[300px]">
          <div className="flex flex-col items-center space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="text-gray-600 dark:text-gray-300">
              Loading song details...
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
