import * as outlinedHeroIcons from '@heroicons/vue/24/outline'
import * as solidHeroIcons from '@heroicons/vue/24/solid'
import * as syncmatrixIcons from '@/components/Icon/icons'

export type SolidHeroIcon = keyof typeof solidHeroIcons
export type OutlinedHeroIcon = keyof typeof outlinedHeroIcons
export type HeroIcon = SolidHeroIcon | OutlinedHeroIcon
export type SyncmatrixIcon = keyof typeof syncmatrixIcons
export type Icon = HeroIcon | SyncmatrixIcon