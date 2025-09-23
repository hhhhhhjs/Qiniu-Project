<template>
  <a class="meteor-pill" href="#" @click.prevent="$emit('click')">
    <span class="meteor-ring"></span>
    <slot>AUGMENT CLI — AUGGIE IS NOW AVAILABLE! →</slot>
  </a>
</template>

<script setup lang="ts">
// 无逻辑，纯展示；对外仅透出 click 事件
</script>

<style scoped>
.meteor-pill {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border-radius: 9999px;
  padding: 10px 16px;
  background: #0b0f14; /* 深色胶囊背景 */
  color: #ffffff;
  overflow: hidden;
  isolation: isolate;
  box-shadow: inset 0 0 0 1px rgba(179,186,255,0.12);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 12px;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

/* 仅显示边框这一圈的“环带” */
.meteor-ring {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  padding: 1px; /* 边框厚度 */
  /* 两层遮罩：content-box 保留边带，exclude 去掉内容区 */
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: exclude;
  mask-composite: exclude;
}

/* 旋转的锥形渐变 + 点阵遮罩，制造“流星/星屑”效果 */
.meteor-ring::before {
  content: "";
  position: absolute;
  inset: 0;
  background: conic-gradient(from 0deg, #ffffff80, #0000 60deg, #0000 300deg, #ffffff80);
  animation: meteor-spin 4s linear infinite;
  /* 点阵遮罩（可按需替换为自定义 pattern） */
  -webkit-mask: url("data:image/svg+xml;utf8,\
<svg xmlns='http://www.w3.org/2000/svg' width='28' height='24' viewBox='0 0 28 24'>\
<circle cx='14' cy='16' r='1.1' fill='black'/>\
<circle cx='19' cy='13' r='1.1' fill='black'/>\
<circle cx='1' cy='3' r='1.1' fill='black'/>\
<circle cx='26' cy='8' r='1.1' fill='black'/>\
<circle cx='13' cy='6' r='1.1' fill='black'/>\
<circle cx='10' cy='18' r='1.1' fill='black'/>\
</svg>") repeat;
  mask: url("data:image/svg+xml;utf8,\
<svg xmlns='http://www.w3.org/2000/svg' width='28' height='24' viewBox='0 0 28 24'>\
<circle cx='14' cy='16' r='1.1' fill='black'/>\
<circle cx='19' cy='13' r='1.1' fill='black'/>\
<circle cx='1' cy='3' r='1.1' fill='black'/>\
<circle cx='26' cy='8' r='1.1' fill='black'/>\
<circle cx='13' cy='6' r='1.1' fill='black'/>\
<circle cx='10' cy='18' r='1.1' fill='black'/>\
</svg>") repeat;
}

@keyframes meteor-spin {
  to { transform: rotate(360deg); }
}
</style>

