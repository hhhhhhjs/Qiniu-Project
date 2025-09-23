<template>
  <div ref="modal" class="modal">
    <a-modal v-model:open="indexListToInfoVisible" :title="temData.modalTitle" width="60%"
      :getContainer="() => $refs.modal">
      <div class="big-title">
        <span>{{ temData.title }}</span>
      </div>
      <div class="title-bottom-time"><span>发布时间：{{ temData.time }}</span></div>
      <div class="table-style">
        <div class="table">
          <div class="table-left">
            <div class="table-left-text" v-for="item in tableLfetObj">
              <div class="text-left">{{ item.title }}</div>
              <div class="text-right">{{ item.label }}</div>
            </div>
          </div>
          <div class="table-right">
            <div class="table-right-text" v-for="item in tableRightObj">
              <div class="text-left">{{ item.title }}</div>
              <div class="text-right">{{ item.label }}</div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <a-button type="primary" @click="hanldeCheckInfo">查看详情
          <ArrowRightOutlined />
        </a-button>
      </template>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, toRefs } from 'vue'
import { ArrowRightOutlined, } from '@ant-design/icons-vue';
import { executeApi } from '@/api/Execute/index'
import {useRouter} from 'vue-router'
const indexListToInfoVisible = ref<boolean>(false)
const $router  = useRouter()

const temData = reactive({
  id: '',
  modalTitle: '',
  title: '',
  time: '',
})
const initData = (id: string, modalTitle: any) => {
  temData.id = id
  temData.modalTitle = modalTitle
  indexListToInfoVisible.value = true
  executeApi.getExecuteInfo(id).then(res => {
    const { success, obj: infoData }: { success: boolean, obj: any } = res
    if (success) {
      temData.title = infoData.projectName
      temData.time = infoData.startDate

      tableLfetObj.projectName.label = infoData.projectName
      tableLfetObj.purchaseWay.label = infoData.purchaseWay
      tableLfetObj.companyName.label = infoData.companyName
      tableLfetObj.startDate.label = infoData.startDate
      tableLfetObj.amount.label = infoData.amount || '-'
      tableLfetObj.collectionAccount.label = infoData.collectionAccount || '-'
      tableLfetObj.contacts.label = infoData.contacts
      tableLfetObj.email.label = infoData.email

      tableRightObj.number.label = infoData.number
      tableRightObj.classify.label = infoData.classify
      tableRightObj.purchasePriceLimit.label = infoData.purchasePriceLimit
      tableRightObj.endDate.label = infoData.endDate
      tableRightObj.currency.label = infoData.currency || '-'
      tableRightObj.bank.label = infoData.bank || '-'
      tableRightObj.phone.label = infoData.phone
      tableRightObj.demandAddress.label = infoData.demandAddress
    }
  })
}
const tableLfetObj = reactive<any>({
  projectName: { title: '项目名称', label: '' },
  purchaseWay: { title: '采购类型', label: '' },
  companyName: { title: '采购单位', label: '' },
  startDate: { title: '开始时间', label: '' },
  amount: { title: '保证金', label: '' },
  collectionAccount: { title: '收款账号', label: '' },
  contacts: { title: '联系人', label: '' },
  email: { title: '电子邮箱', label: '' },

})
const tableRightObj = reactive<any>({
  number: { title: '项目编码', label: '' },
  classify: { title: '行业分类', label: '' },
  purchasePriceLimit: { title: '采购限价', label: '' },
  endDate: { title: '结束时间', label: '' },
  currency: { title: '币种', label: '' },
  bank: { title: '银行名称', label: '' },
  phone: { title: '电话', label: '' },
  demandAddress: { title: '需求地点', label: '' },
})
const hanldeCheckInfo = () => {
  $router.push({ name: 'projectsAreAvailableDetail', query: { id: temData.id }})
  indexListToInfoVisible.value = false
}
defineExpose({ initData })
</script>
<style lang="less" scoped>
.modal {
  // text-align: center;

  :deep(.ant-modal-title) {
    text-align: left;
  }
  .big-title {
    font-size: 22px;
    font-weight: 600;
    text-align: center;
  }
  .title-bottom-time {
    text-align: center;
  }
  :deep(.ant-modal-footer) {
    text-align: center;
  }
}

.table-style {
  height: 400px;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0 16px;

  .table {
    margin-top: 28px;
    margin-bottom: 16px;
    display: flex;
    margin-left: 42px;
    margin-right: 58px;
    width: calc(100% - 132px);

    .table-left {
      width: 50%;

      .table-left-text {
        display: flex;
        height: 40px;

        .text-left {
          font-size: 16px;
          background-color: var(--unnamed, #F9FAFB);
          width: 120px;
          border: 1px solid var(--unnamed, #8D99A5);
          border-right: 0;
          padding: 0 16px;
          display: flex;
          // justify-content: center;
          align-items: center;
        }

        .text-right {
          font-size: 16px;
          width: calc(100% - 120px);
          border: 1px solid var(--unnamed, #8D99A5);
          border-right: 0;
          padding: 0 16px;
          display: flex;
          // justify-content: center;
          align-items: center;
        }
      }
    }

    .table-right {
      width: 50%;

      .table-right-text {
        display: flex;
        height: 40px;

        .text-left {
          font-size: 16px;
          background-color: var(--unnamed, #F9FAFB);
          width: 120px;
          border: 1px solid var(--unnamed, #8D99A5);
          border-right: 0;
          padding: 0 16px;
          display: flex;
          // justify-content: center;
          align-items: center;
        }

        .text-right {
          font-size: 16px;
          width: calc(100% - 120px);
          border: 1px solid var(--unnamed, #8D99A5);
          padding: 0 16px;
          display: flex;
          // justify-content: center;
          align-items: center;
        }
      }
    }
  }
}
</style>