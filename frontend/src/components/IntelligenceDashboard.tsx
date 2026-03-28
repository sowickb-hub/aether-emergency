import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Siren, Truck, HeartPulse, ShieldAlert, Flame, Biohazard,
  UserRound, MapPin, Clock, Brain, ChevronDown, ChevronUp,
  Activity, TriangleAlert, AlertCircle
} from 'lucide-react';
import type { DispatchResult, HazardLevel } from '../types';
import ShimmerCard from './ShimmerCard';

interface IntelligenceDashboardProps {
  result: DispatchResult | null;
  isLoading: boolean;
  error: string | null;
}

/* ── Animation variants ─────────────────────────────────────────────── */
const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.12 } },
};

const cardVariants = {
  hidden:  { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.45, ease: 'easeOut' as const } },
};

/* ── Hazard config ───────────────────────────────────────────────────── */
const HAZARD_CONFIG: Record<HazardLevel, {
  label: string; bg: string; text: string; border: string; glow: string; dot: string;
}> = {
  RED: {
    label: 'Critical',
    bg: 'bg-red-50',        text: 'text-red-600',
    border: 'border-red-200', glow: 'glow-red',
    dot: 'bg-red-500',
  },
  ORANGE: {
    label: 'Serious',
    bg: 'bg-amber-50',      text: 'text-amber-600',
    border: 'border-amber-200', glow: 'glow-amber',
    dot: 'bg-amber-500',
  },
  YELLOW: {
    label: 'Moderate',
    bg: 'bg-emerald-50',    text: 'text-emerald-600',
    border: 'border-emerald-200', glow: 'glow-emerald',
    dot: 'bg-emerald-500',
  },
};

const UNIT_ICONS: Record<string, React.ReactNode> = {
  engine:  <Flame     size={14} />, fire: <Flame       size={14} />,
  medic:   <HeartPulse size={14} />, ems: <HeartPulse   size={14} />,
  police:  <ShieldAlert size={14} />, law: <ShieldAlert  size={14} />,
  rescue:  <Truck      size={14} />, hazmat: <Biohazard  size={14} />,
  ladder:  <Truck      size={14} />,
};

function getUnitIcon(unit: string) {
  const lc = unit.toLowerCase();
  for (const [key, icon] of Object.entries(UNIT_ICONS)) {
    if (lc.includes(key)) return icon;
  }
  return <Truck size={14} />;
}

/* ── JSON syntax highlighter ─────────────────────────────────────────── */
function highlightJson(json: string) {
  return json
    .replace(/(".*?")\s*:/g, '<span class="json-key">$1</span>:')
    .replace(/:\s*(".*?")/g, ': <span class="json-string">$1</span>')
    .replace(/:\s*(\d+\.?\d*)/g, ': <span class="json-number">$1</span>')
    .replace(/:\s*(true|false)/g, ': <span class="json-bool">$1</span>')
    .replace(/:\s*(null)/g, ': <span class="json-null">$1</span>');
}

/* ── Sub-cards ───────────────────────────────────────────────────────── */

function PriorityCard({ result }: { result: DispatchResult }) {
  const cfg = HAZARD_CONFIG[result.hazard_level] ?? HAZARD_CONFIG.YELLOW;
  const conf = Math.round(result.confidence_score * 100);

  return (
    <motion.div
      variants={cardVariants}
      className={`glass-card p-5 border ${cfg.border} ${cfg.glow}`}
      role="region"
      aria-label={`Priority status: ${cfg.label}`}
    >
      <p className="section-label mb-3">Priority Status</p>
      <div className="flex items-center gap-4">
        {/* Glowing indicator */}
        <div
          aria-label={`Hazard indicator: ${result.hazard_level}`}
          className={`pulse-soft w-16 h-16 rounded-full ${cfg.bg} border-2 ${cfg.border}
                      flex items-center justify-center shrink-0`}
        >
          <Siren size={28} className={cfg.text} />
        </div>
        <div className="min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className={`status-dot ${cfg.dot}`} aria-hidden="true" />
            <span className={`text-xl font-bold tracking-tight ${cfg.text}`}>
              {cfg.label}
            </span>
            <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${cfg.bg} ${cfg.text}`}>
              {result.hazard_level}
            </span>
          </div>
          <p className="text-xs text-gray-500 leading-relaxed line-clamp-2">
            {result.hazard_justification}
          </p>
          <div className="mt-2 flex items-center gap-3 text-[11px] text-gray-400">
            <span className="flex items-center gap-1">
              <Brain size={11} /> EMS {result.ems_priority_code}
            </span>
            <span className="flex items-center gap-1">
              <Activity size={11} /> {conf}% confidence
            </span>
            <span className="flex items-center gap-1">
              <Clock size={11} /> ~{result.estimated_response_time_min} min
            </span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function UnitsCard({ result }: { result: DispatchResult }) {
  return (
    <motion.div variants={cardVariants} className="glass-card p-5" role="region" aria-label="Recommended response units">
      <p className="section-label mb-3">Recommended Response Units</p>
      <div className="flex flex-wrap gap-2">
        {result.recommended_units.map((unit, i) => (
          <div key={i} className="unit-pill" aria-label={`Response unit: ${unit}`}>
            {getUnitIcon(unit)}
            <span>{unit}</span>
          </div>
        ))}
      </div>
      {result.secondary_needs.length > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <p className="section-label mb-2">Secondary Needs</p>
          <div className="flex flex-wrap gap-1.5">
            {result.secondary_needs.map((need, i) => (
              <span key={i} className="text-[11px] px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full">
                {need}
              </span>
            ))}
          </div>
        </div>
      )}
      <div className="mt-3 pt-3 border-t border-gray-100 grid grid-cols-2 gap-2 text-xs text-gray-500">
        <div className="flex items-center gap-1.5">
          <MapPin size={12} className="shrink-0" />
          <span className="truncate">{result.location_details}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <UserRound size={12} className="shrink-0" />
          <span>Casualties: {result.casualties_reported}</span>
        </div>
      </div>
    </motion.div>
  );
}

function FirstAidCard({ result }: { result: DispatchResult }) {
  return (
    <motion.div variants={cardVariants} className="glass-card p-5" role="region" aria-label="First aid protocols">
      <p className="section-label mb-3">First Aid Protocols</p>
      <p className="text-xs text-gray-600 leading-relaxed mb-3">
        {result.narrative_summary}
      </p>
      {result.first_aid_protocols.length > 0 && (
        <ol className="space-y-1.5 text-xs text-gray-700">
          {result.first_aid_protocols.map((step, i) => (
            <li key={i} className="flex items-start gap-2">
              <span className="shrink-0 w-4 h-4 rounded-full bg-gray-100 text-gray-500
                               flex items-center justify-center text-[9px] font-bold mt-0.5">
                {i + 1}
              </span>
              <span className="leading-snug">{step}</span>
            </li>
          ))}
        </ol>
      )}
      {result.imminent_threats.length > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <p className="section-label mb-2">Imminent Threats</p>
          <div className="space-y-1">
            {result.imminent_threats.map((threat, i) => (
              <div key={i} className="flex items-center gap-1.5 text-xs text-amber-700">
                <TriangleAlert size={11} className="shrink-0" />
                {threat}
              </div>
            ))}
          </div>
        </div>
      )}
      {result.image_observations && result.image_observations !== 'NO IMAGES PROVIDED' && (
        <div className="mt-3 pt-3 border-t border-gray-100 text-xs text-gray-500">
          <p className="section-label mb-1">Image Analysis</p>
          <p className="leading-relaxed">{result.image_observations}</p>
        </div>
      )}
    </motion.div>
  );
}

function JsonCard({ result }: { result: DispatchResult }) {
  const [open, setOpen] = useState(false);
  const json = JSON.stringify(result, null, 2);

  return (
    <motion.div variants={cardVariants} className="glass-card overflow-hidden" role="region" aria-label="System JSON output">
      <button
        id="json-toggle-btn"
        aria-expanded={open}
        aria-controls="json-output"
        className="w-full flex items-center justify-between px-5 py-4
                   text-left hover:bg-gray-50/60 transition-colors"
        onClick={() => setOpen(o => !o)}
      >
        <p className="section-label">System JSON Output</p>
        {open
          ? <ChevronUp size={14} className="text-gray-400" />
          : <ChevronDown size={14} className="text-gray-400" />
        }
      </button>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            id="json-output"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.28, ease: [0.22, 1, 0.36, 1] }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-5">
              <pre
                className="font-mono text-[11px] leading-relaxed text-gray-600
                           bg-gray-50 rounded-xl p-4 overflow-x-auto overflow-y-auto
                           max-h-56 border border-gray-100"
                dangerouslySetInnerHTML={{ __html: highlightJson(json) }}
                aria-label="JSON dispatch output"
              />
              <button
                onClick={() => {
                  const blob = new Blob([json], { type: 'application/json' });
                  const url  = URL.createObjectURL(blob);
                  const a    = document.createElement('a');
                  a.href = url; a.download = 'aether-emergency_dispatch.json'; a.click();
                  URL.revokeObjectURL(url);
                }}
                className="mt-3 text-xs text-gray-500 hover:text-gray-800 transition-colors"
                aria-label="Download dispatch JSON"
              >
                ↓ Download JSON
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

/* ── Empty state ─────────────────────────────────────────────────────── */
function EmptyState() {
  return (
    <div
      className="h-full flex flex-col items-center justify-center gap-4 text-center px-8"
      aria-label="Awaiting crisis data"
    >
      <div className="w-20 h-20 rounded-full bg-gray-100 flex items-center justify-center">
        <Siren size={36} className="text-gray-300" />
      </div>
      <div>
        <p className="text-sm font-semibold text-gray-500">Awaiting Crisis Data</p>
        <p className="text-xs text-gray-400 mt-1 max-w-xs leading-relaxed">
          Enter a crisis report on the left and click{' '}
          <strong className="text-gray-500">Analyze &amp; Dispatch</strong> to generate
          emergency intelligence.
        </p>
      </div>
    </div>
  );
}

/* ── Main component ──────────────────────────────────────────────────── */
export default function IntelligenceDashboard({ result, isLoading, error }: IntelligenceDashboardProps) {
  return (
    <section
      aria-label="Intelligence Dashboard"
      className="h-full flex flex-col p-8 gap-4 overflow-y-auto"
    >
      {/* Header */}
      <div className="shrink-0">
        <p className="section-label">Intelligence Dashboard</p>
        <h2 className="mt-1 text-2xl font-semibold tracking-tight text-gray-900">
          Dispatch Assessment
        </h2>
      </div>

      {/* Content */}
      {!result && !isLoading && !error && <EmptyState />}

      {error && (
        <div
          role="alert"
          className="glass-card p-5 border border-red-200 bg-red-50 flex items-start gap-3"
        >
          <AlertCircle size={16} className="text-red-500 shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-red-700">Analysis Failed</p>
            <p className="text-xs text-red-600 mt-0.5 leading-relaxed">{error}</p>
          </div>
        </div>
      )}

      {isLoading && !result && (
        <div className="flex flex-col gap-3">
          <ShimmerCard height="h-28" />
          <ShimmerCard height="h-20" />
          <ShimmerCard height="h-36" />
          <ShimmerCard height="h-12" />
        </div>
      )}

      {result && (
        <motion.div
          className="flex flex-col gap-3"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          key={result.narrative_summary} // re-trigger animation on new result
        >
          <PriorityCard result={result} />
          <UnitsCard    result={result} />
          <FirstAidCard result={result} />
          <JsonCard     result={result} />
        </motion.div>
      )}
    </section>
  );
}
