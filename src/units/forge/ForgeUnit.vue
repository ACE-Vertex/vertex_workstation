<script setup lang="ts">
import { forgeManifest } from "./index";
</script>

<template>
  <div class="unit">
    <div class="unit-title">MUTATION ENGINE</div>
    <div class="foundation">FOUNDATION ONLY</div>

    <div class="capabilities">
      <span v-for="capability in forgeManifest.capabilities" :key="capability">
        {{ capability }}
      </span>
    </div>

    <p>
      Incoming → Validate → Stage → Human Apply → Verify → Restore / Rollback
      will be implemented and proven end-to-end before FORGE is promoted.
    </p>
  </div>
</template>

<style scoped>
.unit { padding: 18px; }
.unit-title { font-size: 12px; letter-spacing: .16em; opacity: .7; }
.foundation { margin-top: 22px; font-size: 28px; font-weight: 700; }
.capabilities { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 18px; }
.capabilities span { padding: 6px 8px; border: 1px solid #2e3a43; border-radius: 7px; font-size: 11px; }
p { max-width: 620px; opacity: .65; line-height: 1.7; }
</style>
