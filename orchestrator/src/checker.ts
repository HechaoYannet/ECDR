import { Service, type Context } from 'cordis'
import type { StreamSpec } from './physics.ts'

declare module 'cordis' {
  interface Context {
    checker: CheckerService
  }
}

/** What the agent proposes. A proposal is not a certificate until the checker accepts it. */
export interface CertificateProposal {
  claim: string
  value: number
  units: string
  tag: Record<string, unknown>
}

export interface CheckResult {
  sound: boolean
  reason: string
  /** the independently computed value the proposal was judged against */
  reference: number
}

/**
 * The certificate CHECKER. It lives on the Python side of the process boundary, in
 * python/bridge.py, and never in the agent's process - the project's discipline, enforced by
 * the process rather than by convention.
 *
 * A utility lower-bound certificate claims "no network needs less hot utility than VALUE".
 * It is SOUND exactly when VALUE <= Q_H_min computed from the stream data alone, because
 * Q_H_min is a true lower bound over all networks (Finding 036). A proposal above that is
 * refuted, and being refuted is a normal outcome, not an error.
 */
export class CheckerService extends Service {
  constructor(ctx: Context) {
    super(ctx, 'checker')
  }

  checkUtilityBound(streams: StreamSpec[], dtMin: number,
                    p: CertificateProposal): CheckResult {
    const truth = this.ctx.physics.minUtility(streams, dtMin)
    const ref = truth.Q_H_min as number
    const tol = 1e-9 * Math.max(1, Math.abs(ref))
    if (p.value <= ref + tol) {
      return { sound: true, reference: ref,
        reason: 'value ' + p.value.toFixed(6) + ' <= Q_H_min ' + ref.toFixed(6)
          + ', so it excludes nothing that exists' }
    }
    return { sound: false, reference: ref,
      reason: 'value ' + p.value.toFixed(6) + ' > Q_H_min ' + ref.toFixed(6)
        + '; a network attaining ' + ref.toFixed(6) + ' exists, so the claim is FALSE' }
  }
}

export const name = 'ecdr-checker'
export const inject = ['physics']

export function apply(ctx: Context) {
  ctx.plugin(CheckerService)
}
