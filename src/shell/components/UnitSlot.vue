<script setup lang="ts">
import type { VertexUnitDefinition } from "../../contracts/unit";

defineProps<{
  definition: VertexUnitDefinition;
}>();
</script>

<template>
  <section class="slot">
    <header class="slot-header">
      <div>
        <strong>{{ definition.manifest.displayName }}</strong>
        <span>v{{ definition.manifest.version }}</span>
      </div>
      <div class="badges">
        <span>{{ definition.manifest.authority }}</span>
        <span>DETACHABLE</span>
      </div>
    </header>

    <component :is="definition.component" />
  </section>
</template>

<style scoped>
.slot {
  min-height: 420px;
  border: 1px solid #28343d;
  border-radius: 14px;
  background: #0d1318;
  overflow: hidden;
  display: grid;
  grid-template-rows: auto 1fr;
}

.slot-header {
  padding: 12px 14px;
  border-bottom: 1px solid #253039;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.slot-header strong {
  letter-spacing: .08em;
}

.slot-header span {
  margin-left: 8px;
  font-size: 10px;
  opacity: .6;
}

.badges {
  display: flex;
  gap: 6px;
}
</style>
