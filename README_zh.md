# 📘 Interlearn — 把任意主题变成交互式学习体验

将一个关键词或 URL 转化为结构完整、动手实践型的 Jupyter Notebook，内置骨架代码、自动化测试和即时反馈——让你在实践中学习，而非仅靠阅读。

[English](./README.md) | 简体中文

<p align="center">
  <img src="./doc/img/image-zh.png" alt="Interlearn Demo" width="70%" />
</p>

## ✨ 特性

- **🧩 骨架代码**：每一章都包含带提示的 TODO 占位符，学习者自行补全实现
- **✅ 即时验证**：每个知识点都有自动化测试，即时校验正确性——无论完成与否都能运行
- **🌍 多语言支持**：所有说明、提示和 Notebook 内容自动匹配你输入的语言（中文、英文、日文、西班牙文、法文等）
- **📦 零摩擦部署**：自动安装 `uv`、创建隔离虚拟环境、注册 Jupyter Kernel——全部本地运行，无全局污染
- **♻️ 迭代学习**：基于生成的 Notebook 继续向 Agent 提问——深入探索、细化理解或扩展相关主题，无需切换工作流
- **⚙️ 程序化生成**：使用 `nbformat` + `jupyter_client` 可靠地构建 Notebook，而非手工编写 JSON

## 🚀 快速开始

```bash
# 通过 npx skills 全局安装
npx skills add GaryXiongxiong/interlearn -g
```

## 📖 使用方法

### 前置依赖

- **[uv](https://docs.astral.sh/uv/)** — 高速 Python 包安装器和虚拟环境管理器。使用前请先安装：

  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

### 生成 Notebook

输入一个关键词或 URL，Interlearn 会自动完成后续工作：

```
/interlearn Transformer
```

### 示例

| 输入类型 | 示例 | 输出 |
|------------|---------|--------|
| **URL** | `/interlearn https://en.wikipedia.org/wiki/Depth-first_search` | [DFS 交互式 Notebook](./examples/dfs.ipynb) |
| **关键词** | `"教我快速排序"` | [快速排序交互式 Notebook（中文）](./examples/quicksort.ipynb) |