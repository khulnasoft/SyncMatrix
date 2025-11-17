import { applyColorModeClass, ColorMode, isColorMode } from '@syncmatrix/ui-library'
import { useLocalStorage } from '@syncmatrix/vue-compositions'
import { computed } from 'vue'

const colorModeLocalStorageKey = 'syncmatrix-color-mode'
const nonJsonVersion = localStorage.getItem(colorModeLocalStorageKey)
const defaultValue = isColorMode(nonJsonVersion) ? nonJsonVersion : null

const { value: colorMode, set: setColorMode } = useLocalStorage<ColorMode | null>(colorModeLocalStorageKey, defaultValue)

export const activeColorMode = computed({
  get() {
    return colorMode.value
  },
  set(value: ColorMode | null) {
    setColorMode(value)
    applyColorModeClass(value)
  },
})

export function initColorMode(): void {
  applyColorModeClass(activeColorMode.value)
}