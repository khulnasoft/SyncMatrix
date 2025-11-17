export type RunGraphEventResource = {
  'syncmatrix.resource.id': string,
  'syncmatrix.resource.role'?: string,
  'syncmatrix.resource.name'?: string,
  'syncmatrix.name'?: string,
  'syncmatrix-cloud.name'?: string,
} & Record<string, string | undefined>

export type EventRelatedResource = RunGraphEventResource & {
  'syncmatrix.resource.role': string,
}

export type RunGraphEvent = {
  id: string,
  occurred: Date,
  event: string,
  payload: unknown,
  received: Date,
  related: EventRelatedResource[],
  resource: RunGraphEventResource,
}