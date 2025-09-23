<template>
    <div class="height100">
        <div>
            <UtilsTitle :title="'采购执行'">
            </UtilsTitle>
        </div>
        <SearchHeader :formList="formList" :height="'150px'" @search="search"></SearchHeader>
        <div class="border1"></div>
        <div class="needs-table">
            <div class="menu">
                <a-menu v-model:selectedKeys="menusCurrent" mode="horizontal" :items="menus" @select="selectItem" />
            </div>
            <div class="table-header">
                <a-button class="button-top" @click="addExecuteDialog">
                    <img src="@/assets/images//add.png" style="height: 14px;">
                    新增</a-button>
            </div>
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
                                <div class="del-style" @click="openConfirm(record)" v-if="record.purchaseStatus == '1'">
                                    删除
                                </div>
                                <div class="del-style" v-else>

                                </div>
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

    <!-- 弹框 -->
    <!-- 新增修改弹框 -->
    <a-modal v-model:open="modalDialog" :title="formTile" @ok="formOk" :destroyOnClose="true">
        <a-form :model="formState" ref="formRef" :rules="formRules">
            <a-form-item :label="item.label" :name="item.name" v-for="(item, index) in formEntry">
                <a-input v-model:value="formState[item.name]" :disabled="item?.disabled || false"
                    v-if="item.type === 'a-input'" class="broder-red" />
                <a-select v-model:value="formState[item.name]" style="width: 100%"
                    :placeholder="$t('placeholder.pleaseSelect')" :options="item.options" v-if="item.type === 'a-select'"
                    :allowClear="true"></a-select>
                <a-space direction="vertical" style="width: 100%" v-if="item.type == 'a-date'">
                    <a-date-picker v-model:value="formState[item.name]" style="width: 100%" />
                </a-space>
            </a-form-item>
        </a-form>
    </a-modal>

    <!-- 删除弹框 -->
    <DelModal ref="delRef" :delElementTitle="'项目'" :delElementValue="delElementValue" @delData="delData"></DelModal>
</template>

<script setup lang='ts'>
import UtilsTitle from '@/components/UtilsTitle/index.vue';
import { inject, onMounted, ref, watchEffect } from 'vue';
import SearchHeader from '@/components/SearchHeader/index.vue'
import { useRouter } from "vue-router";
import { executeApi } from '@/api/Execute/index';
import type { execute, updataExecute } from '@/api/Execute/index';
import { demandApi } from '@/api/demand';
import dayjs from 'dayjs';
import { getTypeOfPurchase, getIndustryClassification, getuserInfo } from '@/utils/UntilsHank'
import { getI18 } from '@/store/getI18Status'
import DelModal from '@/components/DelModal/index.vue'

const getI18Store = getI18()
const $router = useRouter();
const gotoManage = (record: any) => {
    $router.push({ name: 'projectManagement', query: { id: record.id } })
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
//上面的状态选择
const menusCurrent = ref<string[]>(['0'])
const menus = ref<any>(
    [
        { label: '全部', title: '全部', key: '0' },
        { label: '待发布', title: '待发布', key: '1' },
        { label: '执行中', title: '执行中', key: '2' },
        { label: '已截止', title: '已截止', key: '3' },
        { label: '已完成', title: '已完成', key: '4' },
        { label: '已废弃', title: '已废弃', key: '5' },
    ]
)
const selectItem = () => {
    getExecutrList()
}
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
    { type: 'a-select', title: '采购方式', bind: 'purchaseWay', span: 8, options: procurementMethodsOptions },
    { type: 'a-select', title: '采购类型', bind: 'type', span: 8, options: typeOfPurchase.value },//
    { type: 'a-select', title: '行业分类', bind: 'classify', span: 8, options: industryClassification.value },//
    { type: 'a-range', title: '起止时间', bind: 'startAndEndTime', span: 8 },
])
const header_formState = ref<execute>()
const search = (formState: any) => {
    header_formState.value = JSON.parse(JSON.stringify(formState))
    getExecutrList()
}
//表格相关
const loading = ref<boolean>(true)
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
        title: '采购方式',
        dataIndex: 'purchaseWay',
        width: 200,
        key: 'purchaseWay',
        align: 'center',
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
    // {
    //     title: '需求地点',
    //     dataIndex: 'demandAddress',
    //     key: 'demandAddress',
    //     align: 'center',
    //     width: 200,
    // },
    {
        title: '采购状态',
        dataIndex: 'purchaseStatus',
        key: 'purchaseStatus',
        align: 'center',
        fixed: 'right',
        width: 100,
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
        let { number, projectName, purchaseWay, startAndEndTime, classify, type } = JSON.parse(JSON.stringify(header_formState.value))
        const data = {
            status: menusCurrent.value[0],
            current: pageExecute.value.current,
            size: pageExecute.value.pageSize,
            number: number || null,
            projectName: projectName || null,
            classify: classify || null,
            type: type || null,
            purchaseWay: purchaseWay || null,
            startDate: startAndEndTime ? dayjs(startAndEndTime[0]).format('YYYY-MM-DD') : null,
            endDate: startAndEndTime ? dayjs(startAndEndTime[1]).format('YYYY-MM-DD') : null,
        }
        executeApi.getExecutePage(data).then((res: any) => {
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
            status: menusCurrent.value[0],
        }
        executeApi.getExecutePage(data).then((res: any) => {
            if (res.success) {
                // console.log('获取的exe数组', res.obj.records);
                loading.value = false
                dataSource.value = res.obj.records
                pageExecute.value.total = res.obj.total - 0
            }
        })
    }
}

//新增弹框相关
const modalDialog = ref<boolean>(false)
const formState: any = ref({})
const formTile = ref<string>()
interface entry {
    name: string,
    type: string,
    label: string,
    disabled: boolean;
    options: any;
}
const formEntry: any = ref<entry[]>()
const formRules = ref<any>([])
const formApi = ref<string>('')
const formRef = ref<any>(null)
const formOk = () => {
    switch (formApi.value) {
        case 'addExecute':
            addExecute()
            break;
        case 'editExecute':
            editExecute()
            break;
    }
}



let purchaseStatusList = [
    { color: '#FF7D00', value: '1', label: '待发布' },
    { color: '#2272DD', value: '2', label: '执行中' },
    { color: '#00B42A', value: '3', label: '已截止' },
    { color: '#00B42A', value: '4', label: '已完成' },
    { color: '#F53F3F', value: '5', label: '已废弃' },

]
//新增
const addExecuteDialog = () => {
    let proList: any = []
    demandApi.getTrueDemandList().then((res: any) => {
        if (res.success) {
            res.obj.forEach((ele: any) => {
                const TEMPOBJ = {
                    value: ele.id,
                    label: ele.projectName,
                    classify: ele.classify,
                    type: ele.type
                }
                proList.push(TEMPOBJ)
            })
        }
        addExecuteObj.formEntry[0].options = proList
        editExecuteObj.formEntry[0].options = proList
        modalDialog.value = true
        formState.value = addExecuteObj.formState
        formTile.value = addExecuteObj.formTile
        formEntry.value = addExecuteObj.formEntry
        formRules.value = addExecuteObj.formRules
        formApi.value = addExecuteObj.formApi
        addExecuteReset()
    })
}
const addExecuteReset = () => {
    formState.value.demandId = ''
    formState.value.purchaseWay = ''
}
let addExecuteObj = {
    formTile: '新增执行',
    formEntry: [
        { name: 'demandId', type: 'a-select', label: '采购需求', disabled: false, options: [] },//采购需求id,数组通过getProcurementNeedsList获取
        { name: 'purchaseWay', type: 'a-select', label: '采购方式', disabled: false, options: procurementMethodsOptions },//采购方式
    ],
    formState: {
        demandId: '',//采购需求id
        purchaseWay: '',//采购方式
    },
    formRules: {
        demandId: [{ required: true, message: '采购需求id不可为空' }],
        purchaseWay: [{ required: true, message: '采购方式不可为空' }],
    },
    formApi: 'addExecute'
}

const addExecute = () => {
    formRef.value.validate().then((res: any) => {
        if (res) {
            const data: any = {
                demandId: formState.value.demandId,
                purchaseWay: formState.value.purchaseWay,
            }
            executeApi.postExecute(data).then((res: any) => {
                if (res.success) {
                    // console.log('新增成功没', res);
                    modalDialog.value = false
                    getExecutrList()
                }
            })
        }
    })
}
//删除
let crudId = ref<string>('')
const delElementValue = ref<string>('')
const delRef = ref<any>()
const openConfirm = (record: any) => {
    delRef.value.open()
    delElementValue.value = record.projectName
    crudId.value = record.id
}
const delData = () => {
    executeApi.delExecute(crudId.value).then((res: any) => {
        if (res.success) {
            delRef.value.close()
            getExecutrList()
        }
    })
}

//编辑
const editExecuteDialog = (record: execute) => {
    modalDialog.value = true
    formState.value = editExecuteObj.formState
    formTile.value = editExecuteObj.formTile
    formEntry.value = editExecuteObj.formEntry
    formRules.value = editExecuteObj.formRules
    formApi.value = editExecuteObj.formApi
    editExecuteReset(record)
}
const editExecuteReset = (record: execute) => {
    formState.value.id = record.id
    formState.value.demandId = record.demandId
    formState.value.purchaseWay = record.purchaseWay

}
let editExecuteObj = {
    formTile: '新增执行',
    formEntry: [
        { name: 'demandId', type: 'a-select', label: '采购需求', disabled: false, options: [] },//采购需求id,数组通过getProcurementNeedsList获取
        { name: 'purchaseWay', type: 'a-select', label: '采购方式', disabled: false, options: procurementMethodsOptions },//采购方式
    ],
    formState: {
        demandId: '',//采购需求id
        purchaseWay: '',//采购方式
        id: ''
    },
    formRules: {
        demandId: [{ required: true, message: '采购需求id不可为空' }],
        purchaseWay: [{ required: true, message: '采购方式不可为空' }],
    },
    formApi: 'editExecute'
}

const editExecute = () => {
    formRef.value.validate().then((res: any) => {
        if (res) {
            const data: any = {
                id: formState.value.id,
                data: {
                    demandId: formState.value.demandId,
                    purchaseWay: formState.value.purchaseWay,
                }
            }
            executeApi.putExecute(data).then((res: any) => {
                if (res.success) {
                    console.log('编辑成功没', res);
                    modalDialog.value = false
                    getExecutrList()
                }
            })
        }
    })
}
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
    height: calc(100% - 224px);
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

