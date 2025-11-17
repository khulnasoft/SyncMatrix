import { AutomationTriggerEvent } from '@/automations/types/automationTriggerEvent'
import { AutomationTrigger } from '@/automations/types/triggers'
import { WorkspaceEvent } from '@/models'
import { MapFunction } from '@/services/Mapper'
import { getSyncmatrixResourceRole } from '@/utilities/events'

export const mapEventToAutomationTrigger: MapFunction<WorkspaceEvent, AutomationTrigger> = function(event) {
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