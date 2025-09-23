import { http } from "../request"

export interface ISupplySocialIntegrity{
    id?:string;
    file?:Blob;
    companyId: string;
    creditType: string;// 信用类型
    evaluationYear: string;// 评价年度
    creditGrade: string;// 信用等级
    evaluationUnit: string;// 评价单位
    releaseDate: string;// 发布日期
    // fileName: string;// 证明材料
    // fileExtension: string;// 证明材料后缀
};
interface setfile{
    data:FormData;
    id:string;
}
interface editSupply{
    data:ISupplySocialIntegrity;
    id:string;
}
// 供应商-社会诚信
// Supply Social Integrity Controller
export const supplySocialIntegrityApi = {

    // 供应商-社会诚信列表
    getSupplySocialIntegrityList:()=>http.request({
        url:`supply/socialIntegrity`,
        method:'get',
    }),
    
    // 供应商-社会诚信新增
    postSupplySocialIntegrity:(formData: FormData)=>http.request({
        url:`supply/socialIntegrity`,
        method:'post',
        data:formData,
  
    }),    
    
    // 供应商-社会诚信修改
    editSupplySocialIntegrity:(data:editSupply)=>http.request({
        url:`supply/socialIntegrity/${data.id}`,
        method:'put',
        data:data.data,
        // data:data.data,
        // params:{executeId:data.executeId},
        // headers: {
        //     'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundaryyw1pDnl7NkZAzeRp'
        // }
    }),    
    
    // 供应商-社会诚信删除
    delSupplySocialIntegrity:(id:string)=>http.request({
        url:`supply/socialIntegrity/${id}`,
        method:'delete',
    }),
    
    // 供应商-社会诚信附件下载
    getSupplySocialIntegrity:(id:string)=>http.request({
        url:`purchase/socialIntegrity/downLoadFile/${id}`,
        method:'get',
        responseType: 'blob',
    }),
        // 供应商-社会诚信附件下载
        setFile:(data:setfile)=>http.request({
            url:`supply/socialIntegrity/fileImport/${data.id}`,
            method:'post',
            data:data.data,
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        }),
};