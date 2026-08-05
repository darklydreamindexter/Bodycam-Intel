import Link from "next/link";
import { Shell } from "./components/shell";
import { apiFetch, Case, Summary } from "./lib/api";

const metrics = [
  ["Casos registrados", "cases_total"],
  ["Casos priorizados", "cases_prioritized"],
  ["Agências mapeadas", "agencies_total"],
  ["Rascunhos de pedido", "requests_draft"],
  ["Fontes ativas", "sources_total"],
] as const;

export default async function DashboardPage() {
  const [summary, cases] = await Promise.all([apiFetch<Summary>("/dashboard/summary"), apiFetch<Case[]>("/cases")]);
  return <Shell title="Centro de operações">
    <div className="metrics">{metrics.map(([label, key]) => <article className="metric" key={key}><span>{label}</span><strong>{summary?.[key] ?? "—"}</strong></article>)}</div>
    <section className="panel attention"><div><p className="eyebrow">FILA DE DECISÃO</p><h2>{summary?.requests_awaiting_approval ?? 0} pedido(s) aguardando sua aprovação</h2><p>A aprovação é uma ação consciente: nenhum pedido será submetido pela plataforma sem você.</p></div><Link className="button" href="/requests">Ver pedidos</Link></section>
    <section className="panel"><div className="section-title"><div><p className="eyebrow">ATIVIDADE RECENTE</p><h2>Casos descobertos</h2></div><Link href="/cases">Ver todos →</Link></div>
      {cases && cases.length > 0 ? <div className="list">{cases.slice(0, 5).map((item) => <article className="row" key={item.id}><div><strong>{item.title}</strong><span>{item.city ? `${item.city}, ` : ""}{item.state} · confiança {item.confidence}%</span></div><span className="status">{item.status.replaceAll("_", " ")}</span></article>)}</div> : <Empty message="Ainda não há casos. Cadastre uma fonte em Fontes para iniciar a descoberta automática." />}
    </section>
  </Shell>;
}

function Empty({ message }: { message: string }) { return <p className="empty">{message}</p>; }
