import { Shell } from "../components/shell";
import { Status } from "../components/status";
import { apiFetch, RecordsRequest } from "../lib/api";

export default async function RequestsPage() {
  const requests = await apiFetch<RecordsRequest[]>("/records-requests");
  return <Shell title="Pedidos de registros">
    <section className="panel"><div className="section-title"><div><p className="eyebrow">PUBLIC RECORDS</p><h2>Rascunhos, aprovações e acompanhamento</h2></div><span className="count">{requests?.length ?? 0}</span></div>
      {!requests?.length ? <p className="empty">Ainda não há pedidos. Ao criar um pedido, ele nascerá como rascunho e só poderá avançar após sua aprovação.</p> : <div className="list">{requests.map((request) => <article className="row detailed" key={request.id}><div><strong>{request.subject}</strong><span>{request.requested_items.join(" · ")}</span></div><Status value={request.status} /></article>)}</div>}
    </section>
  </Shell>;
}
