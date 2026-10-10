import { useEffect, useState } from 'react'

// Calls an API function when the component mounts, and again whenever `key`
// changes. The previous data stays on screen while the next request is in
// flight, so the layout does not jump.
export function useApi(load, key = 'once') {
  const [result, setResult] = useState({ key: null, data: null, error: null })

  useEffect(() => {
    let cancelled = false

    load()
      .then((data) => {
        if (!cancelled) setResult({ key, data, error: null })
      })
      .catch((problem) => {
        const error = problem instanceof TypeError ? 'Could not reach the API.' : problem.message
        if (!cancelled) setResult((previous) => ({ key, data: previous.data, error }))
      })

    return () => {
      cancelled = true
    }
    // `load` is a new function on every render, so `key` alone decides when to refetch.
    // oxlint-disable-next-line react-hooks/exhaustive-deps
  }, [key])

  return { data: result.data, error: result.error, loading: result.key !== key }
}
