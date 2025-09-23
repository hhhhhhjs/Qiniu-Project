<script setup lang="ts">
// import zhCN from "ant-design-vue/es/locale/zh_CN";
import i18n from './i18n/index';
import {provide} from 'vue'
provide('TT',i18n.global.t)
import { onMounted, reactive, ref, watch } from "vue";
import enUS from 'ant-design-vue/es/locale/en_US';
import zhCN from 'ant-design-vue/es/locale/zh_CN';
import dayjs from 'dayjs';
import 'dayjs/locale/zh-cn';
import { theme } from 'ant-design-vue';
const { token } = theme.useToken();

dayjs.locale('zh');
const locale = ref(zhCN.locale);
watch(locale, val => {
  dayjs.locale(val);
});

const langType = ref<boolean>(false)
// 切换英文 切换中文
const language = ref<string>(
  localStorage.getItem('lang') == 'zh' ? 'ZH' : 'EN' || 'ZH'
)
watch(
    () => langType.value,
    val => {
        if (val) {
            language.value = 'EN';
            locale.value = enUS.locale
            localStorage.setItem('lang', 'en')
            i18n.global.locale = 'en'
            // location.reload();
        } else {
            language.value = 'ZH';
            locale.value = zhCN.locale
            localStorage.setItem('lang', 'zh')
            i18n.global.locale = 'zh'
        }
    }
)
</script>

<template>
  <a-config-provider :locale="locale === 'en' ? enUS : zhCN"
  :theme="{ token: { colorPrimary: '#2454ca' } }">
    <router-view></router-view>
  </a-config-provider>
</template>

<style>
/* 删除起始页滚动条 */
/* body{
  overflow-x: hidden !important;
} */
</style>
