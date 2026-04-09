# Polymarket API Quickstart (Reference)

This reference was compiled from Polymarket's public docs index (`https://docs.polymarket.com/llms.txt`) and Quickstart page (`https://docs.polymarket.com/quickstart.md`).

## 1) Discover a Market (Public endpoint)

Use Gamma markets API to fetch an active market and token IDs:

```bash
curl "https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=1"
```

Important output fields:
- `question`: market prompt
- `clobTokenIds`: `[yesTokenId, noTokenId]`

## 2) Install an SDK

- TypeScript: `npm install @polymarket/clob-client ethers@5`
- Python: `pip install py-clob-client`
- Rust: `cargo add polymarket-client-sdk`

## 3) Set up Trading Authentication

Trading endpoints require authenticated CLOB client setup:

- Host: `https://clob.polymarket.com`
- Chain ID: `137` (Polygon mainnet)
- Derive API credentials from wallet signer (L1 auth) and use them for L2 trading calls.

For EOA accounts, use signature type `0`.

Funding requirements before buying outcome tokens:
- `USDC.e` for purchases
- `POL` for gas (EOA flow)

## 4) Place a First Limit Order

Workflow:
1. Use `token_id` from step 1 (`clobTokenIds`).
2. Read market metadata for `minimum_tick_size` and `neg_risk` (if SDK needs explicit options).
3. Submit a BUY/SELL limit order.

## Useful follow-up docs

From the docs index (`llms.txt`), these are the most relevant pages to continue:

- Authentication: `https://docs.polymarket.com/api-reference/authentication.md`
- Trading Quickstart: `https://docs.polymarket.com/trading/quickstart.md`
- Fetching Markets: `https://docs.polymarket.com/market-data/fetching-markets.md`
- Markets & Events concepts: `https://docs.polymarket.com/concepts/markets-events.md`
- CLOB OpenAPI spec: `https://docs.polymarket.com/api-spec/clob-openapi.yaml`
- AsyncAPI spec (websocket): `https://docs.polymarket.com/asyncapi.json`

## Notes

- Market data endpoints are public and do not require authentication.
- Trading/order management endpoints require authentication.
- The `llms.txt` index currently exposes API reference pages, conceptual guides, and OpenAPI/AsyncAPI specs in one place.
