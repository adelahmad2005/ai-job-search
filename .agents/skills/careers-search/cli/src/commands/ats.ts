// One adapter per applicant-tracking system. Each returns the company's open
// postings in the target location, already reshaped to the contract fields.
// Location scoping happens server-side where the ATS supports it, and every
// adapter re-checks client-side against the registry's location pattern.

import {
  type Company,
  type JobResult,
  decodeEntities,
  getJson,
  getText,
  isoDate,
  parseDate,
  toResult,
  workdayPosted,
} from "../helpers.js"

export type Adapter = (c: Company, loc: RegExp, max: number) => Promise<JobResult[]>

const COUNTRY_NAME = "United Arab Emirates"

function need(c: Company, ...keys: (keyof Company)[]): void {
  for (const k of keys) if (!c[k]) throw new Error(`registry entry "${c.name}" (${c.ats}) is missing "${k}"`)
}

// Workday: POST /wday/cxs/{tenant}/{site}/jobs. The first call returns the
// facet tree; pick the location facet whose values match the pattern and
// re-query with it applied. No matching facet value means no local openings.
const workday: Adapter = async (c, loc, max) => {
  need(c, "host", "tenant", "site")
  const api = `https://${c.host}/wday/cxs/${c.tenant}/${c.site}/jobs`
  const first = await getJson(api, { appliedFacets: {}, limit: 20, offset: 0, searchText: "" })

  const byParam = new Map<string, { ids: string[]; count: number }>()
  const walk = (facets: any[], parent: string) => {
    for (const f of facets ?? []) {
      const param = f.facetParameter ?? parent
      for (const v of f.values ?? []) {
        if (v.values) walk([v], param)
        else if (loc.test(v.descriptor ?? "")) {
          const e = byParam.get(param) ?? { ids: [], count: 0 }
          e.ids.push(v.id)
          e.count += v.count ?? 0
          byParam.set(param, e)
        }
      }
    }
  }
  walk(first.facets, "")
  if (byParam.size === 0) return []
  // Apply one facet only (the broadest); several are ANDed by Workday.
  const [param, best] = [...byParam.entries()].sort((a, b) => b[1].count - a[1].count)[0]

  const out: JobResult[] = []
  for (let offset = 0; offset < max; offset += 20) {
    const d = await getJson(api, { appliedFacets: { [param]: best.ids }, limit: 20, offset, searchText: "" })
    for (const j of d.jobPostings ?? []) {
      out.push(
        toResult(c, {
          id: (j.bulletFields?.[0] as string) ?? j.externalPath,
          title: j.title,
          location: j.locationsText ?? null,
          date: workdayPosted(j.postedOn),
          url: `https://${c.host}/en-US/${c.site}${j.externalPath}`,
          posted_label: j.postedOn ?? null,
        }),
      )
    }
    if ((d.jobPostings ?? []).length < 20 || offset + 20 >= (d.total ?? 0)) break
  }
  return out
}

// Oracle HCM Candidate Experience: recruitingCEJobRequisitions finder.
const oracle: Adapter = async (c, loc, max) => {
  need(c, "host", "site")
  const out: JobResult[] = []
  for (let offset = 0; offset < max; offset += 25) {
    const finder = `findReqs;siteNumber=${c.site},limit=25,offset=${offset},location=${encodeURIComponent(COUNTRY_NAME)},sortBy=POSTING_DATES_DESC`
    const d = await getJson(
      `https://${c.host}/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList.secondaryLocations&finder=${finder}`,
    )
    const item = d.items?.[0]
    const reqs = item?.requisitionList ?? []
    for (const r of reqs) {
      const locs = [r.PrimaryLocation, ...(r.secondaryLocations ?? []).map((s: any) => s.Name)].filter(Boolean)
      if (!locs.some((l: string) => loc.test(l))) continue
      out.push(
        toResult(c, {
          id: String(r.Id),
          title: r.Title,
          location: locs.join("; "),
          date: parseDate(r.PostedDate),
          url: `https://${c.host}/hcmUI/CandidateExperience/en/sites/${c.site}/job/${r.Id}`,
          posted_label: null,
        }),
      )
    }
    if (reqs.length < 25 || offset + 25 >= (item?.TotalJobsCount ?? 0)) break
  }
  return out
}

// Phenom People career sites: POST /widgets with the refineSearch ddo. Used by
// the G42 group site, where `brand` names the operating company (CPX, Inception42...).
const phenom: Adapter = async (c, loc, max) => {
  need(c, "host")
  const base = `https://${c.host}`
  const out: JobResult[] = []
  for (let from = 0; from < max; from += 50) {
    const d = await getJson(`${base}/widgets`, {
      lang: "en_global",
      deviceType: "desktop",
      country: "global",
      pageName: "search-results",
      ddoKey: "refineSearch",
      sortBy: "",
      subsearch: "",
      from,
      jobs: true,
      counts: true,
      all_fields: ["country"],
      size: 50,
      clearAll: false,
      jdsource: "facets",
      isSliderEnable: false,
      pageId: "page20",
      siteType: "external",
      keywords: "",
      global: true,
      selected_fields: { country: [COUNTRY_NAME] },
    })
    const rs = d.refineSearch
    const jobs = rs?.data?.jobs ?? []
    for (const j of jobs) {
      const location = j.location ?? j.cityStateCountry ?? null
      if (location && !loc.test(location)) continue
      out.push(
        toResult(c, {
          id: j.jobSeqNo ?? j.jobId,
          title: j.title,
          company: j.brand ? `${c.name} - ${j.brand}` : c.name,
          location,
          date: parseDate(j.postedDate),
          url: `${base}/global/en/job/${j.jobSeqNo}`,
          posted_label: null,
        }),
      )
    }
    if (jobs.length < 50 || from + 50 >= (rs?.totalHits ?? 0)) break
  }
  return out
}

// SAP SuccessFactors Recruiting Marketing career sites: server-rendered search
// table at /search/?locationsearch=... (25 rows per page).
const successfactors: Adapter = async (c, loc, max) => {
  need(c, "host")
  const out: JobResult[] = []
  for (let start = 0; start < max; start += 25) {
    const html = await getText(
      `https://${c.host}/search/?q=&locationsearch=${encodeURIComponent(COUNTRY_NAME)}&startrow=${start}`,
    )
    const rows = [...html.matchAll(/<tr class="data-row"[\s\S]*?<\/tr>/g)].map((m) => m[0])
    const before = out.length
    for (const row of rows) {
      const a =
        row.match(/href="([^"]+)"[^>]*class="jobTitle-link"[^>]*>([^<]+)/) ??
        row.match(/class="jobTitle-link"[^>]*href="([^"]+)"[^>]*>([^<]+)/)
      if (!a) continue
      const location = row.match(/class="jobLocation"[^>]*>\s*([^<]+)/)?.[1]?.trim() ?? null
      if (location && !loc.test(location)) continue
      const href = decodeEntities(a[1])
      out.push(
        toResult(c, {
          id: href.match(/\/(\d+)\/?$/)?.[1] ?? href,
          title: a[2],
          location,
          date: parseDate(row.match(/class="jobDate"[^>]*>\s*([^<]+)/)?.[1]),
          url: `https://${c.host}${href}`,
          posted_label: null,
        }),
      )
    }
    // Location search ranks local jobs first, then pads with other countries:
    // a page with no local match means the local list is exhausted.
    if (rows.length < 25 || out.length === before) break
  }
  return out
}

// Microsoft careers (Eightfold PCSX search API).
const microsoft: Adapter = async (c, loc, max) => {
  const out: JobResult[] = []
  for (let start = 0; start < max; ) {
    const d = await getJson(
      `https://apply.careers.microsoft.com/api/pcsx/search?domain=microsoft.com&query=&location=${encodeURIComponent(COUNTRY_NAME)}&start=${start}`,
    )
    const ps = d.data?.positions ?? []
    for (const p of ps) {
      const locs: string[] = p.locations ?? []
      if (!locs.some((l) => loc.test(l)) && !(p.standardizedLocations ?? []).includes("AE")) continue
      out.push(
        toResult(c, {
          id: String(p.displayJobId ?? p.id),
          title: p.name,
          location: locs.join("; "),
          date: p.postedTs ? isoDate(new Date(p.postedTs * 1000)) : null,
          url: `https://apply.careers.microsoft.com${p.positionUrl}`,
          posted_label: null,
        }),
      )
    }
    start += ps.length
    if (ps.length === 0 || start >= (d.data?.count ?? 0)) break
    // This API answers bursts with 429; pace page requests.
    await new Promise((r) => setTimeout(r, 1500))
  }
  return out
}

// Amazon / AWS: amazon.jobs search.json, filtered to the UAE (country=ARE).
const amazon: Adapter = async (c, loc, max) => {
  const out: JobResult[] = []
  for (let offset = 0; offset < max; offset += 100) {
    const d = await getJson(
      `https://www.amazon.jobs/en/search.json?country=ARE&result_limit=100&offset=${offset}&sort=recent`,
    )
    const jobs = d.jobs ?? []
    for (const j of jobs) {
      const location = j.normalized_location ?? j.location ?? null
      if (location && !loc.test(location)) continue
      out.push(
        toResult(c, {
          id: String(j.id_icims ?? j.id),
          title: j.title,
          // company_name is the hiring legal entity ("Q-Express Documents Trading");
          // report the brand instead.
          company: /web services|AWS/i.test(`${j.company_name} ${j.title}`) ? "AWS" : "Amazon",
          location,
          date: parseDate(j.posted_date),
          url: `https://www.amazon.jobs${j.job_path}`,
          posted_label: null,
        }),
      )
    }
    if (jobs.length < 100 || offset + 100 >= (d.hits ?? 0)) break
  }
  return out
}

// IBM careers search API (Elasticsearch-style). It exposes no posting date.
const ibm: Adapter = async (c, loc, max) => {
  const d = await getJson("https://www-api.ibm.com/search/api/v2", {
    appId: "careers",
    scopes: ["careers2"],
    query: { bool: { must: [] } },
    size: Math.min(max, 100),
    from: 0,
    sort: [{ _score: "desc" }],
    lang: "zz",
    localeSelector: {},
    p: 1,
    sm: { query: "", lang: "zz" },
    _source: ["_id", "title", "url", "field_keyword_19"],
    post_filter: { bool: { must: [{ term: { field_keyword_05: COUNTRY_NAME } }] } },
  })
  return (d.hits?.hits ?? []).map((h: any) =>
    toResult(c, {
      id: h._source.url?.match(/jobId=(\d+)/)?.[1] ?? h._id,
      title: h._source.title,
      location: h._source.field_keyword_19 || COUNTRY_NAME,
      date: null,
      url: h._source.url,
      posted_label: null,
    }),
  )
}

// Greenhouse job board API.
const greenhouse: Adapter = async (c, loc) => {
  need(c, "board")
  const d = await getJson(`https://boards-api.greenhouse.io/v1/boards/${c.board}/jobs`)
  return (d.jobs ?? [])
    .filter((j: any) => loc.test(j.location?.name ?? ""))
    .map((j: any) =>
      toResult(c, {
        id: String(j.id),
        title: j.title,
        location: j.location?.name ?? null,
        date: parseDate(j.first_published ?? j.updated_at),
        url: j.absolute_url,
        posted_label: null,
      }),
    )
}

// Lever postings API.
const lever: Adapter = async (c, loc) => {
  need(c, "board")
  const d = await getJson<any[]>(`https://api.lever.co/v0/postings/${c.board}?mode=json`)
  return d
    .filter((j) => loc.test([j.categories?.location, ...(j.categories?.allLocations ?? [])].join(" ")))
    .map((j) =>
      toResult(c, {
        id: j.id,
        title: j.text,
        location: j.categories?.location ?? null,
        date: j.createdAt ? isoDate(new Date(j.createdAt)) : null,
        url: j.hostedUrl,
        posted_label: null,
      }),
    )
}

// SmartRecruiters public postings API, country-scoped server-side.
const smartrecruiters: Adapter = async (c, loc, max) => {
  need(c, "board")
  const d = await getJson(
    `https://api.smartrecruiters.com/v1/companies/${c.board}/postings?country=ae&limit=${Math.min(max, 100)}`,
  )
  return (d.content ?? [])
    .map((j: any) => {
      const location = [j.location?.city, j.location?.country?.toUpperCase()].filter(Boolean).join(", ")
      return { j, location }
    })
    .filter(({ location }: any) => loc.test(location))
    .map(({ j, location }: any) =>
      toResult(c, {
        id: String(j.id),
        title: j.name,
        location,
        date: parseDate(j.releasedDate),
        url: `https://jobs.smartrecruiters.com/${c.board}/${j.id}`,
        posted_label: null,
      }),
    )
}

// Ashby public job board API.
const ashby: Adapter = async (c, loc) => {
  need(c, "board")
  const d = await getJson(`https://api.ashbyhq.com/posting-api/job-board/${c.board}`)
  return (d.jobs ?? [])
    .filter((j: any) =>
      loc.test([j.location, ...(j.secondaryLocations ?? []).map((s: any) => s.location)].join(" ")),
    )
    .map((j: any) =>
      toResult(c, {
        id: j.id,
        title: j.title,
        location: j.location ?? null,
        date: parseDate(j.publishedAt),
        url: j.jobUrl,
        posted_label: null,
      }),
    )
}

export const ADAPTERS: Record<Exclude<Company["ats"], "manual">, Adapter> = {
  workday,
  oracle,
  phenom,
  successfactors,
  microsoft,
  amazon,
  ibm,
  greenhouse,
  lever,
  smartrecruiters,
  ashby,
}
