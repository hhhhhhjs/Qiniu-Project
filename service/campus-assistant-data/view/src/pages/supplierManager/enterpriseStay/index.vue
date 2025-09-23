<template>
  <div class="page-content1">
    <div class="page_title1">
      <div class="title_left">入驻企业</div>
    </div>
    <div class="company_content1">
      <div class="authorized">
        <span>已授权企业</span>
      </div>
      <div class="authorized_content">
        <div class="icon_and_name" v-for="item in authPurchaserList">
          <div class="icon">
            <img src="../../../assets/images/company_icon.svg" alt="">
          </div>
          <div class="name">
            <span>{{ item.purchaserName }}</span>
          </div>
        </div>
      </div>
      <div class="unauthorized">
        <span>未授权企业</span>
      </div>
      <div class="unauthorized_content">
        <div class="items_content">
          <div class="items" v-for="item in purchaserList">
            <span class="title">{{ item.companyName }}</span>
            <span class="apply" @click="applyToJoin(item.id)">申请</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
  
<script lang="ts" setup>
import { joinPurchaserApi } from "@/api/JoinPurchaser";
import { companyApi } from "@/api/company";
import { message } from "ant-design-vue";
import { onMounted, ref } from "vue";

const purchaserList = ref<any>([]);   // 未授权企业
const authPurchaserList = ref<any>([]);   // 已授权企业
const getPurchaserCompany = () => {
  const pageData = {
    size: 1000,
    current: 1,
    purchaser: true
  }
  companyApi.getCompanyTypeListPage(pageData).then((res: any) => {
    if (res.success) {
      res.obj.records.filter((v: any) => authPurchaserList.value.every((val: any) => val.id != v.id))
      let local = localStorage.getItem('userInfo') as any
      let storage = JSON.parse(local)
      purchaserList.value = res.obj.records.filter((item: any) => item.id !== storage.companyId);
    };
  })
}
const getAuthPurchaserCompany = () => {
  joinPurchaserApi.getJoinPurchaserList('1').then((res: any) => {
    if (res.success) {
      authPurchaserList.value = res.obj;
      getPurchaserCompany();
    };
  })
}

const applyToJoin = (id: string) => {
  joinPurchaserApi.postJoinPurchaser(id).then((res: any) => {
    if (res.success) {
      message.success("已提交申请")
    }
  });
}

onMounted(() => {
    getAuthPurchaserCompany();
})
</script>
  
<style lang="less" scoped>
.page-content1 {
  width: 100%;
  height: 100%;
  background-color: #fff;
  overflow: hidden;
}

.page_title1 {
  height: 48px;
  width: 100%;
  display: flex;
  align-items: center;
  padding: 0 16px;
  background-color: #fff;
  border-bottom: 1px solid var(--unnamed, #F1F2F4);

  .title_left {
    color: var(--unnamed, #1D2129);
    font-family: PingFang SC;
    font-size: 16px;
    font-style: normal;
    font-weight: 600;
    line-height: normal;
  }
}

.company_content1 {
  width: 100%;
  height: calc(100% - 48px);
  padding: 34px 24px;
  overflow: hidden;

  .authorized {
    display: flex;
    width: 100%;
    height: 32px;
    justify-content: center;
    align-items: center;
    background: linear-gradient(90deg, rgba(0, 112, 216, 0.00) 0%, #2454CA 50%, rgba(0, 125, 216, 0.00) 100%);

    span {
      text-align: center;
      color: var(--unnamed, #FFF);
      font-family: PingFang SC;
      font-size: 16px;
      font-style: normal;
      font-weight: 500;
      line-height: normal;
    }
  }

  .authorized_content {
    display: flex;
    gap: 16px 0;
    padding: 32px 19px;
    width: 100%;
    height: 200px;
    border-bottom: 1px solid var(--unnamed, #F1F2F4);
    // gap: 32px;
    flex-wrap: wrap;
    overflow: hidden auto;

    .icon_and_name {
      display: flex;
      position: relative;
      // width: 320px;
      width: 33%;
      min-width: 320px;
      height: 48px;

      .icon {
        display: flex;
        z-index: 9999;
        width: 48px;
        height: 48px;
        padding: 8px;
        justify-content: center;
        align-items: center;

        border-radius: 100%;
        background: linear-gradient(180deg, #0045AD 0%, #16A8FF 100%);
        box-shadow: 0px 4px 10px 0px rgba(0, 0, 0, 0.15);
      }

      .name {
        position: absolute;
        left: 25px;
        padding-right: 25px;
        // width: 295px;
        min-width: 295px;
        width: calc(100% - 48px);
        height: 48px;

        display: flex;
        flex-direction: column;
        justify-content: center;
        padding-left: 29px;
        gap: 8px;
        flex: 1 0 0;
        border-radius: 0px 36px 36px 0px;
        border: 1px solid var(--unnamed, #F7F8F9);
        background: var(--unnamed, #F7F8F9);
        box-shadow: 0px 4px 10px 0px rgba(0, 0, 0, 0.15);

        span {
          width: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          overflow: hidden;
          color: var(--unnamed, #1D2129);
          text-overflow: ellipsis;
          font-family: PingFang SC;
          font-size: 14px;
          font-style: normal;
          font-weight: 400;
          line-height: normal;
          cursor: default;
        }
      }
    }
  }

  .unauthorized {
    display: flex;
    width: 100%;
    height: 54px;
    padding: 19px;

    span {
      color: var(--unnamed, #86909C);
      font-family: PingFang SC;
      font-size: 16px;
      font-style: normal;
      font-weight: 500;
      line-height: normal;
    }
  }

  .unauthorized_content {

    width: 100%;
    // height: calc(100% - 32px - 200px - 54px);
    height: calc(100% - 286px);
    padding: 19px;
    overflow: hidden auto;

    .items_content {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      /* 横向排列规则，把宽度分为三等分 */
      gap: 32px;

      .items {
        position: relative;
        display: flex;
        min-width: 320px;
        width: 100%;
        height: 50px;
        padding: 8px 15px;
        justify-content: center;
        align-items: center;
        gap: 8px;
        flex-shrink: 0;
        border-radius: 4px;
        background: var(--unnamed, #F7F8F9);

        .title {
          overflow: hidden;
          color: var(--unnamed, #4E5969);
          text-align: center;
          text-overflow: ellipsis;
          font-family: PingFang SC;
          font-size: 14px;
          font-weight: 500;
          cursor: default;
        }

        .apply {
          position: absolute;
          z-index: 999;
          top: 0;
          right: 0;
          display: none;
          width: 50px;
          height: 50px;
          padding: 8px;
          justify-content: center;
          align-items: center;
          gap: 8px;
          flex-shrink: 0;
          border-radius: 4px;
          color: #fff;
          background: linear-gradient(180deg, rgba(45, 129, 255, 0.95) 0%, rgba(22, 168, 255, 0.95) 100%, rgba(33, 172, 255, 0.95) 100%);
        }

        .apply:hover {
          cursor: pointer;
        }
      }

      .items:hover {
        border-radius: 4px;
        border: 1px solid var(--unnamed, #F1F2F4);
        background: #FFF;
        box-shadow: 4px 4px 10px 0px rgba(0, 0, 0, 0.15);

        .apply {
          display: flex;
        }
      }
    }
  }
}</style>
  