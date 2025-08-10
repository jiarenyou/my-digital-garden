# 核心记录系统设计文档

## 概述

核心记录系统是Kairos应用的基础架构，实现用户快速记录四种类型的个人成长数据：心情、觉察、灵感和反思。系统采用前后端分离架构，使用React + Express + MongoDB技术栈，支持离线功能和实时数据同步。

设计目标：
- 极简用户体验，3秒内完成记录
- 可靠的数据存储和同步机制
- 支持离线使用和自动同步
- 为后续AI分析功能提供结构化数据基础

## 架构

### 整体架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React前端     │    │   Express后端   │    │   MongoDB数据库  │
│                 │    │                 │    │                 │
│ - 记录界面      │◄──►│ - REST API      │◄──►│ - 记录集合      │
│ - 离线存储      │    │ - 数据验证      │    │ - 索引优化      │
│ - 状态管理      │    │ - 同步逻辑      │    │ - 备份策略      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐
│   IndexedDB     │
│   (离线存储)     │
└─────────────────┘
```

### 数据流架构
1. **在线模式**: 用户输入 → 前端验证 → API调用 → 数据库存储 → 响应返回
2. **离线模式**: 用户输入 → 前端验证 → IndexedDB存储 → 网络恢复时同步
3. **草稿模式**: 实时输入 → IndexedDB草稿 → 用户保存时转为正式记录

## 组件和接口

### 前端组件架构

#### 核心组件
```
App
├── HomePage (四类记录入口)
│   ├── RecordTypeCard (记录类型卡片)
│   └── RecentRecords (最近记录)
├── RecordPage (记录管理)
│   ├── RecordForm (记录表单)
│   ├── RecordList (记录列表)
│   └── SearchBar (搜索栏)
└── OfflineIndicator (离线状态指示)
```

#### 关键组件设计

**RecordForm组件**
- 支持四种记录类型的动态表单
- 心情记录包含1-10评分滑块
- 实时草稿保存功能
- 表单验证和错误提示

**RecordTypeCard组件**
- 每种记录类型的专用入口
- 视觉区分（图标、颜色）
- 快速记录模式支持

### 后端API接口

#### REST API设计
```
POST   /api/records              # 创建新记录
GET    /api/records              # 获取记录列表（支持分页、筛选）
GET    /api/records/:id          # 获取单个记录
PUT    /api/records/:id          # 更新记录
DELETE /api/records/:id          # 软删除记录
POST   /api/records/:id/restore  # 恢复删除的记录

GET    /api/records/search       # 搜索记录
POST   /api/sync/upload          # 批量上传离线记录
GET    /api/sync/status          # 获取同步状态
```

#### API响应格式
```json
{
  "success": true,
  "data": {
    "records": [...],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 100
    }
  },
  "message": "操作成功"
}
```

### 服务层设计

#### 前端服务
- **RecordService**: 记录CRUD操作和API调用
- **OfflineService**: 离线数据管理和同步
- **DraftService**: 草稿自动保存和恢复
- **ValidationService**: 前端数据验证

#### 后端服务
- **RecordController**: 处理记录相关的HTTP请求
- **SyncController**: 处理离线数据同步
- **ValidationMiddleware**: 数据验证中间件

## 数据模型

### MongoDB记录模型
```javascript
const RecordSchema = new mongoose.Schema({
  // 基础字段
  type: {
    type: String,
    enum: ['mood', 'awareness', 'inspiration', 'reflection'],
    required: true
  },
  content: {
    type: String,
    required: true,
    maxlength: 2000
  },
  
  // 心情专用字段
  moodScore: {
    type: Number,
    min: 1,
    max: 10,
    required: function() { return this.type === 'mood'; }
  },
  
  // 时间戳
  createdAt: {
    type: Date,
    default: Date.now,
    index: true
  },
  updatedAt: {
    type: Date,
    default: Date.now
  },
  
  // 软删除支持
  isDeleted: {
    type: Boolean,
    default: false,
    index: true
  },
  deletedAt: {
    type: Date,
    default: null
  },
  
  // 版本控制
  version: {
    type: Number,
    default: 1
  },
  editHistory: [{
    content: String,
    moodScore: Number,
    editedAt: Date
  }],
  
  // 同步相关
  syncStatus: {
    type: String,
    enum: ['synced', 'pending', 'conflict'],
    default: 'synced'
  },
  clientId: String, // 用于离线同步冲突解决
  
  // 索引
}, {
  timestamps: true
});

// 复合索引
RecordSchema.index({ type: 1, createdAt: -1 });
RecordSchema.index({ isDeleted: 1, createdAt: -1 });
```

### IndexedDB离线存储模型
```javascript
// 草稿存储
const DraftStore = {
  keyPath: 'id',
  data: {
    id: 'draft_timestamp',
    type: 'mood|awareness|inspiration|reflection',
    content: 'string',
    moodScore: 'number?',
    createdAt: 'timestamp',
    autoSaved: 'boolean'
  }
};

// 离线记录存储
const OfflineRecordStore = {
  keyPath: 'tempId',
  data: {
    tempId: 'uuid',
    type: 'string',
    content: 'string',
    moodScore: 'number?',
    createdAt: 'timestamp',
    syncStatus: 'pending|failed|synced'
  }
};
```

## 错误处理

### 错误分类和处理策略

#### 前端错误处理
1. **网络错误**: 自动重试机制，最多3次
2. **验证错误**: 实时表单验证和用户友好提示
3. **存储错误**: IndexedDB操作失败时的降级策略
4. **同步冲突**: 用户选择界面解决数据冲突

#### 后端错误处理
1. **数据验证错误**: 返回详细的字段错误信息
2. **数据库连接错误**: 自动重连和健康检查
3. **同步冲突**: 基于时间戳和版本号的冲突检测

#### 错误响应格式
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "数据验证失败",
    "details": {
      "content": "内容不能为空",
      "moodScore": "心情评分必须在1-10之间"
    }
  }
}
```

## 测试策略

### 单元测试
- **前端组件测试**: React Testing Library
- **API接口测试**: Jest + Supertest
- **数据模型测试**: Mongoose模型验证测试
- **服务层测试**: 业务逻辑单元测试

### 集成测试
- **前后端API集成**: 端到端API调用测试
- **数据库集成**: MongoDB操作集成测试
- **离线同步测试**: 模拟网络断开和恢复场景

### 性能测试
- **加载性能**: 页面加载时间 < 3秒
- **API响应**: 记录保存 < 1秒
- **大数据量**: 1000+记录的列表渲染性能

### 用户体验测试
- **快速记录流程**: 从打开到保存完成 < 10秒
- **离线功能**: 网络断开时的用户体验
- **数据恢复**: 意外退出后的草稿恢复

## 关键设计决策

### 1. 数据存储策略
**决策**: 使用MongoDB作为主数据库，IndexedDB作为离线存储
**理由**: 
- MongoDB的文档结构适合灵活的记录数据
- IndexedDB提供可靠的浏览器端存储
- 支持复杂查询和索引优化

### 2. 离线同步机制
**决策**: 采用乐观锁和时间戳比较的冲突解决策略
**理由**:
- 简化同步逻辑，减少复杂性
- 用户可控的冲突解决方案
- 保证数据一致性和用户体验

### 3. 草稿自动保存
**决策**: 使用防抖技术，每2秒自动保存一次草稿
**理由**:
- 平衡性能和数据安全
- 减少不必要的存储操作
- 提供良好的用户体验

### 4. 软删除策略
**决策**: 实现软删除，保留30天恢复期
**理由**:
- 防止用户误删重要数据
- 符合数据保护最佳实践
- 支持数据分析和审计需求

### 5. API设计原则
**决策**: RESTful API设计，统一响应格式
**理由**:
- 标准化的API设计易于维护
- 前端可预期的数据结构
- 支持未来的API版本管理

### 6. 性能优化策略
**决策**: 分页加载、索引优化、缓存策略
**理由**:
- 支持大量历史数据的高效查询
- 保证应用响应速度
- 优化用户体验和资源使用