<!-- 预邀厂商 -->
<template>
    <div class="basicInfo" id="participateInTheProject">
        <div class="basic-item">
            <UtilsTitle :title="'参与项目'">
            </UtilsTitle>

            <div class="table-style">
                <a-button  @click="joinProject">参与项目</a-button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {excutePartake} from '@/api/ExecutePartake'
import type {partake} from '@/api/ExecutePartake'
import { getuserInfo } from '@/utils/UntilsHank';
import { message } from 'ant-design-vue';

interface props {
    propsid: string,
}
const props = defineProps<props>()
const joinProject = () => {
    const USER = getuserInfo()
    const data = <partake>{
        "companyId": USER.companyId,
        "executeId": props.propsid,
        "partake": false
    }
    excutePartake.addExecuteList(data).then((res:any)=>{
        if(res.success){
            message.success('参与项目成功')
        }
    })
}
</script>

<style lang="less" scoped>
.basicInfo {
    // height: 100%;
    margin-top: 16px;
    height: 100px;

    .basic-item {
        // padding: 16px;
        height: 100%;
        padding-top: 0px;
        background-color: #fff;

        .add-style {
            display: flex;
            width: 60px;
            height: 24px;
            justify-content: center;
            align-items: center;
            flex-shrink: 0;
            border-radius: 4px;
            border: 1px solid var(--unnamed, #2454CA);
            color: #2454CA;
        }
    }

    .table-style {
        width: 100%;
        height: 50px;
        display: flex;
        justify-content: center;
        align-items: center;
    }
}
</style>