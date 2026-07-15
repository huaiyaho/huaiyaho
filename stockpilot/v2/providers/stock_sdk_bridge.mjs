#!/usr/bin/env node

/**
 * Thin JSON-lines bridge between Python StockPilot and the JavaScript stock-sdk.
 *
 * Input: one JSON object on stdin.
 * Output: one JSON object on stdout.
 *
 * Supported actions:
 * - health
 * - cn_market
 * - quotes
 * - kline
 */

import { StockSDK } from 'stock-sdk';

const sdk = new StockSDK({
  retry: { maxRetries: 2, baseDelay: 500 },
  providerPolicies: {
    eastmoney: {
      timeout: 15000,
      rateLimit: { requestsPerSecond: 3, maxBurst: 3 },
    },
  },
});

function write(payload) {
  process.stdout.write(`${JSON.stringify(payload)}\n`);
}

async function readRequest() {
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  const raw = Buffer.concat(chunks).toString('utf8').trim();
  if (!raw) return { action: 'health' };
  return JSON.parse(raw);
}

function normalizeQuote(q) {
  return {
    symbol: q.symbol ?? q.code ?? null,
    code: q.code ?? q.symbol ?? null,
    name: q.name ?? null,
    market: q.market ?? 'CN',
    price: q.price ?? q.current ?? q.close ?? null,
    open: q.open ?? null,
    high: q.high ?? null,
    low: q.low ?? null,
    previousClose: q.previousClose ?? q.preClose ?? null,
    change: q.change ?? null,
    changePercent: q.changePercent ?? q.percent ?? null,
    volume: q.volume ?? null,
    amount: q.amount ?? q.turnover ?? null,
    turnoverRate: q.turnoverRate ?? null,
    marketCap: q.marketCap ?? q.totalMarketCap ?? null,
    floatMarketCap: q.floatMarketCap ?? null,
    pe: q.pe ?? q.peTtm ?? null,
    pb: q.pb ?? null,
    raw: q,
  };
}

function normalizeBar(bar) {
  return {
    date: bar.date ?? bar.time ?? bar.datetime ?? null,
    open: bar.open ?? null,
    high: bar.high ?? null,
    low: bar.low ?? null,
    close: bar.close ?? null,
    volume: bar.volume ?? null,
    amount: bar.amount ?? bar.turnover ?? null,
    changePercent: bar.changePercent ?? bar.percent ?? null,
    raw: bar,
  };
}

async function main() {
  const request = await readRequest();
  const action = request.action ?? 'health';

  if (action === 'health') {
    write({ ok: true, provider: 'stock-sdk', node: process.version });
    return;
  }

  if (action === 'cn_market') {
    const rows = await sdk.batch.cn({
      concurrency: Number(request.concurrency ?? 5),
    });
    write({ ok: true, action, count: rows.length, data: rows.map(normalizeQuote) });
    return;
  }

  if (action === 'quotes') {
    const symbols = Array.isArray(request.symbols) ? request.symbols : [];
    if (!symbols.length) throw new Error('symbols must not be empty');
    const rows = await sdk.quotes.cnSimple(symbols);
    write({ ok: true, action, count: rows.length, data: rows.map(normalizeQuote) });
    return;
  }

  if (action === 'kline') {
    const symbol = String(request.symbol ?? '').trim();
    if (!symbol) throw new Error('symbol must not be empty');
    const period = request.period ?? 'daily';
    const limit = Number(request.limit ?? 250);
    const rows = await sdk.kline.cn(symbol, { period, limit });
    const list = Array.isArray(rows) ? rows : rows?.data ?? rows?.klines ?? [];
    write({ ok: true, action, symbol, count: list.length, data: list.map(normalizeBar) });
    return;
  }

  throw new Error(`unsupported action: ${action}`);
}

main().catch((error) => {
  write({
    ok: false,
    error: {
      name: error?.name ?? 'Error',
      message: error?.message ?? String(error),
      code: error?.code ?? null,
    },
  });
  process.exitCode = 1;
});
