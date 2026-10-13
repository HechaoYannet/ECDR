import type { Context } from 'cordis'
import { BisectionPolicy, LLMPolicy } from './loop.ts'
import type { Scenario } from './loop.ts'

export const name = 'ecdr-run'
export const inject = ['loop', 'physics', 'checker', 'certificates', 'llm']

const SCENARIO: Scenario = {
  name: 'textbook 4-stream',
  streams: [
    { name: 'H1', t_in: 150, t_out: 60, cp: 2.0 },
    { name: 'H2', t_in: 90, t_out: 60, cp: 8.0 },
    { name: 'C1', t_in: 20, t_out: 125, cp: 2.5 },
    { name: 'C2', t_in: 100, t_out: 150, cp: 3.0 },
  ],
  dtMin: 10,
  requirement: 128.25,
}

export async function apply(ctx: Context) {
  const policy = process.argv.includes('--llm') ? new LLMPolicy(ctx) : new BisectionPolicy()
  console.log('[policy] ' + policy.kind)
  const log = await ctx.loop.run(SCENARIO, policy, 3)
  for (const s of log) console.log('[' + s.kind.padEnd(9) + '] ' + s.detail)
}
