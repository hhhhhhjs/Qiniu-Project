<template>
    <div class="page-content">
        <div class="page_left">
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
                            <div class="text-top-status" @click="gotoRouter('mainPage')">
                                <img src="@/assets/images//Vector.svg" />
                            </div>
                        </div>
                        <div class="text-bottom ">
                            <span>{{ user.phone.replace(/(\d{3})\d{4}(\d{4})/, "$1****$2") }}</span>
                        </div>
                    </div>
                </div>
                <div class="left-user-work">
                    <a-button class="work" @click="gotoRouter('supplierInfoMaintain')">
                        <div class="work-img">
                            <img src="@/assets/images//msg.svg" />
                        </div>
                        <div class="work-text">
                            <!-- 信息维护 -->
                            <span>信息维护</span>
                        </div>
                    </a-button>
                    <a-button class="work" :disabled="!userInfo.purchaser && userInfo.supplierStatus !== '3'" @click="gotoRouter('supplierEnterpriseStay')">
                        <div class="work-img">
                            <img src="@/assets/images//guanli.svg" />
                        </div>
                        <div class="work-text">
                            <!-- 入驻企业 -->
                            <span>入驻企业</span>
                        </div>
                    </a-button>
                </div>
            </div>
            <div class="tree-style">
                <a-directory-tree v-model:selectedKeys="selectedKeys" :tree-data="treeData" show-icon default-expand-all
                    @select="treeSelect" v-model:expandedKeys="expandedKeys">
                    <template #switcherIcon="{ switcherCls }"><down-outlined :class="switcherCls" /></template>
                    <template #icon="{ key, selected }">
                        <template v-if="titleList[0]==key">
                            <div class="shop-car-style">
                                <img src="@/assets/images//project.svg">
                            </div>
                        </template>
                    </template>
                </a-directory-tree>
            </div>
        </div>
        <div class="page_right">
            <router-view></router-view>
        </div>

        <ChangePwd :visible="changePwdVisible" @handle-ok="changePwdFunc"
            @handle-cancel="changePwdVisible = false"></ChangePwd>
    </div>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue';
import ChangePwd from "@/components/changePwd/index.vue";
import { 
    DownOutlined,
    CaretDownOutlined 
} from '@ant-design/icons-vue';
import { useRoute,useRouter } from "vue-router";
import { getuserInfo } from '@/utils/UntilsHank';
import { userMenuApi } from '@/api/userMenu'
import type { getTreeObj } from '@/api/userMenu';
import { userApi } from '@/api/user/index';
import { storeToRefs } from 'pinia'
import { useDataStore } from '@/store/userStatus';
const store = useDataStore();
const { userInfo, isLogin } = storeToRefs(store);
const $router = useRouter();
const $route = useRoute()

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


// 用户信息
const user = ref<any>({
    name: '',
    phone: ''
})
const gotoRouter = (routerName: string) => {
    if (routerName == 'supplierEnterpriseStay' || routerName == 'supplierInfoMaintain') {
        selectedKeys.value.length = 0;
    }
    $router.push({ name: routerName });
}


// 树形结构
const treeData: any = ref([
])
const treeSelect = (selectedKeys: any, e: any) => {
    const temp_data = e.node.dataRef
    const name = temp_data.name
    $router.push({ name });
}
const selectedKeys = ref(['0']);
const expandedKeys = ref<any>([])
const titleList = ref<string[]>([])
const getTreeMenu = () => {
    const data: getTreeObj = {
        type: '0',
        user: localStorage.getItem('token')
    }
    let nowPathKey = $route.path.split('/').at(-1)
    let isFlushed = false
    userMenuApi.getMenuTree(data).then((res: any) => {
        if (res.success) {
            let temp_treeData: any = []
            res.obj.forEach((item: any, index: string) => {
                let tree_children: any = []
                item.children.forEach((ele: any, index2: string) => {
                    const children_obj = {
                        key: ele.id,
                        title: ele.menuName,
                        name: ele.router
                    }
                    tree_children.push(children_obj)
                    //刷新后菜单自动定位到当前路由对应的位置
                    if (nowPathKey === ele.router) {
                        isFlushed = true
                        selectedKeys.value = [ele.id]
                        expandedKeys.value = [item.id]
                    }
                })
                let temp_tree = {
                    key: item.id,
                    title: item.menuName,
                    children: tree_children
                }
                titleList.value.push(item.id)
                temp_treeData.push(temp_tree)
            })
            treeData.value = temp_treeData
            //是否展开第一项
            if (!isFlushed) {
                selectedKeys.value = [temp_treeData[0].children[0].key]
                expandedKeys.value = [temp_treeData[0].key]
            }
        }
    })
}

const logout = () => {
    localStorage.removeItem("userInfo");
    localStorage.removeItem("time");
    localStorage.removeItem("token");
    $router.push({ name: "login" });
};

onMounted(() => {
    getTreeMenu()
    user.value = getuserInfo()

})
</script>

<style scoped lang="less">
.page-content {
    width: 100%;
    height: 100%;
    background-color: '#F7F8F9';
    display: flex;
    overflow: hidden;
}

.page_left {
    width: 308px;
    margin-right: 16px;
    height: 100%;
    background-color: #fff;
}

.page_right {
    width: calc(100% - 324px);
    height: 100%;
    // background-color: #fff;
}

.tree-style {
    padding: 16px 32px;
    background-color: #fff;
    height: 600px;
    width: 308px;
}

:deep(.ant-tree-iconEle) {
    margin-right: 8px;
}

:deep(.ant-tree-title) {
    height: 48px;
    line-height: 48px;
    // font-size: 20px;
    width: calc(100% - 25px) !important;
    display: flex;
    width: 269px;
    height: 48px;
    align-items: center;
    flex-shrink: 0;
}

:deep(.ant-tree-node-content-wrapper) {
    display: flex;
}

:deep(.ant-tree-treenode-selected) {
    span {
        color: var(--unnamed, #2454CA) !important;
    }
}

:deep(.ant-tree-switcher) {
    height: 48px;
    line-height: 48px;
}


:deep(.ant-tree-switcher-noop) {
    margin-right: 8px;
}

:deep(.ant-tree-treenode-selected::before) {
    background-color: #F5F9FC !important;
}


.left-user {
    padding: 16px;
    width: 308px;
    padding-top: 32px;
    height: 180px;
    background-color: #fff;
    border-bottom: dotted 1px #F1F2F4;

    .left-user-msg {
        width: 100%;
        display: flex;
        justify-content: space-between;

        .uesr-msg-phoot {
            width: 60px;
            height: 60px;

            .width60 {
                background: #D6E2FF;
                height: 100%;
                width: 100%;
            }
        }

        .user-msg-text {
            width: calc(100% - 76px);

            .text-top {
                display: flex;
                justify-content: space-between;
                align-items: center;

                .text-top-name {
                    font-weight: 550;
                    font-size: 20px;
                    margin-top: 2px;
                }

                .text-top-status {
                    cursor: pointer;
                    // background-color: #cff7d3;
                    // color: #00B42A;
                    padding: 8px;
                    font-size: 12px;
                    font-weight: 600;

                    img {
                        width: 12px;
                        height: 12px;
                    }
                }
            }

            .text-bottom {
                font-size: 16px;
                margin-top: 10px;
                color: #999999;
            }
        }
    }

    .left-user-work {
        margin-top: 24px;
        display: flex;

        .work {
            height: 40px;
            display: flex;
            align-items: center;
            padding-left: 16px;
            padding-right: 16px;
            gap: 8px;
            flex: 1;
            align-self: stretch;
            border-radius: 4px;
            background: #F7F8F9;
            margin-right: 16px;
            border: 0;

            .work-text {
                color: var(--unnamed, #4E5969);
                font-family: PingFang SC;
                font-size: 16px;
                font-style: normal;
                font-weight: 400;
                line-height: 16px;
                /* 100% */
            }

            .work-img {
                margin-right: 1px;
            }
        }
    }
}

.treeItem {
    display: inline-flex;
    align-items: center;
    justify-content: space-between;

    .treeText {
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
    }

    .treeBtn {
        display: none;
    }

    .treeNum {
        display: inline-block;
        color: #8d99a5;
        font-size: 14px;
        text-align: right;
        margin-right: 5px;
    }
}

.shop-car-style {
    height: 48px;
    line-height: 48px;
}
</style>