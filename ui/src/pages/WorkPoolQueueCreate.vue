<template>
  <p-layout-default>
    <template #header>
      <PageHeadingWorkPoolQueueCreate :work-pool-name="workPoolName" />
    </template>

    <WorkPoolQueueCreateForm :work-pool-name="workPoolName" />
  </p-layout-default>
</template>

<script lang="ts" setup>
  import { PageHeadingWorkPoolQueueCreate, WorkPoolQueueCreateForm } from '@syncmatrix/ui-library'
  import { useRouteParam } from '@syncmatrix/vue-compositions'
  import { usePageTitle } from '@/compositions/usePageTitle'

  const workPoolName = useRouteParam('workPoolName')

  usePageTitle('Create Work Pool Queue')
</script>