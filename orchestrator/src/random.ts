import type { Context } from 'cordis'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'
import type { StreamSpec } from './physics.ts'

export const name = 'ecdr-random'
export const inject = ['physics', 'checker', 'certificates', 'llm']

const HERE = dirname(fileURLToPath(import.meta.url))

interface Scenario {
  id: string
  dt_min: number
  Q_H_min: number
  streams: StreamSpec[]
}

/**
 * The recall test.
 *
 * Finding 041's exact answers came on the standard textbook 4-stream problem, which the model
 * may have seen in training. Exactness there is consistent both with reasoning from the stream
 * data and with recall.
 *
 * These scenarios are randomly generated: temperatures, heat capacity flowrates, stream counts
 * and approach temperatures all vary, and they were drawn from a seeded generator this session.
 * A recalled answer cannot be exact on them.
 *
 * ALL SIX are asked in ONE call. A call at max effort costs minutes and tens of thousands of
 * reasoning tokens, so the question is made to carry as much as it can.
 */
export async function apply(ctx: Context) {
  const path = join(HERE, '..', '..', 'runs', 'llm_scenarios.json')
  const all: Scenario[] = JSON.parse(readFileSync(path, 'utf8'))

  const system = [
    'You are a process engineer doing pinch analysis.',
    '',
    'For each problem you are given a set of streams and a minimum approach temperature',
    'dt_min. Exactly one number is wanted per problem:',
    '',
    '  V = a lower bound on the hot utility any heat exchanger network of any size or',
    '      topology would need, i.e. no network can use less than V.',
    '',
    'The tightest correct V is the thermodynamic minimum hot utility. A V above it is FALSE;',
    'a V far below it is true but useless. Aim for the tightest value you can justify.',
    '',
    'Reply with ONE JSON array and nothing else, one object per problem, in order:',
    '[{"id": "R1", "value": <number>}, ...]',
  ].join('\n')

  const blocks = all.map(s => {
    const lines = s.streams.map(x =>
      '    ' + x.name + ': ' + x.t_in + ' -> ' + x.t_out + ' C, cp = ' + x.cp + ' kW/K')
    return '  ' + s.id + '  (dt_min = ' + s.dt_min + ' C)\n' + lines.join('\n')
  })
  const user = 'Hot streams must be cooled, cold streams must be heated.\n\n'
    + blocks.join('\n\n') + '\n\nGive V for each of the ' + all.length + ' problems.'

  console.log('[input] ' + all.length + ' random scenarios, ONE model call, max effort')
  const t0 = Date.now()
  const text = await ctx.llm.complete(system, user)
  console.log('[llm] returned in ' + ((Date.now() - t0) / 1000).toFixed(1) + ' s, '
    + text.length + ' chars')

  const m = text.match(/\[[\s\S]*\]/)
  if (!m) { console.log('[fail] no JSON array in: ' + text.slice(0, 400)); return }
  const parsed: Array<{ id: string, value: number }> = JSON.parse(m[0])

  const byId = new Map(all.map(s => [s.id, s]))
  console.log('')
  console.log('  ' + 'id'.padEnd(5) + 'proposed'.padStart(12) + 'truth'.padStart(12)
    + 'ratio'.padStart(10) + 'error'.padStart(12) + '   verdict')
  let sound = 0, exact = 0
  const ratios: number[] = []
  for (const p of parsed) {
    const s = byId.get(p.id)
    if (!s) continue
    const verdict = ctx.checker.checkUtilityBound(s.streams, s.dt_min,
      { claim: 'lower bound on hot utility', value: p.value, units: 'kW', tag: {} })
    const ratio = p.value / s.Q_H_min
    ratios.push(ratio)
    if (verdict.sound) sound++
    if (Math.abs(ratio - 1) < 1e-6) exact++
    console.log('  ' + p.id.padEnd(5) + p.value.toFixed(4).padStart(12)
      + s.Q_H_min.toFixed(4).padStart(12) + ratio.toFixed(4).padStart(10)
      + (p.value - s.Q_H_min).toFixed(4).padStart(12)
      + '   ' + (verdict.sound ? 'SOUND' : 'REFUTED'))
  }
  console.log('')
  console.log('[result] sound ' + sound + '/' + parsed.length
    + ',  exactly tight ' + exact + '/' + parsed.length)
  const mean = ratios.reduce((a, b) => a + b, 0) / ratios.length
  console.log('[result] mean ratio to the true minimum = ' + mean.toFixed(4)
    + '  (1.0000 would be perfect)')
}
