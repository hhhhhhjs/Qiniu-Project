<template>
    <div class="page-body">
        <div class="body-left">
            <div class="body-left-top">
                <!-- 违规公告 -->
                <UtilsTitle :title="$t('mainPage.body.violationAnnouncement')" >
                </UtilsTitle>
                <div class="top-body">
                    <div v-for="item in violationAnnouncementList">
                        <div class="flex-btw top-body-main">
                            <div class="top-body-text">
                                {{ item.label }}
                            </div>
                            <div class="top-body-status">
                                {{ item.status }}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="body-left-bottom">
                <!-- 联系方式 -->
                <UtilsTitle :title="$t('mainPage.body.contact')" :remark="$t('mainPage.body.helpCenter')"></UtilsTitle>
                <div class="bottom-body">
                    <div class="flex-btw body-text">
                        <div>
                            <!-- 热线电话 -->
                            <phone-outlined class="icon-style" />
                            {{ $t('mainPage.body.hotline') }}
                        </div>
                        <div>
                            {{ orgInfo.hotLine }}
                        </div>
                    </div>

                    <div class="flex-btw body-text">
                        <div>
                            <!-- 企业邮箱 -->
                            <mail-outlined class="icon-style" />
                            {{ $t('mainPage.body.businessMailbox') }}
                        </div>
                        <div>
                            {{ orgInfo.email }}
                        </div>
                    </div>

                    <div class="flex-btw body-text">
                        <div>
                            <!-- 举报邮箱 -->
                            <safety-certificate-outlined class="icon-style" />
                            {{ $t('mainPage.body.reportEmail') }}
                        </div>
                        <div>
                            {{ orgInfo.report }}
                        </div>
                    </div>

                </div>
            </div>
        </div>
        <div class="body-right">
            <div class="white">
                <!-- 采集商城 -->
                <UtilsTitle :title="$t('mainPage.body.captureMarketplace')" :remark="$t('mainPage.utilsTitle.more')">
                </UtilsTitle>
                <div class="photo-list">
                    <div class="photo" v-for="item in productList" >
                        <div class="width80">
                            <img class="photo-photo"
                                :src="`http://www.tangguangdi.com/zjimee-pbm/fileImport/downLoadFile?fileName=${item.id}.jpg&id=${item.id}`" 
                                alt="暂无图片"/>
                            <div class="photo-price">
                                ￥{{ item.price }}
                            </div>
                            <div class="photo-description">
                                {{ item.name }}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import './bodyLeft.less'
import './bodyRight.less'
import UtilsTitle from '../../../../components/UtilsTitle/index.vue';
import { PhoneOutlined, MailOutlined, SafetyCertificateOutlined } from '@ant-design/icons-vue';
import { createFromIconfontCN } from '@ant-design/icons-vue';
import { onMounted, reactive, ref } from 'vue';
import { contactUsApi } from '../../../../api/contactUs';
import { commodityApi } from '@/api/Commodity';

const IconFont = createFromIconfontCN({
    scriptUrl: '//at.alicdn.com/t/font_8d5l8fzk5b87iudi.js',
});
const violationAnnouncementList = [
    { label: '海上风电监测算法开发项目', status: '违规类型' },
    { label: '海上风电监测算法开发项目', status: '违规类型' },
    { label: '海上风电监测算法开发项目', status: '违规类型' },
    { label: '海上风电监测算法开发项目', status: '违规类型' },
    { label: '海上风电监测算法开发项目', status: '违规类型' },
    { label: '海上风电监测算法开发项目', status: '违规类型' },
    { label: '海上风电监测算法开发项目', status: '违规类型' },
    { label: '海上风电监测算法开发项目', status: '违规类型' },
    { label: '海上风电监测算法开发项目', status: '违规类型' },
]

const contactList = [
    { label: '热线电话', svg: 'phone-outlined', text: '0571-88888888' },
    { label: '企业邮箱', svg: 'mail-outlined', text: 'jdjtzczx@163.com' },
    { label: '举报邮箱', svg: 'safety-certificate-outlined', text: 'jdjtJbzx@163.com' },
]
const photoList = [
    { src: '', price: '63.00', description: '商品简单描述商品简单描述商品简单描述商品简单描述商品简单描述' },
    { src: '', price: '63.00', description: '商品简单描述商品简单描述商品简单描述商品简单描述商品简单描述' },
    { src: '', price: '63.00', description: '商品简单描述商品简单描述商品简单描述商品简单描述商品简单描述' },
    { src: '', price: '63.00', description: '商品简单描述商品简单描述商品简单描述商品简单描述商品简单描述' },
    { src: '', price: '63.00', description: '商品简单描述商品简单描述商品简单描述商品简单描述商品简单描述' },
    { src: '', price: '63.00', description: '商品简单描述商品简单描述商品简单描述商品简单描述商品简单描述' },
    { src: '', price: '63.00', description: '商品简单描述商品简单描述商品简单描述商品简单描述商品简单描述' },
    { src: '', price: '63.00', description: '商品简单描述商品简单描述商品简单描述商品简单描述商品简单描述' },
]

const productList = ref<any>([])
const getProductList = () => {
    const page = { 
        current:1,
        size:20
    }
    commodityApi.getCommodityIndexPage(page).then((res:any) => {
        // `http://www.tangguangdi.com/zjimee-pbm/fileImport/downLoadFile?fileName=${res.obj.id}.jpg&id=${res.obj.id}`
        if (res.success) {
            productList.value = res.obj.records;
            res.obj.records.forEach((item:any)=>{
                console.log('item',item);
                // const temp_data = JSON.parse(item.commodityInfo)
                // console.log('temp_data',item.commodityInfo);
            })
        }        
    })
}

interface IOrgInfo {
    address: string;
    email: string;
    hotLine: string;
    report: string;
};
const orgInfo = reactive<IOrgInfo>({
    address: '',
    email: '',
    hotLine: '',
    report: '',
});
const getCompanyInfo = () => {
    contactUsApi({}).getCompanyInfo().then((res: any) => {
        orgInfo.address = res.obj.address
        orgInfo.email = res.obj.email
        orgInfo.hotLine = res.obj.hotLine
        orgInfo.report = res.obj.report
    })
};
onMounted(() => {
    getCompanyInfo()
    getProductList()
})
</script>

<style scoped lang="less">
.page-body {
    height: 660px;
    margin-top: 16px;
    display: flex;
}
</style>

