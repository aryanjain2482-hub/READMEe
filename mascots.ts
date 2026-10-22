/**
 * Original cartoon mascots for RouteWise (drawn as inline SVG strings).
 * Every agent gets a friendly animal courier; the bandana uses the agent's route colour,
 * so you can match mascot <-> route on the map at a glance.
 * Helper robot "Rooty" gives tips.
 */

export type MascotKind = "cheetah" | "bunny" | "turtle" | "owl";
export const MASCOT_KINDS: MascotKind[] = ["cheetah", "bunny", "turtle", "owl"];
export const MASCOT_NAMES: Record<MascotKind, string> = {
  cheetah: "Zippy the Cheetah",
  bunny: "Bunny Boo",
  turtle: "Tuk-Tuk Turtle",
  owl: "Hooty the Owl",
};

const INK = "#0f172a";

function eyes(big = false): string {
  const r = big ? 8 : 6;
  return `
    <ellipse cx="23" cy="32" rx="${r}" ry="${r + 1}" fill="#fff" stroke="${INK}" stroke-width="2"/>
    <ellipse cx="41" cy="32" rx="${r}" ry="${r + 1}" fill="#fff" stroke="${INK}" stroke-width="2"/>
    <circle cx="24" cy="33" r="3.2" fill="${INK}"/><circle cx="40" cy="33" r="3.2" fill="${INK}"/>
    <circle cx="25.2" cy="31.6" r="1.1" fill="#fff"/><circle cx="41.2" cy="31.6" r="1.1" fill="#fff"/>`;
}

const SMILE = `<path d="M24 43 Q32 51 40 43" fill="none" stroke="${INK}" stroke-width="2.6" stroke-linecap="round"/>`;
const CHEEKS = `<circle cx="15" cy="42" r="3.4" fill="#fb7185" opacity=".6"/><circle cx="49" cy="42" r="3.4" fill="#fb7185" opacity=".6"/>`;

function bandana(color: string): string {
  return `<path d="M12 22 Q32 8 52 22 Q32 17 12 22 Z" fill="${color}" stroke="${INK}" stroke-width="2.4" stroke-linejoin="round"/>
          <path d="M50 21 L58 17 L56 26 Z" fill="${color}" stroke="${INK}" stroke-width="2" stroke-linejoin="round"/>`;
}

export function mascotSvg(kind: MascotKind, color: string, size = 48): string {
  let back = "";
  let head = "";
  let extra = "";
  switch (kind) {
    case "cheetah":
      back = `<circle cx="14" cy="17" r="8" fill="#fbbf24" stroke="${INK}" stroke-width="2.6"/>
              <circle cx="50" cy="17" r="8" fill="#fbbf24" stroke="${INK}" stroke-width="2.6"/>`;
      head = "#fbbf24";
      extra = `<circle cx="17" cy="38" r="1.6" fill="${INK}"/><circle cx="47" cy="38" r="1.6" fill="${INK}"/>
               <circle cx="20" cy="46" r="1.4" fill="${INK}"/><circle cx="44" cy="46" r="1.4" fill="${INK}"/>
               <ellipse cx="32" cy="39" rx="3" ry="2.2" fill="${INK}"/>`;
      break;
    case "bunny":
      back = `<ellipse cx="22" cy="12" rx="6.5" ry="15" fill="#fbcfe8" stroke="${INK}" stroke-width="2.6"/>
              <ellipse cx="42" cy="12" rx="6.5" ry="15" fill="#fbcfe8" stroke="${INK}" stroke-width="2.6"/>
              <ellipse cx="22" cy="13" rx="2.6" ry="9" fill="#f472b6"/><ellipse cx="42" cy="13" rx="2.6" ry="9" fill="#f472b6"/>`;
      head = "#fff1f2";
      extra = `<path d="M30 38 L34 38 L32 41 Z" fill="#f472b6"/>`;
      break;
    case "turtle":
      back = `<path d="M6 62 Q32 36 58 62 Z" fill="#16a34a" stroke="${INK}" stroke-width="2.6" stroke-linejoin="round"/>
              <path d="M20 58 L26 50 M32 56 L32 47 M44 58 L38 50" stroke="${INK}" stroke-width="1.8" fill="none"/>`;
      head = "#86efac";
      extra = `<circle cx="29" cy="39" r="1" fill="${INK}"/><circle cx="35" cy="39" r="1" fill="${INK}"/>`;
      break;
    case "owl":
      back = `<path d="M10 24 L12 6 L26 16 Z" fill="#a16207" stroke="${INK}" stroke-width="2.6" stroke-linejoin="round"/>
              <path d="M54 24 L52 6 L38 16 Z" fill="#a16207" stroke="${INK}" stroke-width="2.6" stroke-linejoin="round"/>`;
      head = "#d6a45c";
      extra = `<path d="M29 38 L35 38 L32 44 Z" fill="#f59e0b" stroke="${INK}" stroke-width="1.6" stroke-linejoin="round"/>`;
      break;
  }
  const face = `<circle cx="32" cy="34" r="22" fill="${head}" stroke="${INK}" stroke-width="3"/>`;
  const bigEyes = kind === "owl";
  const mouth = kind === "owl" || kind === "bunny" ? "" : SMILE;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="${size}" height="${size}">
    ${back}${face}${CHEEKS}${eyes(bigEyes)}${extra}${mouth}${bandana(color)}</svg>`;
}

export type RootyMood = "happy" | "oops" | "think";

/** Helper robot that gives tips in a speech bubble. */
export function rootySvg(mood: RootyMood = "happy", size = 64): string {
  const mouth =
    mood === "oops"
      ? `<path d="M24 47 Q32 40 40 47" fill="none" stroke="${INK}" stroke-width="3" stroke-linecap="round"/>`
      : mood === "think"
      ? `<path d="M26 45 L38 45" stroke="${INK}" stroke-width="3" stroke-linecap="round"/>`
      : `<path d="M23 43 Q32 53 41 43" fill="#fff" stroke="${INK}" stroke-width="3" stroke-linejoin="round"/>`;
  const eyeY = mood === "oops" ? 31 : 32;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="${size}" height="${size}">
    <line x1="32" y1="4" x2="32" y2="13" stroke="${INK}" stroke-width="3"/>
    <circle cx="32" cy="5" r="4" fill="#f43f5e" stroke="${INK}" stroke-width="2.4"/>
    <rect x="9" y="13" width="46" height="44" rx="14" fill="#38bdf8" stroke="${INK}" stroke-width="3"/>
    <rect x="3" y="30" width="6" height="12" rx="3" fill="#facc15" stroke="${INK}" stroke-width="2.4"/>
    <rect x="55" y="30" width="6" height="12" rx="3" fill="#facc15" stroke="${INK}" stroke-width="2.4"/>
    <rect x="15" y="21" width="34" height="26" rx="9" fill="#e0f2fe" stroke="${INK}" stroke-width="2.4"/>
    <circle cx="25" cy="${eyeY}" r="4.2" fill="${INK}"/><circle cx="39" cy="${eyeY}" r="4.2" fill="${INK}"/>
    <circle cx="26.2" cy="${eyeY - 1.4}" r="1.3" fill="#fff"/><circle cx="40.2" cy="${eyeY - 1.4}" r="1.3" fill="#fff"/>
    ${mouth}
  </svg>`;
}
