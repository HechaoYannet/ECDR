import { Service, type Context } from 'cordis'
import type { StreamSpec } from './physics.ts'

declare module 'cordis' {
  interface Context {
    checker: CheckerService
    argumentChecker: ArgumentCheckerService
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

/** What an independent reader concluded about a certificate's ARGUMENT. */
export interface ArgumentVerdict {
  status: 'sound' | 'flawed' | 'unverifiable'
  confidence: number
  objection: string
}

/**
 * Check the ARGUMENT, not the number.
 *
 * Roadmap section 3 line 98 requires a **soundness argument** checkable by a third party,
 * independent of the search that motivated it. Finding 049 recorded that the harness was instead
 * recomputing the claim by another route - which is a consistency check between two
 * implementations, not a reading of the argument, and which Finding 048 showed is circular when
 * both sides reduce to the same algorithm.
 *
 * This sends the argument, and only the argument plus the problem, to a reader in a SEPARATE
 * context from the one that produced it. The reader is asked to fault it and to say what it cannot
 * verify. It is explicitly NOT told the answer.
 *
 * The reader is a model, so its verdict is a CONFIDENCE and not a proof. That is why the result is
 * stored in the certificate's confidence rather than used as a gate, and why the roadmap's
 * statistical regime (section 5.5) remains available even when no certificate is accepted.
 */
export class ArgumentCheckerService extends Service {
  constructor(ctx: Context) {
    super(ctx, 'argumentChecker')
  }

  async judge(problem: string, claim: string, argument: string,
              names: string): Promise<ArgumentVerdict> {
    const system = [
      'You are checking another engineer\'s argument, not their arithmetic.',
      '',
      'You will be given a problem, a claim, and the argument offered for it. Decide whether the',
      'ARGUMENT establishes the CLAIM. You are not told the answer and you must not assume the',
      'claim is true because it is stated confidently.',
      '',
      'Look for: steps that do not follow; conditions the argument needs but does not state;',
      'quantities it treats as comparable that are not; and things it never considers.',
      '',
      'Reply with ONE JSON object and nothing else:',
      '{"status": "sound"|"flawed"|"unverifiable", "confidence": <0..1>,',
      ' "objection": "<the specific defect, or why you cannot verify it; at most 60 words>"}',
      '',
      'Use "flawed" when you can name a defect. Use "unverifiable" when the argument depends on',
      'something you cannot check from what you were given. Use "sound" only when the steps hold.',
    ].join('\n')
    const user = ['PROBLEM', problem, '', 'CLAIM', claim, '',
                  'ARGUMENT', argument, '', 'WHAT IT SAYS IS MISSING', names].join('\n')
    const text = await this.ctx.llm.complete(system, user)
    const m = text.match(/\{[\s\S]*?\}/)
    if (!m) return { status: 'unverifiable', confidence: 0,
                     objection: 'reader returned no JSON: ' + text.slice(0, 120) }
    const p = JSON.parse(m[0])
    return { status: p.status, confidence: Number(p.confidence ?? 0),
             objection: String(p.objection ?? '').slice(0, 400) }
  }
}

export const name = 'ecdr-checker'
export const inject = ['physics', 'llm']

export function apply(ctx: Context) {
  ctx.plugin(CheckerService)
  ctx.plugin(ArgumentCheckerService)
}
