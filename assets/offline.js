// assets/offline.js
export async function safeInsert(supabase, table, data) {
  if (navigator.onLine) {
    await supabase.from(table).upsert(data);
  } else {
    let pending = JSON.parse(localStorage.getItem('pending') || '[]');
    pending.push({ table, data });
    localStorage.setItem('pending', JSON.stringify(pending));
    alert('Saved offline — will sync later.');
  }
}

export async function syncPending(supabase) {
  const pending = JSON.parse(localStorage.getItem('pending') || '[]');
  for (const item of pending) {
    await supabase.from(item.table).upsert(item.data);
  }
  if (pending.length > 0) {
    localStorage.removeItem('pending');
    alert('Offline data synced!');
  }
}

window.addEventListener('online', () => {
  import('./config.js').then(({ SUPABASE_URL, SUPABASE_KEY }) => {
    const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
    syncPending(supabase);
  });
});
