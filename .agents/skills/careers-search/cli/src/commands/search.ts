// search: query every registered company's careers feed for open roles in the
// registry's target location, then apply the optional keyword/recency filters
// client-side. One company failing never aborts the run: its error is reported
// in `errors` and the rest still return.

import { type Company, type JobResult, loadRegistry, writeError } from "../helpers.js"
import { ADAPTERS } from "./ats.js"

export interface SearchOpts {
  query: string[]
  companies: string[]
  jobage: number | null
  max: number
  format: "json" | "table"
}

const CONCURRENCY = 5

function matchesCompany(c: Company, wanted: string[]): boolean {
  if (wanted.length === 0) return true
  const n = c.name.toLowerCase()
  return wanted.some((w) => n.includes(w.toLowerCase()))
}

/** Keep a job when its title contains any of the query terms (case-insensitive). */
function matchesQuery(j: JobResult, terms: string[]): boolean {
  if (terms.length === 0) return true
  const t = j.title.toLowerCase()
  return terms.some((q) => t.includes(q.toLowerCase()))
}

/**
 * Recency filter. A job with an exact date is kept when within `days`. With no
 * exact date: a "30+ days" label is dropped for windows under 30 days; anything
 * else undated (IBM exposes no date) is kept, since dropping it would guess.
 */
function withinAge(j: JobResult, days: number | null, today = new Date()): boolean {
  if (days === null) return true
  if (j.date) return (today.getTime() - Date.parse(j.date)) / 86400000 <= days
  if (j.posted_label && j.posted_label.includes("+") && days < 30) return false
  return true
}

async function pool<T, R>(items: T[], n: number, fn: (t: T) => Promise<R>): Promise<R[]> {
  const out: R[] = new Array(items.length)
  let i = 0
  await Promise.all(
    Array.from({ length: Math.min(n, items.length) }, async () => {
      while (i < items.length) {
        const k = i++
        out[k] = await fn(items[k])
      }
    }),
  )
  return out
}

function renderTable(rows: JobResult[]): string {
  if (rows.length === 0) return "No results."
  const cols: [string, number, (r: JobResult) => string][] = [
    ["COMPANY", 22, (r) => r.company],
    ["TITLE", 50, (r) => r.title],
    ["LOCATION", 24, (r) => r.location ?? "-"],
    ["DATE", 10, (r) => r.date ?? r.posted_label ?? "-"],
  ]
  const line = (cells: string[]) => cells.map((c, i) => c.slice(0, cols[i][1]).padEnd(cols[i][1])).join("  ")
  const head = line(cols.map((c) => c[0]))
  return [head, "-".repeat(head.length), ...rows.map((r) => line(cols.map((c) => c[2](r))))].join("\n")
}

export async function runSearch(opts: SearchOpts): Promise<number> {
  let registry
  try {
    registry = loadRegistry()
  } catch (e) {
    writeError(`could not read companies.json: ${e instanceof Error ? e.message : String(e)}`, "REGISTRY")
    return 1
  }
  const loc = new RegExp(registry.location_pattern, "i")
  const selected = registry.companies.filter((c) => matchesCompany(c, opts.companies))
  if (selected.length === 0) {
    writeError(`no registry company matches --company ${opts.companies.join(",")}`, "NO_COMPANY")
    return 1
  }

  const manual = selected
    .filter((c) => c.ats === "manual")
    .map((c) => ({ company: c.name, careers_url: c.careers_url ?? null, network: !!c.network, note: c.note ?? null }))
  const live = selected.filter((c) => c.ats !== "manual")

  const errors: { company: string; ats: string; error: string }[] = []
  const perCompany: { company: string; found: number }[] = []
  const batches = await pool(live, CONCURRENCY, async (c) => {
    try {
      const jobs = await ADAPTERS[c.ats as keyof typeof ADAPTERS](c, loc, opts.max)
      perCompany.push({ company: c.name, found: jobs.length })
      return jobs
    } catch (e) {
      errors.push({ company: c.name, ats: c.ats, error: e instanceof Error ? e.message : String(e) })
      return [] as JobResult[]
    }
  })

  const seen = new Set<string>()
  const results = batches
    .flat()
    .filter((j) => matchesQuery(j, opts.query) && withinAge(j, opts.jobage))
    .filter((j) => (seen.has(j.url) ? false : (seen.add(j.url), true)))
    .sort((a, b) => (b.date ?? "").localeCompare(a.date ?? ""))

  // Every live company failing is a broken run, not an empty one.
  if (live.length > 0 && errors.length === live.length) {
    writeError(`every company feed failed: ${errors.map((e) => `${e.company}: ${e.error}`).join("; ")}`, "SEARCH_FAILED")
    return 1
  }

  if (opts.format === "table") {
    process.stdout.write(renderTable(results) + "\n")
    if (errors.length) process.stdout.write(`\nfailed: ${errors.map((e) => `${e.company} (${e.error})`).join(", ")}\n`)
    if (manual.length) process.stdout.write(`manual check: ${manual.map((m) => m.company).join(", ")}\n`)
  } else {
    process.stdout.write(
      JSON.stringify(
        {
          meta: { count: results.length, companies_searched: live.length, per_company: perCompany },
          results,
          errors,
          manual,
        },
        null,
        2,
      ) + "\n",
    )
  }
  return 0
}
