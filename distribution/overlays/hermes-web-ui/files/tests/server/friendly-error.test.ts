import { describe, expect, it, vi } from 'vitest'
import { friendlyErrorEnvelope, sendFriendlyError } from '../../packages/server/src/lib/friendly-error'

describe('friendly error envelope', () => {
  it('hides raw upstream 50x details while returning a traceable envelope', () => {
    const envelope = friendlyErrorEnvelope(new Error('HTTP 502 Bad Gateway from upstream'), undefined, 'backend_error')

    expect(envelope.userMessage).toContain('\u670d\u52a1\u8fde\u63a5')
    expect(envelope.error).toBe(envelope.userMessage)
    expect(envelope.code).toBe('backend_error')
    expect(envelope.debugId).toMatch(/^[0-9a-f-]{36}$/)
    expect(JSON.stringify(envelope)).not.toContain('HTTP 502')
    expect(JSON.stringify(envelope)).not.toContain('Bad Gateway')
  })

  it('keeps raw traceback details out of the response body', () => {
    const envelope = friendlyErrorEnvelope(new Error('Traceback RuntimeError: token secret leaked'))

    expect(envelope.userMessage).toContain('\u5df2\u9690\u85cf\u6280\u672f\u7ec6\u8282')
    expect(JSON.stringify(envelope)).not.toContain('Traceback')
    expect(JSON.stringify(envelope)).not.toContain('secret')
  })

  it('sets status and records debug metadata when sending', () => {
    const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => undefined)
    const ctx: { status?: number; body?: unknown } = {}

    sendFriendlyError(ctx, Object.assign(new Error('Gateway Timeout'), { code: 'backend_timeout' }), 504)

    expect(ctx.status).toBe(504)
    expect(ctx.body).toMatchObject({ code: 'backend_timeout' })
    expect(errorSpy).toHaveBeenCalledOnce()
    errorSpy.mockRestore()
  })
})
