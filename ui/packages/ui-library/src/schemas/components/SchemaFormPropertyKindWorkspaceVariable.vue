<template>
  <WorkspaceVariableCombobox v-model:selected="value" class="schema-form-property-kind-workspace-variable" />
</template>

<script lang="ts" setup>
  /* eslint-disable camelcase */
  import { computed } from 'vue'
  import WorkspaceVariableCombobox from '@/components/WorkspaceVariableCombobox.vue'
  import { SyncmatrixKindWorkspaceVariable } from '@/schemas/types/schemaValues'

  const props = defineProps<{
    value: SyncmatrixKindWorkspaceVariable,
  }>()

  const emit = defineEmits<{
    'update:value': [SyncmatrixKindWorkspaceVariable],
  }>()

  const value = computed({
    get() {
      return props.value.variable_name
    },
    set(variable_name) {
      emit('update:value', {
        __syncmatrix_kind: 'workspace_variable',
        variable_name,
      })
    },
  })
</script>