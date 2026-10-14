import os
import discord
from discord.ext import commands

# Lấy token từ biến môi trường trên Render để bảo mật
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

game_active = False
last_word = ""
used_words = set()
last_player = None

@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} đã sẵn sàng chơi nối từ!')

@bot.command(name="start")
async def start_game(ctx, *, first_word: str = None):
    global game_active, last_word, used_words, last_player

    if game_active:
        await ctx.send("Trò chơi đang diễn ra! Gõ `!stop` để dừng trước khi bắt đầu lượt mới.")
        return

    if not first_word:
        await ctx.send("Vui lòng nhập từ bắt đầu! Ví dụ: `!start con mèo`")
        return

    words = first_word.strip().split()
    if len(words) != 2:
        await ctx.send("Từ mở màn phải đúng **2 từ** (Ví dụ: `con mèo`, `học sinh`)!")
        return

    game_active = True
    last_word = first_word.lower().strip()
    used_words = {last_word}
    last_player = ctx.author

    await ctx.send(f"🎮 **Trò chơi Nối Từ bắt đầu!**\nTừ khởi đầu: **{last_word.upper()}**\nTừ tiếp theo phải bắt đầu bằng chữ: **'{last_word.split()[-1].upper()}'**")

@bot.command(name="stop")
async def stop_game(ctx):
    global game_active, last_word, used_words, last_player
    if not game_active:
        await ctx.send("Hiện chưa có trò chơi nào đang diễn ra.")
        return

    game_active = False
    await ctx.send(f"🛑 Trò chơi đã kết thúc! Tổng số từ đã nối: **{len(used_words)}**.")

@bot.event
async def on_message(message):
    global game_active, last_word, used_words, last_player

    if message.author == bot.user:
        return

    await bot.process_commands(message)

    if not game_active or message.content.startswith("!"):
        return

    content = message.content.strip().lower()
    words = content.split()

    if len(words) != 2:
        return

    if message.author == last_player:
        await message.channel.send(f"❌ {message.author.mention}, bạn vừa ra từ trước rồi! Hãy đợi người khác nối tiếp.")
        return

    if content in used_words:
        await message.channel.send(f"❌ Từ **'{content}'** đã được sử dụng rồi! Thử từ khác nhé.")
        return

    expected_first_word = last_word.split()[-1]
    if words[0] != expected_first_word:
        await message.channel.send(f"❌ Khái niệm sai! Từ của bạn phải bắt đầu bằng **'{expected_first_word.upper()}'**.")
        return

    last_word = content
    used_words.add(content)
    last_player = message.author

    await message.add_reaction("✅")
    await message.channel.send(f"👉 Từ tiếp theo phải bắt đầu bằng: **'{words[-1].upper()}'**")

if TOKEN:
    bot.run(TOKEN)
else:
    print("Lỗi: Không tìm thấy DISCORD_TOKEN trong biến môi trường!")
