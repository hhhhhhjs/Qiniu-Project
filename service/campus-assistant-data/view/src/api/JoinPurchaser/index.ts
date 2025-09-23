import { http } from "../request"

export interface IJoinPurchaserApi{
    id:string;
}

// 供应商加盟采购商
// Join Purchaser Controller
export const joinPurchaserApi ={
    // 申请中和已通过的供应商分页
    getJoinPurchaserPage:(data:any)=>http.request({
        url:`supply/joinPurchaser`,
        method:'get',
        params:data,
    }),

    // 供应商加盟采购商新增
    postJoinPurchaser:(purchaserId:string)=>http.request({
        url:`supply/joinPurchaser`,
        method:'post',
        data:purchaserId,
    }),
    
    // 采购商通过供应商加盟
    putJoinPurchaser:(id:string)=>http.request({
        url:`supply/joinPurchaser/${id}`,
        method:'put',
    }),

    // 采购商拒绝供应商加盟
    delJoinPurchaser:(id:string)=>http.request({
        url:`supply/joinPurchaser/${id}`,
        method:'delete',
    }),
    
    // 供应商加盟采购商已通过列表    
    getJoinPurchaserList:(status:string)=>http.request({
        url:`supply/joinPurchaser/list`,
        method:'get',
        params:{status}
    }),
}