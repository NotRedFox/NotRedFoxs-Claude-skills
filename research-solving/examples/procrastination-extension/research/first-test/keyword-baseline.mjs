// First test: can a zero-dependency keyword + domain rule tell on-task tabs from off-task tabs?
// Pass if accuracy >= 0.80 on the labelled set below. Fail otherwise.
// The titles are hand-written examples, not real browsing history. Replace them with a day of your own
// tab titles (exported from the logger in idea 1) to get a real answer.

const task = 'learn javascript build a browser extension manifest service worker';
const distractionDomains = ['youtube.com', 'reddit.com', 'x.com', 'instagram.com', 'netflix.com', 'tiktok.com', 'twitch.tv', 'facebook.com'];
const workDomains = ['developer.mozilla.org', 'stackoverflow.com', 'github.com', 'developer.chrome.com', 'npmjs.com', 'localhost'];

// [title, domain, label] label 1 = on task, 0 = off task
const tabs = [
  ['chrome.tabs - MDN Web Docs', 'developer.mozilla.org', 1],
  ['How to use chrome.alarms in a service worker - Stack Overflow', 'stackoverflow.com', 1],
  ['ActivityWatch/aw-watcher-web: Browser watcher', 'github.com', 1],
  ['Manifest V3 migration checklist', 'developer.chrome.com', 1],
  ['webextension-polyfill - npm', 'npmjs.com', 1],
  ['localhost:5173 extension popup', 'localhost', 1],
  ['JavaScript async await explained', 'javascript.info', 1],
  ['Promise.all vs Promise.allSettled', 'javascript.info', 1],
  ['Building a Chrome extension in 10 minutes', 'youtube.com', 1],     // on task, distracting domain
  ['r/learnjavascript - service worker keeps dying', 'reddit.com', 1], // on task, distracting domain
  ['Intro to IndexedDB for beginners', 'web.dev', 1],
  ['Notification API tutorial', 'dev.to', 1],
  ['Understanding the event loop', 'medium.com', 1],
  ['ESLint configuration guide', 'eslint.org', 1],
  ['tabs.onActivated firing twice? Issue #412', 'github.com', 1],
  ['Gmail - Inbox (3)', 'mail.google.com', 0],
  ['Top 10 goals of the week', 'youtube.com', 0],
  ['r/funny - my cat discovered the printer', 'reddit.com', 0],
  ['Home / X', 'x.com', 0],
  ['Stranger Things | Netflix', 'netflix.com', 0],
  ['Amazon.com: noise cancelling headphones', 'amazon.com', 0],
  ['Weather forecast for the weekend', 'weather.com', 0],
  ['BBC News - Home', 'bbc.co.uk', 0],
  ['Wordle - A daily word game', 'nytimes.com', 0],
  ['Instagram', 'instagram.com', 0],
  ['Best pizza near me - Google Maps', 'google.com', 0],
  ['Twitch: live speedrun', 'twitch.tv', 0],
  ['Cheap flights to Lisbon', 'skyscanner.net', 0],
  ['Hacker News', 'news.ycombinator.com', 0],
  ['Show HN: I built a JavaScript game engine', 'news.ycombinator.com', 0], // keyword trap
  ['JavaScript drama: the framework wars thread', 'reddit.com', 0],          // keyword trap
  ['Facebook', 'facebook.com', 0],
  ['Spotify - Web Player', 'open.spotify.com', 0],
  ['eBay vintage keyboards', 'ebay.com', 0],
  ['Wikipedia: List of largest octopuses', 'wikipedia.org', 0],
  ['How old is the oldest tortoise', 'google.com', 0],
  ['Premier League table', 'bbc.co.uk', 0],
  ['TikTok - For You', 'tiktok.com', 0],
  ['Chrome extension ideas that make money', 'youtube.com', 0],              // keyword trap
  ['Reddit - r/webdev memes', 'reddit.com', 0],
];

const tokens = s => s.toLowerCase().split(/[^a-z0-9]+/).filter(w => w.length > 2);
const taskWords = new Set(tokens(task).concat(['mdn', 'api', 'npm', 'chrome', 'tabs', 'async', 'promise', 'eslint', 'indexeddb', 'notification', 'event', 'loop']));

function score(title, domain) {
  if (workDomains.some(d => domain.endsWith(d))) return 1;
  const overlap = tokens(title).filter(w => taskWords.has(w)).length;
  if (distractionDomains.some(d => domain.endsWith(d))) return overlap >= 2 ? 1 : 0;
  return overlap >= 1 ? 1 : 0;
}

let tp = 0, tn = 0, fp = 0, fn = 0;
const errors = [];
for (const [title, domain, label] of tabs) {
  const p = score(title, domain);
  if (p === 1 && label === 1) tp++;
  else if (p === 0 && label === 0) tn++;
  else { p === 1 ? fp++ : fn++; errors.push(`${p === 1 ? 'FP' : 'FN'}: ${title} (${domain})`); }
}
const acc = (tp + tn) / tabs.length;
console.log(`n=${tabs.length} tp=${tp} tn=${tn} fp=${fp} fn=${fn}`);
console.log(`accuracy=${acc.toFixed(3)} precision(on-task)=${(tp / (tp + fp)).toFixed(3)} recall(on-task)=${(tp / (tp + fn)).toFixed(3)}`);
errors.forEach(e => console.log(e));
console.log(acc >= 0.8 ? 'RESULT: PASS (>= 0.80)' : 'RESULT: FAIL (< 0.80)');
