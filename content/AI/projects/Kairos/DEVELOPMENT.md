# Kairos App 开发指南

## 项目简介
Kairos 是一款用于记录觉察、心情、灵感和反思的应用程序，帮助用户更好地了解自己，实现个人成长。

## 技术栈
- **前端**: React + Vite
- **后端**: Node.js + Express + MongoDB
- **样式**: CSS3
- **日期处理**: date-fns

## 项目结构
```
Kairos-app/
├── src/                    # 前端源代码
│   ├── components/         # React组件
│   ├── pages/             # 页面组件
│   ├── services/          # API服务
│   ├── styles/            # 样式文件
│   └── utils/             # 工具函数
├── backend/               # 后端代码
│   ├── models/            # 数据模型
│   ├── routes/            # API路由
│   ├── controllers/       # 控制器（预留）
│   ├── middleware/        # 中间件（预留）
│   └── config/            # 配置文件（预留）
├── public/                # 静态资源
├── assets/                # 图片和图标
└── docs/                  # 文档
```

## 快速开始

### 1. 安装依赖
```bash
# 安装前端依赖
npm install

# 安装后端依赖
cd backend && npm install
```

### 2. 配置环境
复制 `.env.example` 为 `.env` 并配置：
```bash
cp .env.example .env
```

### 3. 启动MongoDB
确保MongoDB服务正在运行：
```bash
# macOS/Linux
mongod

# Windows
# 启动MongoDB服务
```

### 4. 启动应用
```bash
# 启动后端服务器
npm run server

# 启动前端开发服务器
npm run dev
```

## 功能特性

### 1. 记录功能
- 支持四种记录类型：心情、觉察、灵感、反思
- 心情值评分（1-10）
- 标签系统
- 时间戳记录

### 2. 热力图
- 年度记录可视化
- 按天显示记录密度
- 点击查看详情

### 3. 数据管理
- 创建、编辑、删除记录
- 按日期筛选
- 最近记录展示

## API接口

### 记录相关
- `GET /api/records` - 获取所有记录
- `GET /api/records/recent?limit=5` - 获取最近记录
- `GET /api/records/date/:date` - 获取特定日期记录
- `POST /api/records` - 创建新记录
- `PUT /api/records/:id` - 更新记录
- `DELETE /api/records/:id` - 删除记录
- `GET /api/records/stats` - 获取统计信息

## 开发计划

### 第一阶段（已完成）
- ✅ 基础项目结构
- ✅ 前端页面和组件
- ✅ 后端API接口
- ✅ 数据模型设计
- ✅ 热力图功能

### 第二阶段（待实现）
- [ ] 用户认证系统
- [ ] 数据备份和同步
- [ ] AI分析报告
- [ ] 提醒功能
- [ ] 数据导出

### 第三阶段（未来规划）
- [ ] 移动端适配
- [ ] 主题切换
- [ ] 社交分享
- [ ] 语音输入
- [ ] 图表分析

## 贡献指南
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证
MIT License
