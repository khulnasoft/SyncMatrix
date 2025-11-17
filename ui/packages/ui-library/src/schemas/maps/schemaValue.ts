import { isDefined } from '@syncmatrix/design'
import { SyncmatrixKind, SyncmatrixKindJinja, SyncmatrixKindJson, SyncmatrixKindWorkspaceVariable, SchemaValue, getSyncmatrixKindFromValue, isSyncmatrixKindJinja, isSyncmatrixKindJson, isSyncmatrixKindNull, isSyncmatrixKindWorkspaceVariable, isSyncmatrixKindValue } from '@/schemas/types/schemaValues'
import { isRecord, mapValues, parseUnknownJson } from '@/utilities'
import { isValidJson, stringify } from '@/utilities/json'

export class InvalidSchemaValueTransformation extends Error {
  public constructor(from: SyncmatrixKind, to: SyncmatrixKind) {
    super(`Unable to convert syncmatrix kind value from ${from} to ${to}`)
  }
}

export function isInvalidSchemaValueTransformationError(value: unknown): value is InvalidSchemaValueTransformation {
  return value instanceof InvalidSchemaValueTransformation
}

export function mapSchemaValue(value: SchemaValue, to: SyncmatrixKind): SchemaValue {
  const from = getSyncmatrixKindFromValue(value)

  if (isSyncmatrixKindJinja(value)) {
    return mapSchemaValueJinja(value, to)
  }

  // we cannot map a workspace variable to any other kinds
  if (isSyncmatrixKindWorkspaceVariable(value)) {
    throw new InvalidSchemaValueTransformation(from, to)
  }

  if (isSyncmatrixKindJson(value)) {
    return mapSchemaValueJson(value, to)
  }


  if (from === 'none') {
    return mapSchemaValueNone(value, to)
  }

  throw new Error(`Unhandled syncmatrix kind value in mapSchemaValue: ${from}`)
}

function mapSchemaValueJinja(jinja: SyncmatrixKindJinja, to: SyncmatrixKind): SchemaValue {
  switch (to) {
    case 'jinja':
      return jinja

    case 'workspace_variable':
      throw new InvalidSchemaValueTransformation('jinja', 'workspace_variable')

    case 'json':
      return {
        __syncmatrix_kind: 'json',
        value: jinja.template,
      } satisfies SyncmatrixKindJson

    case 'none':
      if (isValidJson(jinja.template)) {
        return JSON.parse(jinja.template)
      }

      throw new InvalidSchemaValueTransformation('jinja', 'none')
    default:
      throw new Error(`mapSchemaValueJson missing case for kind: ${to}`)
  }
}

function mapSchemaValueJson(json: SyncmatrixKindJson, to: SyncmatrixKind): SchemaValue {
  switch (to) {
    case 'jinja':
      return {
        __syncmatrix_kind: 'jinja',
        template: json.value,
      } satisfies SyncmatrixKindJinja

    case 'workspace_variable':
      throw new InvalidSchemaValueTransformation('json', 'workspace_variable')

    case 'json':
      return json

    case 'none':
      if (isDefined(json.value) && isValidJson(json.value)) {
        return JSON.parse(json.value)
      }

      throw new InvalidSchemaValueTransformation('json', 'none')

    default:
      throw new Error(`mapSchemaValueJson missing case for kind: ${to}`)
  }
}

function mapSchemaValueNone(none: unknown, to: SyncmatrixKind): SchemaValue {
  const value = isSyncmatrixKindNull(none) ? none.value : none

  switch (to) {
    case 'jinja':
      return {
        __syncmatrix_kind: 'jinja',
        template: stringify(value),
      } satisfies SyncmatrixKindJinja

    case 'workspace_variable':
      return {
        __syncmatrix_kind: 'workspace_variable',
      } satisfies SyncmatrixKindWorkspaceVariable

    case 'json':
      let normalizedMappedValue: SchemaValue = value

      if (isDefined(value) && isRecord(value)) {
        normalizedMappedValue = mapValues(value, (key, value) => mapSchemaValue(value, 'none'))
      }

      return {
        __syncmatrix_kind: 'json',
        value: stringify(normalizedMappedValue),
      } satisfies SyncmatrixKindJson

    case 'none':
      return none

    default:
      throw new Error(`mapSchemaValueNone missing case for kind: ${to}`)
  }
}