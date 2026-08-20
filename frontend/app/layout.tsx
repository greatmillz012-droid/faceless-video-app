import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Faceless Video App',
  description: 'AI short-form video automation dashboard',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
