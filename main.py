import discord
import os
import asyncio
import logging
logging.basicConfig(level=logging.DEBUG)

from discord.ext import commands
from keep_alive import keep_alive
from datetime import datetime, timedelta
from typing import List
from discord import app_commands
from discord.ext.commands import Greedy



# Initialize bot and intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# กำหนดเขตเวลาไทย
import pytz  
THAI_TZ = pytz.timezone("Asia/Bangkok")


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
        value=(
            "`/ping` - ทดสอบว่าบอทออนไลน์หรือไม่\n"
            "`/status` - แสดงสถานะของบอท\n"
            "`/help` - แสดงคำสั่งทั้งหมดของบอท"
        ),
        inline=False
    )
    embed.add_field(
        name="📩 คำสั่งสำหรับแอดมิน",
        value=(
            "`/dm` - ส่งข้อความ DM ให้สมาชิกใน Role"
        ),
        inline=False
    )
    embed.set_footer(
        text="69Ranger Gentleman Community Bot | พัฒนาโดย | Silver BlackWell", 
        icon_url="https://images-ext-1.discordapp.net/external/KHtLY8ldGkiHV5DbL-N3tB9Nynft4vdkfUMzQ5y2A_E/https/cdn.discordapp.com/avatars/1290696706605842482/df2732e4e949bcb179aa6870f160c615.png?format=webp&quality=lossless&width=102&height=102"  # เพิ่มไอคอนใน Footer
    )
    embed.set_thumbnail(
        url="https://images-ext-1.discordapp.net/external/KHtLY8ldGkiHV5DbL-N3tB9Nynft4vdkfUMzQ5y2A_E/https/cdn.discordapp.com/avatars/1290696706605842482/df2732e4e949bcb179aa6870f160c615.png?format=webp&quality=lossless&width=102&height=102"  # เพิ่มไอคอนใน Thumbnail
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

#=============================================================================================
#⚠️ /ping ทดสอบสถานะของบอท
@bot.tree.command(name="ping", description="ทดสอบสถานะของบอท")
async def slash_ping(interaction: discord.Interaction):
    await interaction.response.send_message("บอทยังทำงานอยู่ 🟢")

#=============================================================================================
#⚠️  /status เพื่อแสดงสถานะของบอท
@bot.tree.command(name="status", description="แสดงสถานะของบอท")
async def status_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📊 สถานะของบอท",
        description="สถานะปัจจุบันของบอท",
        color=discord.Color.green()
    )
    embed.add_field(name="🟢 สถานะ", value="ออนไลน์", inline=False)
    embed.add_field(name="📅 เวลาปัจจุบัน", value=datetime.now(THAI_TZ).strftime("%d-%m-%Y %H:%M:%S"), inline=False)
    embed.set_footer(text="69Ranger Gentleman Community Bot")
    await interaction.response.send_message(embed=embed, ephemeral=True)

#=============================================================================================
#⚠️ /DM ส่ง ข้อความ DM 
@bot.tree.command(name="dm", description="ส่ง DM ให้สมาชิกเฉพาะ Role หรือ @สมาชิก (เฉพาะแอดมิน)")
@app_commands.describe(
    role="เลือก Role ที่ต้องการส่งถึง (ปล่อยว่างหากต้องการส่งถึงสมาชิกเฉพาะ)",
    members="เลือกสมาชิกที่ต้องการส่งถึง (ปล่อยว่างหากต้องการส่งถึง Role)",
    message="ข้อความที่จะส่ง"
)
async def dm(interaction: discord.Interaction, role: discord.Role = None, members: List[discord.Member] = None, message: str = None):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ (ต้องเป็นแอดมิน)", ephemeral=True)
        return

    if not role and not members:
        await interaction.response.send_message("❌ โปรดเลือก Role หรือ @สมาชิก อย่างน้อยหนึ่งตัวเลือก", ephemeral=True)
        return

    if role:
        target_members = [m for m in role.members if not m.bot]
    elif members:
        target_members = [m for m in members if not m.bot]

    if not target_members:
        await interaction.response.send_message("❌ ไม่มีสมาชิกที่สามารถส่ง DM ได้", ephemeral=True)
        return

    view = ConfirmView(role, message, target_members)
    await interaction.response.send_message(
        f"⚠️ คุณต้องการส่งข้อความนี้ให้กับ `{len(target_members)}` คนหรือไม่?\n\n📨 ข้อความ:\n```{message}```",
        view=view,
        ephemeral=True
    )

class ConfirmView(discord.ui.View):
    def __init__(self, role, message, members):
        super().__init__(timeout=None)  # ตั้งค่า timeout=None เพื่อป้องกัน View หมดอายุ
        self.role = role
        self.message = message
        self.members = members

    @discord.ui.button(label="✅ ยืนยัน", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="📤 เริ่มส่งข้อความ...", view=None)
        success = 0
        failed = 0
        for member in self.members:
            try:
                await member.send(self.message)
                success += 1
            except discord.Forbidden:
                failed += 1
                print(f"❌ ไม่สามารถส่งข้อความให้ {member.name} ได้ (สมาชิกอาจปิดการรับ DM)")

        await interaction.followup.send(f"✅ ส่งสำเร็จ: {success} คน\n❌ ส่งไม่สำเร็จ: {failed} คน", ephemeral=True)

    @discord.ui.button(label="❌ ยกเลิก", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="🚫 ยกเลิกการส่งข้อความ", view=None)



#=============================================================================================
#⚠️ auto Role  เพิ่ม Role ให้สมาชิกใหม่
@bot.event
async def on_member_join(member):
    try:
        role = discord.utils.get(member.guild.roles, name="Civilian")
        if role:
            if member.guild.me.guild_permissions.manage_roles:
                await member.add_roles(role)
                print(f"✅ ให้ Role '{role.name}' กับ {member.name} แล้ว")
            else:
                print("❌ บอทไม่มีสิทธิ์ในการจัดการ Role")
        else:
            print("❌ ไม่พบ Role 'Civilian'")
    except discord.Forbidden:
        print(f"❌ ไม่สามารถเพิ่ม Role ให้ {member.name} ได้ (ไม่มีสิทธิ์)")
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
        print(f"✅ ส่งข้อความต้อนรับไปยัง {member.name}'s DM")
    except discord.Forbidden:
        print(f"❌ ไม่สามารถส่งข้อความให้ {member.name} ได้ (สมาชิกอาจปิดการรับ DM)")
        channel = discord.utils.get(member.guild.text_channels, name="🧰𝐜𝐨𝐦𝐦𝐚𝐧𝐝𝐬-𝐛𝐨𝐭-𝐥𝐨𝐠")  # เปลี่ยนชื่อช่องตามต้องการ
        if channel:
            await channel.send(f"ยินดีต้อนรับ {member.mention}! โปรดเปิดการรับข้อความ DM เพื่อรับข้อมูลเพิ่มเติม.")


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
        print(f"✅ ส่งข้อความลาไปยัง {member.name}'s DM")
    except discord.Forbidden:
        print(f"❌ ไม่สามารถส่งข้อความให้ {member.name} ได้ (สมาชิกอาจปิดการรับ DM)")
        channel = discord.utils.get(member.guild.text_channels, name="🧰𝐜𝐨𝐦𝐦𝐚𝐧𝐝𝐬-𝐛𝐨𝐭-𝐥𝐨𝐠")  # เปลี่ยนชื่อช่องตามต้องการ
        if channel:
            await channel.send(f"{member.name} ได้ออกจากเซิร์ฟเวอร์แล้ว แต่ไม่สามารถส่งข้อความ DM ได้.")
#=============================================================================================
@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="Arma 3 | 69RangerGTMCommunit")
    )
    try:
        synced = await bot.tree.sync()  # ซิงค์คำสั่งกับ Discord
        print(f"✅ ซิงค์คำสั่ง {len(synced)} คำสั่งเรียบร้อยแล้ว")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการซิงค์คำสั่ง: {e}")

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
keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
