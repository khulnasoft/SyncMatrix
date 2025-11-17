import { AutomationTriggerEvent } from '@/automations/types/automationTriggerEvent'
import { AutomationTrigger } from '@/automations/types/triggers'
import { WorkspaceEventResponse } from '@/models/api/workspaceEvents'
import { WorkspaceEvent } from '@/models/workspaceEvent'
import { MapFunction } from '@/services/Mapper'
import { getSyncmatrixResourceRole } from '@/utilities/events'

export const mapWorkspaceEventResponseToWorkspaceEvent: MapFunction<WorkspaceEventResponse, WorkspaceEvent> = function(source) {
  return new WorkspaceEvent({
    id: source.id,
    account: source.account,
    event: source.event,
    payload: source.payload,
    related: source.related,
    resource: source.resource,
    workspace: source.workspace,
    occurred: this.map('string', source.occurred, 'Date'),
    received: this.map('string', source.received, 'Date'),
  })
}

export const mapWorkspaceEventToAutomationTrigger: MapFunction<WorkspaceEvent, AutomationTrigger> = function(event) {
  const role = getSyncmatrixResourceRole(event.event)

  switch (role) {
    case 'flow-run':
      return mapEventToFlowRunStateChangeTrigger(event)
    case 'work-queue':
      return mapEventToWorkQueueTrigger(event)
    default:
      return mapEventToCustomAutomationTrigger(event)
  }
}

function mapEventToFlowRunStateChangeTrigger(event: WorkspaceEvent): AutomationTrigger {
  const relatedFlow = event.getRelatedByRole('flow')

  return new AutomationTriggerEvent({
    'posture': 'Reactive',
    'match': {
      'syncmatrix.resource.id': event.resourceId,
    },
    'matchRelated': {
      'syncmatrix.resource.role': 'flow',
      'syncmatrix.resource.id': relatedFlow?.['syncmatrix.resource.id'],
    },
    'forEach': ['syncmatrix.resource.id'],
    'expect': [event.event],
  })
}

function mapEventToWorkQueueTrigger(event: WorkspaceEvent): AutomationTrigger {
  const relatedWorkQueue = event.getRelatedByRole('work-queue')

  return new AutomationTriggerEvent({
    'posture': 'Reactive',
    'match': {
      'syncmatrix.resource.id': event.resourceId,
    },
    'matchRelated': {
      'syncmatrix.resource.role': 'flow',
      'syncmatrix.resource.id': relatedWorkQueue?.['syncmatrix.resource.id'],
    },
    'forEach': ['syncmatrix.resource.id'],
    'expect': [event.event],
  })
}

function mapEventToCustomAutomationTrigger(event: WorkspaceEvent): AutomationTrigger {
  return new AutomationTriggerEvent({
    'posture': 'Reactive',
    'match': {
      'syncmatrix.resource.id': event.resourceId,
    },
    'expect': [event.event],
  })
}