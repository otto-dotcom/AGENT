'use client';

import dynamic from 'next/dynamic';

const TribeApp = dynamic(() => import('./TribeApp'), {
  ssr: false,
  loading: () => (
    <div style={{
      minHeight: '60vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      color: '#3a4f6a', fontFamily: 'ui-monospace, monospace', fontSize: '0.8rem', letterSpacing: '0.1em',
    }}>
      Loading…
    </div>
  ),
});

export default function ClientPage() {
  return (
    <div className="container">
      <TribeApp />
    </div>
  );
}
