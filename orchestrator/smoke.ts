import { Context, Service } from 'cordis'

class Greeter extends Service {
  static inject = []
  constructor(ctx: Context) {
    super(ctx, 'greeter')
  }
  hello(name: string) {
    return 'hello ' + name
  }
}

const ctx = new Context()
ctx.plugin(Greeter)
console.log('service:', (ctx as any).greeter.hello('ecdr'))
console.log('has service:', ctx.get('greeter') !== undefined)

// revertible effect: a registration that carries its own inverse
const log: string[] = []
const dispose = ctx.effect(() => {
  log.push('registered')
  return () => { log.push('reverted') }
})
dispose()
console.log('effect log:', JSON.stringify(log))
