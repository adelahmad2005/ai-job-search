// Shared plumbing for careers-search: the company registry, HTTP with bounded
// retries, date normalisation, and the portal-skill contract result shape.
// Every source is a public, unauthenticated careers feed — the same JSON the
// company's own careers page calls from the browser.

import { readFileSync } from "node:fs"
import { dirname, join } from "node:path"
import { fileURLToPath } from "node:url"

export const REGISTRY_PATH = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "companies.json")

export type Ats =
  | "workday"
  | "oracle"
  | "phenom"
  | "successfactors"
  | "microsoft"
  | "amazon"
  | "ibm"
  | "greenhouse"
  | "lever"
  | "smartrecruiters"
  | "ashby"
  | "manual"

export interface Company {
  name: string
  ats: Ats
  /** Referral-network company (Dell, NVIDIA, Red Hat, VMware/Broadcom, IBM). */
  network?: boolean
  /** Careers page a human can open; required for manual entries. */
  careers_url?: string
  note?: string
  // ATS-specific identifiers; which ones apply depends on `ats`.
  host?: string
  tenant?: string
  site?: string
  board?: string
}

export interface Registry {
  location_pattern: string
  companies: Company[]
}

export function loadRegistry(): Registry {
  return JSON.parse(readFileSync(REGISTRY_PATH, "utf-8")) as Registry
}

/**
 * A search result in the portal-skill contract shape. Missing values are
 * `null`, never omitted. `posted_label` keeps the ATS's own wording when it
 * only gives a relative age ("Posted 30+ Days Ago"), so an unknown exact date
 * is never guessed.
 */
export interface JobResult {
  id: string
  title: string
  company: string
  location: string | null
  date: string | null
  url: string
  ats: Ats
  network: boolean
  posted_label: string | null
}

export function toResult(c: Company, r: Omit<JobResult, "company" | "ats" | "network"> & { company?: string }): JobResult {
  return {
    id: r.id,
    title: decodeEntities(r.title).trim() || "(untitled)",
    company: r.company || c.name,
    location: r.location ? decodeEntities(r.location).trim() : null,
    date: r.date,
    url: r.url,
    ats: c.ats,
    network: !!c.network,
    posted_label: r.posted_label,
  }
}

export function writeError(error: string, code: string): void {
  process.stderr.write(JSON.stringify({ error, code }) + "\n")
}

const UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"

/**
 * Fetch with a 20 s timeout. Retries 5xx up to twice with backoff. A 429 is
 * never retried: it is surfaced so the caller backs off instead of hammering
 * a company's careers site.
 */
export async function http(url: string, init: { method?: string; json?: unknown; accept?: string } = {}): Promise<Response> {
  let delay = 800
  for (let attempt = 0; ; attempt++) {
    const res = await fetch(url, {
      method: init.method ?? (init.json !== undefined ? "POST" : "GET"),
      headers: {
        "User-Agent": UA,
        Accept: init.accept ?? "application/json",
        ...(init.json !== undefined ? { "Content-Type": "application/json" } : {}),
      },
      body: init.json !== undefined ? JSON.stringify(init.json) : undefined,
      redirect: "follow",
      signal: AbortSignal.timeout(20000),
    })
    if (res.status >= 500 && attempt < 2) {
      await new Promise((r) => setTimeout(r, delay))
      delay *= 2
      continue
    }
    if (!res.ok) throw new Error(`HTTP ${res.status} from ${new URL(url).host}`)
    return res
  }
}

export async function getJson<T = any>(url: string, json?: unknown): Promise<T> {
  const res = await http(url, { json })
  return (await res.json()) as T
}

export async function getText(url: string): Promise<string> {
  const res = await http(url, { accept: "text/html" })
  return await res.text()
}

export function isoDate(d: Date): string {
  return d.toISOString().slice(0, 10)
}

/** Parse an absolute date string ("2026-09-25", "Sep 10, 2026", ISO timestamp); null if unparseable. */
export function parseDate(s: string | null | undefined): string | null {
  if (!s) return null
  const t = Date.parse(s.trim())
  return Number.isNaN(t) ? null : isoDate(new Date(t))
}

/**
 * Workday's relative "Posted N Days Ago" label → a date. "30+ Days Ago" has no
 * exact date, so it returns null and the caller keeps the label.
 */
export function workdayPosted(label: string | null | undefined, today = new Date()): string | null {
  if (!label) return null
  const l = label.toLowerCase()
  if (l.includes("+")) return null
  if (l.includes("today")) return isoDate(today)
  if (l.includes("yesterday")) return isoDate(new Date(today.getTime() - 86400000))
  const m = l.match(/(\d+)\s+days?/)
  return m ? isoDate(new Date(today.getTime() - Number(m[1]) * 86400000)) : null
}

function numericEntity(cp: number): string {
  return cp >= 0 && cp <= 0x10ffff ? String.fromCodePoint(cp) : ""
}

export function decodeEntities(text: string): string {
  return text
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;|&apos;/g, "'")
    .replace(/&nbsp;/g, " ")
    .replace(/&#(\d+);/g, (_, d) => numericEntity(parseInt(d, 10)))
    .replace(/&#[xX]([0-9a-fA-F]+);/g, (_, h) => numericEntity(parseInt(h, 16)))
}

export function htmlToText(html: string): string {
  return decodeEntities(
    html
      .replace(/<(script|style)[\s\S]*?<\/\1>/gi, "")
      .replace(/<br\s*\/?>|<\/(p|div|li|h[1-6]|tr)>/gi, "\n")
      .replace(/<li[^>]*>/gi, "- ")
      .replace(/<[^>]+>/g, ""),
  )
    .replace(/[ \t]+/g, " ")
    .replace(/\n\s*\n\s*\n+/g, "\n\n")
    .trim()
}
