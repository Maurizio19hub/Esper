// Immagini SVG generate al volo per i documenti di esempio.

const uri = (svg: string) => `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;

export function sunsetArt(): string {
  return uri(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
  <defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#3b2a6b"/><stop offset=".5" stop-color="#e2563a"/><stop offset="1" stop-color="#ffb347"/></linearGradient></defs>
  <rect width="400" height="300" fill="url(#g)"/>
  <circle cx="200" cy="170" r="42" fill="#ffd27a"/>
  <rect y="180" width="400" height="120" fill="#1d2a4a"/>
  <g stroke="#ffd27a" stroke-opacity=".55" stroke-width="3" stroke-linecap="round">
    <path d="M165 195h70M175 208h50M184 221h32"/></g>
  <path d="M0 230 L60 200 L120 235 L170 215 L170 300 L0 300Z" fill="#0f1730"/></svg>`);
}

export function blueprintArt(): string {
  return uri(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
  <rect width="400" height="300" fill="#0e3a5f"/>
  <g stroke="#7fc4ff" stroke-opacity=".18">${Array.from({ length: 20 }, (_, i) => `<path d="M${i * 20} 0V300M0 ${i * 20}H400"/>`).join('')}</g>
  <g fill="none" stroke="#bfe3ff" stroke-width="2.5" stroke-linecap="round">
    <rect x="30" y="40" width="90" height="120" rx="4"/><path d="M120 70h90v-30h60M210 70v90h90M120 130h70M210 160h60"/>
    <circle cx="270" cy="40" r="10"/><circle cx="300" cy="160" r="10"/><circle cx="190" cy="130" r="8"/>
    <path d="M45 70h60M45 100h60M45 130h60"/><path d="M270 200v60M240 230h60M250 260h40" /></g></svg>`);
}

export function screenshotArt(): string {
  return uri(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
  <rect width="400" height="300" fill="#eef1f5"/>
  <rect x="40" y="30" width="320" height="240" rx="10" fill="#fff" stroke="#cfd6df"/>
  <rect x="40" y="30" width="320" height="28" rx="10" fill="#e3e8ef"/>
  <circle cx="58" cy="44" r="5" fill="#ff6b6b"/><circle cx="76" cy="44" r="5" fill="#ffd166"/><circle cx="94" cy="44" r="5" fill="#6bd18a"/>
  <rect x="70" y="90" width="260" height="30" rx="6" fill="#f3f5f8" stroke="#d5dbe4"/>
  <rect x="70" y="135" width="260" height="30" rx="6" fill="#f3f5f8" stroke="#d5dbe4"/>
  <rect x="70" y="180" width="260" height="22" rx="5" fill="#fde8e8"/><rect x="82" y="188" width="150" height="6" rx="3" fill="#e05252"/>
  <rect x="70" y="220" width="110" height="30" rx="6" fill="#3b82f6"/></svg>`);
}

export function catArt(): string {
  return uri(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
  <rect width="400" height="300" fill="#d9c7a7"/><rect y="190" width="400" height="110" fill="#8a5a44"/>
  <ellipse cx="200" cy="200" rx="110" ry="45" fill="#7a6a58"/>
  <circle cx="200" cy="150" r="42" fill="#c98b4e"/>
  <path d="M165 120l10-32 22 20zM235 120l-10-32-22 20z" fill="#c98b4e"/>
  <circle cx="186" cy="148" r="5" fill="#222"/><circle cx="214" cy="148" r="5" fill="#222"/>
  <path d="M194 162q6 6 12 0" stroke="#5a3b22" stroke-width="3" fill="none" stroke-linecap="round"/></svg>`);
}
