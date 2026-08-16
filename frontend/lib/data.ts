import type { Question, Section, Spec, Template } from "./types";

export const TEMPLATES: Record<string, Template> = {
  saas: {
    kicker: "SaaS dashboard tool",
    title: "Invoice chaser for freelancers",
    body: "Automated payment reminders with a single client-facing status page.",
    meta: "6 answers prefilled · 8-week scope",
    form: {
      idea: "A tool that chases unpaid invoices for freelancers so they stop doing it by hand. It watches due dates and sends the polite follow-up for you.",
      who: "Solo designers and developers who invoice 3–10 clients a month",
      problem: "Freelancers get paid late because chasing is awkward and easy to forget. They lose a day a month to it and still write off invoices.",
      platform: "Web",
      features: "Connect invoices from Stripe or a CSV\nReminder schedule per invoice\nEditable message templates\nPaid / overdue dashboard",
      budget: "8 weeks, under $6k",
      comfort: "Some code",
    },
  },
  churn: {
    kicker: "SaaS dashboard tool",
    title: "Churn early-warning board",
    body: "One screen that ranks accounts by risk with the signal behind each score.",
    meta: "6 answers prefilled · 10-week scope",
    form: {
      idea: "A dashboard that flags which customer accounts are about to cancel, and says why, so a small success team knows who to call today.",
      who: "Customer success leads at 10–40 person B2B SaaS companies",
      problem: "Churn is only visible after it happens. Usage data exists but nobody has time to read it weekly.",
      platform: "Web",
      features: "Risk score per account\nSignal breakdown\nWeekly digest email\nOwner assignment",
      budget: "10 weeks, under $12k",
      comfort: "Technical",
    },
  },
  ops: {
    kicker: "SaaS dashboard tool",
    title: "Studio capacity planner",
    body: "Who is booked, who is free, and what that does to next month's revenue.",
    meta: "6 answers prefilled · 6-week scope",
    form: {
      idea: "A planner that shows a small studio's booked hours against available hours, so they know when to say yes to a new project.",
      who: "Owners of 3–12 person design and dev studios",
      problem: "Capacity lives in spreadsheets and heads. Studios overcommit, then scramble.",
      platform: "Web",
      features: "Per-person weekly capacity\nProject allocation\nRevenue forecast\nOvercommit warnings",
      budget: "6 weeks, under $5k",
      comfort: "Non-technical",
    },
  },
  copilot: {
    kicker: "AI assistant",
    title: "Support reply copilot",
    body: "Drafts answers from your own past tickets, with the source ticket attached.",
    meta: "6 answers prefilled · 9-week scope",
    form: {
      idea: "An assistant that drafts support replies using the team's previous answers, and always shows which past ticket it borrowed from.",
      who: "Two- to six-person support teams handling 200+ tickets a week",
      problem: "Agents rewrite the same answer daily, and new hires cannot find the accepted wording.",
      platform: "Web",
      features: "Draft reply from ticket history\nCited source tickets\nOne-click insert into inbox\nThumbs up/down learning",
      budget: "9 weeks, under $15k",
      comfort: "Technical",
    },
  },
  research: {
    kicker: "AI assistant",
    title: "Interview synthesis assistant",
    body: "Turns user-interview transcripts into themes you can click back to the quote.",
    meta: "6 answers prefilled · 7-week scope",
    form: {
      idea: "An assistant that reads user-interview transcripts and clusters them into themes, keeping every claim linked to the exact quote.",
      who: "Solo researchers and PMs running 5–20 interviews per study",
      problem: "Synthesis takes longer than the interviews, and findings lose their evidence on the way to the deck.",
      platform: "Web",
      features: "Transcript upload\nTheme clustering\nQuote-level citations\nExport to doc",
      budget: "7 weeks, under $9k",
      comfort: "Some code",
    },
  },
  onboard: {
    kicker: "AI assistant",
    title: "Onboarding guide in-app",
    body: "Answers product questions in context, escalating when it is unsure.",
    meta: "6 answers prefilled · 8-week scope",
    form: {
      idea: "An in-app guide that answers new users' questions about the product from the docs, and hands off to a human when confidence is low.",
      who: "Product teams whose trial users drop off in week one",
      problem: "New users hit a wall, do not read docs, and do not open a ticket. They just leave.",
      platform: "Web and mobile",
      features: "Docs-grounded answers\nIn-app launcher\nLow-confidence handoff\nUnanswered-question log",
      budget: "8 weeks, under $11k",
      comfort: "Technical",
    },
  },
  marketplace: {
    kicker: "Local services marketplace",
    title: "Vetted repair pro finder",
    body: "Matches homeowners with background-checked local tradespeople and tracks the job to done.",
    meta: "6 answers prefilled · 10-week scope",
    form: {
      idea: "A marketplace that matches homeowners with vetted local plumbers, electricians and handymen, and tracks the job from request to paid invoice.",
      who: "Homeowners in a single metro area, plus 20–50 independent tradespeople",
      problem: "Homeowners do not know who to trust and call three people for one quote. Tradespeople lose jobs to whoever answers the phone first.",
      platform: "Web and mobile",
      features: "Request with photos and urgency\nVetted pro matching by trade and area\nIn-app quote and message thread\nJob status and payment on completion",
      budget: "10 weeks, under $18k",
      comfort: "Technical",
    },
  },
  routes: {
    kicker: "Local services marketplace",
    title: "Delivery route planner for couriers",
    body: "Builds a driver's daily route from today's orders and tracks delivery proof.",
    meta: "6 answers prefilled · 7-week scope",
    form: {
      idea: "A tool that takes a small courier team's daily orders and builds the fastest delivery route per driver, with photo proof of delivery.",
      who: "Independent courier and last-mile delivery teams with 2–15 drivers",
      problem: "Routes get built by hand each morning and drivers backtrack. Proof of delivery lives in text messages and gets lost.",
      platform: "Mobile",
      features: "Daily order import\nAuto-built route per driver\nPhoto and signature proof of delivery\nCustomer delivery-window notifications",
      budget: "7 weeks, under $9k",
      comfort: "Some code",
    },
  },
  maintenance: {
    kicker: "Local services marketplace",
    title: "Rental maintenance request tracker",
    body: "Tenants report issues with a photo, landlords see one queue instead of scattered texts.",
    meta: "6 answers prefilled · 6-week scope",
    form: {
      idea: "A tracker where tenants submit maintenance issues with a photo, and small landlords manage every property's open requests in one queue instead of texts and calls.",
      who: "Landlords self-managing 5–40 rental units",
      problem: "Requests arrive by text, call and email and get forgotten. Tenants chase the landlord and trust erodes.",
      platform: "Web and mobile",
      features: "Tenant request form with photo\nPer-property request queue\nStatus updates to tenant\nVendor assignment and cost log",
      budget: "6 weeks, under $7k",
      comfort: "Non-technical",
    },
  },
  meds: {
    kicker: "Health and community",
    title: "Medication adherence tracker for caregivers",
    body: "Tracks an aging parent's doses and alerts family the moment one is missed.",
    meta: "6 answers prefilled · 8-week scope",
    form: {
      idea: "A tracker that reminds an elderly parent to take medication and alerts their adult children the moment a dose is missed, without the parent needing to learn an app.",
      who: "Adult children coordinating care for a parent who lives alone",
      problem: "Missed doses go unnoticed until a health scare. Family finds out too late and second-guesses whether care is working.",
      platform: "Mobile",
      features: "Simple dose reminder for the parent\nMissed-dose alert to family\nShared medication schedule\nWeekly adherence summary",
      budget: "8 weeks, under $10k",
      comfort: "Some code",
    },
  },
  volunteer: {
    kicker: "Health and community",
    title: "Volunteer shift scheduler",
    body: "Fills a nonprofit's weekly shifts and chases the gaps automatically.",
    meta: "6 answers prefilled · 6-week scope",
    form: {
      idea: "A scheduler that lets volunteers claim open shifts themselves and automatically reminds people when a shift is still uncovered close to the date.",
      who: "Small nonprofits and community orgs with 20–100 recurring volunteers",
      problem: "Shift coordination happens over a group chat and a shared spreadsheet. Gaps get discovered the day of the shift.",
      platform: "Web and mobile",
      features: "Open shift calendar\nSelf-serve claim and swap\nAutomated gap reminders\nVolunteer hours log for reporting",
      budget: "6 weeks, under $6k",
      comfort: "Non-technical",
    },
  },
  waitlist: {
    kicker: "Health and community",
    title: "Clinic waitlist and no-show reducer",
    body: "Fills cancelled appointment slots automatically from a standby list.",
    meta: "6 answers prefilled · 8-week scope",
    form: {
      idea: "A tool that keeps a standby waitlist for a clinic and automatically offers a cancelled slot to the next eligible patient by text.",
      who: "Small clinics and single-provider practices with 15%+ no-show rates",
      problem: "Cancelled appointments sit empty because refilling them by phone takes staff time nobody has. Revenue and patient access both suffer.",
      platform: "Web",
      features: "Standby waitlist by provider\nAuto text offer on cancellation\nFirst-to-confirm gets the slot\nNo-show and fill-rate reporting",
      budget: "8 weeks, under $12k",
      comfort: "Technical",
    },
  },
};

export const QUESTIONS: Question[] = [
  {
    key: "who",
    label: "Who is it for?",
    help: "The narrower the better — you can widen it after launch.",
    choices: ["Solo freelancers and independents", "Small teams of 2 to 20", "Consumers", "Businesses buying for a team"],
  },
  {
    key: "problem",
    label: "What problem does it solve?",
    help: "What goes wrong today, in one line.",
    choices: ["Saves time on a manual, repeated task", "Replaces a spreadsheet", "Connects two groups of people", "Makes something confusing clear"],
  },
  {
    key: "platform",
    label: "Where does it live?",
    help: "Pick the one place it has to work on day one.",
    choices: ["Web", "Mobile", "Web and mobile", "Not sure yet"],
  },
  {
    key: "features",
    label: "What must it do on day one?",
    help: "The single loop the MVP has to complete.",
    choices: ["Track something and remind me", "Search and browse a collection", "Create and share documents", "Analyse data and report on it"],
  },
  {
    key: "budget",
    label: "What is your timeline and budget?",
    help: "This decides how much gets cut.",
    choices: ["4 weeks, minimal budget", "8 weeks, under $10k", "3 months, funded", "No fixed timeline yet"],
  },
  {
    key: "comfort",
    label: "How technical are you?",
    help: "The stack recommendation follows your answer.",
    choices: ["Non-technical", "Some code", "Technical", "Working with a developer"],
  },
];

export const SHORTS: Record<string, string> = {
  saas: "Chase unpaid invoices",
  churn: "Flag accounts about to cancel",
  ops: "Booked hours against capacity",
  copilot: "Draft replies from past tickets",
  research: "Cluster interviews into themes",
  onboard: "Answer product questions in app",
  marketplace: "Match homeowners with vetted pros",
  routes: "Build a driver's daily route",
  maintenance: "One queue for tenant requests",
  meds: "Alert family on a missed dose",
  volunteer: "Fill shifts without a group chat",
  waitlist: "Refill cancelled slots by text",
};

export const SECTIONS: Section[] = [
  {
    id: "problem",
    num: "01",
    title: "Problem and target user",
    lead: "Solo designers and developers invoice a handful of clients a month and get paid late on a predictable share of them. Chasing is a social cost, not a technical one: the first reminder is easy, the second feels like begging, and the third never gets sent. The result is unpaid work carried for weeks and, on a small number of invoices, written off entirely.",
    groups: [
      {
        label: "Primary user",
        items: [
          { text: "Freelancer billing 3–10 clients a month, invoice values $500–$8,000." },
          { text: "Already sends invoices from Stripe, Wave or a spreadsheet — will not migrate their invoicing." },
          { text: "Comfortable in web tools, not interested in configuring automations." },
        ],
      },
      {
        label: "Explicitly not the user",
        items: [
          { text: "Agencies with a bookkeeper, who need approvals and multi-seat permissions." },
          { text: "Businesses needing legal collections or debt sale." },
        ],
      },
    ],
  },
  {
    id: "features",
    num: "02",
    title: "Core features",
    lead: "The MVP does one job end to end: know what is owed, and send the next reminder without the user writing it. Anything that does not serve that loop is deferred.",
    groups: [
      {
        label: "Must have",
        items: [
          { text: "Invoice import — Stripe connection plus CSV upload, with amount, client, due date." },
          { text: "Reminder schedule — a default cadence (3 days before, day of, +7, +21) editable per invoice." },
          { text: "Message templates — three tones, editable, with merge fields for name, amount, due date." },
          { text: "Status board — every invoice as upcoming, due, overdue or paid, sorted by money at risk." },
          { text: "Send and log — email sends from the user's address, and every send is visible on the invoice." },
        ],
      },
      {
        label: "Should have, post-launch",
        items: [
          { text: "Client-facing status page with a pay link." },
          { text: "Weekly Monday digest: what is owed, what goes out this week." },
          { text: "Partial payment tracking." },
        ],
      },
      {
        label: "Will not have in the MVP",
        items: [
          { text: "Invoice creation or editing — this is not an invoicing tool." },
          { text: "SMS or WhatsApp channels." },
          { text: "Multi-user accounts, roles, or client portals with logins." },
          { text: "Accounting integrations beyond Stripe." },
        ],
      },
    ],
  },
  {
    id: "stories",
    num: "03",
    title: "User stories",
    lead: "Written from the freelancer's side. Each is testable in the built MVP.",
    groups: [
      {
        label: "Setup",
        items: [
          { text: "As a freelancer, I connect Stripe once and see my open invoices without re-entering them." },
          { text: "When a client pays me outside Stripe, I upload a CSV to keep the board accurate." },
          { text: "I pick a reminder cadence once and have it apply to every new invoice." },
        ],
      },
      {
        label: "Day to day",
        items: [
          { text: "As a freelancer, I open the board and see the single largest overdue invoice first." },
          { text: "I approve a queued reminder in one click, or edit the wording before it goes." },
          { text: "When a client tells me payment is coming, I pause reminders on that invoice." },
          { text: "I see that a reminder was sent and opened, so I do not chase twice." },
        ],
      },
    ],
  },
  {
    id: "flows",
    num: "04",
    title: "User flows",
    lead: "Three flows carry the product. The first-run flow must end with at least one real invoice on the board, or the user has no reason to return.",
    groups: [
      {
        label: "First run — signup to first invoice",
        items: [
          { text: "Sign up with email -> connect Stripe or upload CSV -> confirm the imported list -> accept the default cadence -> land on the board with reminders queued." },
          { text: "Fallback: no invoices to import. Offer manual entry of one invoice so the board is never empty." },
        ],
      },
      {
        label: "Reminder approval",
        items: [
          { text: "Digest email or board badge -> queued reminders view -> read the draft -> send, edit or skip -> send is logged on the invoice timeline." },
        ],
      },
      {
        label: "Invoice paid",
        items: [
          { text: "Stripe webhook marks paid -> invoice moves to paid, remaining reminders cancel automatically -> user sees a confirmation on the board." },
          { text: "Manual case: user marks paid themselves, with the same cancellation behaviour." },
        ],
      },
    ],
  },
  {
    id: "stack",
    num: "05",
    title: "Tech stack",
    lead: "Chosen for one developer at a moderate comfort level shipping in eight weeks. Managed services over self-hosted, and no infrastructure the user has to think about.",
    groups: [
      {
        label: "Build",
        items: [
          { text: "Frontend: Next.js with TypeScript and Tailwind — one deployable, server actions for the small amount of backend work." },
          { text: "Backend and data: Supabase (Postgres, auth, row-level security). Tables: user, invoice, reminder, send_log." },
          { text: "Scheduling: a single cron job hitting one endpoint that queues the day's reminders. No queue system in the MVP." },
          { text: "Email: Resend, with domain authentication so reminders send from the freelancer's address." },
          { text: "Payments data: Stripe API for invoice read and paid webhooks." },
          { text: "Hosting: Vercel. Error tracking with Sentry from day one." },
        ],
      },
      {
        label: "Deliberately deferred",
        items: [{ text: "No background worker infrastructure, no Redis, no custom auth." }],
      },
    ],
  },
  {
    id: "risks",
    num: "06",
    title: "Risks and assumptions",
    lead: "The two risks that can end the product are deliverability and trust. Both need a check inside the eight weeks, not after.",
    groups: [
      {
        label: "Risks",
        items: [
          { text: "Deliverability: reminders landing in spam makes the product invisible. Mitigation — require domain verification at setup and show a send-health state." },
          { text: "Trust in automation: users may not let the tool send unsupervised. Mitigation — approval-required by default, auto-send as an opt-in after the first month." },
          { text: "Stripe-only import limits the reachable market. Mitigation — CSV covers the rest at launch; measure how many use it." },
          { text: "Tone: a badly worded reminder damages a client relationship. Mitigation — conservative default copy, always previewable." },
        ],
      },
      {
        label: "Assumptions to validate",
        items: [
          { text: "Freelancers will connect a payment account to a new tool in the first session." },
          { text: "Late payment is frequent enough to justify a recurring subscription, not a one-off." },
          { text: "A reminder from the freelancer's own address performs better than one from the product." },
        ],
      },
    ],
  },
];

// Used by the two entry points that skip real generation (Landing's "see a sample spec"
// and Dashboard's "open" spec item) so SpecView can stay purely prop-driven instead of
// importing SECTIONS itself.
export const SAMPLE_SPEC: Spec = {
  title: "Invoice chaser for freelancers",
  summary:
    "Web app for solo designers and developers invoicing 3–10 clients a month. Scoped to 8 weeks and a low-code build.",
  sections: SECTIONS,
};

export const GEN_LABELS: string[] = [
  "Reading the idea",
  "Framing the problem and user",
  "Cutting features to an MVP",
  "Writing stories and flows",
  "Choosing a stack for your comfort level",
  "Naming risks and assumptions",
];
