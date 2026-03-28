/** Shimmer skeleton card shown while AI is streaming. */
interface ShimmerCardProps {
  height?: string;
  className?: string;
}

export default function ShimmerCard({ height = 'h-24', className = '' }: ShimmerCardProps) {
  return (
    <div
      role="status"
      aria-label="Loading intelligence card"
      className={`glass-card p-5 overflow-hidden ${className}`}
    >
      <div className={`shimmer rounded-lg w-full ${height}`} />
      <div className="mt-3 shimmer rounded h-3 w-2/3" />
      <div className="mt-2 shimmer rounded h-3 w-1/2" />
      <span className="sr-only">Loading…</span>
    </div>
  );
}
