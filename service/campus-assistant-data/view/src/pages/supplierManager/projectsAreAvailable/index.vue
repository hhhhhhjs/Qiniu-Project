<template>
    <div class="height100">
        <div >
            <UtilsTitle :title="'可参与项目'">
            </UtilsTitle>
        </div>
        <SearchHeader :formList="formList" @search="search" :height="'200px'"></SearchHeader>
        <div class="border1"></div>
        <div class="needs-table">
            <!-- <div class="table-header">

            </div> -->
            <div class="table-body">
                <a-table :dataSource="dataSource" :columns="columns" :pagination="false" :size="'middle'"
                    :scroll="{ x: 1000 }" class="ant-table-striped" :row-class-name="(record: any, index: any) => {
                        return (index - 0) % 2 == 1 ? 'bg-f' : 'bg-white'
                    }" :loading="loading">
                    <template #bodyCell="{ column, text, record, index }">
                        <template v-if="column.dataIndex === 'operate'">
                            <div class="operate-style">
                                <!-- <div class="detail-style" @click="editExecuteDialog(record)">编辑</div> -->
                                <div class="detail-style" @click="gotoManage(record)">详情</div>
                                <!-- <div class="del-style" @click="openConfirm(record)">
                                    删除
                                </div> -->
                            </div>
                        </template>

                        <template v-if="column.dataIndex === 'purchaseWay'">
                            <div v-if="procurementMethodsOptions?.length > 0 && record.purchaseWay">
                                {{ procurementMethodsOptions.filter((item: any) => item.value ==
                                    record.purchaseWay)[0]['label'] }}
                            </div>
                        </template>

                        <template v-if="column.dataIndex === 'purchaseStatus'">
                            <div v-if="purchaseStatusList?.length > 0 && record.purchaseWay">
                                <span :style="{
                                    color: purchaseStatusList.filter((item: any) => item.value == record.purchaseStatus
                                    )[0]['color']
                                }">
                                    {{ purchaseStatusList.filter((item: any) => item.value == record.purchaseStatus
                                    )[0]['label'] }}
                                </span>
                            </div>
                        </template>

                        <template v-if="column.dataIndex === 'number'" >
                           <div class="text-omit" :title="record.number">{{ record.number }}</div>
                        </template>
                        <template v-if="column.dataIndex === 'projectName'" >
                            <div class="text-omit" :title="record.projectName">{{ record.projectName }}</div>
                        </template>
                        <template v-if="column.dataIndex === 'companyName'" >
                            <div class="text-omit" :title="record.companyName">{{ record.companyName }}</div>
                        </template>

                    </template>
                </a-table>
                <div class="right-table-pages">
                    <div>
                        共 {{ pageExecute.total }} 条数据
                    </div>
                    <a-pagination v-model:current="pageExecute.current" v-model:pageSize="pageExecute.pageSize"
                        show-size-changer :total="pageExecute.total" @change="sizeChangeNeeds">
                    </a-pagination>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang='ts'>
import UtilsTitle from '@/components/UtilsTitle/index.vue';
import { inject, onMounted, ref, watchEffect } from 'vue';
import SearchHeader from '@/components/SearchHeader/index.vue'
import { useRouter } from "vue-router";
import { executeApi } from '@/api/Execute'
import type { execute, updataExecute } from '@/api/Execute'
import { demandApi } from '@/api/demand'
import dayjs from 'dayjs';
import { getTypeOfPurchase, getIndustryClassification, getuserInfo } from '@/utils/UntilsHank'
import { getI18 } from '@/store/getI18Status'
const getI18Store = getI18()
const $router = useRouter();
const gotoManage = (record: any) => {
    $router.push({ name: 'projectsAreAvailableDetail', query: { id: record.id } })
}
const $TT: any = inject('TT')
interface key_value {
    value: string,
    label: string
}
let typeOfPurchase = ref<key_value[]>(getTypeOfPurchase())
let industryClassification = ref<key_value[]>(getIndustryClassification())
watchEffect((onInvalidate) => {
    getI18Store.lang
    onInvalidate(() => {
        formList.value[3].options = getTypeOfPurchase()
        formList.value[4].options = getIndustryClassification()
    })
})
let procurementMethodsOptions = [
    { value: '0', label: '招投标' },
    { value: '1', label: '竞争性谈判' },
    { value: '2', label: '单一采购' },
    { value: '3', label: '询比价' },
]
//header serach
let formList = ref([
    { type: 'a-input', title: '项目名称', bind: 'projectName', span: 8 },
    { type: 'a-input', title: '项目编码', bind: 'number', span: 8 },
    { type: 'a-input', title: '采购单位', bind: 'companyName', span: 8 },
    { type: 'a-input', title: '联系人员', bind: 'contacts', span: 8 },
    { type: 'a-select', title: '采购方式', bind: 'purchaseWay', span: 8, options: procurementMethodsOptions },
    { type: 'a-select', title: '采购类型', bind: 'type', span: 8, options: typeOfPurchase.value },//
    { type: 'a-select', title: '行业分类', bind: 'classify', span: 8, options: industryClassification.value },//
    { type: 'a-range', title: '起止时间', bind: 'startAndEndTime', span: 16 },
])
const header_formState = ref<execute>()
const search = (formState: any) => {
    header_formState.value = JSON.parse(JSON.stringify(formState))
    getExecutrList()
}
//表格相关
const loading = ref<boolean>(false)
const dataSource = ref([
])
let columns = [
    {
        title: '项目编码',
        dataIndex: 'number',
        width: 200,
        key: 'number',
        align: 'center',
    },
    {
        title: '项目名称',
        dataIndex: 'projectName',
        width: 200,
        key: 'projectName',
        align: 'center',
        // fixed: 'left',
    },
    {
        title: '采购单位',
        dataIndex: 'companyName',
        width: 200,
        key: 'companyName',
        align: 'center',
        // fixed: 'left',
    },
    {
        title: '联系人员',
        dataIndex: 'contacts',
        width: 200,
        key: 'contacts',
        align: 'center',
        // fixed: 'left',
    },
    {
        title: '创建人员',
        width: 200,
        dataIndex: 'creatorName',
        key: 'creatorName',
        align: 'center',
    },
    {
        title: '创建时间',
        dataIndex: 'createDate',
        width: 200,
        key: 'createDate',
        align: 'center',
    },
    {
        title: '采购方式',
        dataIndex: 'purchaseWay',
        width: 200,
        key: 'purchaseWay',
        align: 'center',
    },
    {
        title: '采购类型',
        dataIndex: 'type',
        key: 'type',
        align: 'center',
        width: 200,
    },
    {
        title: '行业分类',
        dataIndex: 'classify',
        key: 'classify',
        align: 'center',
        width: 200,
    },
    {
        title: '开始时间',
        dataIndex: 'startDate',
        key: 'startDate',
        align: 'center',
        width: 200,
    },
    {
        title: '结束时间',
        dataIndex: 'endDate',
        key: 'endDate',
        align: 'center',
        width: 200,
    },
    {
        title: '操作',
        dataIndex: 'operate',
        key: 'operate',
        align: 'center',
        fixed: 'right',
        width: 150,
    },
]
const getExecutrList = () => {
    loading.value = true
    if (header_formState.value) {
        let { number, projectName, purchaseWay, startAndEndTime, classify, type, companyName, creatorName,contacts } = JSON.parse(JSON.stringify(header_formState.value))
        const data = {
            current: pageExecute.value.current,
            size: pageExecute.value.pageSize,
            creatorName: creatorName || null,
            companyName: companyName || null,
            contacts:contacts||null,
            number: number || null,
            projectName: projectName || null,
            classify: classify || null,
            type: type || null,
            purchaseWay: purchaseWay || null,
            startDate: startAndEndTime ? dayjs(startAndEndTime[0]).format('YYYY-MM-DD') + ' ' + '00:00:00' : null,
            endDate: startAndEndTime ? dayjs(startAndEndTime[1]).format('YYYY-MM-DD') + ' ' + '23:59:59' : null,
        }
        executeApi.getVendorExecuteIndexListPage(data).then((res: any) => {
            if (res.success) {
                // console.log('获取的exe数组', res.obj.records);
                loading.value = false
                dataSource.value = res.obj.records
                pageExecute.value.total = res.obj.total - 0
            }
        })
    } else {
        const data = {
            current: pageExecute.value.current,
            size: pageExecute.value.pageSize,
        }
        executeApi.getVendorExecuteIndexListPage(data).then((res: any) => {
            if (res.success) {
                // console.log('获取的exe数组', res.obj.records);
                loading.value = false
                dataSource.value = res.obj.records
                pageExecute.value.total = res.obj.total - 0
            }
        })
    }
}

let purchaseStatusList = [
    { color: '#FF7D00', value: '1', label: '待发布' },
    { color: '#2272DD', value: '2', label: '执行中' },
    { color: '#00B42A', value: '3', label: '已截止' },
    { color: '#00B42A', value: '4', label: '已完成' },
    { color: '#F53F3F', value: '5', label: '已废弃' },

]
const procurmentList = ref<any>()
const getProcurementNeedsList = () => {
    let proList: any = []
    const data: any = {
        current: 1,
        size: 100
    }
    demandApi.getDemandList(data).then((res: any) => {
        if (res.success) {
            res.obj.records.forEach((ele: any) => {
                const TEMPOBJ = {
                    value: ele.id,
                    label: ele.projectName,
                    classify: ele.classify,
                    type: ele.type
                }
                proList.push(TEMPOBJ)
            })
        }
        procurmentList.value = proList
    })
}
const USERINFO = getuserInfo()

// 分页
interface page {
    current: number;
    pageSize: number;
    total: number;
}
const pageExecute = ref<page>(
    {
        current: 1,
        pageSize: 10,
        total: 0,
    }
)
const sizeChangeNeeds = () => {
    getExecutrList()
}

onMounted(() => {
    getExecutrList()
    getProcurementNeedsList()
})
</script>

<style scoped lang="less">
.height100 {
    height: 100%;
}

.border1 {
    border-bottom: dotted 2px #F1F2F4;
    margin-left: 32px;
    margin-right: 32px;
    margin-bottom: 24px;
}

.needs-table {
    background-color: #fff;
    height: calc(100% - 274px);
    overflow: hidden;

    .table-header {
        height: 40px;
        display: flex;
        justify-content: right;
        align-items: center;
        margin-right: 24px;
        margin-bottom: 12px;
        margin-top: 16px;

        .button-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #1357AF;
            color: #fff;
            height: 32px;
            width: 96px;
            height: 32px;
            padding: 5px 22px;
            margin-top: 12px;
            font-weight: 500;
        }
    }

    .table-body {
        margin-left: 24px;
        // margin-right: 24px;
        padding-right: 12px;
        height: calc(100% - 148px);
        overflow: hidden;
        overflow-y: auto;

        .operate-style {
            display: flex;
            justify-content: space-around;
        }

        .detail-style {
            color: var(--unnamed, #2272DD);
            font-family: PingFang SC;
            font-size: 14px;
            font-style: normal;
            font-weight: 400;
            line-height: 22px;
            cursor: pointer;
            /* 157.143% */
        }

        .del-style {
            color: var(--5, #F53F3F);
            font-family: PingFang SC;
            font-size: 14px;
            font-style: normal;
            font-weight: 400;
            line-height: 22px;
            cursor: pointer;
            /* 157.143% */
        }
    }

    .right-table-pages {
        margin-top: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

}

.mar-left-16 {
    padding-left: 16px;
    background-color: #fff;
}

:deep(.ant-menu-item-selected) {
    color: #165DFF !important;
    font-weight: 550;
}
</style>

