<!-- 预邀厂商 -->
<template>
  <div class="basicInfo" id="qAClarification">
    <div class="basic-item">
      <UtilsTitle :title="'答疑澄清'">
        <a-button class="add-style" @click="addQADialog" :disabled="props.current">提疑</a-button>
      </UtilsTitle>
      <div style="padding: 16px 32px;">
        <div v-for="item in dataSource" style="margin-bottom: 8px;">
          <div class='issue-style'>
            <div class="issue-unit text-omit">
              提问单位：{{ item.companyName }}
            </div>
            <div class="issue-text text-omit">
              <img src="@/assets/images/Arrow-grh.svg" alt="" class="arrow-17">
              <img src="@/assets/images/clock.svg" alt="" class="clock-margin">
              <span class="issue-time">&nbsp; 提问时间 &nbsp;&nbsp;&nbsp;
                {{ item.createTime }}</span>
              <span>
                问题：{{ item.question }}
              </span>
            </div>
            <div class="issue-status" v-if="item.reply">
              <span>已答疑</span>
              <RightOutlined class="icon-style" v-if="item.iconFlag" @click="item.iconFlag = false" />
              <DownOutlined class="icon-style" v-else @click="item.iconFlag = true" />
            </div>
            <div class="issue-status2" v-else="item.reply">
              未答疑
            </div>
          </div>
          <div class="reply-style" v-if="item.iconFlag">
            {{ item.reply }}
          </div>
        </div>
        <div class="right-table-pages">
          <div>
            <!-- 共xx条数据 -->
            {{ $t('placeholder.allOf') }} {{ pageVO2.total }} {{ $t('placeholder.strip') }}{{
              $t('placeholder.data') }}
          </div>
          <a-pagination v-model:current="pageVO2.currentPage" v-model:pageSize="pageVO2.pageSize" show-size-changer
            :total="pageVO2.total" @change="sizeChangeNeeds">
          </a-pagination>
        </div>
        <!-- 
        <vxe-pager v-model:current-page="pageVO2.currentPage" v-model:page-size="pageVO2.pageSize" :total="pageVO2.total"
          size="medium" /> -->
      </div>

    </div>
  </div>

  <!-- 弹框 -->
  <!-- 新增修改弹框 -->
  <a-modal v-model:open="modalDialog" :title="formTile" @ok="formOk" :destroyOnClose="true">
    <a-form :model="formState" ref="formRef" :rules="formRules" >
      <a-form-item :label="item.label" :name="item.name" v-for="(item, index) in formEntry">
        <a-input v-model:value="formState[item.name]" :disabled="item?.disabled || false" v-if="item.type === 'a-input'"
          class="broder-red" />
        <a-select v-model:value="formState[item.name]" style="width: 100%" :placeholder="$t('placeholder.pleaseSelect')"
          :options="item.options" v-if="item.type === 'a-select'" :allowClear="true"></a-select>
        <a-space direction="vertical" style="width: 100%" v-if="item.type == 'a-date'">
          <a-date-picker v-model:value="formState[item.name]" style="width: 100%" />
        </a-space>
      </a-form-item>
    </a-form>
  </a-modal>
  <!-- 删除弹框 -->
  <DelModal ref="delRef" :delElementTitle="'税率/单价'" :delElementValue="delElementValue" @delData="delData"></DelModal>
</template>

<script lang="ts" setup>
import UtilsTitle from '@/components/UtilsTitle/index.vue';
import { ref, onMounted, reactive } from 'vue'
import { quotationApi } from '@/api/quotation'
import { executePurchaseFileApi } from '@/api/ExecuteQuestionReply'
import type { questionReply } from '@/api/ExecuteQuestionReply'
import { RightOutlined, DownOutlined } from '@ant-design/icons-vue';
interface props {
  propsid: string,
  current: number
}
const loading = ref<boolean>(true)
const props = defineProps<props>()
const dataSource = ref<any>(
  [
  ]
)
const toggleExpandChangeEvent: any = (e: any) => {
  console.log('行展开事件' + e.expanded)
}
const pageVO2 = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 8
})
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
    case 'addQA':
      addQA()
      break;
  }
}

//新增
const addQADialog = () => {
  modalDialog.value = true
  formState.value = addExecuteResponFileObj.formState
  formTile.value = addExecuteResponFileObj.formTile
  formEntry.value = addExecuteResponFileObj.formEntry
  formRules.value = addExecuteResponFileObj.formRules
  formApi.value = addExecuteResponFileObj.formApi
  addQAReset()
}
const addQAReset = () => {
  formState.value['question'] = ''

}
const addExecuteResponFileObj = {
  formTile: '提出疑问',
  formEntry: [
    { name: 'question', type: 'a-input', label: '疑问', disabled: false },
  ],
  formState: {
    question: '',//品牌
  },
  formRules: {
    question: [{ required: true, message: '疑问不可为空' }],
  },
  formApi: 'addQA'
}
const addQA = () => {
  formRef.value.validate().then((res: any) => {
    if (res) {
      const data = <questionReply>{
        executeId: props.propsid,
        question: formState.value['question']
      }
      executePurchaseFileApi.addExecutePurchaseFile(data).then((res: any) => {
        if (res.success) {
          console.log('是否成功', res);
          getexecuteListList()
          modalDialog.value = false
        }
      })
    }
  })
}

//删除
let crudId = ref<string>('')
const delElementValue = ref<string>('')
const delRef = ref<any>()
const openConfirm = (record: any) => {
  delRef.value.open()
  delElementValue.value = record.materialName
  crudId.value = record.idd
}
const delData = () => {
  quotationApi.delQuotation(crudId.value).then((res: any) => {
    if (res.success) {
      delRef.value.close()
      getexecuteListList()
    }
  })
}


const sizeChangeNeeds = () => {
  getexecuteListList()
}

const getexecuteListList = () => {
    const data = {
      current: pageVO2.currentPage,
      size: pageVO2.pageSize,
      executeId: props.propsid
    }
    executePurchaseFileApi.getSupplyList(data).then((res: any) => {
      if (res.success) {
        dataSource.value = res.obj.records
        pageVO2.total = res.obj.total
        loading.value = false
      }
    })
}
const initialize =()=>{
  getexecuteListList()
}
defineExpose({initialize})
</script>

<style lang="less" scoped>
.basicInfo {
  // height: 100%;
  margin-top: 16px;
  overflow: hidden;

  .basic-item {
    // padding: 16px;
    overflow-y: auto;
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
  }
}

.expand-wrapper {
  padding: 20px;
}

:deep(.vxe-body--row:hover) {
  background-color: #fafafa;
}

//答疑单体
.issue-style {
  width: 100%;
  height: 40px;
  background-color: #F1F2F4;
  border-radius: 4px;
  border: 1px solid #F1F2F4;
  box-sizing: border-box;
  padding: 0 16px;
  display: grid;
  grid-template-columns: 3fr 5fr 80px;
  align-items: center;
  .issue-unit {
    color: var(--unnamed, #1D2129);
    font-family: PingFang SC;
    font-size: 14px;
    font-style: normal;
    font-weight: 550;
    line-height: normal;
    padding-right: 20px;
  }

  .issue-text {
    color: var(--unnamed, #4E5969);
    font-family: PingFang SC;
    font-size: 14px;
    font-style: normal;
    font-weight: 400;
    line-height: normal;

    .arrow-17 {
      height: 17px;
    }

    .clock-margin {
      margin-left: 20px;
      margin-right: 4px;
      // margin-top: -2px;
    }

    .issue-time {
      margin-right: 12px;
    }
  }

  .issue-status {
    color: var(--1, #165DFF);
    font-family: PingFang SC;
    font-size: 12px;
    font-style: normal;
    font-weight: 550;
    line-height: normal;
    display: flex;
    justify-content: right;
    align-items: center;

    .icon-style {
      margin-left: 8px;
    }
  }

  .issue-status2 {
    color: var(--4, #FF7D00);
    font-family: PingFang SC;
    font-size: 12px;
    font-style: normal;
    font-weight: 500;
    line-height: normal;
    display: flex;
    justify-content: right;
    align-items: center;
    margin-right: 20px;

  }
}

.reply-style {
  padding: 12px;
  border: 1px solid #F1F2F4;
}

.right-table-pages {
  margin-top: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>