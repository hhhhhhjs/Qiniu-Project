<!-- 预邀厂商 -->
<template>
    <div class="basicInfo" id="inventoryDetails">
        <div class="basic-item">
            <UtilsTitle :title="'报价清单'">
                <!-- <a-button class="add-style" @click="addexecuteListDialog" v-if="!disabledFlag">新增</a-button> -->
            </UtilsTitle>
            <div class="table-style">
                <a-steps progress-dot :current="current" direction="vertical">
                    <a-step>
                        <template #title>
                            <div class="tender-header">
                                <div class="tender-status">
                                    响应报价
                                </div>

                                <div class="tender-time">
                                    {{ respondToQuotes }}
                                </div>
                            </div>
                        </template>
                        <template #description>
                            <vxe-table border show-overflow :data="dataSource" :column-config="{ resizable: true }"
                                :edit-config="{ trigger: 'click', mode: 'cell' }" :loading="loading" align="center">
                                <vxe-column title="物料名称" field="materialName"></vxe-column>
                                <vxe-column title="品牌型号" field="brand"></vxe-column>
                                <vxe-column title="规格参数" field="specificationParameters"></vxe-column>
                                <vxe-column title="购买数量" field="num"></vxe-column>
                                <vxe-column :edit-render="{ autofocus: '.vxe-input--inner' }" title="税率" field="taxRate"
                                    v-if="disabledFlag">
                                    <template #edit="{ row }">
                                        <vxe-input v-model="row.taxRate" type="text" @blur="dataBlur(row)" @keydown="(event: any) => {
                                            if (event.$event.keyCode == 13) {
                                                dataBlur(row)
                                            }
                                        }"></vxe-input>
                                    </template>
                                </vxe-column>

                                <vxe-column :edit-render="{ autofocus: '.vxe-input--inner' }" title="单价(含税)"
                                    field="unitPrice" v-if="disabledFlag">
                                    <template #edit="{ row }">
                                        <vxe-input v-model="row.unitPrice" type="text" @blur="dataBlur(row)" @keydown="(event: any) => {
                                            if (event.$event.keyCode == 13) {
                                                dataBlur(row)
                                            }
                                        }"></vxe-input>
                                    </template>
                                </vxe-column>
                                <vxe-column title="总价(含税)(元)" field="allPrice" v-if="disabledFlag">
                                    <template #default="{ row, rowIndex }">
                                        {{ row.unitPrice * row.num > 0 ? row.unitPrice * row.num : '' }}
                                    </template>
                                </vxe-column>
                                <vxe-column title="操作" field="operia" v-if="disabledFlag" fixed="right">
                                    <template #default="{ row, rowIndex }">
                                        <div class="flex-center" style="cursor: pointer;">
                                            <span style=" color: var(--5, #F53F3F);" @click="openConfirm(row)">重置</span>
                                        </div>
                                    </template>
                                </vxe-column>
                            </vxe-table>
                        </template>
                    </a-step>



                    <a-step>
                        <template #title>
                            <div class="evaluationOfBids-header">
                                <div class="evaluationOfBids-status">
                                    第一轮询价
                                </div>

                                <div class="evaluationOfBids-time">
                                    <!-- 2023/07/26 06:55 -->
                                </div>
                            </div>
                        </template>
                        <template #description>
                            <vxe-table border show-overflow :data="dataSource2" :column-config="{ resizable: true }"
                                :edit-config="{ trigger: 'click', mode: 'cell' }" align="center">
                                <vxe-column title="物料名称" field="materialName"></vxe-column>
                                <vxe-column title="品牌型号" field="brand"></vxe-column>
                                <vxe-column title="规格参数" field="specificationParameters"></vxe-column>
                                <vxe-column title="购买数量" field="num"></vxe-column>
                                <vxe-column :edit-render="{ autofocus: '.vxe-input--inner' }" title="税率" field="taxRate"
                                    v-if="disabledFlag">
                                    <template #edit="{ row }">
                                        <vxe-input v-model="row.taxRate" type="text" @blur="dataBlur(row)" @keydown="(event: any) => {
                                            if (event.$event.keyCode == 13) {
                                                dataBlur(row)
                                            }
                                        }"></vxe-input>
                                    </template>
                                </vxe-column>

                                <vxe-column :edit-render="{ autofocus: '.vxe-input--inner' }" title="单价(含税)"
                                    field="unitPrice" v-if="disabledFlag">
                                    <template #edit="{ row }">
                                        <vxe-input v-model="row.unitPrice" type="text" @blur="dataBlur(row)" @keydown="(event: any) => {
                                            if (event.$event.keyCode == 13) {
                                                dataBlur(row)
                                            }
                                        }"></vxe-input>
                                    </template>
                                </vxe-column>
                                <vxe-column title="总价(含税)(元)" field="allPrice" v-if="disabledFlag">
                                    <template #default="{ row, rowIndex }">
                                        {{ row.unitPrice * row.num > 0 ? row.unitPrice * row.num : '' }}
                                    </template>
                                </vxe-column>
                                <vxe-column title="操作" field="operia" v-if="disabledFlag" fixed="right">
                                    <template #default="{ row, rowIndex }">
                                        <div class="flex-center" style="cursor: pointer;">
                                            <span style=" color: var(--5, #F53F3F);" @click="openConfirm(row)">重置</span>
                                        </div>
                                    </template>
                                </vxe-column>
                            </vxe-table>
                        </template>
                    </a-step>
                </a-steps>

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
    <DelModal ref="delRef" :delElementTitle="'物料(重置税率/单价)'" :delElementValue="delElementValue" @delData="delData">
    </DelModal>
</template>

<script lang="ts" setup>
import UtilsTitle from '@/components/UtilsTitle/index.vue';
import { ref, onMounted, reactive } from 'vue'
import { executeApi } from '@/api/Execute'
import { executeListApi } from '@/api/ExecuteListDetails'
import { quotationApi } from '@/api/quotation'
import type { quotation, editQuotation } from '@/api/quotation'
import { getuserInfo } from '@/utils/UntilsHank';
import { message } from 'ant-design-vue';
import dayjs from 'dayjs';
interface props {
    propsid: string,
    current: number,
    baseData: any,
}
const props = defineProps<props>()
const disabledFlag = ref<boolean>(false)
const dataSource = ref<any>(
    [

    ]
)
const dataSource2 = ref<any>([])
const editableData: any = reactive({});
const loading = ref<boolean>(true)
let columns: any = [
    {
        title: '物料名称',//物料名称
        dataIndex: 'materialName',
        key: 'materialName',
        align: 'center'
    },
    {
        title: '品牌型号',//品牌
        dataIndex: 'brand',
        key: 'brand',
        align: 'center'
    },
    {
        title: '规格参数',//规格参数
        dataIndex: 'specificationParameters',
        key: 'specificationParameters',
        align: 'center'
    },
    {
        title: '数量',//数量
        dataIndex: 'num',
        key: 'num',
        align: 'center'
    },
    {
        title: '税率',//税率
        dataIndex: 'taxRate',
        key: 'taxRate',
        align: 'center'
    },
    {
        title: '单价(含税)',//单价
        dataIndex: 'unitPrice',
        key: 'unitPrice',
        align: 'center'
    },
    {
        title: '总价(含税)(元)',//单价
        dataIndex: 'allPrice',
        key: 'allPrice',
        align: 'center'
    },
    {
        title: '操作',//
        dataIndex: 'operate',
        key: 'operate',
        align: 'center'
    },
]
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
        case 'addExecuteList':
            addExecuteList()
            break;
        case 'editExecuteList':
            editExecuteList()
            break;
    }
}

//新增
const addexecuteListDialog = () => {
    modalDialog.value = true
    formState.value = addExecuteResponFileObj.formState
    formTile.value = addExecuteResponFileObj.formTile
    formEntry.value = addExecuteResponFileObj.formEntry
    formRules.value = addExecuteResponFileObj.formRules
    formApi.value = addExecuteResponFileObj.formApi
    addexecuteListReset()
}
const addexecuteListReset = () => {
    formState.value['brand'] = ''
    formState.value['materialName'] = ''
    formState.value['num'] = ''
    formState.value['specificationParameters'] = ''
}
const addExecuteResponFileObj = {
    formTile: '新增需求',
    formEntry: [
        { name: 'brand', type: 'a-input', label: '品牌型号', disabled: false },
        { name: 'materialName', type: 'a-input', label: '物料名称', disabled: false },
        { name: 'num', type: 'a-input', label: '购买数量', disabled: false },
        { name: 'specificationParameters', type: 'a-input', label: '规格参数', disabled: false },

    ],
    formState: {
        brand: '',//品牌
        materialName: '',//物料名称
        num: '',//数量
        specificationParameters: '',//规格参数
    },
    formRules: {
        brand: [{ required: true, message: '品牌型号不可为空' }],
        materialName: [{ required: true, message: '物料名称不可为空' }],
        num: [{ required: true, message: '购买数量不可为空' }],
        specificationParameters: [{ required: true, message: '规格参数不可为空' }],
    },
    formApi: 'addExecuteList'
}
const addExecuteList = () => {
    formRef.value.validate().then((res: any) => {
        if (res) {
            const data: any = {
                brand: formState.value['brand'],
                materialName: formState.value['materialName'],
                num: formState.value['num'],
                specificationParameters: formState.value['specificationParameters'],
                executeId: props.propsid
            }
            executeListApi.addExecuteList(data).then((res: any) => {
                if (res.success) {
                    modalDialog.value = false
                    getexecuteListList()
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
    delElementValue.value = record.materialName
    crudId.value = record.idd
}
const delData = () => {
    if (!crudId.value) {
        message.error('该物料没有税率和单价')
        return false
    }
    quotationApi.delQuotation(crudId.value).then((res: any) => {
        if (res.success) {
            delRef.value.close()
            getexecuteListList()
        }
    })
}

//编辑
const editexecuteListDialog = (record: any) => {
    modalDialog.value = true
    formState.value = editExecuteResponFileObj.formState
    formTile.value = editExecuteResponFileObj.formTile
    formEntry.value = editExecuteResponFileObj.formEntry
    formRules.value = editExecuteResponFileObj.formRules
    formApi.value = editExecuteResponFileObj.formApi
    editexecuteListReset(record)
}
const editexecuteListReset = (record: any) => {
    formState.value['unitPrice'] = record.unitPrice
    formState.value['taxRate'] = record.taxRate
    formState.value['detailsId'] = record.id
}
const editExecuteResponFileObj = {
    formTile: '新增税率/单价',
    formEntry: [
        { name: 'taxRate', type: 'a-input', label: '税率', disabled: false },
        { name: 'unitPrice', type: 'a-input', label: '价格', disabled: false },
    ],
    formState: {
        unitPrice: '',//价格
        taxRate: '',//税率
        id: ''
    },
    formRules: {
        unitPrice: [{ required: true, message: '价格不可为空' }],
        taxRate: [{ required: true, message: '税率不可为空' }],
    },
    formApi: 'editExecuteList'
}
const editExecuteList = () => {
    formRef.value.validate().then((res: any) => {
        if (res) {
            const data: any = {
                // companyId: USER.companyId,
                detailsId: formState.value.detailsId,
                // executeId: props.propsid,
                unitPrice: formState.value['unitPrice'],
                taxRate: formState.value['taxRate'],
            }
            quotationApi.addQuotation(data).then((res: any) => {
                if (res.success) {
                    modalDialog.value = false
                    getexecuteListList()
                }
            })
        }
    })
}

const dataBlur = (row: any) => {
    const data: any = {
        // companyId: USER.companyId,
        detailsId: row.id,
        // executeId: props.propsid,
        unitPrice: row['unitPrice'],
        taxRate: row['taxRate'],
    }
    quotationApi.addQuotation(data).then((res: any) => {
        if (res.success) {
            modalDialog.value = false
            getexecuteListList()
        }
    })
}

const getexecuteListList = async() => {
    loading.value = true
    loading.value = false
    if (!props.propsid) {
        setTimeout(() => {
            getexecuteListList()
        }, 500);
    } else {
        dataSource.value = props.baseData.listDetails
        const list: any = await getQuotationList(props.propsid)
        list.list.forEach((item: any) => {
            const temp_data = dataSource.value.filter((ele: any) => ele.id == item.detailsId)[0]
            temp_data['taxRate'] = item.taxRate
            temp_data['unitPrice'] = item.unitPrice
            temp_data['idd'] = item.id

        })
    }
}

const getQuotationList = (executeId: string) => {
    return new Promise((resolve) => {
        quotationApi.getQuotationList(executeId).then((res: any) => {
            if (res.success) {
                resolve({
                    list: res.obj
                })
            }
        })

    })
}

//respondToQuotes响应报价
const respondToQuotes = ref<string>('')
const getRespondToQuotes = () => {
    const today = dayjs();
    const formattedToday = today.format('YYYY-MM-DD HH:MM:ss');
    if (props.baseData?.endDate) {
        respondToQuotes.value = `${dateDiff(props.baseData.endDate, formattedToday) || 0}`
    } else {
        setTimeout(() => {
            getRespondToQuotes()
        }, 500);
    }
}
function dateDiff(date1: string, date2: string) {
    // 将日期字符串转换为Date对象
    const d1: any = new Date(date1);
    const d2: any = new Date(date2);
    // 计算两个日期之间的毫秒差值
    if (d2.getTime() < d1.getTime()) {
        let diffMilliseconds = Math.abs(d2 - d1);
        // 将毫秒差值转换为天数
        // const diffDays = Math.ceil(diffMilliseconds / (1000 * 60 * 60 * 24));
        const days = Math.floor(diffMilliseconds / (24 * 60 * 60 * 1000));
        diffMilliseconds %= 24 * 60 * 60 * 1000;
        const hours = Math.floor(diffMilliseconds / (60 * 60 * 1000));
        diffMilliseconds %= 60 * 60 * 1000;
        const minutes = Math.floor(diffMilliseconds / (60 * 1000));
        diffMilliseconds %= 60 * 1000;
        const seconds = Math.floor(diffMilliseconds / 1000);
        return `还剩余${days}天${hours}小时${minutes}分钟`;
    } else {
        return '已截止'
    }
}
const initialize =()=>{
    getexecuteListList()
    disabledFlag.value = props.current < 1 
    getRespondToQuotes()
}

defineExpose({initialize})
</script>

<style lang="less" scoped>
@import './index.less';

.basicInfo {
    // height: 100%;
    margin-top: 16px;
    overflow: hidden;

    .basic-item {
        // padding: 16px;
        overflow-y: auto;
        height: 100%;
        padding-top: 0px;
        background-color: #fff;

        .add-style {
            display: flex;
            width: 60px;
            height: 24px;
            justify-content: center;
            align-items: center;
            flex-shrink: 0;
            border-radius: 4px;
            border: 1px solid var(--unnamed, #2454CA);
            color: #2454CA;
        }
    }

    .table-style {
        margin-top: 24px;
        margin-left: 24px;
        margin-right: 24px;
        padding-bottom: 24px;
    }
}
</style>