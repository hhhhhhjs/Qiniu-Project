<template>
    <div class="page-bottom">
        <!-- //成员单位 -->
        <UtilsTitle :title="$t('mainPage.bottom.memberUnits')" ></UtilsTitle>
        <div class="photo-list" @mousewheel="(e: any) => onScroll(e)" id="grhscrool">
            <div class="photo" v-for="item in conpanyList">
                <!-- <img class="photo-photo"
                    src="https://s3-alpha-sig.figma.com/img/6b65/819e/c106290e7c3d3db0758a2102aabb4b0f?Expires=1691366400&Signature=YAJ00eZVZEWYvUA5sJQTvYD~np6f4VrxbInz1QyuQz4vAl-BzucRfe31JzAA7SeWGulqfqpRHIbmweo8IgoFM1b5IukbYmcR~PNra1WbMLg0ESkg~acBux0SNLvTgxjNWRif9ZmyxsFwic6PGkeO-lS1D1t7TsGNH-dvHqDsHzpAmljgE0QcxDwmiC56IrWF3DElIm5eNcIdcBRxgToaBnszFaNulijWoRR6J8jWM2q80EOBSa9BnHO81Fec~MxSfEJoNSyLjHVzGmJROjG39LHqNqc19hHl8jubitDlR2IjTW21j-ybt7~YeKFpqQLQzJeZSS1Kffm1BsArJJLP0g__&Key-Pair-Id=APKAQ4GOSFWCVNEHN3O4" /> -->
                <img class="photo-photo"
                    :src="'http://www.tangguangdi.com/zjimee-pbm/organization/company/downLoadPhoto?fileName=' + item.photo" />
                <div class="photo-name">
                    {{ item.companyName }}
                </div>
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
import UtilsTitle from '@/components/UtilsTitle/index.vue';
import { companyApi } from '@/api/company'
import type { company } from '@/api/company'
import { onMounted, ref } from 'vue';
import _  from 'lodash';
const conpanyList = ref<company[]>()

const onScroll = (e: any) => {
    const element = document.querySelector('#grhscrool') as HTMLElement
    //下面的实现的是内部元素横向滚动，前提设置好内部元素横向的滚动样式了
    e.preventDefault(); // 防止默认的滚动行为
    // 计算元素应该滚动的距离
    var dx = e.deltaY > 0 ? 100 : -100;
    // console.log('dx',dx,element );

    // 滚动元素
    element.scrollLeft += dx;
    // setInterval(()=>{
    //     element.scrollLeft += 1;
    // },10)
}
const getCompanyList = () => {
    companyApi.getCompanyList().then((res: any) => {
        if (res.success) {
            conpanyList.value = res.obj
        }
    })
}
let timer = null
const scrollAuto = () => {
    const element = document.querySelector('#grhscrool') as HTMLElement
    function SCROOLFLET0(){
        element.scrollLeft = 0
    }
    
    // 滚动元素
    timer = setInterval(() => {
        element.scrollLeft += 1.5;
        if (element.scrollLeft + element.clientWidth >= element.scrollWidth) {
            _.throttle(SCROOLFLET0,150)()
        }
    }, 15)
}
onMounted(() => {
    getCompanyList()
    scrollAuto()
})
</script>

<style lang="less" scoped>
.page-bottom {
    margin-top: 16px;
    width: 100%;
    height: 350px;
    // padding: 16px;
    padding-top: 0px;
    background-color: #fff;
    overflow: hidden;

    ::-webkit-scrollbar {
        width: 0rem !important;
        /* 纵向滚动条*/
        height: 0rem !important;
        /* 横向滚动条 */
        background-color: #fff;
    }

    .photo-list {
        height: calc(100% - 40px);
        margin: 16px;
        display: flex;
        overflow: hidden;
        overflow-x: scroll;

        .photo {
            width: 250px;
            margin: 8px;

            .photo-photo {
                width: 250px;
                height: 180px;
                // fill (不保持纵横比缩放图片,使图片完全适应)
                // contain (保持纵横比缩放图片,使图片的长边能完全显示出来)
                // cover (保持纵横比缩放图片,只保证图片的短边能完全显示出来)
                // none (保持图片宽高不变)
                // scale-down (当图片实际宽高小于所设置的图片宽高时,显示效果与none一致;否则,显示效果与contain一致)
                // object-fit: scale-down;
            }

            .photo-name {
                margin-top: 16px;
                color: var(--unnamed, #4E5969);
                text-align: center;
                font-family: PingFang SC;
                font-size: 16px;
                font-style: normal;
                font-weight: 500;
                line-height: normal;
            }
        }
    }
}</style>