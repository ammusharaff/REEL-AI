export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body style={{ fontFamily: "Arial", margin: 0, padding: 0 }} suppressHydrationWarning>
        <div style={{ padding: 16, borderBottom: "1px solid #eee" }}>
          <b>Reels AI Studio (MVP)</b>
          <span style={{ marginLeft: 12, color: "#666" }}>48-hour build</span>
        </div>
        <div style={{ padding: 16 }}>{children}</div>
      </body>
    </html>
  );
}
