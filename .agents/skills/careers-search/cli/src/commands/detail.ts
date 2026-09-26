// detail: full description for one posting URL returned by `search`.
// Workday and Oracle expose JSON detail endpoints; every other ATS is read from
// the public posting page and stripped to text.

import { decodeEntities, getJson, getText, htmlToText, parseDate, workdayPosted, writeError } from "../helpers.js"

export interface DetailOpts {
  url: string
  format: "json" | "plain"
}

interface Detail {
  title: string | null
  company: string | null
  location: string | null
  date: string | null
  url: string
  description: string
}

async function fetchDetail(url: string): Promise<Detail> {
  const u = new URL(url)

  // https://{host}/en-US/{site}/job/... -> /wday/cxs/{tenant}/{site}/job/...
  if (u.host.endsWith(".myworkdayjobs.com")) {
    const tenant = u.host.split(".")[0]
    const parts = u.pathname.split("/").filter(Boolean)
    const i = parts.indexOf("job")
    const site = parts[i - 1]
    const d = await getJson(`https://${u.host}/wday/cxs/${tenant}/${site}/${parts.slice(i).join("/")}`)
    const p = d.jobPostingInfo ?? {}
    return {
      title: p.title ?? null,
      company: d.hiringOrganization?.name ?? null,
      location: p.location ?? null,
      date: parseDate(p.startDate) ?? workdayPosted(p.postedOn),
      url,
      description: htmlToText(p.jobDescription ?? ""),
    }
  }

  // https://{host}/hcmUI/CandidateExperience/en/sites/{site}/job/{id}
  const oracle = u.pathname.match(/\/sites\/([^/]+)\/job\/(\d+)/)
  if (u.host.includes("oraclecloud.com") && oracle) {
    const [, site, id] = oracle
    const d = await getJson(
      `https://${u.host}/hcmRestApi/resources/latest/recruitingCEJobRequisitionDetails?expand=all&onlyData=true&finder=ById;Id=%22${id}%22,siteNumber=${site}`,
    )
    const r = d.items?.[0] ?? {}
    return {
      title: r.Title ?? null,
      company: null,
      location: r.PrimaryLocation ?? null,
      date: parseDate(r.ExternalPostedStartDate),
      url,
      description: htmlToText(
        [r.ExternalDescriptionStr, r.ExternalQualificationsStr, r.ExternalResponsibilitiesStr].filter(Boolean).join("\n"),
      ),
    }
  }

  // https://apply.careers.microsoft.com/careers/job/{id} is an in-browser app;
  // the PCSX position_details API carries the description.
  const msft = u.pathname.match(/\/careers\/job\/(\d+)/)
  if (u.host === "apply.careers.microsoft.com" && msft) {
    const d = await getJson(
      `https://apply.careers.microsoft.com/api/pcsx/position_details?position_id=${msft[1]}&domain=microsoft.com&hl=en`,
    )
    const p = d.data ?? {}
    return {
      title: p.name ?? null,
      company: "Microsoft",
      location: (p.locations ?? []).join("; ") || null,
      date: p.postedTs ? new Date(p.postedTs * 1000).toISOString().slice(0, 10) : null,
      url,
      description: htmlToText(p.jobDescription ?? ""),
    }
  }

  const html = await getText(url)

  // Phenom pages render in-browser but embed the job in `phApp.ddo = {...};`.
  const ddo = embeddedObject(html, "phApp.ddo =")
  const job = ddo?.jobDetail?.data?.job
  if (job) {
    return {
      title: job.title ?? null,
      company: job.brand ?? null,
      location: job.location ?? null,
      date: parseDate(job.postedDate),
      url,
      description: htmlToText(decodeEntities(job.description ?? "")),
    }
  }

  const title = html.match(/<title[^>]*>([^<]*)<\/title>/i)?.[1]?.trim() ?? null
  return { title, company: null, location: null, date: null, url, description: htmlToText(html) }
}

/** Parse the JSON object literal that follows `marker` in a page, or null. */
function embeddedObject(html: string, marker: string): any {
  const at = html.indexOf(marker)
  const start = at < 0 ? -1 : html.indexOf("{", at)
  if (start < 0) return null
  let depth = 0
  let inStr = false
  for (let i = start; i < html.length; i++) {
    const ch = html[i]
    if (inStr) {
      if (ch === "\\") i++
      else if (ch === '"') inStr = false
    } else if (ch === '"') inStr = true
    else if (ch === "{") depth++
    else if (ch === "}" && --depth === 0) {
      try {
        return JSON.parse(html.slice(start, i + 1))
      } catch {
        return null
      }
    }
  }
  return null
}

export async function runDetail(opts: DetailOpts): Promise<number> {
  try {
    const d = await fetchDetail(opts.url)
    if (opts.format === "plain") {
      process.stdout.write(
        [d.title, [d.company, d.location, d.date].filter(Boolean).join(" · "), d.url, "", d.description].join("\n") + "\n",
      )
    } else {
      process.stdout.write(JSON.stringify(d, null, 2) + "\n")
    }
    return 0
  } catch (e) {
    writeError(e instanceof Error ? e.message : String(e), "DETAIL_FAILED")
    return 1
  }
}
