import { generateText, tool, type CoreMessage } from "ai";
import { openai } from "@ai-sdk/openai";
import { z } from "zod";
import { fetchMarkets, fetchOrderBook, placeOrder } from "./polymarket";

type ProposedBet = {
  id: string;
  tokenID: string;
  side: "BUY" | "SELL";
  price: number;
  size: number;
  rationale: string;
  createdAt: string;
};

const pendingBets = new Map<string, ProposedBet>();

function createId() {
  return `bet_${Math.random().toString(36).slice(2, 10)}`;
}

export const agentSystemPrompt = `You are a Polymarket research and execution assistant.

Rules:
1) You may research and compare markets.
2) NEVER execute a bet automatically.
3) You can only execute a bet if the user explicitly asks to execute and provides the exact phrase: CONFIRM BET <bet_id>
4) If uncertain, draft a bet and ask for confirmation.
5) Keep risk notes concise and explicit.`;

export const agentTools = {
  list_markets: tool({
    description: "List active Polymarket markets. Optionally filter by search query.",
    parameters: z.object({
      search: z.string().optional(),
    }),
    execute: async ({ search }) => {
      const markets = await fetchMarkets(search);
      return markets.map((m: any) => ({
        question: m.question,
        conditionId: m.conditionId,
        slug: m.slug,
        tokens: m.clobTokenIds,
        endDate: m.endDate,
      }));
    },
  }),

  get_order_book: tool({
    description: "Get top-of-book and liquidity snapshot for a token ID.",
    parameters: z.object({ tokenID: z.string() }),
    execute: async ({ tokenID }) => fetchOrderBook(tokenID),
  }),

  draft_bet: tool({
    description: "Create a pending bet draft that requires explicit confirmation before execution.",
    parameters: z.object({
      tokenID: z.string(),
      side: z.enum(["BUY", "SELL"]),
      price: z.number().positive().max(1),
      size: z.number().positive(),
      rationale: z.string().min(10),
    }),
    execute: async ({ tokenID, side, price, size, rationale }) => {
      const id = createId();
      const bet: ProposedBet = {
        id,
        tokenID,
        side,
        price,
        size,
        rationale,
        createdAt: new Date().toISOString(),
      };
      pendingBets.set(id, bet);
      return {
        message: "Draft bet created. Not executed.",
        bet,
        howToConfirm: `Send exactly: CONFIRM BET ${id}`,
      };
    },
  }),

  execute_bet: tool({
    description: "Execute a previously drafted bet only if exact confirmation phrase is provided.",
    parameters: z.object({
      betID: z.string(),
      confirmation: z.string(),
    }),
    execute: async ({ betID, confirmation }) => {
      const expected = `CONFIRM BET ${betID}`;
      if (confirmation.trim() !== expected) {
        return { executed: false, reason: `Confirmation mismatch. Expected: ${expected}` };
      }

      const bet = pendingBets.get(betID);
      if (!bet) {
        return { executed: false, reason: "Bet draft not found or already executed." };
      }

      const orderResponse = await placeOrder({
        tokenID: bet.tokenID,
        side: bet.side,
        price: bet.price,
        size: bet.size,
      });

      pendingBets.delete(betID);
      return { executed: true, bet, orderResponse };
    },
  }),
};

export async function runAgent(messages: CoreMessage[]) {
  const result = await generateText({
    model: openai("gpt-4o-mini"),
    system: agentSystemPrompt,
    messages,
    tools: agentTools,
    maxSteps: 6,
  });

  return result.text;
}
