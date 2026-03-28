import { useStream } from './hooks/useStream';
import InputChamber         from './components/InputChamber';
import IntelligenceDashboard from './components/IntelligenceDashboard';
import type { ImagePayload } from './types';

export default function App() {
  const { result, status, error, analyze, reset } = useStream();
  const isLoading = status === 'streaming';

  const handleAnalyze = (text: string, images: ImagePayload[]) => {
    analyze({ text, images });
  };

  return (
    <main
      role="main"
      aria-label="Aether Emergency — AI Dispatch Intelligence"
      className="flex h-screen overflow-hidden"
    >
      {/* ── Divider line ── */}
      <div className="absolute inset-y-0 left-[40%] w-px bg-gray-100 z-10" aria-hidden="true" />

      {/* ── Left: Input Chamber (40%) ── */}
      <div className="w-[40%] h-full border-r border-white/40 overflow-hidden bg-white/20 backdrop-blur-xl z-20 shadow-[10px_0_30px_-10px_rgba(0,0,0,0.05)]">
        <InputChamber
          onAnalyze={handleAnalyze}
          isLoading={isLoading}
          onReset={reset}
        />
      </div>

      {/* ── Right: Intelligence Dashboard (60%) ── */}
      <div className="w-[60%] h-full bg-transparent">
        <IntelligenceDashboard
          result={result}
          isLoading={isLoading}
          error={error}
        />
      </div>
    </main>
  );
}
