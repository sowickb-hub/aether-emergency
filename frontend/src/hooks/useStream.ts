import { useState, useCallback, useRef } from 'react';
import type { AnalyzeRequest, DispatchResult } from '../types';

type StreamStatus = 'idle' | 'streaming' | 'done' | 'error';

interface UseStreamReturn {
  result: DispatchResult | null;
  rawText: string;
  status: StreamStatus;
  error: string | null;
  analyze: (payload: AnalyzeRequest) => Promise<void>;
  reset: () => void;
}

/**
 * Consumes the FastAPI /analyze StreamingResponse.
 * Accumulates text chunks until a valid JSON object can be parsed,
 * then populates `result`.
 */
export function useStream(): UseStreamReturn {
  const [result, setResult]   = useState<DispatchResult | null>(null);
  const [rawText, setRawText] = useState('');
  const [status, setStatus]   = useState<StreamStatus>('idle');
  const [error, setError]     = useState<string | null>(null);
  const abortRef              = useRef<AbortController | null>(null);

  const reset = useCallback(() => {
    abortRef.current?.abort();
    setResult(null);
    setRawText('');
    setStatus('idle');
    setError(null);
  }, []);

  const analyze = useCallback(async (payload: AnalyzeRequest) => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setResult(null);
    setRawText('');
    setError(null);
    setStatus('streaming');

    try {
      const response = await fetch('/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });

      if (!response.ok) {
        const detail = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(detail?.detail ?? `HTTP ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body');

      const decoder = new TextDecoder();
      let accumulated = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        accumulated += chunk;
        setRawText(accumulated);
      }

      // Strip markdown fences if Gemini wraps response
      let clean = accumulated.trim();
      if (clean.startsWith('```')) {
        clean = clean.replace(/^```[a-z]*\n?/, '').replace(/\n?```$/, '').trim();
      }

      // Find the JSON object boundaries robustly
      const start = clean.indexOf('{');
      const end   = clean.lastIndexOf('}');
      if (start === -1 || end === -1) throw new Error('No JSON found in response.');
      const parsed: DispatchResult = JSON.parse(clean.slice(start, end + 1));

      // Check for Gemini-level error forwarded from backend
      if ('error' in parsed) throw new Error((parsed as any).error);

      setResult(parsed);
      setStatus('done');
    } catch (err: any) {
      if (err.name === 'AbortError') return;
      setError(err.message ?? 'Unknown error');
      setStatus('error');
    }
  }, []);

  return { result, rawText, status, error, analyze, reset };
}
