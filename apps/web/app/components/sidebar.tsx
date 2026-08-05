import Link from "next/link";

const links = [
  ["Visão geral", "/"],
  ["Casos", "/cases"],
  ["Agências", "/agencies"],
  ["Fontes", "/sources"],
  ["Pedidos", "/requests"],
];

export function Sidebar() {
  return (
    <aside className="sidebar">
      <Link className="brand" href="/">BODYCAM<span>INTEL</span></Link>
      <p className="eyebrow">OPERATIONS PLATFORM</p>
      <nav>{links.map(([label, href]) => <Link key={href} href={href}>{label}</Link>)}</nav>
      <div className="sidebar-note"><strong>Revisão humana ativa</strong><span>Pedidos nunca são enviados automaticamente.</span></div>
    </aside>
  );
}
