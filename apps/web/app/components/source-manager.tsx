"use client";

import { FormEvent, useState } from "react";
import { CollectionSource } from "../lib/api";

const publicApi = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function SourceManager({ sources }: { sources: CollectionSource[] }) {
  const [message, setMessage] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function addSource(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setBusy(true);
    setMessage(null);
    const response = await fetch(`${publicApi}/api/v1/sources`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: form.get("name"), url: form.get("url"), default_state: String(form.get("default_state") || "").trim().toUpperCase() || null, kind: form.get("kind"), reliability_score: Number(form.get("reliability_score")), poll_interval_minutes: Number(form.get("poll_interval_minutes")) }),
    });
    const data = await response.json().catch(() => null);
    setBusy(false);
    if (!response.ok) return setMessage(data?.detail ?? "Não foi possível cadastrar a fonte.");
    event.currentTarget.reset();
    setMessage("Fonte cadastrada. A primeira coleta será agendada automaticamente em até um minuto.");
    window.location.reload();
  }

  async function collectNow(source: CollectionSource) {
    setBusy(true); setMessage(null);
    const response = await fetch(`${publicApi}/api/v1/sources/${source.id}/collect`, { method: "POST" });
    const data = await response.json().catch(() => null);
    setBusy(false);
    setMessage(response.ok ? data?.message ?? "Coleta colocada na fila." : data?.detail ?? "Não foi possível iniciar a coleta.");
  }

  return <>
    <section className="panel">
      <div className="section-title"><div><p className="eyebrow">DISCOVERY ENGINE</p><h2>Adicionar fonte pública</h2></div></div>
      <form className="source-form" onSubmit={addSource}>
        <label>Nome<input name="name" required placeholder="Ex.: Austin Police — News" /></label>
        <label>URL do RSS/Atom<input name="url" type="url" required placeholder="https://…/feed" /></label>
        <label>Estado padrão (opcional)<input name="default_state" maxLength={2} placeholder="TX" /></label>
        <label>Confiabilidade (0–100)<input name="reliability_score" type="number" min="0" max="100" defaultValue="70" /></label>
        <label>Intervalo em minutos<input name="poll_interval_minutes" type="number" min="15" max="1440" defaultValue="60" /></label>
        <label>Tipo<select name="kind"><option value="rss">Notícia / RSS público</option><option value="official_rss">Comunicado oficial / RSS</option></select></label>
        <button className="button" disabled={busy}>{busy ? "Aguarde…" : "Salvar fonte"}</button>
      </form>
      {message && <p className="form-message">{message}</p>}
    </section>
    <section className="panel">
      <div className="section-title"><div><p className="eyebrow">FONTES ATIVAS</p><h2>Coleta com origem rastreável</h2></div><span className="count">{sources.length}</span></div>
      {!sources.length ? <p className="empty">Cadastre uma fonte RSS ou de comunicados oficiais. Nada é coletado até você optar por uma fonte.</p> : <div className="list">{sources.map((source) => <article className="row detailed" key={source.id}><div><strong>{source.name}</strong><span>{source.kind === "official_rss" ? "Comunicado oficial" : "Notícia pública"} · {source.default_state ?? "EUA sem estado definido"} · a cada {source.poll_interval_minutes} min</span><p>{source.last_collected_at ? `Última coleta: ${new Date(source.last_collected_at).toLocaleString("pt-BR")}` : "Aguardando a primeira coleta"}</p></div><button className="button secondary" onClick={() => collectNow(source)} disabled={busy}>Coletar agora</button></article>)}</div>}
    </section>
  </>;
}
