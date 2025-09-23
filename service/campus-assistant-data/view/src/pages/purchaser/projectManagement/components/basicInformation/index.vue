<template>
    <div class="basicInfo">
        <div class="basic-item">
            <UtilsTitle :title="'基本信息'">
                <slot>
                    <a-button class="add-style" @click=saveData v-if="!disabledFlag">保存</a-button>
                </slot>
            </UtilsTitle>
            <div class="info-form">
                <a-form :model="basicForm" name="basic" ref="formRef" :label-col="{ style: { width: '80px' } }"
                    :rules="rules">
                    <a-row :gutter="24">
                        <a-col :span="8">
                            <a-form-item label="创建人员">
                                <a-input v-model:value="USERINFO.creatorName" disabled></a-input>
                            </a-form-item>
                        </a-col>

                        <a-col :span="8">
                            <a-form-item label="创建时间">
                                <a-input v-model:value="USERINFO.createDate" disabled></a-input>
                            </a-form-item>
                        </a-col>

                        <a-col :span="8">
                            <a-form-item label="行业分类">
                                <a-input v-model:value="USERINFO.classify" disabled></a-input>
                            </a-form-item>
                        </a-col>

                        <a-col :span="8">
                            <a-form-item label="采购类型">
                                <a-input v-model:value="USERINFO.type" disabled></a-input>
                            </a-form-item>
                        </a-col>


                        <!-- 公开项目 -->
                        <a-col :span="8">
                            <a-form-item label="公开项目" name="publicProjects">
                                <a-radio-group v-model:value="basicForm.publicProjects" :options="PUBLICPROJECTRADIO" :disabled="disabledFlag">
                                </a-radio-group>
                            </a-form-item>
                        </a-col>

                        <!-- 设置限价 -->
                        <a-col :span="8">
                            <a-form-item label="设置限价" name="setPriceLimit">
                                <a-radio-group v-model:value="basicForm.setPriceLimit" :options="PUBLICPROJECTRADIO" :disabled="disabledFlag">
                                </a-radio-group>
                            </a-form-item>
                        </a-col>

                        <!-- 采购限价 -->
                        <a-col :span="8">
                            <a-form-item label="采购限价" name="purchasePriceLimit">
                                <a-input v-model:value="basicForm.purchasePriceLimit"
                                    :placeholder="$t('placeholder.pleaseEnter')" :disabled="disabledFlag"></a-input>
                            </a-form-item>
                        </a-col>

                        <!-- 联系人员 -->
                        <a-col :span="8">
                            <a-form-item label="联系人员" name="contacts">
                                <a-input v-model:value="basicForm.contacts"
                                    :placeholder="$t('placeholder.pleaseEnter')" :disabled="disabledFlag"></a-input>
                            </a-form-item>
                        </a-col>

                        <!-- 联系电话 -->
                        <a-col :span="8">
                            <a-form-item label="联系电话" name="phone">
                                <a-input v-model:value="basicForm.phone"
                                    :placeholder="$t('placeholder.pleaseEnter')" :disabled="disabledFlag"></a-input>
                            </a-form-item>
                        </a-col>

                        <!-- 电子邮箱 -->
                        <a-col :span="8">
                            <a-form-item label="电子邮箱" name="email">
                                <a-input v-model:value="basicForm.email"
                                    :placeholder="$t('placeholder.pleaseEnter')" :disabled="disabledFlag"></a-input>
                            </a-form-item>
                        </a-col>

                        <!-- 起止时间 -->
                        <a-col :span="16">
                            <a-form-item label="起止时间" name="startAndEndTime">
                                <a-space direction="vertical" style="width: 100%">
                                    <a-range-picker v-model:value="basicForm.startAndEndTime" style="width: 100%" show-time
                                        :disabled-date="disabledDate" :disabled-time="disabledDateTime" :disabled="disabledFlag"/>
                                </a-space>
                            </a-form-item>
                        </a-col>

                        <!-- 收取保证金 -->
                        <a-col :span="24">
                            <a-form-item label="收取保证金">
                                <div class="deposit-style">
                                    <a-radio-group v-model:value="basicForm.collectMargin" :options="PUBLICPROJECTRADIO" :disabled="disabledFlag">
                                    </a-radio-group>
                                    <div class="deposit-msg" v-if="basicForm.collectMargin">
                                        <a-form :label-col="{ style: { width: '80px' } }" :rules="rules" ref="depositRef"
                                            :model="basicForm">
                                            <a-row :gutter="24">
                                                <a-col :span="10">
                                                    <a-form-item label="币种" name="currency">
                                                        <!-- <a-input v-model:value="basicForm.currency"
                                                            :placeholder="$t('placeholder.pleaseEnter')" :disabled="disabledFlag"></a-input> -->
                                                            <a-select v-model:value="basicForm.currency" style="width: 100%"
                                                            :placeholder="$t('placeholder.pleaseEnter')" :options="currencyOptions" :disabled="disabledFlag"></a-select>
                                                    </a-form-item>
                                                </a-col>
                                                <a-col :span="10">
                                                    <a-form-item label="  金额" name="amount">
                                                        <a-input v-model:value="basicForm.amount"
                                                            :placeholder="$t('placeholder.pleaseEnter')" :disabled="disabledFlag"></a-input>
                                                    </a-form-item>
                                                </a-col>
                                                <a-col :span="10">
                                                    <a-form-item label="收款账号" name="collectionAccount">
                                                        <a-input v-model:value="basicForm.collectionAccount"
                                                            :placeholder="$t('placeholder.pleaseEnter')" :disabled="disabledFlag"></a-input>
                                                    </a-form-item>
                                                </a-col>
                                                <a-col :span="10">
                                                    <a-form-item label="开户银行" name="bank">
                                                        <a-input v-model:value="basicForm.bank"
                                                            :placeholder="$t('placeholder.pleaseEnter')" :disabled="disabledFlag"></a-input>
                                                    </a-form-item>
                                                </a-col>
                                            </a-row>
                                        </a-form>

                                    </div>
                                </div>

                            </a-form-item>
                        </a-col>

                    </a-row>
                </a-form>
            </div>
        </div>
    </div>
</template>
<!-- manufacturers -->
<script setup lang="ts">
import UtilsTitle from '@/components/UtilsTitle/index.vue';
import { onMounted, ref } from 'vue'
import { executeApi } from '@/api/Execute'
import type { execute } from '@/api/Execute'
import dayjs, { Dayjs } from 'dayjs';
import { message } from 'ant-design-vue';
import {companyApi} from '@/api/company'
interface basicForm {
    [key: string]: any;
}
interface props {
    propsid: string,
    baseData: execute | undefined,
    current:number
}
const props = defineProps<props>()
const disabledFlag = ref<boolean>(false)
const USERINFO = ref<any>({
    creatorName: '',//创建人员：
    classify: '',//行业分类：
    createDate: '',//创建时间
    type: '',//采购类型：
})
const basicForm = ref<basicForm>({
    publicProjects: '',//公开项目
    setPriceLimit: '',//设置限价
    purchasePriceLimit: '',//采购限价

    contacts: '',//联系人员
    phone: '',//联系电话
    email: '',//电子邮箱

    startDate: '',//开始时间
    endDate: '',//结束时间
    startAndEndTime: [],//起止时间

    collectMargin: '',//是否收取保证金
    currency: '',//币种
    amount: '',//金额
    collectionAccount: '',//收款账号
    bank: '',//开户银行
})
//不可选中的日期
const disabledDate = (current: Dayjs) => {
    // Can not select days before today and today
    const now = dayjs();
    const startOfYesterday = now.subtract(0, 'day').startOf('day'); // 获取前一天的开始时刻时间戳
    return current && current <startOfYesterday;
};
const disabledDateTime = (current: Dayjs) => {
    const isgreaterThanNowDay = current > dayjs().endOf('day')//是否比今天大
    const currentTime = new Date(); // 获取当前时间
    const currentHour = currentTime.getHours() + 2; // 获取当前小时数
    let temp_disabledHoursList:number[] = []
    for(let i=0;i<currentHour;i++){
        temp_disabledHoursList.push(i)
    }
    return {
        disabledHours: () => isgreaterThanNowDay?[]:temp_disabledHoursList,
        disabledMinutes: () => [],
        disabledSeconds: () => [],
    };
};
const currencyOptions =ref<any>([
])
const rules = {
    publicProjects: [{
        required: true,
        message: `请输入` + '公开项目',
        trigger: 'blur',
    },],
    setPriceLimit: [{
        required: true,
        message: `请输入` + '设置限价',
        trigger: 'blur',
    },],
    purchasePriceLimit: [{
        required: true,
        message: `请输入` + '采购限价',
        trigger: 'blur',
    },],

    contacts: [{
        required: true,
        message: `请输入` + '联系人员',
        trigger: 'blur',
    },],
    phone: [{
        required: true,
        message: `请输入` + '联系电话',
        trigger: 'blur',
    },],
    email: [{
        required: true,
        message: `请输入` + '电子邮箱',
        trigger: 'blur',
    },],

    startAndEndTime: [{
        required: true,
        message: `请输入` + '起止时间',
        trigger: 'blur',
    },],


    collectMargin: [{
        required: true,
        message: `请输入` + '是否收取保证金',
        trigger: 'blur',
    },],
    currency: [{
        required: true,
        message: `请输入` + '币种',
        trigger: 'blur',
    },],
    amount: [{
        required: true,
        message: `请输入` + '金额',
        trigger: 'blur',
    },],
    collectionAccount: [{
        required: true,
        message: `请输入` + '收款账号',
        trigger: 'blur',
    },],
    bank: [{
        required: true,
        message: `请输入` + '开户银行',
        trigger: 'blur',
    },],
};

const PUBLICPROJECTRADIO = [
    { label: '是', value: true },
    { label: '否', value: false },
]
const saveData = () => {
    formRef.value.validate().then((res: any) => {
        console.log('basicForm.value.collectMargin', basicForm.value.collectMargin);
        if (res) {
            if (basicForm.value.collectMargin) {
                depositRef.value.validate().then((res: any) => {
                    depostSave()
                })
            } else {
                formSave()
            }

        }
    })
}
const formSave = () => {
    const data: any = {
        id: props.propsid,
        data: {
            publicProjects: basicForm.value.publicProjects || null,
            setPriceLimit: basicForm.value.setPriceLimit || null,
            purchasePriceLimit: basicForm.value.purchasePriceLimit || null,
            contacts: basicForm.value.contacts || null,
            phone: basicForm.value.phone || null,
            email: basicForm.value.email || null,
            startDate: dayjs(basicForm.value.startAndEndTime[0]).format('YYYY-MM-DD HH:mm:ss') || null,
            endDate: dayjs(basicForm.value.startAndEndTime[1]).format('YYYY-MM-DD HH:mm:ss') || null,
            collectMargin: basicForm.value.collectMargin || false,
            // currency: basicForm.value.currency || null,
            // amount: basicForm.value.amount || null,
            // collectionAccount: basicForm.value.collectionAccount || null,
            // bank: basicForm.value.bank || null,
        }
    }
    executeApi.putExecute(data).then((res: any) => {
        if (res.success) {
            message.success('保存成功')
        }
    })
}
const depostSave = () => {
    const data: any = {
        id: props.propsid,
        data: {
            publicProjects: basicForm.value.publicProjects || null,
            setPriceLimit: basicForm.value.setPriceLimit || null,
            purchasePriceLimit: basicForm.value.purchasePriceLimit || null,
            contacts: basicForm.value.contacts || null,
            phone: basicForm.value.phone || null,
            email: basicForm.value.email || null,
            startDate: dayjs(basicForm.value.startAndEndTime[0]).format('YYYY-MM-DD HH:mm:ss') || null,
            endDate: dayjs(basicForm.value.startAndEndTime[1]).format('YYYY-MM-DD HH:mm:ss') || null,
            collectMargin: basicForm.value.collectMargin || false,
            currency: basicForm.value.currency || null,
            amount: basicForm.value.amount || null,
            collectionAccount: basicForm.value.collectionAccount || null,
            bank: basicForm.value.bank || null,
        }
    }
    executeApi.putExecute(data).then((res: any) => {
        if (res.success) {
            message.success('保存成功')
        }
    })
}

const initialize = () => {
    USERINFO.value.createDate = props.baseData?.createDate
    USERINFO.value.classify= props.baseData?.classify
    USERINFO.value.type= props.baseData?.type
    USERINFO.value.creatorName= props.baseData?.creatorName
  
    disabledFlag.value = props.current >0
    if (props.baseData) {
        basicForm.value = props.baseData
        basicForm.value.publicProjects = props.baseData.publicProjects ? props.baseData.publicProjects : true
        basicForm.value.setPriceLimit = props.baseData.setPriceLimit ? props.baseData.setPriceLimit : true
        basicForm.value.purchasePriceLimit = props.baseData.purchasePriceLimit ? props.baseData.purchasePriceLimit : 100000
        basicForm.value.collectMargin = props.baseData.collectMargin ? props.baseData.collectMargin : false

        if (props.baseData.startDate && props.baseData.endDate) {
            // console.log('props.baseData.startDate', props.baseData.startDate, dayjs(props.baseData.startDate));
            basicForm.value.startAndEndTime = [
                dayjs(props.baseData.startDate, 'YYYY-MM-DD HH:mm:ss'),
                dayjs(props.baseData.endDate, 'YYYY-MM-DD HH:mm:ss')
            ]
        } else {
            // 获取当前时间
            const now = dayjs();
            // 将小时数增加1
            now.add(1, 'hour');
            // console.log('now.format()', dayjs(now.format('YYYY-MM-DD HH:mm:ss')));
            basicForm.value.startAndEndTime = [dayjs(now.format('YYYY-MM-DD HH:mm:ss')), '']
        }
    }

    //获取币种
    currencyOptions.value = []
    companyApi.getCurrencyList().then((res:any)=>{
        if(res.success){
            res.obj.forEach((item:any)=>{
                currencyOptions.value.push({
                    label:item,
                    value:item
                })
            })
        }
    })
}
const formRef = ref<any>(null)
const depositRef = ref<any>(null)

defineExpose({initialize})
</script>

<style scoped lang="less">
.basicInfo {
    .basic-item {
        // padding: 16px;
        height: 100%;
        padding-top: 0px;
        background-color: #fff;
    }
}

//基本信息
.info-form {
    padding: 12px 76px;

    .deposit-style {
        width: 100%;
        height: 168px;
        background-color: #F7F8F9;
        padding: 16px;

        .deposit-msg {
            padding: 16px;
        }
    }
}

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
</style>