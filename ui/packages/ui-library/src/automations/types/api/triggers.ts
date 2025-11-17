import { AutomationTriggerCompoundRequire } from '@/automations/types/automationTriggerCompound'
import { isRecord } from '@/utilities/object'
import { createTuple } from '@/utilities/tuples'

export type AutomationTriggerEventResourceLabel =
 | 'syncmatrix.resource.id'
 | 'syncmatrix.resource.role'
 | 'syncmatrix.resource.name'
 | 'syncmatrix-cloud.incident.severity'

export type AutomationTriggerEventResource =
 | 'syncmatrix.deployment'
 | 'syncmatrix.flow-run'
 | 'syncmatrix.flow'
 | 'syncmatrix.tag'
 | 'syncmatrix.work-pool'
 | 'syncmatrix.work-queue'
 | 'syncmatrix-cloud.incident'

export type AutomationTriggerEventResourceRole =
 | 'flow'
 | 'tag'
 | 'work-queue'
 | 'work-pool'

export type EventResourceValue = string | string[] | undefined

export type AutomationTriggerMatch = Partial<Record<AutomationTriggerEventResourceLabel, EventResourceValue>>

export const { values: automationTriggerEventPosture, isValue: isAutomationTriggerEventPosture } = createTuple([
  'Reactive',
  'Proactive',
])

export const DEFAULT_EVENT_TRIGGER_WITHIN = 0

export type AutomationTriggerEventPosture = typeof automationTriggerEventPosture[number]

export type AutomationTriggerEventResponse = {
  type: 'event',
  match?: AutomationTriggerMatch,
  match_related?: AutomationTriggerMatch,
  after?: string[],
  expect?: string[],
  for_each?: string[],
  posture: AutomationTriggerEventPosture,
  threshold: number,
  within?: number,
}

export function isAutomationTriggerEventResponse(value: unknown): value is AutomationTriggerEventResponse {
  return isRecord(value) && value.type === 'event' && isAutomationTriggerEventPosture(value.posture)
}

export type AutomationTriggerCompoundResponse = {
  type: 'compound',
  triggers: AutomationTriggerResponse[],
  within: number,
  require: AutomationTriggerCompoundRequire,
}

export function isAutomationTriggerCompoundResponse(value: AutomationTriggerResponse): value is AutomationTriggerCompoundResponse {
  return value.type === 'compound'
}

export type AutomationTriggerSequenceResponse = {
  type: 'sequence',
  triggers: AutomationTriggerResponse[],
  within: number,
}

export function isAutomationTriggerSequenceResponse(value: AutomationTriggerResponse): value is AutomationTriggerSequenceResponse {
  return value.type === 'sequence'
}

export type AutomationTriggerResponse = AutomationTriggerEventResponse | AutomationTriggerCompoundResponse | AutomationTriggerSequenceResponse