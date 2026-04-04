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

- **Public:**  https://github.com/velmavalienteqejimu22-jpg/asm-spec
- **Private:** https://github.com/velmavalienteqejimu22-jpg/asm-spec-private-

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
