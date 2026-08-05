import { Shell } from "../components/shell";
import { SourceManager } from "../components/source-manager";
import { apiFetch, CollectionRun, CollectionSource } from "../lib/api";

export default async function SourcesPage() {
  const [sources, runs] = await Promise.all([apiFetch<CollectionSource[]>("/sources"), apiFetch<CollectionRun[]>("/sources/runs/recent")]);
  return <Shell title="Fontes e descoberta">
    <SourceManager sources={sources ?? []} />
    <section className="panel">
      <div className="section-title"><div><p className="eyebrow">HISTÓRICO</p><h2>Execuções recentes</h2></div></div>
      {!runs?.length ? <p className="empty">Ainda não houve execução. Ao cadastrar uma fonte, ela entra na fila em até um minuto.</p> : <div className="list">{runs.map((run) => <article className="row detailed" key={run.id}><div><strong>{run.status === "completed" ? "Coleta concluída" : "Coleta com falha"}</strong><span>{run.documents_new} item(ns) novo(s) · {run.candidate_cases_created} caso(s) candidato(s) · acionada por {run.trigger}</span>{run.error_message && <p>{run.error_message}</p>}</div><span className={`status status-${run.status}`}>{run.status}</span></article>)}</div>}
    </section>
  </Shell>;
}
