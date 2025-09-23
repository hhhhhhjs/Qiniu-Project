import { http } from "../request"

export interface ISupplyPatentTechnology{
    id?:string;
    companyId: string;
    inventName: string;// 发明名称
    patentType: string;// 专利类型
    lawStatus: string;// 法律状态
    applyNo: string;// 申请号
    applyDate: string;// 申请日期
    openNo: string;// 公开(公告)号
    openDate: string;// 公开(公告)日期
    inventor: string;// 发明人
};

// 供应商-专利技术
// Supply Patent Technology Controller
export const supplyPatentTechnologyApi = {
    // 供应商-专利技术列表
    getSupplyPatentTechnology:()=>http.request({
        url:`supply/patentTechnology`,
        method:'get',
    }),
    // 供应商-专利技术新增
    postSupplyPatentTechnology:(data:ISupplyPatentTechnology)=>http.request({
        url:`supply/patentTechnology`,
        method:'post',
        data:data,
    }),
    
    // 供应商-专利技术修改
    editSupplyPatentTechnology:(data:ISupplyPatentTechnology)=>http.request({
        url:`supply/patentTechnology/${data.id}`,
        method:'put',
        data:data
    }),
    
    // 供应商-专利技术删除
    delSupplyPatentTechnology:(id:string)=>http.request({
        url:`supply/patentTechnology/${id}`,
        method:'delete',
    }),
};