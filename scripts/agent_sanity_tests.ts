import { TaxCalculatorAgent } from "../src/agents/specialized/TaxCalculatorAgent";
import { OrchestratorAgent } from "../src/agents/specialized/OrchestratorAgent";
import type { AgentMessage } from "../src/agents/types";

function sleep(ms: number) { return new Promise(r => setTimeout(r, ms)); }

async function runQuickCommandTests(iterations = 10) {
  const agent = new TaxCalculatorAgent();
  let pass = 0;

  for (let i = 1; i <= iterations; i++) {
    try {
      const tests = [
        { msg: "compute agi from w2 + 1099 w2: 75000 1099: 1200 deductions: 0", expect: /AGI\s*:\s*\$?76,?200/i },
        { msg: "simulate standard vs itemized status: single agi: 75000 itemized: 18000", expect: /Best option: Itemized|Best option: Standard/ },
        { msg: "calc ctc 2 dependents status: single agi: 75000", expect: /Child Tax Credit:\s*\$?4,?000/i }
      ];

      for (const t of tests) {
        const message: AgentMessage = { id: `m-${i}-${Math.random()}`, role: 'user', content: t.msg, timestamp: new Date() };
        const res = await agent.generateResponse(message);
        if (!res.success || !t.expect.test(res.message)) {
          throw new Error(`Unexpected output for: ${t.msg}\nGot: ${res.message}`);
        }
      }
      pass++;
    } catch (e) {
      console.error(`Iteration ${i} failed:`, e instanceof Error ? e.message : e);
    }
    await sleep(100);
  }

  return { iterations, pass, fail: iterations - pass };
}

async function runFilingTriggerTest(iterations = 3) {
  let pass = 0;

  for (let i = 1; i <= iterations; i++) {
    const orch = new OrchestratorAgent();
    const message: AgentMessage = { id: `start-${i}`, role: 'user', content: 'I want to file my taxes', timestamp: new Date() };
    const res = await orch.generateResponse(message);
    if (res.success && /Step 1:\s*Personal Information/i.test(res.message)) pass++; else console.error('Filing trigger output unexpected:', res.message);
    await sleep(100);
  }
  return { iterations, pass, fail: iterations - pass };
}

async function main() {
  console.log("\n=== Agent Sanity Tests ===");
  const quick = await runQuickCommandTests(10);
  console.log(`Quick Commands: PASS ${quick.pass}/${quick.iterations}, FAIL ${quick.fail}`);

  const filing = await runFilingTriggerTest(3);
  console.log(`Filing Trigger: PASS ${filing.pass}/${filing.iterations}, FAIL ${filing.fail}`);

  const overallPass = quick.fail === 0 && filing.fail === 0;
  console.log(`\nOverall: ${overallPass ? 'PASS' : 'FAIL'}`);
  if (!overallPass) process.exitCode = 1;
}

main().catch(err => { console.error(err); process.exit(1); });
