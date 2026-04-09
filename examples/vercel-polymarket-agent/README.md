# Vercel-style Polymarket Betting Agent (Human-Gated Execution)

This is a starter agent that lets you:

- chat to research markets,
- inspect token order books,
- draft bets,
- and only execute bets when **you** explicitly confirm them.

## Safety model: "only bets I tell it to take"

Execution is hard-gated in two layers:

1. The system prompt forbids automatic execution.
2. The `execute_bet` tool requires an exact phrase:

```text
CONFIRM BET <bet_id>
```

If the phrase does not match exactly, the order is rejected.

## Quick start

1. Install dependencies:

```bash
npm install
```

2. Copy env file and fill credentials:

```bash
cp .env.example .env
```

3. Start in dry-run mode (default):

```bash
npm run dev
```

4. In chat, ask it to:
   - find a market,
   - check token order book,
   - draft a bet,
   - then execute only after you send `CONFIRM BET <bet_id>`.

## Environment variables

- `OPENAI_API_KEY`: model key for the agent.
- `POLYMARKET_PRIVATE_KEY`: wallet private key for live trading.
- `POLYMARKET_FUNDER_ADDRESS`: funder address used by CLOB client.
- `POLYMARKET_DRY_RUN`: defaults to `true`; set to `false` for live order submission.

## Files

- `src/agent.ts`: model + tools + confirmation guardrails.
- `src/polymarket.ts`: market data calls + order placement.
- `src/cli.ts`: interactive chat loop.

## Notes

- Use dry-run mode first.
- You are responsible for strategy, sizing, and regional compliance.
- This starter is for educational use and should be audited before production deployment.
