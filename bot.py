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
async def rule(interaction: discord.Interaction, mode: Literal["zw", "ffa", "box", "1v1"]):
    rules = {
        "zw": "【zw】\n・7本先取\n・過度なあおり行為は禁止！",
        "ffa": "【ffa】\n・7本先取\n・過度なあおり行為は禁止！",
        "box": "【Box】\n・5本先取\n・過度なあおり行為は禁止！",
        "1v1": "【1v1】\n・3本先取\n・落下すれば登ってください過度なあおり行為は禁止！",
    }
    selected_rule = rules.get(mode, "ルールが見つかりませんでした。")
    await interaction.response.send_message(selected_rule)
# --- 上の rule コマンドが終わったすぐ下 ---

@client.tree.command(name="team", description="メンバーをランダムに2チームに分けます")
async def team(interaction: discord.Interaction, members: str):
    import random
    member_list = members.split()
    if len(member_list) < 2:
        await interaction.response.send_message("2人以上の名前を入力してください！")
        return
    random.shuffle(member_list)
    mid = len(member_list) // 2
    team1 = member_list[:mid]
    team2 = member_list[mid:]
    response = (
        f"🏃 **チーム分け結果** 🏃\n\n"
        f"🟦 **チーム1:** {', '.join(team1)}\n"
        f"🟧 **チーム2:** {', '.join(team2)}"
    )
    await interaction.response.send_message(response)

from typing import Literal

@client.tree.command(name="lfm", description="対戦メンバーを募集します")
async def lfm(
    interaction: discord.Interaction, 
    mode: Literal["ZW", "FFA", "BOX", "1v1"], 
    count: Literal[1, 2, 3, 4, 5, 6, 7],
    time: Literal["5分後", "10分後", "15分後", "20分後", "30分後", "45分後", "60分後",]
):
    """
    mode: ゲームモード
    count: 募集人数 (最大7人)
    time: 終了時間の目安
    """
    
    # 募集メッセージの作成
    embed = discord.Embed(
        title="🎮募集中🎮",
        description=f"\nメンバー募集中",
        color=0x00ff00 # 緑色
    )
    
    embed.add_field(name="モード", value=f"**{mode}**", inline=True)
    embed.add_field(name="あと", value=f"**{count}名**", inline=True)
    embed.add_field(name="期限", value=f"**{time}**", inline=False)
    
    embed.set_footer(text="参加する人はvcかチャット")

    # @everyone付きで送信
    await interaction.response.send_message(content="@everyone", embed=embed)
    
@client.tree.command(name="ranking", description="本日の戦績ランキングを作成します")
async def ranking(
    interaction: discord.Interaction, 
    p1_name: str, p1_win: int, p1_lose: int,
    p2_name: str, p2_win: int, p2_lose: int,
    p3_name: str, p3_win: int, p3_lose: int
):
    # データをリストにまとめる
    players = []
    for name, w, l in [(p1_name, p1_win, p1_lose), (p2_name, p2_win, p2_lose), (p3_name, p3_win, p3_lose)]:
        total = w + l
        rate = (w / total * 100) if total > 0 else 0
        players.append({"name": name, "win": w, "lose": l, "rate": rate})

    # 勝率が高い順に並び替え
    players.sort(key=lambda x: x["rate"], reverse=True)

    # ランキングの作成
    embed = discord.Embed(title="🏆 本日の戦績ランキング", color=0xffd700) # ゴールド
    
    medals = ["🥇", "🥈", "🥉"]
    for i, p in enumerate(players):
        embed.add_field(
            name=f"{medals[i]} {p['name']}",
            value=f"勝率: **{p['rate']:.1f}%** ({p['win']}勝 {p['lose']}敗)",
            inline=False
        )

    await interaction.response.send_message(embed=embed)
# 実行
if __name__ == "__main__":
    keep_alive()  # Webサーバーを起動
    token = os.getenv('DISCORD_TOKEN')
    client.run(token)










