<template>
    <div class="management-header">
        <div class="header-top">
            <div class="header-top-left">
                <div class="title">
                    <left-outlined style="margin-right: 8px;height: 31px;font-size: 20px;" @click="gotoRetrun" />
                    <span v-if="baseData.projectName" style="margin-right: 12px;">{{  baseData.number +'/'+ baseData.projectName}}</span>
                    <a-button @click="openConfirm" type="primary" class="button-style" danger
                        v-if=THESTATUS>放弃该项目</a-button>
                    <a-button @click="joinProject" type="primary" class="button-style" v-else>参与该项目</a-button>
                    <!-- <span>{{ USERINFO.name }}</span> -->
                </div>
            </div>
            <div class="header-top-right" v-if="baseData.purchaseWay">
                {{ theWayList[baseData.purchaseWay].label }}
            </div>
        </div>
        <div class="header-bottom">
            <div class="steps">
                <a-steps v-model:current="current1" label-placement="vertical" :items="items">
                    <template #renderItem="{ item }">
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
        <TenderInformation :baseData="baseData" ref="TenderInformationRef"></TenderInformation>
        <TenderRules :propsid="THEID" :current="current1" :baseData="baseData" ref="TenderRulesRef"></TenderRules>
        <QAClarification :propsid="THEID" :current="current1" :baseData="baseData" ref="QAClarificationRef"></QAClarification>
        <ResponseFile :propsid="THEID" :current="current1" :baseData="baseData" :THESTATUS="THESTATUS" ref="ResponseFileRef">
        </ResponseFile>
        <InventoryDetails :propsid="THEID" :current="current1" :baseData="baseData" :THESTATUS="THESTATUS"
            ref="InventoryDetailsRef"></InventoryDetails>
        <!-- <ParticipateInTheProject :propsid="THEID"></ParticipateInTheProject> -->
    </div>

    <!-- 删除弹框 -->
    <DelModal ref="delRef" :delElementTitle="'该项目'" :delElementValue="baseData.projectName" @delData="giveupProject">
    </DelModal>
</template>
    
<script setup lang="ts">
import {
    LeftOutlined
} from '@ant-design/icons-vue';
import { onMounted, ref } from 'vue'
import { useRouter, useRoute } from "vue-router";
import TenderInformation from './components/tenderInformation/index.vue'
import TenderRules from './components/tenderRules/index.vue'
import InventoryDetails from './components/inventoryDetails/index.vue'
import QAClarification from './components/qAClarification/index.vue'
import ResponseFile from './components/responseFile/index.vue'
import { executeApi } from '@/api/Execute'
import dayjs from 'dayjs';
import { excutePartake } from '@/api/ExecutePartake'
import type { partake } from '@/api/ExecutePartake'
import { getuserInfo } from '@/utils/UntilsHank';
import { message } from 'ant-design-vue';
const getContainer = () => {
    return document.querySelector(".management-body");
};
const handleNavClick = (e: MouseEvent) => {
    // @ts-ignore
    e.preventDefault();
};
const $router = useRouter();
const $route = useRoute();
const gotoRetrun = () => {
    $router.go(-1)
}
const current = ref<number>(1)
const current1 = ref<any>(0)
const items = ref<any>([
    {
        title: '招标',
        subTitle: '2023/07/31',
        description: '已创建10天',
    },
    {
        title: '响应',
        subTitle: '2023/07/31',
    },
    {
        title: '公示',
        subTitle: '',
    }
]);
const menus = ref<any>(
    [
        { title: '招标信息', key: 'tenderInformation', href: '#tenderInformation' },
        { title: '采购附件', key: 'tenderRules', href: '#tenderRules' },
        { title: '答疑澄清', key: 'qAClarification', href: '#qAClarification' },
        { title: '响应文件', key: 'responseFile', href: '#responseFile' },
        { title: '报价清单', key: 'inventoryDetails', href: '#inventoryDetails' },
        // {title: '执行进程', key: 'executeTheProcess', href: '#executeTheProcess'  },
        // { title: '参与项目', key: 'participateInTheProject', href: '#participateInTheProject' },
    ]
)
const baseData = ref<any>({
    projectName: ''
})
const THEID = ref<any>('')
const theWayList = [
    { label: '招投标', list: ['招标', '评标', '公示'] },
    { label: '竞争性谈判', list: ['响应', '谈判', '公示'] },
    { label: '单一采购', list: ['响应', '谈判', '成交'] },
    { label: '询比价', list: ['询价', '比价', '成交'] },
]
const THESTATUS = ref<boolean>(false)

const TenderInformationRef = ref<any>(null) //招标信息
const TenderRulesRef = ref<any>(null) //采购附件
const QAClarificationRef = ref<any>(null) //答疑澄清
const ResponseFileRef = ref<any>(null) //响应文件
const InventoryDetailsRef = ref<any>(null) //报价清单

const componentsGetData = () => {
    TenderInformationRef.value.initialize()
    TenderRulesRef.value.initialize()
    QAClarificationRef.value.initialize()
    ResponseFileRef.value.initialize()
    InventoryDetailsRef.value.initialize()
}
const initialize = () => {
    THEID.value = $route.query.id
    executeApi.getExecuteInfo($route.query.id).then((res2: any) => {
        if (res2.success) {
            baseData.value = res2.obj
            if (baseData.value['purchaseStatus'] == 1) {
                THESTATUS.value = true
            }
            const purchaseWay = baseData.value['purchaseWay']
            const list = theWayList[purchaseWay].list
            list.forEach((ele: any, index: number) => {
                items.value[index]['title'] = ele
            })
            items.value[0].subTitle = baseData.value?.createDate
            items.value[1].subTitle = baseData.value?.endDate
            // items.value[2].subTitle = baseData.value?.endDate
            const today = dayjs();
            const formattedToday = today.format('YYYY-MM-DD');
            const d1 = new Date(formattedToday).getTime()
            const d2 = new Date(baseData.value.endDate).getTime()
            if(d1>d2){
                current1.value = 1
            }            

            items.value[0].description = `已创建${dateDiff(items.value[0].subTitle, formattedToday) || 0}天`
            setTimeout(() => {
                componentsGetData()
            }, 500);
            
        }
    })

    //获取当前状态
    excutePartake.isPush($route.query.id).then((res: any) => {
        if (res.success) {
            if (res.success) {
                THESTATUS.value = res.obj
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

//参与项目
const joinProject = () => {
    const USER = getuserInfo()
    const data = <partake>{
        "companyId": USER.companyId,
        "executeId": THEID.value,
        "partake": false
    }
    excutePartake.addExecuteList(data).then((res: any) => {
        if (res.success) {
            message.success('参与项目成功')
            initialize()
        }
    })
}
//放弃该项目
const delElementValue = ref<string>('')
const delRef = ref<any>()
const openConfirm = (record: any) => {
    delRef.value.open()
    delElementValue.value = record.materialName
}
const giveupProject = () => {
    excutePartake.giveUpExecuteList(THEID.value).then((res: any) => {
        if (res.success) {
            message.success('项目放弃成功')
            $router.go(-1)
        }
    })
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
</style>