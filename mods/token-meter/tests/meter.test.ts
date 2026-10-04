import { expect, mock, test } from 'claude-code/testing'

const STEP = { turnId: 't1', index: 0, model: 'test-model', messageCount: 1 }
const SLOW = { timeoutMs: 20_000 }

function usage(output: number) {
  return { input_tokens: 10, output_tokens: output, cache_read_input_tokens: 0, cache_creation_input_tokens: 0, model: 'test-model' }
}

// The response beneath the plugin: `pieces` text pieces of 40 characters, then a stop with `output` tokens.
function response(pieces: number, output: number) {
  return async function* (_$: unknown, e: { turnId: string; index: number }) {
    for (let i = 0; i < pieces; i++) yield { kind: 'text' as const, index: 0, text: 'x'.repeat(40) }
    yield { kind: 'stop' as const, stopReason: 'end_turn' as const, usage: usage(output) }
    return { turnId: e.turnId, index: e.index, answer: '', toolUses: [], stopReason: 'end_turn' as const, usage: usage(output) }
  }
}

async function drain(stream: AsyncGenerator<unknown, unknown>) {
  for (;;) if ((await stream.next()).done) return
}

function watchStatus(on: any) {
  const statuses: (string | undefined)[] = []
  on('ui.status', (_$: unknown, e: { text: string | undefined }) => { statuses.push(e.text); return {} as never })
  return statuses
}

test('shows the exact speed once a reply ends', SLOW, async ($, on) => {
  const clock = mock.clock(on)
  const statuses = watchStatus(on)
  on('turn.step', response(1, 100))

  const stream = $.turn.step(STEP)
  await stream.next()            // the first piece arrives at 0 ms
  await clock.advance(2000)      // the reply takes 2 seconds
  await drain(stream)

  expect(statuses.at(-1)).toBe('50 tok/s | 100 tok/min | 100 tok/hr')
})

test('shows a live estimate marked ~ while a reply streams', SLOW, async ($, on) => {
  const clock = mock.clock(on)
  const statuses = watchStatus(on)
  on('turn.step', response(16, 160))

  const stream = $.turn.step(STEP)
  await stream.next()            // piece 1 at 0 ms
  await clock.advance(800)
  await drain(stream)            // pieces 2 to 16 at 800 ms; the meter updates every 8 pieces

  // At piece 8: 320 characters is about 80 tokens over 0.8 seconds.
  expect(statuses).toContain('~100 tok/s | 0 tok/min | 0 tok/hr')
  // When the reply ends, the exact count replaces the estimate: 160 tokens over 0.8 seconds.
  expect(statuses.at(-1)).toBe('200 tok/s | 160 tok/min | 160 tok/hr')
})

test('per-minute drops after a minute while per-hour keeps the total', SLOW, async ($, on) => {
  const clock = mock.clock(on)
  const statuses = watchStatus(on)
  let replies = 0
  on('turn.step', async function* ($s, e) {
    replies += 1
    return yield* response(1, replies === 1 ? 1000 : 50)($s, e)
  })

  const first = $.turn.step(STEP)
  await first.next()
  await clock.advance(10_000)
  await drain(first)
  expect(statuses.at(-1)).toBe('100 tok/s | 1.0k tok/min | 1.0k tok/hr')

  await clock.advance(61_000)
  const second = $.turn.step({ ...STEP, index: 1 })
  await second.next()
  await clock.advance(1000)
  await drain(second)
  expect(statuses.at(-1)).toBe('50 tok/s | 50 tok/min | 1.1k tok/hr')
})

test('clears the status line when nothing has been counted', async ($, on) => {
  const statuses = watchStatus(on)
  on('turn.step', async function* (_$, e) {
    yield { kind: 'stop' as const, stopReason: null, usage: null }
    return { turnId: e.turnId, index: e.index, answer: '', toolUses: [], stopReason: null, usage: null }
  })
  await drain($.turn.step(STEP))
  expect(statuses.at(-1)).toBeUndefined()
})
