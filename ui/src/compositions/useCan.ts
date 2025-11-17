import { Can, inject } from '@syncmatrix/ui-library'
import { Permission, canKey } from '@/utilities/permissions'

export function useCan(): Can<Permission> {
  return inject(canKey)
}
