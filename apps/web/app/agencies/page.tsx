import { Shell } from "../components/shell";
import { apiFetch, Agency } from "../lib/api";

export default async function AgenciesPage() {
  const agencies = await apiFetch<Agency[]>("/agencies");
  return <Shell title="Agências">
    <section className="panel"><div className="section-title"><div><p className="eyebrow">AGENCY INTELLIGENCE</p><h2>Contatos e canais de registros</h2></div><span className="count">{agencies?.length ?? 0}</span></div>
      {!agencies?.length ? <p className="empty">Nenhuma agência cadastrada. O módulo irá reutilizar contatos e políticas de cada agência em pedidos futuros.</p> : <div className="list">{agencies.map((agency) => <article className="row detailed" key={agency.id}><div><strong>{agency.name}</strong><span>{agency.agency_type} · {agency.city ? `${agency.city}, ` : ""}{agency.state}</span><p>{agency.records_email ?? "E-mail de records ainda não mapeado"}{agency.records_portal_url ? " · portal disponível" : ""}</p></div></article>)}</div>}
    </section>
  </Shell>;
}
