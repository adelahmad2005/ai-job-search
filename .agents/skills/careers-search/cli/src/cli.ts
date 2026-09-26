#!/usr/bin/env bun
// careers-search: query target companies' own careers sites (Workday, Oracle,
// SuccessFactors, Phenom, Microsoft, Amazon, IBM, Greenhouse, Lever,
// SmartRecruiters, Ashby) for open roles in the registry's location.
// Zero runtime dependencies; the company list lives in ../../companies.json.

import { runSearch, type SearchOpts } from "./commands/search.js"
import { runDetail } from "./commands/detail.js"
import { loadRegistry, writeError } from "./helpers.js"

const HELP = `careers-search — open roles on target companies' own careers sites

USAGE
  bun run src/cli.ts search [--query "<terms>"] [--company "<names>"] [--jobage <days>] [--limit <n>] [--format json|table]
  bun run src/cli.ts detail <posting-url> [--format json|plain]
  bun run src/cli.ts list [--format json|table]

SEARCH FLAGS
  --query, -q <terms>    Comma-separated title terms; a job is kept when its title
                         contains any of them (case-insensitive). Omit for all roles.
  --company <names>      Comma-separated company names (substring match) to search
                         only those registry entries.
  --jobage <days>        Keep jobs posted within N days (client-side; undated jobs are kept).
  --limit, -n <n>        Max postings fetched per company. Default 100.
  --format <fmt>         json (default) | table.

LIST
  Prints the registry: every company, its ATS, and the manual-check entries.

EXAMPLES
  bun run src/cli.ts search --format table
  bun run src/cli.ts search -q "engineer,consultant,presales,analyst,graduate" --jobage 14
  bun run src/cli.ts search --company "nvidia,cisco" --format table
  bun run src/cli.ts detail https://cisco.wd5.myworkdayjobs.com/en-US/Cisco_Careers/job/...
`

const KNOWN: Record<string, Set<string>> = {
  search: new Set(["query", "company", "jobage", "limit", "format", "help", "h"]),
  detail: new Set(["format", "help", "h"]),
  list: new Set(["format", "help", "h"]),
}
const ALIAS: Record<string, string> = { q: "query", n: "limit" }

function parse(argv: string[]): { _: string[]; [k: string]: string | boolean | string[] } {
  const f: { _: string[]; [k: string]: string | boolean | string[] } = { _: [] }
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i]
    if (!a.startsWith("-")) {
      f._.push(a)
      continue
    }
    const key = ALIAS[a.replace(/^-+/, "")] ?? a.replace(/^-+/, "")
    const next = argv[i + 1]
    if (next !== undefined && !next.startsWith("-")) {
      f[key] = next
      i++
    } else f[key] = true
  }
  return f
}

const list = (v: unknown): string[] =>
  typeof v === "string"
    ? v
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean)
    : []

function intFlag(name: string, v: unknown): number | null | undefined {
  if (v === undefined) return undefined
  const n = typeof v === "string" ? Number(v.trim()) : NaN
  if (!Number.isInteger(n) || n < 1) {
    writeError(`--${name} must be a whole number of at least 1, got "${v}"`, "BAD_ARG")
    return null
  }
  return n
}

async function main(): Promise<number> {
  const f = parse(process.argv.slice(2))
  const cmd = f._[0]
  if (!cmd || f.help || f.h) {
    process.stdout.write(HELP)
    return cmd ? 0 : 1
  }
  const known = KNOWN[cmd]
  if (!known) {
    writeError(`Unknown command "${cmd}"`, "BAD_CMD")
    return 1
  }
  for (const k of Object.keys(f)) {
    if (k !== "_" && !known.has(k)) {
      writeError(
        `unknown flag --${k} for '${cmd}' - flags are never silently ignored, because a discarded filter changes what the search returns; see --help`,
        "UNKNOWN_FLAG",
      )
      return 1
    }
  }
  const fmt = typeof f.format === "string" ? f.format : "json"

  if (cmd === "search") {
    if (!["json", "table"].includes(fmt)) {
      writeError(`--format must be json or table, got "${fmt}"`, "BAD_ARG")
      return 1
    }
    const jobage = intFlag("jobage", f.jobage)
    const limit = intFlag("limit", f.limit)
    if (jobage === null || limit === null) return 1
    const opts: SearchOpts = {
      query: list(f.query),
      companies: list(f.company),
      jobage: jobage ?? null,
      max: limit ?? 100,
      format: fmt as SearchOpts["format"],
    }
    return runSearch(opts)
  }

  if (cmd === "detail") {
    const url = f._[1]
    if (!url || !/^https?:\/\//.test(url)) {
      writeError("detail requires a posting URL from a search result", "NO_URL")
      return 1
    }
    return runDetail({ url, format: fmt === "plain" ? "plain" : "json" })
  }

  // list
  const reg = loadRegistry()
  if (fmt === "table") {
    for (const c of reg.companies) {
      process.stdout.write(
        `${c.name.padEnd(28)} ${c.ats.padEnd(15)} ${c.network ? "network " : "        "}${c.careers_url ?? c.host ?? ""}\n`,
      )
    }
  } else process.stdout.write(JSON.stringify(reg, null, 2) + "\n")
  return 0
}

main()
  .then((code) => process.exit(code))
  .catch((e) => {
    writeError(e instanceof Error ? e.message : String(e), "INTERNAL_ERROR")
    process.exit(1)
  })
