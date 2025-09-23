<!-- 采购附件 -->
<template>
    <div class="basicInfo" id="purchaseAttachments">
        <div class="basic-item">
            <UtilsTitle :title="'采购附件'"></UtilsTitle>
            <div class="manufacturers">
                <div class="img-list">
                    <div v-for="(item, index) in executePurchaseFileList">
                        <div class="img-obj-father">
                            <div class="img-obj">
                                <div class="img-image">
                                    <img src="@/assets/images//file-img.svg">
                                </div>
                                <div class="img-text" :title="item.fileName + item.fileExtension">
                                    {{ item.fileName }}{{ item.fileExtension }}
                                </div>
                            </div>
                            <div class="logic-icon-list-father" >
                                <div :class="disabledFlag?'logic-icon-list2':'logic-icon-list'">
                                    <img src="@/assets/images/upload.svg" class="logic-icon-style"
                                        @click="downLoadFile(item)">
                                    <img src="@/assets/images/del.png" class="logic-icon-style" @click="openConfirm(item)" v-if="!disabledFlag">
                                </div>
                            </div>

                        </div>

                    </div>

                    <div class="img-obj2" v-if="!disabledFlag">
                        <a-upload v-model:file-list="fileList" list-type="picture-card" :before-upload="beforeUpload"
                            @preview="handlePreview(fileList)" style="{height:100%}">
                            <div>
                                <div class="svg-style">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 40 40"
                                        fill="none">
                                        <rect y="19" width="40" height="2" fill="#2454CA" />
                                        <rect x="19" y="40" width="40" height="2" transform="rotate(-90 19 40)"
                                            fill="#2454CA" />
                                    </svg>
                                </div>
                                <div class="upload-text">添加文件</div>
                            </div>
                        </a-upload>
                    </div>

                </div>
            </div>
        </div>
    </div>
    <!-- 删除弹框 -->
    <a-modal v-model:open="delDialog" title="删除确认" @ok="delOk" :destroyOnClose="true">
        <div class="del-dialog-style">
            <div class="del-style-svg">
                <ExclamationCircleOutlined :style="{ color: '#F99D1F' }"></ExclamationCircleOutlined>
            </div>
            <div class="del-style-body">
                <div class="del-style-body-top">
                    <!-- 删除提示 -->
                    {{ $t('placeholder.deleteThePrompt') }}
                </div>
                <div class="del-style-body-bottom">
                    <!-- 请确认删除该 -->
                    {{ $t('placeholder.pleaseConfirmTheDeletion') }} {{ delElementTitle }}:{{ delElementValue }}
                </div>
            </div>
        </div>
    </a-modal>
</template>

<script lang="ts" setup>
import UtilsTitle from '@/components/UtilsTitle/index.vue';
import { executePurchaseFileApi } from '@/api/ExecutePurchaseFile'
import type { purchaseFile } from '@/api/ExecutePurchaseFile'
import { onMounted, ref } from 'vue'
import { executeApi } from '@/api/Execute'
import {
    ExclamationCircleOutlined
} from "@ant-design/icons-vue";
//删除弹框相关
const delDialog = ref<boolean>(false)
const delApi = ref<string>('')//删除执行方法
const delRecord = ref<any>()//删除传值
const delElementTitle = ref<string>('')
const delElementValue = ref<string>('')
const delOk = () => {
    switch (delApi.value) {
        case 'delFile':
            delFile()
            break;
    }
}
interface props {
    propsid: string,
    current: number,
    baseData:any
}
const props = defineProps<props>()
const disabledFlag = ref<boolean>(false)
function getBase64(file: any) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
    });
}
const previewImage = ref<any>()
const fileList = ref<any>([])
const beforeUpload = async (file: any) => {
    console.log('file', file)

    previewImage.value = await getBase64(file)
    const formdata = new FormData()
    formdata.append('file', file)
    const data: purchaseFile = {
        executeId: props.propsid,
        data: formdata
    }
    executePurchaseFileApi.addExecutePurchaseFile(data).then((res: any) => {
        if (res.success) {
            getExecutePurchaseFileList()
        }
    })
    return
}
//删除
let crudId = ref<string>('')
const openConfirm = (record: any) => {
    delDialog.value = true
    delApi.value = 'delFile'
    delRecord.value = record
    delElementTitle.value = '文件'
    delElementValue.value = record.fileName + record.fileExtension
    crudId.value = record.id
}

const delFile = () => {
    executePurchaseFileApi.delExecutePurchaseFile(crudId.value).then((res: any) => {
        console.log('是否删除成功', res);
        if (res.success) {
            delDialog.value = false
            getExecutePurchaseFileList()
        }
    })
}
//下载
const downLoadFile = (item: any) => {
    console.log('item', item);
    executePurchaseFileApi.downLoadExecutePurchaseFile(item.id).then((res: any) => {
        let url = window.URL.createObjectURL(
            new Blob([res], {
                type:
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=utf-8"
            })
        );
        let link = document.createElement("a");
        link.style.display = "none";
        link.href = url;
        link.setAttribute("download", item.fileName + item.fileExtension);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link); //下载完成移除元素
        window.URL.revokeObjectURL(url); //释放掉blob对象
    })
}

const handlePreview = (fileObj: any) => {
    const _url = fileObj[0].url || null
    const img = new window.Image();
    img.src = _url || previewImage.value;
    const newWin: any = window.open('');
    newWin.document.write(img.outerHTML);
    newWin.document.close();
}

const activeKey = ref<number | string>('')
const setActiveKey = (number: number | string) => {
    activeKey.value = number
}

interface files {
    executeId: string;//关联id
    fileExtension: string;//类型
    fileName: string;//文件名
    id: string;
    orderIndex: string;//顺序
}
const executePurchaseFileList = ref<files[]>([])
const initialize =()=>{
    disabledFlag.value = props.current >0
    executePurchaseFileList.value = props.baseData.files
}
const getExecutePurchaseFileList = () => {
        executeApi.getExecuteInfo(props.propsid).then((res: any) => {
            if (res.success) {
                // console.log('这是采购附件这里', res);
                if (res.success) {
                    executePurchaseFileList.value = res.obj.files
                }
            }
        })
}

defineExpose({ initialize })
</script>

<style lang="less" scoped>
.basicInfo {
    // height: 100%;
    margin-top: 16px;

    .basic-item {
        // padding: 16px;
        height: 100%;
        padding-top: 0px;
        background-color: #fff;
    }

    .manufacturers {
        padding: 48px 36px;
        height: 220px;

        .img-list {
            display: flex;

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
                    /* 183.333% */
                }
            }

            .img-obj2 {
                width: 156px;
                margin-right: 24px;
                border-radius: 7px;
            }
        }
    }
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
    justify-content: space-between;
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
    justify-content: center;
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

:deep(.ant-upload) {
    background-color: #fff;
    width: 156px !important;
    height: 156px !important;
}

:deep(.ant-upload-list-item-container) {
    display: none !important;
}

:deep(.ant-upload-list-item-error) {
    background-color: #fafafa !important;
}

.svg-style {
    height: 80px;
    // margin-top: 20px;
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
}
</style>