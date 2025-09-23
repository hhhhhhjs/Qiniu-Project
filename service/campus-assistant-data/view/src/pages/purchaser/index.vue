<template>
    <div class="purchaser">
        <div class="purchaser-left">
                <User></User>
                <Tree></Tree>
        </div>

        <div class="purchaser-right">
            <router-view></router-view>
        </div>
    </div>
</template>

<script setup lang="ts">
import Tree from './components/tree/index.vue'
import User from './components/userInfo/index.vue'

</script>

<style scoped lang="less">
.purchaser {
    background-color: '#F7F8F9';
    width: 100%;
    height: 100%;
    // overflow-y: auto;
    display: flex;
    overflow: hidden;
    .purchaser-left {
        width: 308px;
        margin-right: 16px;
        height: 100%;
        background-color: #fff;
    }

    .purchaser-right {
        width: calc(100% - 324px);
        height: 100%;
    }
}
</style>