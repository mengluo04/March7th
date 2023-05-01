import random

from nonebot import get_driver, on_regex, require
from nonebot.params import RegexDict
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_datastore")
require("nonebot_plugin_saa")

from nonebot_plugin_saa import Image, MessageFactory, Text

from .config import plugin_config
from .models import character, light_cone, mapping_cn, update_resources

__plugin_meta__ = PluginMetadata(
    name="StarRailWiki",
    description="崩坏：星穹铁道百科",
    usage="(角色|武器)(攻略|图鉴|材料)",
    extra={
        "version": "1.0",
    },
)

driver = get_driver()


@driver.on_startup
async def _():
    await update_resources()


BASE_TYPE = [
    "角色",
    "光锥",
]
BASE_TYPE_RE = "(" + "|".join(BASE_TYPE) + ")"
WIKI_TYPE = ["图鉴", "攻略", "材料"]
WIKI_TYPE_RE = "(" + "|".join(WIKI_TYPE) + ")"

WIKI_RE = (
    rf"(?P<name>\w{{0,7}}?)(?P<type>{BASE_TYPE_RE}?{WIKI_TYPE_RE})(?P<res>\w{{0,7}})"
)

wiki_search = on_regex(WIKI_RE, priority=9, block=True)


@wiki_search.handle()
async def _(regex_dict: dict = RegexDict()):
    wiki_name: str = regex_dict["name"] or ""
    wiki_type: str = regex_dict.get("type") or ""
    res: str = regex_dict.get("res") or ""
    if wiki_name and res != "":
        await wiki_search.finish()
    if not wiki_name or not wiki_type:
        await wiki_search.finish()
    if "角色" in wiki_type:
        wiki_type_1 = "character"
    elif "光锥" in wiki_type:
        wiki_type_1 = "light_cone"
    else:
        wiki_type_1 = "all"
    if "材料" in wiki_type:
        wiki_type_2 = "material"
    else:
        wiki_type_2 = "overview"
    pic_content = ""
    if wiki_type_1 in {"all", "character"} and wiki_type_2 == "overview":
        if wiki_name in mapping_cn["character"]:
            name_en = mapping_cn["character"][wiki_name]
            character_overview = list(character[name_en]["character_overview"])
            pic_content = (
                random.choice(character_overview) if character_overview else ""
            )
    if (
        pic_content == ""
        and wiki_type_1 in {"all", "character"}
        and wiki_type_2 == "material"
    ):
        if wiki_name in mapping_cn["character"]:
            name_en = mapping_cn["character"][wiki_name]
            pic_content = character[name_en]["character_material"] or ""
    if pic_content == "" and wiki_type_1 in {"all", "light_cone"}:
        if wiki_name in mapping_cn["light_cone"]:
            name_en = mapping_cn["light_cone"][wiki_name]
            light_cone_overview = list(light_cone[name_en]["light_cone_overview"])
            pic_content = (
                random.choice(light_cone_overview) if light_cone_overview else ""
            )
    if pic_content == "":
        msg_builder = MessageFactory([Text(f"未找到『{regex_dict['name']}』的攻略")])
    else:
        msg_builder = MessageFactory(
            [
                Image(
                    f"{plugin_config.github_proxy}/{plugin_config.sr_wiki_url}/{pic_content}"
                )
            ]
        )
    await msg_builder.send(at_sender=True)
    await wiki_search.finish()