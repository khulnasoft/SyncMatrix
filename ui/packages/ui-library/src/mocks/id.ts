import { randomId as generateRandomId } from '@syncmatrix/design'
import { MockFunction } from '@/services/Mocker'

export const randomId: MockFunction<string, []> = function() {
  return generateRandomId()
}