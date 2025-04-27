#=============================================================================================
# 69Ranger Gentleman Community Bot
# Developed by Silver BlackWell
# Discord Bot for 69Ranger Gentleman Community
# This bot is designed to manage the community and provide various commands for users and admins.
# It includes features like sending direct messages, managing roles, and providing status updates.
# The bot is built using discord.py and includes error handling, logging, and timezone support.
# The bot is designed to be user-friendly and provide a seamless experience for community members.
# The bot is hosted on Replit and uses a keep_alive function to keep the bot running continuously.
#=============================================================================================
# Import necessary libraries
#=============================================================================================
import discord
import os
import logging
import pytz
import asyncio
import uuid
import re
import json

from datetime import datetime, timedelta
from typing import Optional
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, View, Button, Modal, TextInput
from itertools import zip_longest
from keep_alive import keep_alive

# Logging Configuration
logging.basicConfig(level=logging.DEBUG)

# Initialize bot and intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)
tree = bot.tree

# ตั้งค่า Timezone
THAI_TZ = pytz.timezone("Asia/Bangkok")

#=============================================================================================
# ⚙️ General Commands
#=============================================================================================
# ⚠️ /Event สร้างกิจกรรมพร้อมปุ่มตอบรับ
thai_days = ["วันจันทร์", "วันอังคาร", "วันพุธ", "วันพฤหัสบดี", "วันศุกร์", "วันเสาร์", "วันอาทิตย์"]
thai_months = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
               "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]

bangkok_tz = pytz.timezone("Asia/Bangkok")
events = {}

#=============================================================================================
# ⚠️ ปุ่มตอบรับกิจกรรม 
class EventView(View):
    def __init__(self, message, event_id, mod_links):
        super().__init__(timeout=None)
        self.message = message
        self.event_id = event_id
        self.mod_links = mod_links
        self.notified_users = set()  # เก็บรายชื่อผู้ที่กดปุ่ม "รับการแจ้งเตือน"   

    async def update_counts(self):
        event = events[self.event_id]
        counts = f"✅Accepted ( {len(event['joined'])} ) คน | ❌Declined ( {len(event['declined'])} ) คน | ❓Tentative ( {len(event['maybe'])} ) คน"
    
        # ตรวจสอบก่อนเพิ่ม ModDropdown
        if not any(isinstance(item, ModDropdown) for item in self.children):
            if self.mod_links:
                self.add_item(ModDropdown(self.mod_links))
    
        # ตรวจสอบก่อนเพิ่ม NotificationDropdown
        if not any(isinstance(item, NotificationDropdown) for item in self.children):
            self.add_item(NotificationDropdown(self.notified_users))
    
        embed = event['embed']
        if embed.fields:
            embed.set_field_at(0, name="จำนวนผู้ตอบรับ", value=counts, inline=False)
        else:
            embed.add_field(name="จำนวนผู้ตอบรับ", value=counts, inline=False)
        await self.message.edit(embed=embed, view=self)
        await update_summary_embed(event)

    async def handle_response(self, interaction, status):
        user = interaction.user.mention
        event = events[self.event_id]

        for lst in [event['joined'], event['declined'], event['maybe']]:
            if user in lst:
                lst.remove(user)

        if status == 'joined':
            event['joined'].append(user)
        elif status == 'declined':
            event['declined'].append(user)
        elif status == 'maybe':
            event['maybe'].append(user)

        await interaction.response.defer()
        await self.update_counts()

    @discord.ui.button(label="เข้าร่วม", style=discord.ButtonStyle.success, emoji="✅", row=0)
    async def join(self, interaction: discord.Interaction, button: Button):
        await self.handle_response(interaction, 'joined')

    @discord.ui.button(label="ไม่เข้าร่วม", style=discord.ButtonStyle.danger, emoji="❌", row=0)
    async def decline(self, interaction: discord.Interaction, button: Button):
        await self.handle_response(interaction, 'declined')

    @discord.ui.button(label="อาจจะมา", style=discord.ButtonStyle.secondary, emoji="❓", row=0)
    async def maybe(self, interaction: discord.Interaction, button: Button):
        await self.handle_response(interaction, 'maybe')

class ModDropdown(Select):
    def __init__(self, mod_links):
        # ลบค่าที่ซ้ำกันใน mod_links
        unique_links = list(dict.fromkeys(mod_links))  # ใช้ dict เพื่อกรองค่าซ้ำ
        options = [
            discord.SelectOption(label=f"Mod #{i+1}", value=link, description="คลิกเพื่อดูข้อมูล")
            for i, link in enumerate(unique_links)
        ]
        super().__init__(placeholder="🔗 ดู Mod เพิ่มเติม", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🔗 [คลิกเพื่อดู Mod]({self.values[0]})", ephemeral=True)

class NotificationDropdown(Select):
    def __init__(self, notified_users):
        options = [
            discord.SelectOption(label="เปิดการแจ้งเตือน", value="enable", emoji="🔔"),
            discord.SelectOption(label="ปิดการแจ้งเตือน", value="disable", emoji="🔕"),
        ]
        super().__init__(placeholder="🔔 การแจ้งเตือน", options=options)
        self.notified_users = notified_users

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        if self.values[0] == "enable":
            if user_id not in self.notified_users:
                self.notified_users.add(user_id)
                await interaction.response.send_message("✅ คุณจะได้รับการแจ้งเตือนทาง DM!", ephemeral=True)
            else:
                await interaction.response.send_message("❌ คุณได้เปิดการแจ้งเตือนไปแล้ว!", ephemeral=True)
        elif self.values[0] == "disable":
            if user_id in self.notified_users:
                self.notified_users.remove(user_id)
                await interaction.response.send_message("✅ คุณได้ปิดการแจ้งเตือนแล้ว!", ephemeral=True)
            else:
                await interaction.response.send_message("❌ คุณยังไม่ได้เปิดการแจ้งเตือน!", ephemeral=True)

#=============================================================================================
# ฟังก์ชันสำหรับอัปเดต Embed สรุปการตอบรับ
async def update_summary_embed(event):
    joined = event.get('joined') or []
    declined = event.get('declined') or []
    maybe = event.get('maybe') or []

    joined_str = "\n".join(joined) if joined else "-"
    declined_str = "\n".join(declined) if declined else "-"
    maybe_str = "\n".join(maybe) if maybe else "-"

    embed = discord.Embed(title="📋 สรุปการตอบรับ", color=discord.Color.blue())
    embed.add_field(name="เข้าร่วม", value=joined_str, inline=True)
    embed.add_field(name="ไม่เข้าร่วม", value=declined_str, inline=True)
    embed.add_field(name="อาจจะเข้าร่วม", value=maybe_str, inline=True)

    if 'thread_message' in event:
        try:
            await event['thread_message'].edit(embed=embed)
        except:
            pass
    else:
        thread_msg = await event['thread'].send(embed=embed)
        event['thread_message'] = thread_msg
#=============================================================================================
# ฟังก์ชันสำหรับส่งข้อความขอบคุณใน Thread ของกิจกรรม
async def send_thank_you_message(event):
    try:
        embed = discord.Embed(
            title="⚫ กิจกรรมสิ้นสุดแล้ว",
            description=(
                f"**{event['operation']}** ได้จบลงแล้ว!\n\n"
                "ขอบคุณสำหรับการเข้าร่วมกิจกรรม!\n"
                "หากมีข้อเสนอแนะหรือคำติชม โปรดแจ้งให้เราทราบเพื่อปรับปรุงในอนาคต 😊\n\n"
                "เราหวังว่าจะได้พบคุณในกิจกรรมครั้งถัดไป!"
            ),
            color=discord.Color.dark_gray()
        )
        embed.set_footer(
            text="69Ranger Gentleman Community Bot | พัฒนาโดย Silver BlackWell",
            icon_url="https://images-ext-1.discordapp.net/external/KHtLY8ldGkiHV5DbL-N3tB9Nynft4vdkfUMzQ5y2A_E/https/cdn.discordapp.com/avatars/1290696706605842482/df2732e4e949bcb179aa6870f160c615.png"
        )
        await event['thread'].send(embed=embed)
        logging.info(f"✅ ส่งข้อความขอบคุณใน Thread สำเร็จ")
    except Exception as e:
        logging.error(f"❌ เกิดข้อผิดพลาดในการส่งข้อความใน Thread: {e}")

#=============================================================================================
# ฟังก์ชันสำหรับการแจ้งเตือนกิจกรรม แจ้งเตือน 30 นาทีก่อนเริ่มกิจกรรม
async def event_timer(event_id):
    event = events[event_id]
    now = datetime.now(bangkok_tz)
    wait_time = (event['start_time'] - now).total_seconds() - 1800  # แจ้งเตือน 30 นาทีก่อนเริ่มกิจกรรม
    print(f"[TIMER] Waiting {wait_time} seconds until 30-min warning for event {event['operation']}")

    if wait_time > 0:
        await asyncio.sleep(wait_time)

        # แจ้งเตือน 30 นาทีก่อนเริ่มกิจกรรม (DM)
        if 'view' in event and hasattr(event['view'], 'notified_users'):
            for user_id in event['view'].notified_users:
                try:
                    user = await bot.fetch_user(user_id)
                    embed = discord.Embed(
                        title="🔔 แจ้งเตือนกิจกรรม",
                        description=(
                            f"อีก 30 นาทีจะถึงเวลา **{event['operation']}** กำลังจะเริ่มแล้ว!\n"
                            "ขอให้ผู้เล่นเตรียมตัวเข้า TeamSpeak 3 | Arma3 รอได้เลย!!!"
                        ),
                        color=discord.Color.orange()
                    )
                    embed.set_footer(
                        text="69Ranger Gentleman Community Bot | พัฒนาโดย Silver BlackWell",
                        icon_url="https://images-ext-1.discordapp.net/external/KHtLY8ldGkiHV5DbL-N3tB9Nynft4vdkfUMzQ5y2A_E/https/cdn.discordapp.com/avatars/1290696706605842482/df2732e4e949bcb179aa6870f160c615.png"
                    )
                    await user.send(embed=embed)
                except Exception as e:
                    print(f"[ERROR] DM failed for user {user_id}: {e}")

        # แจ้งเตือน 30 นาทีใน Thread
        try:
            embed_30_min = discord.Embed(
                title="🔔 แจ้งเตือนกิจกรรม",
                description=(
                    f"อีก 30 นาทีจะถึงเวลา **{event['operation']}** กำลังจะเริ่มแล้ว!\n"
                    "ขอให้ผู้เล่นเตรียมตัวเข้า TeamSpeak 3 | Arma3 รอได้เลย!!!"
                ),
                color=discord.Color.orange()
            )
            embed_30_min.set_footer(
                text="69Ranger Gentleman Community Bot | พัฒนาโดย Silver BlackWell",
                icon_url="https://images-ext-1.discordapp.net/external/KHtLY8ldGkiHV5DbL-N3tB9Nynft4vdkfUMzQ5y2A_E/https/cdn.discordapp.com/avatars/1290696706605842482/df2732e4e949bcb179aa6870f160c615.png"
            )
            await event['thread'].send(embed=embed_30_min)
            print(f"[INFO] Sent 30-minute warning to thread for event {event['operation']}")
        except Exception as e:
            print(f"[ERROR] Failed to send 30-minute warning to thread: {e}")


#=============================================================================================
#อัปเดตสถานะกิจกรรม 
    now = datetime.now(bangkok_tz)
    wait_until_start = (event['start_time'] - now).total_seconds()
    if wait_until_start > 0:
        await asyncio.sleep(wait_until_start)

    embed = event['embed']
    embed.title = f"🟢 {event['operation']} (อยู่ในระหว่างกำลังดำเนินการ)"
    try:
        await event['message'].edit(embed=embed, view=None)
    except discord.errors.NotFound:
        print(f"[ERROR] Message for event {event['operation']} not found. It may have been deleted.")
        return
    except Exception as e:
        print(f"[ERROR] Failed to edit message for event {event['operation']}: {e}")
        return
#=============================================================================================
# ส่ง DM เฉพาะผู้ที่กดปุ่ม "รับการแจ้งเตือน "ส่ง DM แจ้งว่าเริ่มกิจกรรมแล้ว
    for user_id in event['view'].notified_users:
        try:
            user = await bot.fetch_user(user_id)
            embed = discord.Embed(
                title="🔔 กิจกรรมเริ่มต้นแล้ว!",
                description=(
                    f"**{event['operation']}** ได้เริ่มต้นขึ้นแล้ว!\n"
                    "ขอให้ผู้เล่นเข้าเซิร์ฟเวอร์โดยด่วน!!!\n\n"
                    "หากคุณมีคำถามหรือปัญหาใด ๆ โปรดแจ้งให้ทีมงานทราบ"
                ),
                color=discord.Color.green()
            )
            embed.set_footer(
                text="69Ranger Gentleman Community Bot | พัฒนาโดย Silver BlackWell",
                icon_url="https://images-ext-1.discordapp.net/external/KHtLY8ldGkiHV5DbL-N3tB9Nynft4vdkfUMzQ5y2A_E/https/cdn.discordapp.com/avatars/1290696706605842482/df2732e4e949bcb179aa6870f160c615.png"
            )
            await user.send(embed=embed)
        except Exception as e:
            print(f"[ERROR] Failed to DM user {user_id}: {e}")
    # แจ้งใน Thread ว่ากิจกรรมเริ่มต้นแล้ว
    try:
        embed_start = discord.Embed(
            title="🟢 กิจกรรมเริ่มต้นแล้ว!",
            description=(
                f"**{event['operation']}** ได้เริ่มต้นขึ้นแล้ว!\n"
                "ขอให้ผู้เล่นเข้าเซิร์ฟเวอร์โดยด่วน!!!\n\n"
                "หากคุณมีคำถามหรือปัญหาใด ๆ โปรดแจ้งให้ทีมงานทราบ"
            ),
            color=discord.Color.green()
        )
        embed_start.set_footer(
            text="69Ranger Gentleman Community Bot | พัฒนาโดย Silver BlackWell",
            icon_url="https://images-ext-1.discordapp.net/external/KHtLY8ldGkiHV5DbL-N3tB9Nynft4vdkfUMzQ5y2A_E/https/cdn.discordapp.com/avatars/1290696706605842482/df2732e4e949bcb179aa6870f160c615.png"
        )
    
        # ส่ง Embed ไปยัง Thread
        await event['thread'].send(embed=embed_start)
        print(f"[INFO] Sent event start notification to thread for event {event['operation']}")
    except Exception as e:
        print(f"[ERROR] Failed to send event start notification to thread: {e}")
#=============================================================================================
    # รอจนถึงเวลาสิ้นสุดกิจกรรม
    now = datetime.now(bangkok_tz)
    wait_until_end = (event['end_time'] - now).total_seconds()
    if wait_until_end > 0:
        await asyncio.sleep(wait_until_end)

    # อัปเดตสถานะกิจกรรมเป็นจบ
    embed = event['embed']
    embed.title = f"⚫ {event['operation']} (กิจกรรมได้จบลงแล้ว)"
    try:
        await event['message'].edit(embed=embed, view=None)
    except Exception as e:
        print(f"[ERROR] Failed to update event status to finished: {e}")

        # ...หลังจากอัปเดต embed เป็นจบกิจกรรม...
    try:
        await event['message'].edit(embed=embed, view=None)
    except Exception as e:
        print(f"[ERROR] Failed to update event status to finished: {e}")

    # ส่งข้อความขอบคุณใน Thread ของกิจกรรม
    await send_thank_you_message(event)

#=============================================================================================

# ฟังก์ชันสำหรับการยืนยันการส่งข้อความ 
class ConfirmationView(View):
    def __init__(self):
        super().__init__(timeout=120)
        self.value = None

    @discord.ui.button(label="ยืนยัน", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        self.value = True
        await interaction.response.edit_message(content="✅ ยืนยันการสร้างกิจกรรมแล้ว", view=None)
        self.stop()

    @discord.ui.button(label="ยกเลิก", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        self.value = False
        await interaction.response.edit_message(content="❌ ยกเลิกการสร้างกิจกรรม", view=None)
        self.stop()
#=============================================================================================
#⚠️ /event สร้างกิจกรรมพร้อมปุ่มตอบรับ

@tree.command(name="event", description="สร้างกิจกรรมพร้อมปุ่มตอบรับ")
@app_commands.describe(
    channel="เลือกห้องที่จะโพสต์กิจกรรม",
    datetime_input="วันและเวลาของกิจกรรม (เช่น 01-01-2568 20:00-23:00)",
    operation="ชื่อ Operation (เช่น The Darknight Ep.4)",
    editor="ชื่อผู้แก้ไข (เช่น @Silver BlackWell)",
    preset="Mod ที่ใช้งาน (เช่น69Ranger RE Preset Edit V5)",
    tags="แท็กผู้เข้าร่วม เลือก Role ที่ต้องการแท็ก (ห้าม @everyone หรือ @here)",
    roles="บทบาทที่ได้เล่น (เช่น 75th Ranger Regiment)",
    story="เนื้อเรื่องของกิจกรรม (เช่น เรื่องราวที่เกี่ยวข้องกับกิจกรรม)",
    substory="ย่อหน้าเนื้อเรือง หรือ ข้อมูล HVT (ถ้ามี)",
    addmod="ลิงก์ Mod เพิ่มเติม (ใส่หลายลิงก์คั่นด้วยเครื่องหมายจุลภาค ',')(ถ้ามี)",
    image_url="URL ของรูปภาพกิจกรรม (ถ้ามี)"
)



async def create_event(interaction: discord.Interaction, 
    channel: discord.TextChannel, 
    datetime_input: str,
    operation: str, 
    editor: str, 
    preset: str, 
    tags: str, 
    roles: str, 
    story: str, 
    substory: Optional[str] = None, 
    addmod: Optional[str] = None,
    image_url: Optional[str] = None):

    try:
        # DEBUG: print input ที่รับเข้ามา
        print(f"DEBUG datetime_input: '{datetime_input}'")
        # รองรับรูปแบบ 22-04-2568 23:57-23:59 หรือ 22-04-2568 23:57 - 23:59 (มีหรือไม่มี space รอบขีดกลาง)
        pattern = r"^\d{2}-\d{2}-\d{4} \d{2}:\d{2}\s*-\s*\d{2}:\d{2}$"
        if not re.match(pattern, datetime_input.strip()):
            await interaction.response.send_message("❌ รูปแบบวันที่ไม่ถูกต้อง ใช้: 01-01-2568 20:00-23:00", ephemeral=True)
            return
    
        # แยกวันที่และเวลาทั้งหมด
        date_part, time_part = datetime_input.strip().split(" ", 1)
        start_time_str, end_time_str = [t.strip() for t in re.split(r"-", time_part)]
        day, month, year = date_part.split("-")
        hour, minute = start_time_str.split(":")
        end_hour, end_minute = end_time_str.split(":")
        year = int(year) - 543
        dt_start = datetime(int(year), int(month), int(day), int(hour), int(minute))
        dt_end = datetime(int(year), int(month), int(day), int(end_hour), int(end_minute))
        dt_start = bangkok_tz.localize(dt_start)
        dt_end = bangkok_tz.localize(dt_end)
    except Exception as e:
        print(f"[ERROR] datetime_input parse: {e}")
        await interaction.response.send_message("❌ รูปแบบวันที่ไม่ถูกต้อง ใช้: 01-01-2568 20:00-23:00", ephemeral=True)
        return

    timestamp = int(dt_start.timestamp())
    end_timestamp = int(dt_end.timestamp())
    counts_text = f"✅ joined (0) คน | ❌ Declined (0) คน | ❓ Tentative (0) คน"

    
    embed = discord.Embed(
        title=f"📌 {operation}",
        description=(
            f"<t:{timestamp}:F> | <t:{timestamp}:R>\n"
            f"**Editor:** {editor}\n"
            f"**Preset:** {preset}\n"
            f"**Tags:** {tags}\n\n"
            f"📖 **Story:**\n{story}\n\n"
            f"{substory if substory else ''}\n\n"
            f"**Roles:** {roles}\n"
        ),
        color=discord.Color.red()
    )
    embed.add_field(name="จำนวนผู้ตอบรับ", value=counts_text, inline=False)
    if image_url:
        embed.set_image(url=image_url)
    embed.set_footer(
        text="69Ranger Gentleman Community Bot | พัฒนาโดย Silver BlackWell",
        icon_url="https://images-ext-1.discordapp.net/external/KHtLY8ldGkiHV5DbL-N3tB9Nynft4vdkfUMzQ5y2A_E/https/cdn.discordapp.com/avatars/1290696706605842482/df2732e4e949bcb179aa6870f160c615.png"
    )

#=============================================================================================
    # แยก Mod Links
    mod_links = [link.strip() for link in addmod.split(",")] if addmod else []

    # แสดง Embed ตัวอย่างพร้อมปุ่มยืนยัน
    view = ConfirmationView()
    try:
        await interaction.response.send_message("⚠️ คุณต้องการส่งข้อความนี้หรือไม่?", embed=embed, view=view, ephemeral=True)
    except discord.errors.NotFound:
        await interaction.followup.send("❌ การโต้ตอบหมดอายุแล้ว กรุณาลองใหม่อีกครั้ง", ephemeral=True)
        return
    
    # รอการตอบสนองจากผู้ใช้
    await view.wait()
    
    if view.value is None:
        await interaction.followup.send("⏰ หมดเวลาการยืนยัน", ephemeral=True)
        return
    
    elif view.value:
        # ส่งข้อความไปยังช่องที่กำหนด
        msg = await channel.send(embed=embed, view=None)
        thread = await msg.create_thread(name=operation)
        event_id = str(uuid.uuid4())
        view = EventView(msg, event_id, mod_links)
        events[event_id] = {
            'operation': operation,
            'editor': editor,
            'preset': preset,
            'roles': roles,
            'story': story,
            'joined': [],
            'declined': [],
            'maybe': [],
            'embed': embed,
            'timestamp': timestamp,
            'start_time': dt_start,
            'end_time': dt_end,  # เพิ่มเวลาสิ้นสุดกิจกรรม
            'thread': thread,
            'message': msg,
            'view': view,  
        }
        await msg.edit(embed=embed, view=view)
        bot.loop.create_task(event_timer(event_id))
        await interaction.followup.send("✅ ข้อความถูกส่งเรียบร้อยแล้ว!", ephemeral=True)

        # DM ไปยัง Role ที่ถูกแท็กใน tags 
        if tags:
            tag_list = tags.split()
            sent_users = set()
            for tag in tag_list:
                if tag.startswith("<@&"):
                    role_id = int(tag.replace("<@&", "").replace(">", ""))
                    role = discord.utils.get(interaction.guild.roles, id=role_id)
                    if role:
                        msg_link = f"https://discord.com/channels/{interaction.guild.id}/{channel.id}/{msg.id}"
                        for member in role.members:
                            if member.bot or member.id in sent_users:
                                continue
                            try:
                                embed_dm = discord.Embed(
                                    title="📣 มีกิจกรรมใหม่!",
                                    description=(
                                        f"**📌 ชื่อกิจกรรม:** {operation}\n"
                                        f"**📅 วันที่:** <t:{timestamp}:D>\n"
                                        f"**🕒 เวลา:** <t:{timestamp}:t>\n\n"
                                        f"หากสนใจเข้าร่วมกิจกรรม สามารถตอบรับได้ที่โพสต์นี้\n"
                                        f"[🔗 ดูรายละเอียดกิจกรรม]({msg_link})"
                                    ),
                                    color=discord.Color.blue()
                                )
                                embed_dm.set_footer(
                                    text="69Ranger Gentleman Community Bot | พัฒนาโดย Silver BlackWell",
                                    icon_url="https://images-ext-1.discordapp.net/external/KHtLY8ldGkiHV5DbL-N3tB9Nynft4vdkfUMzQ5y2A_E/https/cdn.discordapp.com/avatars/1290696706605842482/df2732e4e949bcb179aa6870f160c615.png"
                                )
                                await member.send(embed=embed_dm)
                                sent_users.add(member.id)
                            except Exception as e:
                                logging.warning(f"❌ ไม่สามารถส่งข้อความให้ {member.name}: {e}")
#=============================================================================================
#⚠️ /backup_events ทดสอบการ Backup ข้อมูล
@bot.tree.command(name="backup_events", description="ทดสอบการ Backup ข้อมูลกิจกรรม")
async def backup_events_command(interaction: discord.Interaction):
    try:
        # แปลง embed เป็น dict ก่อนบันทึก
        backup_data = {
            event_id: {
                **event_data,
                'embed': event_data['embed'].to_dict()  # แปลง embed เป็น dict
            }
            for event_id, event_data in events.items()
        }
        with open("events_backup.json", "w", encoding="utf-8") as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=4, default=datetime_converter)
        await interaction.response.send_message("✅ Backup ข้อมูล Event สำเร็จ!", ephemeral=True)
        logging.info("✅ Backup ข้อมูล Event สำเร็จ")
    except Exception as e:
        await interaction.response.send_message(f"❌ เกิดข้อผิดพลาดในการ Backup ข้อมูล: {e}", ephemeral=True)
        logging.error(f"❌ เกิดข้อผิดพลาดในการ Backup ข้อมูล: {e}")

# ฟังก์ชันสำหรับ Backup ข้อมูลกิจกรรม

def datetime_converter(o):
    if isinstance(o, datetime):
        return o.isoformat()  # แปลง datetime เป็น ISO 8601 string
    elif isinstance(o, discord.Embed):
        return o.to_dict()  # แปลง Embed เป็น dict
    elif isinstance(o, discord.Thread):
        return {"id": o.id}  # เก็บเฉพาะ ID ของ Thread
    elif isinstance(o, discord.Message):
        return {"id": o.id, "channel_id": o.channel.id}  # เก็บเฉพาะ ID ของ Message และ Channel
    raise TypeError(f"Type {type(o)} not serializable")

async def backup_events_periodically():
    while True:
        try:
            # แปลงข้อมูลก่อนบันทึก
            with open("events_backup.json", "w", encoding="utf-8") as f:
                json.dump(events, f, ensure_ascii=False, indent=4, default=datetime_converter)
            logging.info("✅ Backup ข้อมูล Event สำเร็จ")
        except Exception as e:
            logging.error(f"❌ เกิดข้อผิดพลาดในการ Backup ข้อมูล: {e}")
        await asyncio.sleep(1800)  # รอ 30 นาที (1800 วินาที) ก่อน Backup ครั้งถัดไป

# ฟังก์ชันสำหรับ Restore ข้อมูล
async def restore_events():
    global events
    try:
        with open("events_backup.json", "r", encoding="utf-8") as f:
            restored_events = json.load(f)
            for event_id, event_data in restored_events.items():
                # แปลง start_time และ end_time จาก string เป็น datetime
                event_data['start_time'] = datetime.fromisoformat(event_data['start_time']).astimezone(pytz.timezone("Asia/Bangkok"))
                event_data['end_time'] = datetime.fromisoformat(event_data['end_time']).astimezone(pytz.timezone("Asia/Bangkok"))

                # แปลง embed จาก dict เป็น discord.Embed
                embed_data = event_data['embed']
                event_data['embed'] = discord.Embed.from_dict(embed_data)

                # แปลง thread จาก dict เป็น discord.Thread (ใช้ ID เพื่อค้นหา Thread)
                thread_id = event_data['thread']['id']
                event_data['thread'] = bot.get_channel(thread_id)

                # กู้คืน message จาก message.id และ channel.id
                message_data = event_data['message']
                channel = bot.get_channel(message_data['channel_id'])
                event_data['message'] = await channel.fetch_message(message_data['id'])

                # สร้าง View ใหม่
                view = EventView(event_data['message'], event_id, event_data.get('mod_links', []))
                event_data['view'] = view

                # สร้าง Task สำหรับ event_timer
                bot.loop.create_task(event_timer(event_id))
                logging.info(f"🔄 กำลัง Restore ข้อมูล Event ID: {event_id}")

                # อัปเดต events
                events[event_id] = event_data

        logging.info("✅ Restore ข้อมูล Event สำเร็จ")
    except FileNotFoundError:
        logging.warning("⚠️ ไม่พบไฟล์ Backup ข้อมูล Event")
    except Exception as e:
        logging.error(f"❌ เกิดข้อผิดพลาดในการ Restore ข้อมูล: {e}")


#=============================================================================================
#⚠️ /Help แสดงคำสั่งทั้งหมดของบอท
@bot.tree.command(name="help", description="แสดงคำสั่งทั้งหมดของบอท")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📜 รายการคำสั่งของบอท",
        description="คำสั่งทั้งหมดที่สามารถใช้งานได้ในเซิร์ฟเวอร์นี้",
        color=discord.Color.blue()
    )
    # หมวดหมู่คำสั่งทั่วไป
    embed.add_field(
        name="⚙️ คำสั่งทั่วไป",
        value=(
            "`/ping` - ทดสอบว่าบอทออนไลน์หรือไม่\n"
            "`/status` - แสดงสถานะของบอท\n"
            "`/help` - แสดงคำสั่งทั้งหมดของบอท"
        ),
        inline=False
    )
    # หมวดหมู่คำสั่งสำหรับแอดมิน
    embed.add_field(
        name="📩 คำสั่งสำหรับแอดมิน",
        value=(
            "`/announce` - ส่งข้อความประกาศไปยังห้องที่กำหนด\n"
            "`/dm` - ส่งข้อความ DM ให้สมาชิกใน Role\n"
            "`/event` - สร้างกิจกรรมพร้อมปุ่มตอบรับ\n"
            "`/reset` - รีเซ็ตคำสั่งบอททั้งหมด"
        ),
        inline=False
    )
    # หมวดหมู่คำสั่งจัดการห้องเสียง
    embed.add_field(
        name="🎙️ คำสั่งจัดการห้องเสียง",
        value=(
            "`/join` - ให้บอทเข้าร่วมห้องเสียง\n"
            "`/leave` - ให้บอทออกจากห้องเสียง"
        ),
        inline=False
    )
    # หมวดหมู่คำสั่งที่เกี่ยวข้องกับ DM
    embed.add_field(
        name="📬 คำสั่งที่เกี่ยวข้องกับ DM",
        value=(
            "`/dm` - ส่งข้อความ DM ให้สมาชิกใน Role\n"
            "`/event` - ส่ง DM แจ้งเตือนกิจกรรมให้สมาชิก\n"
            "ระบบต้อนรับสมาชิกใหม่ - ส่งข้อความต้อนรับผ่าน DM\n"
            "ระบบแจ้งลาก่อน - ส่งข้อความลาก่อนให้สมาชิกที่ออกจากเซิร์ฟเวอร์"
        ),
        inline=False
    )
    embed.set_footer(
        text="69Ranger Gentleman Community Bot | พัฒนาโดย Silver BlackWell",
        icon_url="https://images-ext-1.discordapp.net/external/KHtLY8ldGkiHV5DbL-N3tB9Nynft4vdkfUMzQ5y2A_E/https/cdn.discordapp.com/avatars/1290696706605842482/df2732e4e949bcb179aa6870f160c615.png"
    )
    embed.set_thumbnail(
        url="https://images-ext-1.discordapp.net/external/KHtLY8ldGkiHV5DbL-N3tB9Nynft4vdkfUMzQ5y2A_E/https/cdn.discordapp.com/avatars/1290696706605842482/df2732e4e949bcb179aa6870f160c615.png"
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)
#=============================================================================================
# ⚠️ /ping ทดสอบสถานะของบอท
@bot.tree.command(name="ping", description="ทดสอบสถานะของบอท")
async def slash_ping(interaction: discord.Interaction):
    await interaction.response.send_message("บอทยังทำงานอยู่ 🟢")
#=============================================================================================
#⚠️ /reset สำหรับการรีเซ็ตคำสั่งบอททั้งหมด (เฉพาะแอดมิน)
@bot.tree.command(name="reset", description="รีเซ็ตคำสั่งบอททั้งหมด (เฉพาะแอดมิน)")
async def reset_command(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ (ต้องเป็นแอดมิน)", ephemeral=True)
        return

    try:
        synced = await bot.tree.sync()
        await interaction.response.send_message(f"✅ รีเซ็ตคำสั่งทั้งหมดสำเร็จ ({len(synced)} คำสั่งถูกซิงค์ใหม่)", ephemeral=True)
        logging.info(f"✅ คำสั่งทั้งหมดถูกรีเซ็ตและซิงค์ใหม่ ({len(synced)} คำสั่ง)")
    except Exception as e:
        await interaction.response.send_message(f"❌ เกิดข้อผิดพลาดในการรีเซ็ตคำสั่ง: {e}", ephemeral=True)
        logging.error(f"❌ เกิดข้อผิดพลาดในการรีเซ็ตคำสั่ง: {e}")
#=============================================================================================
# ⚠️ /status เพื่อแสดงสถานะของบอท
@bot.tree.command(name="status", description="แสดงสถานะของบอท")
async def status_command(interaction: discord.Interaction):
    # คำนวณข้อมูลเพิ่มเติม
    latency = round(bot.latency * 1000)  # Latency ของบอท (ms)
    current_time = datetime.now(THAI_TZ).strftime("%d-%m-%Y %H:%M:%S")  # เวลาปัจจุบันในเขตเวลาไทย
    total_guilds = len(bot.guilds)  # จำนวนเซิร์ฟเวอร์ที่บอทอยู่
    total_members = sum(guild.member_count for guild in bot.guilds)  # จำนวนสมาชิกทั้งหมดในเซิร์ฟเวอร์
    uptime_seconds = (datetime.now() - bot.start_time).total_seconds()  # เวลาทำงานของบอท
    uptime = f"{int(uptime_seconds // 3600)} ชั่วโมง {int((uptime_seconds % 3600) // 60)} นาที"

    # สร้าง Embed สำหรับแสดงสถานะ
    embed = discord.Embed(
        title="📊 สถานะของบอท",
        description="ข้อมูลสถานะปัจจุบันของบอท",
        color=discord.Color.green()
    )
    embed.add_field(name="🟢 สถานะ", value="ออนไลน์", inline=False)
    embed.add_field(name="� Latency", value=f"{latency} ms", inline=False)
    embed.add_field(name="⏰ เวลาปัจจุบัน", value=current_time, inline=False)
    embed.add_field(name="🌐 จำนวนเซิร์ฟเวอร์", value=f"{total_guilds} เซิร์ฟเวอร์", inline=False)
    embed.add_field(name="👥 จำนวนสมาชิกทั้งหมด", value=f"{total_members} คน", inline=False)
    embed.add_field(name="⏳ เวลาทำงาน", value=uptime, inline=False)
    embed.set_footer(text="69Ranger Gentleman Community Bot | พัฒนาโดย Silver BlackWell")

    # ส่ง Embed ไปยังผู้ใช้
    await interaction.response.send_message(embed=embed, ephemeral=True)

#=============================================================================================
# 📩 Admin Commands
#=============================================================================================
#⚠️ /announce ส่งข้อความไปยังห้องที่กำหนด
@bot.tree.command(name="announce", description="ให้บอทส่งข้อความประกาศไปยังห้องที่กำหนด (เฉพาะแอดมิน)")
@app_commands.describe(
    channel="เลือกห้องที่ต้องการส่งข้อความ",
    message="ข้อความที่จะส่ง",
    image_url="URL ของรูปภาพ (ถ้ามี)"
)
async def announce_command(interaction: discord.Interaction, channel: discord.TextChannel, message: str, image_url: Optional[str] = None):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ (ต้องเป็นแอดมิน)", ephemeral=True)
        return

    # แสดงข้อความตัวอย่างพร้อมปุ่มยืนยัน
    embed = discord.Embed(
        title="📢 ยืนยันการส่งข้อความประกาศ",
        description=f"**ข้อความที่จะส่ง:**\n{message}\n\n**ห้อง:** {channel.mention}",
        color=discord.Color.orange()
    )
    if image_url:
        embed.set_image(url=image_url)

    view = ConfirmationView()
    try:
        await interaction.response.send_message("⚠️ คุณต้องการส่งข้อความนี้หรือไม่?", embed=embed, view=view, ephemeral=True)
    except discord.errors.NotFound:
        await interaction.followup.send("❌ การโต้ตอบหมดอายุแล้ว กรุณาลองใหม่อีกครั้ง", ephemeral=True)
        return
    
    # รอการตอบสนองจากผู้ใช้
    await view.wait()
    
    if view.value is None:
        await interaction.followup.send("⏰ หมดเวลาการยืนยัน", ephemeral=True)
        return
    elif view.value:
        try:
            embed = discord.Embed(description=message, color=discord.Color.green())
            if image_url:
                embed.set_image(url=image_url)
            await channel.send(embed=embed)
            await interaction.followup.send(f"✅ ส่งข้อความไปยังห้อง {channel.mention} สำเร็จ!", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send(f"❌ ไม่สามารถส่งข้อความไปยังห้อง {channel.mention} ได้ (บอทอาจไม่มีสิทธิ์)", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ เกิดข้อผิดพลาด: {e}", ephemeral=True)
    else:
        await interaction.followup.send("❌ การส่งข้อความถูกยกเลิก", ephemeral=True)

#=============================================================================================
#⚠️ /dm ส่งข้อความ DM ให้สมาชิกเฉพาะ Role
@bot.tree.command(name="dm", description="ส่ง DM ให้สมาชิกเฉพาะ Role (เฉพาะแอดมิน)")
@app_commands.describe(
    role="เลือก Role ที่ต้องการส่งถึง",
    message="ข้อความที่จะส่ง",
    image_url="URL ของรูปภาพ (ถ้ามี)"
)
async def dm(interaction: discord.Interaction, role: discord.Role, message: str, image_url: Optional[str] = None):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ (ต้องเป็นแอดมิน)", ephemeral=True)
        return

    members = [m for m in role.members if not m.bot]
    if not members:
        await interaction.response.send_message("❌ ไม่มีสมาชิกใน Role นี้ที่สามารถส่ง DM ได้", ephemeral=True)
        return

    # แสดงข้อความตัวอย่างพร้อมปุ่มยืนยัน
    embed = discord.Embed(
        title="📢 ยืนยันการส่งข้อความ DM",
        description=f"**ข้อความที่จะส่ง:**\n{message}\n\n**Role:** {role.mention}\n**จำนวนสมาชิก:** {len(members)} คน",
        color=discord.Color.orange()
    )
    if image_url:
        embed.set_image(url=image_url)

    view = ConfirmationView()
    await interaction.response.send_message("⚠️ คุณต้องการส่งข้อความนี้หรือไม่?", embed=embed, view=view, ephemeral=True)

    # รอการตอบสนองจากผู้ใช้
    await view.wait()

    if view.value is None:
        await interaction.followup.send("⏰ หมดเวลาการยืนยัน", ephemeral=True)
        return
    elif view.value:
        success, failed = 0, 0
        for member in members:
            try:
                # ส่งข้อความ DM พร้อมรูปภาพ
                embed = discord.Embed(description=message, color=discord.Color.green())
                if image_url:
                    embed.set_image(url=image_url)
                await member.send(embed=embed)
                success += 1
            except discord.Forbidden:
                failed += 1
                logging.warning(f"❌ ไม่สามารถส่งข้อความให้ {member.name} ได้ (สมาชิกอาจปิดการรับ DM)")

        await interaction.followup.send(
            f"✅ ส่งสำเร็จ: {success} คน\n❌ ส่งไม่สำเร็จ: {failed} คน", ephemeral=True
        )
    else:
        await interaction.followup.send("❌ การส่งข้อความถูกยกเลิก", ephemeral=True)
#=============================================================================================
#⚠️ /join ให้บอทเข้าร่วมห้องเสียง
@bot.tree.command(name="join", description="ให้บอทเข้าร่วมห้องเสียง (Voice Channel)")
async def join_command(interaction: discord.Interaction):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❌ คุณต้องอยู่ในห้องเสียงก่อนถึงจะใช้คำสั่งนี้ได้", ephemeral=True)
        return

    channel = interaction.user.voice.channel
    try:
        await channel.connect()
        await interaction.response.send_message(f"✅ บอทเข้าร่วมห้องเสียง {channel.name} สำเร็จ!", ephemeral=True)
    except discord.ClientException:
        await interaction.response.send_message("❌ บอทอยู่ในห้องเสียงแล้ว", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("❌ บอทไม่มีสิทธิ์เข้าร่วมห้องเสียงนี้", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ เกิดข้อผิดพลาด: {e}", ephemeral=True)
#=============================================================================================
#⚠️ /leave ให้บอทออกจากห้องเสียง
@bot.tree.command(name="leave", description="ให้บอทออกจากห้องเสียง (Voice Channel)")
async def leave_command(interaction: discord.Interaction):
    if not interaction.guild.voice_client:
        await interaction.response.send_message("❌ บอทไม่ได้อยู่ในห้องเสียง", ephemeral=True)
        return

    try:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("✅ บอทออกจากห้องเสียงสำเร็จ!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ เกิดข้อผิดพลาด: {e}", ephemeral=True)

#=============================================================================================
# 🛠️ Events
#=============================================================================================
#⚠️ auto Role เพิ่ม Role ให้สมาชิกใหม่
@bot.event
async def on_member_join(member):
    try:
        role = discord.utils.get(member.guild.roles, name="Civilian")
        if role and member.guild.me.guild_permissions.manage_roles:
            await member.add_roles(role)
            logging.info(f"✅ ให้ Role '{role.name}' กับ {member.name} แล้ว")
        else:
            logging.warning("❌ ไม่พบ Role 'Civilian' หรือบอทไม่มีสิทธิ์จัดการ Role")
    except discord.Forbidden:
        logging.error(f"❌ ไม่สามารถเพิ่ม Role ให้ {member.name} ได้ (ไม่มีสิทธิ์)")

#=============================================================================================
# ⚠️ ส่งข้อความต้อนรับผ่าน DM
    try:
        welcome_message = (
            f"สวัสดี {member.mention}! ยินดีต้อนรับสู่เซิร์ฟเวอร์ของเรา 🎉\n"
            "โปรดอ่านกฎในช่อง <#1211204645410570261> และสนุกกับการพูดคุยในชุมชนของเรา!\n"
            "ถ้าคุณมีคำถามหรือปัญหา สอบถามได้ที่ <#1281566308097462335>\n"
            "หากต้องการเข้าร่วม สามารถกรอกใบสมัครได้ที่ <#1349726875030913085>"
        )
        await member.send(welcome_message)
        logging.info(f"✅ ส่งข้อความต้อนรับไปยัง {member.name}'s DM")
    except discord.Forbidden:
        logging.warning(f"❌ ไม่สามารถส่งข้อความให้ {member.name} ได้ (สมาชิกอาจปิดการรับ DM)")

#=============================================================================================
# ⚠️ ส่งข้อความ DM ให้กับสมาชิกที่ออกจากเซิร์ฟเวอร์
@bot.event
async def on_member_remove(member):
    try:
        farewell_message = (
            f"สวัสดี {member.name},\n"
            "เราสังเกตว่าคุณได้ออกจากเซิร์ฟเวอร์ของเราแล้ว 😢\n"
            "หากมีข้อเสนอแนะหรือคำถามใด ๆ โปรดแจ้งให้เราทราบ เรายินดีต้อนรับคุณกลับมาเสมอ!\n"
            "หากคุณต้องการกลับมา Join our Discord : https://discord.gg/277nRyGhmq\n"
            "เราหวังว่าจะได้พบคุณอีกครั้งในอนาคต ❤️"
        )
        await member.send(farewell_message)
        logging.info(f"✅ ส่งข้อความลาไปยัง {member.name}'s DM")
    except discord.Forbidden:
        logging.warning(f"❌ ไม่สามารถส่งข้อความให้ {member.name} ได้ (สมาชิกอาจปิดการรับ DM)")
    except Exception as e:
        logging.error(f"❌ เกิดข้อผิดพลาด: {e}")
#=============================================================================================
# ⚠️ Bot Ready Event
@bot.event
async def on_ready():
    bot.start_time = datetime.now()  # เก็บเวลาที่บอทเริ่มทำงาน
    await restore_events()  # โหลดข้อมูลจากไฟล์ Backup

    logging.info(f'✅ Logged in as {bot.user}')
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="Arma 3 | 69RangerGTMCommunity")
    )
    try:
        synced = await bot.tree.sync()
        logging.info(f"✅ ซิงค์คำสั่ง {len(synced)} คำสั่งเรียบร้อยแล้ว")
    except Exception as e:
        logging.error(f"❌ เกิดข้อผิดพลาดในการซิงค์คำสั่ง: {e}")

    # เริ่ม Task สำหรับ Backup ข้อมูล Event ทุกๆ 30 นาที
    bot.loop.create_task(backup_events_periodically())
    logging.info("✅ Task สำหรับ Backup ข้อมูล Event เริ่มทำงานแล้ว")
#=============================================================================================
# ⚠️ Error Handling
#=============================================================================================
#⚠️ การจัดการข้อผิดพลาดทั่วไป
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ ไม่พบคำสั่งนี้")
    else:
        await ctx.send("❌ เกิดข้อผิดพลาดบางอย่าง")
        raise error

#=============================================================================================
# Run Bot
#=============================================================================================
keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
