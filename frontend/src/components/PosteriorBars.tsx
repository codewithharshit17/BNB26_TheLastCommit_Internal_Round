export function PosteriorBars({ posterior }: { posterior: Record<string, number> }) { return <div>{Object.entries(posterior).map(([name, value]) => <div key={name}>{name}: {value}</div>)}</div>; }
