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
from datetime import datetime
from typing import Optional
from discord.ext import commands
from discord import app_commands
from keep_alive import keep_alive
import pytz

# Logging Configuration
logging.basicConfig(level=logging.DEBUG)

# Initialize bot and intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# ตั้งค่า Timezone
THAI_TZ = pytz.timezone("Asia/Bangkok")

#=============================================================================================
# ⚙️ General Commands
#=============================================================================================
#⚠️ /Help แสดงคำสั่งทั้งหมดของบอท
@bot.tree.command(name="help", description="แสดงคำสั่งทั้งหมดของบอท")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📜 รายการคำสั่งของบอท",
        description="คำสั่งทั้งหมดที่สามารถใช้งานได้ในเซิร์ฟเวอร์นี้",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="⚙️ คำสั่งทั่วไป",
        value="`/ping` - ทดสอบว่าบอทออนไลน์หรือไม่\n"
              "`/status` - แสดงสถานะของบอท\n"
              "`/help` - แสดงคำสั่งทั้งหมดของบอท",
        inline=False
    )
    embed.add_field(
        name="📩 คำสั่งสำหรับแอดมิน",
        value=(
            "`/dm` - ส่งข้อความ DM ให้สมาชิกใน Role\n"
            "`/say` - ส่งข้อความไปยังห้องที่กำหนด"
        ),
        inline=False
    )
    embed.set_footer(
        text="69Ranger Gentleman Community Bot | พัฒนาโดย | Silver BlackWell",
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
#⚠️ /DM ส่ง ข้อความ DM
@bot.tree.command(name="dm", description="ส่ง DM ให้สมาชิกเฉพาะ Role (เฉพาะแอดมิน)")
@app_commands.describe(role="เลือก Role ที่ต้องการส่งถึง", message="ข้อความที่จะส่ง")
async def dm(interaction: discord.Interaction, role: discord.Role, message: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ (ต้องเป็นแอดมิน)", ephemeral=True)
        return

    members = [m for m in role.members if not m.bot]
    if not members:
        await interaction.response.send_message("❌ ไม่มีสมาชิกใน Role นี้ที่สามารถส่ง DM ได้", ephemeral=True)
        return

    success, failed = 0, 0
    for member in members:
        try:
            await member.send(message)
            success += 1
        except discord.Forbidden:
            failed += 1
            logging.warning(f"❌ ไม่สามารถส่งข้อความให้ {member.name} ได้ (สมาชิกอาจปิดการรับ DM)")

    await interaction.response.send_message(
        f"✅ ส่งสำเร็จ: {success} คน\n❌ ส่งไม่สำเร็จ: {failed} คน", ephemeral=True
    )
#=============================================================================================
#⚠️ /say ส่งข้อความไปยังห้องที่กำหนด
@bot.tree.command(name="say", description="ให้บอทส่งข้อความไปยังห้องที่กำหนด (เฉพาะแอดมิน)")
@app_commands.describe(channel="เลือกห้องที่ต้องการส่งข้อความ", message="ข้อความที่จะส่ง")
async def say_command(interaction: discord.Interaction, channel: discord.TextChannel, message: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ (ต้องเป็นแอดมิน)", ephemeral=True)
        return

    try:
        await channel.send(message)
        await interaction.response.send_message(f"✅ ส่งข้อความไปยังห้อง {channel.mention} สำเร็จ!", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message(f"❌ ไม่สามารถส่งข้อความไปยังห้อง {channel.mention} ได้ (บอทอาจไม่มีสิทธิ์)", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ เกิดข้อผิดพลาด: {e}", ephemeral=True)
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
# ⚠️ /event สร้างข้อความกิจกรรมในรูปแบบที่กำหนด
import asyncio  # ใช้สำหรับการทำงานแบบ Asynchronous
import re

def is_valid_url(url: str) -> bool:
    regex = re.compile(
        r'^(https?://)?'  # http:// or https://
        r'([a-zA-Z0-9.-]+)'  # domain
        r'(\.[a-zA-Z]{2,})'  # .com, .org, etc.
        r'(/.*)?$'  # path
    )
    return re.match(regex, url) is not None

@bot.tree.command(name="event", description="สร้างข้อความกิจกรรมพร้อมเวลานับถอยหลังแบบเรียลไทม์")
@app_commands.describe(
    channel="เลือกห้องที่ต้องการส่งข้อความ",
    datetime_input="วันและเวลาของกิจกรรม (เช่น 01-01-2568 20:30)",
    operation="ชื่อ Operation (เช่น The Darknight Ep.4 – Phantom nightmare)",
    editor="ชื่อผู้แก้ไข (เช่น @Silver BlackWell)",
    preset="Preset-mod (เช่น 69Ranger RE Preset Edit V5)",
    tags="แท็กที่ต้องการ (เช่น @69Rg Staff @69Rg Member @everyone)",
    story="เนื้อเรื่องของกิจกรรม",
    roles="บทบาทที่ต้องการ (เช่น  75th Ranger Regiment )",
    image_url="URL ของรูปภาพ (ถ้ามี)"
)
async def event_command(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    datetime_input: str,
    operation: str,
    editor: str,
    preset: str,
    tags: str,
    story: str,
    roles: str,
    image_url: Optional[str] = None
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ (ต้องเป็นแอดมิน)", ephemeral=True)
        return

    
    # แปลงวันที่และเวลา
    try:
        date_part, time_part = datetime_input.split(" ")
        day, month, year = map(int, date_part.split("-"))
        year -= 543  # แปลงปี พ.ศ. เป็น ค.ศ.
        event_datetime = datetime.strptime(f"{day}-{month}-{year} {time_part}", "%d-%m-%Y %H:%M").replace(tzinfo=THAI_TZ)
    except ValueError:
        await interaction.response.send_message(
            "❌ รูปแบบวันที่หรือเวลาไม่ถูกต้อง! ใช้รูปแบบ: `วัน-เดือน-ปี ชั่วโมง:นาที`\n"
            "ตัวอย่าง: `01-01-2568 20:30`",
            ephemeral=True
        )
        return
    # แปลงวันที่และเวลาเป็นภาษาไทย
    thai_days = ["วันอาทิตย์", "วันจันทร์", "วันอังคาร", "วันพุธ", "วันพฤหัสบดี", "วันศุกร์", "วันเสาร์"]
    thai_months = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
                   "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
    
    # ดึงชื่อวันและเดือนในภาษาไทย
    day_thai = thai_days[event_datetime.weekday()]  # ชื่อวันในภาษาไทย
    month_thai = thai_months[event_datetime.month - 1]  # ชื่อเดือนในภาษาไทย
    
    # แปลงวันที่และเวลาเป็นรูปแบบภาษาไทย
    thai_datetime = f"{day_thai}ที่ {event_datetime.day} {month_thai} {event_datetime.year + 543} เวลา {event_datetime.strftime('%H:%M')}"
    
    # แจ้ง Discord ว่าบอทกำลังดำเนินการ
    await interaction.response.defer()
    
    # สร้าง Embed สำหรับกิจกรรม
    embed = discord.Embed(
        title=f"📅 {operation}",  # ใช้ชื่อ Operation เป็นหัวข้อ
        description=(
            f"**🗓️ วันและเวลา:** {thai_datetime}\n\n"  # ใช้วันที่และเวลาในภาษาไทย
            f"**✏️ Editor by:** {editor}\n\n"
            f"**🛠️ Preset:** {preset}\n\n"
            f"**🏷️ Tags:** {tags}"
        ),
        color=discord.Color.blue()
    )

    embed.add_field(
        name="📖 **Story**",
        value=story,  # แสดงค่า story โดยตรง
        inline=False
    )
    embed.add_field(
        name="🧥 **Roles**",
        value=roles,  # แสดงค่า roles โดยตรง
        inline=False
    )
    if image_url:
        embed.set_image(url=image_url)
    embed.set_footer(
        text="69Ranger Gentleman Community Bot | พัฒนาโดย Silver BlackWell",
        icon_url="https://images-ext-1.discordapp.net/external/KHtLY8ldGkiHV5DbL-N3tB9Nynft4vdkfUMzQ5y2A_E/https/cdn.discordapp.com/avatars/1290696706605842482/df2732e4e949bcb179aa6870f160c615.png"
    )
    
    from discord.ui import View, Button
    
    class ConfirmationView(View):
        def __init__(self, interaction: discord.Interaction):
            super().__init__(timeout=60)  # ตั้งเวลา Timeout 60 วินาที
            self.interaction = interaction
            self.value = None
    
        @discord.ui.button(label="✅ ยืนยัน", style=discord.ButtonStyle.green)
        async def confirm(self, interaction: discord.Interaction, button: Button):
            if interaction.user != self.interaction.user:
                await interaction.response.send_message("❌ คุณไม่มีสิทธิ์กดปุ่มนี้", ephemeral=True)
                return
            self.value = True
            self.stop()
    
        @discord.ui.button(label="❌ ยกเลิก", style=discord.ButtonStyle.red)
        async def cancel(self, interaction: discord.Interaction, button: Button):
            if interaction.user != self.interaction.user:
                await interaction.response.send_message("❌ คุณไม่มีสิทธิ์กดปุ่มนี้", ephemeral=True)
                return
            self.value = False
            self.stop()
    
    # ในคำสั่ง /event
    confirmation_view = ConfirmationView(interaction)
    
    # ใช้ interaction.response.defer() เพื่อบอก Discord ว่าบอทกำลังดำเนินการ
    await interaction.response.defer(ephemeral=True)
    
    # ส่งข้อความยืนยันพร้อมปุ่ม
    await interaction.followup.send(
        "⚠️ คุณต้องการส่งข้อความนี้หรือไม่?",
        embed=embed,
        view=confirmation_view
    )
    
    # รอการตอบสนองจากผู้ใช้
    await confirmation_view.wait()
    
    if confirmation_view.value is None:
        await interaction.followup.send("⏰ หมดเวลาการยืนยัน", ephemeral=True)
        return
    elif confirmation_view.value:
        # ส่งข้อความไปยังช่องที่กำหนด
        message = await channel.send(embed=embed)
    
        # สร้างเธรดสำหรับสรุปรายชื่อ
        thread = await message.create_thread(name="📋 รายชื่อผู้เข้าร่วม", auto_archive_duration=1440)
    
        # เพิ่มปุ่มสำหรับการตอบกลับ
        await interaction.followup.send("✅ ข้อความถูกส่งเรียบร้อยแล้ว!", ephemeral=True)
    else:
        await interaction.followup.send("❌ การส่งข้อความถูกยกเลิก", ephemeral=True)

    # เพิ่มปฏิกิริยา (Reaction) สำหรับการยืนยัน
    await confirmation_message.add_reaction("✅")
    await asyncio.sleep(0.5)  # หน่วงเวลา 0.5 วินาทีก่อนเพิ่มปฏิกิริยาถัดไป
    await confirmation_message.add_reaction("❌")
    await asyncio.sleep(0.5)
    await confirmation_message.add_reaction("🤔")
    
    # เรียกใช้งานฟังก์ชัน update_summary พร้อมส่งอาร์กิวเมนต์
    await update_summary(message, thread)
    
    # ฟังก์ชัน update_summary
    async def update_summary(message, thread):
        try:
            # ดึงข้อมูลผู้ใช้จากปฏิกิริยา
            join_reaction = discord.utils.get(message.reactions, emoji="✅")
            not_join_reaction = discord.utils.get(message.reactions, emoji="❌")
            maybe_reaction = discord.utils.get(message.reactions, emoji="🤔")
    
            join_users = [user async for user in join_reaction.users() if not user.bot] if join_reaction else []
            not_join_users = [user async for user in not_join_reaction.users() if not user.bot] if not_join_reaction else []
            maybe_users = [user async for user in maybe_reaction.users() if not user.bot] if maybe_reaction else []
    
            # สร้างข้อความสรุป
            summary = f"**✅ เข้าร่วม ({len(join_users)}):**\n" + "\n".join([user.mention for user in join_users])
            summary += f"\n\n**❌ ไม่เข้าร่วม ({len(not_join_users)}):**\n" + "\n".join([user.mention for user in not_join_users])
            summary += f"\n\n**🤔 อาจจะมา ({len(maybe_users)}):**\n" + "\n".join([user.mention for user in maybe_users])
    
            # ส่งข้อความสรุปใหม่ (เพิ่มต่อท้าย)
            await thread.send(summary)
        except Exception as e:
            logging.error(f"❌ เกิดข้อผิดพลาดในการอัปเดตรายชื่อ: {e}")

        # ตั้งเวลานับถอยหลัง
    while True:
        now = datetime.now(THAI_TZ)
        time_remaining = (event_datetime - now).total_seconds()
    
        if time_remaining > 0:
            # ก่อนถึงเวลาเริ่มกิจกรรม
            hours, remainder = divmod(int(time_remaining), 3600)
            minutes, seconds = divmod(remainder, 60)
            embed.set_field_at(
                index=0,
                name="⏳ เวลาก่อนเริ่มกิจกรรม",
                value=f"{hours} ชั่วโมง {minutes} นาที {seconds} วินาที",
                inline=False
            )
            await message.edit(embed=embed)
    
        elif 0 <= time_remaining <= 14400:  # ระหว่าง 0 ถึง 4 ชั่วโมง
            # ระหว่างดำเนินการ
            elapsed_time = abs(time_remaining)
            hours, remainder = divmod(int(elapsed_time), 3600)
            minutes, seconds = divmod(remainder, 60)
            embed.set_field_at(
                index=0,
                name="🟢 สถานะกิจกรรม",
                value=f"อยู่ในระหว่างดำเนินการ\nผ่านไปแล้ว {hours} ชั่วโมง {minutes} นาที {seconds} วินาที",
                inline=False
            )
            await message.edit(embed=embed)
    
        else:
            # หลังจาก 4 ชั่วโมง (กิจกรรมสิ้นสุด)
            embed.set_field_at(
                index=0,
                name="🔴 สถานะกิจกรรม",
                value="กิจกรรมสิ้นสุดแล้ว",
                inline=False
            )
            await message.edit(embed=embed)
            break
    
        # อัปเดตสรุปรายชื่อ
        await update_summary(message, thread)
    
        # รอ 1 วินาทีก่อนอัปเดตครั้งถัดไป
        await asyncio.sleep(1)
    
        # เมื่อถึงเวลาเริ่มกิจกรรม
        if time_remaining <= 0:
            await message.reply("⏰ ถึงเวลารวมพลแล้ว!")
    
            # แจ้งเตือนผู้ที่กด "เข้าร่วม"
            join_reaction = discord.utils.get(message.reactions, emoji="✅")
            if join_reaction:
                join_users = [user async for user in join_reaction.users() if not user.bot]
                for user in join_users:
                    try:
                        await user.send(f"⏰ ถึงเวลารวมพลสำหรับกิจกรรม: **{operation}** แล้ว!")
                    except discord.Forbidden:
                        logging.warning(f"❌ ไม่สามารถส่งข้อความแจ้งเตือนให้ {user.name} ได้ (สมาชิกอาจปิดการรับ DM)")
            break
        # อัปเดต Embed และสรุปรายชื่อ
        hours, remainder = divmod(int(time_remaining), 3600)
        minutes, seconds = divmod(remainder, 60)
        embed.set_field_at(
            index=0,
            name="⏳ เวลาก่อนเริ่มกิจกรรม",
            value=f"{hours} ชั่วโมง {minutes} นาที {seconds} วินาที",
            inline=False
        )
        await message.edit(embed=embed)
        await update_summary()

        # รอ 1 วินาทีก่อนอัปเดตครั้งถัดไป
        await asyncio.sleep(1)
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
