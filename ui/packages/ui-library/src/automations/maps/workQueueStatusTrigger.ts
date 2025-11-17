import { toResourceId, toMatchRelatedId, fromResourceId } from '@/automations/maps/utilities'
import { AutomationTriggerEvent } from '@/automations/types'
import { WorkQueueStatusEvent, WorkQueueStatusTrigger, isWorkQueueStatusEvent } from '@/automations/types/workQueueStatusTrigger'
import { WorkPoolQueueStatus, workPoolQueueStatus } from '@/models'
import { MapFunction } from '@/services'

export const mapWorkQueueStatusTriggerToAutomationTrigger: MapFunction<WorkQueueStatusTrigger, AutomationTriggerEvent> = function(source) {
  if (source.posture === 'Reactive') {
    return mapReactiveWorkQueueStatusTriggerToAutomationTrigger(source)
  }

  return mapProactiveWorkQueueStatusTriggerToAutomationTrigger(source)
}

function mapReactiveWorkQueueStatusTriggerToAutomationTrigger(source: WorkQueueStatusTrigger): AutomationTriggerEvent {
  return new AutomationTriggerEvent({
    posture: 'Reactive',
    match: {
      'syncmatrix.resource.id': toResourceId('syncmatrix.work-queue', source.workQueues),
    },
    matchRelated: {
      ...toMatchRelatedId('work-pool', source.workPools),
    },
    forEach: ['syncmatrix.resource.id'],
    expect: [mapWorkQueueStatusToEvent(source.status)],
  })
}

function mapProactiveWorkQueueStatusTriggerToAutomationTrigger(source: WorkQueueStatusTrigger): AutomationTriggerEvent {
  return new AutomationTriggerEvent({
    posture: 'Proactive',
    match: {
      'syncmatrix.resource.id': toResourceId('syncmatrix.work-queue', source.workQueues),
    },
    matchRelated: {
      ...toMatchRelatedId('work-pool', source.workPools),
    },
    forEach: ['syncmatrix.resource.id'],
    expect: anyStatusExcept(source.status).map(mapWorkQueueStatusToEvent),
    after: [mapWorkQueueStatusToEvent(source.status)],
    within: source.time,
  })
}

function anyStatusExcept(status: WorkPoolQueueStatus): WorkPoolQueueStatus[] {
  return workPoolQueueStatus.filter(_status => _status !== status)
}

export const mapAutomationTriggerToWorkQueueStatusTrigger: MapFunction<AutomationTriggerEvent, WorkQueueStatusTrigger> = function(source) {
  if (source.posture === 'Reactive') {
    return mapReactiveAutomationTriggerToWorkQueueStatusTrigger(source)
  }

  return mapProactiveAutomationTriggerToWorkQueueStatusTrigger(source)
}

function mapReactiveAutomationTriggerToWorkQueueStatusTrigger(trigger: AutomationTriggerEvent): WorkQueueStatusTrigger {
  return {
    workPools: fromResourceId('syncmatrix.work-pool', trigger.matchRelated['syncmatrix.resource.id']),
    workQueues: fromResourceId('syncmatrix.work-queue', trigger.match['syncmatrix.resource.id']),
    status: statusFromAutomationTriggerEvent(trigger),
    posture: 'Reactive',
    time: trigger.within,
  }
}

function mapProactiveAutomationTriggerToWorkQueueStatusTrigger(trigger: AutomationTriggerEvent): WorkQueueStatusTrigger {
  return {
    workPools: fromResourceId('syncmatrix.work-pool', trigger.matchRelated['syncmatrix.resource.id']),
    workQueues: fromResourceId('syncmatrix.work-queue', trigger.match['syncmatrix.resource.id']),
    status: statusFromAutomationTriggerEvent(trigger),
    posture: 'Proactive',
    time: trigger.within,
  }
}

const statusEventToStatus: Record<WorkQueueStatusEvent, WorkPoolQueueStatus> = {
  'syncmatrix.work-queue.ready': 'ready',
  'syncmatrix.work-queue.not-ready': 'not_ready',
  'syncmatrix.work-queue.paused': 'paused',
}

function statusFromAutomationTriggerEvent(trigger: AutomationTriggerEvent): WorkPoolQueueStatus {
  const statusEvents = trigger.posture === 'Reactive' ? trigger.expect : trigger.after

  for (const statusEvent of statusEvents) {
    if (isWorkQueueStatusEvent(statusEvent)) {
      return statusEventToStatus[statusEvent]
    }
  }

  throw new Error(`Unknown work queue status events: ${statusEvents}`)
}

function mapWorkQueueStatusToEvent(status: WorkPoolQueueStatus): WorkQueueStatusEvent {
  switch (status) {
    case 'not_ready':
      return 'syncmatrix.work-queue.not-ready'
    case 'ready':
    case 'paused':
      return `syncmatrix.work-queue.${status}`
    default:
      const exhaustiveCheck: never = status
      return `syncmatrix.work-queue.${exhaustiveCheck}`
  }
}