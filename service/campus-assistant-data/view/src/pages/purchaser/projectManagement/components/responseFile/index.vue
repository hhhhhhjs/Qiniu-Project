<!-- 预邀厂商 -->
<template>
    <div class="basicInfo" id="responseFile">
        <div class="basic-item">
            <UtilsTitle :title="'响应文件'">
                <a-button class="add-style" @click="addexecuteResponseFileDialog" v-if="!disabledFlag">新增</a-button>
            </UtilsTitle>
            <div class="table-style">
                <a-table :dataSource="dataSource" :columns="columns" :pagination="false" :size="'large'" :loading="loading">
                    <template #bodyCell="{ column, text, record, index }">
                        <template v-if="column.dataIndex === 'operate'">
                            <div class="operate-style" v-if="!disabledFlag">
                                <div class="detail-style" @click="editexecuteResponseFileDialog(record)">修改</div>
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

    <!-- 删除弹框 -->
    <DelModal ref="delRef" :delElementTitle="'文件'" :delElementValue="delElementValue" @delData="delData"></DelModal>
</template>

<script lang="ts" setup>
import UtilsTitle from '@/components/UtilsTitle/index.vue';
import { onMounted, ref } from 'vue'
import { executeApi } from '@/api/Execute'
import { executeResponseFileApi } from '@/api/ExecuteResponseFile'
import type { executeResponseFile, updataexecuteResponseFile } from '@/api/ExecuteResponseFile'
import DelModal from '@/components/DelModal/index.vue'
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
        title: '文件名称',//文件名称
        dataIndex: 'fileName',
        key: 'fileName',
        align: 'center'
    },
    {
        title: '文件描述',//文件描述
        dataIndex: 'description',
        key: 'description',
        align: 'center'
    },
    {
        title: '操作',//操作
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
        case 'addExecuteRespon':
            addExecuteRespon()
            break;
        case 'editExecuteRespon':
            editExecuteRespon()
            break;
    }
}


const getExecuteResponseFileList = () => {
    loading.value = true
    executeApi.getExecuteInfo(props.propsid).then((res: any) => {
        if (res.success) {
            loading.value = false
            dataSource.value = res.obj.responseFileList
        }
    })
}

//新增
const addexecuteResponseFileDialog = () => {
    modalDialog.value = true
    formState.value = addExecuteResponFileObj.formState
    formTile.value = addExecuteResponFileObj.formTile
    formEntry.value = addExecuteResponFileObj.formEntry
    formRules.value = addExecuteResponFileObj.formRules
    formApi.value = addExecuteResponFileObj.formApi
    addexecuteResponseFileReset()
}
const addexecuteResponseFileReset = () => {
    formState.value['description'] = ''
    formState.value['fileName'] = ''
}
const addExecuteResponFileObj = {
    formTile: '新增需求',
    formEntry: [
        { name: 'description', type: 'a-input', label: '文件描述', disabled: false },
        { name: 'fileName', type: 'a-input', label: '文件名称', disabled: false },
    ],
    formState: {
        description: '',//文件描述
        fileName: ''//文件名称
    },
    formRules: {
        description: [{ required: true, message: '文件描述不可为空' }],
        fileName: [{ required: true, message: '文件名称不可为空' }],
    },
    formApi: 'addExecuteRespon'
}
const addExecuteRespon = () => {
    formRef.value.validate().then((res: any) => {
        if (res) {
            const data: any = {
                description: formState.value['description'],
                fileName: formState.value['fileName'],
                executeId: props.propsid
            }
            executeResponseFileApi.addexecuteResponseFile(data).then((res: any) => {
                if (res.success) {
                    modalDialog.value = false
                    getExecuteResponseFileList()
                }
            })
        }
    })
}
//删除
let crudId = ref<string>('')
const delElementValue = ref<string>('')
const delRef = ref<any>()
const openConfirm = (record: executeResponseFile) => {
    delRef.value.open()
    delElementValue.value = record.fileName
    crudId.value = record.id
}
const delData = () => {
    executeResponseFileApi.delexecuteResponseFile(crudId.value).then((res: any) => {
        if (res.success) {
            delRef.value.close()
            getExecuteResponseFileList()
        }
    })
}

//编辑
const editexecuteResponseFileDialog = (record: executeResponseFile) => {
    modalDialog.value = true
    formState.value = editExecuteResponFileObj.formState
    formTile.value = editExecuteResponFileObj.formTile
    formEntry.value = editExecuteResponFileObj.formEntry
    formRules.value = editExecuteResponFileObj.formRules
    formApi.value = editExecuteResponFileObj.formApi
    editexecuteResponseFileReset(record)
}
const editexecuteResponseFileReset = (record: executeResponseFile) => {
    formState.value['description'] = record.description
    formState.value['fileName'] = record.fileName
    formState.value['id'] = record.id
}
const editExecuteResponFileObj = {
    formTile: '新增需求',
    formEntry: [
        { name: 'description', type: 'a-input', label: '文件描述', disabled: false },
        { name: 'fileName', type: 'a-input', label: '文件名称', disabled: false },
    ],
    formState: {
        description: '',//文件描述
        fileName: '',//文件名称
        id: ''
    },
    formRules: {
        description: [{ required: true, message: '文件描述不可为空' }],
        fileName: [{ required: true, message: '文件名称不可为空' }],
    },
    formApi: 'editExecuteRespon'
}
const editExecuteRespon = () => {
    formRef.value.validate().then((res: any) => {
        if (res) {
            const data: any = {
                id: formState.value.id,
                data: {
                    description: formState.value['description'],
                    fileName: formState.value['fileName'],
                    executeId: props.propsid
                }
            }
            executeResponseFileApi.editexecuteResponseFile(data).then((res: any) => {
                if (res.success) {
                    modalDialog.value = false
                    getExecuteResponseFileList()
                }
            })
        }
    })
}
const initialize = () => {
    disabledFlag.value = props.current > 0
    loading.value = false
    dataSource.value = props.baseData.responseFileList
}
defineExpose({ initialize })
</script>

<style lang="less" scoped>
.basicInfo {
    // height: 100%;
    margin-top: 16px;

    .basic-item {
        // padding: 16px;
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