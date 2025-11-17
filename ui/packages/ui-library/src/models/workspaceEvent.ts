import { capitalize } from 'vue'
import { formatDate, formatDateTimeNumeric, formatTimeNumeric } from '@/utilities/dates'
import { removeSyncmatrixEventLabelPrefix } from '@/utilities/events'
import { createTuple } from '@/utilities/tuples'

/*
 * This are a list of known resource id prefixes. A resource id is something like `syncmatrix.flow-run.24a73358-f660-462a-9d19-10ae5037415f`
 * We use these as a means to identify specific resources and and create specific ui experiences based on them.
 *
 * Note: Currently we're conflating resource ids and roles. Not everything in this list is even a valid resource id from a syncmatrix perspective.
 * Technically anything is a valid id (users can create their own), but for example `syncmatrix.creator` is never used as a resource id internally.
 * However "creator" is a valid resource role. So you might see this as a related resource on an event
 *
 * {
 *    "syncmatrix.resource.id": "syncmatrix.deployment.8afa5630-d5ee-4d7b-b0db-558fd1aedb22",
 *    "syncmatrix.resource.role": "creator",
 *    "syncmatrix.resource.name": "10611b"
 *  }
 *
 * Notice that the role is "creator". But since we're inferring our list of known roles from this list of known resource id prefixes
 * you'll see `syncmatrix.creator` in this list. Even though that is not a valid resource id prefix. This will hopefully be fixed as a follow up
 * to opens sourcing events in the ui. But priorities may dictate that this wont change for a while.
 */
export const { values: syncmatrixEventPrefixes } = createTuple([
  'syncmatrix.block-document',
  'syncmatrix.deployment',
  'syncmatrix.flow-run',
  'syncmatrix.flow',
  'syncmatrix.task-run',
  'syncmatrix.work-queue',
  'syncmatrix.work-pool',
  'syncmatrix.tag',
  'syncmatrix.concurrency-limit',
  'syncmatrix.artifact-collection',
  'syncmatrix.automation',
  'syncmatrix.creator',

  // cloud only but here for simplicity
  'syncmatrix-cloud.actor',
  'syncmatrix-cloud.automation',
  'syncmatrix-cloud.workspace',
  'syncmatrix-cloud.webhook',
])
export type SyncmatrixEventPrefixes = typeof syncmatrixEventPrefixes[number]

export const syncmatrixResourceRoles = syncmatrixEventPrefixes.map(prefix => prefix.split('.').at(-1)!)
export type SyncmatrixResourceRole = SyncmatrixEventPrefixes extends `${string}.${infer T}` ? T : never

export function isSyncmatrixResourceRole(value: unknown): value is SyncmatrixResourceRole {
  return syncmatrixResourceRoles.includes(value as SyncmatrixResourceRole)
}

export type WorkspaceEventResource = {
  'syncmatrix.resource.id': string,
  'syncmatrix.resource.role'?: string,
  'syncmatrix.resource.name'?: string,
  'syncmatrix.name'?: string,
  'syncmatrix-cloud.name'?: string,
} & Record<string, string | undefined>

export type WorkspaceEventRelatedResource = WorkspaceEventResource & {
  'syncmatrix.resource.role': string,
}

export type IWorkspaceEvent = {
  id: string,
  account: string,
  event: string,
  occurred: Date,
  payload: unknown,
  received: Date,
  related: WorkspaceEventRelatedResource[],
  resource: WorkspaceEventResource,
  workspace: string | null,
}

export class WorkspaceEvent implements IWorkspaceEvent {
  public id: string
  public account: string
  public event: string
  public occurred: Date
  public payload: unknown
  public received: Date
  public related: WorkspaceEventRelatedResource[]
  public resource: WorkspaceEventResource
  public workspace: string | null

  public constructor(event: IWorkspaceEvent) {
    this.id = event.id
    this.account = event.account
    this.event = event.event
    this.occurred = event.occurred
    this.payload = event.payload
    this.received = event.received
    this.related = event.related
    this.resource = event.resource
    this.workspace = event.workspace
  }

  public getRelatedByRole(role: SyncmatrixResourceRole): WorkspaceEventRelatedResource | null {
    return this.related.find(value => value['syncmatrix.resource.role'] === role) ?? null
  }

  public get email(): string {
    const actor = this.getRelatedByRole('actor')

    return actor?.['syncmatrix-cloud.email'] ?? ''
  }

  public get actorName(): string | null {
    const actor = this.getRelatedByRole('actor')

    return actor?.['syncmatrix-cloud.name'] ?? null
  }

  public get workspaceHandle(): string {
    const workspace = this.getRelatedByRole('workspace')

    return workspace?.['syncmatrix-cloud.handle'] ?? ''
  }

  public get occurredFormatted(): string {
    return formatDateTimeNumeric(this.occurred)
  }

  public get eventSyncmatrixWithoutPrefix(): string {
    return removeSyncmatrixEventLabelPrefix(this.event)
  }

  public get eventLabel(): string {
    const label = this.eventSyncmatrixWithoutPrefix.replaceAll(/[_.-]/g, ' ')

    return capitalize(label.toLocaleLowerCase())
  }

  public get occurredDate(): string {
    return formatDate(this.occurred)
  }

  public get occurredTime(): string {
    return formatTimeNumeric(this.occurred)
  }

  public get resourceId(): string {
    return this.resource['syncmatrix.resource.id']
  }
}

export function isWorkspaceEvent(value: unknown): value is WorkspaceEvent {
  return value instanceof WorkspaceEvent
}