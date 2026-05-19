export interface FriendlyNoticeOptions {
  fallback?: string
  maxLength?: number
}

interface FriendlyNoticeRule {
  pattern: RegExp
  message: string
}

const DEFAULT_FALLBACK = '\u64cd\u4f5c\u6682\u65f6\u672a\u5b8c\u6210\uff5c\u8bf7\u7a0d\u540e\u91cd\u8bd5'
const DEFAULT_MAX_LENGTH = 120

const FRIENDLY_RULES: FriendlyNoticeRule[] = [
  {
    pattern: /Warning:.*apply_patch|apply_patch.*exec_command/i,
    message: '\ud83d\udccc \u5185\u90e8\u63d0\u793a\u5df2\u6536\u655b\uff5c\u65e0\u9700\u5904\u7406',
  },
  {
    pattern: /Gateway restarted successfully|Gateway online/i,
    message: '\u267b\ufe0f \u7f51\u5173\u5df2\u6062\u590d\uff5c\u53ef\u4ee5\u7ee7\u7eed\u4f7f\u7528',
  },
  {
    pattern: /Still working|No activity for/i,
    message: '\u23f3 \u4efb\u52a1\u4ecd\u5728\u5904\u7406\uff5c\u6211\u4f1a\u7ee7\u7eed\u89c2\u5bdf',
  },
  {
    pattern: /\bHTTP\s+50\d\b|Bad Gateway|Gateway Timeout|ECONNRESET|ECONNREFUSED|fetch failed|NetworkError/i,
    message: '\ud83d\udce1 \u670d\u52a1\u8fde\u63a5\u77ed\u6682\u6ce2\u52a8\uff5c\u8bf7\u7a0d\u540e\u91cd\u8bd5',
  },
  {
    pattern: /Traceback|RuntimeError|TypeError|ReferenceError|Unhandled|Exception/i,
    message: '\u26a0\ufe0f \u64cd\u4f5c\u6682\u65f6\u672a\u5b8c\u6210\uff5c\u5df2\u9690\u85cf\u6280\u672f\u7ec6\u8282',
  },
]

const FORBIDDEN_VISIBLE_PATTERNS = [
  /\[Codex\]/gi,
  /Gateway restarted successfully|Gateway online/gi,
  /Still working/gi,
  /No activity for/gi,
  /\bHTTP\s+50\d\b/gi,
  /Warning:/gi,
  /Traceback/gi,
  /RuntimeError|TypeError|ReferenceError|Exception/gi,
  /Bad Gateway|Gateway Timeout/gi,
]

export function friendlyNoticeText(input: unknown, fallbackOrOptions?: string | FriendlyNoticeOptions): string {
  const options = normalizeOptions(fallbackOrOptions)
  const fallback = cleanText(options.fallback || DEFAULT_FALLBACK)
  const raw = cleanText(extractNoticeText(input))

  if (!raw) return fallback

  for (const rule of FRIENDLY_RULES) {
    if (rule.pattern.test(raw)) return rule.message
  }

  const sanitized = stripForbiddenTokens(raw)
  if (!sanitized || sanitized !== raw) return fallback

  return truncateNotice(sanitized, options.maxLength ?? DEFAULT_MAX_LENGTH)
}

export function containsRawTechnicalNotice(input: unknown): boolean {
  const raw = cleanText(extractNoticeText(input))
  return FORBIDDEN_VISIBLE_PATTERNS.some(pattern => pattern.test(raw))
}

function normalizeOptions(value?: string | FriendlyNoticeOptions): FriendlyNoticeOptions {
  if (typeof value === 'string') return { fallback: value }
  return value || {}
}

function extractNoticeText(input: unknown): string {
  if (typeof input === 'string') return input
  if (input instanceof Error) return input.message
  if (input && typeof input === 'object') {
    const maybeUserMessage = (input as { userMessage?: unknown }).userMessage
    if (typeof maybeUserMessage === 'string') return maybeUserMessage
    const maybeMessage = (input as { message?: unknown }).message
    if (typeof maybeMessage === 'string') return maybeMessage
    const maybeError = (input as { error?: unknown }).error
    if (typeof maybeError === 'string') return maybeError
  }
  if (input == null) return ''
  return String(input)
}

function cleanText(value: string): string {
  return value.replace(/\s+/g, ' ').trim()
}

function stripForbiddenTokens(value: string): string {
  return FORBIDDEN_VISIBLE_PATTERNS.reduce((current, pattern) => current.replace(pattern, ''), value).replace(/\s+/g, ' ').trim()
}

function truncateNotice(value: string, maxLength: number): string {
  if (value.length <= maxLength) return value
  return `${value.slice(0, Math.max(0, maxLength - 1)).trimEnd()}?`
}
