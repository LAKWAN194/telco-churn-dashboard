const wholeNumber = new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 })
const money = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 0,
})
const moneyWithCents = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' })
const dateTime = new Intl.DateTimeFormat('en-GB', {
  day: 'numeric',
  month: 'short',
  hour: '2-digit',
  minute: '2-digit',
})

export function formatNumber(value) {
  return wholeNumber.format(value)
}

export function formatMoney(value) {
  return money.format(value)
}

export function formatMoneyWithCents(value) {
  return moneyWithCents.format(value)
}

// 0.4271 -> "42.7%"
export function formatPercent(rate) {
  return `${(rate * 100).toFixed(1)}%`
}

export function formatDateTime(value) {
  // The API sends UTC timestamps without a timezone suffix
  const utc = /Z|[+-]\d\d:\d\d$/.test(value) ? value : `${value}Z`
  return dateTime.format(new Date(utc))
}
