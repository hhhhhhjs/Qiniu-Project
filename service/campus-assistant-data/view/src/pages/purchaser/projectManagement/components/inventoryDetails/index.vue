<!-- 预邀厂商 -->
<template>
    <div class="basicInfo" id="inventoryDetails">
        <div class="basic-item">
            <UtilsTitle :title="'清单明细'">
                <a-button class="add-style" @click="addexecuteListDialog" v-if="!disabledFlag">新增</a-button>
            </UtilsTitle>
            <div class="table-style">
                <a-table :dataSource="dataSource" :columns="columns" :pagination="false" :size="'large'" :loading="loading">
                    <template #bodyCell="{ column, text, record, index }">
                        <template v-if="column.dataIndex === 'operate'">
                            <div class="operate-style" v-if="!disabledFlag">
                                <div class="detail-style" @click="editexecuteListDialog(record)">修改</div>
                                <div class="del-style" @click="openConfirm(record)">
                                    删除
                                </div>
                            </div>
                        </template>

                    </template>
                </a-table>
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
    <DelModal ref="delRef" :delElementTitle="'清单'" :delElementValue="delElementValue" @delData="delData"></DelModal>
</template>

<script lang="ts" setup>
import UtilsTitle from '@/components/UtilsTitle/index.vue';
import { ref, onMounted } from 'vue'
import { executeApi } from '@/api/Execute'
import { executeListApi } from '@/api/ExecuteListDetails'
interface props {
    propsid: string,
    current: number,
    baseData: any
}
const props = defineProps<props>()
const disabledFlag = ref<boolean>(false)
const dataSource = ref<any>(
    [

    ]
)
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
        title: '购买数量',//数量
        dataIndex: 'num',
        key: 'num',
        align: 'center'
    },
    {
        title: '操作',
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
    crudId.value = record.id
}
const delData = () => {
    executeListApi.delExecuteList(crudId.value).then((res: any) => {
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
    formState.value['brand'] = record.brand
    formState.value['materialName'] = record.materialName
    formState.value['num'] = record.num
    formState.value['specificationParameters'] = record.specificationParameters
    formState.value['id'] = record.id
}
const editExecuteResponFileObj = {
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
        id: ''
    },
    formRules: {
        brand: [{ required: true, message: '品牌型号不可为空' }],
        materialName: [{ required: true, message: '物料名称不可为空' }],
        num: [{ required: true, message: '购买数量不可为空' }],
        specificationParameters: [{ required: true, message: '规格参数不可为空' }],
    },
    formApi: 'editExecuteList'
}
const editExecuteList = () => {
    formRef.value.validate().then((res: any) => {
        if (res) {
            const data: any = {
                id: formState.value.id,
                data: {
                    brand: formState.value['brand'],
                    materialName: formState.value['materialName'],
                    num: formState.value['num'],
                    specificationParameters: formState.value['specificationParameters'],
                    executeId: props.propsid
                }
            }
            executeListApi.editExecuteList(data).then((res: any) => {
                if (res.success) {
                    modalDialog.value = false
                    getexecuteListList()
                }
            })
        }
    })
}


const getexecuteListList = () => {
    loading.value = true
    executeApi.getExecuteInfo(props.propsid).then((res: any) => {
        if (res.success) {
            loading.value = false
            dataSource.value = res.obj.listDetails
        }
    })
}
const initialize = () => {
    disabledFlag.value = props.current > 0
    loading.value = false
    dataSource.value = props.baseData.listDetails
}
defineExpose({initialize})
</script>

<style lang="less" scoped>
.basicInfo {
    // height: 100%;
    margin-top: 16px;

    .basic-item {
        // padding: 16px;
        padding-bottom: 24px;
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
    }
}
</style>