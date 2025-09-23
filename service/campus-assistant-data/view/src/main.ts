import { createApp,provide } from 'vue'
import App from './App.vue'
import router from "./router"
import Antd from 'ant-design-vue';
import 'ant-design-vue/dist/reset.css';
import '../src/assets/css/antd.less'
import "./assets/main.css";
// 引入国际化
import i18n from './i18n/index';
import { createPinia } from "pinia";
import '../src/assets/utils/grh.less'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';
import VXETable from 'vxe-table'
import 'vxe-table/lib/style.css'
// 富文本组件

createApp(App).use(router)
    .use(VXETable)
    .use(Antd)
    .use(createPinia()
    .use(piniaPluginPersistedstate))
    .use(i18n)
    .mount('#app');
