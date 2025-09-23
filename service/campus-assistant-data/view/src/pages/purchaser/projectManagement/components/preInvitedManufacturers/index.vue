<!-- 预邀厂商 -->
<template>
    <div class="basicInfo" id="preInvitedManufacturers">
        <div class="basic-item">
            <UtilsTitle :title="'预邀厂商'">
            </UtilsTitle>
            <div class="manufacturers">
                <div class="img-list">
                    <div class="img-obj" v-for="(item, index) in companyNameList"
                        :class="activeKey == index ? 'active-style' : ''">
                        <div class="del-style" v-if="!disabledFlag">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 10 10" fill="none"
                                @click="delConpany(item)">
                                <path fill-rule="evenodd" clip-rule="evenodd"
                                    d="M5 10C7.76142 10 10 7.76147 10 5.00005C10 2.23862 7.76142 4.56248e-05 5 4.56248e-05C2.23858 4.56248e-05 8.6849e-08 2.23862 8.6849e-08 5.00005C8.6849e-08 7.76147 2.23858 10 5 10ZM6.64261 3.10473C6.50304 2.96516 6.27676 2.96516 6.13719 3.10473L5 4.24191L3.86281 3.10472C3.72324 2.96515 3.49696 2.96515 3.35739 3.10472L3.10468 3.35743C2.96511 3.497 2.96512 3.72328 3.10468 3.86285L4.24188 5.00004L3.10468 6.13724C2.96511 6.27681 2.96511 6.50309 3.10468 6.64266L3.35739 6.89537C3.49695 7.03494 3.72324 7.03494 3.8628 6.89537L5 5.75817L6.1372 6.89536C6.27676 7.03493 6.50305 7.03493 6.64262 6.89536L6.89532 6.64265C7.03489 6.50309 7.03489 6.2768 6.89532 6.13723L5.75813 5.00004L6.89532 3.86286C7.03489 3.72329 7.03489 3.49701 6.89532 3.35744L6.64261 3.10473Z"
                                    fill="#C9CDD4" />
                            </svg>
                        </div>
                        <div class="img-image">
                            <img src="@/assets/images//manufacturers.svg">
                        </div>

                        <div class="img-text text-omit" :title="item.companyName">
                            {{ item.companyName }}
                        </div>
                    </div>

                    <div class="img-obj" v-if="!disabledFlag">
                        <div class="picture-card" @click="openDialog">
                            <div class="svg-style">
                                <svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 40 40"
                                    fill="none">
                                    <rect y="19" width="40" height="2" fill="#2454CA" />
                                    <rect x="19" y="40" width="40" height="2" transform="rotate(-90 19 40)"
                                        fill="#2454CA" />
                                </svg>
                            </div>
                            <div class="upload-text">邀请厂商</div>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    </div>
    <a-modal v-model:open="modalDialog" :title="'预邀厂商'" @ok="formOk" :destroyOnClose="true">
        <a-form :model="formState" ref="formRef" :rules="formRules">
            <a-form-item label="厂商名" name="companyId">
                <a-select v-model:value="formState.companyId" style="width: 100%"
                    :placeholder="$t('placeholder.pleaseSelect')" :options="companyList" @select="selectChange"></a-select>
            </a-form-item>
        </a-form>
    </a-modal>
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
                    {{ $t('placeholder.pleaseConfirmTheDeletion') }}公司:{{ delItem.companyName }}
                </div>
            </div>
        </div>
    </a-modal>
</template>

<script lang="ts" setup>
import UtilsTitle from '@/components/UtilsTitle/index.vue';
import { onMounted, ref } from 'vue'
import { companyApi } from '@/api/company'
import { executeApi } from '@/api/Execute'
import { excutePartake } from '@/api/ExecutePartake'
import type { partake } from '@/api/ExecutePartake'
import { message } from 'ant-design-vue';
import {
    ExclamationCircleOutlined
} from "@ant-design/icons-vue";
import { joinPurchaserApi } from '@/api/JoinPurchaser'
interface props {
    propsid: string,
    current: number,
    baseData: any
}
const props = defineProps<props>()
const disabledFlag = ref<boolean>(false)
const activeKey = ref<number | string>('')
const setActiveKey = (number: number | string) => {
    activeKey.value = number
}
const modalDialog = ref<boolean>(false)
const formRef = ref<any>()
const formState = ref<any>({
    companyId: '',
    companyName: ''
})
const formRules = {
    companyId: [{ required: true, message: '厂商名不可为空' }],
}
const openDialog = () => {
    modalDialog.value = true
}
const companyNameList = ref<any>([])
const companyList = ref<any>()
const formOk = () => {
    formRef.value.validate().then((res: any) => {
        const data = <partake>{
            companyId: formState.value.companyId,
            executeId: THEID.value,
            partake: true
        }
        excutePartake.addExecuteList(data).then((res: any) => {
            if (res.success) {
                message.success('新增成功')
                modalDialog.value = false
                getCompanyNameList()
            }
        })
        // console.log('companyNameList.value', companyNameList.value);
        // if (!companyNameList.value) {
        //     companyNameList.value = []
        // }
        // companyNameList.value.push(JSON.parse(JSON.stringify(formState.value)))
        // saveData().then((res: any) => {
        //     if (res.success) {
        //         message.success('保存成功')
        //         companyList.value.forEach((item: any) => {
        //             if (item.value === formState.value.companyId) {
        //                 item.disabled = true
        //             }
        //         })
        //         formState.value.companyId = ''
        //         modalDialog.value = false
        //     }
        // })
    })
}
const selectChange = (value: any, options: any) => {
    console.log(value, options);
    formState.value.companyName = options.label
}
const getCompanyList = () => {
    const data = {
        current: 1,
        size: 1000,
        status: 1
    }
    joinPurchaserApi.getJoinPurchaserPage(data).then((res: any) => {
        if (res.success) {
            companyList.value = []
            res.obj.records.forEach((item: any) => {
                const obj = {
                    label: item.supplierName,
                    value: item.supplierId,
                    disabled: false
                }
                companyList.value.push(obj)
            })
        }
    })
}
//保存
// const saveData = () => {
//     return new Promise((resolve) => {
//         let temp_companyIds = ''
//         companyNameList.value.forEach((item: any) => {
//             temp_companyIds += item.companyId + ','
//         })
//         temp_companyIds = temp_companyIds.slice(0, -1);
//         const data: any = {
//             id: props.propsid,
//             companyIds: temp_companyIds
//         }
//         executeApi.putinvitedCompany(data).then((res: any) => {
//             if (res.success) {
//                 resolve({ success: true })
//             }
//         })
//     })
// }
const delDialog = ref<boolean>(false)
const delItem = ref<any>()
const delConpany = (item: any) => {
    console.log('item', item)

    delDialog.value = true
    delItem.value = item
}
const delOk = () => {
    const item: any = delItem.value
    excutePartake.delExecuteList(item.id).then((res: any) => {
        if (res.success) {
            message.success('删除成功')
            getCompanyNameList()
            delDialog.value = false
            companyList.value.forEach((ele: any) => {
                if (ele.value == item.companyId) {
                    ele.disabled = false
                }
            })
        }
    })
}
const THEID = ref<string>('')
const initialize = () => {
    getCompanyList()
    disabledFlag.value = props.current > 0
    THEID.value = props.baseData.id
    companyNameList.value = props.baseData.companyList
    setTimeout(() => {
        companyNameList.value.forEach((item: any) => {
            companyList.value.forEach((ele: any) => {
                if (ele.value == item.companyId) {
                    ele.disabled = true
                }
            })
        })
    }, 1000);
}
const getCompanyNameList = () => {
    executeApi.getExecuteInfo(props.propsid).then((res: any) => {
        if (res.success) {
            companyNameList.value = res.obj.companyList
            setTimeout(() => {
                companyNameList.value.forEach((item: any) => {
                    companyList.value.forEach((ele: any) => {
                        if (ele.value == item.companyId) {
                            ele.disabled = true
                        }
                    })
                })
            }, 1000);
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
            height: 156px;

            .img-obj:hover {
                border-radius: 8px;
                border: 1px solid var(--unnamed, #F1F2F4);
                background: var(--unnamed, #F7F8F9);

                .del-style {
                    display: block;
                }
            }

            // .active-style {
            //     border-radius: 8px;
            //     border: 1px solid var(--unnamed, #F1F2F4);
            //     background: var(--unnamed, #F7F8F9);
            // }

            .img-obj {
                width: 156px;
                margin-right: 24px;
                cursor: pointer;

                .del-style {
                    display: none;
                    float: right;
                    margin-top: -5px;
                    margin-right: -5px;
                }

                .img-image {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    margin: 12px;
                    border-radius: 8px;
                    border: 1px solid var(--unnamed, #F1F2F4);
                    background: var(--unnamed, #F7F8F9);
                    background-color: #D6E2FF;
                    margin-left: 30px;
                    height: 96px;
                    width: 96px;
                    border-radius: 50%;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }

                .img-text {
                    padding-left: 8px;
                    padding-right: 8px;
                    margin-top: 20px;
                    color: var(--unnamed, #4E5969);
                    text-align: center;
                    font-family: PingFang SC;
                    font-size: 8px;
                    font-style: normal;
                    font-weight: 400;
                    line-height: 22px;
                    /* 183.333% */
                    text-overflow: wrap;
                    /* 超出部分自动换行 */
                }
            }


        }
    }
}

.picture-card {
    cursor: pointer;
    width: 156px;
    height: 156px;
    flex-shrink: 0;
    border-radius: 7px;
    border: 1px dashed #2454CA;

    .svg-style {
        height: 80px;
        margin-top: 20px;
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
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
    margin-top: 18px;
}

:deep(.ant-upload) {
    background-color: #fff;
    width: 124px !important;
    height: 124px !important;
}
</style>