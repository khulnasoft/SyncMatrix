import syncmatrix


class FlowRunnerTask(syncmatrix.Task):
    def run(self, flow):
        syncmatrix.context.run_flow(flow)
