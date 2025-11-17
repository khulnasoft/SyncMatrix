import syncmatrix.settings
from syncmatrix._internal.compatibility.experimental import experiment_enabled
from syncmatrix.cli.root import app

# Import CLI submodules to register them to the app
# isort: split

import syncmatrix.cli.agent
import syncmatrix.cli.artifact
import syncmatrix.cli.block
import syncmatrix.cli.cloud
import syncmatrix.cli.cloud.webhook
import syncmatrix.cli.concurrency_limit
import syncmatrix.cli.config
import syncmatrix.cli.deploy
import syncmatrix.cli.deployment
import syncmatrix.cli.dev
import syncmatrix.cli.flow
import syncmatrix.cli.flow_run
import syncmatrix.cli.kubernetes
import syncmatrix.cli.profile
import syncmatrix.cli.project
import syncmatrix.cli.server
import syncmatrix.cli.variable
import syncmatrix.cli.work_pool
import syncmatrix.cli.work_queue
import syncmatrix.cli.worker
import syncmatrix.cli.task_run
