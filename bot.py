import discord
from discord import app_commands
import os

# --- サーバー維持用の設定 ---
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "OK"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
# -------------------------

class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

client = MyClient()

@client.tree.command(name="winrate", description="勝率を計算します")
async def winrate(interaction: discord.Interaction, win: int, lose: int):
    total = win + lose
    if total == 0:
        await interaction.response.send_message("合計試合数が0なので計算できません！")
        return
    rate = (win / total) * 100
    await interaction.response.send_message(f"合計: {total}戦 {win}勝 {lose}敗\n勝率: **{rate:.1f} %**")
from typing import Literal

@client.tree.command(name="rule", description="ゲームのルールを確認します")
async def rule(interaction: discord.Interaction, mode: Literal["zw", "ffa", "box", "1v1", "2v2"]):
    rules = {
        "zw": "【zw】\n・7本先取\n・過度なあおり行為は禁止！",
        "ffa": "【ffa】\n・7本先取\n・過度なあおり行為は禁止！",
        "box": "【Box】\n・5本先取\n・過度なあおり行為は禁止！",
        "1v1": "【1v1】\n・3本先取\n・落下すれば登ってください過度なあおり行為は禁止！",
    }
    selected_rule = rules.get(mode, "ルールが見つかりませんでした。")
    await interaction.response.send_message(selected_rule)
# 実行
if __name__ == "__main__":
    keep_alive()  # Webサーバーを起動
    token = os.getenv('DISCORD_TOKEN')
    client.run(token)

