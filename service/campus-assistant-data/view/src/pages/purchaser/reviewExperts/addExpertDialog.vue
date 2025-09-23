<!--
 * @Description: 弹窗
-->
<template>
    <a-modal :title="type == 'add'?'新增':'编辑'" v-model:open="visible" width="450px"
        :destroyOnClose="true" @ok="handleOk"  @cancel="handleCancel">
        <template #footer>
            <a-button key="back" @click="handleCancel">取消</a-button>
            <a-button key="submit" type="primary" :loading="loading" @click="handleOk">确认</a-button>
        </template>
        <!-- :label-col="{ span: 8 }" -->
        <a-form :model="formData" ref="formRef" :rules="formRules">
            <a-form-item label="真实姓名" name="name">
                <a-input class="input"
                    :placeholder="$t('placeholder.pleaseEnter')"
                    v-model:value="formData.name">
                </a-input>
            </a-form-item>
            
            <a-form-item label="身份证号" name="idNumber">
                <a-input class="input"
                    :placeholder="$t('placeholder.pleaseEnter')"
                    v-model:value="formData.idNumber">
                </a-input>
            </a-form-item>

            <a-form-item label="手机号码" name="phone">
                <a-input class="input"
                    :placeholder="$t('placeholder.pleaseEnter')"
                    v-model:value="formData.phone">
                </a-input>
            </a-form-item>
            
            <a-form-item label="所属单位" name="companyId">
                <!-- <a-input class="input"
                    :placeholder="$t('placeholder.pleaseEnter')"
                    v-model:value="formData.companyId">
                </a-input> -->
                <a-tree-select
                    v-model:value="formData.companyId"
                    style="width: 100%"
                    :dropdown-style="{ maxHeight: '400px', overflow: 'auto' }"
                    :placeholder="$t('placeholder.pleaseEnter')"
                    tree-default-expand-all
                    :tree-data="companyTree"
                    :field-names="{ label: 'companyName', value: 'id', children: 'children' }"
                ></a-tree-select>
            </a-form-item>

            <a-form-item label="职称等级" name="grade">
                <a-select class="input"
                    :placeholder="$t('placeholder.pleaseEnter')"
                    v-model:value="formData.grade">
                    <a-select-option :value="1">正高级</a-select-option>
                    <a-select-option :value="2">副高级</a-select-option>
                    <a-select-option :value="3">中级</a-select-option>
                    <a-select-option :value="4">初级</a-select-option>
                </a-select>
            </a-form-item>

            <a-form-item label="专业名称" name="major">
                <a-input class="input"
                    :placeholder="$t('placeholder.pleaseEnter')"
                    v-model:value="formData.major">
                </a-input>
            </a-form-item>

            <!-- <a-form-item label="电子邮箱" name="email">
                <a-input class="input"
                    :placeholder="$t('placeholder.pleaseEnter')"
                    v-model:value="formData.email">
                </a-input>
            </a-form-item> -->
        </a-form>
    </a-modal>
</template>

<script setup lang="ts">
import i18n from "@/i18n";
import { onMounted, reactive, ref, toRefs, watch } from "vue";
import type { IReviewExperts } from "@/api/ReviewExperts/index";

const loading = ref(false)
const props = defineProps<{
    visible: boolean;
    type: string;
    formData: IReviewExperts;
    companyTree: any;
}>();
const { visible, type, formData, companyTree } = toRefs(props);
const emits = defineEmits(["handleOk", "handleCancel"]);

const formRef = ref();
const checkPhone = (rule:any, value:any) => {
    if (!value) {
        return Promise.reject('手机号码不能为空');
    } else {
        const reg = /^1[3|4|5|7|8][0-9]\d{8}$/
        if (reg.test(value)) {
            return Promise.resolve();
        } else {
            return Promise.reject('请输入正确的手机号码');
        }
    }
};
const formRules = {
    //所属企业id
    companyId: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
    //等级（排序字段）
    grade: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
    //身份证号
    idNumber: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
    //所属专业
    major: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
    //真实姓名
    name: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
    //手机号码
    phone: [
        { required: true, validator: checkPhone, trigger: "blur" },
    ],
    //职称等级 正高级、副高级、中级以及初级四个级别
    // professionalQualifications: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],

    // email: [
    //     { required: true, message: '电子邮箱不能为空', trigger: "blur" },
    //     { type: 'email', message: '请输入正确的电子邮箱', trigger: "change" },
    // ],
};

const gradeOptions = {
    '1':'正高级',
    '2':'副高级',
    '3':'中级',
    '4':'初级',
}

const handleOk = async () => {    
  await formRef.value
    .validate()
    .then(() => {  
        formData.value.professionalQualifications = gradeOptions[formData.value.grade]
        emits("handleOk", type.value ,formData.value);
    })
    .catch((err:any) => {
      console.log(err);
    });
};

function handleCancel() {
    emits("handleCancel");
}
</script>