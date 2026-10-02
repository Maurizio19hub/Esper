// Icone a tratto (viewBox 24x24): ogni icona è un elenco di path.

const circle = (cx: number, cy: number, r: number) => `M${cx - r} ${cy}a${r} ${r} 0 1 0 ${2 * r} 0a${r} ${r} 0 1 0 ${-2 * r} 0`;
const rect = (x: number, y: number, w: number, h: number, r: number) =>
  `M${x + r} ${y}h${w - 2 * r}a${r} ${r} 0 0 1 ${r} ${r}v${h - 2 * r}a${r} ${r} 0 0 1 ${-r} ${r}h${-(w - 2 * r)}a${r} ${r} 0 0 1 ${-r} ${-r}v${-(h - 2 * r)}a${r} ${r} 0 0 1 ${r} ${-r}z`;

const FILE = ['M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z', 'M14 3v5h5'];

export const ICONS = {
  search: [circle(11, 11, 7), 'm20 20-3.5-3.5'],
  upload: ['M12 16V4m0 0-4 4m4-4 4 4', 'M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3'],
  file: FILE,
  'file-text': [...FILE, 'M9 13h6M9 17h6'],
  image: [rect(3, 4, 18, 16, 2), circle(9, 10, 1.7), 'm21 16-5-5-9 9'],
  tag: ['M20.6 13.4 13.4 20.6a2 2 0 0 1-2.8 0L3 13V4a1 1 0 0 1 1-1h9l7.6 7.6a2 2 0 0 1 0 2.8z', 'M7.5 7.5h.01'],
  x: ['M6 6l12 12M18 6 6 18'],
  trash: ['M4 7h16M10 11v6M14 11v6M6 7l1 12a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1l1-12M9 7V4h6v3'],
  sun: [circle(12, 12, 4), 'M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4'],
  moon: ['M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5z'],
  grid: [rect(4, 4, 7, 7, 1.5), rect(13, 4, 7, 7, 1.5), rect(4, 13, 7, 7, 1.5), rect(13, 13, 7, 7, 1.5)],
  list: ['M8 6h13M8 12h13M8 18h13M3.5 6h.01M3.5 12h.01M3.5 18h.01'],
  check: ['m5 12 5 5 9-10'],
  alert: ['M12 3 2 20h20z', 'M12 10v4M12 17.5v.01'],
  clock: [circle(12, 12, 9), 'M12 7v5l3 2'],
  menu: ['M4 6h16M4 12h16M4 18h16'],
  plus: ['M12 5v14M5 12h14'],
  library: ['M5 4v16M10 4v16M15.2 5.5l3.8 14.5'],
  external: ['M14 4h6v6M20 4 10 14M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5'],
  sparkle: ['M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z', 'M19 17v4M17 19h4'],
  loader: ['M12 3a9 9 0 1 0 9 9'],
  layers: ['m12 3 9 5-9 5-9-5z', 'm3 13 9 5 9-5'],
} satisfies Record<string, string[]>;

export type IconName = keyof typeof ICONS;
