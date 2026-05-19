import { randomUUID } from 'crypto'

export interface FriendlyErrorEnvelope {
  error: string
  userMessage: string
  code: string
  debugId: string
}

interface FriendlyErrorLike {
  code?: unknown
  message?: unknown
  stack?: unknown
}

const DEFAULT_FRIENDLY_MESSAGE = '\u26a0\ufe0f \u64cd\u4f5c\u6682\u65f6\u672a\u5b8c\u6210\uff5c\u5df2\u9690\u85cf\u6280\u672f\u7ec6\u8282'
const NETWORK_FRIENDLY_MESSAGE = '\ud83d\udce1 \u670d\u52a1\u8fde\u63a5\u77ed\u6682\u6ce2\u52a8\uff5c\u8bf7\u7a0d\u540e\u91cd\u8bd5'

const CODE_MESSAGES: Record<string, string> = {
  missing_path: '\ud83d\udcc1 \u8def\u5f84\u4fe1\u606f\u4e0d\u5b8c\u6574\uff5c\u8bf7\u8865\u5145\u540e\u91cd\u8bd5',
  invalid_path: '\ud83d\udcc1 \u8def\u5f84\u683c\u5f0f\u672a\u901a\u8fc7\uff5c\u8bf7\u68c0\u67e5\u540e\u91cd\u8bd5',
  not_found: '\ud83d\udcc1 \u6587\u4ef6\u6682\u65f6\u4e0d\u53ef\u7528\uff5c\u8bf7\u786e\u8ba4\u8def\u5f84\u540e\u91cd\u8bd5',
  ENOENT: '\ud83d\udcc1 \u6587\u4ef6\u6682\u65f6\u4e0d\u53ef\u7528\uff5c\u8bf7\u786e\u8ba4\u8def\u5f84\u540e\u91cd\u8bd5',
  already_exists: '\ud83d\udcc1 \u76ee\u6807\u5df2\u5b58\u5728\uff5c\u8bf7\u66f4\u6362\u540d\u79f0\u540e\u91cd\u8bd5',
  permission_denied: '\ud83d\udd12 \u64cd\u4f5c\u88ab\u5b89\u5168\u9650\u5236\uff5c\u8bf7\u68c0\u67e5\u6743\u9650\u6216\u8def\u5f84',
  file_too_large: '\ud83d\udce6 \u6587\u4ef6\u8d85\u8fc7\u9650\u5236\uff5c\u8bf7\u6362\u7528\u66f4\u5c0f\u6587\u4ef6',
  not_a_directory: '\ud83d\udcc1 \u76ee\u6807\u4e0d\u662f\u6587\u4ef6\u5939\uff5c\u8bf7\u786e\u8ba4\u8def\u5f84',
  not_a_file: '\ud83d\udcc4 \u76ee\u6807\u4e0d\u662f\u6587\u4ef6\uff5c\u8bf7\u786e\u8ba4\u8def\u5f84',
  unsupported_backend: '\ud83d\udce1 \u5f53\u524d\u5b58\u50a8\u540e\u7aef\u6682\u4e0d\u652f\u6301\uff5c\u8bf7\u5207\u6362\u540e\u91cd\u8bd5',
  backend_error: NETWORK_FRIENDLY_MESSAGE,
  backend_timeout: NETWORK_FRIENDLY_MESSAGE,
}

const FRIENDLY_RULES: Array<{ pattern: RegExp; message: string }> = [
  { pattern: /Warning:.*apply_patch|apply_patch.*exec_command/i, message: '\ud83d\udccc \u5185\u90e8\u63d0\u793a\u5df2\u6536\u655b\uff5c\u65e0\u9700\u5904\u7406' },
  { pattern: /Gateway restarted successfully|Gateway online/i, message: '\u267b\ufe0f \u7f51\u5173\u5df2\u6062\u590d\uff5c\u53ef\u4ee5\u7ee7\u7eed\u4f7f\u7528' },
  { pattern: /Still working|No activity for/i, message: '\u23f3 \u4efb\u52a1\u4ecd\u5728\u5904\u7406\uff5c\u6211\u4f1a\u7ee7\u7eed\u89c2\u5bdf' },
  { pattern: /\bHTTP\s+50\d\b|Bad Gateway|Gateway Timeout|ECONNRESET|ECONNREFUSED|fetch failed|NetworkError/i, message: NETWORK_FRIENDLY_MESSAGE },
  { pattern: /Traceback|RuntimeError|TypeError|ReferenceError|Unhandled|Exception/i, message: DEFAULT_FRIENDLY_MESSAGE },
]

export function friendlyErrorEnvelope(error: unknown, fallback = DEFAULT_FRIENDLY_MESSAGE, code?: string): FriendlyErrorEnvelope {
  const rawMessage = extractMessage(error)
  const normalizedCode = code || extractCode(error) || 'internal_error'
  const userMessage = friendlyErrorMessage(rawMessage, fallback, normalizedCode)
  return {
    error: userMessage,
    userMessage,
    code: normalizedCode,
    debugId: randomUUID(),
  }
}

export function sendFriendlyError(ctx: { status?: number; body?: unknown }, error: unknown, status = 500, fallback?: string, code?: string): void {
  const envelope = friendlyErrorEnvelope(error, fallback, code)
  ctx.status = normalizeStatus(status)
  ctx.body = envelope
  recordFriendlyError(error, envelope, ctx.status)
}

function friendlyErrorMessage(rawMessage: string, fallback: string, code: string): string {
  if (CODE_MESSAGES[code]) return CODE_MESSAGES[code]
  for (const rule of FRIENDLY_RULES) {
    if (rule.pattern.test(rawMessage)) return rule.message
  }
  return fallback
}

function extractMessage(error: unknown): string {
  if (typeof error === 'string') return error
  if (error && typeof error === 'object') {
    const message = (error as FriendlyErrorLike).message
    if (typeof message === 'string') return message
  }
  if (error == null) return ''
  return String(error)
}

function extractCode(error: unknown): string {
  if (error && typeof error === 'object') {
    const code = (error as FriendlyErrorLike).code
    if (typeof code === 'string' && code.trim()) return code.trim()
  }
  return ''
}

function normalizeStatus(status: number): number {
  return Number.isInteger(status) && status >= 400 ? status : 500
}

function recordFriendlyError(error: unknown, envelope: FriendlyErrorEnvelope, status: number): void {
  const rawMessage = extractMessage(error).slice(0, 500)
  const stack = error && typeof error === 'object' && typeof (error as FriendlyErrorLike).stack === 'string'
    ? String((error as FriendlyErrorLike).stack).slice(0, 2000)
    : undefined
  console.error(JSON.stringify({
    scope: 'friendly-error-envelope',
    debugId: envelope.debugId,
    status,
    code: envelope.code,
    rawMessage,
    stack,
  }))
}
