import type { Context } from 'cordis'
import { writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

export const name = 'ecdr-argue'
export const inject = ['llm', 'argumentChecker', 'certificates', 'physics']

const HERE = dirname(fileURLToPath(import.meta.url))

const PROBLEM = [
  'Streams (0-indexed; hot must be cooled, cold heated):',
  '  0 = H1: 150 -> 60 C, cp = 2.0 kW/K',
  '  1 = H2: 90 -> 60 C, cp = 8.0 kW/K',
  '  2 = C1: 20 -> 125 C, cp = 2.5 kW/K',
  '  3 = C2: 100 -> 150 C, cp = 3.0 kW/K',
  '',
  'Minimum approach temperature dt_min = 10 C.',
  'The thermodynamic minimum hot utility for these streams is 142.5 kW.',
  'Both utilities are needed: hot utility 142.5 kW and cold utility 150.0 kW.',
].join('\n')

const CLAIM_TEXT = 'No DESIGN using fewer than V heat exchanger units can attain hot utility '
  + '<= 142.5 kW.'

/**
 * The certificate as the roadmap describes it: an OBJECT carrying its soundness argument and
 * naming the remedy, judged by a reader in a separate context.
 *
 * Finding 049 recorded three deviations from the roadmap, and this is the first experiment that
 * addresses all three at once:
 *   * line 98 - a soundness ARGUMENT checkable by a third party, rather than a number recomputed;
 *   * Layer B (iv) - the certificate must NAME the structural remedy, or it is a gate;
 *   * line 99 - a domain tag, which is what makes it revocable rather than a gate.
 *
 * A control certificate is judged alongside, whose argument is the pinch-decomposition argument
 * that Finding 046 recorded: "at least 3 units above the pinch and at least 3 below, and no
 * exchanger can serve both, so 6". That argument is FLAWED - a single exchanger can span the
 * pinch - and its number is too strong, since 5 units suffice (Finding 056). A reader that cannot
 * tell the two apart is not reading.
 */
export async function apply(ctx: Context) {
  if (!process.argv.includes('--argue')) return

  console.log('[argue] the certificate is an OBJECT: claim + argument + named remedy + tag')
  console.log('[argue] the reader is a separate model call, told neither answer')
  console.log('')

  const system = [
    'You are a process engineer. You will state a certificate and the argument for it.',
    '',
    'The certificate has this form: "' + CLAIM_TEXT + '"',
    '',
    'A larger V is a stronger claim and more useful, but it is FALSE if any design with fewer',
    'than V units attains the requirement.',
    '',
    'Reply with ONE JSON object and nothing else:',
    '{"V": <integer>, "argument": "<the derivation: why no design with fewer than V units can',
    ' reach 142.5 kW. At most 120 words, and it must be a reasoning chain a reader can fault>",',
    ' "names": "<what is structurally MISSING that would have to change; at most 25 words>"}',
  ].join('\n')

  const t0 = Date.now()
  const raw = await ctx.llm.complete(system, PROBLEM + '\n\nState your certificate.')
  console.log('[agent] ' + ((Date.now() - t0) / 1000).toFixed(1) + ' s')
  const m = raw.match(/\{[\s\S]*\}/)
  if (!m) { console.log('[fail] no JSON: ' + raw.slice(0, 300)); return }
  const p = JSON.parse(m[0])
  console.log('')
  console.log('  V        : ' + p.V)
  console.log('  argument : ' + String(p.argument ?? '').slice(0, 400))
  console.log('  names    : ' + String(p.names ?? '').slice(0, 200))

  // The ground truth, from Finding 056's enumeration with the utilities as nodes.
  const TRUTH = 5
  console.log('')
  console.log('  the enumerated truth (not told to either party): ' + TRUTH)

  // --- the reader judges the agent's certificate -------------------------------------
  console.log('')
  console.log('[reader] judging the agent\'s ARGUMENT - not its number')
  const v1 = await ctx.argumentChecker.judge(PROBLEM, CLAIM_TEXT.replace('V', String(p.V)),
    String(p.argument ?? ''), String(p.names ?? ''))
  console.log('  status     : ' + v1.status + '   confidence ' + v1.confidence)
  console.log('  objection  : ' + v1.objection)

  // --- and a control whose argument is known to be flawed -----------------------------
  const BAD_ARG = 'Above the pinch, the subnetwork has nodes {H1, C1, C2, HU} and needs at least '
    + '3 units. Below the pinch, {H1, H2, C1, CU} needs at least 3. Since no feasible exchanger '
    + 'can serve both above and below the pinch, the two counts cannot share a unit, so the total '
    + 'is at least 6.'
  console.log('')
  console.log('[reader] judging a CONTROL whose argument is known to be flawed (it claims 6)')
  const v2 = await ctx.argumentChecker.judge(PROBLEM,
    'No DESIGN using fewer than 6 heat exchanger units can attain hot utility <= 142.5 kW.',
    BAD_ARG, 'more units above and below the pinch')
  console.log('  status     : ' + v2.status + '   confidence ' + v2.confidence)
  console.log('  objection  : ' + v2.objection)

  // --- install on the reader's confidence, not on a gate ------------------------------
  console.log('')
  const THRESHOLD = 0.6
  if (v1.status === 'sound' && v1.confidence >= THRESHOLD) {
    const id = ctx.certificates.install({
      id: 'heat.units.V' + p.V, domain: 'heat-exchanger-network',
      claim: CLAIM_TEXT.replace('V', String(p.V)), argument: String(p.argument ?? ''),
      names: String(p.names ?? ''), value: Number(p.V), units: 'units',
      tag: { dt_min: 10, streams: 4, Q_star: 142.5, phase: 'single', cp: 'constant' },
      confidence: v1.confidence, verdict: v1,
    })
    const c = ctx.certificates.get(id)!
    console.log('  INSTALLED ' + id + ' at confidence ' + c.confidence)
    console.log('  it names: ' + c.names)
    console.log('  domain tag: ' + JSON.stringify(c.tag))
    console.log('  the tag is what makes it revocable: crossing dt_min or the stream set revokes it')
  } else {
    console.log('  NOT INSTALLED: the reader judged it ' + v1.status + ' at confidence '
      + v1.confidence + ' (threshold ' + THRESHOLD + ')')
  }

  console.log('')
  console.log('[result] agent V=' + p.V + ' (truth ' + TRUTH + ')   control V=6 (known false)')
  console.log('[result] reader: agent -> ' + v1.status + ', control -> ' + v2.status)
  const discriminates = v2.status === 'flawed' && v1.status === 'sound'
  console.log('[result] the reader DISCRIMINATES: ' + discriminates)
  console.log('')
  if (discriminates) {
    console.log('  The reader accepted a sound argument and faulted a flawed one, without being')
    console.log('  told either answer. That is the third-party check of line 98, exercised on an')
    console.log('  ARGUMENT rather than on a number.')
  } else {
    console.log('  The reader did not separate them. A reader that cannot is not reading, and the')
    console.log('  argument-based check would be decorative.')
  }

  writeFileSync(join(HERE, '..', '..', 'runs', 'argue_result.json'),
    JSON.stringify({ agent: p, reader_agent: v1, reader_control: v2, truth: TRUTH },
      null, 1))
  console.log('[saved] runs/argue_result.json')
}
