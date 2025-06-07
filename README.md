# AI-Toolkit

AI时代的各种小工具和开发规范的集合，包含编程规范、提示词文件和实用工具。

## 📁 项目结构

```
AI-Toolkit/
├── Rules/              # 编程规范和提示词
│   └── Python/         # Python开发规范
│       └── copilot-instructions.md  # GitHub Copilot指令文件
└── Tools/              # 实用工具
    └── ChatToMD.py     # 聊天记录转换工具，把Copilot Chat导出的JSON转换为Markdown
```

## 📋 Rules - 编程规范

### Python 规范
- **copilot-instructions.md**: GitHub Copilot的Python开发指令文件
  - 包含AI助手行为规范
  - 匈牙利命名法约定
  - 编码最佳实践
  - 错误处理模式
  - [官方文档](https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot)

## 🛠️ Tools - 实用工具

### ChatToMD.py
用于将GitHub Copilot导出的JSON聊天记录转换为Markdown格式的工具。

**功能特性:**
- 解析JSON格式的聊天记录
- 转换为易读的Markdown格式
- 保持对话结构和格式

**使用方法:**
```bash
python Tools/ChatToMD.py input.json output.md
```

## 🚀 使用说明

1. **作为GitHub Copilot指令**: 将`Rules/Python/copilot-instructions.md`放在项目根目录
2. **自定义规范**: 根据项目需求修改编程规范
3. **工具使用**: 直接运行Tools目录下的Python脚本

## 📄 License

本项目遵循MIT许可证 - 详见[LICENSE](LICENSE)文件


