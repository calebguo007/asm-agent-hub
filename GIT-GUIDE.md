# ASM 双仓库 Git 指南

## 为什么要两个仓库？

```
asm-spec (public)           ← 给别人看的：代码、schema、文档
asm-spec-private- (private) ← 给自己看的：包含内部规划、调研、冲刺计划
```

**核心原因：** GitHub 没有文件级别的权限控制。一个 public repo 里的所有文件对所有人可见。你的内部规划文档（竞争分析、曝光策略、冲刺计划）不应该公开，所以需要两个仓库。

---

## 两个仓库的内容对比

| 文件 | Public | Private | 为什么 |
|------|--------|---------|--------|
| schema/, manifests/, scorer/, registry/, demo/ | ✅ | ✅ | 核心代码，对外展示 |
| README.md, LICENSE | ✅ | ✅ | 开源必备 |
| paper/ | ✅ | ✅ | 学术定位，公开有利 |
| 调研文档.md | ❌ | ✅ | 内部调研，含竞品分析 |
| 冲刺计划-4月.md | ❌ | ✅ | 内部排期 |
| ASM曝光与学术规划.md | ❌ | ✅ | 曝光策略，不宜公开 |
| 论文阅读指南.md | ❌ | ✅ | 个人笔记 |
| 黑客松选择建议.md | ❌ | ✅ | 内部决策 |
| PROJECT-CONTEXT.md | ❌ | ✅ | 项目内部 briefing |
| github-discussion-69-reply.md | ❌ | ✅ | 回复草稿 |

---

## 仓库地址

- **Public:**  https://github.com/calebguo007/asm-spec.git
- **Private:** https://github.com/calebguo007/asm-spec.git-private-

---

## Git Remote 配置

本地仓库配置了两个 remote：

```
origin  → public repo  (asm-spec)
private → private repo (asm-spec-private-)
```

查看当前配置：

```bash
git remote -v
```

---

## 日常操作

### 改了代码（schema、scorer、manifests 等）

代码改动需要推送到**两个**仓库：

```bash
# 1. 在 main 分支上提交
git add .
git commit -m "描述你的改动"

# 2. 推到 public
git push origin main

# 3. 切到 private-full 分支，合并，推到 private
git checkout private-full
git merge main
git push private private-full:main

# 4. 切回 main
git checkout main
```

### 改了中文文档（调研、计划等）

中文文档只推到 private：

```bash
# 1. 切到 private-full 分支
git checkout private-full

# 2. 提交（需要 -f 因为被 .gitignore 屏蔽了）
git add -f 调研文档.md
git commit -m "更新调研文档"

# 3. 推到 private
git push private private-full:main

# 4. 切回 main
git checkout main
```

### 只想快速推 public

```bash
git add .
git commit -m "your message"
git push origin main
```

---

## 分支说明

| 分支 | 用途 | 推送到 |
|------|------|--------|
| `main` | 公开代码，不含中文文档 | `origin` (public) |
| `private-full` | 全部内容，含中文文档 | `private` (private) |

---

## 注意事项

1. **不要在 main 分支 `git add -f` 中文文档** — 否则会推到 public repo
2. **代码改动记得同步两边** — 改了 main 后要 merge 到 private-full
3. **`.gitignore` 是关键** — 它阻止中文文档进入 public repo，不要删除里面的中文文件名
4. **private repo 的 URL 不要分享给别人**


---

## 三仓库策略（2026-04-15 更新 — 最新）

项目现在分为三个仓库，每个有明确的用途和受众：

| 仓库 | 用途 | 受众 | 分支 | Remote |
|------|------|------|------|--------|
| **asm-agent-hub** | 🏆 **比赛版** — 黑客松提交的完整交付物 | Circle / lablab.ai 评委 | main | `hub` |
| **asm-spec** | 🌐 **对外版** — 开源协议规范 + 核心代码 | MCP 社区 / 潜在贡献者 / arXiv 读者 | main | `spec` |
| **asm-spec-private-** | 🔒 **完整版** — 所有内容含内部规划 | 只给自己 | private-full | `private` |

### 为什么要三个仓库？

- **asm-agent-hub**（比赛版）：面向评委，可以包含黑客松特定的包装（DEMO-SCRIPT、SUBMISSION-DRAFT、Pitch Deck）。比赛结束后作为"这个项目参加过 hackathon 的证据"留存。
- **asm-spec**（对外版）：面向长期开源社区，干净的协议定义 + 代码 + 论文。不带比赛特定的内容。
- **asm-spec-private-**（完整版）：含所有中文文档、冲刺计划、调研、学习计划等，只给自己看。

### Remote 配置（验证）

```bash
git remote -v
# hub      https://github.com/calebguo007/asm-agent-hub.git
# spec     https://github.com/calebguo007/asm-spec.git
# private  https://github.com/calebguo007/asm-spec-private-.git
```

如果少了哪个：

```bash
git remote add hub     https://github.com/calebguo007/asm-agent-hub.git
git remote add spec    https://github.com/calebguo007/asm-spec.git
git remote add private https://github.com/calebguo007/asm-spec-private-.git
```

---

## Push 规则（按改动类型决定推到哪里）

### 场景 A：改了核心代码（schema、scorer、registry、payments、manifests 等）

**推全部三个仓库**（代码是所有版本都需要的）：

```bash
# 1. 在 main 分支提交
git checkout main
git add <files>
git commit -m "your message"

# 2. 推到比赛版
git push hub main

# 3. 推到对外版
git push spec main

# 4. 推到完整版（先合并）
git checkout private-full
git merge main
git push private private-full:main

# 5. 切回 main
git checkout main
```

### 场景 B：改了比赛专用文档（HACKATHON、DEMO-SCRIPT、SUBMISSION-DRAFT、VIDEO-RECORDING-GUIDE、Pitch Deck 等）

这些文件在 `docs/hackathon/` 下，被 `.gitignore` 屏蔽。**只推 hub 和 private**：

```bash
git checkout private-full
git add -f docs/hackathon/HACKATHON.md docs/hackathon/DEMO-SCRIPT.md
git commit -m "update hackathon materials"

# 推到比赛版（比赛评委需要看）
git push private private-full:main
git push hub private-full:main

git checkout main
```

**注意**：不推到 `spec`（对外版不该有比赛特定内容）。

### 场景 C：改了内部文档（调研、冲刺计划、学习计划、战略分析等）

这些文件在 `docs/internal/` 下，也被 `.gitignore` 屏蔽。**只推 private**：

```bash
git checkout private-full
git add -f docs/internal/论文阅读指南.md docs/internal/冲刺计划-4月.md
git commit -m "update internal docs"
git push private private-full:main
git checkout main
```

**注意**：绝对不推到 `hub` 或 `spec`。

### 场景 D：快速推送已经提交的 main（同步三边）

```bash
git push hub main && git push spec main
git checkout private-full && git merge main && git push private private-full:main && git checkout main
```

---

## 目标仓库速查表

| 改动类型 | 文件示例 | hub | spec | private |
|---------|---------|:---:|:----:|:-------:|
| 核心代码 | `registry/`, `payments/`, `scorer/`, `manifests/` | ✅ | ✅ | ✅ |
| 公开文档 | `README.md`, `paper/`, `sep/`, `docs/specs/` | ✅ | ✅ | ✅ |
| 比赛材料 | `docs/hackathon/*` | ✅ | ❌ | ✅ |
| 内部文档 | `docs/internal/*`（含学习计划、冲刺计划、战略分析）| ❌ | ❌ | ✅ |

---

## 分支说明

| 分支 | 用途 | 推送到 |
|------|------|--------|
| `main` | 核心代码 + 公开文档 | `hub`, `spec` |
| `private-full` | 全部内容含内部文档 | `private` (兼具 `hub` 的比赛材料) |

`main` 追踪 `spec/main`，所以 `git push` 默认推对外版。要推比赛版必须显式 `git push hub main`。

---

## 核心原则（务必遵守）

1. **三种改动三种推法** — 不要偷懒每次都推全部
2. **对外版保持干净** — spec 永远不能出现 `docs/hackathon/` 或 `docs/internal/` 的内容
3. **内部文档只在 private** — `docs/internal/` 严格保护，永远不推 hub/spec
4. **`.gitignore` 是最后一道防线** — 不要删它里面的规则，尤其是 `docs/hackathon/` 和 `docs/internal/`
5. **提交前 `git status` 检查** — 如果看到意外的 `??` untracked 文件在暂存区，先 reset 再想
6. **用 `git add <specific-file>` 而不是 `git add .`** — 防止意外带上敏感文件

---

## 常见错误排查

### 错误 1：中文文档泄漏到 public

症状：在 asm-spec 或 asm-agent-hub 的 GitHub 页面上看到了中文文档。

原因：
- 可能在 `main` 分支用了 `git add -f` 加了被 gitignore 的文件
- 或者 gitignore 规则被破坏

修复：
```bash
# 1. 在 main 分支移除（保留本地文件）
git rm --cached docs/internal/xxx.md
git commit -m "chore: remove leaked internal doc from public tracking"
git push hub main
git push spec main

# 2. 检查 .gitignore 是否还有规则
cat .gitignore | grep internal
```

### 错误 2：推送被拒绝（non-fast-forward）

症状：`! [rejected] ... (non-fast-forward)`

原因：远程有本地没有的提交。

修复：
```bash
git pull <remote> <branch> --no-rebase   # 合并而非 rebase，保留历史
# 解决冲突后 commit
git push <remote> <branch>
```

### 错误 3：忘了切回 main

症状：你停在了 `private-full` 分支然后继续改代码，提交到了私有分支。

修复：
```bash
git log --oneline -5   # 找到要转移的 commit hash
git checkout main
git cherry-pick <hash> # 把 commit 复制到 main
# 然后到 private-full 上 git reset --hard HEAD~1 去掉重复的
```
