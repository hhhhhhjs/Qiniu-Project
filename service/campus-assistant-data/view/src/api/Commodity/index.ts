import { http } from "../request"

export interface ICommodity{
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

export interface IPages{
    current:number;
    size:number;
}

// 供应商-商品
// Commodity Controller
export const commodityApi ={
    // 供应商-商品分页
    getCommodityPage:(data:IPages)=>http.request({
        url:`supply/commodity`,
        method:'get',
        params:data
    }),
    // 供应商-商品新增
    postCommodity:(data:ICommodity)=>http.request({
        url:`supply/commodity`,
        method:'post',
        data:data,
    }),
    // 供应商-商品修改
    putCommodity:(data:ICommodity)=>http.request({
        url:`supply/commodity/${data.id}`,
        method:'put',
        data:data
    }),
    // 供应商-商品删除
    delCommodity:(id:string)=>http.request({
        url:`supply/commodity/${id}`,
        method:'delete',
    }),
    // 主页-上架商品分页
    getCommodityIndexPage:(data:IPages)=>http.request({
        url:`supply/commodity/indexPage`,
        method:'get',
        params:data
    }),
    // 供应商-商品详情
    getCommodityById:(id:string)=>http.request({
        url:`supply/commodity/info`,
        method:'get',
        params:{id}
    }),
}