<!--
 * @Description: 弹窗
-->
<template>
    <a-modal :title="type == 'add'?'新增':'编辑'" v-model:open="visible" width="550px"
        :destroyOnClose="true" @ok="handleOk"  @cancel="handleCancel">
        <template #footer>
            <a-button key="back" @click="handleCancel">取消</a-button>
            <a-button key="submit" type="primary" @click="handleOk">确认</a-button>
        </template>

        <a-form :model="formData" ref="formRef" :rules="formRules" :label-col="{ span: 8 }" wrap>
            <a-form-item label="上传企业图标" v-if="type == 'edit'">
                <a-upload
                    v-model:file-list="fileList"
                    list-type="picture-card"
                    @preview="handlePreview"
                    :before-upload="beforeUpload"
                    :maxCount="1"
                    :customRequest="fileUploadChange"
                >
                    <div>
                        <plus-outlined />
                        <div style="margin-top: 8px">Upload</div>
                    </div>
                </a-upload>
            </a-form-item>
            <a-form-item label="公司名称" name="companyName">
                <a-input class="input"
                    :placeholder="$t('placeholder.pleaseEnter')"
                    v-model:value="formData.companyName">
                </a-input>
            </a-form-item>
            <a-form-item label="注册地址" name="address">
                <a-input class="input"
                    :placeholder="$t('placeholder.pleaseEnter')"
                    v-model:value="formData.address">
                </a-input>
            </a-form-item>
            <a-form-item label="开户行" name="bank">
                <a-input class="input"
                    :placeholder="$t('placeholder.pleaseEnter')"
                    v-model:value="formData.bank">
                </a-input>
            </a-form-item>
            <a-form-item label="银行账户" name="bankAccount">
                <a-input class="input"
                    :placeholder="$t('placeholder.pleaseEnter')"
                    v-model:value="formData.bankAccount">
                </a-input>
            </a-form-item>
            <a-form-item label="企业编码" name="companyCode">
                <a-input class="input"
                    :placeholder="$t('placeholder.pleaseEnter')"
                    v-model:value="formData.companyCode">
                </a-input>
            </a-form-item>
            <a-form-item label="统一信用识别码" name="creditCode">
                <a-input class="input"
                    :placeholder="$t('placeholder.pleaseEnter')"
                    v-model:value="formData.creditCode">
                </a-input>
            </a-form-item>
            <a-form-item label="法人代表" name="legalPerson">
                <a-input class="input"
                    :placeholder="$t('placeholder.pleaseEnter')"
                    v-model:value="formData.legalPerson">
                </a-input>
            </a-form-item>
            <!-- <a-form-item label="是否是采购商" name="purchaser">               
                <a-radio-group v-model:value="formData.purchaser">
                    <a-radio :value="true">是</a-radio>
                    <a-radio :value="false">否</a-radio>
                </a-radio-group>
            </a-form-item>
            <a-form-item label="是否是供应商" name="supplier">
                <a-radio-group v-model:value="formData.supplier">
                    <a-radio :value="true">是</a-radio>
                    <a-radio :value="false">否</a-radio>
                </a-radio-group>
            </a-form-item> -->
        </a-form>


    </a-modal>
</template>

<script setup lang="ts">
import i18n from "@/i18n";
import { onMounted, reactive, ref, toRefs, watch } from "vue";
import {
    LoadingOutlined,
    PlusOutlined,
} from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import type { UploadChangeParam, UploadProps } from 'ant-design-vue';
import { companyApi } from "@/api/company";

// {
//   "address": "string",
//   "bank": "string",
//   "bankAccount": "string",
//   "companyCode": "string",
//   "companyName": "string",
//   "creditCode": "string",
//   "id": 0,
//   "legalPerson": "string",
//   "level": 0,
//   "orderIndex": 0,
//   "parentId": 0,
//   "parentIds": "string",
//   "photo": "string",
//   "taxpayerCode": "string"
// }

const props = defineProps<{
    visible: boolean;
    type: string;
    formData: any;
}>();
const { visible, type, formData } = toRefs(props);
const emits = defineEmits(["handleOk", "handleCancel"]);

watch(
    () => visible.value,
    val => {
        if (val) {
            fileList.value.length = 0;
            fileList.value.push(
                {
                    uid: '-1',
                    name: 'image.png',
                    status: 'done',
                    url: 'http://www.tangguangdi.com/zjimee-pbm/organization/company/downLoadPhoto?fileName=' + formData.value.photo,
                }
            )
        }
    }
)

// 企业信息
interface IFormState {
    address: string;//注册地址
    bank: string;// 开户行
    bankAccount: string;// 银行账户
    companyCode: string;// 企业编号
    companyName: string;// 公司名称
    creditCode: string;// 统一信用识别码
    legalPerson: string;// 法人代表
    // level: string;// 层级
    // orderIndex: string;// 排序权重值
    // parentId: string;// 父节点id
    // parentIds: string;// 所有父节点id
    photo: string;// 图片地址
    taxpayerCode: string;// 纳税人识别号
}

const formState = reactive<IFormState>({
    address: '',//注册地址    
    bank: '',// 开户行    
    bankAccount: '',// 银行账户
    companyCode: '',// 企业编号    
    companyName: '',// 公司名称    
    creditCode: '',// 统一信用识别码    
    legalPerson: '',// 法人代表    
    // level: '',// 层级    
    // orderIndex: '',// 排序权重值    
    // parentId: '',// 父节点id    
    // parentIds: '',// 所有父节点id    
    photo: '',// 图片地址    
    taxpayerCode: '',// 纳税人识别号    
});
const formRef = ref();
const formRules = {
    address: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
    bank: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
    bankAccount: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
    companyCode: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
    companyName: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
    creditCode: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
    legalPerson: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
    taxpayerCode: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
    supplier: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
    purchaser: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
};


function getBase64(file: File) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = error => reject(error);
  });
}
interface IFileItem {
    uid:string;
    name:string;
    status:string;
    url:string;
}
const fileList = ref<IFileItem[]>([]);
const beforeUpload = (file: any) => {
  const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png';
  if (!isJpgOrPng) {
    message.error('You can only upload JPG file!');
  }
  const isLt2M = file.size / 1024 / 1024 < 2;
  if (!isLt2M) {
    message.error('Image must smaller than 2MB!');
  }
  return isJpgOrPng && isLt2M;
};
const previewVisible = ref(false);
const previewImage = ref('');
const previewTitle = ref('');
const fileUploadChange = (file:any) => {
    const fileData = new FormData();
    fileData.append("file", file.file);
    companyApi.uploadCompanyPic(formData.value.id,fileData).then((res:any) => {        
        if (res.success) {
            fileList.value[0] = {
                uid: '-1',
                name: 'image.png',
                status: "done",
                url: 'http://www.tangguangdi.com/zjimee-pbm/organization/company/downLoadPhoto?fileName=' + res.obj
            }
        }
    })  
};
const handlePreview = async (file: any) => {
  if (!file.url && !file.preview) {
    file.preview = (await getBase64(file.originFileObj)) as string;
  }
  previewImage.value = file.url || file.preview;
  previewVisible.value = true;
  previewTitle.value = file.name || file.url.substring(file.url.lastIndexOf('/') + 1);
};

const handleOk = async (formState: IFormState) => {
  await formRef.value
    .validate()
    .then(() => {  
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

<style lang="less" scoped>
:deep(.ant-upload-list .ant-upload ){
    width: 100px !important;
}
</style>