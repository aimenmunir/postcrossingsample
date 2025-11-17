function parsePostcrossing(urlStr) {
  try {
    const url = new URL(urlStr);
    const m = url.pathname.match(/\/postcards\/([A-Z]{2})-(\d+)/i);
    if (!m) return null;
    return { cc: m[1].toUpperCase(), num: parseInt(m[2], 10) };
  } catch (e) {
    return null;
  }
}

async function sortTabsInCurrentWindow() {
  const tabs = await browser.tabs.query({ currentWindow: true });
  const pcs = tabs
    .map(t => ({ tab: t, parsed: t.url ? parsePostcrossing(t.url) : null }))
    .filter(x => !!x.parsed);
  if (pcs.length === 0) {
    console.log("[Postcrossing Tab Sorter] No Postcrossing tabs found.");
    return { count: 0 };
  }
  const minIndex = Math.min(...pcs.map(x => x.tab.index));
  pcs.sort((a, b) => {
    if (a.parsed.num !== b.parsed.num) return a.parsed.num - b.parsed.num;
    if (a.parsed.cc < b.parsed.cc) return -1;
    if (a.parsed.cc > b.parsed.cc) return 1;
    return a.tab.index - b.tab.index;
  });
  for (let i = 0; i < pcs.length; i++) {
    const targetIndex = minIndex + i;
    await browser.tabs.move(pcs[i].tab.id, { index: targetIndex });
  }
  console.log(`[Postcrossing Tab Sorter] Sorted ${pcs.length} tab(s).`);
  return { count: pcs.length };
}

(browser.action || browser.browserAction).onClicked.addListener(async () => {
  await sortTabsInCurrentWindow();
});

browser.commands.onCommand.addListener(async (command) => {
  if (command === "sort-postcrossing-tabs") {
    await sortTabsInCurrentWindow();
  }
});

browser.runtime.onMessage.addListener(async (msg) => {
  if (msg && msg.type === "SORT_TABS") {
    return await sortTabsInCurrentWindow();
  }
});
