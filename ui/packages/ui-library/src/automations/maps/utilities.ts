import { asArray } from '@syncmatrix/design'
import { AutomationTriggerMatch, AutomationTriggerEventResource, AutomationTriggerEventResourceLabel, AutomationTriggerEventResourceRole, EventResourceValue } from '@/automations/types/api/triggers'
import { AutomationTrigger, isAutomationTriggerEvent } from '@/automations/types/triggers'

export function toResourceId(resource: AutomationTriggerEventResource, values: string[]): string | string[] {
  if (values.length === 0) {
    return `${resource}.*`
  }

  return values.map(flowId => `${resource}.${flowId}`)
}

export function fromResourceId(resource: AutomationTriggerEventResource, value: EventResourceValue): string[] {
  if (value === undefined) {
    return []
  }

  if (asArray(value).includes(`${resource}.*`)) {
    return []
  }

  return asArray(value).filter(value => value.startsWith(resource)).map(value => {
    const [, id] = value.split(`${resource}.`)

    return id
  })
}

export function fromResourceName(match: AutomationTriggerMatch, role: AutomationTriggerEventResourceRole): string[] {
  if (role !== match['syncmatrix.resource.role']) {
    return []
  }

  const value = match['syncmatrix.resource.name']

  if (value === undefined) {
    return []
  }

  return asArray(value)
}


export function toStateNameEvents(stateTypes: string[]): string[] {
  if (stateTypes.length === 0) {
    return ['syncmatrix.flow-run.*']
  }

  return stateTypes.map(stateType => `syncmatrix.flow-run.${stateType}`)
}

export function fromStateNameEvents(events: string[]): string[] {
  if (events.includes('syncmatrix.flow-run.*')) {
    return []
  }

  return events.filter(event => event.startsWith('syncmatrix.flow-run')).map(event => {
    const [, name] = event.split('syncmatrix.flow-run.')

    return name
  })
}

export function toMatchRelatedId(role: AutomationTriggerEventResourceRole, id: string | string[]): AutomationTriggerMatch | undefined {
  const ids = asArray(id)

  if (ids.length === 0) {
    return undefined
  }

  return {
    'syncmatrix.resource.role': role,
    'syncmatrix.resource.id': toResourceId(`syncmatrix.${role}`, ids),
  }
}

export function toMatchRelatedName(role: AutomationTriggerEventResourceRole, name: string | string[]): AutomationTriggerMatch | undefined {
  const names = asArray(name)

  if (names.length === 0) {
    return undefined
  }

  return {
    'syncmatrix.resource.role': role,
    'syncmatrix.resource.name': names,
  }
}

export function isMatchResource(trigger: AutomationTrigger, predicate: (resourceIds: string[]) => boolean): boolean {
  const syncmatrixResourceIds = getTriggerMatchValue(trigger, 'syncmatrix.resource.id')

  if (syncmatrixResourceIds.length === 0) {
    return false
  }

  return predicate(syncmatrixResourceIds)
}

function getTriggerMatchValue(trigger: AutomationTrigger, key: AutomationTriggerEventResourceLabel): string[] {
  if (isAutomationTriggerEvent(trigger)) {
    const value = trigger.match[key]

    return value ? asArray(value) : []
  }

  return []
}

export function isForEachResource(trigger: AutomationTrigger, resource: AutomationTriggerEventResourceLabel): boolean {
  if (isAutomationTriggerEvent(trigger)) {
    return trigger.forEach.every(value => value.startsWith(resource))
  }

  return false
}

export function isExpectResource(trigger: AutomationTrigger, predicate: (resourceIds: string[]) => boolean): boolean {
  if (isAutomationTriggerEvent(trigger)) {
    return predicate(trigger.expect)
  }

  return false
}

export function isAfterResource(trigger: AutomationTrigger, predicate: (resourceIds: string[]) => boolean): boolean {
  if (isAutomationTriggerEvent(trigger)) {
    return predicate(trigger.after)
  }

  return false
}