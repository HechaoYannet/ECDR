import type { Context } from 'cordis'
import type { StreamSpec } from './physics.ts'

export const name = 'ecdr-demo'
export const inject = ['physics', 'certificates']

const STREAMS: StreamSpec[] = [
  { name: 'H1', t_in: 150, t_out: 60, cp: 2.0 },
  { name: 'H2', t_in: 90, t_out: 60, cp: 8.0 },
  { name: 'C1', t_in: 20, t_out: 125, cp: 2.5 },
  { name: 'C2', t_in: 100, t_out: 150, cp: 3.0 },
]
const DT_MIN = 10.0

/**
 * Round 33 slice: prove the Cordis wiring drives the real physics across the process
 * boundary, and that a certificate is registered and revoked as an effect. The agent loop
 * and the LLM adapter are NOT here yet.
 */
export async function apply(ctx: Context) {
  const cert = ctx.physics.minUtility(STREAMS, DT_MIN)
  console.log('[physics] Q_H_min = ' + cert.Q_H_min.toFixed(6)
    + '  Q_C_min = ' + cert.Q_C_min.toFixed(6)
    + '  pinch(shifted) = ' + cert.pinch_shifted_T)

  const id = ctx.certificates.install({
    id: 'heat.utility.lower-bound',
    domain: 'heat-exchanger-network',
    claim: 'every network needs at least this much hot utility',
    value: cert.Q_H_min,
    units: 'kW',
    tag: { dt_min: DT_MIN, streams: STREAMS.length, phase: 'single', cp: 'constant' },
  })
  console.log('[cert] installed ' + id
    + '  live = ' + ctx.certificates.list().length
    + '  tag = ' + JSON.stringify(ctx.certificates.get(id)!.tag))

  const req = 0.9 * cert.Q_H_min
  const net = ctx.physics.network(STREAMS, DT_MIN)
  console.log('[verdict] requirement Q* = ' + req.toFixed(4)
    + '   certificate = ' + cert.Q_H_min.toFixed(4)
    + '   best unconstrained network = ' + net.Q_H.toFixed(4))
  console.log('[verdict] the certificate decides it infeasible: ' + (cert.Q_H_min > req))

  ctx.certificates.revoke(id, 'demo teardown')
  console.log('[cert] after revoke, live = ' + ctx.certificates.list().length)
}
