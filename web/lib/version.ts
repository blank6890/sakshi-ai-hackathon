/** Normalize a version string into a ``vMAJOR.MINOR.PATCH`` tag form.
 *
 * Accepts PEP 440 / semver forms used in ``deeptutor/__version__.py`` and
 * GitHub release tags (``1.4.0``, ``v1.4.0``, ``1.4.0rc1``, ``v1.0.0-beta.4``)
 * while rejecting git-describe output like ``v1.2.3-5-gabc1234``.
 */
export function normalizeVersionTag(
  raw: string | null | undefined,
): string | null {
  const value = raw?.trim();
  if (!value) return null;
  const match = value.match(
    /^v?(\d+\.\d+\.\d+(?:(?:rc|a|b)\d+|\.dev\d+|\.post\d+|-[A-Za-z][0-9A-Za-z.-]*)?)$/,
  );
  return match ? `v${match[1]}` : null;
}

/** The desktop shell appends ``OpenDeepTutor/<version> (macOS)`` to its user agent. */
const DESKTOP_AGENT = /\bOpenDeepTutor\/\S+ \((macOS)\)/;

/** The client this page runs in, as shown beside the version: ``MacOS`` or ``Web``. */
export function clientPlatform(userAgent?: string | null): string {
  const agent =
    userAgent ?? (typeof navigator === "undefined" ? "" : navigator.userAgent);
  return DESKTOP_AGENT.test(agent) ? "MacOS" : "Web";
}

/** ``Open DeepTutor MacOS v1.7.0`` / ``Open DeepTutor Web v1.7.0``. */
export function clientEditionLabel(
  version: string | null | undefined,
  userAgent?: string | null,
): string {
  const tag = normalizeVersionTag(version);
  return ["Open DeepTutor", clientPlatform(userAgent), tag]
    .filter(Boolean)
    .join(" ");
}
