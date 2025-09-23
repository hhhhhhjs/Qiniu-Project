<template>
    <div class="management-header">
        <div class="header-top">
            <div class="header-top-left">
                <div class="title" @click="gotoRetrun">
                    <left-outlined style="margin-right: 8px;" />
                    <span>{{ USERINFO.number +'/'+ USERINFO.projectName }}</span>
                </div>
            </div>
            <div class="header-top-right">
                {{ PURCHASEWAY[USERINFO.purchaseWay] }}
            </div>
        </div>
        <div class="header-bottom">
            <div class="steps">
                <a-steps v-model:current="cuurent1" label-placement="vertical" :items="items">
                    <template #renderItem="{ item }" :disabled="true">
                        {{ item }}
                    </template>
                </a-steps>
            </div>
            <div class="menu">
                <a-anchor direction="horizontal" :affix="false" :getContainer="getContainer" @click="handleNavClick"
                    :items="menus">
                </a-anchor>
            </div>
        </div>
    </div>

    <div class="management-body">
        <BasicInformation id="basicInformation" :propsid="THEID" :baseData="baseData" :current="current"
            ref="BasicInformationRef"></BasicInformation>
        <PreInvitedManufacturers :propsid="THEID" :current="current" :baseData="baseData" ref="PreInvitedManufacturersRef">
        </PreInvitedManufacturers>
        <PurchaseAttachments :propsid="THEID" :current="current" :baseData="baseData" ref="PurchaseAttachmentsRef">
        </PurchaseAttachments>
        <ResponseFile :propsid="THEID" :current="current" :baseData="baseData" ref="ResponseFileRef"></ResponseFile>
        <InventoryDetails :propsid="THEID" :current="current" :baseData="baseData" ref="InventoryDetailsRef">
        </InventoryDetails>
        <ExecuteTheProcess :propsid="THEID" :USERINFO="USERINFO" :baseData="baseData" v-if="current != 0"
            ref="ExecuteTheProcessRef"></ExecuteTheProcess>
    </div>
</template>
    
<script setup lang="ts">
import {
    LeftOutlined
} from '@ant-design/icons-vue';
import { onMounted, ref } from 'vue'
import { useRouter, useRoute } from "vue-router";
import BasicInformation from './components/basicInformation/index.vue'//基本信息
import ExecuteTheProcess from './components/executeTheProcess/index.vue'//执行进程
import InventoryDetails from './components/inventoryDetails/index.vue'//清单明细
import PreInvitedManufacturers from './components/preInvitedManufacturers/index.vue'//预邀厂商
import PurchaseAttachments from './components/purchaseAttachments/index.vue'//采购附件
import ResponseFile from './components/responseFile/index.vue'//响应文件
import { executeApi } from '@/api/Execute'
import type { execute } from '@/api/Execute'
import dayjs from 'dayjs';
const PURCHASEWAY = ['招投标', '竞争性谈判', '单一采购', '询比价']
const getContainer = () => {
    return document.querySelector(".management-body");
};
const $router = useRouter();
const $route = useRoute();
const gotoRetrun = () => {
    $router.push({ name: 'procurementExecution' })
}
let cuurent1 = 0
const current = ref<number>(1)
const items = ref<any>([
    {
        title: '待发布',
        subTitle: '',
        description: '',
    },
    {
        title: '执行中',
        subTitle: '',
    },
    {
        title: '已截止',
        subTitle: '',
    },
    {
        title: '已完成',
        subTitle: '',
    },
]);
const menus = ref<any>([])
const handleNavClick = (e: MouseEvent) => {
    // @ts-ignore
    e.preventDefault();
};

const baseData = ref<execute | undefined>()
const THEID = ref<any>('')
const USERINFO = ref<any>({
    creatorName: '',//创建人员：
    purchaseWay: '',//采购方式
    projectName: '',
    industry: '',//行业分类：
    createDate: '',//创建时间
    typeOfPurchase: '',//采购类型：
    purchaseStatus: '',//采购状态
})
const BasicInformationRef = ref<any>(null)//基本信息的ref
const PreInvitedManufacturersRef = ref<any>(null)//预邀商场的ref
const PurchaseAttachmentsRef = ref<any>(null)//采购附件的ref
const ResponseFileRef = ref<any>(null)//响应文件的ref
const InventoryDetailsRef = ref<any>(null)//清单明细的ref
const ExecuteTheProcessRef = ref<any>(null)//执行进程
const componentsInitialize = () => {
    setTimeout(() => {
        BasicInformationRef.value.initialize()
        PreInvitedManufacturersRef.value.initialize()
        PurchaseAttachmentsRef.value.initialize()
        ResponseFileRef.value.initialize()
        InventoryDetailsRef.value.initialize()
        if(current.value!=0){
            ExecuteTheProcessRef.value.initialize()
        }
    }, 1000);
}
const initialize = () => {
    THEID.value = $route.query.id //执行ID
    executeApi.getExecuteInfo($route.query.id).then((res: any) => {
        if (res.success) {
            if (res.obj) {
                USERINFO.value = res.obj
                baseData.value = res.obj
                items.value[0].subTitle = baseData.value?.createDate
                items.value[1].subTitle = baseData.value?.startDate
                items.value[2].subTitle = baseData.value?.endDate
                const today = dayjs();
                current.value = USERINFO.value.purchaseStatus - 1
                cuurent1 = current.value //设置步骤条  不是响应式变量即不可选中
                menus.value = cuurent1 != 0 ?
                    [
                        { title: '基本信息', key: 'basicInformation', href: '#basicInformation' },
                        { title: '预邀厂商', key: 'preInvitedManufacturers', href: '#preInvitedManufacturers' },
                        { title: '采购附件', key: 'purchaseAttachments', href: '#purchaseAttachments' },
                        { title: '响应文件', key: 'responseFile', href: '#responseFile' },
                        { title: '清单明细', key: 'inventoryDetails', href: '#inventoryDetails' },
                        { title: '执行进程', key: 'executeTheProcess', href: '#executeTheProcess' },
                    ] :
                    [
                        { title: '基本信息', key: 'basicInformation', href: '#basicInformation' },
                        { title: '预邀厂商', key: 'preInvitedManufacturers', href: '#preInvitedManufacturers' },
                        { title: '采购附件', key: 'purchaseAttachments', href: '#purchaseAttachments' },
                        { title: '响应文件', key: 'responseFile', href: '#responseFile' },
                        { title: '清单明细', key: 'inventoryDetails', href: '#inventoryDetails' },
                    ]
                const formattedToday = today.format('YYYY-MM-DD');
                items.value[0].description = `已创建${dateDiff(items.value[0].subTitle, formattedToday) || 0}天`
                componentsInitialize()
            }
        }
    })
}
function dateDiff(date1: string, date2: string) {
    // 将日期字符串转换为Date对象
    const d1: any = new Date(date1);
    const d2: any = new Date(date2);
    // 计算两个日期之间的毫秒差值
    const diffMilliseconds = Math.abs(d2 - d1);
    // 将毫秒差值转换为天数
    const diffDays = Math.ceil(diffMilliseconds / (1000 * 60 * 60 * 24));
    return diffDays;
}
onMounted(() => {
    initialize()
})
</script>

<style lang="less" scoped>
@import './index.less';

:deep(.ant-menu-item-selected) {
    color: #165DFF !important;
    font-weight: 550;
}

:deep(.ant-steps-item-subtitle) {
    font-size: 16px;
}

.menu {
    margin-top: 8px;
    padding-left: 16px;
}</style>