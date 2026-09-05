<script setup lang="ts">
import { computed } from "vue";
import UnitSlot from "./components/UnitSlot.vue";
import { workstationUnits } from "./unitRegistry";

const foundationStatus = computed(() => "FOUNDATION / UNIT CONTRACT ACTIVE");
</script>

<template>
  <main class="works-shell">
    <header class="works-header">
      <div>
        <div class="eyebrow">VERTEX WORKS</div>
        <h1>WORKSTATION</h1>
      </div>
      <div class="status">{{ foundationStatus }}</div>
    </header>

    <section class="unit-grid">
      <UnitSlot
        v-for="unit in workstationUnits"
        :key="unit.manifest.id"
        :definition="unit"
      />
    </section>

    <footer class="works-footer">
      <span>UNIT METHOD</span>
      <span>NO WELDED DEPENDENCY</span>
      <span>HOST NEUTRAL</span>
      <span>DETACHABLE</span>
    </footer>
  </main>
</template>

<style scoped>
.works-shell {
  min-height: 100vh;
  padding: 20px;
  display: grid;
  grid-template-rows: auto 1fr auto;
  gap: 16px;
}

.works-header, .works-footer {
  border: 1px solid #26313a;
  background: #0f151b;
  border-radius: 12px;
}

.works-header {
  padding: 16px 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.eyebrow {
  font-size: 11px;
  letter-spacing: 0.22em;
  opacity: .65;
}

h1 {
  margin: 2px 0 0;
  font-size: 20px;
  letter-spacing: .08em;
}

.status {
  font-size: 12px;
  opacity: .72;
}

.unit-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 16px;
  min-height: 0;
}

.works-footer {
  min-height: 34px;
  padding: 8px 12px;
  display: flex;
  gap: 18px;
  align-items: center;
  flex-wrap: wrap;
  font-size: 10px;
  letter-spacing: .12em;
  opacity: .65;
}

@media (max-width: 900px) {
  .unit-grid {
    grid-template-columns: 1fr;
  }
}
</style>
