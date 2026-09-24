# SupportLens - 工单分析与数据看板

基于 Next.js + FastAPI 的工单数据分析系统。支持上传 CSV 工单数据，自动分类和优先级判断，并通过 Dashboard 展示统计结果。

## 功能特性

- 上传 CSV 工单数据
- 自动工单分类（Billing / Technical / Account / Feature Request / Other）
- 自动优先级判断（Low / Medium / High / Urgent）
- Dashboard 数据看板：工单总数、未分析数量、分类分布、优先级分布

## 技术栈

- 前端：Next.js、TypeScript、Tailwind CSS
- 后端：FastAPI、Python
- 部署：Vercel（前端）、Render（后端）

## 目录结构


.
├── frontend/ # Next.js 前端
│ ├── app/
│ │ ├── dashboard/ # Dashboard 页面
│ │ └── page.tsx # 首页
│ └── package.json
├── backend/ # FastAPI 后端
│ ├── main.py # 主应用
│ ├── requirements.txt
│ └── ...
└── README.md


## 本地开发

### 1. 启动后端

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

后端默认运行在 http://127.0.0.1:8000。

2. 启动前端
cd frontend
npm install

创建 frontend/.env.local：

NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000

启动前端：

npm run dev

前端默认运行在 http://localhost:3000。

部署说明
后端部署到 Render

将代码推送到 GitHub

在 Render 创建 Web Service，连接仓库

构建命令：pip install -r requirements.txt

启动命令：uvicorn main:app --host 0.0.0.0 --port $PORT

前端部署到 Vercel

将代码推送到 GitHub

在 Vercel 导入项目，framework 选择 Next.js

配置环境变量（见下方）

环境变量
Vercel 环境变量
变量名	值	说明
NEXT_PUBLIC_API_BASE_URL	https://supportlens-api-2x2i.onrender.com	线上后端地址，前端构建时注入
本地环境变量（不提交到 Git）
变量名	值	说明
NEXT_PUBLIC_API_BASE_URL	http://127.0.0.1:8000	本地后端地址
API 接口
方法	路径	说明
GET	/api/tickets/stats	获取工单统计信息
POST	/api/tickets/upload	上传 CSV 工单数据
示例：获取统计信息
curl https://supportlens-api-2x2i.onrender.com/api/tickets/stats

返回示例：
{
  "total": 100,
  "unanalyzed": 20,
  "by_category": {
    "billing": 40,
    "technical": 30
  },
  "by_priority": {
    "high": 10,
    "low": 50
  }
}
线上地址

前端：https://supportlens-gold.vercel.app

后端：https://supportlens-api-2x2i.onrender.com

备注

本地 .env.local 文件不要提交到 GitHub

修改 Vercel 环境变量后，需要重新部署前端才会生效


---

### 几个关键点

1. **本地地址写 `127.0.0.1:8000` 没问题**，但要在「部署说明」和「环境变量」里明确区分「本地」和「线上」。
2. **`.env.local` 一定不要提交到 GitHub**，在 README 中注明即可。
3. API 接口部分如果你还有别的接口（比如上传），根据实际情况补充。
4. 线上地址要写真实可访问的地址。