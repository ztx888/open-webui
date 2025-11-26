# OpenWebUI - 功能增强版 (Enhanced Edition)

> **基于官方 OpenWebUI 二次开发，深度汉化细节体验。**
> 本版本同步至官方最新，在保留原版所有功能的前提下，补充了官方没做的汉化细节，并新增了按次计费、模型快捷入口、Token 预估、Gemini 原生支持等实用功能，使用更顺手。

-----

## ✨ 独家功能 (Features)

### 🛠️ 1. 深度 UI/UX 体验优化 (用的更顺手)

#### ⚡ 快捷入口与 Token 预估

  - **模型设置直达**：在首页模型下拉框中，新增了\*\*【模型设置】\*\*跳转按钮。想改参数不用去后台翻半天，点一下直接达。
  - **输入框 Token 预估**：输入框右下角新增 **Token 预估** (≈ 0 tokens)，发送前心里有数，不再盲目消耗。

<img width="650" height="465" alt="PixPin_2025-11-25_20-28-43" src="https://github.com/user-attachments/assets/6dead822-da02-4d22-9d6e-6b652eefd7b9" />

#### 🔗 外部连接管理增强 (治好强迫症)

  - **备注功能**：给一堆 key 加上备注（如 "主力号", "备用", "DeepSeek"），一眼分辨，不再瞎猜。
  - **点击跳转**：点击名称直接编辑，操作逻辑更符合直觉。

<img width="487" height="313" alt="PixPin\_2025-11-25\_20-29-34" src="https://github.com/user-attachments/assets/6dbdfef7-ec1d-40e3-856c-158f2d2bc8d8" />

#### 🧠 高级设置人性化

  - **思考等级 (Reasoning Effort) 下拉框**：针对 o1/Claude 等推理模型，把手动输参数改成了标准的**下拉选择** (Low/Medium/High)，简单直接。
  - **全汉化界面**：把高级设置里的温度、惩罚系数等参数说明全部汉化。

<img width="390" height="1077" alt="image" src="https://github.com/user-attachments/assets/6ec4aaae-2f75-4526-a84e-dda8618164f5" />
<img width="390" height="507" alt="image" src="https://github.com/user-attachments/assets/7c29cbb6-69b3-4143-8fef-eae18be24966" />

-----

### 💰 2. 更灵活的计费模式

在基础上加了三种模式，方便分享给朋友或小圈子使用时管理成本。

| 模式 | 描述 |
| :--- | :--- |
| **按量计费 (Per Token)** | 官方原生逻辑，算得细，用多少扣多少。 |
| **按次计费 (Per Request)** |简单粗暴，聊一次扣一次钱（比如 0.1元/次），不用算 Token 账。 |
| **免费模式 (Free)** | 设置为免费的模型，前端会直接提示“免费”，不扣余额。 |
<img width="1630" height="321" alt="PixPin\_2025-11-25\_20-34-00" src="https://github.com/user-attachments/assets/38294f08-978f-4659-a321-d06e3e76ab18" />

> **费用统计汉化**：重写了对话框底部的黑色浮窗，完全汉化，并能根据计费模式显示如 `¥0.05 (按次计费)`。

<img width="528" height="202" alt="PixPin\_2025-11-25\_20-31-50" src="https://github.com/user-attachments/assets/983cc367-1561-47fe-a5f2-f8f980fe1579" />
<img width="252" height="158" alt="PixPin\_2025-11-25\_20-32-37" src="https://github.com/user-attachments/assets/eebbad79-c0e0-4109-a5a1-953c44cd5b48" />

-----

### ♊ 3. Gemini 原生深度支持 (Native Integration)

> **专为 Gemini 代理用户优化，解决官方版“水土不服”的问题。**

  - **多协议无缝切换**：在【外部连接】中新增了 **“提供商 (Provider)”** 选项。支持显式选择 **OpenAI** 或 **Gemini** 协议，彻底解决用 OpenAI 格式强连 Gemini 代理导致的协议冲突。
  - **“哑巴代理”智能兼容**：针对 `aistudio-build-proxy` 等不返回模型列表 (`/models`) 或 Header 不标准的代理，重写了后端逻辑。
      - **自动兜底**：连接验证失败时，自动加载标准 Gemini 模型列表 (1.5 Pro/Flash/Ultra 等)，拒绝 404。
      - **格式容错**：强制解析非标准 JSON 响应，解决 `unexpected mimetype` 报错。
  - **安全设置 (Safety Settings)**：新增**安全等级**配置项。可针对特定连接一键开启 **“无限制 (Block None)”** 模式，彻底告别 Gemini 动不动就因为“安全原因”中断对话的烦恼。
<img width="1035" height="543" alt="image" src="https://github.com/user-attachments/assets/df6958af-281e-41d2-9bf2-5be541580dc9" />

<img width="2186" height="546" alt="image" src="https://github.com/user-attachments/assets/578703d8-e072-4f8b-94a7-eef566528cf8" />

-----

### 🛡️ 4. 稳定性与构建修复

  - **数据库防崩**：修复了官方更新可能导致的数据库“重复列”报错，加了自动检查脚本，Docker 重启更稳。
  - **跨平台构建**：修复了 Windows 本地开发环境导致的 Linux 构建失败问题

-----

## 🚀 部署方法

和官方原版完全一致，可用 Docker Compose 启动。

```yaml
version: '3.8'
services:
  open-webui:
    image: ghcr.io/ztx888/openwebui:latest
    volumes:
      - ./data:/app/backend/data
    ports:
      - 3000:8080
    restart: always
```

🙏 致谢
感谢 [OpenWebUI](https://github.com/open-webui/open-webui) 的官方项目！致以崇高的敬意！
