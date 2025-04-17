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

# Timezone Configuration
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
