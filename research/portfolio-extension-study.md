# Can `agentic-portfolio-public` host the longevity-loop mission tracker?

Study of the LOCAL repo `/Users/jialiang.wu/Documents/Projects/agentic-portfolio-public`
(Next.js 15 App Router + CopilotKit 1.5.20 + Tailwind 3). All claims below are verified
against the actual source; file paths are absolute-relative to that repo root.

---

## 1. Sections / instances model

There are **two content layers**, and both matter for a tracker.

### (a) The default "portfolio" site — file + KV backed
- **Layout config** lives in `content/portfolio.yaml`, schema in `lib/portfolio.ts`
  (`PortfolioConfig` = `theme`, `sections[]`, `articles[]`, `writingSources[]`,
  `overrides{}`). `readPortfolioAsync()` reads KV key `portfolio:config` **over** the
  YAML seed; `writePortfolioDurable()` writes KV when `POSTGRES_URL` is set, else the
  local fs (serverless fs is read-only → falls back to localStorage client-side).
  So content is **both** file-backed (committed seed) **and** KV-backed (durable live edits).
- **Built-in sections are a FIXED registry**: `SECTION_DEFAULTS` in `lib/portfolio.ts`
  (`practices, projects, writing, receipts, job-fit, deep-dives, compass, values`). YAML
  controls order/visibility/labels only; unknown ids are dropped, missing known ids are
  re-appended. Each is rendered by a `switch` in `components/Portfolio.tsx → renderBody()`.
  **A NEW built-in section = 3 edits**: add an id to `SECTION_DEFAULTS`, add a component,
  add a `case` in `renderBody()`.
- **Custom sections already exist at runtime, no code**: the agent action `addSection`
  (`components/useContentActions.ts`) creates `id = custom-<slug>` with an `items[]` array
  of `{title, body, tag?, url?}` cards, rendered by `CustomSectionBody` in
  `components/sections.tsx`. But these are **static text/link card grids** — no live data,
  no charts.

### (b) The "instances" concept — YES, supports multiple portfolios/pages
- `content/instances/index.ts` holds `INSTANCES` (a registry of `InstanceConfig` packs) and
  `getActiveInstance()`, selected by the **`INSTANCE` env var** (one active instance per
  deploy; default `portfolio`). Type is `InstanceConfig` in
  `packages/core/src/instance-types.ts`: `entity / story / agent / sections /
  content{offerings,outcomes,writings}` + `proof/scout/network/owner/storage`.
- A **new instance** can be: a `.ts` pack (registered in `INSTANCES`), a dropped-in
  `content/instances/<slug>.json` (rendered with no code change — see `loadJsonPack`), or a
  **KV-hosted** instance at `/p/<slug>` created by `/api/make` (the no-code "Maker").
- A non-portfolio instance renders via `components/InstanceSite.tsx` (generic hero +
  principles + offerings + writings + outcomes card grids, its own grounded agent). See the
  branch in `app/page.tsx`.
- A **new route/page** is just standard Next.js: the repo already has `app/network`,
  `app/society`, `app/make`, `app/p/[slug]`, `app/recover`. Adding `app/longevity/page.tsx`
  is idiomatic.

**Bottom line:** a tracker can be (i) a new built-in section on the portfolio, (ii) a new
custom section (text cards, zero code), (iii) a standalone `InstanceConfig`/`/p/<slug>`, or
(iv) a new `app/<route>` page. All four are supported patterns.

---

## 2. The agent / chat — working, grounding-context based (NOT RAG)

- **Two surfaces, both live:** the CopilotKit sidebar (`components/Copilot.tsx` →
  `CopilotSidebar`, runtime `/api/copilotkit/route.ts`) for humans, and the A2A JSON-RPC
  endpoint `/api/a2a/route.ts` for other agents (discovered via
  `/api/agent-card/route.ts`, rewritten to `/.well-known/agent-card.json` in
  `next.config.mjs`).
- **How it gets knowledge:** *not* RAG, no vector store. The context is a **grounding blob**
  built from the config/content and handed to the model:
  - Copilot: `app/page.tsx` builds a big `agentContext` JSON (profile, mission, values,
    projects, 12X practices, capabilities) and registers it client-side via
    `useCopilotReadable` (`components/Copilot.tsx`, plus more readables inside
    `components/Portfolio.tsx`). The model is instructed to answer **only** from it.
  - A2A: `buildEvidence()` in `/api/a2a/route.ts` assembles a `~12k-char` JSON evidence
    string; instances use `instanceEvidence(config)` (`instance-types.ts`, budget
    `12k`–`120k` chars).
- **Could it answer longevity-loop questions?** Yes — **if** the mission/progress data is
  added to that grounding context (as instance `content`, a new readable, or the Deep Dives
  feed). The limit is size: everything must fit in the capped in-context blob.
- **LLM provider/keys:** the free-LLM survival chain `lib/llm.ts` / `lib/llm-complete.ts`.
  Needs **any one** of `NVIDIA_API_KEY`, `GROQ_API_KEY`, `GEMINI_API_KEY`, `OPENAI_API_KEY`
  (all OpenAI-compatible). Copilot leads with Gemini (largest free daily quota). No key →
  A2A returns a static grounded summary; Copilot returns 503.

---

## 3. Reusable API routes (`app/api/`)

| Route | What it does |
|---|---|
| `copilotkit` | CopilotKit runtime — the on-page chat brain; free-LLM failover chain; rate-limited. |
| `a2a` | A2A JSON-RPC 2.0 endpoint — other agents ask/verify/role-fit, grounded + honest. |
| `agent-card` | Serves the A2A Agent Card (deploy + per-`/p/<slug>`). |
| `deep-dive` | **(owner)** Fetch a source URL → LLM distills digest + knowledge graph + skills → ingest. |
| `ingest-knowledge` | **(owner / `x-ingest-secret`)** POST a distilled artifact into the durable Deep Dives feed; GET is public. |
| `repo-digest` | Fetch a **public GitHub repo** README + file/dir tree + metadata (for grounding a section). |
| `repo-activity` | Aggregate the owner's GitHub PR activity (last 30d) per repo. |
| `sync` | Pull a hosted portfolio's public sources (GitHub + YouTube) on demand/cron; owner or cron secret. |
| `sync-writing` | Pull Substack/Medium/RSS feeds into `articles` (owner button or weekly cron). |
| `sync-projects` | **(owner)** Sync GitHub repos into Projects. |
| `scout` / `standing` | Compass "what's next" draft (deepen/widen/lengthen/heighten); TRUE-standing scoring. |
| `opportunities` | **(owner)** Search public discussions, DRAFT outreach replies (never posts). |
| `lead` | Capture a qualified lead (public POST) / read the pipeline (owner GET). |
| `join` | Society/mailing-list intake (public POST, owner GET). |
| `growth` | Network viral-coefficient dashboard (public read). |
| `make` | No-code Maker: generate + host an InstanceConfig at `/p/<slug>`. |
| `portfolio` | Read/persist the editable layout config (owner-gated write). |
| `registry` / `registry/ask` | Portfolio-network "DNS": search/join nodes; fan-out ask across nodes. |
| `verify-resume` / `verified-resume` / `job-fit` / `fetch-article` / `feedback*` / `owner*` / `recover` / `badge` / `health` | résumé audit, JD-fit scoring, article metadata fetch, feedback, owner/recovery, SVG badge, health. |

**Directly reusable for the tracker:**
- **Track milestones/progress:** no purpose-built milestone store, but `/api/portfolio`
  (KV config + custom sections) or `/api/ingest-knowledge` (durable feed) or `lib/storage.ts`
  KV directly. `/api/scout`+Compass model "next moves"/roadmap.
- **Answer questions:** `/api/copilotkit` + `/api/a2a`.
- **Outreach / lead capture:** `/api/lead`, `/api/join`, `/api/opportunities`.
- **Ingest external data:** `/api/ingest-knowledge`, `/api/deep-dive`, `/api/repo-digest`,
  `/api/repo-activity`, `/api/sync`, plus `lib/source-fetch.ts` (SSRF-guarded public fetch).

---

## 4. Rendering / UI + infographics/animation

- **Design system:** CSS-variable **theme seam** (`app/themes.css`, 9 brand themes via
  `data-theme` on `<html>`), tokens mapped to Tailwind in `tailwind.config.ts`
  (`canvas/surface/edge/ink/muted/accent/accent2/onaccent`, `font-{sans,display,mono}`,
  `radius-theme`). Utility classes `.card`, `.chip`, `.section-title` in `app/globals.css`.
  `StyleSwitcher` swaps themes live.
- **Components:** section bodies (`Projects`, `Articles`, `Receipts`, `JobFit`, `Deepen`,
  `Compass`, `Network`), card grids (`components/sections.tsx`), CSS sliders
  (`PracticesSlider`, `ValuesSlider`), owner/share UI. All **card-grid / list** layouts.
- **Charting / animation / infographic capability: essentially NONE.** `package.json` has
  **no** framer-motion, recharts, d3, three, or chart.js. The only "graphics" are CSS
  transitions (`app/globals.css`, `themes.css`) and one server-generated **SVG badge**
  (`app/api/badge/route.ts`). `components/Network.tsx` is a **searchable list**, not a
  node-graph visualization. So progress bars/charts/a field-graph are **net-new** work
  (hand-rolled SVG or add a library).

---

## 5. Data ingestion from the external longevity-loop repo

There **is** an established pattern for pulling external/live data server-side:
- `/api/repo-digest` fetches a public GitHub repo's README + tree + metadata (but README/tree,
  not arbitrary raw file contents like `data/*.yml`).
- `/api/repo-activity` fetches GitHub PR activity via the search API.
- `lib/source-fetch.ts` (`fetchSourceText`) + `/api/deep-dive` fetch **any** public URL
  (bounded, SSRF-guarded) and strip HTML → text.
- `/api/sync` + `/api/sync-writing` pull public GitHub/YouTube/RSS feeds, and **`vercel.json`
  already schedules a daily cron** to `/api/sync` — the "fetch-on-cron" pattern.
- Pages are `export const dynamic = "force-dynamic"`, so a page could also `fetch(...)` at
  request time.

**For longevity-loop specifically:**
- Pulling GitHub Pages `site/data.json` + `site/graph.json`: no existing route consumes them,
  but a **thin new route** (`fetch(rawUrl).then(r => r.json())`) fits the pattern in minutes;
  don't route JSON through `htmlToText` (it would mangle it) — parse directly.
- Consuming `data/*.yml` / executions / roadmap / frontier: `repo-digest` gives the tree; raw
  file contents need a direct `raw.githubusercontent.com` fetch (trivial to add).
- `graph.json` **visualization** has no home — `Network.tsx` is not a graph renderer — so any
  field-graph visual is net-new UI.

---

## 6. Deploy

- **Vercel**, `vercel.json` (`framework: nextjs`, daily cron `/api/sync`). `next.config.mjs`
  adds `.well-known` + `/p/<slug>` rewrites.
- **Public reads vs owner-gated writes:** owner gate via `PORTFOLIO_OWNER_TOKEN` /
  `lib/owner.ts` `isOwnerRequest()` (`x-portfolio-owner` header), or headless secrets
  (`SCOUT_SECRET`, `INGEST_SECRET`, `CRON_SECRET`/`x-sync-secret`). Reads are public +
  rate-limited (`lib/rate-limit.ts`).
- **Durability:** optional Postgres/Neon KV (`POSTGRES_URL`/`DATABASE_URL`, `lib/storage.ts`,
  lazy `kv_store` table). Without it, live writes fall back to localStorage / committed files.

---

## Verdict

**Adding the longevity-loop tracker as a section/instance of THIS app is clearly easier and
better than a standalone webapp for the conversational + content + ingestion layers — but it
is NOT a drop-in for the *visual* tracker.** The repo already gives you, for free, a grounded
agent (CopilotKit + A2A + free-LLM chain), a multi-instance/multi-section content model with
owner-gated durable writes, a Vercel-cron external-fetch pattern, and a themable design
system — so a "mission tracker" page that lets an agent answer questions about
mission/progress/roadmap, ingest the longevity-loop repo data on a schedule, and capture
interested leads is mostly **wiring, not building**. The two things it genuinely lacks are
(1) any charting/graph/animation capability and (2) real retrieval — so a rich
infographic/`graph.json` field-graph and a large/growing dataset both require net-new code.
If the tracker is primarily *chat + text/card status + progress that you're willing to render
as simple SVG/CSS*, extend this app. If it's primarily a *data-viz dashboard / interactive
graph*, you'll be writing that part from scratch either way — but still cheaper here (you
inherit the agent, auth, ingestion, cron, and hosting).

### Top 3 reusable pieces
1. **The grounded agent stack** — `/api/copilotkit` (sidebar) + `/api/a2a` (agent-to-agent) +
   `lib/llm.ts` free-LLM survival chain. Inject longevity mission/progress into the grounding
   context (via instance `content`, a new `useCopilotReadable`, or the Deep Dives feed) and it
   answers Q&A / fit / verify with no new agent code. Needs one free LLM key.
2. **The instance/section content model + owner-gated durable writes** —
   `InstanceConfig` packs (`content/instances/*`, `/p/<slug>`, `/api/make`), the fixed+custom
   section system (`lib/portfolio.ts`, `useContentActions.ts`), `/api/portfolio`,
   `/api/ingest-knowledge`, and KV storage (`lib/storage.ts`). A tracker page/section with no
   new plumbing.
3. **External-data ingestion + Vercel cron** — `/api/repo-digest`, `/api/repo-activity`,
   `/api/sync`, `lib/source-fetch.ts`, and the existing daily cron in `vercel.json`. The
   template for pulling longevity-loop's GitHub/Pages data on a schedule (add ~1 thin JSON route).

### Top 2 risks / gaps
1. **No visualization capability.** Zero charting/graph/animation libraries (no recharts, d3,
   framer-motion, chart.js); UI is card grids + CSS + one SVG badge, and `Network.tsx` is a
   list, not a graph. Progress charts and the `graph.json` field-graph are net-new (hand-rolled
   SVG or add a library). Custom sections are text/link cards only.
2. **Grounding, not RAG.** Agent knowledge is a size-capped in-context blob (~12k–120k chars),
   injected per request — a large or continuously-growing longevity dataset won't fit and would
   need a summarize/ingest step (the Deep Dives pipeline) or a real retrieval layer. Also,
   durable *shared* writes require Postgres/Neon (`POSTGRES_URL`) and the agent requires an LLM
   key; without them the app degrades to localStorage/static.
