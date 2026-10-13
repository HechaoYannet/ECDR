import type { Context } from 'cordis'

const line = '='.repeat(96)
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

// The stream data as the physics bridge wants it. A ReferenceError here is invisible: Cordis
// swallows a throw inside an async plugin and Node exits 0 with no output, which is exactly what
// happened twice before this constant existed.
const STREAMS = [
  { name: 'H1', t_in: 150, t_out: 60, cp: 2.0 },
  { name: 'H2', t_in: 90, t_out: 60, cp: 8.0 },
  { name: 'C1', t_in: 20, t_out: 125, cp: 2.5 },
  { name: 'C2', t_in: 100, t_out: 150, cp: 3.0 },
]

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
  try {
    await run(ctx)
  } catch (e) {
    // Without this, a throw inside an async plugin is swallowed and Node exits 0 silently -
    // which is how the missing STREAMS constant hid for two runs.
    console.log('[argue] FAILED: ' + (e as Error).message)
    console.log((e as Error).stack?.split('\n').slice(0, 4).join('\n'))
  }
}

async function run(ctx: Context) {

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

  // --- FALSIFICATION FIRST: a reader that can only read accepts falsehoods -----------
  //
  // Finding 057: given prose alone, the reader judged a false certificate sound at 0.95 and a
  // deliberately flawed control at 0.88. Finding 045's reader found real defects because it had
  // concrete cases to EVALUATE. So the harness now runs the falsification attempt and hands the
  // reader the result - either a concrete counterexample design, or the count of designs searched
  // with none attaining it.
  const BAD_ARG = 'Above the pinch, the subnetwork has nodes {H1, C1, C2, HU} and needs at least '
    + '3 units. Below the pinch, {H1, H2, C1, CU} needs at least 3. Since no feasible exchanger '
    + 'can serve both above and below the pinch, the two counts cannot share a unit, so the total '
    + 'is at least 6.'

  // Three certificates are put to the reader, including the TRUE one so that the criterion does
  // not depend on what the agent happens to say.
  const CASES = [
    { tag: 'TRUE  V=5', V: 5, argument: 'The optimal design is a spanning tree on the six nodes '
      + '{H1, H2, C1, C2, HU, CU}: five edges, connected, acyclic. Its process part is H1-C1, '
      + 'H1-C2, H2-C1, with a heater on C2 and a cooler on H2. No design with four units reaches '
      + '142.5 kW.', names: 'a cross-pinch process exchanger', truth: true },
    { tag: 'FALSE V=6', V: 6, argument: BAD_ARG,
      names: 'more units above and below the pinch', truth: false },
    { tag: 'AGENT V=' + p.V, V: Number(p.V), argument: String(p.argument ?? ''),
      names: String(p.names ?? ''), truth: Number(p.V) === TRUTH },
  ]

  // --- THE REMEDY TEST, run BEFORE the reader and independently of it ---------------
  //
  // Finding 059: the false certificate's own [[names]] field asserted that the repair it named
  // was FORBIDDEN.  Finding 057: a reader given the argument and no way to test it judged that
  // certificate sound at 0.95.  ** The architecture never asked whether the named thing is
  // actually forbidden, and one enumeration answers it. **  So the assertion is a declared,
  // checkable field, and it is tested first.
  console.log('')
  console.log(line)
  console.log('THE REMEDY TEST - before any reader sees the argument')
  console.log(line)
  const REMEDY_CASES = [
    { tag: 'FALSE V=6', remedy: 'cross-pinch', asserts: 'forbidden',
      why: 'its own name says the repair is impossible' },
    { tag: 'TRUE  V=5', remedy: 'cross-pinch', asserts: 'required',
      why: 'the optimum uses a cross-pinch exchanger' },
  ]
  const remedyOut = []
  for (const rc of REMEDY_CASES) {
    const t = ctx.physics.testRemedy(STREAMS, 10, 142.5, rc.remedy, rc.asserts)
    console.log('  ' + rc.tag + '  asserts "' + rc.remedy + '" is ' + rc.asserts
      + '  (' + rc.why + ')')
    console.log('    enumerated ' + t.searched + ' designs; ' + t.attaining
      + ' attain 142.5 kW; ' + t.n_users + ' of them use the remedy')
    if (t.witness) {
      console.log('    witness: ' + t.witness.units + ' units, match H' + (t.witness.match[0] + 1)
        + '-C' + (t.witness.match[1] - 1) + ', ' + t.witness.heat.toFixed(3)
        + ' kW, Q_H = ' + t.witness.Q_H.toFixed(3))
    }
    console.log('    ** assertion_holds = ' + t.assertion_holds + ' **')
    remedyOut.push({ ...rc, holds: t.assertion_holds, witness: t.witness,
                     searched: t.searched, attaining: t.attaining })
  }
  const falseRemedy = remedyOut.find(r => r.tag.startsWith('FALSE'))!
  const trueRemedy = remedyOut.find(r => r.tag.startsWith('TRUE'))!
  console.log('')
  if (!falseRemedy.holds && trueRemedy.holds) {
    console.log('  ** The remedy test separates them WITHOUT a reader, an argument analysis or a')
    console.log('  confidence score. ** The false certificate is refuted by its own declared field,')
    console.log('  with a concrete witness: a 5-unit design attaining the requirement that USES the')
    console.log('  exchanger it called impossible.')
    console.log('')
    console.log('  This is what Finding 057 said was missing. The check needs TEST ACCESS, and a')
    console.log('  declared remedy assertion is a place to put it that costs one enumeration.')
  } else {
    console.log('  ** the remedy test did not separate them - recorded as a failure **')
  }

  const results: Array<{ tag: string, V: number, truth: boolean, status: string,
                         confidence: number, objection: string, evidence: string }> = []
  for (const c of CASES) {
    const f = ctx.physics.falsifyUnits(STREAMS, 10, 142.5, c.V)
    const evidence = f.n_hits === 0
      ? 'Searched all ' + f.searched + ' designs with at most ' + f.max_units_searched
        + ' units. NONE attains 142.5 kW.'
      : 'Searched all ' + f.searched + ' designs with at most ' + f.max_units_searched
        + ' units. ' + f.n_hits + ' attain 142.5 kW. A concrete counterexample: '
        + JSON.stringify(f.counterexamples[0])
    console.log('')
    console.log('[falsify] ' + c.tag + '  ->  ' + (f.n_hits === 0 ? 'no counterexample'
      : f.n_hits + ' counterexample(s)'))
    const v = await ctx.argumentChecker.judge(
      PROBLEM + '\n\nFALSIFICATION EVIDENCE (a complete enumeration)\n' + evidence,
      CLAIM_TEXT.replace('V', String(c.V)), c.argument, c.names)
    console.log('  reader: ' + v.status + ' at ' + v.confidence
      + (v.objection ? '   "' + v.objection.slice(0, 140) + '"' : ''))
    results.push({ tag: c.tag, V: c.V, truth: c.truth, status: v.status,
                   confidence: v.confidence, objection: v.objection, evidence })
  }

  const v1 = results[2]
  console.log('')
  console.log('[criterion] the reader must call the TRUE one sound and the FALSE one flawed')
  const trueCase = results.find(r => r.truth)!
  const falseCase = results.find(r => !r.truth)!
  const passes = trueCase.status === 'sound' && falseCase.status === 'flawed'
  console.log('  TRUE  V=' + trueCase.V + ' -> ' + trueCase.status
    + '   (want sound)')
  console.log('  FALSE V=' + falseCase.V + ' -> ' + falseCase.status
    + '   (want flawed)')
  console.log('')
  if (passes) {
    console.log('  PASS. With the falsification evidence in front of it the reader separates a')
    console.log('  sound certificate from a false one, which is what Finding 057 said was missing.')
  } else {
    console.log('  FAIL. Even given a complete enumeration and a concrete counterexample the')
    console.log('  reader did not separate them. The argument-checking mechanism does not work')
    console.log('  in this domain and should be recorded as unusable rather than as partial.')
  }

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
