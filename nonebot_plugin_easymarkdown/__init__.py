from nonebot.plugin import PluginMetadata

from .easy_md_main import *

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-easymarkdown",
    description="格式化markdown语法，并转化为可读性较好的图片",
    usage="pip install nonebot-plugin-easymarkdown",
    type="application",
    homepage="https://github.com/phquathi/nonebot_plugin_easymarkdown",
    config=None,
    supported_adapters={"~onebot.v11"}
)