import { Service, type Context } from 'cordis'
import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

declare module 'cordis' {
  interface Context {
    physics: PhysicsService
  }
}

const HERE = dirname(fileURLToPath(import.meta.url))
const BRIDGE = join(HERE, '..', 'python', 'bridge.py')
const PYTHON = join(HERE, '..', '..', '.venv', 'Scripts', 'python.exe')

export interface StreamSpec {
  name: string
  t_in: number
  t_out: number
  cp: number
}

/**
 * ECDR physics behind a process boundary. Every call runs python/bridge.py and parses one
 * JSON object back. A non-zero exit or unparseable stdout is a FAILURE and raises; the
 * bridge never prints anything but the response, so a stray print is a bug, not a result.
 */
export class PhysicsService extends Service {
  constructor(ctx: Context) {
    super(ctx, 'physics')
  }

  call(request: Record<string, unknown>): any {
    const proc = spawnSync(PYTHON, [BRIDGE, JSON.stringify(request)], {
      encoding: 'utf8', maxBuffer: 64 * 1024 * 1024,
    })
    if (proc.status !== 0) {
      throw new Error('physics bridge exited ' + proc.status + ': ' + proc.stderr.slice(0, 400))
    }
    let parsed: any
    try {
      parsed = JSON.parse(proc.stdout)
    } catch {
      throw new Error('physics bridge returned non-JSON: ' + proc.stdout.slice(0, 200))
    }
    if (parsed.ok !== true) throw new Error('physics error: ' + parsed.error)
    return parsed
  }

  minUtility(streams: StreamSpec[], dtMin: number) {
    return this.call({ op: 'min_utility', streams, dt_min: dtMin })
  }
  network(streams: StreamSpec[], dtMin: number, allowed?: number[][]) {
    return this.call({ op: 'network', streams, dt_min: dtMin, allowed: allowed ?? null })
  }
  enumerate(streams: StreamSpec[], dtMin: number) {
    return this.call({ op: 'enumerate', streams, dt_min: dtMin })
  }
  searchUnits(streams: StreamSpec[], dtMin: number, requirement: number, maxUnits: number) {
    return this.call({ op: 'search_units', streams, dt_min: dtMin,
                       requirement, max_units: maxUnits })
  }
  unitCheck(streams: StreamSpec[], dtMin: number, requirement: number, value: number) {
    return this.call({ op: 'unit_check', streams, dt_min: dtMin,
                       requirement, value })
  }
}

export const name = 'ecdr-physics'

export function apply(ctx: Context) {
  ctx.plugin(PhysicsService)
}
