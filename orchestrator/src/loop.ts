import { Service, type Context } from 'cordis'

import type { StreamSpec } from './physics.ts'
import type { CertificateProposal } from './checker.ts'

declare module 'cordis' {
  interface Context {
    loop: LoopService
  }
}

export interface Scenario {
  name: string
  streams: StreamSpec[]
  dtMin: number
  /** the requirement: hot utility must not exceed this */
  requirement: number
}

/** What the checker said about the previous proposal. A policy that ignores this cannot adapt. */
export interface Feedback {
  value: number
  sound: boolean
  reference: number
}

/** A policy proposes; it never decides. The checker decides. */
export interface Policy {
  readonly kind: string
  proposeCertificate(sc: Scenario, budgetLeft: number,
                     history: readonly Feedback[]): Promise<CertificateProposal>
  /**
   * What to change once a certificate has established that the requirement is out of reach
   * inside its domain. For a bound over ALL networks no structural change can lower it, so
   * the only repair is to change the PROBLEM - which is exactly what the domain tag names.
   */
  proposeDomainChange(sc: Scenario, bound: number): Promise<Scenario | null>
}

export interface Step {
  kind: string
  detail: string
}

/**
 * Bracket-and-bisect. The policy does NOT know Q_H_min; it discovers the boundary by asking
 * the checker. It expands an upper bracket until refuted, then bisects, and stops as soon as
 * it holds a SOUND bound that exceeds the requirement - which is exactly what decides the
 * question. It never learns Q_H_min itself, only whether a given value is too high.
 *
 * The loop therefore ends holding a certificate it has PROVED, not one it asserted.
 */
export class BisectionPolicy implements Policy {
  readonly kind = 'bisection'

  async proposeCertificate(sc: Scenario, _budgetLeft: number,
                           history: readonly Feedback[]): Promise<CertificateProposal> {
    const refuted = history.filter(h => !h.sound)
    const sound = history.filter(h => h.sound)
    let value: number
    if (refuted.length === 0) {
      // expand upward: start just above the requirement, then grow
      const last = sound.length ? Math.max(...sound.map(h => h.value)) : 0
      value = last > 0 ? last * 1.4 : sc.requirement * 1.02
    } else {
      const hi = Math.min(...refuted.map(h => h.value))
      const lo = sound.length ? Math.max(...sound.map(h => h.value)) : 0
      value = (lo + hi) / 2
    }
    return {
      claim: 'no network needs less than this much hot utility',
      value,
      units: 'kW',
      tag: { dt_min: sc.dtMin, streams: sc.streams.length, phase: 'single', cp: 'constant' },
    }
  }

  async proposeDomainChange(sc: Scenario, bound: number): Promise<Scenario | null> {
    // tighten the approach temperature until the bound falls below the requirement
    for (const dt of [5, 2, 1]) {
      if (dt < sc.dtMin) {
        return { ...sc, dtMin: dt, name: sc.name + ' (dt_min ' + dt + ')' }
      }
    }
    return null
  }
}

/**
 * The model proposes; the checker decides. One call per proposal, so the cost of a run is
 * the number of proposals and nothing else. The prompt carries the ENTIRE scenario, because
 * a call is expensive and a half-specified question wastes it.
 */
export class LLMPolicy implements Policy {
  readonly kind = 'llm'
  private readonly ctx: Context

  constructor(ctx: Context) {
    this.ctx = ctx
  }

  async proposeCertificate(sc: Scenario, budgetLeft: number,
                           history: readonly Feedback[]): Promise<CertificateProposal> {
    const streamLines = sc.streams.map(s =>
      '  ' + s.name + ': ' + s.t_in + ' -> ' + s.t_out + ' C, cp = ' + s.cp + ' kW/K')
      .join('\n')
    const priorText = history.length === 0 ? '(none yet)'
      : history.map(h => '  proposed ' + h.value.toFixed(4) + ' kW -> '
        + (h.sound ? 'ACCEPTED as sound' : 'REFUTED as false')).join('\n')

    const system = [
      'You are a process engineer. A heat exchanger network must use no more than Q* kW of',
      'hot utility. You may propose a LOWER BOUND certificate of the form "no network of any',
      'size or topology needs less than V kW of hot utility".',
      '',
      'A proposal is SOUND only if V is at or below the true thermodynamic minimum utility',
      'computable from the stream data. A proposal is USEFUL only if V is above Q*, because',
      'only then does it exclude the requirement.',
      '',
      'Reply with ONE JSON object and nothing else:',
      '{"value": <number in kW>, "reasoning": "<at most 30 words>"}',
    ].join('\n')

    const user = [
      'Streams (hot must be cooled, cold must be heated):',
      streamLines,
      '',
      'Minimum approach temperature dt_min = ' + sc.dtMin + ' C.',
      'Requirement: hot utility <= Q* = ' + sc.requirement + ' kW.',
      'Proposals left in budget: ' + budgetLeft + '.',
      '',
      'Values already proposed in this run:',
      priorText,
      '',
      'Propose one value V.',
    ].join('\n')

    const text = await this.ctx.llm.complete(system, user)
    const m = text.match(/\{[\s\S]*?\}/)
    if (!m) throw new Error('LLM did not return JSON: ' + text.slice(0, 200))
    const parsed = JSON.parse(m[0])
    return {
      claim: 'no network needs less than this much hot utility',
      value: Number(parsed.value),
      units: 'kW',
      tag: { dt_min: sc.dtMin, streams: sc.streams.length, phase: 'single', cp: 'constant',
             proposed_by: 'llm', note: String(parsed.reasoning ?? '').slice(0, 120) },
    }
  }

  async proposeDomainChange(sc: Scenario, bound: number): Promise<Scenario | null> {
    for (const dt of [5, 2, 1]) if (dt < sc.dtMin) return { ...sc, dtMin: dt }
    return null
  }
}

export class LoopService extends Service {
  constructor(ctx: Context) {
    super(ctx, 'loop')
  }

  /**
   * Run one scenario against a policy under a hard budget of physics calls.
   * Returns a transcript; every decision is visible with the number that drove it.
   */
  async run(sc: Scenario, policy: Policy, budget: number): Promise<Step[]> {
    const log: Step[] = []
    const history: Feedback[] = []
    let spent = 0
    let current = sc
    let certId: string | null = null

    log.push({ kind: 'scenario', detail: current.name + '  dt_min=' + current.dtMin
      + '  streams=' + current.streams.length + '  requirement Q*=' + current.requirement })

    while (spent < budget) {
      // --- propose, then let the CHECKER decide; a proposal is not a certificate ---
      const proposal = await policy.proposeCertificate(current, budget - spent, history)
      spent++
      const verdict = this.ctx.checker.checkUtilityBound(current.streams, current.dtMin,
        proposal)
      history.push({ value: proposal.value, sound: verdict.sound,
                     reference: verdict.reference })
      log.push({ kind: 'propose', detail: 'value ' + proposal.value.toFixed(4) + ' '
        + proposal.units + '  ->  ' + (verdict.sound ? 'SOUND' : 'REFUTED')
        + '  (' + verdict.reason + ')' })

      if (!verdict.sound) {
        if (spent >= budget) { log.push({ kind: 'budget', detail: 'exhausted' }); break }
        continue   // the policy gets another attempt inside the budget
      }

      // --- accepted: install it as a revocable effect ---
      certId = this.ctx.certificates.install({
        id: 'heat.utility.' + current.dtMin, domain: 'heat-exchanger-network',
        claim: proposal.claim, value: proposal.value, units: proposal.units,
        tag: proposal.tag,
      })
      log.push({ kind: 'certify', detail: 'installed ' + certId + ' at '
        + proposal.value.toFixed(4) + ' ' + proposal.units })

      // The certificate decides only if its bound EXCEEDS the requirement. A sound bound
      // below the requirement excludes nothing that matters and the loop must keep going.
      const outOfReach = proposal.value > current.requirement
      log.push({ kind: 'decide', detail: 'requirement ' + current.requirement.toFixed(4)
        + ' is ' + (outOfReach ? 'OUT OF REACH inside this domain' : 'reachable') })

      if (!outOfReach) {
        if (spent >= budget) { log.push({ kind: 'budget', detail: 'exhausted' }); break }
        continue
      }

      // --- the certificate says no structure in this family works. Change the PROBLEM. ---
      const next = await policy.proposeDomainChange(current, proposal.value)
      if (!next) { log.push({ kind: 'stop', detail: 'no domain change available' }); break }

      this.ctx.certificates.revoke(certId, 'domain crossed: dt_min '
        + current.dtMin + ' -> ' + next.dtMin)
      log.push({ kind: 'revoke', detail: certId + ' revoked, domain crossed' })
      certId = null
      current = next
      log.push({ kind: 'scenario', detail: current.name + '  dt_min=' + current.dtMin
        + '  streams=' + current.streams.length + '  requirement Q*='
        + current.requirement })
    }

    log.push({ kind: 'end', detail: 'physics calls spent ' + spent + ' of ' + budget
      + ';  live certificates ' + this.ctx.certificates.list().length })
    return log
  }
}

export const name = 'ecdr-loop'
export const inject = ['physics', 'checker', 'certificates']

export function apply(ctx: Context) {
  ctx.plugin(LoopService)
}
