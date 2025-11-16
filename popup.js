document.getElementById('sort').addEventListener('click', async () => {
  const statusEl = document.getElementById('status');
  statusEl.textContent = 'Sorting...';
  try {
    const res = await browser.runtime.sendMessage({ type: 'SORT_TABS' });
    const n = (res && typeof res.count === 'number') ? res.count : 0;
    statusEl.textContent = n ? `Sorted ${n} tab(s).` : 'No Postcrossing tabs found.';
  } catch (e) {
    console.error(e);
    statusEl.textContent = 'Error: check the console.';
  }
});
