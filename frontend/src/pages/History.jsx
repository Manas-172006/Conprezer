export default function History({ items, loading, onDownload }) {
  if (loading) return <p className="py-8 text-slate-500">Loading history…</p>;
  if (!items.length) return <p className="py-8 text-slate-500">Your completed jobs will appear here.</p>;

  return (
    <ul className="divide-y divide-slate-100">
      {items.map((item) => (
        <li key={item.id} className="flex flex-wrap items-center justify-between gap-3 py-4">
          <div>
            <p className="font-medium">Job #{item.id} · {item.input_type.toUpperCase()} → {item.output_type.toUpperCase()}</p>
            <p className="text-sm text-slate-500">{new Date(item.created_at).toLocaleString()}</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm capitalize text-slate-500">{item.status}</span>
            {item.download_url && (
              <button onClick={() => onDownload(item.download_url)} className="font-semibold text-indigo-600 hover:text-indigo-800">
                Download
              </button>
            )}
          </div>
        </li>
      ))}
    </ul>
  );
}
