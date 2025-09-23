import { http } from "../request"

export interface ICommodityType{
    id?: string;
    orderIndex?: string; 
    parentId?: string;
    parentIds?: string;
    typeName: string;
}

export interface IPages{
    current:number;
    size:number;
}

// 供应商-商品类别
// Commodity Type Controller
export const commodityTypeApi ={
    // 供应商-商品类别新增
    postCommodityType:(data:ICommodityType)=>http.request({
        url:`supply/commodityType`,
        method:'post',
        data:data,
    }),
    // 供应商-商品类别修改
    putCommodityType:(data:ICommodityType)=>http.request({
        url:`supply/commodityType/${data.id}`,
        method:'put',
        data:data
    }),
    // 供应商-商品类别删除
    delCommodityTypeById:(id:string)=>http.request({
        url:`supply/commodityType/${id}`,
        method:'delete',
        params:{id}
    }),
    // 商品类别调整
    putCommodityTypeOrder:(data:ICommodityType)=>http.request({
        url:`supply/commodityType/order`,
        method:'put',
        params:data
    }),
    // 供应商-商品类别树
    getCommodityTypeTree:()=>http.request({
        url:`supply/commodityType/tree`,
        method:'get',
    }),
}