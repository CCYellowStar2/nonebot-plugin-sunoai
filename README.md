<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-sunoai

_✨ 基于第三方柏拉图api的sunoai插件，支持文生音乐和纯音乐 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/CCYellowStar2/nonebot-plugin-sunoai.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-sunoai">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-sunoai.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">

</div>
  

## 📖 介绍

这是使用第三方拉图api的sunoai插件，你需要先去[柏拉图api](https://one-api.bltcy.top/)注册一个账号，创建一个key放到env配置里`suno_key = "sk-xxxxxxxxx"`，然后账户里充点钱，**因为使用是一毛钱一首**，然后就可以使用了

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-sunoai

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-sunoai
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-sunoai
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-sunoai
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-sunoai
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_sunoai"]

</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| suno_key | 是 | 无 | [柏拉图api](https://one-api.bltcy.top/)创建的key |

## 🎉 使用
### 指令表
发送 suno -h 获取帮助

使用指令 'suno -p 我要炸学校'生成简易模式歌曲 或 'suno -n 炸学校(标题) -t pop,edm(风格) -l 我去炸学校，天天不迟到(歌词) '来生成自定义歌曲，如果是纯音乐请不要加-l和歌词，要加个-i


可用的选项有:

使用简单模式 Prompt(使用后无需其他参数)

-p│--prompt <prompt: str+>
歌曲的标题

--name│-n <name: str+>
歌曲的tag，逗号分隔

--tag│-t <tag: str+>
歌词（支持更高级的语法）

--lyrics│-l <lyrics: str+>
纯音乐模式

-i│--instrumental


使用示例:

suno -p 我要炸学校

suno -n 炸学校 -t pop,edm -l 我去炸学校，天天不迟到
### 效果图
![c3be587b67a2dcb58e54d98731060b9](https://github.com/user-attachments/assets/6e14668c-4333-452a-8c48-8342b1f40829)

