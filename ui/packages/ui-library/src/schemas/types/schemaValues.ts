import { isDefined } from '@syncmatrix/design'
import { MaybeRefOrGetter, toValue } from 'vue'
import { isRecord, isString } from '@/utilities'
import { createTuple } from '@/utilities/tuples'

export type SchemaValue = unknown
export type SchemaValues = Record<string, SchemaValue>

export const { values: syncmatrixKinds, isValue: isSyncmatrixKind } = createTuple([
  'none',
  'json',
  'jinja',
  'workspace_variable',
])

export type SyncmatrixKind = typeof syncmatrixKinds[number]

export function getSyncmatrixKindFromValue(source: MaybeRefOrGetter<SchemaValue>): SyncmatrixKind {
  const value = toValue(source)

  if (isSyncmatrixKindValue(value)) {
    return value.__syncmatrix_kind
  }

  return 'none'
}

type BaseSyncmatrixKindValue<
  TKind extends SyncmatrixKind = SyncmatrixKind,
  TRest extends Record<string, unknown> = Record<string, unknown>
> = {
  __syncmatrix_kind: TKind,
} & TRest

export type SyncmatrixKindValue = SyncmatrixKindNull | SyncmatrixKindJinja | SyncmatrixKindJson | SyncmatrixKindWorkspaceVariable

export function isSyncmatrixKindValue<T extends SyncmatrixKind = SyncmatrixKind>(value: unknown, kind?: T): value is SyncmatrixKindValue & { __syncmatrix_kind: T } {
  const isKindObject = isRecord(value) && isSyncmatrixKind(value.__syncmatrix_kind)

  if (!isKindObject) {
    return false
  }

  if (isSyncmatrixKind(kind)) {
    return value.__syncmatrix_kind === kind
  }

  return true
}

export type SyncmatrixKindNull = BaseSyncmatrixKindValue<'none', {
  value: unknown,
}>

export function isSyncmatrixKindNull(value: unknown): value is SyncmatrixKindNull {
  return isSyncmatrixKindValue(value, 'none') && 'value' in value
}

export type SyncmatrixKindJson = BaseSyncmatrixKindValue<'json', {
  value?: string,
}>

export function isSyncmatrixKindJson(value: unknown): value is SyncmatrixKindJson {
  return isSyncmatrixKindValue(value, 'json') && (isString(value.value) || !isDefined(value.value))
}

export type SyncmatrixKindJinja = BaseSyncmatrixKindValue<'jinja', {
  template?: string,
}>

export function isSyncmatrixKindJinja(value: unknown): value is SyncmatrixKindJinja {
  return isSyncmatrixKindValue(value, 'jinja') && isString(value.template)
}

export type SyncmatrixKindWorkspaceVariable = BaseSyncmatrixKindValue<'workspace_variable', {
  variable_name?: string,
}>

export function isSyncmatrixKindWorkspaceVariable(value: unknown): value is SyncmatrixKindWorkspaceVariable {
  return isSyncmatrixKindValue(value, 'workspace_variable') && (isString(value.variable_name) || !isDefined(value.variable_name))
}

export type BlockDocumentReferenceValue = {
  $ref: string,
}

export function isBlockDocumentReferenceValue(value: unknown): value is BlockDocumentReferenceValue {
  return isRecord(value) && isString(value.$ref)
}

export function asBlockDocumentReferenceValue(value: unknown): BlockDocumentReferenceValue | undefined {
  if (isBlockDocumentReferenceValue(value)) {
    return value
  }

  return undefined
}