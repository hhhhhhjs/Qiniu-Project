<template>
    <div class="page_content">
        <div class="top">
            <div class="title"><span>签约商品</span></div>
            <div class="search_area">
                <SearchHeader :formList="formList" :height="'150px'" @search="search"></SearchHeader>
            </div>
        </div>
        <div class="bottom">
            <div class="search_area">
                <!-- <a-button type="primary" style="width:82px;" :icon="h(SearchOutlined)">查询</a-button>
                <a-button type="primary" style="width:82px;" ghost>上架</a-button>
                <a-button type="primary" style="width:82px;" ghost>下架</a-button>
                <a-button type="primary" style="width:82px;" ghost danger>删除</a-button> -->
                <a-button type="primary" style="width:82px;" :icon="h(PlusOutlined)" @click="addOrEdit('add')">新增</a-button>
            </div>
            <div class="search_table" id="data_result">
                <!-- <a-table :row-selection="{ selectedRowKeys: state.selectedRowKeys, onChange: onSelectChange }" -->
                <a-table :scroll="{ y: tableScrollY }" :pagination="pagination" size="middle"
                    :columns="columns" :data-source="data">
                    <template #bodyCell="{ column, text, record, index }">
                        <template v-if="column.dataIndex === 'num'">
                            {{ index + 1 }}
                        </template>
                        <template v-if="column.dataIndex === 'status'">
                            <span>{{ record.status?"已上架":"未上架" }}</span>
                        </template>
                        <template v-if="column.dataIndex === 'operate'">
                            <div class="operate-style">
                                <!-- 下架 -->
                                <a-button type="link" v-if="record.status" @click="shelfOrTakedown('down', record)" class="btn">
                                    下架
                                </a-button>
                                <!-- 上架 -->
                                <a-button type="link" v-else @click="shelfOrTakedown('up', record)" class="btn">
                                    上架
                                </a-button>
                                <!-- 编辑 -->
                                <a-button type="link" @click="addOrEdit('edit', record.id)" class="btn">
                                    {{ $t('placeholder.edit') }}
                                </a-button>
                                <!-- 删除 -->
                                <!-- <a-button type="link" danger @click="delColumns6ById(record.id)"> -->
                                <a-button type="link" danger @click="openConfirm(record.id)" class="btn">
                                    {{ $t('placeholder.delete') }}
                                </a-button>
                            </div>
                        </template>
                    </template>
                </a-table>
            </div>
        </div>

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
import { commodityApi } from "@/api/Commodity/index";
import { commodityTypeApi } from '@/api/CommodityType';

const $route = useRoute();
const $router = useRouter();

interface DataType {
    commodityAttribute:string;//商品属性
    commodityInfo:string;//商品详情
    commodityType:string;//商品类别id
    // companyId:string;//企业id
    contacts:string;//联系人
    // createTime:string;//创建时间
    id?:string;//主键id
    name:string;//商品名称
    phone:string;//联系方式
    photo?:string;//
    price:number|null;//协议价格
    status:boolean;//是否上架
}

const columns = [
    {
        title: '商品编号',
        dataIndex: 'id',
        key: 'id',
        align: 'center',
    },
    {
        title: '商品标题',
        dataIndex: 'name',
        key: 'name',
        align: 'center',
    },
    {
        title: '商品类目',
        dataIndex: 'typeName',
        key: 'typeName',
        align: 'center',
    },
    {
        title: '商品规格',
        dataIndex: 'commodityAttribute',
        key: 'commodityAttribute',
        align: 'center',
    },
    {
        title: '价格',
        dataIndex: 'price',
        key: 'price',
        align: 'center',
        width: 120,
    },
    {
        title: '状态',
        dataIndex: 'status',
        key: 'status',
        align: 'center',
        width: 120,
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
        getProductList();
    }),
})
const pages = reactive<any>({
    size: 10,
    current: 1,
    name:'',
    commodityType:'',
    commodityAttribute:'',
    status:null,
})

const data = ref<DataType[]>([]);


// 新增/删除 商品
const addOrEdit = (type:string, id?:any) => {
    if (type == 'add') {
        $router.push({name: 'addProduct'})        
    } else {
        $router.push({name: 'editProduct', params: { id: id }})    
    }
}
// 上架/下架 商品
const shelfOrTakedown = (type:string, record:any) => {
    let tempDate = JSON.parse(JSON.stringify(record))
    if (type == 'up') {
        tempDate.status = true;
    } else {
        tempDate.status = false;        
    }
    commodityApi.putCommodity(tempDate).then((res:any) => {
        if (res.success) {
            getProductList();
        }
    })
}
const delProductById = (id:string) => {
    commodityApi.delCommodity(id).then((res:any) => {
        if (res.success) {
            getProductList();
        }
    })    
}

//删除
const delFileId = ref<string>('');
const delRef = ref<any>();
const delData = () => {
  delProductById(delFileId.value);
  delRef.value.close()
}
const openConfirm = (id: any) => {
  delFileId.value = id;
  delRef.value.open();
}

const getProductList = () => {
    commodityApi.getCommodityPage(pages).then((res:any) => {
        if (res.success) {
            data.value = res.obj.records;
        }        
    })
}

// 获取商品类型树
const getCommodityType = () => {
    commodityTypeApi.getCommodityTypeTree().then((res:any) => {
        if (res.success) {
            formList.value[1].options = res.obj;
        }
    })
};

const formList = ref<any>([
    { type: 'a-input', title: '商品标题', bind: 'name', span: 12 },
    { type: 'a-select-diy', title: '商品类目', bind: 'commodityType', span: 12, label:'typeName', value:'id', options: [] },
    { type: 'a-input', title: '商品规格', bind: 'commodityAttribute', span: 12 },
    { type: 'a-select', title: '商品状态', bind: 'status', span: 12, options: [{value: true, label: '已上架'}, {value: false,label: '未上架'}]},
])
const search = (formState: any) => {
    pages.size = 10
    pages.current = 1
    pages.name = formState.name
    pages.commodityType = formState.commodityType
    pages.commodityAttribute = formState.commodityAttribute
    pages.status = formState.status
    getProductList()
}

const tableScrollY = ref<number>(0)
const resizeScrollY = () => {
  let dataResultHeight = (document.getElementById('data_result') as HTMLElement).offsetHeight;
  tableScrollY.value = dataResultHeight - 140
};
onMounted(() => {
  resizeScrollY()
  window.addEventListener("resize", resizeScrollY)
  getProductList()
  getCommodityType()
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
