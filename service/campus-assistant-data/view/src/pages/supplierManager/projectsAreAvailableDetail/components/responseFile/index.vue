<!-- 预邀厂商 -->
<template>
    <div class="basicInfo" id="responseFile">
        <div class="basic-item">
            <UtilsTitle :title="'响应文件'">
            </UtilsTitle>
            <div class="table-style">
                <div style="  display: flex;">
                    <div v-for="(item, index) in dataSource">
                        <div class="img-obj-father" v-if="item.fileId">
                            <div class="img-obj">
                                <div class="img-image">
                                    <img src="@/assets/images//file-img.svg">
                                </div>
                                <div class="img-text" :title="item.description">
                                    <span class="img-span">{{ item.fileName }}</span>
                                    <img src="@/assets/images/wenhao.svg">
                                </div>
                            </div>
                            <div class="logic-icon-list-father" @click="uploadNow(item.id)">
                                <div :class="'logic-icon-list2'">
                                    <div>
                                        <img src="@/assets/images/upload.svg" class="logic-icon-style"
                                            @click="downLoadFile(item)">
                                    </div>

                                    <div style="margin-top: -4px;">
                                        <a-upload name="file" :beforeUpload="beforeUpload" :maxCount="1"
                                            :disabled="props.current">
                                            <img src="@/assets/images/up-load.svg" class="logic-icon-style">
                                        </a-upload>
                                    </div>

                                    <div>
                                        <img src="@/assets/images/del.png" class="logic-icon-style"
                                            @click="openConfirm(item)">
                                    </div>
                                </div>
                            </div>
                        </div>



                        <div class="img-obj-father" v-else>
                            <div class="img-obj">
                                <div class="img-image">
                                    <img src="@/assets/images//no-file.svg">
                                </div>
                                <div class="img-text" :title="item.description">
                                    <span class="img-span">{{ item.fileName }}</span>
                                    <img src="@/assets/images/wenhao.svg">
                                </div>
                            </div>
                            <div class="logic-icon-list-father" @click="uploadNow(item.id)">
                                <a-upload name="file" :beforeUpload="beforeUpload" :maxCount="1" :disabled="props.current">
                                    <div class="logic-icon-list">
                                        <img src="@/assets/images/up-load.svg" class="logic-icon-style">
                                    </div>
                                </a-upload>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    </div>
    <!-- 删除弹框 -->
    <DelModal ref="delRef" :delElementTitle="'文件'" :delElementValue="delElementValue" @delData="delData"></DelModal>
</template>

<script lang="ts" setup>
import UtilsTitle from '@/components/UtilsTitle/index.vue';
import { onMounted, ref } from 'vue'
import { executeApi } from '@/api/Execute'
import { executeResponseFileApi } from '@/api/ExecuteResponseFile'
import type { executeResponseFile } from '@/api/ExecuteResponseFile'

import { responseFileApi } from '@/api/ResponseFile'
import type { responseFile } from '@/api/ResponseFile'
import { saveAs } from 'file-saver'
import DelModal from '@/components/DelModal/index.vue'
import { message } from 'ant-design-vue';
interface props {
    propsid: string,
    current: number,
    THESTATUS: boolean,
    baseData: any
}
const props = defineProps<props>()
const dataSource = ref<any>(
)
const loading = ref<boolean>(true)
//新增弹框相关

const fileId = ref<string>()
const uploadNow = (id: string) => {
    fileId.value = id
}
const beforeUpload = (file: any) => {
    const formData = new FormData()
    formData.append('file', file)
    const data = <responseFile>{
        data: formData,
        responseId: fileId.value
    }
    responseFileApi.summitResponseFile(data).then((res: any) => {
        if (res.success) {
            message.success('上传成功')
            getResponseFileList()
        }
    })
    return
}

const getExecuteResponseFileList = () => {
    loading.value = true
    executeApi.getExecuteInfo(props.propsid).then((res: any) => {
        if (res.success) {
            loading.value = false
            dataSource.value = res.obj.responseFileList
            getResponseFileList()
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
            getResponseFileList()
        }
    })
}

const downLoadFile = (item: any) => {
    responseFileApi.downLoadFile(item.fileId).then((res: any) => {
        saveAs(new Blob([res], { type: 'text/csv;charset=utf-8;' }), item.fileName + item.fileExtension)
    })
}
const getResponseFileList = () => {
    responseFileApi.getResponseFileList(props.propsid).then((res: any) => {
        if (res.success) {
            res.obj.forEach((item: any) => {
                const temp_data = dataSource.value.filter((ele: any) => { return ele.id == item.responseId })
                if (temp_data.length > 0) {
                    temp_data[0]['fileId'] = item.id
                    temp_data[0]['fileExtension'] = item.fileExtension
                }
            })
        }
    })
}

const initialize = () => {
    loading.value = false
    dataSource.value = props.baseData.responseFileList
    getResponseFileList()
}
defineExpose({ initialize })
</script>

<style lang="less" scoped>
.basicInfo {
    margin-top: 16px;

    .basic-item {
        // padding: 16px;
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

.img-obj2 {
    width: 156px;
    margin-right: 24px;
    border-radius: 7px;

    .svg-style {
        height: 80px;
        // margin-top: 20px;
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .upload-text {
        color: var(--unnamed, #2454CA);
        text-align: center;
        font-family: PingFang SC;
        font-size: 12px;
        font-style: normal;
        font-weight: 400;
        line-height: 22px;
        /* 183.333% */
        margin-top: 12px;
    }
}

.img-obj {
    width: 156px;
    height: 130px;
    // margin-right: 24px;
    cursor: pointer;

    .img-image {
        cursor: pointer;
        margin-left: 30px;
        height: 96px;
        width: 96px;
        // border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;

        img {
            height: 64px;
            width: 64px;
        }
    }

    .img-text {
        margin-top: 0px;
        color: var(--unnamed, #4E5969);
        text-align: center;
        font-family: PingFang SC;
        font-size: 12px;
        font-style: normal;
        font-weight: 400;
        line-height: 22px;
        /* 183.333% */
    }
}

:deep(.ant-upload) {
    // background-color: #fff;
    // width: 156px !important;
    // height: 156px !important;
}

:deep(.ant-upload-list-item-container) {
    display: none !important;
}

:deep(.ant-upload-list-item-error) {
    background-color: #fafafa !important;
}


.upload-text {
    color: var(--unnamed, #2454CA);
    text-align: center;
    font-family: PingFang SC;
    font-size: 12px;
    font-style: normal;
    font-weight: 400;
    line-height: 22px;
    /* 183.333% */
    margin-top: 12px;
}

//那些upload接口下面的一些逻辑样式  还有右上角的×
.logic-icon-list-father {
    display: none;
}

.logic-icon-list {
    margin-top: 4px;
    border-radius: 4px;
    border: 1px solid var(--unnamed, #F1F2F4);
    background: var(--unnamed, #FFF);
    box-shadow: 0px 4px 4px 0px rgba(0, 0, 0, 0.15);
    display: flex;
    justify-content: center;
    padding-left: 24px;
    padding-right: 24px;
    width: 156px;
    height: 24px;
    align-items: center;
    gap: 16px;
    flex-shrink: 0;

    img {
        cursor: pointer;
    }

    .logic-icon-style {
        height: 16px;
    }
}

.logic-icon-list2 {
    img {
        cursor: pointer;
    }

    margin-top: 4px;
    border-radius: 4px;
    border: 1px solid var(--unnamed, #F1F2F4);
    background: var(--unnamed, #FFF);
    box-shadow: 0px 4px 4px 0px rgba(0, 0, 0, 0.15);
    display: flex;
    justify-content: space-around;
    padding-left: 24px;
    padding-right: 24px;
    width: 156px;
    height: 24px;
    align-items: center;
    gap: 16px;
    flex-shrink: 0;

    .logic-icon-style {
        height: 16px;
    }
}

.del-style {
    float: right;
    margin-top: -5px;
    margin-right: -5px;
}

.svg-style {
    height: 80px;
    // margin-top: 20px;
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
}

.img-obj-father {
    height: 150px;
}

.img-obj-father:hover {
    .img-obj {
        border-radius: 8px;
        border: 1px solid var(--unnamed, #F1F2F4);
        background: var(--unnamed, #F7F8F9);
    }

    .logic-icon-list-father {
        display: block !important;
    }
}

.active-style {
    border-radius: 8px;
    border: 1px solid var(--unnamed, #F1F2F4);
    background: var(--unnamed, #F7F8F9);
}

.img-obj {
    width: 156px;
    height: 130px;
    margin-right: 24px;
    cursor: pointer;

    .img-image {
        cursor: pointer;
        margin-left: 30px;
        height: 96px;
        width: 96px;
        // border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;

        img {
            height: 64px;
            width: 64px;
        }
    }

    .img-text {
        margin-top: 0px;
        color: var(--unnamed, #4E5969);
        text-align: center;
        font-family: PingFang SC;
        font-size: 12px;
        font-style: normal;
        font-weight: 400;
        line-height: 22px;
        display: flex;
        justify-content: center;
        align-items: center;

        .img-span {
            font-size: 14px;
            margin-right: 4px;
        }

        img {
            height: 13px;
        }

        /* 183.333% */
    }
}

:deep(.ant-upload) {
    border-radius: 0;
    border: 0px dashed #2454CA;
}
</style>