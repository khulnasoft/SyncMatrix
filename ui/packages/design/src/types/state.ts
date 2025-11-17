import { UseValidationState } from '@syncmatrix/vue-compositions'

export type State = Pick<UseValidationState, 'pending' | 'valid' | 'validated'>