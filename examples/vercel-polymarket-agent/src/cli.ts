import "dotenv/config";
import readline from "node:readline/promises";
import { stdin as input, stdout as output } from "node:process";
import type { CoreMessage } from "ai";
import { runAgent } from "./agent.js";

async function main() {
  const rl = readline.createInterface({ input, output });
  const history: CoreMessage[] = [];

  console.log("Polymarket Research Agent (Vercel AI SDK)");
  console.log("Type 'exit' to quit.");

  while (true) {
    const userText = await rl.question("\nYou: ");
    if (userText.trim().toLowerCase() === "exit") {
      break;
    }

    history.push({ role: "user", content: userText });

    try {
      const response = await runAgent(history);
      history.push({ role: "assistant", content: response });
      console.log(`\nAgent: ${response}`);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      console.error(`\nAgent error: ${message}`);
    }
  }

  rl.close();
}

main().catch((error) => {
  const message = error instanceof Error ? error.message : String(error);
  console.error(message);
  process.exit(1);
});
