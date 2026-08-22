import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: {
    default: 'Faceless Video App',
    template: '%s | Faceless Video App',
  },
  description: 'AI-powered short-form video automation dashboard...',
  
  // ↓↓↓ Add this section ↓↓↓
  verification: {
    google: '<meta name="google-site-verification" content="galV_JY_4ZE9RWCTrHOHP35SVsKXgqtNKEM2n0LNWcg" />',
  },
  // ↑↑↑ Add this section ↑↑↑
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}