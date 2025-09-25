<template>
  <div ref="containerRef" class="audio-spectrum">
    <div v-if="!isInitialized" class="text-red-500 text-center">正在初始化频谱...</div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch, nextTick } from 'vue'
import * as THREE from 'three'

interface Props {
  isActive?: boolean
  intensity?: number
  color?: string
  frequencies?: number[] // 真实频谱数据
  useRealAudio?: boolean // 是否使用真实音频数据
}

const props = withDefaults(defineProps<Props>(), {
  isActive: true,
  intensity: 0.8,
  color: '#8b5cf6', // 紫色，匹配主题
  frequencies: () => [],
  useRealAudio: false
})

const containerRef = ref<HTMLDivElement>()
const isInitialized = ref(false)

let scene: THREE.Scene
let camera: THREE.OrthographicCamera
let renderer: THREE.WebGLRenderer
let animationId: number
let spectrumBars: THREE.Mesh[] = []

const BAR_COUNT = 60
const BAR_WIDTH = 0.15
const BAR_SPACING = 0.2
const MAX_HEIGHT = 3

onMounted(async () => {
  await nextTick()
  setTimeout(() => {
    initThreeJS()
    animate()
  }, 100)
})

onUnmounted(() => {
  cleanup()
})

watch(() => props.color, (newColor) => {
  updateBarColors(newColor)
})

function initThreeJS() {
  if (!containerRef.value) {
    console.error('Container not found')
    return
  }

  console.log('Initializing Three.js...')

  // 场景
  scene = new THREE.Scene()

  // 获取容器尺寸
  const width = containerRef.value.clientWidth || 600
  const height = containerRef.value.clientHeight || 120

  console.log('Container size:', width, height)
  // 正交相机设置
  const viewWidth = BAR_COUNT * BAR_SPACING
  const viewHeight = MAX_HEIGHT * 2

  camera = new THREE.OrthographicCamera(
    -viewWidth / 2,
    viewWidth / 2,
    viewHeight / 2,
    -viewHeight / 2,
    0.1,
    1000
  )
  camera.position.set(0, 0, 5)
  camera.lookAt(0, 0, 0)

  // 渲染器
  renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true
  })
  renderer.setSize(width, height)
  renderer.setClearColor(0x000000, 0) // 透明背景
  containerRef.value.appendChild(renderer.domElement)

  // 创建频谱条
  createSpectrumBars()

  isInitialized.value = true
  console.log('Three.js initialized successfully')

  // 监听窗口大小变化
  window.addEventListener('resize', onWindowResize)
}

function createSpectrumBars() {
  console.log('Creating spectrum bars...')

  for (let i = 0; i < BAR_COUNT; i++) {
    // 使用BoxGeometry创建3D条形
    const geometry = new THREE.BoxGeometry(BAR_WIDTH, 1, BAR_WIDTH)

    const material = new THREE.MeshBasicMaterial({
      color: new THREE.Color(props.color),
      transparent: true,
      opacity: 0.8
    })

    const bar = new THREE.Mesh(geometry, material)

    // 水平排列
    bar.position.x = (i - BAR_COUNT / 2) * BAR_SPACING
    bar.position.y = 0.5 // 让条形从底部开始
    bar.position.z = 0

    spectrumBars.push(bar)
    scene.add(bar)
  }

  console.log(`Created ${spectrumBars.length} spectrum bars`)
}

function animate() {
  if (!renderer || !scene || !camera) return

  animationId = requestAnimationFrame(animate)

  // 更新频谱条
  updateSpectrumBars()

  renderer.render(scene, camera)
}

function updateSpectrumBars() {
  if (!spectrumBars.length) return

  const time = Date.now() * 0.001
  const baseIntensity = props.isActive ? props.intensity : 0.2

  spectrumBars.forEach((bar, i) => {
    let height: number

    if (props.useRealAudio && props.frequencies.length > 0) {
      // 使用真实音频频谱数据
      const freqIndex = Math.min(i, props.frequencies.length - 1)
      const freqValue = props.frequencies[freqIndex] || 0

      // 将频谱值转换为高度
      height = freqValue * baseIntensity * MAX_HEIGHT * 2

      // 添加一些平滑处理
      height = Math.max(0.1, height)

    } else {
      // 模拟音频频谱数据 - 不同频率的波形组合
      const freq1 = Math.sin(time * 3 + i * 0.2) * 0.5 + 0.5
      const freq2 = Math.sin(time * 5 + i * 0.1) * 0.3 + 0.3
      const freq3 = Math.sin(time * 7 + i * 0.15) * 0.2 + 0.2

      // 低频到高频的衰减效果
      const freqDecay = Math.exp(-i * 0.03)

      // 组合频谱数据
      height = (freq1 + freq2 + freq3) * baseIntensity * freqDecay * MAX_HEIGHT

      // 添加随机噪声模拟真实音频
      if (props.isActive) {
        height += (Math.random() - 0.5) * baseIntensity * 0.8
      }

      height = Math.max(0.2, height) // 最小高度
    }

    // 平滑过渡
    const currentHeight = bar.scale.y
    const targetHeight = height
    bar.scale.y = THREE.MathUtils.lerp(currentHeight, targetHeight, 0.15)

    // 根据高度调整透明度
    const material = bar.material as THREE.MeshBasicMaterial
    const intensity = Math.min(1, height / MAX_HEIGHT)
    material.opacity = 0.4 + intensity * 0.6
  })
}

function updateBarColors(newColor: string) {
  spectrumBars.forEach(bar => {
    const material = bar.material as THREE.MeshBasicMaterial
    material.color = new THREE.Color(newColor)
  })
}

function onWindowResize() {
  if (!containerRef.value || !camera || !renderer) return

  const width = containerRef.value.clientWidth || 600
  const height = containerRef.value.clientHeight || 120

  // 更新正交相机的视锥体
  const viewWidth = BAR_COUNT * BAR_SPACING
  const viewHeight = MAX_HEIGHT * 2

  camera.left = -viewWidth / 2
  camera.right = viewWidth / 2
  camera.top = viewHeight / 2
  camera.bottom = -viewHeight / 2
  camera.updateProjectionMatrix()
  renderer.setSize(width, height)
}

function cleanup() {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }

  window.removeEventListener('resize', onWindowResize)

  if (renderer && containerRef.value) {
    containerRef.value.removeChild(renderer.domElement)
    renderer.dispose()
  }

  // 清理几何体和材质
  spectrumBars.forEach((bar: THREE.Mesh) => {
    bar.geometry.dispose()
    if (Array.isArray(bar.material)) {
      bar.material.forEach((mat: THREE.Material) => mat.dispose())
    } else {
      bar.material.dispose()
    }
  })

  spectrumBars = []
}
</script>

<style scoped>
.audio-spectrum {
  width: 100%;
  height: 120px;
  position: relative;
  background: transparent;
  border-radius: 16px;
}

.audio-spectrum canvas {
  display: block;
  width: 100% !important;
  height: 100% !important;
  border-radius: 16px;
}
</style>
