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

from datetime import datetime, timedelta
from typing import Optional
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Modal, TextInput
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

class EventView(View):
    def __init__(self, message, event_id, mod_links):
        super().__init__(timeout=None)
        self.message = message
        self.event_id = event_id
        self.mod_links = mod_links
        self.notified_users = set()  # เก็บรายชื่อผู้ที่กดปุ่ม "รับการแจ้งเตือน"

    async def update_counts(self):
        event = events[self.event_id]
        counts = f"✅เข้าร่วม {len(event['joined'])} คน | ❌ไม่เข้าร่วม {len(event['declined'])} คน | ❓อาจจะเข้า {len(event['maybe'])} คน"

        embed = event['embed']
        if embed.fields:
            embed.set_field_at(0, name="จำนวนผู้ตอบรับ", value=counts, inline=False)
        else:
            embed.add_field(name="จำนวนผู้ตอบรับ", value=counts, inline=False)
        await self.message.edit(embed=embed, view=self)

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

    @discord.ui.button(label="🔗Mod เพิ่มเติม", style=discord.ButtonStyle.primary, emoji="🔗", row=1)
    async def view_mod(self, interaction: discord.Interaction, button: Button):
        if self.mod_links:
            embed = discord.Embed(
                title="🔗 Mod เพิ่มเติม",
                description="ลิงก์ Mod ที่เกี่ยวข้องกับกิจกรรมนี้:",
                color=discord.Color.blue()
            )
            for i, link in enumerate(self.mod_links, start=1):
                embed.add_field(name=f"Mod #{i}", value=f"[คลิกเพื่อดูข้อมูล]({link})", inline=False)

            embed.set_footer(
                text="69Ranger Gentleman Community Bot | พัฒนาโดย Silver BlackWell",
                icon_url="https://images-ext-1.discordapp.net/external/KHtLY8ldGkiHV5DbL-N3tB9Nynft4vdkfUMzQ5y2A_E/https/cdn.discordapp.com/avatars/1290696706605842482/df2732e4e949bcb179aa6870f160c615.png"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="🔗 Mod เพิ่มเติม",
                description="❌ Preset-mod ไม่มีการเพิ่ม mod ใดๆ",
                color=discord.Color.red()
            )
            embed.set_footer(
                text="69Ranger Gentleman Community Bot | พัฒนาโดย Silver BlackWell",
                icon_url="https://images-ext-1.discordapp.net/external/KHtLY8ldGkiHV5DbL-N3tB9Nynft4vdkfUMzQ5y2A_E/https/cdn.discordapp.com/avatars/1290696706605842482/df2732e4e949bcb179aa6870f160c615.png"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="รับการแจ้งเตือน", style=discord.ButtonStyle.success, emoji="🔔", row=1)
    async def notify(self, interaction: discord.Interaction, button: Button):
        user_id = interaction.user.id
        if user_id not in self.notified_users:
            self.notified_users.add(user_id)
            await interaction.response.send_message("✅ คุณจะได้รับการแจ้งเตือนทาง DM!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ คุณได้สมัครรับการแจ้งเตือนไปแล้ว!", ephemeral=True)

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


async def event_timer(event_id):
    event = events[event_id]
    now = datetime.now(bangkok_tz)
    wait_time = (event['start_time'] - now).total_seconds() - 1800  # แจ้งเตือน 30 นาทีก่อนเริ่มกิจกรรม
    print(f"[TIMER] Waiting {wait_time} seconds until 30-min warning for event {event['operation']}")

    if wait_time > 0:
        await asyncio.sleep(wait_time)

        # แจ้งเตือน 30 นาทีก่อนเริ่มกิจกรรม
        for user_id in event['view'].notified_users:  # ส่ง DM เฉพาะผู้ที่กดปุ่ม "รับการแจ้งเตือน"
            try:
                user = await bot.fetch_user(user_id)
                embed = discord.Embed(
                    title="� แจ้งเตือนกิจกรรม",
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

    now = datetime.now(bangkok_tz)
    wait_until_start = (event['start_time'] - now).total_seconds()
    if wait_until_start > 0:
        await asyncio.sleep(wait_until_start)

    # แจ้งว่าเริ่มกิจกรรมแล้ว
    embed = event['embed']
    embed.title = f"🟢 {event['operation']} (อยู่ในระหว่างกำลังดำเนินการ)"
    await event['message'].edit(embed=embed, view=None)

    # ส่ง DM แจ้งว่าเริ่มกิจกรรมแล้ว
    for user_id in event['view'].notified_users:  # ส่ง DM เฉพาะผู้ที่กดปุ่ม "รับการแจ้งเตือน"
        try:
            user = await bot.fetch_user(user_id)
            embed = discord.Embed(
                title="� กิจกรรมเริ่มต้นแล้ว!",
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


    now = datetime.now(bangkok_tz)
    wait_until_start = (event['start_time'] - now).total_seconds()
    if wait_until_start > 0:
        await asyncio.sleep(wait_until_start)

    embed = event['embed']
    embed.title = f"🟢 {event['operation']} (อยู่ในระหว่างกำลังดำเนินการ)"
    await event['message'].edit(embed=embed, view=None)

    # ส่ง DM แจ้งว่าเริ่มกิจกรรมแล้ว
    for user_mention in event['joined'] + event['maybe']:  # รวมผู้ที่ตอบว่าเข้าร่วมและอาจจะเข้าร่วม
        try:
            user_id = int(user_mention.replace("<@!", "").replace("<@", "").replace(">", ""))
            user = await bot.fetch_user(user_id)
            
            # สร้าง Embed สำหรับแจ้งเตือน
            embed = discord.Embed(
                title="🟢 กิจกรรมเริ่มต้นแล้ว!",
                description=(
                    f"**{event['operation']}** ได้เริ่มต้นขึ้นแล้ว!\n"
                    "ขอให้ผู้เล่นเข้าเซิร์ฟเวอร์โดยด่วน!!!"
                ),
                color=discord.Color.green()
            )
            embed.set_footer(
                text="69Ranger Gentleman Community Bot | พัฒนาโดย Silver BlackWell",
                icon_url="https://images-ext-1.discordapp.net/external/KHtLY8ldGkiHV5DbL-N3tB9Nynft4vdkfUMzQ5y2A_E/https/cdn.discordapp.com/avatars/1290696706605842482/df2732e4e949bcb179aa6870f160c615.png"
            )
            await user.send(embed=embed)
        except Exception as e:
            print(f"[ERROR] Failed to DM user {user_mention}: {e}")
            try:
                # ส่งข้อความแจ้งเตือนใน Thread
                embed = discord.Embed(
                    title="🟢 กิจกรรมเริ่มต้นแล้ว!",
                    description=(
                        f"{user_mention} **{event['operation']}** ได้เริ่มต้นขึ้นแล้ว!\n"
                        "ขอให้ผู้เล่นเข้าเซิร์ฟเวอร์โดยด่วน!!!"
                    ),
                    color=discord.Color.green()
                )
                await event['thread'].send(embed=embed)
            except Exception as thread_error:
                print(f"[ERROR] Failed to send to thread for {user_mention}: {thread_error}")

    # รอ 3 ชั่วโมง 30 นาที แล้วอัปเดตสถานะเป็นจบ
    await asyncio.sleep(3.5 * 3600)
    
    # อัปเดตสถานะกิจกรรมเป็นจบ
    embed.title = f"⚫ {event['operation']} (กิจกรรมได้จบลงแล้ว)"
    await event['message'].edit(embed=embed)
    
    # ส่ง DM ขอบคุณผู้เข้าร่วม
    for user_mention in event['joined']:
        try:
            user_id = int(user_mention.replace("<@!", "").replace("<@", "").replace(">", ""))
            user = await bot.fetch_user(user_id)
            
            # สร้าง Embed สำหรับขอบคุณ
            embed = discord.Embed(
                title="⚫ กิจกรรมสิ้นสุดแล้ว",
                description=(
                    f"**{event['operation']}** ได้จบลงแล้ว\n"
                    "ขอบคุณสำหรับการเข้าร่วมกิจกรรม!\n"
                    "หากมีข้อเสนอแนะหรือคำติชม โปรดแจ้งให้เราทราบเพื่อปรับปรุงในอนาคต 😊"
                ),
                color=discord.Color.dark_gray()
            )
            embed.set_footer(
                text="69Ranger Gentleman Community Bot | พัฒนาโดย Silver BlackWell",
                icon_url="https://images-ext-1.discordapp.net/external/KHtLY8ldGkiHV5DbL-N3tB9Nynft4vdkfUMzQ5y2A_E/https/cdn.discordapp.com/avatars/1290696706605842482/df2732e4e949bcb179aa6870f160c615.png"
            )
            await user.send(embed=embed)
        except Exception as e:
            print(f"[ERROR] Failed to DM user {user_mention}: {e}")




class ConfirmationView(View):
    def __init__(self):
        super().__init__(timeout=60)  # ตั้งเวลาหมดอายุ 60 วินาที
        self.value = None

    @discord.ui.button(label="ยืนยัน", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        self.value = True
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="ยกเลิก", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        self.value = False
        await interaction.response.defer()
        self.stop()

@tree.command(name="event", description="สร้างกิจกรรมพร้อมปุ่มตอบรับ")
@app_commands.describe(
    channel="เลือกห้องที่จะโพสต์กิจกรรม",
    datetime_input="วันและเวลาของกิจกรรม (เช่น 01-01-2568 20:30)",
    operation="ชื่อ Operation (เช่น The Darknight Ep.4)",
    editor="ชื่อผู้แก้ไข (เช่น @Silver BlackWell)",
    preset="Mod ที่ใช้งาน (เช่น69Ranger RE Preset Edit V5)",
    tags="แท็กผู้เข้าร่วม เลือก Role ที่ต้องการแท็ก (ห้าม @everyone หรือ @here)",
    roles="บทบาทที่ได้เล่น (เช่น 75th Ranger Regiment)",
    story="เนื้อเรื่องของกิจกรรม (เช่น เรื่องราวที่เกี่ยวข้องกับกิจกรรม)",
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
    addmod: Optional[str] = None,
    image_url: Optional[str] = None):

    try:
        day, month, year_time = datetime_input.split("-")
        year, time = year_time.split(" ")
        hour, minute = time.split(":")
        year = int(year) - 543
        dt = datetime(int(year), int(month), int(day), int(hour), int(minute))
        dt = bangkok_tz.localize(dt)
    except:
        await interaction.response.send_message("❌ รูปแบบวันที่ไม่ถูกต้อง ใช้: 01-01-2568 20:30", ephemeral=True)
        return

    timestamp = int(dt.timestamp())
    counts_text = f"✅เข้าร่วม 0 คน | ❌ไม่เข้าร่วม 0 คน | ❓อาจจะเข้าร่วม 0 คน"

    # สร้าง Embed ตัวอย่าง
    embed = discord.Embed(
        title=f"📌 {operation}",
        description=(
            f"<t:{timestamp}:F> | <t:{timestamp}:R>\n"
            f"**Editor:** {editor}\n"
            f"**Preset:** {preset}\n"
            f"**Tags:** {tags}\n\n"
            f"📖 **Story:**\n{story}\n\n"  
             f"**Roles:** {roles}"
        ),
        color=discord.Color.red()
    )
    embed.add_field(name="จำนวนผู้ตอบรับ", value=counts_text, inline=False)

    if image_url:
        embed.set_image(url=image_url)

    embed.set_footer(
        text=f"69Ranger Gentleman Community Bot | พัฒนาโดย Silver BlackWell",
        icon_url="https://images-ext-1.discordapp.net/external/KHtLY8ldGkiHV5DbL-N3tB9Nynft4vdkfUMzQ5y2A_E/https/cdn.discordapp.com/avatars/1290696706605842482/df2732e4e949bcb179aa6870f160c615.png"
    )

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
            'start_time': dt,
            'thread': thread,
            'message': msg
        }
        view = EventView(msg, event_id, mod_links)
        await msg.edit(embed=embed, view=view)
        bot.loop.create_task(event_timer(event_id))
        await interaction.followup.send("✅ ข้อความถูกส่งเรียบร้อยแล้ว!", ephemeral=True)
    else:
        await interaction.followup.send("❌ การส่งข้อความถูกยกเลิก", ephemeral=True)

    # DM ไปยัง Role ที่ถูกแท็กใน tags
    if tags:
        # แยกค่า tags ออกเป็นรายการ
        tag_list = tags.split()
        sent_users = set()  # เก็บ user_id ของผู้ใช้ที่ส่งข้อความไปแล้ว
    
        for tag in tag_list:
            # ตรวจสอบว่าเป็น Role หรือไม่
            if tag.startswith("<@&"):  # Role
                role_id = int(tag.replace("<@&", "").replace(">", ""))
                role = discord.utils.get(interaction.guild.roles, id=role_id)
                if role:
                    msg_link = f"https://discord.com/channels/{interaction.guild.id}/{channel.id}/{msg.id}"
                    for member in role.members:
                        if member.bot or member.id in sent_users:
                            continue  # ข้ามผู้ใช้ที่เป็นบอทหรือส่งข้อความไปแล้ว
                        try:
                            # สร้าง Embed สำหรับข้อความ DM
                            embed = discord.Embed(
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
                            embed.set_footer(
                                text="69Ranger Gentleman Community Bot | พัฒนาโดย Silver BlackWell",
                                icon_url="https://images-ext-1.discordapp.net/external/KHtLY8ldGkiHV5DbL-N3tB9Nynft4vdkfUMzQ5y2A_E/https/cdn.discordapp.com/avatars/1290696706605842482/df2732e4e949bcb179aa6870f160c615.png"
                            )
                            await member.send(embed=embed)
                            sent_users.add(member.id)  # เพิ่ม user_id ลงใน set
                        except Exception as e:
                            logging.warning(f"❌ ไม่สามารถส่งข้อความให้ {member.name}: {e}")
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
    await interaction.response.send_message("⚠️ คุณต้องการส่งข้อความนี้หรือไม่?", embed=embed, view=view, ephemeral=True)

    # รอการตอบสนองจากผู้ใช้
    await view.wait()

    if view.value is None:
        await interaction.followup.send("⏰ หมดเวลาการยืนยัน", ephemeral=True)
        return
    elif view.value:
        try:
            # ส่งข้อความพร้อมรูปภาพ
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
    logging.info(f'✅ Logged in as {bot.user}')
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="Arma 3 | 69RangerGTMCommunit")
    )
    try:
        synced = await bot.tree.sync()
        logging.info(f"✅ ซิงค์คำสั่ง {len(synced)} คำสั่งเรียบร้อยแล้ว")
    except Exception as e:
        logging.error(f"❌ เกิดข้อผิดพลาดในการซิงค์คำสั่ง: {e}")

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
