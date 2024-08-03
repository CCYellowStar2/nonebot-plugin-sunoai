import re
import os
import random
import aiohttp
import time
import asyncio
from nonebot import get_plugin_config, logger
from nonebot.plugin import PluginMetadata, inherit_supported_adapters, require
require("nonebot_plugin_alconna")
from arclet.alconna import (
    Alconna,
    Arg,
    Args,
    Arparma,
    StrMulti,
    ArparmaBehavior,
    CommandMeta,
    Option,
    store_true,
)
from arclet.alconna.exceptions import OutBoundsBehave, SpecialOptionTriggered
from nonebot_plugin_alconna import AlconnaMatcher, CommandResult, on_alconna
from nonebot_plugin_alconna.uniseg import Receipt, UniMessage
from nonebot_plugin_alconna.builtins.uniseg.music_share import MusicShare,MusicShareKind
from .config import Config, ConfigError

__plugin_meta__ = PluginMetadata(
    name="SunoAI音乐生成",
    description="基于第三方柏拉图的sunoai插件，支持文生音乐和纯音乐",
    usage="""
        使用指令 'suno -p 我要炸学校'生成简易模式歌曲 或 'suno -n 炸学校(标题) -t pop,edm(风格) -l 我去炸学校，天天不迟到(歌词) '来生成自定义歌曲，如果是纯音乐请不要加-l和歌词，要加个-i
    """,
    config=Config,
    extra={},
    type="application",
    homepage="https://github.com/CCYellowStar2/nonebot_plugin_sunoai",
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
)

plugin_config = get_plugin_config(Config)

if not plugin_config.suno_key:
    raise ConfigError("请配置sunoAI音乐生成的KEY")
    
SUNO_API_KEY = plugin_config.suno_key

headers = {
    'Authorization':f'Bearer {SUNO_API_KEY}',
    'Content-Type':'application/json',
    'Accept':'application/json',
}


class sunoBehavior(ArparmaBehavior):
    def operate(self, interface: Arparma):
        name: Optional[str] = interface["name"]
        prompt: Optional[str] = interface["prompt"]
        tag: Optional[str] = interface["tag"]
        lyrics: Optional[str] = interface["lyrics"]
        instrumental: bool = interface["instrumental"].value

        if prompt and isinstance(prompt,str):
            if lyrics and isinstance(lyrics,str):
                raise OutBoundsBehave("不能同时指定 简单模式Prompt 和 自定义歌词 使用指令 `suno -h` 查看帮助")
            if name and isinstance(name,str):
                raise OutBoundsBehave("不能同时指定 简单模式Prompt 和 歌名 使用指令 `suno -h` 查看帮助")
            if tag and isinstance(tag,str):
                raise OutBoundsBehave("不能同时指定 简单模式Prompt 和 tag 使用指令 `suno -h` 查看帮助")
        elif prompt and not isinstance(prompt,str):
            if not instrumental:
                if lyrics and not isinstance(lyrics,str):
                    raise OutBoundsBehave("请指定 自定义歌词 使用指令 `suno -h` 查看帮助")
            else:
                if lyrics and isinstance(lyrics,str):
                    raise OutBoundsBehave("不能同时指定 自定义歌词 和 纯音乐模式 使用指令 `suno -h` 查看帮助")
            if name and not isinstance(name,str):
                raise OutBoundsBehave("请指定 歌名 使用指令 `suno -h` 查看帮助")
            if tag and not isinstance(tag,str):
                raise OutBoundsBehave("请指定 tag 使用指令 `suno -h` 查看帮助")

play = on_alconna(
    Alconna(
        "suno",
        Option(
            "--prompt",
            Args["prompt", StrMulti],
            alias=("-p",),
            default=None,
            help_text="使用简单模式 Prompt(使用后无需其他参数)",
        ),
        Option(
            "--name",
            Args["name", StrMulti],
            alias=("-n",),
            default=None,
            help_text="歌曲的标题",
        ),
        Option(
            "--tag",
            Args["tag", StrMulti],
            alias=("-t",),
            default=None,
            help_text="歌曲的tag，逗号分隔",
        ),
        Option(
            "--lyrics",
            Args["lyrics", StrMulti],
            alias=("-l",),
            default=None,
            help_text="歌词（支持更高级的语法）",
        ),
        Option(
            "--instrumental",
            alias=("-i",),
            default=False,
            action=store_true,
            help_text="纯音乐模式",
        ),
        meta=CommandMeta(
            description="使用指令 'suno -p 我要炸学校'生成简易模式歌曲 或 'suno -n 炸学校(标题) -t pop,edm(风格) -l 我去炸学校，天天不迟到(歌词) '来生成自定义歌曲，如果是纯音乐请不要加-l和歌词，要加个-i",
            example='suno -p 我要炸学校\nsuno -n 炸学校 -t pop,edm -l 我去炸学校，天天不迟到',
        ),
        behaviors=[sunoBehavior()],
    ),
    aliases={"生成音乐","生成歌曲"},
    skip_for_unmatch=False,
    use_cmd_start=True,
)

@play.handle()
async def _(matcher: AlconnaMatcher, res: CommandResult):
    if not res.result.error_info:
        return
    if isinstance(res.result.error_info, SpecialOptionTriggered):
        await matcher.finish(res.output)
    await matcher.finish(f"{res.result.error_info}")

@play.handle()
async def _(matcher: AlconnaMatcher, parma: Arparma):
    name: Optional[str] = parma["name"]
    prompt: Optional[str] = parma["prompt"]
    lyrics: Optional[str] = parma["lyrics"]
    tag: Optional[str] = parma["tag"]
    instrumental: bool = parma["instrumental"].value
    
    if prompt and isinstance(prompt,str):
        json_data={
            "mv": "chirp-v3-5",
            "gpt_description_prompt": prompt,
            "make_instrumental": instrumental
        }
        await _run(matcher,json_data)
    else:
        json_data={
            "prompt":lyrics,
            "tags": tag,
            "mv": "chirp-v3-5",
            "title": name,
            "make_instrumental": instrumental
        }
        await _run(matcher,json_data)
          
async def _run(matcher, json_data):
    ids="" 
    r={}    
    await matcher.send("开始生成歌曲", at_sender=True)
    session = aiohttp.ClientSession()
    try:
        res = await session.post(f"https://api.bltcy.ai/task/suno/v1/submit/music", headers=headers, json=json_data, timeout=10)
        r = await res.json()
    except:
        await matcher.send(f"生成失败，请求失败，请稍后再试", at_sender=True)
        await session.close()
        return
    if not r["code"] == "success":
        await matcher.send(f"生成失败，请稍后再试或检查余额，返回码：{r['code']}，返回消息：{r['message']}", at_sender=True)
        await session.close()
        return
    ids=r["data"]
    json_data2={
        "ids": [
            ids
        ],
        "action": "MUSIC"
    }
    await matcher.send("生成中", at_sender=True)
    not_ready = True
    i=0
    while not_ready:
        if i>3:
            logger.error("sunoai请求失败！")
            await session.close()
            await matcher.send("请求失败，请重试")
            return  
        rst={}
        await asyncio.sleep(10)
        try:
            res2 = await session.post(f"https://api.bltcy.ai/task/suno/v1/fetch", headers=headers, json=json_data2, timeout=10)
            rst = await res2.json()
        except Exception as e:
            logger.warning(f"请求失败，错误：{e}，重试第 {i + 1} 次...")
            i=i+1
            continue
        if rst["data"] is None:   
            await matcher.send(f"返回歌曲失败，请稍后再试，返回码：{rst['code']}，返回消息：{rst['message']}", at_sender=True)
            await session.close()
            return
        i=0
        if not rst["data"][0]["progress"]=="100%":
            logger.info("sunoai生成中...")
        elif rst["data"][0]["status"]=="SUCCESS":
            logger.success("sunoai生成完成！")
            not_ready = False
        elif rst["data"][0]["status"]=="FAILURE":
            logger.error("sunoai生成失败！")
            await session.close()
            await matcher.send("生成失败，请重试")
            return

    try:           
        if isinstance(rst["data"][0]["data"], list):
            for i in rst["data"][0]["data"]:
                url=i["audio_url"]
                title=i["title"]
                imgurl=i["image_url"]
                video=i["video_url"]
                tag=i["metadata"]["tags"]
                m = MusicShare(kind=MusicShareKind.Custom,title=title,content=tag,url=video,audio=url,thumbnail=imgurl)
                try:
                    await matcher.send(m)
                except:
                    await UniMessage.audio(raw=await get_record(url)).send()
                    pass
        else:
            await session.close()
            await matcher.send("返回歌曲失败")
            return
    except Exception as e:
        await session.close()
        await matcher.finish(f"返回歌曲失败 {e}")
        return
    await matcher.send("歌曲生成完成", at_sender=True)
    await session.close()
    
async def get_record(url):
    headers2 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
    }
    async with aiohttp.ClientSession() as client:
        async with client.get(url, headers=headers2, timeout=60) as resp:
            voice = await resp.read()
            return voice
    
