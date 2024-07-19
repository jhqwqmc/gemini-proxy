import os
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源的请求
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有HTTP头部
)

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(request: Request, path: str):
    method = request.method
    url = f'https://generativelanguage.googleapis.com/{path}'  # 目标API的URL

    # 获取并保留原始请求的头部
    headers = {k: v for k, v in request.headers.items() if k.lower() not in ['host', 'content-length']}
    # 获取请求体和查询参数
    data = await request.body() if method in ['POST', 'PUT'] else None
    params = dict(request.query_params)

    async with httpx.AsyncClient() as client:
        response = await client.request(
            method,
            url,
            headers=headers,
            params=params,
            data=data
        )

    # 返回目标API的响应
    return Response(
        content=response.content,  # 使用 response.content 以原始字节流返回
        status_code=response.status_code,
        headers=dict(response.headers)  # 返回目标API的头部信息
    )

if __name__ == "__main__":
    import uvicorn

    # 读取环境变量PORT，如果不存在则使用3000
    port = int(os.getenv("PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="debug")
