<template>
    <div class="height100">
        <div>
            <UtilsTitle :title="'供应商管理'"></UtilsTitle>
        </div>
        <SearchHeader :formList="formList" :height="'150px'" @search="search"></SearchHeader>
        <div class="border1"></div>
        <div class="needs-table">
            <div class="menu">
                <a-menu v-model:selectedKeys="menusCurrent" mode="horizontal" :items="menus" @select="selectItem" />
            </div>
            <div class="table-body">
                <a-table :columns="columns" :data-source="dataSource" :pagination="pagination" 
                    bordered :loading="loading" size="small" rowKey="id">
                    <template #bodyCell="{ column, text, record, index }">
                        <template v-if="column.dataIndex === 'xuhao'">
                            <span>{{ index + 1 }}</span>
                        </template>
                        <template v-if="column.dataIndex === 'status'">
                            <span v-if="text === '0'">申请中</span>
                            <span v-else>已通过</span>
                        </template>
                        <template v-if="column.dataIndex === 'operate'">
                            <div class="operate-style">
                                <div class="detail-style" @click="gotoManage(record)">详情</div>
                                <div class="detail-style" v-if="record.status == '0'" @click="openConfirm(record, '同意')">通过</div>
                                <div class="del-style" v-if="record.status == '0'" @click="openConfirm(record, '拒绝')">拒绝</div>
                            </div>
                        </template>
                    </template>
                </a-table>
            </div>
        </div>
    </div>

    <DelDialogWithTitle ref="confirmRef" @delData="confirmData" :title="confirmTitle"></DelDialogWithTitle>
</template>

<script setup lang='ts'>
import UtilsTitle from '@/components/UtilsTitle/index.vue';
import DelDialogWithTitle from "@/components/DelModal/delDialogWithTitle.vue";
import { onMounted, ref, reactive } from 'vue';
import SearchHeader from '@/components/SearchHeader/index.vue'
import { useRouter, useRoute } from "vue-router";
import {
    ExclamationCircleOutlined
} from "@ant-design/icons-vue";
import { joinPurchaserApi } from '@/api/JoinPurchaser';

const $router = useRouter();

//上面的状态选择
const menusCurrent = ref<string[]>(['2'])
const menus = ref<any>([
    { label: '全部', title: '全部', key: '2' },
    { label: '申请中', title: '待发布', key: '0' },
    { label: '已通过', title: '执行中', key: '1' },
])
const selectItem = (e:any) => {
    pages.current = 1;
    pages.size = '10';
    pages.companyName = '';
    switch (e.key) {
        case '2': pages.status = '';
            break;
        case '0': pages.status = e.key;            
            break;
        case '1': pages.status = e.key;            
            break;
    
        default:
            break;
    }
    getSupplierList();
}

//header serach
let formList = ref([
    { type: 'a-input', title: '企业名称', bind: 'companyName', span: 8 },
    // { type: 'a-input', title: '项目编码', bind: 'number', span: 8 },
    // { type: 'a-select', title: '采购方式', bind: 'purchaseWay', span: 8, options: procurementMethodsOptions },
    // { type: 'a-select', title: '采购类型', bind: 'type', span: 8, options: typeOfPurchase.value },//
    // { type: 'a-select', title: '行业分类', bind: 'classify', span: 8, options: industryClassification.value },//
    // { type: 'a-range', title: '起止时间', bind: 'startAndEndTime', span: 8 },
])
const header_formState = ref<any>()
const search = (formState: any) => {
    header_formState.value = JSON.parse(JSON.stringify(formState))
    pages.current = 1;
    pages.size = '10';
    pages.companyName = header_formState.value.companyName;
    getSupplierList();
}
//表格相关
const loading = ref<boolean>(true);
const dataSource = ref([]);
const columns = [
    {
        title: '企业名称',
        dataIndex: 'supplierName',
        width: 200,
        key: 'supplierName',
        align: 'center',
    },
    {
        title: '申请时间',
        dataIndex: 'createTime',
        width: 200,
        key: 'createTime',
        align: 'center',
    },

    {
        title: '信用代码',
        dataIndex: 'creditCode',
        width: 200,
        key: 'creditCode',
        align: 'center',
    },
    {
        title: '企业法人',
        dataIndex: 'legalPerson',
        width: 200,
        key: 'legalPerson',
        align: 'center',
    },
    {
        title: '状态',
        dataIndex: 'status',
        key: 'status',
        align: 'center',
        width: 100,
    },
    {
        title: '操作',
        dataIndex: 'operate',
        key: 'operate',
        align: 'center',
        width: 150,
    },
]

// 分页
const pagination = reactive<any>({
    pageSizeOptions: ['10', '20', '30', '40', '50'],
    showSizeChanger: true,
    showTotal: ((total:any) => {
        return `共 ${total} 条`;
    }),
    onShowSizeChange: ((current:any,pageSize:any) => {
        pages.current = current;
        pages.size = pageSize;
    }),
    onChange: ((current:any) => {
        pages.current = current;
        getSupplierList();
    }),
})
const pages = reactive<any>({
    size: '10',
    current: 1,
    status: '',
    companyName:'',
})

const getSupplierList = () => {
    loading.value = true;
    joinPurchaserApi.getJoinPurchaserPage(pages).then((res:any) => {
        if (res.success) {
            dataSource.value = res.obj.records;
        }        
    })
    loading.value = false;
}

const confirmTitle = ref<string>('');
const confirmType = ref<string>('');
const confirmId = ref<string>('');
const confirmRef = ref<any>();
const openConfirm = (record:any, type:string) => {
    confirmId.value = record.id;
    confirmType.value = type;
    if (type == '拒绝') {
        confirmTitle.value = '是否拒绝'+record.supplierName+'的申请？';
    } else {
        confirmTitle.value = '是否同意'+record.supplierName+'的申请？';
    }
    confirmRef.value.open();
}
const confirmData = () => {
    switch (confirmType.value) {
        case '拒绝': delApplyById(confirmId.value);
            break;
        case '同意': passApply(confirmId.value);
            break;    
        default:
            break;
    }
    confirmRef.value.close();
}

const gotoManage = (record:any) => {
    $router.push({ name: 'supplierDetail', params: { id: record.supplierId }})
}

const passApply = (id:string) => {
    joinPurchaserApi.putJoinPurchaser(id).then((res:any) => {
        if (res.success) {
            getSupplierList();
        }
    })
}

const delApplyById = (id:string) => {
    joinPurchaserApi.delJoinPurchaser(id).then((res:any) => {
        if (res.success) {
            getSupplierList();
        }
    })
}

onMounted(() => {
    getSupplierList();
})
</script>

<style scoped lang="less">
.height100 {
    height: 100%;
}

.border1 {
    border-bottom: dotted 2px #F1F2F4;
    margin-left: 32px;
    margin-right: 32px;
    margin-bottom: 24px;
}

.needs-table {
    background-color: #fff;
    height: calc(100% - 224px);
    overflow: hidden;

    .table-header {
        height: 40px;
        display: flex;
        justify-content: right;
        align-items: center;
        margin-right: 24px;
        margin-bottom: 12px;
        margin-top: 16px;

        .button-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #1357AF;
            color: #fff;
            height: 32px;
            width: 96px;
            height: 32px;
            padding: 5px 22px;
            margin-top: 12px;
            font-weight: 500;
        }
    }

    .table-body {
        margin-left: 24px;
        margin-top: 24px;
        // margin-right: 24px;
        padding-right: 12px;
        height: calc(100% - 148px);
        overflow: hidden;
        overflow-y: auto;

        .operate-style {
            display: flex;
            justify-content: space-around;
        }

        .detail-style {
            color: var(--unnamed, #2272DD);
            font-family: PingFang SC;
            font-size: 14px;
            font-style: normal;
            font-weight: 400;
            line-height: 22px;
            cursor: pointer;
            /* 157.143% */
        }

        .del-style {
            color: var(--5, #F53F3F);
            font-family: PingFang SC;
            font-size: 14px;
            font-style: normal;
            font-weight: 400;
            line-height: 22px;
            cursor: pointer;
            /* 157.143% */
        }
    }

    .right-table-pages {
        margin-top: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

}

.mar-left-16 {
    padding-left: 16px;
    background-color: #fff;
}

:deep(.ant-menu-item-selected) {
    color: #165DFF !important;
    font-weight: 550;
}
</style>

