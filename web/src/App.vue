<template>
  <router-view></router-view>
</template>

<script setup lang="ts">
import jixiaomeiImg from '@/assets/images/roles/jixiaomei.jpg'
import feidudu from '@/assets/images/roles/肥嘟嘟左卫门.jpg'
import labixx from '@/assets/images/roles/image.png' // 这里解析完之后变量名就是图片的绝对路径
import { onMounted } from 'vue'


// home 组件图片预渲染
const preLoadImages = (urls:string[]) => {
  urls.forEach((url) => {
    const img = new Image()
    img.src = url
  })
}

const imgList:string[] = [
  jixiaomeiImg,
  feidudu,
  labixx,
]

onMounted(() => {
  console.log('预渲染')
  preLoadImages(imgList)
})
</script>

<style scoped></style>
