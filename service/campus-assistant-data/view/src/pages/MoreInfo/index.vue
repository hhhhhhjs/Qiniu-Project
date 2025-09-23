<template>
  <div class="more-info-wrapper">
    <div class="left">
      <a-card title="公告" :bordered="false" style="width: 18.75rem;height: 100%;">
        <div v-for="item in treeData" :key="item.id" class="flex-space-bt item-title"
          :class="[isActive == item.id ? 'active' : '']" @click="handleCheck(item.id)">
          <span>{{ item.name }}</span>
          <CaretRightOutlined :style="{ color: '#1890ff' }" />
        </div>
      </a-card>

    </div>
    <div class="right">
      <div class="top">
        <a-card :bordered="false" style="width: 100%; height: 88px;line-height: 88px;">
          <!-- <span><LeftOutlined /> 返回</span> -->
          <a-form layout="inline" :model="formState">
            <a-form-item label="关键字">
              <a-input v-model:value="formState.projectName" placeholder="请输入" style="width: 300px;"></a-input>
            </a-form-item>
            <a-form-item label="发布时间">
              <a-date-picker v-model:value="formState.startDate" placeholder="开始日期" format="YYYY/MM/DD" valueFormat="YYYY/MM/DD"
                style="width: 300px;" />
              <span style="margin: 0 5px;">-</span>
              <a-date-picker v-model:value="formState.endDate" placeholder="结束日期" format="YYYY/MM/DD" valueFormat="YYYY/MM/DD"
                style="width: 300px;" />
            </a-form-item>
            <a-form-item>
              <a-space>
                <a-button type="primary" @click="handleSearch">
                  <SearchOutlined />
                  搜索
                </a-button>
                <a-button type="primary" ghost @click="handleReset">
                  重置
                </a-button>
              </a-space>
            </a-form-item>
          </a-form>
        </a-card>
      </div>
      <div class="bottom">
        <div class="list-wrapper">
          <div v-for="item in infoList" :key="item.id" class="info-item flex-space-bt" @click="handleClick">
            <span>
              <span class="company-name">[{{ item.companyName }}]</span>&puncsp;
              <span>{{ item.projectName }}</span>
            </span>
            <span>
              {{ item.timeRemaining }}
            </span>
          </div>
        </div>
        <div class="footer-pagination">
          <a-pagination v-model:current="formState.current" v-model:page-size="formState.size" :total="total"
            :show-total="(total: number) => `总 ${total} 条`" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { CaretRightOutlined, SearchOutlined,LeftOutlined } from '@ant-design/icons-vue'
import { executeApi } from '@/api/Execute/index'
import { useRouter } from 'vue-router'
import {debounce} from 'lodash'
const $router = useRouter()
const treeData = ref([
  {
    id: '0',
    name: '招标公告',
  },
  {
    id: '1',
    name: '竞争性谈判公示',
  },
  {
    id: '3',
    name: '询比价公示',
  }, {
    id: '4',
    name: '中标&成交公示',
  }
])
const typeId =  computed(()=> $router.currentRoute.value.query.id)
const isActive = ref(typeId.value)
const handleCheck = (id: string) => {
  isActive.value = id
  formState.purchaseWay = id
  if (id == '4') {
    initGetExecutePublicityData()
  } else {
    initDataMethod()
  }
}

const total = ref<number>(0)
const formState = reactive<any>({
  current: 1,
  size: 20,
  projectName: '',
  startDate: '',
  endDate: '',
  purchaseWay: '0'
})
const infoList = ref<any>([])
const initDataMethod = () => {
  executeApi.getExecuteIndexListPage(formState).then(res => {
    console.log(res);
    const { success, obj }: { success: boolean, obj: any } = res
    if (success) {
      obj.records.forEach((item: any) => {
        item.timeRemaining = getRemainTime(item.endDate)
      })
      infoList.value = obj.records
      total.value = Number(obj.total)
    }
  })
}
const initGetExecutePublicityData = () => {
  executeApi.getExecutePublicityPage(formState).then(res => {
    console.log(res);

  })
}
const getRemainTime = (endTime: string) => {
  // 现在时间
  var now = Date.now();
  //截止时间
  var until: any = new Date(endTime)
  // 计算时会发生隐式转换，调用valueOf()方法，转化成时间戳的形式
  var days = (until - now) / 1000 / 3600 / 24;
  // 下面都是简单的数学计算 
  var day = Math.floor(days);
  var hours = (days - day) * 24;
  var hour = Math.floor(hours);
  var back = '剩余' + day + '天' + hour + '小时'
  return back;
}
const initAll = () => {
  if (isActive.value == '4') {
    initGetExecutePublicityData()
  } else {
    initDataMethod()
  }
}
const handleSearch = debounce(() => {
    initAll()
},300)
const handleReset = () => {
  initAll()
  formState.current = 1
  formState.size = 20
  formState.projectName = ''
  formState.startDate = ''
  formState.endDate = ''
  formState.purchaseWay = isActive.value
}
onMounted(() => {
  initAll()
})
const handleClick = () => {

}
</script>
<style lang="less" scoped>
.more-info-wrapper {
  display: flex;
  height: 100%;

  .left {
    width: 18.75rem;
    height: 100%;
    margin-right: 1rem;
  }

  .right {
    flex: 1;

    .top {
      margin-bottom: 1rem;
    }

    .bottom {
      position: relative;
      width: 100%;
      height: calc(100% - 104px);
      background-color: #fff;
      padding: 1rem;

      .list-wrapper {
        height: 90%;
        overflow: auto;
      }

      .footer-pagination {
        position: absolute;
        right: 20px;
        bottom: 20px;
      }

      .info-item {
        cursor: pointer;
        .company-name {
          color: #ff7b1d;
        }

      }
    }
  }
}

.item-title {
  height: 2.18rem;
  line-height: 2.18rem;
  padding: 0 0.8rem;
  cursor: pointer;
  border-radius: 0.4rem;
}

.active {
  background-color: #e4f2ff;
  color: #1890ff;
}

.ant-card {
  border-radius: 0;
}
</style>