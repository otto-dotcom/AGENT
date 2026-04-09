import { ClobClient, OrderType, Side } from "@polymarket/clob-client";
import { Wallet } from "ethers";

const HOST = "https://clob.polymarket.com";
const CHAIN_ID = 137;

type PlaceOrderInput = {
  tokenID: string;
  side: "BUY" | "SELL";
  price: number;
  size: number;
};

export async function fetchMarkets(search?: string) {
  const url = new URL("https://gamma-api.polymarket.com/markets");
  url.searchParams.set("active", "true");
  url.searchParams.set("closed", "false");
  url.searchParams.set("limit", "10");

  if (search) {
    url.searchParams.set("search", search);
  }

  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error(`Gamma markets request failed with status ${response.status}`);
  }

  return response.json();
}

export async function fetchOrderBook(tokenId: string) {
  const url = new URL("https://clob.polymarket.com/book");
  url.searchParams.set("token_id", tokenId);

  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error(`CLOB book request failed with status ${response.status}`);
  }

  return response.json();
}

async function buildAuthenticatedClient() {
  const privateKey = process.env.POLYMARKET_PRIVATE_KEY;
  const funder = process.env.POLYMARKET_FUNDER_ADDRESS;

  if (!privateKey || !funder) {
    throw new Error("Missing POLYMARKET_PRIVATE_KEY or POLYMARKET_FUNDER_ADDRESS");
  }

  const signer = new Wallet(privateKey);
  const tempClient = new ClobClient(HOST, CHAIN_ID, signer);
  const creds = await tempClient.createOrDeriveApiKey();

  return new ClobClient(HOST, CHAIN_ID, signer, creds, 0, funder);
}

export async function placeOrder(input: PlaceOrderInput) {
  const isDryRun = (process.env.POLYMARKET_DRY_RUN ?? "true") === "true";
  if (isDryRun) {
    return {
      dryRun: true,
      message: "Dry run enabled; no order submitted.",
      order: input,
    };
  }

  const client = await buildAuthenticatedClient();
  const tickSize = await client.getTickSize(input.tokenID);

  const result = await client.createAndPostOrder(
    {
      tokenID: input.tokenID,
      side: input.side === "BUY" ? Side.BUY : Side.SELL,
      price: input.price,
      size: input.size,
    },
    {
      tickSize,
    },
    OrderType.GTC,
  );

  return {
    dryRun: false,
    orderID: result.orderID,
    status: result.status,
  };
}
