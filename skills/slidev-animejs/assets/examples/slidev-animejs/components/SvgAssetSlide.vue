<template>
  <RuntimeSvgAssetSlide :asset="asset" :step="step" />
</template>

<script setup>
import RuntimeSvgAssetSlide from '../../../templates/slidev-svg-asset-pack/components/SvgAssetSlide.vue'

defineProps({
  asset: {
    type: String,
    required: true,
  },
  step: {
    type: Number,
    default: 0,
  },
})
</script>
