# hello-wiki

基于 **pnpm** 的 monorepo，Web 应用使用 [Next.js](https://nextjs.org)（位于 `apps/web`），配套 React 19、TypeScript 与 Tailwind CSS v4。

## 环境要求

与 CI 保持一致即可本地开发与通过检查：

- **Node.js** 20
- **pnpm** 10

安装 pnpm 可参考官方文档：[pnpm 安装](https://pnpm.io/installation)。

## 协作与 Pull Request

团队在 **GitHub** 上以「功能分支 → Pull Request → 合并到 `main`」的方式开发，避免直接向 `main` 推送。

### 推荐流程

1. **同步主分支**  
   `git checkout main` → `git pull origin main`

2. **从 `main` 拉分支**  
   命名建议与改动类型一致，便于识别，例如：  
   `feat/词条搜索`、`fix/目录跳转`、`docs/更新 README`

3. **开发与自测**  
   在仓库根目录使用 `pnpm dev`（默认 <http://localhost:3000>）。  
   **提交或开 PR 前**在本地执行 `pnpm lint` 与 `pnpm build`，与 CI 步骤一致，减少返工。

4. **推送并创建 PR**  
   推送到远端后在 GitHub 上开 Pull Request。描述里建议写清：  
   要解决什么问题、主要改了什么、是否需要额外配置或迁移说明。

5. **代码审查与合并**  
   由团队成员 Review；**CI 全部通过**后再合并。具体合并策略（merge / squash / rebase）由团队约定。

### CI 检查说明

工作流定义在 `.github/workflows/ci.yml`：在 **push** 与 **pull_request** 上会执行 `pnpm install --frozen-lockfile`、`pnpm lint`、`pnpm build`。  
PR 需绿灯后再合并。

## 本地开发

在仓库根目录执行：

| 命令 | 说明 |
|------|------|
| `pnpm dev` | 启动开发服务器（默认 <http://localhost:3000>） |
| `pnpm build` | 生产构建 |
| `pnpm start` | 启动生产服务（需先 build） |
| `pnpm lint` | 运行 ESLint |

页面入口：`apps/web/src/app/page.tsx`，修改后热更新。

## 项目结构

```
hello-wiki/
├── apps/
│   └── web/          # Next.js 应用
├── .github/
│   └── workflows/    # CI 工作流
├── package.json      # 根脚本与 workspace
└── pnpm-lock.yaml
```

## Git Commit 规范

提交信息建议使用类型前缀，便于检索与变更说明：

| 类型 | 说明 |
|------|------|
| **feat** | 新增 feature |
| **fix** | 修复 bug |
| **docs** | 仅仅修改了文档，比如 README、CHANGELOG、CONTRIBUTE 等等 |
| **style** | 仅仅修改了空格、格式缩进、逗号等等，不改变代码逻辑 |
| **refactor** | 代码重构，没有加新功能或者修复 bug |
| **perf** | 优化相关，比如提升性能、体验 |
| **test** | 测试用例，包括单元测试、集成测试等 |
| **chore** | 改变构建流程、或者增加依赖库、工具等 |
| **revert** | 回滚到上一个版本 |

示例：`feat: 添加词条搜索`、`fix: 修正目录跳转错误`。

## 参考文档

- [Next.js 文档](https://nextjs.org/docs)
- [Next.js 部署说明](https://nextjs.org/docs/app/building-your-application/deploying)
