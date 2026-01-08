import { useState, useCallback } from 'react';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

interface UseApiReturn<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  execute: (...args: any[]) => Promise<T | null>;
  reset: () => void;
  setData: (data: T | null) => void;
}

/**
 * Custom hook for handling API calls with loading, error, and data states
 */
export function useApi<T>(
  apiFunction: (...args: any[]) => Promise<T>,
  immediate: boolean = false
): UseApiReturn<T> {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: immediate,
    error: null,
  });

  const execute = useCallback(
    async (...args: any[]): Promise<T | null> => {
      setState({ data: null, loading: true, error: null });

      try {
        const result = await apiFunction(...args);
        setState({ data: result, loading: false, error: null });
        return result;
      } catch (err: any) {
        const errorMessage = err.message || 'An unexpected error occurred';
        setState({ data: null, loading: false, error: errorMessage });
        return null;
      }
    },
    [apiFunction]
  );

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  const setData = useCallback((data: T | null) => {
    setState(prev => ({ ...prev, data }));
  }, []);

  return {
    ...state,
    execute,
    reset,
    setData,
  };
}

/**
 * Custom hook for handling list/array API calls
 */
export function useApiList<T>(
  apiFunction: (...args: any[]) => Promise<T[]>,
  immediate: boolean = false
): UseApiReturn<T[]> & { refresh: () => Promise<T[] | null> } {
  const [lastArgs, setLastArgs] = useState<any[]>([]);

  const apiResult = useApi<T[]>(apiFunction, immediate);

  const executeWithArgs = useCallback(
    async (...args: any[]): Promise<T[] | null> => {
      setLastArgs(args);
      return apiResult.execute(...args);
    },
    [apiResult]
  );

  const refresh = useCallback(async (): Promise<T[] | null> => {
    return apiResult.execute(...lastArgs);
  }, [apiResult, lastArgs]);

  return {
    ...apiResult,
    execute: executeWithArgs,
    refresh,
  };
}

export default useApi;
