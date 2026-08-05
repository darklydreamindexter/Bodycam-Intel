import { Sidebar } from "./sidebar";

export function Shell({ title, children }: Readonly<{ title: string; children: React.ReactNode }>) {
  return <main className="app-shell"><Sidebar /><section className="content"><header><p className="eyebrow">UNITED STATES · LOCAL WORKSPACE</p><h1>{title}</h1></header>{children}</section></main>;
}
