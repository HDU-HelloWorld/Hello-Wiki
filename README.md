# hello-wiki

`hello-wiki` 是一个基于 **pnpm workspace** 的 monorepo，当前包含：

- `apps/web`：Next.js 16 + React 19 + TypeScript + Tailwind CSS v4
- `apps/backend`：FastAPI 分层 MVP 脚手架（可运行，业务逻辑待实现）

## 当前开发进度

### Web（`apps/web`）

- [x] 已完成 Next.js 工程初始化与基础依赖接入
- [x] 已有根页面 `apps/web/src/app/page.tsx`（默认模板内容）
- [x] 已创建路由文件：`/about`、`/home`、`/login`
- [ ] `about/home/login` 页面内容待实现（当前为空文件）

### Backend（`apps/backend`）

- [x] 已完成 FastAPI 分层目录骨架（`api/application/domain/infra/workers/core`）
- [x] 已可本地启动服务（`python main.py`，默认 `127.0.0.1:8000`）
- [x] 已提供基础健康检查与占位接口路由
- [ ] Wiki / Compile / QA 业务逻辑仍为占位实现（MVP scaffold）

## 环境要求

建议本地与 CI 保持一致：

- **Node.js** 20
- **pnpm** 10
- **Python** 3.11+（用于 `apps/backend`）

安装 pnpm 参考：[pnpm 安装文档](https://pnpm.io/installation)

## 本地开发

在仓库根目录执行：

| 命令 | 说明 |
|------|------|
| `pnpm install` | 安装 workspace 依赖 |
| `pnpm dev` | 并行启动 web 与 backend 开发服务 |
| `pnpm build` | 构建 web 应用 |
| `pnpm start` | 启动 web 生产服务（需先 build） |
| `pnpm lint` | 运行 web 的 ESLint |

### 访问地址

- Web: <http://localhost:3000>
- Backend API: <http://127.0.0.1:8000/api>
- Backend 健康检查: <http://127.0.0.1:8000/api/health>

## 当前路由与接口状态

### Web 路由

- `/`：默认模板页面（待替换为业务首页）
- `/about`：文件已创建，页面内容待实现
- `/home`：文件已创建，页面内容待实现
- `/login`：文件已创建，页面内容待实现

### Backend 接口

- `GET /api/`：可访问
- `GET /api/health`：健康检查
- `GET /api/wiki`：占位接口（501）
- `POST /api/compile`：占位接口（501）
- `POST /api/qa`：占位接口（501）

## 项目结构

```
hello-wiki/
├── apps/
│   ├── web/               # Next.js 前端
│   └── backend/           # FastAPI 分层后端脚手架
├── .github/workflows/     # CI 工作流
├── package.json           # 根脚本（workspace 编排）
└── pnpm-lock.yaml
```

## 协作与 Pull Request

团队在 GitHub 采用「功能分支 -> Pull Request -> 合并到 `main`」流程，避免直接向 `main` 推送。

1. 同步主分支：`git checkout main` -> `git pull origin main`
2. 从 `main` 拉分支：如 `feat/xxx`、`fix/xxx`、`docs/xxx`
3. 开发与自测：提交前执行 `pnpm lint`、`pnpm build`
4. 推送并创建 PR：说明问题背景、主要改动、是否有迁移/配置影响
5. Review 与合并：CI 绿灯后再合并

## CI 检查说明

CI 位于 `.github/workflows/ci.yml`，在 `push` 与 `pull_request` 上执行：

- `pnpm install --frozen-lockfile`
- `pnpm lint`
- `pnpm build`

## Git Commit 规范

建议使用 Conventional 风格前缀，便于检索与生成变更说明：

- `feat`：新增功能
- `fix`：修复问题
- `docs`：文档更新
- `style`：仅格式调整（不改逻辑）
- `refactor`：重构（无新增功能/无修复）
- `perf`：性能优化
- `test`：测试相关
- `chore`：工程配置/脚手架/依赖维护
- `revert`：回滚提交

示例：`feat: 添加词条搜索`、`docs: 更新项目开发进度`

## 参考文档

- [Next.js 文档](https://nextjs.org/docs)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [pnpm Workspace 文档](https://pnpm.io/workspaces)
- [JS 开发命名规范](https://juejin.cn/post/6844903492415406088)
