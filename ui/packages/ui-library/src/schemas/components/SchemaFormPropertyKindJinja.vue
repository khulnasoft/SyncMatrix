<template>
  <p-content class="schema-form-property-kind-jinja">
    <p-code-input v-model="value" lang="jinja" :state="state" show-line-numbers />
    <SchemaFormPropertyErrors :errors="errors" />
  </p-content>
</template>

<script lang="ts" setup>
  import { State } from '@syncmatrix/design'
  import { computed } from 'vue'
  import SchemaFormPropertyErrors from '@/schemas/components/SchemaFormPropertyErrors.vue'
  import { SyncmatrixKindJinja } from '@/schemas/types/schemaValues'
  import { SchemaValueError } from '@/schemas/types/schemaValuesValidationResponse'

  const props = defineProps<{
    value: SyncmatrixKindJinja,
    errors: SchemaValueError[],
    state: State,
  }>()

  const emit = defineEmits<{
    'update:value': [SyncmatrixKindJinja],
  }>()

  const value = computed({
    get() {
      return props.value.template
    },
    set(template) {
      emit('update:value', {
        __syncmatrix_kind: 'jinja',
        template,
      })
    },
  })
</script>