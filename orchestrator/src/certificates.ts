import { Service, type Context } from 'cordis'

declare module 'cordis' {
  interface Context {
    certificates: CertificateService
  }
}

/**
 * A certificate is a REVOCABLE statement with a domain tag, never a decision.
 *
 * Finding 049 recorded that the roadmap's section 3, line 98, requires a **soundness argument**
 * checkable by a third party - and that the harness was checking a NUMBER by recomputing it, which
 * is not checking an argument. The fields below are what makes the object match the roadmap:
 *
 *   argument      the derivation, in enough detail for a third party to follow and fault it
 *   names         what the certificate says is MISSING; section 6 Layer B (iv) requires it,
 *                 because "a certificate that says only 'impossible' is a gate"
 *   confidence    a multiplier, not a decision. Roadmap line 104 says a certificate sets the
 *                 confidence of a family to ZERO; treating it as a graded quantity is an
 *                 extension, recorded as such, and it is what lets one object straddle the
 *                 certain and statistical regimes of section 5.5.
 *   verdict       what an independent reader concluded about the argument
 */
export interface Certificate {
  id: string
  domain: string
  claim: string
  /** the soundness argument: why the claim holds, in checkable steps */
  argument: string
  /** what is missing, and therefore what a repair must act on */
  names: string
  value: number
  units: string
  /** what the certificate is valid for; crossing it revokes rather than silently widens */
  tag: Record<string, unknown>
  /** 0 to 1. A certificate at 0 is not relied upon. */
  confidence: number
  /** the reader's conclusion and its objection, when it had one */
  verdict?: { status: string; confidence: number; objection: string }
}

/**
 * The certificate knowledge base. Every registration is a Cordis effect, so a certificate
 * carries its own inverse: revoke() and plugin unload do the same thing by construction, and
 * a certificate cannot outlive the component that asserted it.
 */
export class CertificateService extends Service {
  private readonly live = new Map<string, Certificate>()
  private readonly disposers = new Map<string, () => void>()

  constructor(ctx: Context) {
    super(ctx, 'certificates')
  }

  /** Install a certificate; returns its id. Ids encode the domain so a tag is never lost. */
  install(cert: Certificate): string {
    if (this.live.has(cert.id)) throw new Error('certificate already installed: ' + cert.id)
    const dispose = this.ctx.effect(() => {
      this.live.set(cert.id, cert)
      return () => { this.live.delete(cert.id) }
    })
    this.disposers.set(cert.id, dispose)
    return cert.id
  }

  revoke(id: string, reason: string): boolean {
    const dispose = this.disposers.get(id)
    if (!dispose) return false
    dispose()
    this.disposers.delete(id)
    this.ctx.emit('ecdr/certificate-revoked' as any, { id, reason } as any)
    return true
  }

  list(): Certificate[] {
    return [...this.live.values()]
  }

  get(id: string): Certificate | undefined {
    return this.live.get(id)
  }
}

export const name = 'ecdr-certificates'

export function apply(ctx: Context) {
  ctx.plugin(CertificateService)
}
