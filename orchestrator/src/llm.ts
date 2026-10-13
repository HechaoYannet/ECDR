import { Service, type Context } from 'cordis'
import { readFileSync } from 'node:fs'

declare module 'cordis' {
  interface Context {
    llm: LLMService
  }
}

export interface LLMConfig {
  /** Path to a file holding the API key. Never a literal key in configuration. */
  keyFile: string
  baseUrl?: string
  model?: string
  /**
   * Thinking is ON unless explicitly set false. It is the model's default and its intended
   * mode; disabling it is faster and measurably worse - it produced a BACKWARDS answer on
   * the very question Finding 037 settled by enumeration. See Finding 040.
   */
  thinking?: boolean
  /** Omit to use the model's full output allowance. Capping it truncates the reasoning. */
  maxTokens?: number
  /**
   * low | high | max. Defaults to "max": the strongest setting, and the one worth paying for.
   * Reasoning is not cheap - a max-effort call on a hard question took 206 s and 42,753
   * reasoning tokens - so callers should ask few questions and make each one count.
   */
  reasoningEffort?: 'low' | 'high' | 'max'
}

/**
 * A completion that cannot be trusted is a FAILURE, not an answer.
 *
 * A request whose max_tokens is too small for the reasoning returns HTTP 200 with
 * finish_reason "length" and an EMPTY content string: the reasoning consumed the budget
 * before the answer began.
 *
 * Finding 038 recorded this as a model pathology and recommended disabling thinking. That
 * was WRONG - see Finding 040. The cause was the caller's token cap, and disabling thinking
 * is not a fix but a loss: on the question Finding 037 settled by enumeration, the
 * no-thinking answer stated the direction BACKWARDS.
 *
 * The guard remains, with a corrected justification: it catches a budget the caller got
 * wrong, so that no caller can mistake truncation for an answer. Callers receive a string or
 * an exception; they never receive "".
 */
export class EmptyCompletionError extends Error {
  // No parameter properties anywhere in this package: Node's type-stripping is strip-only.
  readonly finishReason: string
  readonly reasoningChars: number
  readonly completionTokens: number

  constructor(finishReason: string, reasoningChars: number, completionTokens: number) {
    super('LLM returned no content (finish_reason=' + finishReason + ', '
      + completionTokens + ' tokens, ' + reasoningChars + ' chars of reasoning)')
    this.name = 'EmptyCompletionError'
    this.finishReason = finishReason
    this.reasoningChars = reasoningChars
    this.completionTokens = completionTokens
  }
}

export interface LLMResult {
  content: string
  /** the model's chain of thought; empty when thinking is disabled */
  reasoning: string
  completionTokens: number
  reasoningTokens: number
}

export class LLMService extends Service {
  private readonly apiKey: string
  // Declared and assigned explicitly: Node's type-stripping runs in strip-only mode and
  // rejects TypeScript PARAMETER PROPERTIES, and a module that fails to parse makes the
  // Cordis loader exit 0 with no output at all rather than reporting the error.
  private readonly config: LLMConfig

  constructor(ctx: Context, config: LLMConfig) {
    super(ctx, 'llm')
    this.config = config
    this.apiKey = readFileSync(config.keyFile, 'utf8').match(/sk-[A-Za-z0-9_-]+/)?.[0]
      ?? (() => { throw new Error('no API key found in ' + config.keyFile) })()
  }

  /** One completion. Throws EmptyCompletionError rather than returning an empty string. */
  async complete(system: string, user: string): Promise<string> {
    return (await this.completeFull(system, user)).content
  }

  /**
   * The same call, returning the reasoning as well.
   *
   * Finding 042 recorded that reasoning_content was not captured, so HOW the model reached an
   * answer was unknown. When the question is whether it DERIVED something rather than
   * recalled it, the path is part of the evidence, and capturing it costs nothing extra.
   */
  async completeFull(system: string, user: string,
                     messages?: Array<Record<string, unknown>>): Promise<LLMResult> {
    const res = await fetch((this.config.baseUrl ?? 'https://api.deepseek.com')
      + '/chat/completions', {
      method: 'POST',
      headers: { Authorization: 'Bearer ' + this.apiKey, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: this.config.model ?? 'deepseek-flash',
        messages: messages ?? [{ role: 'system', content: system },
                              { role: 'user', content: user }],
        // max_tokens is passed ONLY when configured. The API docs' own examples omit it, and
        // the default is the model's full output allowance. Capping it truncates the
        // reasoning and yields finish_reason "length" with EMPTY content - which is a
        // failure of the caller's budget, not of the model. See Finding 040.
        ...(this.config.maxTokens ? { max_tokens: this.config.maxTokens } : {}),
        reasoning_effort: this.config.reasoningEffort ?? 'max',
        ...(this.config.thinking === false ? { thinking: { type: 'disabled' } } : {}),
      }),
    })
    if (!res.ok) throw new Error('LLM HTTP ' + res.status + ': ' + (await res.text()).slice(0, 300))
    const body: any = await res.json()
    const choice = body.choices?.[0]
    const content: string = choice?.message?.content ?? ''
    if (!content.trim()) {
      throw new EmptyCompletionError(choice?.finish_reason ?? 'unknown',
        (choice?.message?.reasoning_content ?? '').length,
        body.usage?.completion_tokens ?? 0)
    }
    return {
      content,
      reasoning: choice?.message?.reasoning_content ?? '',
      completionTokens: body.usage?.completion_tokens ?? 0,
      reasoningTokens: body.usage?.completion_tokens_details?.reasoning_tokens ?? 0,
    }
  }
}

export const name = 'ecdr-llm'
export const inject = []

export function apply(ctx: Context, config: LLMConfig) {
  ctx.plugin(LLMService, config)
}
