<!-- 预邀厂商 -->
<template>
    <div class="basicInfo" id="tenderRules">
        <div class="basic-item">
            <UtilsTitle :title="'采购附件'"></UtilsTitle>
            <div class="manufacturers">
                <div class="img-list">
                    <div v-for="(item, index) in executePurchaseFileList">
                        <div class="img-obj-father">
                            <div class="img-obj">
                                <!-- <div class="del-style" v-if="activeKey == index">
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 10 10"
                                    fill="none">
                                    <path fill-rule="evenodd" clip-rule="evenodd"
                                        d="M5 10C7.76142 10 10 7.76147 10 5.00005C10 2.23862 7.76142 4.56248e-05 5 4.56248e-05C2.23858 4.56248e-05 8.6849e-08 2.23862 8.6849e-08 5.00005C8.6849e-08 7.76147 2.23858 10 5 10ZM6.64261 3.10473C6.50304 2.96516 6.27676 2.96516 6.13719 3.10473L5 4.24191L3.86281 3.10472C3.72324 2.96515 3.49696 2.96515 3.35739 3.10472L3.10468 3.35743C2.96511 3.497 2.96512 3.72328 3.10468 3.86285L4.24188 5.00004L3.10468 6.13724C2.96511 6.27681 2.96511 6.50309 3.10468 6.64266L3.35739 6.89537C3.49695 7.03494 3.72324 7.03494 3.8628 6.89537L5 5.75817L6.1372 6.89536C6.27676 7.03493 6.50305 7.03493 6.64262 6.89536L6.89532 6.64265C7.03489 6.50309 7.03489 6.2768 6.89532 6.13723L5.75813 5.00004L6.89532 3.86286C7.03489 3.72329 7.03489 3.49701 6.89532 3.35744L6.64261 3.10473Z"
                                        fill="#C9CDD4" />
                                </svg>
                            </div> -->

                                <div class="img-image">
                                    <img src="@/assets/images//file-img.svg">
                                </div>
                                <div class="img-text" :title="item.fileName + item.fileExtension">
                                    <span class="img-span text-omit">{{ item.fileName }}</span>
                                    <!-- <img src="@/assets/images/wenhao.svg"> -->
                                </div>
                            </div>
                            <div class="logic-icon-list-father" v-if="!disabledFlag">
                                <div class="logic-icon-list">
                                    <img src="@/assets/images/upload.svg" class="logic-icon-style"
                                        @click="downLoadFile(item)">
                                    <!-- <img src="@/assets/images/del.png" class="logic-icon-style" @click="openConfirm(item)"> -->
                                </div>
                            </div>

                        </div>

                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
import UtilsTitle from '@/components/UtilsTitle/index.vue';
import { executePurchaseFileApi } from '@/api/ExecutePurchaseFile'
import type { purchaseFile } from '@/api/ExecutePurchaseFile'
import { onMounted, ref } from 'vue'
import { executeApi } from '@/api/Execute'

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

//下载
const downLoadFile = (item: any) => {
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


interface files {
    executeId: string;//关联id
    fileExtension: string;//类型
    fileName: string;//文件名
    id: string;
    orderIndex: string;//顺序
}
const executePurchaseFileList = ref<files[]>([
])
const getExecutePurchaseFileList = () => {
        executeApi.getExecuteInfo(props.propsid).then((res: any) => {
            if (res.success) {
                if (res.success) {
                    executePurchaseFileList.value = res.obj.files
                }
            }
        })
}
const initialize = ()=>{
    executePurchaseFileList.value = props.baseData.files
    disabledFlag.value = props.current > 0
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
        padding: 48px 40px;
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

.svg-style {
    height: 80px;
    // margin-top: 20px;
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
}</style>