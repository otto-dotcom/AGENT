# Polymarket Betting Agent (Vercel Deployment Ready)

This starter gives you a web chat agent you can deploy on Vercel.

## What it does

- Researches active Polymarket markets.
- Fetches order book snapshots.
- Drafts bets first.
- Executes only after exact user confirmation: `CONFIRM BET <bet_id>`.

## Safety model (human-gated execution)

Execution is blocked unless both are true:

1. You explicitly ask to execute.
2. You provide exact confirmation phrase for a drafted bet ID.

If either check fails, no order is submitted.

## Run locally

```bash
npm install
cp .env.example .env
npm run dev
```

Open `http://localhost:3000`.

## Environment variables

- `OPENAI_API_KEY` (required)
- `POLYMARKET_PRIVATE_KEY` (required for live orders)
- `POLYMARKET_FUNDER_ADDRESS` (required for live orders)
- `POLYMARKET_DRY_RUN` (default `true`; set `false` to enable live order submission)

## Deploy to Vercel

```bash
npm i -g vercel
vercel link
vercel --prod
```

When prompted, add the same environment variables in the Vercel project.

## Project files

- `src/app/page.tsx` — chat UI
- `src/app/api/chat/route.ts` — model+tool orchestration endpoint
- `src/agent.ts` — tools and confirmation guardrails
- `src/polymarket.ts` — Polymarket API / CLOB client helpers
