import type { Context } from 'cordis'
import { writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

export const name = 'ecdr-audit'
export const inject = ['llm', 'physics']

const HERE = dirname(fileURLToPath(import.meta.url))

const STREAMS = [
  { name: 'H1', t_in: 150, t_out: 60, cp: 2.0 },
  { name: 'H2', t_in: 90, t_out: 60, cp: 8.0 },
  { name: 'C1', t_in: 20, t_out: 125, cp: 2.5 },
  { name: 'C2', t_in: 100, t_out: 150, cp: 3.0 },
]
const DT = 10
const QSTAR = 142.5

// Ground truth from the corrected model (step 71). Two are valid counterexamples and two are
// not, and W3's claimed value is the naive "untouched duty" figure, which is BELOW the truth -
// so a model that applies only that rule accepts it and is wrong.
const WITNESSES = [
  { id: 'W1', matches: [[0, 2], [1, 2]], claimed: 142.5, true_Q_H: 150.0, valid: false },
  { id: 'W2', matches: [[0, 2], [0, 3], [1, 2]], claimed: 142.5, true_Q_H: 142.5, valid: true },
  { id: 'W3', matches: [[0, 3], [1, 3]], claimed: 262.5, true_Q_H: 332.5, valid: false },
  { id: 'W4', matches: [[0, 2], [0, 3], [1, 2], [1, 3]], claimed: 142.5, true_Q_H: 142.5, valid: true },
]

/**
 * The witness audit, in ONE call.
 *
 * Finding 043: an agent rejected a counterexample I offered and was right, but the reasoning
 * was discarded and the multi-turn setup could not say whether it was auditing or merely
 * disagreeing. Here four claimed witnesses are presented - two genuine, two false - so that a
 * model which rejects everything scores no better than one which accepts everything.
 *
 * W3 is the discriminator. Its claimed 262.5 is exactly C1's duty, the figure a naive
 * "count the untouched stream's duty" rule produces, and the true value is 332.5. A model that
 * knows only the shortcut accepts W3 and is wrong.
 */
export async function apply(ctx: Context) {
  if (!process.argv.includes('--audit')) return

  const lines = STREAMS.map((s, i) => '  ' + i + ' = ' + s.name + ': ' + s.t_in + ' -> '
    + s.t_out + ' C, cp = ' + s.cp + ' kW/K').join('\n')
  const wit = WITNESSES.map(w => '  ' + w.id + ': matches ' + JSON.stringify(w.matches)
    + ', claimed minimum hot utility = ' + w.claimed + ' kW').join('\n')

  const system = [
    'You are checking another engineer\'s work on a heat exchanger network problem.',
    'You are given streams, a minimum approach temperature, and several claimed networks with',
    'the minimum hot utility their author says each one needs.',
    '',
    'For each claim, decide whether the number is correct, and if it is not, state the true',
    'minimum hot utility for that network. A network is defined by its matches: heat may pass',
    'only between the two streams a match names, and a stream that no match names can only be',
    'served by utility.',
    '',
    'Answer with ONE JSON array and nothing else:',
    '[{"id": "W1", "claim_correct": true|false, "true_value": <number>, "why": "<25 words>"}, ...]',
  ].join('\n')

  const user = [
    'Streams (0-indexed; hot streams must be cooled, cold streams heated):',
    lines,
    '',
    'Minimum approach temperature dt_min = ' + DT + ' C.',
    'A network "meets the requirement" if its minimum hot utility is <= ' + QSTAR + ' kW.',
    '',
    'Claimed networks:',
    wit,
    '',
    'Audit all four claims.',
  ].join('\n')

  console.log('[audit] 4 claimed witnesses, 2 genuine and 2 false, ONE model call')
  const t0 = Date.now()
  const res = await ctx.llm.completeFull(system, user)
  console.log('[llm] ' + ((Date.now() - t0) / 1000).toFixed(1) + ' s, '
    + res.reasoningTokens + ' reasoning tokens, ' + res.reasoning.length + ' chars')

  const out = join(HERE, '..', '..', 'runs', 'witness_audit.json')
  writeFileSync(out, JSON.stringify({
    reasoning: res.reasoning, content: res.content,
    reasoningTokens: res.reasoningTokens, seconds: (Date.now() - t0) / 1000,
    ground_truth: WITNESSES,
  }, null, 1))
  console.log('[saved] runs/witness_audit.json  (reasoning captured this time)')

  const m = res.content.match(/\[[\s\S]*\]/)
  if (!m) { console.log('[fail] no JSON array'); return }
  const parsed: Array<{ id: string, claim_correct: boolean, true_value: number }> =
    JSON.parse(m[0])
  const truth = new Map(WITNESSES.map(w => [w.id, w]))
  console.log('')
  console.log('  ' + 'id'.padEnd(5) + 'said correct'.padStart(14) + 'actually'.padStart(11)
    + 'said value'.padStart(13) + 'true value'.padStart(13) + '   verdict')
  let right = 0
  for (const p of parsed) {
    const t = truth.get(p.id)
    if (!t) continue
    const okVerdict = p.claim_correct === t.valid
    const okValue = Math.abs(p.true_value - t.true_Q_H) < 1e-6
    if (okVerdict && okValue) right++
    console.log('  ' + p.id.padEnd(5) + String(p.claim_correct).padStart(14)
      + String(t.valid).padStart(11) + p.true_value.toFixed(2).padStart(13)
      + t.true_Q_H.toFixed(2).padStart(13) + '   '
      + (okVerdict && okValue ? 'both right'
         : okVerdict ? 'verdict right, VALUE WRONG' : 'VERDICT WRONG'))
  }
  console.log('')
  console.log('[result] ' + right + '/' + parsed.length + ' witnesses fully correct')
}
