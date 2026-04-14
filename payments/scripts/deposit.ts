#!/usr/bin/env tsx
/**
 * Deposit USDC 到 Circle Gateway
 *
 * Usage: npm run deposit -- <amount>
 * Example: npm run deposit -- 10
 */

import { GatewayClient } from "@circle-fin/x402-batching/client";
import * as dotenv from "dotenv";
import * as path from "path";
import { fileURLToPath } from "url";
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.resolve(__dirname, "..", ".env") });

async function main() {
  const amount = process.argv[2] || "10";

  const chain = (process.env.CHAIN || "arcTestnet") as any;
  const privateKey = process.env.BUYER_PRIVATE_KEY as `0x${string}`;

  if (!privateKey || privateKey === "0x0000000000000000000000000000000000000000000000000000000000000001") {
    console.error("❌ 请在 .env 中设置真实的 BUYER_PRIVATE_KEY");
    process.exit(1);
  }

  console.log(`\n🏦 Deposit ${amount} USDC 到 Circle Gateway...`);
  console.log(`   链: ${chain}`);

  const client = new GatewayClient({ chain, privateKey });
  console.log(`   地址: ${client.address}`);

  // 检查Current balance
  const before = await client.getBalances();
  console.log(`\n   Current balance:`);
  console.log(`     钱包 USDC: ${before.wallet.formatted}`);
  console.log(`     Gateway:   ${before.gateway.formattedAvailable} (可用) / ${before.gateway.formattedTotal} (总计)`);

  // Deposit
  console.log(`\n   正在Deposit ${amount} USDC...`);
  const result = await client.deposit(amount);
  console.log(`   ✅ Deposit成功!`);
  console.log(`     金额: ${result.formattedAmount} USDC`);
  console.log(`     Deposit TX: ${result.depositTxHash}`);
  if (result.approvalTxHash) {
    console.log(`     Approval TX: ${result.approvalTxHash}`);
  }

  // 检查新余额
  const after = await client.getBalances();
  console.log(`\n   新余额:`);
  console.log(`     钱包 USDC: ${after.wallet.formatted}`);
  console.log(`     Gateway:   ${after.gateway.formattedAvailable} (可用) / ${after.gateway.formattedTotal} (总计)`);

  console.log(`\n   查看交易: https://testnet.arcscan.app/tx/${result.depositTxHash}\n`);
}

main().catch((err) => {
  console.error("❌ Deposit失败:", err.message);
  process.exit(1);
});
