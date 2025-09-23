<template>
  <div class="page_content">
    <div class="top">
      <div class="title">
        <span @click="routerBack">
          <LeftOutlined />
        </span>
        <span>{{ productType }}商品</span>
      </div>
    </div>
    <div class="bottom">
      <div class="base_title">
        <span>基本信息</span>
      </div>
      <div class="base_content">
        <a-form :model="formData" ref="formRef" :rules="formRules" :label-col="{ span: 6 }">
          <a-form-item label="商品名称" name="name">
            <a-input class="input_with_width" :placeholder="$t('placeholder.pleaseEnter')"
              v-model:value="formData.name">
            </a-input>
          </a-form-item>
          <a-form-item label="商品图片" name="photo">
            <a-upload 
              v-model:file-list="fileList" 
              list-type="picture-card" 
              :before-upload="beforeUpload" 
              :maxCount="1" 
              :customRequest="fileUploadChange">
              <div>
                <plus-outlined :style="{ fontSize: '40px', color: '#2454CA' }" />
                <div style="margin-top: 8px; color: #2454CA;">添加图片</div>
              </div>
            </a-upload>
          </a-form-item>
          <a-form-item label="商品类别" name="commodityType">
            <a-select class="input_with_width" :placeholder="$t('placeholder.pleaseEnter')"
              :field-names="{ label: 'typeName', value: 'id', options: 'children' }"
              :options="commodityTypeOptions" v-model:value="formData.commodityType">
            </a-select>
          </a-form-item>
          <a-form-item label="商品规格" name="commodityAttribute">
            <a-input class="input_with_width" :placeholder="$t('placeholder.pleaseEnter')"
              v-model:value="formData.commodityAttribute">
            </a-input>
          </a-form-item>
          <a-form-item label="协议价格" name="price">
            <a-input-number class="input_with_width" :placeholder="$t('placeholder.pleaseEnter')"
              v-model:value="formData.price" :min="0">
            </a-input-number>
          </a-form-item>
          <a-form-item label="协议人员" name="contacts">
            <a-input class="input_with_width" :placeholder="$t('placeholder.pleaseEnter')"
              v-model:value="formData.contacts">
            </a-input>
          </a-form-item>
          <a-form-item label="联系方式" name="phone">
            <a-input class="input_with_width" :placeholder="$t('placeholder.pleaseEnter')"
              v-model:value="formData.phone">
            </a-input>
          </a-form-item>
          <a-form-item label="是否上架" name="status">
            <a-radio-group v-model:value="formData.status">
              <a-radio :value="true">是</a-radio>
              <a-radio :value="false">否</a-radio>
            </a-radio-group>
          </a-form-item>
          <a-form-item label="商品详情" name="commodityInfo">
            <QuillEditor theme="snow" toolbar="full" 
              ref="quillRef" content-type="html"
              v-model:content="formData.commodityInfo"/>
          </a-form-item>
        </a-form>
      </div>
      <div class="agreement">
        <div class="read_text" v-if="productType !== '编辑'">
          <span>点击阅读</span>
          <span>《机电集团xxxx总则》</span>
        </div>
        <a-button type="primary" @click="submitProduct" v-if="productType === '编辑'">编辑</a-button>
        <a-button type="primary" @click="submitProduct" v-else>同意协议条款,我要发布</a-button>
        <a-button type="primary" ghost @click="routerBack">取消</a-button>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, } from "vue";
import i18n from "@/i18n";
import {
  LeftOutlined,
  PlusOutlined,
} from '@ant-design/icons-vue';
// 富文本编辑框
import { Quill, QuillEditor } from '@vueup/vue-quill';
// 富文本编辑框主题
import '@vueup/vue-quill/dist/vue-quill.snow.css';
import { commodityApi } from "@/api/Commodity/index";
import { fileImportApi } from "@/api/FileImport/index";
import type { ICommodity } from "@/api/Commodity/index";
import { useRouter, useRoute } from 'vue-router';
import { message } from "ant-design-vue";
import { commodityTypeApi } from "@/api/CommodityType";

const $route = useRoute();
const $router = useRouter();

const quillRef = ref<any>()
const productType = ref<string>('编辑')

interface IFileItem {
    uid:string;
    name:string;
    status:string;
    url:string;
    originFileObj?:any;
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

const fileUploadChange = (file:any) => {
  formData.value.photo = file.file.name;
  if (fileList.value.length !== 0) {
    fileList.value[0].status = 'done';    
  }

  if (productType.value == '编辑') {
    const fileData = new FormData();
    fileData.append("file", file.file);
    fileImportApi.uploadFile(formData.value.id as string, fileData).then((res:any) => {
      if (res.success) {
        message.success("提交成功")
      }              
    })            
  }
};

const formData = ref<ICommodity>({
  commodityAttribute:'',//商品属性
  commodityInfo:'',//商品详情
  commodityType:'',//商品类别id
  contacts:'',//联系人
  name:'',//商品名称
  phone:'',//联系方式
  photo:'',//
  price:null,//协议价格
  status:true,//是否上架
})
const formRef = ref();
const formRules = {
  name: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
  commodityType: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
  commodityAttribute: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
  price: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
  contacts: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
  phone: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
  photo: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
  status: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
  commodityInfo: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
};

const confirmType = () => {
  if ($route.params.id === undefined) {
    productType.value = '新增'
  } else {
    productType.value = '编辑'    
    getProductById($route.params.id as string)
  }
}

const getProductById = (id:string) => {
  commodityApi.getCommodityById(id).then((res:any) => {
    if (res.success) {
      formData.value = res.obj
      formData.value.commodityInfo = res.obj.commodityInfo
      quillRef.value.setHTML(res.obj.commodityInfo)
      fileList.value.length = 0;
      fileList.value.push(
          {
              uid: '-1',
              name: 'image.png',
              status: 'done',
              url: `http://www.tangguangdi.com/zjimee-pbm/fileImport/downLoadFile?fileName=${res.obj.id}.jpg&id=${res.obj.id}`,
          }
      )
      formData.value.photo = res.obj.id + '.jpg';
    }
  })
}

const submitProduct = async () => {
  await formRef.value
    .validate()
    .then(() => { 
      if (productType.value == '新增') {
        commodityApi.postCommodity(formData.value).then((res:any) => {
          if (res.success) {
            const pictureId = res.obj
            if (fileList.value.length !== 0) {
              const fileData = new FormData();
              fileData.append("file", fileList.value[0].originFileObj);
              fileImportApi.uploadFile(pictureId, fileData).then((res:any) => {
                if (res.success) {
                  message.success("提交成功！")
                  $router.push({name:'signedProducts'});
                }              
              })            
            }
          }        
        })
      } else {
        commodityApi.putCommodity(formData.value).then((res:any) => {
          if (res.success) {
            message.success("提交成功！")
            $router.push({name:'signedProducts'});
          }        
        })
      }
    })
    .catch((err:any) => {
      console.log(err);
    });
};

// 获取商品类型树
const commodityTypeOptions = ref<any>([])
const getCommodityType = () => {
    commodityTypeApi.getCommodityTypeTree().then((res:any) => {
        if (res.success) {
          commodityTypeOptions.value = res.obj;
        }
    })
};

const routerBack = () => {
  $router.back();
}

onMounted(() => {
  confirmType()
  getCommodityType()
})
</script>

<style lang="less" scoped>
@import url("index.less");

.page_content {
  width: 100%;
  height: 100%;
}
</style>
