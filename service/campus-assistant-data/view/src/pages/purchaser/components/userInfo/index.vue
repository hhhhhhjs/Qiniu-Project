<template>
    <div class="left-user">
        <div class="left-user-msg">
            <div class="uesr-msg-phoot">
                <a-avatar class="width60">
                    <template #icon>
                        <img src="@/assets/images//human.svg">
                    </template>
                </a-avatar>
            </div>
            <div class="user-msg-text">
                <div class="text-top">                    
                    <a-dropdown>
                        <div class="text-top-name">
                            {{ user.name }}
                            <caret-down-outlined />
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
                    <!-- 已实名 -->
                    <div class="text-top-status" @click="logOff">
                        <img src="@/assets/images//Vector.svg" />
                    </div>
                </div>
                <div class="text-bottom ">
                    <span>{{ user.phone.replace(/(\d{3})\d{4}(\d{4})/, "$1****$2") }}</span>
                </div>
            </div>
        </div>
        <div class="left-user-work">
            <a-button class="work" @click="gotoRouter('purchaserInfoMaintain')">
                <div class="work-img">
                    <img src="@/assets/images//msg.svg" />
                </div>
                <div class="work-text">
                    <!-- 信息维护 -->
                    <span>信息维护</span>
                </div>
            </a-button>
            <a-button class="work" @click="gotoRouter('purchaserManage')">
                <div class="work-img">
                    <img src="@/assets/images//guanli.svg" />
                </div>
                <div class="work-text">
                    <!-- 供应商管理 -->
                    <span>供应商管理</span>
                </div>
            </a-button>
        </div>

        <ChangePwd :visible="changePwdVisible" @handle-ok="changePwdFunc"
            @handle-cancel="changePwdVisible = false"></ChangePwd>
    </div>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue'
import { getuserInfo } from '@/utils/UntilsHank'
import { useRouter } from "vue-router";
import ChangePwd from "@/components/changePwd/index.vue";
import { 
    CaretDownOutlined 
} from '@ant-design/icons-vue';
import { userApi } from '@/api/user/index';
import { storeToRefs } from 'pinia'
import { useDataStore } from '../../../../store/userStatus';
const store = useDataStore();
const { userInfo, isLogin } = storeToRefs(store);
const $router = useRouter();

const getUserData = () => {
    let userData = JSON.parse(localStorage.getItem("userInfo") as string);
    if (userData != null) {
        userInfo.value = userData;
        isLogin.value = true
    } else {
        isLogin.value = false
    }
}
const changePwdVisible = ref<boolean>(false)
const changePwdFunc = (data: any) => {
    getUserData();    
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

const gotoRouter = (routerName: string) => {
    $router.push({ name: routerName });
}

const user = ref<any>({
    name: '',
    phone: ''
})
const logOff = () => {
    $router.push({ name: "mainPage" });

    // userApi({}).logOff().then((res: any) => {
    //     if (res.succeed) {
    //         $router.push({ name: "login" });
    //     }
    // })

}

const logout = () => {
    localStorage.removeItem("userInfo");
    localStorage.removeItem("time");
    localStorage.removeItem("token");
    $router.push({ name: "login" });
};

onMounted(() => {
    user.value = getuserInfo()
})
</script>

<style scoped lang="less">
@import './index.less';
</style>