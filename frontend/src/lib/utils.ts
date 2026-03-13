import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(cents: number, currency = 'USD') {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
  }).format(cents / 100)
}

export function formatDate(date: string | Date) {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(new Date(date))
}

export function formatRelative(date: string | Date) {
  const d = new Date(date)
  const diff = Date.now() - d.getTime()
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return 'just now'
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days}d ago`
  return formatDate(date)
}

export function truncate(str: string, max = 80) {
  return str.length > max ? str.slice(0, max) + '…' : str
}

export function platformColor(platform: string) {
  const map: Record<string, string> = {
    facebook: 'bg-blue-100 text-blue-700',
    instagram: 'bg-pink-100 text-pink-700',
    linkedin: 'bg-sky-100 text-sky-700',
  }
  return map[platform] ?? 'bg-gray-100 text-gray-700'
}

export function labelColor(label: string) {
  const map: Record<string, string> = {
    hot: 'bg-red-100 text-red-700',
    warm: 'bg-orange-100 text-orange-700',
    cold: 'bg-blue-100 text-blue-700',
  }
  return map[label] ?? 'bg-gray-100 text-gray-700'
}
