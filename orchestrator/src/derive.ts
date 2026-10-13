import type { Context } from 'cordis'
import type { StreamSpec } from './physics.ts'

export const name = 'ecdr-derive'
export const inject = ['physics', 'checker', 'certificates', 'llm']

const STREAMS: StreamSpec[] = [
  { name: 'H1', t_in: 150, t_out: 60, cp: 2.0 },
  { name: 'H2', t_in: 90, t_out: 60, cp: 8.0 },
  { name: 'C1', t_in: 20, t_out: 125, cp: 2.5 },
  { name: 'C2', t_in: 100, t_out: 150, cp: 3.0 },
]
const DT_MIN = 10
const QSTAR = 142.5
const MAX_TURNS = 3

/**
 * Can the model DERIVE a certificate rather than apply one?
 *
 * Finding 042 showed it computes the pinch minimum utility exactly, on random instances. That
 * is applying a textbook method. This asks for something the textbook gets WRONG.
 *
 * The question is a unit-count bound: "no network using fewer than V units can achieve hot
 * utility <= Q*". The classical answer is U_min = N - 1 with N the streams including
 * utilities - here 5, so 4. Finding 037 refuted that by exhaustive enumeration: a network with
 * TWO units attains the minimum utility, because a disconnected network needs only a spanning
 * tree per component.
 *
 * The checker enumerates every match set and returns a CONCRETE counterexample network when
 * one exists. It never states the correct bound. So the model must work out what to do with a
 * network it did not think of, which is precisely the ECDR setting.
 */
export async function apply(ctx: Context) {
  if (!process.argv.includes('--derive')) return

  const streamLines = STREAMS.map(s =>
    '  ' + s.name + ': ' + s.t_in + ' -> ' + s.t_out + ' C, cp = ' + s.cp + ' kW/K').join('\n')
  const task = [
    'A heat exchanger network must cool the hot streams and heat the cold streams.',
    '',
    streamLines,
    '',
    'Minimum approach temperature dt_min = ' + DT_MIN + ' C.',
    'The requirement: the network must use hot utility <= ' + QSTAR + ' kW.',
    '',
    'Propose a certificate of this precise form:',
    '',
    '  "No network using fewer than V heat exchanger units can meet the requirement."',
    '',
    'V must be a number you can justify. A larger V is a stronger claim and is more useful,',
    'but it is FALSE if any network with fewer than V units meets the requirement.',
    '',
    'Reply with ONE JSON object and nothing else: {"V": <integer>, "why": "<at most 40 words>"}',
  ].join('\n')

  const messages: Array<Record<string, unknown>> = [
    { role: 'system', content: 'You are a process engineer deriving a structural bound on heat exchanger networks. Be exact; a claim you cannot justify is worse than a weaker claim you can.' },
    { role: 'user', content: task },
  ]

  console.log('[task] streams=' + STREAMS.length + '  dt_min=' + DT_MIN
    + '  requirement Q*=' + QSTAR + ' kW')
  console.log('[task] the checker enumerates every network and returns a counterexample, never the answer')

  for (let turn = 1; turn <= MAX_TURNS; turn++) {
    const t0 = Date.now()
    const res = await ctx.llm.completeFull('', '', messages)
    messages.push({ role: 'assistant', content: res.content })
    console.log('')
    console.log('[turn ' + turn + '] ' + ((Date.now() - t0) / 1000).toFixed(1) + ' s, '
      + res.reasoningTokens + ' reasoning tokens, ' + res.reasoning.length
      + ' chars of reasoning')

    const m = res.content.match(/\{[\s\S]*?\}/)
    if (!m) { console.log('  no JSON: ' + res.content.slice(0, 200)); return }
    const parsed = JSON.parse(m[0])
    const V = Number(parsed.V)
    console.log('  proposed V = ' + V + '   ("' + String(parsed.why ?? '').slice(0, 90) + '")')

    const check = ctx.physics.unitCheck(STREAMS, DT_MIN, QSTAR, V)
    console.log('  checker: ' + (check.sound ? 'SOUND' : 'REFUTED')
      + '   (fewest units attaining Q* = ' + check.min_units_attaining + ')')

    if (check.sound) {
      const id = ctx.certificates.install({
        id: 'heat.unit-bound.V' + V, domain: 'heat-exchanger-network',
        claim: 'no network with fewer than ' + V + ' units meets Q* = ' + QSTAR,
        value: V, units: 'units',
        tag: { dt_min: DT_MIN, streams: STREAMS.length, Q_star: QSTAR,
               proposed_by: 'llm', turns: turn, why: String(parsed.why ?? '').slice(0, 120) },
      })
      console.log('')
      console.log('  CERTIFICATE ACCEPTED after ' + turn + ' turn(s): ' + id)
      console.log('  tag: ' + JSON.stringify(ctx.certificates.get(id)!.tag))
      return
    }

    const ce = check.counterexample
    console.log('  counterexample: ' + ce.units + ' units, Q_H = ' + ce.Q_H.toFixed(3)
      + ' kW, matches = ' + JSON.stringify(ce.matches))
    messages.push({
      role: 'user',
      content: 'Your V = ' + V + ' is REFUTED. Here is a network that meets the requirement '
        + 'with fewer units:\n\n'
        + '  units: ' + ce.units + '\n'
        + '  hot utility achieved: ' + ce.Q_H.toFixed(3) + ' kW (requirement <= ' + QSTAR + ')\n'
        + '  matches between streams (0-indexed: 0=H1, 1=H2, 2=C1, 3=C2): '
        + JSON.stringify(ce.matches) + '\n\n'
        + 'Revise V. If no bound of this form is both sound and stronger than a trivial one, '
        + 'say so and give the strongest V you can justify. Same JSON format.',
    })
  }
  console.log('')
  console.log('[end] no accepted certificate within ' + MAX_TURNS + ' turns')
}
