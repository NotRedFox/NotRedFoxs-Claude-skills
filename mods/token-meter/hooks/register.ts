import type { EngineInterface, Register } from 'claude-code'

// Output tokens are what "speed" means for a model, so the meter counts those.
// While a reply is still streaming, the API hasn't reported its token count yet,
// so the live figure is estimated from characters (about 4 per token) and marked
// with "~". Once the reply ends, the exact count from the API replaces it.
const CHARS_PER_TOKEN = 4
const MINUTE = 60_000
const HOUR = 3_600_000
// Shorter than this, a reply's rate is mostly noise (one or two chunks).
const MIN_STREAM_MS = 200

type Sample = { at: number; tokens: number }

export function compact(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 10_000) return `${Math.round(n / 1000)}k`
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`
  return `${Math.round(n)}`
}

export function meterText(tps: number | undefined, isLive: boolean, perMinute: number, perHour: number): string {
  const speed = tps === undefined ? '- tok/s' : `${isLive ? '~' : ''}${compact(tps)} tok/s`
  return `${speed} | ${compact(perMinute)} tok/min | ${compact(perHour)} tok/hr`
}

type Meter = {
  samples: Sample[]
  lastTps: number | undefined
  live: { first: number; chars: number } | undefined
}

async function show($: EngineInterface, m: Meter) {
  const now = await $.clock.now()
  while (m.samples.length > 0 && m.samples[0].at <= now - HOUR) m.samples.shift()
  if (m.samples.length === 0 && m.live === undefined) {
    $.ui.status(undefined)
    return
  }
  const perMinute = m.samples.filter(s => s.at > now - MINUTE).reduce((sum, s) => sum + s.tokens, 0)
  const perHour = m.samples.reduce((sum, s) => sum + s.tokens, 0)
  let tps = m.lastTps
  let isLive = false
  if (m.live !== undefined && now - m.live.first >= MIN_STREAM_MS) {
    tps = m.live.chars / CHARS_PER_TOKEN / ((now - m.live.first) / 1000)
    isLive = true
  }
  $.ui.status(meterText(tps, isLive, perMinute, perHour))
}

export const register: Register = on => {
  const meter: Meter = { samples: [], lastTps: undefined, live: undefined }

  on('session.start', async ($, e, next) => {
    const started = await next(e)
    // Per-minute and per-hour totals fall as time passes, so refresh while idle too.
    $.clock.every(5000, () => void show($, meter))
    return started
  })

  on('turn.step', async function* ($, e, next) {
    const stream = next(e)
    let first: number | undefined
    let chars = 0
    let pieces = 0
    for await (const chunk of stream) {
      if (chunk.kind === 'text' || chunk.kind === 'thinking' || chunk.kind === 'input') {
        first ??= await $.clock.now()
        chars += chunk.kind === 'input' ? chunk.json.length : chunk.text.length
        pieces += 1
        if (pieces % 8 === 0) {
          meter.live = { first, chars }
          await show($, meter)
        }
      } else if (chunk.kind === 'stop') {
        const end = await $.clock.now()
        if (chunk.usage) {
          meter.samples.push({ at: end, tokens: chunk.usage.output_tokens })
          if (first !== undefined && end - first >= MIN_STREAM_MS) {
            meter.lastTps = chunk.usage.output_tokens / ((end - first) / 1000)
          }
        }
        meter.live = undefined
        await show($, meter)
      }
      yield chunk
    }
    return await stream.result
  })
}
