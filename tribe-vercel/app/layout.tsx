import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'TRIBE v2 — Neural Activity Predictor',
  description: 'Predict fMRI BOLD responses on cortical surface from video, audio, or text',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
