<template>
    <div class="body">
        <!-- 用户信息/招标信息 -->
        <div class="body-left">
            <!-- 用户信息 -->
            <div class="left-user">
                <div class="left-user-msg">
                    <div class="uesr-msg-phoot">
                        <a-avatar class="width60" v-if="isLogin">
                            <template #icon>
                                <img src="../../../../assets/images/user_logined.svg">
                            </template>
                        </a-avatar>
                        <a-avatar class="width60" style="background: #F6F6F6;" v-else>
                            <template #icon>
                                <img src="../../../../assets/images/user_unlogined.svg">
                            </template>
                        </a-avatar>
                    </div>
                    <div class="user-msg-text">
                        <div class="text-top">
                            <a-dropdown class="userInfo_name" v-if="isLogin">
                                <div class="langs">
                                    <span class="lang_title">
                                        {{ userInfo.name }}
                                        <caret-down-outlined />
                                    </span>
                                </div>
                                <template #overlay>
                                    <a-menu>
                                        <a-menu-item>
                                            <a @click="changePwdVisible = true;" style="display: flex;justify-content: center;">修改密码</a>
                                        </a-menu-item>
                                        <a-menu-item>
                                            <a @click="logout" style="display: flex;justify-content: center;">退出账号</a>
                                        </a-menu-item>
                                    </a-menu>
                                </template>
                            </a-dropdown>
                            <div class="text-top-name" v-else @click="gotoRouter('login')">
                                点击登录
                            </div>
                            <!-- 已实名 -->
                            <!-- <div class="text-top-status">
                                {{ $t('mainPage.header.realName') }}
                            </div> -->
                        </div>
                        <div class="text-bottom text-omit" v-if="isLogin" :title="userInfo.companyName">
                            {{ userInfo.companyName }}
                        </div>
                        <div class="text-bottom" v-else @click="registerDialogVisible = true;">
                            无账号，点击注册。
                        </div>
                    </div>
                </div>
                <div class="left-user-work">
                    <a-button class="work1" :style="isLogin && userInfo.supplier ? '' : 'background: var(--unnamed, #86909C);'"
                        @click="gotoRouter('supplierManager')" :disabled="!isLogin || !userInfo.supplier">
                        <div class="work-text">
                            <!-- 供应商工作台 -->
                            {{ $t('mainPage.header.purchaserWorkbench') }}
                        </div>
                        <div class="work-img">
                            <img src="../../../../assets/images/purchaser.svg" alt="">
                        </div>
                    </a-button>
                    <a-button class="work2" :style="isLogin && userInfo.purchaser ? '' : 'background: var(--unnamed, #86909C);'"
                        @click="gotoRouter('purchaser')" :disabled="!isLogin || !userInfo.purchaser">
                        <div class="work-text">
                            <!-- 采购商工作台 -->
                            {{ $t('mainPage.header.buyerSWorkbench') }}
                        </div>
                        <div class="work-img">
                            <img src="../../../../assets/images/purchaser.svg" alt="">
                        </div>
                    </a-button>
                </div>
            </div>
            <!-- 中标成功公示 -->
            <div class="left-winning">
                <UtilsTitle :title="$TT('mainPage.header.winningBidTransactionPublicity')"
                    :remark="$TT('mainPage.utilsTitle.more')" @handleToMoreEmit="handleToMore('4')">
                </UtilsTitle>
                <div class="winning-body-list">
                    <div v-for="item in winningBidderList" class="winning-body">
                        <div class="body-time-status flex-btw">
                            <div class="body-time">
                                {{ item.endDate }}
                            </div>
                            <div class="body-status">
                                <!-- 中标 -->
                                <!-- <div v-if="item.purchaseStatus == 0" class="body-status-win">
                                    {{ $t('mainPage.header.winningBidder')}}
                                </div> -->
                                <!-- 成功 -->
                                <!-- <div v-if="item.purchaseStatus == 3" class="body-status-success">
                                    {{ $t('mainPage.header.succeed') }}
                                </div> -->
                                <div class="body-status-success">
                                    <!-- // "0""招投标"
                                    // "1""竞争性谈判"
                                    // "2""单一采购来源"
                                    // "3""询比价" -->
                                    <span v-if="item.purchaseWay == 0">招投标</span>
                                    <span v-else-if="item.purchaseWay == 1">竞争性谈判</span>
                                    <span v-else-if="item.purchaseWay == 2">单一采购来源</span>
                                    <span v-else>询比价</span>
                                </div>
                            </div>
                        </div>

                        <div class="body-text text-omit">
                            {{ item.projectName }}
                        </div>

                        <div class="body-unit">
                            <!-- 单位 -->
                            <div>{{ $t('mainPage.header.unit') }}:机电设计研究院有限公司</div>
                        </div>
                        <!-- 下划线 -->
                        <svg xmlns="http://www.w3.org/2000/svg" width="349" height="2" viewBox="0 0 349 2" fill="none">
                            <path d="M0 1H349" stroke="#F1F2F4" stroke-dasharray="4 4" />
                        </svg>
                    </div>
                </div>
            </div>
        </div>
        <!-- 招标公告等 -->
        <div class="body-right">
            <!-- 招标公告 -->
            <div class="body-right-top">
                <UtilsTitle :title="$TT('mainPage.header.tenderAnnouncement')" :remark="$TT('mainPage.utilsTitle.more')" @handleToMoreEmit="handleToMore('0')">
                </UtilsTitle>
                <div class="table-padding">
                    <a-table :dataSource="dataSource0" :columns="columns0" :pagination="false" :size="'large'"
                        class="ant-table-striped" :row-class-name="(record: any, index: any) => {
                            return (index - 0) % 2 == 1 ? 'bg-f' : 'bg-white'
                        }" :customRow="(record:any)=> handleCustomRow(record, '招标公告')"/>
                </div>
            </div>
            <!-- 竞争性谈判公示和询比价公示 -->
            <div class="body-right-bottom flex-btw">
                <div class="right-bottom-a">
                    <UtilsTitle :title="$TT('mainPage.header.competitiveNegotiationPublicity')"
                        :remark="$TT('mainPage.utilsTitle.more')" @handleToMoreEmit="handleToMore('1')"></UtilsTitle>
                    <div class="table-padding">
                        <a-table :dataSource="dataSource1" :columns="columns1" :pagination="false" :size="'large'" :customRow="(record:any)=> handleCustomRow(record, '竞争性谈判公示')"/>
                    </div>
                </div>
                <div class="right-bottom-b ">
                    <UtilsTitle :title="$TT('mainPage.header.inquiryAndPriceComparisonPublicity')"
                        :remark="$TT('mainPage.utilsTitle.more')" @handleToMoreEmit="handleToMore('3')"></UtilsTitle>
                    <div class="table-padding">
                        <a-table :dataSource="dataSource3" :columns="columns3" :pagination="false" :size="'large'" :customRow="(record:any)=> handleCustomRow(record, '询比价公示')"/>
                    </div>
                </div>
            </div>
        </div>
        <RegisterDialog :visible="registerDialogVisible" @handle-ok="registerAccount"
            @handle-cancel="registerDialogVisible = false"></RegisterDialog>
        <ChangePwd :visible="changePwdVisible" @handle-ok="changePwdFunc"
            @handle-cancel="changePwdVisible = false"></ChangePwd>

        <IndexListToInfoVue ref="indexToInfoRef" />
    </div>
</template>

<script setup lang="ts">
import './headerRight.less'
import RegisterDialog from "@/components/register/registerDialog.vue";
import ChangePwd from "@/components/changePwd/index.vue";
import UtilsTitle from '@/components/UtilsTitle/index.vue';
import IndexListToInfoVue from '@/components/IndexListToInfo/index.vue'
import { useRouter } from "vue-router";
import { inject, onMounted, ref } from 'vue';
import {
    CaretDownOutlined,
} from "@ant-design/icons-vue";
import { executeApi } from '@/api/Execute/index';
import { storeToRefs } from 'pinia'
import { useDataStore } from '../../../../store/userStatus';
import { userApi } from '@/api/user/index';
const store = useDataStore();
const { userInfo, isLogin } = storeToRefs(store);

const $TT: any = inject('TT')
const $router = useRouter();

const registerDialogVisible = ref<boolean>(false)
const registerAccount = (data: any) => {
    userApi(data).postUserRegister().then((res: any) => {
        if (res.success) {
            registerDialogVisible.value = false;
            localStorage.setItem("token", res.obj);
            localStorage.setItem('time', Date.now() + '')

            userApi({}).getUserInfo().then((res: any) => {
                if (res.success) {
                    localStorage.setItem("userInfo", JSON.stringify(res.obj));
                    userInfo.value = res.obj;
                    isLogin.value = true
                    $router.push({ name: "mainPage" });
                }
            });
        }
    })
}

const changePwdVisible = ref<boolean>(false)
const changePwdFunc = (data: any) => {
    getUserInfo();    
    const changePwdData = {
        "id":userInfo.value.id,
        "newPassword": data.newPassword,
        "oldPassword": data.password,
    };
    userApi(changePwdData).changeUserPwd().then((res:any) => {
        if (res.success) {
            changePwdVisible.value = false;
            logout();
        }        
    });    
}

const winningBidderList = ref<any>([])

const dataSource0 = ref<any>([])
const columns0 = [
    {
        title: $TT('mainPage.header.itemNumber'),//项目编号
        align: 'center',
        dataIndex: 'number',
        key: 'number',
    },
    {
        title: $TT('mainPage.header.projectName'),//项目名称
        align: 'center',
        dataIndex: 'projectName',
        key: 'projectName',
    },
    {
        title: $TT('mainPage.header.procurementMethods'),//采购方式
        align: 'center',
        dataIndex: 'purchaseWay',
        key: 'purchaseWay',
    },
    {
        title: $TT('mainPage.header.purchasingUnit'),//采购单位
        align: 'center',
        dataIndex: 'companyName',
        key: 'companyName',
    },
    {
        title: $TT('mainPage.header.releaseTime'),//发布时间
        align: 'center',
        dataIndex: 'startDate',
        key: 'startDate',
    },
    {
        title: $TT('mainPage.header.deadline'),//截止时间
        align: 'center',
        dataIndex: 'endDate',
        key: 'endDate',
    },
    {
        title: $TT('mainPage.header.timeRemaining'),//剩余时长
        align: 'center',
        dataIndex: 'timeRemaining',
        key: 'timeRemaining',
    },

]

const dataSource1 = ref<any>([])
const columns1 = [
    {
        title: $TT('mainPage.header.projectName'),//项目名称
        align: 'center',
        dataIndex: 'projectName',
        key: 'projectName',
    },
    {
        title: $TT('mainPage.header.timeRemaining'),//剩余时长
        align: 'center',
        dataIndex: 'timeRemaining',
        key: 'timeRemaining',
    },
    {
        title: $TT('mainPage.header.deadline'),//截止时间
        align: 'center',
        dataIndex: 'endDate',
        key: 'endDate',
    },
]

const dataSource3 = ref<any>([])
const columns3 = [
    {
        title: $TT('mainPage.header.projectName'),//项目名称
        dataIndex: 'projectName',
        key: 'projectName',
        align: 'center',
    },
    {
        title: $TT('mainPage.header.timeRemaining'),//剩余时长
        dataIndex: 'timeRemaining',
        align: 'center',
        key: 'timeRemaining',
    },
    {
        title: $TT('mainPage.header.deadline'),//截止时间
        align: 'center',
        dataIndex: 'endDate',
        key: 'endDate',
    },
]

const gotoRouter = (urlName: string) => {
    $router.push({ name: urlName });
}

interface IUserInfo {
    email: string;
    companyId: string;
    companyName: string;
    department: string;
    duty: string;
    id: string;
    name: string;
    phone: string;
}
// const userInfo = ref<IUserInfo>({
//     email: '',
//     companyId: '',
//     companyName: '',
//     department: '',
//     duty: '',
//     id: '',
//     name: '',
//     phone: '',
// })
const getUserInfo = () => {
    let userData = JSON.parse(localStorage.getItem("userInfo") as string);
    if (userData != null) {
        userInfo.value = userData;
        isLogin.value = true
    } else {
        isLogin.value = false
    }
}

// "0""招投标"
// "1""竞争性谈判"
// "2""单一采购来源"
// "3""询比价"
const getAnnouncementData = (size: number, purchaseWay: number) => {
    return new Promise((resolve, reject) => {
        const data = {
            current: 1,
            size: size,
            purchaseWay: purchaseWay,
        }
        executeApi.getExecuteIndexListPage(data).then((res: any) => {
            if (res.success) {
                res.obj.records.forEach(async (item: any) => {
                    item['timeRemaining'] = await timeRemainingFunc(item.startDate, item.endDate)
                    switch (Number(item['purchaseWay'])) {
                        case 1: item['purchaseWay'] = '竞争性谈判';
                            break;
                        case 2: item['purchaseWay'] = '单一采购来源';
                            break;
                        case 3: item['purchaseWay'] = '询比价';
                            break;
                        default: item['purchaseWay'] = '招投标';
                            break;
                    }
                });
                resolve(res.obj.records);
            } else {
                reject('error');
            }
        })
    })
}
// 中标&成交公示
interface IPages {
    current: number;
    size: number;
}
const getExecutePublicityData = (pages: IPages) => {
    return new Promise((resolve, reject) => {
        executeApi.getExecutePublicityPage(pages).then((res: any) => {
            if (res.success) {
                resolve(res.obj.records);
            } else {
                reject('error');
            }
        })
    })
}

const logout = () => {
    localStorage.removeItem("userInfo");
    localStorage.removeItem("time");
    localStorage.removeItem("token");
    $router.push({ name: "login" });
};

const timeRemainingFunc = (startDate: string, endDate: string) => {
    // 定义两个日期
    let s_date = new Date(startDate);
    let e_date = new Date(endDate);
    // 计算两个日期之间的毫秒数差异
    let timeDiff = e_date.getTime() - s_date.getTime();
    // 将毫秒数转换为天数和小时数
    let days = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
    let hours = Math.floor((timeDiff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    // 格式化输出
    let result = days + "天" + hours + "小时";

    return result;
}

const getUserInfoFromApi = () => {
    userApi({}).getUserInfo().then((res: any) => {
        if (res.success) {
            localStorage.setItem("userInfo", JSON.stringify(res.obj));
            userInfo.value = res.obj;
            isLogin.value = true
            $router.push({ name: "mainPage" });
        }
    });
};
onMounted(async () => {
    getUserInfoFromApi();
    // "0""招投标"
    // "1""竞争性谈判"
    // // "2""单一采购来源"
    // "3""询比价"
    dataSource0.value = await getAnnouncementData(6, 0);
    dataSource1.value = await getAnnouncementData(3, 1);
    dataSource3.value = await getAnnouncementData(3, 3);
    winningBidderList.value = await getExecutePublicityData({ current: 1, size: 5 })
})
const indexToInfoRef = ref()
const handleCustomRow = (record:any, title:string) => {
return {
  onClick: (e:any)=> { 
      indexToInfoRef.value.initData(record.id, title)
  }
  }
}
const handleToMore = (id:string) => {
  $router.push({name: 'moreInfo',query: {id}})
}
</script>

<style lang="less" scoped>
@import url('./headerLft.less');

.body {
    height: 812px;
    width: 100%;
    display: flex;
}

.width60 {
    width: 58px;
    height: 58px;
}
</style>
@/api/Execute/index