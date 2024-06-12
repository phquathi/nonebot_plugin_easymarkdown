import os
import base64
import re
import io
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment, Bot, Event
from nonebot.typing import T_State
from nonebot.params import CommandArg
from .to_md import markdown_to_html, create_pdf, pdf_to_images

md_command = on_command(".md", aliases={"markdown"}, priority=5)
current_directory = os.path.dirname(os.path.abspath(__file__))
pdf_path = os.path.join(current_directory, 'output.pdf')


@md_command.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State, args: Message = CommandArg()):
    md_text = args.extract_plain_text().strip()
    if not md_text:
        await md_command.finish("请发送需要格式化的Markdown文本。")

    await bot.send(event, "markdown图片生成中...请稍等...（如文本量大则响应时间稍久）")

    html = markdown_to_html(md_text)
    create_pdf(html, pdf_path)
    images = pdf_to_images(pdf_path)

    for i, img in enumerate(images):
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        await send_image(bot, event, img_byte_arr)

    plain_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', md_text)
    plain_text = re.sub(r'(```|~~|__|\*\*|\*|#+)', '', plain_text)
    await bot.send(event, plain_text)

    clean_up()


async def send_image(bot: Bot, event: Event, img_byte_arr: io.BytesIO):
    image_base64 = base64.b64encode(img_byte_arr.getvalue()).decode()
    image_segment = MessageSegment.image(f"base64://{image_base64}")
    await bot.send(event, Message(image_segment))


def clean_up():
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    for i in range(100):
        img_path = os.path.join(current_directory, f'output_page_{i + 1}.png')
        if os.path.exists(img_path):
            os.remove(img_path)
