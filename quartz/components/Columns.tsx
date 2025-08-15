export default function Columns({ children }: { children: React.ReactNode[] }) {
  return (
    <div style={{ display: 'flex', gap: '2rem' }}>
      {children.map((child, i) => (
        <div key={i} style={{ flex: 1 }}>
          {child}
        </div>
      ))}
    </div>
  );
}
