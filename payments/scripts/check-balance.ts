#!/usr/bin/env tsx
/**
 * Query Circle Gateway 余额
 *
 * Usage: npm run balance
 */

import { GatewayClient } from "@circle-fin/x402-batching/client";
import * as dotenv from "dotenv";
import * as path from "path";
import { fileURLToPath } from "url";
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.resolve(__dirname, "..", ".env") });

async function main() {
  const chain = (process.env.CHAIN || "arcTestnet") as any;
  const privateKey = process.env.BUYER_PRIVATE_KEY as `0x${string}`;

  if (!privateKey || privateKey === "0x0000000000000000000000000000000000000000000000000000000000000001") {
    console.error("❌ 请在 .env 中设置真实的 BUYER_PRIVATE_KEY");
    console.log("\n💡 Mock 模式余额:");
    console.log("   Gateway:   10.000000 USDC (模拟)");
    console.log("   钱包:      100.000000 USDC (模拟)");
    process.exit(0);
  }

  console.log(`\n💰 Query余额...`);
  console.log(`   链: ${chain}`);

  const client = new GatewayClient({ chain, privateKey });
  console.log(`   地址: ${client.address}`);

  const balances = await client.getBalances();

  console.log(`\n   钱包 USDC:     ${balances.wallet.formatted}`);
  console.log(`   Gateway 可用:  ${balances.gateway.formattedAvailable}`);
  console.log(`   Gateway 总计:  ${balances.gateway.formattedTotal}`);
  console.log(`   提现中:        ${balances.gateway.formattedWithdrawing}`);
  console.log(`   可提现:        ${balances.gateway.formattedWithdrawable}`);

  console.log(`\n   View on-chain: https://testnet.arcscan.app/address/${client.address}\n`);
}

main().catch((err) => {
  console.error("❌ Query失败:", err.message);
  process.exit(1);
});
