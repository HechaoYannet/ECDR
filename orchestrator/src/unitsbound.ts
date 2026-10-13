import type { Context } from 'cordis'
import { readFileSync, writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

export const name = 'ecdr-unitsbound'
export const inject = ['llm', 'physics']

const HERE = dirname(fileURLToPath(import.meta.url))

/**
 * A bound WE DO NOT HAVE.
 *
 * Finding 048: every heat-domain demonstration so far was circular, because the checker and the
 * ground truth were the same algorithm. This one is not. The textbook result - the fewest units
 * a minimum-utility design can use is N - 1, with N the streams including utilities - was
 * refuted by Finding 044 and no replacement has been found. The training rows below show it
 * failing in every case.
 *
 * So the answer cannot be precomputed, because it is not known. The agent sees eight solved
 * instances and one new instance whose answer is withheld, and must say what it expects and
 * whether it claims that is exact or only a lower bound. Both are then checked.
 */
export async function apply(ctx: Context) {
  if (!process.argv.includes('--unitsbound')) return

  const data = JSON.parse(readFileSync(
    join(HERE, '..', '..', 'runs', 'units_bound.json'), 'utf8'))
  const fmt = (r: any) => {
    const N = r.hot + r.cold + (r.Q_H_min_positive ? 1 : 0)
    return '  dt_min=' + String(r.dt_min).padStart(2) + '  N=' + N
      + '  hot/cold=' + r.hot + '/' + r.cold
      + '  above pinch hot/cold=' + r.hot_above_pinch + '/' + r.cold_above_pinch
      + '  below pinch hot/cold=' + r.hot_below_pinch + '/' + r.cold_below_pinch
  }
  const trainText = data.train.map((r: any, i: number) =>
    '  T' + (i + 1) + fmt(r) + '  ->  fewest units ' + r.min_units).join('\n')
  const t = data.test[0]
  const tN = t.hot + t.cold + (t.Q_H_min_positive ? 1 : 0)
  const heldText = '  H1: ' + fmt(t) + '\n'
    + t.streams.map((s: any) => '      ' + s.name + ': ' + s.t_in + ' -> ' + s.t_out
        + ' C, cp = ' + s.cp).join('\n')

  const system = [
    'You are a process engineer studying how few heat exchanger units a design needs.',
    '',
    'For a set of streams, a network attains the MINIMUM hot utility when no network of any',
    'size can use less. Among those, different networks use different numbers of units. The',
    'quantity of interest is the FEWEST units any such network needs.',
    '',
    'The classical answer is N - 1, where N counts the process streams plus any utility stream',
    'the design requires. It has already been shown FALSE on the cases below.',
    '',
    'You will see eight solved cases, then one new case. Say what you expect for the new case,',
    'and say whether you claim that number is EXACT or only a LOWER BOUND on the true value.',
    '',
    'Reply with ONE JSON object and nothing else:',
    '{"rule": "<your rule, at most 40 words>", "held_out": <integer>,',
    ' "is_exact": true|false, "why": "<at most 30 words>"}',
    '',
    'The answer for the new case WILL be computed and returned to you as the next message.',
  ].join('\n')

  const user = 'SOLVED CASES (fewest units is given):\n' + trainText
    + '\n\nNEW CASE (answer withheld):\n' + heldText
    + '\n\nWhat do you expect for the new case?'

  console.log('[unitsbound] 8 solved cases, 1 withheld; the textbook N-1 fails on all 8')
  console.log('[unitsbound] true held-out answer (the agent does not see this): '
    + t.min_units)
  const t0 = Date.now()
  const messages: Array<Record<string, unknown>> = [
    { role: 'system', content: system }, { role: 'user', content: user }]
  const res = await ctx.llm.completeFull('', '', messages)
  console.log('[llm] ' + ((Date.now() - t0) / 1000).toFixed(1) + ' s, '
    + res.reasoningTokens + ' reasoning tokens')
  messages.push({ role: 'assistant', content: res.content })

  const m = res.content.match(/\{[\s\S]*?\}/)
  if (!m) { console.log('[fail] no JSON: ' + res.content.slice(0, 300)); return }
  const p = JSON.parse(m[0])
  console.log('')
  console.log('  rule       : ' + String(p.rule ?? '').slice(0, 200))
  console.log('  held_out   : ' + p.held_out + '   claims exact: ' + p.is_exact)
  console.log('  why        : ' + String(p.why ?? '').slice(0, 200))

  const truth = t.min_units
  const sound = p.is_exact ? (p.held_out === truth) : (p.held_out <= truth)
  console.log('')
  console.log('  true answer            : ' + truth)
  console.log('  as a LOWER BOUND       : ' + (p.held_out <= truth ? 'SOUND' : 'UNSOUND'))
  console.log('  as an EXACT prediction : ' + (p.held_out === truth ? 'CORRECT' : 'wrong'))
  console.log('  as claimed (' + (p.is_exact ? 'exact' : 'lower bound') + ') : '
    + (sound ? 'STANDS' : 'REFUTED'))
  console.log('')
  if (sound && !p.is_exact && p.held_out < truth) {
    console.log('  A sound but loose bound: true, and it excludes fewer networks than it could.')
  } else if (sound) {
    console.log('  A sound and tight bound on a case nobody had solved.')
  } else {
    console.log('  REFUTED. The rule is false and the transcript says by how much.')
  }

  messages.push({ role: 'user', content: 'The true fewest units for the new case is '
    + truth + '. Your answer was ' + p.held_out + ', claimed '
    + (p.is_exact ? 'exact' : 'a lower bound') + '. State the corrected rule. Same JSON.' })
  const res2 = await ctx.llm.completeFull('', '', messages)
  const m2 = res2.content.match(/\{[\s\S]*?\}/)
  if (m2) {
    const q = JSON.parse(m2[0])
    console.log('')
    console.log('  after being told: rule = ' + String(q.rule ?? '').slice(0, 200))
    console.log('                    held_out = ' + q.held_out
      + '   as a lower bound: ' + ((q.held_out ?? 0) <= truth ? 'SOUND' : 'still unsound'))
  }

  writeFileSync(join(HERE, '..', '..', 'runs', 'unitsbound_reasoning.txt'),
    '--- turn 1 ---\n' + res.reasoning + '\n\n--- turn 2 ---\n' + res2.reasoning)
  console.log('[saved] runs/unitsbound_reasoning.txt')
}
