<!--
 * @Description: 弹窗
-->
<template>
    <a-modal :title="type == 'add'?'新增':'编辑'" v-model:open="visible" width="500px"
        :destroyOnClose="true" @ok="handleOk"  @cancel="handleCancel">
        <template #footer>
            <a-button key="back" @click="handleCancel">取消</a-button>
            <a-button key="submit" type="primary" @click="handleOk">确认</a-button>
        </template>    
         <!-- :label-col="{ span: 6 }" -->
        <a-form :model="formData" ref="formRef" :rules="formRules">
            <!-- supplyType: string;// 可供类目 -->
            <a-form-item label="可供类目" name="supplyType">
                <a-input class="input"
                    :placeholder="$t('placeholder.pleaseEnter')"
                    v-model:value="formData.supplyType">
                </a-input>
            </a-form-item>
            <!-- supplyMaterial: string;// 可供物料 -->
            <a-form-item label="可供物料" name="supplyMaterial">
                <a-input class="input"
                    :placeholder="$t('placeholder.pleaseEnter')"
                    v-model:value="formData.supplyMaterial">
                </a-input>
            </a-form-item>
        </a-form>
    </a-modal>
</template>

<script setup lang="ts">
import i18n from "@/i18n";
import { onMounted, reactive, ref, toRefs } from "vue";
import {
    LoadingOutlined,
    PlusOutlined,
} from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';

import { supplyListApi } from "@/api/SupplyList";
import type { ISupplyList } from "@/api/SupplyList";

const props = defineProps<{
    visible: boolean;
    type: string;
    formData: ISupplyList;
}>();
const { visible, type, formData } = toRefs(props);
const emits = defineEmits(["handleOk", "handleCancel"]);

const formRef = ref();
const formRules = {
    supplyType: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
    supplyMaterial: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
};

const handleOk = async () => {
  await formRef.value
    .validate()
    .then(() => {  
        const data = JSON.parse(JSON.stringify(formData.value))
        emits("handleOk", type.value ,data);
        formRef.value.resetFields();
    })
    .catch((err:any) => {
        console.log(err);
    });
};

const handleCancel = () => {
    emits("handleCancel");
    formRef.value.resetFields();
}
</script>

<style lang="less" scoped>
</style>