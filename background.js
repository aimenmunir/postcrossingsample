// background.js (MV3 or MV2-safe)

function parsePostcrossing(urlStr) {
  try {
    const url = new URL(urlStr);
    // Expect paths like /postcards/CL-34269
    const m = url.pathname.match(/\/postcards\/([A-Z]{2})-(\d+)/i);
    if (!m) return null;
    return { cc: m[1].toUpperCase(), num: parseInt(m[2], 10) };
  } catch (e) {
    return null;
  }
}

// Core sorter: sorts only within the current window and keeps the block contiguous.
async function sortTabsInCurrentWindow() {
  const tabs = await browser.tabs.query({ currentWindow: true });

  // Filter Postcrossing tabs
  const pcs = tabs
      .map(t => ({ tab: t, parsed: t.url ? parsePostcrossing(t.url) : null }))
      .filter(x => !!x.parsed);

  if (pcs.length === 0) {
    console.log("[Postcrossing Tab Sorter] No Postcrossing tabs found.");
    return { count: 0 };
  }

  // Determine the starting index where the sorted block will live
  const minIndex = Math.min(...pcs.map(x => x.tab.index));

  // Sort by numeric ID asc, then country code asc for ties
  pcs.sort((a, b) => {
    if (a.parsed.num !== b.parsed.num) return a.parsed.num - b.parsed.num;
    if (a.parsed.cc < b.parsed.cc) return -1;
    if (a.parsed.cc > b.parsed.cc) return 1;
    // As a final tiebreaker, keep the original tab order (stable-ish)
    return a.tab.index - b.tab.index;
  });

  // Move tabs so they occupy a contiguous block starting at minIndex
  for (let i = 0; i < pcs.length; i++) {
    const targetIndex = minIndex + i;
    // Moving one-by-one at increasing indices keeps the order stable.
    await browser.tabs.move(pcs[i].tab.id, { index: targetIndex });
  }

  console.log(`[Postcrossing Tab Sorter] Sorted ${pcs.length} tab(s).`);
  return { count: pcs.length };
}

// Click on the toolbar button => sort  (MV3 `action` or MV2 `browserAction`)
(browser.action || browser.browserAction).onClicked.addListener(async () => {
  await sortTabsInCurrentWindow();
});

// Keyboard command
browser.commands.onCommand.addListener(async (command) => {
  if (command === "sort-postcrossing-tabs") {
    await sortTabsInCurrentWindow();
  }
});

// For popup -> background messaging
browser.runtime.onMessage.addListener(async (msg) => {
  if (msg && msg.type === "SORT_TABS") {
    return await sortTabsInCurrentWindow();
  }
});
