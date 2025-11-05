import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'OpenMedia - Your Movie & Series Platform',
  description: 'Track, discover and manage your favorite movies and series',
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
