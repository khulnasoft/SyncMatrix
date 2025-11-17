import 'vue-router'
import { RouteGuard } from '@syncmatrix/ui-library'

declare module 'vue-router' {
  interface RouteMeta {
    guards?: RouteGuard[],
    filters?: { visible?: boolean, disabled?: boolean },
  }
}