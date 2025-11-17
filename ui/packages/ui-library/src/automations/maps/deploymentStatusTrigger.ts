import { fromResourceId, toResourceId } from '@/automations/maps/utilities'
import { AutomationTriggerEvent } from '@/automations/types/automationTriggerEvent'
import { DeploymentStatusEvent, DeploymentStatusTrigger, isDeploymentStatusEvent } from '@/automations/types/deploymentStatusTrigger'
import { DeploymentStatus } from '@/models/DeploymentStatus'
import { MapFunction } from '@/schemas/mapper'

export const mapDeploymentStatusTriggerToAutomationTrigger: MapFunction<DeploymentStatusTrigger, AutomationTriggerEvent> = function(source) {
  if (source.posture === 'Reactive') {
    return mapReactiveDeploymentStatusTriggerToAutomationTrigger(source)
  }

  return mapProactiveDeploymentStatusTriggerToAutomationTrigger(source)
}

export const mapAutomationTriggerToDeploymentStatusTrigger: MapFunction<AutomationTriggerEvent, DeploymentStatusTrigger> = function(source) {
  if (source.posture === 'Reactive') {
    return mapReactiveAutomationTriggerToDeploymentStatusTrigger(source)
  }

  return mapProactiveAutomationTriggerToDeploymentStatusTrigger(source)
}

function mapReactiveDeploymentStatusTriggerToAutomationTrigger(source: DeploymentStatusTrigger): AutomationTriggerEvent {
  return new AutomationTriggerEvent({
    posture: 'Reactive',
    match: {
      'syncmatrix.resource.id': toResourceId('syncmatrix.deployment', source.deployments),
    },
    forEach: ['syncmatrix.resource.id'],
    expect: [mapDeploymentStatusToEvent(source.status)],
  })
}

function mapProactiveDeploymentStatusTriggerToAutomationTrigger(source: DeploymentStatusTrigger): AutomationTriggerEvent {
  return new AutomationTriggerEvent({
    posture: 'Proactive',
    match: {
      'syncmatrix.resource.id': toResourceId('syncmatrix.deployment', source.deployments),
    },
    forEach: ['syncmatrix.resource.id'],
    expect: [mapDeploymentStatusToEvent(oppositeStatus(source.status))],
    after: [mapDeploymentStatusToEvent(source.status)],
    within: source.time,
  })
}

function mapReactiveAutomationTriggerToDeploymentStatusTrigger(trigger: AutomationTriggerEvent): DeploymentStatusTrigger {
  return {
    deployments: fromResourceId('syncmatrix.deployment', trigger.match['syncmatrix.resource.id']),
    posture: 'Reactive',
    status: statusFromDeploymentStatusEvents(trigger.expect),
    time: trigger.within,
  }
}

function mapProactiveAutomationTriggerToDeploymentStatusTrigger(trigger: AutomationTriggerEvent): DeploymentStatusTrigger {
  return {
    deployments: fromResourceId('syncmatrix.deployment', trigger.match['syncmatrix.resource.id']),
    posture: 'Proactive',
    status: statusFromDeploymentStatusEvents(trigger.after),
    time: trigger.within,
  }

}

function oppositeStatus(status: DeploymentStatus): DeploymentStatus {
  return status === 'ready' ? 'not_ready' : 'ready'
}

function mapDeploymentStatusToEvent(status: DeploymentStatus): DeploymentStatusEvent {
  switch (status) {
    case 'ready':
      return 'syncmatrix.deployment.ready'
    case 'not_ready':
      return 'syncmatrix.deployment.not-ready'
    case 'disabled':
      return 'syncmatrix.deployment.disabled'
    default:
      const exhaustiveCheck: never = status
      return `syncmatrix.deployment.${exhaustiveCheck}`
  }
}

const statusEventToStatus: Record<DeploymentStatusEvent, DeploymentStatus> = {
  'syncmatrix.deployment.ready': 'ready',
  'syncmatrix.deployment.not-ready': 'not_ready',
  'syncmatrix.deployment.disabled': 'disabled',
}

function statusFromDeploymentStatusEvents(events: string[]): DeploymentStatus {
  for (const event of events) {
    if (isDeploymentStatusEvent(event)) {
      return statusEventToStatus[event]
    }
  }

  throw new Error(`Unknown deployment status events: ${events}`)
}