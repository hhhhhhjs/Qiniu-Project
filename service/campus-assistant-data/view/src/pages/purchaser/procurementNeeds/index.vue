<template>
    <div class="height100">
        <div >
            <!-- 采购需求管理 -->
            <UtilsTitle :title="$t('purchaser.procurementNeeds.procurementRequirementsManagement')">
            </UtilsTitle>
        </div>
        <SearchHeader :formList="formList"  :height="'150px'"  @search="search"></SearchHeader>
        <div class="border1"></div>
        <div class="needs-table">
            <div class="table-header">
                <a-button class="button-top" @click="addNeedsDialog">
                    <img src="@/assets/images//add.png" style="height: 14px;">
                    <!-- 新增 -->
                    {{ $t('placeholder.new') }}
                </a-button>
            </div>
            <div class="table-body">
                <a-table :dataSource="dataSource" :columns="columns" :pagination="false" :size="'middle'"
                    class="ant-table-striped" :row-class-name="(record: any, index: any) => {
                        return (index - 0) % 2 == 1 ? 'bg-f' : 'bg-white'
                    }" :loading="loading">
                    <template #bodyCell="{ column, text, record,index }">
                        <template v-if="column.dataIndex === 'operate'">
                            <div class="operate-style">
                                <div class="detail-style" @click="editNeedsDialog(record)"><!-- 编辑 -->{{
                                    $t('placeholder.edit') }}</div>
                                <div class="del-style" @click="openConfirm(record)">
                                    <!-- 删除 --> {{ $t('placeholder.delete') }}
                                </div>
                            </div>
                        </template>

                        <template v-if="column.dataIndex === 'company'">
                            <div v-if="companyList?.length > 0 && record.company">
                                {{ companyList.filter((item: any) => item.id == record.company)[0]['companyName'] }}
                            </div>
                        </template>

                        <template v-if="column.dataIndex === 'number'">
                           <div class="text-omit"  :title="record.number">{{ record.number }}</div>
                        </template>
                        <template v-if="column.dataIndex === 'projectName'">
                            <div class="text-omit"  :title="record.projectName">{{ record.projectName }}</div>
                        </template>
                        <template v-if="column.dataIndex === 'companyName'">
                            <div class="text-omit"  :title="record.companyName">{{ record.companyName }}</div>
                        </template>
                    </template>
                </a-table>
                <div class="right-table-pages">
                    <div>
                        <!-- 共xx条数据 -->
                        {{ $t('placeholder.allOf') }} {{ pagePoint.total }} {{ $t('placeholder.strip') }}{{
                            $t('placeholder.data') }}
                    </div>
                    <a-pagination v-model:current="pagePoint.current" v-model:pageSize="pagePoint.pageSize"
                        show-size-changer :total="pagePoint.total" @change="sizeChangeNeeds">
                    </a-pagination>
                </div>
            </div>
        </div>
    </div>

    <!-- 弹框 -->
    <!-- 新增修改弹框 -->
    <a-modal v-model:open="modalDialog" :title="formTile" @ok="formOk" :destroyOnClose="true">
        <a-form :model="formState" ref="formRef" :rules="formRules" >
            <a-form-item :label="item.label" :name="item.name" v-for="(item, index) in formEntry">
                <a-input v-model:value="formState[item.name]" :disabled="item?.disabled || false"
                    v-if="item.type === 'a-input'" class="broder-red" />
                <a-select v-model:value="formState[item.name]" style="width: 100%"
                    :placeholder="$t('placeholder.pleaseSelect')" :options="item.options"
                    v-if="item.type === 'a-select'" :allowClear="true"></a-select>
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
const $TT: any = inject('TT')
import { demandApi } from '@/api/demand'
import type { demand, editDemand } from '@/api/demand'
import { companyApi } from '@/api/company'
import { ExclamationCircleOutlined } from "@ant-design/icons-vue";
import dayjs from "dayjs";
import { getTypeOfPurchase, getIndustryClassification, getuserInfo } from '@/utils/UntilsHank'
import { getI18 } from '@/store/getI18Status'
import DelModal from '@/components/DelModal/index.vue'
import cityData from '@/utils/useCityData'
const getI18Store = getI18()
interface key_value {
    value: string,
    label: string
}
let typeOfPurchase = ref<key_value[]>(getTypeOfPurchase())
let industryClassification = ref<key_value[]>(getIndustryClassification())
watchEffect((onInvalidate) => {
    getI18Store.lang
    onInvalidate(() => {
        formList.value[2].options = getTypeOfPurchase()
        formList.value[3].options = getIndustryClassification()
    })
})
const companyList = ref<any>()
const getCompanyList = () => {
    const data: any = {
        size: 100,
        current: 1
    }
    companyApi.getCompanyList().then((res: any) => {
        if (res.success) {
            companyList.value = res.obj.records
        }
    })
}
let formList = ref<any>([
    // 采购编号
    { type: 'a-input', title: $TT('purchaser.procurementNeeds.purchaseNumber'), bind: 'number', span: 8 },
    // 项目名称
    { type: 'a-input', title: $TT('purchaser.procurementNeeds.projectName'), bind: 'projectName', span: 8 },
    // 采购类型
    {
        type: 'a-select', title: $TT('purchaser.procurementNeeds.typeOfPurchase'), bind: 'type', span: 8, options: typeOfPurchase.value
    },
    // 行业分类
    {
        type: 'a-select', title: $TT('purchaser.procurementNeeds.industryClassification'), bind: 'classify', span: 8, options: industryClassification.value
    },
    // 创建时间
    { type: 'a-range', title: $TT('purchaser.procurementNeeds.startAndEndTime'), bind: 'startAndEndTime', span: 16 },
])
const header_formState = ref<demand>()
const search = (formState: any) => {
    header_formState.value = JSON.parse(JSON.stringify(formState))
    getDemandList()
}
const dataSource = ref<demand[]>([

])
const loading = ref<boolean>(true)
let columns = [
    {
        title: '项目编码',
        dataIndex: 'number',
        key: 'number',
        align: 'center',
    },
    {
        title: '项目名称',
        dataIndex: 'projectName',
        key: 'projectName',
        align: 'center',
    },
    {
        title: '采购单位',
        dataIndex: 'companyName',
        key: 'companyName',
        align: 'center',
    },
    {
        title: '采购类型',
        dataIndex: 'type',
        key: 'type',
        align: 'center',
    },
    {
        title: '行业分类',
        dataIndex: 'classify',
        key: 'classify',
        align: 'center',
    },
    {
        title: '创建时间',
        dataIndex: 'createDate',
        key: 'createDate',
        align: 'center',
    },
    {
        title: '创建人员',
        dataIndex: 'creatorName',
        key: 'creatorName',
        align: 'center',
    },
    {
        title: '需求地点',
        dataIndex: 'demandAddress',
        key: 'demandAddress',
        align: 'center',
    },
    {
        title: '操作',
        dataIndex: 'operate',
        key: 'operate',
        align: 'center',
    },
]

interface page {
    current: number;
    pageSize: number;
    total: number;
}
const pagePoint = ref<page>(
    {
        current: 1,
        pageSize: 10,
        total: 0,
    }
)
const sizeChangeNeeds = () => {
    getDemandList()
}
const getDemandList = () => {
    loading.value = true
    if (header_formState.value) {
        let { classify, startAndEndTime, number, projectName, type } = JSON.parse(JSON.stringify(header_formState.value))
        let endDate = ''
        let startDate = ''
        if (startAndEndTime) {
            startDate = dayjs(startAndEndTime[0]).format('YYYY-MM-DD')
            endDate = dayjs(startAndEndTime[1]).format('YYYY-MM-DD')
        }
        const data: any = {
            classify, startDate, endDate, number, projectName, type, current: pagePoint.value.current,
            size: pagePoint.value.pageSize
        }
        demandApi.getDemandList(data).then((res: any) => {
            if (res.success) {
                loading.value = false
                const temp_list = res.obj.records
                dataSource.value = temp_list
                pagePoint.value.total = res.obj.total - 0
            }
        })
    } else {
        const data: any = {
            current: pagePoint.value.current,
            size: pagePoint.value.pageSize
        }
        demandApi.getDemandList(data).then((res: any) => {
            if (res.success) {
                loading.value = false
                const temp_list = res.obj.records
                dataSource.value = temp_list
                pagePoint.value.total = res.obj.total- 0
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
        case 'addNedds':
            addNedds()
            break;
        case 'editNedds':
            editNedds()
            break;
    }
}



//新增
const addNeedsDialog = () => {
    modalDialog.value = true
    formState.value = addNeddsObj.formState
    formTile.value = addNeddsObj.formTile
    formEntry.value = addNeddsObj.formEntry
    formRules.value = addNeddsObj.formRules
    formApi.value = addNeddsObj.formApi
    addNeedsReset()
}
const addNeedsReset = () => {
    formState.value['projectName'] = ''
    formState.value['type'] = ''
    formState.value['classify'] = ''
}
const addNeddsObj = {
    formTile: '新增需求',
    formEntry: [
        { name: 'projectName', type: 'a-input', label: '项目名称', disabled: false },
        {
            name: 'type', type: 'a-select', label: '采购类型', disabled: false, options:
                typeOfPurchase.value,
        },
        {
            name: 'classify', type: 'a-select', label: '行业分类', disabled: false, options: industryClassification.value
        },
        {
            name: 'demandAddress', type: 'a-input', label: '需求地点', disabled: false
        },
        //a-cascader
    ],
    formState: {
        projectName: '',//项目名称
        type: '',//采购类型
        classify: '',//行业分类
        demandAddress:'',//需求地点
    },
    formRules: {
        projectName: [{ required: true, message: '项目名称不可为空' }],
        type: [{ required: true, message: '采购类型不可为空' }],
        classify: [{ required: true, message: '行业分类不可为空' }],
        demandAddress: [{ required: true, message: '需求地点不可为空' }],
    },
    formApi: 'addNedds'
}
const addNedds = () => {
    formRef.value.validate().then((res: any) => {
        if (res) {
            const data: any =formState.value
            demandApi.addDemand(data).then((res: any) => {
                if (res.success) {
                    modalDialog.value = false
                    getDemandList()
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
    demandApi.delDemand(crudId.value).then((res: any) => {
        if (res.success) {
            delRef.value.close()
            getDemandList()
        }
    })
}


//编辑
const editNeedsDialog = (record: demand) => {
    modalDialog.value = true
    formState.value = editNeddsObj.formState
    formTile.value = editNeddsObj.formTile
    formEntry.value = editNeddsObj.formEntry
    formRules.value = editNeddsObj.formRules
    formApi.value = editNeddsObj.formApi
    crudId.value = record.id
    editNeedsReset(record)
}
const editNeedsReset = (record: demand) => {
    formState.value['projectName'] = record.projectName
    formState.value['type'] = record.type
    formState.value['classify'] = record.classify
    formState.value['demandAddress'] = record.demandAddress
}
const editNeddsObj = {
    formTile: '编辑需求',
    formEntry: [
        { name: 'projectName', type: 'a-input', label: '项目名称', disabled: false },
        {
            name: 'type', type: 'a-select', label: '采购类型', disabled: false, options:
                typeOfPurchase.value,
        },
        {
            name: 'classify', type: 'a-select', label: '行业分类', disabled: false, options: industryClassification.value
        },
        {
            name: 'demandAddress', type: 'a-input', label: '需求地点', disabled: false
        },
        //a-cascader
    ],
    formState: {
        projectName: '',//项目名称
        type: '',//采购类型
        classify: '',//行业分类
        demandAddress:'',//需求地点
    },
    formRules: {
        projectName: [{ required: true, message: '项目名称不可为空' }],
        type: [{ required: true, message: '采购类型不可为空' }],
        classify: [{ required: true, message: '行业分类不可为空' }],
        demandAddress: [{ required: true, message: '需求地点不可为空' }],
    },
    formApi: 'editNedds'
}
const editNedds = () => {
    formRef.value.validate().then((res: any) => {
        if (res) {
            const form: any = formState.value
            const data: editDemand = {
                id: crudId.value,
                data: form
            }
            demandApi.editDemand(data).then((res: any) => {
                if (res.success) {
                    modalDialog.value = false
                    getDemandList()
                }
            })
        }
    })
}

onMounted(() => {
    getDemandList()
    // getCompanyList()
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

    .table-header {
        height: 50px;
        display: flex;
        justify-content: right;
        align-items: center;
        margin-right: 24px;
        margin-bottom: 12px;

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
        height: calc(100% - 100px);
        overflow-y: auto;

        ::-webkit-scrollbar {
            width: 1rem !important
                /* 8/16 */
            ;
            /* 纵向滚动条*/
            height: 1rem !important
                /* 8/16 */
            ;
            /* 横向滚动条 */
            background-color: #fff;
        }

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
</style>