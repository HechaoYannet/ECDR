import { Service, type Context } from 'cordis'

declare module 'cordis' {
  interface Context {
    certificates: CertificateService
  }
}

/** A certificate is a REVOCABLE statement with a domain tag, never a decision. */
export interface Certificate {
  id: string
  domain: string
  claim: string
  value: number
  units: string
  /** what the certificate is valid for; crossing it revokes rather than silently widens */
  tag: Record<string, unknown>
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
