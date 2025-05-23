from io import BytesIO
from typing import List, Dict
import pandas as pd
from fastapi.responses import StreamingResponse

def create_excel_file(data: List[Dict], columns: List[str]) -> StreamingResponse:
    """
    创建 Excel 文件并返回 StreamingResponse
    
    Args:
        data: 要导出的数据列表
        columns: Excel 文件的列名列表
    
    Returns:
        StreamingResponse: 包含 Excel 文件的响应对象
    """
    # 创建 DataFrame
    df = pd.DataFrame(data)
    
    # 重新排序列
    df = df[columns]
    
    # 创建 Excel 文件
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    
    # 设置文件指针到开始位置
    output.seek(0)
    
    # 返回 StreamingResponse
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=export.xlsx"}
    ) 