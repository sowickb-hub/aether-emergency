import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import InputChamber from '../components/InputChamber';
import ShimmerCard from '../components/ShimmerCard';
import IntelligenceDashboard from '../components/IntelligenceDashboard';
import type { DispatchResult } from '../types';

/* ── Mock framer-motion so tests run without a browser engine ── */
vi.mock('framer-motion', () => ({
  motion: new Proxy({}, {
    get: (_t, tag: string) =>
      ({ children, ...props }: any) => {
        const Element = tag as any;
        return <Element data-testid={`motion-${tag}`} {...props}>{children}</Element>;
      },
  }),
  AnimatePresence: ({ children }: any) => children,
}));

/* ── Sample dispatch result ───────────────────────────────────── */
const MOCK_RESULT: DispatchResult = {
  hazard_level: 'RED',
  hazard_justification: 'Active fire with two persons trapped on floor 3.',
  primary_need: 'FIRE',
  secondary_needs: ['MEDICAL', 'RESCUE'],
  location_details: 'Pine Ave Building 7, Floor 3',
  casualties_reported: '2',
  imminent_threats: ['Structural collapse', 'Smoke inhalation'],
  recommended_units: ['Engine 4', 'Medic 2', 'Ladder 1'],
  first_aid_protocols: ['Evacuate building', 'Administer oxygen', 'Treat for burns'],
  ems_priority_code: 'P1',
  estimated_response_time_min: 5,
  narrative_summary: 'Active fire on floor 3 with two persons trapped. Immediate fire suppression and medical response required.',
  confidence_score: 0.95,
  image_observations: 'NO IMAGES PROVIDED',
};

/* ════════════════════════════════════════════════════════════════
   InputChamber
   ════════════════════════════════════════════════════════════════ */
describe('InputChamber', () => {
  const onAnalyze = vi.fn();
  const onReset   = vi.fn();

  beforeEach(() => { onAnalyze.mockClear(); onReset.mockClear(); });

  it('renders textarea with correct aria-label', () => {
    render(<InputChamber onAnalyze={onAnalyze} isLoading={false} onReset={onReset} />);
    const textarea = screen.getByRole('textbox', { name: /crisis report text input/i });
    expect(textarea).toBeInTheDocument();
  });

  it('renders the drop zone with accessible role and label', () => {
    render(<InputChamber onAnalyze={onAnalyze} isLoading={false} onReset={onReset} />);
    const dropZone = screen.getByRole('button', { name: /upload evidence images/i });
    expect(dropZone).toBeInTheDocument();
  });

  it('analyze button is disabled when textarea is empty', () => {
    render(<InputChamber onAnalyze={onAnalyze} isLoading={false} onReset={onReset} />);
    const btn = screen.getByRole('button', { name: /analyze.*dispatch/i });
    expect(btn).toBeDisabled();
  });

  it('analyze button is enabled when text is entered', () => {
    render(<InputChamber onAnalyze={onAnalyze} isLoading={false} onReset={onReset} />);
    const textarea = screen.getByRole('textbox', { name: /crisis report/i });
    fireEvent.change(textarea, { target: { value: 'Fire on floor 3!' } });
    const btn = screen.getByRole('button', { name: /analyze.*dispatch/i });
    expect(btn).not.toBeDisabled();
  });

  it('calls onAnalyze with the entered text on click', async () => {
    render(<InputChamber onAnalyze={onAnalyze} isLoading={false} onReset={onReset} />);
    const textarea = screen.getByRole('textbox', { name: /crisis report/i });
    fireEvent.change(textarea, { target: { value: 'Emergency: building fire!' } });
    fireEvent.click(screen.getByRole('button', { name: /analyze.*dispatch/i }));
    await waitFor(() => expect(onAnalyze).toHaveBeenCalledWith('Emergency: building fire!', []));
  });

  it('shows loading state with spinner text when isLoading=true', () => {
    render(<InputChamber onAnalyze={onAnalyze} isLoading={true} onReset={onReset} />);
    expect(screen.getByText(/analyzing/i)).toBeInTheDocument();
  });

  it('shows cancel button while loading', () => {
    render(<InputChamber onAnalyze={onAnalyze} isLoading={true} onReset={onReset} />);
    expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
  });

  it('disables textarea while loading', () => {
    render(<InputChamber onAnalyze={onAnalyze} isLoading={true} onReset={onReset} />);
    const textarea = screen.getByRole('textbox', { name: /crisis report/i });
    expect(textarea).toBeDisabled();
  });
});

/* ════════════════════════════════════════════════════════════════
   ShimmerCard
   ════════════════════════════════════════════════════════════════ */
describe('ShimmerCard', () => {
  it('renders with role="status"', () => {
    render(<ShimmerCard />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('has accessible aria-label', () => {
    render(<ShimmerCard />);
    expect(screen.getByLabelText(/loading intelligence card/i)).toBeInTheDocument();
  });

  it('contains sr-only text for screen readers', () => {
    render(<ShimmerCard />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });
});

/* ════════════════════════════════════════════════════════════════
   IntelligenceDashboard
   ════════════════════════════════════════════════════════════════ */
describe('IntelligenceDashboard', () => {
  it('shows empty state when no result and not loading', () => {
    render(<IntelligenceDashboard result={null} isLoading={false} error={null} />);
    expect(screen.getByLabelText(/awaiting crisis data/i)).toBeInTheDocument();
  });

  it('renders shimmer cards when loading', () => {
    render(<IntelligenceDashboard result={null} isLoading={true} error={null} />);
    const statuses = screen.getAllByRole('status');
    expect(statuses.length).toBeGreaterThanOrEqual(1);
  });

  it('shows error alert when error is provided', () => {
    render(<IntelligenceDashboard result={null} isLoading={false} error="Connection refused" />);
    const alert = screen.getByRole('alert');
    expect(alert).toBeInTheDocument();
    expect(screen.getByText(/connection refused/i)).toBeInTheDocument();
  });

  it('renders all four card regions when result is provided', () => {
    render(<IntelligenceDashboard result={MOCK_RESULT} isLoading={false} error={null} />);
    expect(screen.getByRole('region', { name: /priority status/i })).toBeInTheDocument();
    expect(screen.getByRole('region', { name: /recommended response units/i })).toBeInTheDocument();
    expect(screen.getByRole('region', { name: /first aid protocols/i })).toBeInTheDocument();
    expect(screen.getByRole('region', { name: /system json output/i })).toBeInTheDocument();
  });

  it('displays hazard level badge text', () => {
    render(<IntelligenceDashboard result={MOCK_RESULT} isLoading={false} error={null} />);
    expect(screen.getByText('RED')).toBeInTheDocument();
    expect(screen.getByText('Critical')).toBeInTheDocument();
  });

  it('displays recommended units', () => {
    render(<IntelligenceDashboard result={MOCK_RESULT} isLoading={false} error={null} />);
    expect(screen.getByLabelText(/response unit: engine 4/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/response unit: medic 2/i)).toBeInTheDocument();
  });

  it('priority status indicator has aria-label', () => {
    render(<IntelligenceDashboard result={MOCK_RESULT} isLoading={false} error={null} />);
    expect(screen.getByLabelText(/hazard indicator: RED/i)).toBeInTheDocument();
  });

  it('json toggle button has aria-expanded=false by default', () => {
    render(<IntelligenceDashboard result={MOCK_RESULT} isLoading={false} error={null} />);
    const btn = screen.getByRole('button', { name: /system json output/i });
    expect(btn).toHaveAttribute('aria-expanded', 'false');
  });



  it('displays estimated response time', () => {
    render(<IntelligenceDashboard result={MOCK_RESULT} isLoading={false} error={null} />);
    expect(screen.getByText(/5 min/i)).toBeInTheDocument();
  });
});
