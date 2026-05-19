import { describe, expect, it } from 'vitest'

import { containsRawTechnicalNotice, friendlyNoticeText } from '@/utils/friendly-notice'

describe('friendly notice adapter', () => {
  it('collapses apply_patch tool warnings', () => {
    const text = friendlyNoticeText('Warning: apply_patch was requested via shell. Use the apply_patch tool instead of exec_command.')

    expect(text).toContain('\u5185\u90e8\u63d0\u793a\u5df2\u6536\u655b')
    expect(text).not.toContain('Warning:')
    expect(text).not.toContain('exec_command')
  })

  it('hides HTTP 50x transport details', () => {
    const text = friendlyNoticeText(new Error('HTTP 502 Bad Gateway'))

    expect(text).toContain('\u670d\u52a1\u8fde\u63a5\u77ed\u6682\u6ce2\u52a8')
    expect(text).not.toContain('HTTP 502')
    expect(text).not.toContain('Bad Gateway')
  })

  it('hides traceback-like exceptions', () => {
    const text = friendlyNoticeText('Traceback (most recent call last): RuntimeError: boom')

    expect(text).toContain('\u5df2\u9690\u85cf\u6280\u672f\u7ec6\u8282')
    expect(text).not.toContain('Traceback')
    expect(text).not.toContain('RuntimeError')
  })

  it('preserves safe user-facing messages', () => {
    expect(friendlyNoticeText('\u4fdd\u5b58\u5931\u8d25\uff0c\u8bf7\u91cd\u8bd5')).toBe('\u4fdd\u5b58\u5931\u8d25\uff0c\u8bf7\u91cd\u8bd5')
  })

  it('detects raw technical notices before display', () => {
    expect(containsRawTechnicalNotice('[Codex] HTTP 502')).toBe(true)
    expect(containsRawTechnicalNotice('\u4efb\u52a1\u5df2\u5b8c\u6210')).toBe(false)
  })
})
