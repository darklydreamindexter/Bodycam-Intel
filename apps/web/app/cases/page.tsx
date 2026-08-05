import { Shell } from "../components/shell";
import { Status } from "../components/status";
import { apiFetch, Case } from "../lib/api";

export default async function CasesPage() {
  const cases = await apiFetch<Case[]>("/cases");
  return <Shell title="Casos">
    <section className="panel"><div className="section-title"><div><p className="eyebrow">CASE INTELLIGENCE</p><h2>Casos e evidências consolidadas</h2></div><span className="count">{cases?.length ?? 0}</span></div>
      {!cases?.length ? <p className="empty">Nenhum caso cadastrado. A coleta automática será conectada a esta fila; enquanto isso, você pode cadastrar casos pela API.</p> : <div className="list">{cases.map((item) => <article className="row detailed" key={item.id}><div><strong>{item.title}</strong><span>{item.city ? `${item.city}, ` : ""}{item.state} · confiança {item.confidence}%</span>{item.summary && <p>{item.summary}</p>}</div><Status value={item.status} /></article>)}</div>}
    </section>
  </Shell>;
}
