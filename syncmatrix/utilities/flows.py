import syncmatrix

DEFAULT_FLOW = None


def reset_default_flow():
    global DEFAULT_FLOW
    flow_name = syncmatrix.config.get("flows", "global_default_flow")
    if flow_name and flow_name != "None":
        DEFAULT_FLOW = syncmatrix.Flow("Default Flow")
        syncmatrix.context.Context.update(flow=DEFAULT_FLOW)


def get_default_flow():
    return DEFAULT_FLOW


def get_flow_by_id(id):
    """
    Retrieves a flow by its ID. This will only work for Flows that are alive
    in the current interpreter.
    """
    return syncmatrix.core.flow.FLOW_REGISTRY.get(id)
