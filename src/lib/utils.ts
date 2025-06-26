import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCookingTime(minutes: number): string {
  if (minutes < 60) {
    return `${minutes} min`
  }
  const hours = Math.floor(minutes / 60)
  const remainingMinutes = minutes % 60
  if (remainingMinutes === 0) {
    return `${hours} hr${hours > 1 ? 's' : ''}`
  }
  return `${hours} hr${hours > 1 ? 's' : ''} ${remainingMinutes} min`
}

export function formatServings(servings: number): string {
  return servings === 1 ? '1 serving' : `${servings} servings`
}

export function calculateTrendingScore(
  likes: number,
  saves: number,
  made: number,
  views: number,
  createdAt: Date
): number {
  const ageInDays = (Date.now() - createdAt.getTime()) / (1000 * 60 * 60 * 24)
  const ageWeight = Math.max(0, 1 - ageInDays / 30) // Decay over 30 days
  
  const engagementScore = (likes * 2 + saves * 3 + made * 5) / Math.max(views, 1)
  return engagementScore * ageWeight
}

export function extractRecipeUrlSlug(title: string): string {
  return title
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
} 