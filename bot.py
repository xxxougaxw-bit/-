import discord
from discord import app_commands
from flask import Flask
from threading import Thread
import os

# --- Renderで寝落ちを防ぐための「生存確認」用設定 ---
app = Flask('')
@app.route('/')
def home():
    return "Bot is running!"

def run_web_server():
    # RenderはPort 8080や10000を使うことが多いです
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web_server)
    t.start()

# --- ここからはいつものボットの中身 ---
class MyBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True 
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

client = MyBot()

@client.tree.command(name="winrate", description="勝率を計算します")
async def winrate(interaction: discord.Interaction, win: int, lose: int):
    total = win + lose
    if total == 0:
        await interaction.response.send_message("まだ試合をしていませんね。")
        return
    rate = (win / total) * 100
    await interaction.response.send_message(f"合計: {total}戦 {win}勝 {lose}敗\n勝率: **{rate:.1f} %**")

# 実行
if __name__ == "__main__":
    keep_alive() # Webサーバーを起動

   import os
# ...（中略）...
token = os.getenv('MTQ3MjMzMjY5Mjc0NDgzNTEyMg.GlNKU2.NMa2HPR2ttkVBK2F7dA4EHMbmVNeLFnsd1Fd2w')
client.run(token)
