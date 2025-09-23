<template>
    <div class="page_content">
        <div class="top">
            <div class="title"><span>评审专家</span></div>
            <div class="search_area">
                <SearchHeader :formList="formList" :height="'150px'" @search="search"></SearchHeader>
            </div>
        </div>
        <div class="bottom">
            <div class="search_area">
                <a-button type="primary" style="width:82px;" :icon="h(PlusOutlined)" @click="addEditColumnsOpen('add')">新增</a-button>
            </div>
            <div class="search_table" id="data_result">
                <a-table  :scroll="{ y: tableScrollY }" :pagination="pagination" size="middle"
                    :dataSource="dataSource" :columns="columns" bordered>
                    <template #bodyCell="{ column, text, record, index }">
                        <template v-if="column.dataIndex === 'num'">
                        {{ index + 1 }}
                        </template>
                        <template v-if="column.dataIndex === 'operate'">
                        <div class="operate-style">
                            <!-- 编辑 -->
                            <a-button type="link" @click="addEditColumnsOpen('edit', record)">
                                {{ $t('placeholder.change') }}
                            </a-button>
                            <!-- 删除 -->
                            <a-button type="link" danger @click="openConfirm(record.id)">
                                {{ $t('placeholder.delete') }}
                            </a-button>
                        </div>
                        </template>
                    </template>
                </a-table>
            </div>
        </div>

        <!-- 经营范围 -->
        <addEditExpert :visible="columnsDialogVisible" :type="columnsDialogType" 
            :form-data="columnsData" :company-tree="companyTree"
            @handle-cancel="columnsDialogVisible = false;" @handle-ok="addEditColumnsExecute"></addEditExpert>

        <!-- 删除弹框 -->
        <DelModal ref="delRef" @delData="delData"></DelModal>
    </div>
</template>

<script lang="ts" setup>
import { reactive, ref, h, onUnmounted, onMounted } from 'vue';
import { 
    SearchOutlined,
    PlusOutlined
} from '@ant-design/icons-vue';
import { useRouter, useRoute } from 'vue-router';
import SearchHeader from '@/components/SearchHeader/index.vue';
// 删除弹窗
import DelModal from '@/components/DelModal/delDialogWithNoInfo.vue';
import addEditExpert from "./addExpertDialog.vue";
// api
import { reviewExpertsApi } from "@/api/ReviewExperts/index";
import { companyApi } from "@/api/company/index";

const $route = useRoute();
const $router = useRouter();

interface DataType {
    companyId: string;//所属企业id
    companyName: string;//所属单位
    grade: number|null;//等级（排序字段）
    id?: string;//主键id
    idNumber: string;//身份证号
    major: string;//所属专业
    name: string;//真实姓名
    phone: string;//手机号码
    professionalQualifications: string;//职称等级
}
const dataSource = ref<DataType[]>([]);
const columns = [
    {
        title: '所属单位',
        dataIndex: 'companyName',
        key: 'companyName',
        align: 'center',
    },
    {
        title: '真实姓名',
        dataIndex: 'name',
        key: 'name',
        align: 'center',
    },
    {
        title: '手机号码',
        dataIndex: 'phone',
        key: 'phone',
        align: 'center',
    },
    {
        title: '身份证号',
        dataIndex: 'idNumber',
        key: 'idNumber',
        align: 'center',
    },
    {
        title: '职称等级',
        dataIndex: 'professionalQualifications',
        key: 'professionalQualifications',
        align: 'center',
    },
    {
        title: '所属专业',
        dataIndex: 'major',
        key: 'major',
        align: 'center',
    },
    {
        title: '操作',
        dataIndex: 'operate',
        key: 'operate',
        align: 'center',
        width: 150,
    },
];

// 分页
const pages = reactive<any>({
    size: 10,
    current: 1,
    company: '',//所属企业id
    major: '',//所属专业
    name: '',//真实姓名
    professionalQualifications: '',//职称等级
})
const pagination = reactive<any>({
    pageSizeOptions: ['10', '20', '30', '40', '50'],
    showSizeChanger: true,
    total: 0,
    showTotal: ((total:any) => {
        return `共 ${total} 条`;
    }),
    onShowSizeChange: ((current:any,pageSize:any) => {
        pages.current = current;
        pages.size = pageSize;
    }),
    onChange: ((current:any) => {
        pages.current = current;
        getColumns()
    }),
})

// 新增、编辑
const columnsDialogVisible = ref<boolean>(false);
const columnsDialogType = ref<string>('edit');
const columnsData = ref<any>();
// 新增、编辑 打开弹窗以及赋初值
const addEditColumnsOpen = (type: string, data?: any) => {
  columnsDialogType.value = type;
  if (type == 'edit') {
    columnsData.value = JSON.parse(JSON.stringify(data))
  } else {
    columnsData.value = {
        companyId: null,//所属企业id
        grade: null,//等级（排序字段）
        idNumber: '',//身份证号
        major: '',//所属专业
        name: '',//真实姓名
        phone: '',//手机号码
        professionalQualifications: '',//职称等级
    }
  }
  columnsDialogVisible.value = true;
}// 编辑 弹窗确认数据返回
const addEditColumnsExecute = (type: string, data: any) => {    
  if (type == 'edit') {
      reviewExpertsApi.putReviewExperts(data).then((res:any) => {
          if (res.success) {
              columnsDialogVisible.value = false;
              getColumns()
          }        
      })
  } else {
    reviewExpertsApi.postReviewExperts(data).then((res:any) => {
        if (res.success) {
            columnsDialogVisible.value = false;
            getColumns()
        }        
    })
  }
}
const delColumnsById = (id: string) => {
    reviewExpertsApi.delReviewExpertsById(id).then((res:any) => {
        if (res.success) {
            getColumns()
        }
    })
}
const getColumns = () => {
    reviewExpertsApi.getReviewExpertsPage(pages).then((res:any) => {
        if (res.success) {
            dataSource.value = res.obj.records
            pagination.total = res.obj.total
        }
    })
}

//删除
const delFileId = ref<string>('');
const delRef = ref<any>();
const delData = () => {
  delColumnsById(delFileId.value)
  delRef.value.close()
}
const openConfirm = (id: any) => {
  delFileId.value = id;
  delRef.value.open();
}

const formList = ref<any>([
    { type: 'a-tree-select-diy', title: '所属单位', bind: 'companyId', span: 12, label:'companyName', value:'id', options: [] },
    { type: 'a-input', title: '真实姓名', bind: 'name', span: 12 },
    { type: 'a-input', title: '所属专业', bind: 'major', span: 12 },
    { type: 'a-select', title: '职称等级', bind: 'professionalQualifications', span: 12,
         options: [ {value: '正高级', label: '正高级'}, 
                    {value: '副高级', label: '副高级'}, 
                    {value: '中级', label: '中级'}, 
                    {value: '初级', label: '初级'}]
    },
])
const search = (formState: any) => {
    pages.size = 10
    pages.current = 1
    pages.name = formState.name//真实姓名
    pages.company = formState.companyId//所属企业id
    pages.major = formState.major//所属专业
    pages.professionalQualifications = formState.professionalQualifications//职称等级
    getColumns()
}

const companyTree = ref<any>([])
const getComTree = () => {
  companyApi.getCompanyTree().then((res:any) => {
    if (res.success) {
      companyTree.value = res.obj;
      formList.value[0].options = res.obj;
    }
  })
}

const tableScrollY = ref<number>(0)
const resizeScrollY = () => {
  let dataResultHeight = (document.getElementById('data_result') as HTMLElement).offsetHeight;
  tableScrollY.value = dataResultHeight - 140
};
onMounted(() => {
  resizeScrollY()
  window.addEventListener("resize", resizeScrollY)
  getComTree()
  getColumns()
})
onUnmounted(() => {
  window.removeEventListener("resize", resizeScrollY)
});
</script>

<style lang="less" scoped>
@import url("index.less");

.page_content {
    width: 100%;
    height: 100%;
}
</style>
