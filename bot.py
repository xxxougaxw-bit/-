import discord
from discord import app_commands
import os
import random
from typing import Literal
from flask import Flask
from threading import Thread

# --- サーバー維持用の設定 ---
app = Flask('')
@app.route('/')
def home():
    return "OK"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()
# -------------------------

class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(
            intents=intents,
            allowed_mentions=discord.AllowedMentions(everyone=True)
        )
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

client = MyClient()
vc_messages = {}

# --- コマンド一覧 ---

@client.tree.command(name="winrate", description="勝率を計算します")
async def winrate(interaction: discord.Interaction, win: int, lose: int):
    total = win + lose
    if total == 0:
        await interaction.response.send_message("合計試合数が0なので計算できません！")
        return
    rate = (win / total) * 100
    await interaction.response.send_message(f"合計: {total}戦 {win}勝 {lose}敗\n勝率: **{rate:.1f} %**")

@client.tree.command(name="rule", description="ゲームのルールを確認します")
async def rule(interaction: discord.Interaction, mode: Literal["zw", "ffa", "box", "1v1"]):
    rules = {
        "zw": "【zw】\n・7本先取\n武器の指定はありません。相手との話し合いで決めてください。\n・過度なあおり行為は禁止！",
        "ffa": "【ffa】\n・7本先取\n武器の指定はありません。相手との話し合いで決めてください。\n・過度なあおり行為は禁止！",
        "box": "【Box】\n・5本先取\n武器の指定はありません。相手との話し合いで決めてください。\n・過度なあおり行為は禁止！",
        "1v1": "【1v1】\n・3本先取\n武器の指定はありません。相手との話し合いで決めてください。\n・落下すれば登ってください。過度なあおり行為は禁止！",
    }
    await interaction.response.send_message(rules.get(mode, "ルール不明"))

@client.tree.command(name="team", description="メンバーをランダムに2チームに分けます")
async def team(interaction: discord.Interaction, members: str):
    member_list = members.split()
    if len(member_list) < 2:
        await interaction.response.send_message("2人以上の名前を入力してください！")
        return
    random.shuffle(member_list)
    mid = len(member_list) // 2
    response = f"🟦 **チーム1:** {', '.join(member_list[:mid])}\n🟧 **チーム2:** {', '.join(member_list[mid:])}"
    await interaction.response.send_message(response)

@client.tree.command(name="coin", description="コイントスで先攻・後攻を決めます")
async def coin(interaction: discord.Interaction):
    result = random.choice(["【先攻】 ⚫️", "【後攻】 ⚪️"])
    embed = discord.Embed(title="🪙 コイントス結果", description=f"結果は... **{result}** です！", color=0xffd700)
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="lfm", description="対戦メンバーや通話を募集します")
async def lfm(
    interaction: discord.Interaction, 
    mode: Literal["ZW", "FFA", "BOX", "1v1", "通話", "VODReview"], 
    count: int, 
    time: Literal["今から", "5分後", "10分後", "15分後", "20分後", "30分後", "45分後", "60分後"]
):
    display_count = "♾️ 無限（誰でもOK！）" if count <= 0 else f"{count}名"
    embed_color = 0x1e90ff if (count == 0 or mode == "通話") else 0xff4500
    embed = discord.Embed(title=f"📢 {mode} 募集中！", description="メンバー募集中", color=embed_color)
    embed.add_field(name="モード", value=f"**{mode}**", inline=True)
    embed.add_field(name="あと", value=f"**{display_count}**", inline=True)
    embed.add_field(name="期限", value=f"**{time}**", inline=False)
    embed.set_footer(text="参加する人はvcかチャットへ！")
    await interaction.response.send_message(content="@everyone", embed=embed)

@client.tree.command(name="ranking", description="戦績ランキングを作成します（最大8名）")
async def ranking(
    interaction: discord.Interaction, 
    p1_name: str, p1_win: int, p1_lose: int,
    p2_name: str, p2_win: int, p2_lose: int,
    p3_name: str, p3_win: int, p3_lose: int,
    p4_name: str = None, p4_win: int = 0, p4_lose: int = 0,
    p5_name: str = None, p5_win: int = 0, p5_lose: int = 0,
    p6_name: str = None, p6_win: int = 0, p6_lose: int = 0,
    p7_name: str = None, p7_win: int = 0, p7_lose: int = 0,
    p8_name: str = None, p8_win: int = 0, p8_lose: int = 0
):
    raw_data = [
        (p1_name, p1_win, p1_lose), (p2_name, p2_win, p2_lose), (p3_name, p3_win, p3_lose),
        (p4_name, p4_win, p4_lose), (p5_name, p5_win, p5_lose), (p6_name, p6_win, p6_lose),
        (p7_name, p7_win, p7_lose), (p8_name, p8_win, p8_lose)
    ]
    players = []
    for n, w, l in raw_data:
        if n is not None:
            total = w + l
            rate = (w / total * 100) if total > 0 else 0
            players.append({"name": n, "win": w, "lose": l, "rate": rate})
    players.sort(key=lambda x: x["rate"], reverse=True)
    embed = discord.Embed(title="🏆 戦績ランキング", color=0xffd700)
    for i, p in enumerate(players):
        medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "👤"
        embed.add_field(name=f"{medal} {i+1}位: {p['name']}", value=f"勝率: **{p['rate']:.1f}%** ({p['win']}勝 {p['lose']}敗)", inline=False)
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="vc", description="自動消滅する通話チャンネルを作成します")
@app_commands.describe(name="チャンネル名", limit="人数制限（0〜99）")
async def vc(interaction: discord.Interaction, name: str, limit: int = 0):
    channel_name = f"🔊 {name}"
    category = interaction.channel.category
    new_channel = await interaction.guild.create_voice_channel(name=channel_name, user_limit=limit, category=category)
    await interaction.response.send_message(f"✅ 通話チャンネル **{new_channel.name}** を作成しました！\n誰もいなくなると自動的に削除されます。")
    msg = await interaction.original_response()
    vc_messages[new_channel.id] = msg

@client.event
async def on_voice_state_update(member, before, after):
    if before.channel is not None:
        if before.channel.name.startswith("🔊") and len(before.channel.members) == 0:
            channel_id = before.channel.id
            try:
                await before.channel.delete()
                if channel_id in vc_messages:
                    await vc_messages[channel_id].delete()
                    del vc_messages[channel_id]
            except:
                pass

@client.tree.command(name="reloadaim", description="【鬼のAIM練習計算】Solo:24分 / Squad:20分")
@app_commands.describe(
    mode="プレイモード", kill="キル数", death="デス数", 
    victory="ビクトリーロイヤルできたか", early_exit="早期脱落したか（Squadのみ適用）"
)
async def reloadaim(
    interaction: discord.Interaction, 
    mode: Literal["Solo", "Duo/Trio/Squad"],
    kill: int, death: int, 
    victory: Literal["した", "してない"],
    early_exit: Literal["はい（早期脱落）", "いいえ"]
):
    # 【3秒ルール対策】
    await interaction.response.defer()

    # 1. 早期脱落判定（Soloは除外）
    if mode != "Solo" and early_exit == "はい（早期脱落）":
        total_time = 60.0
        description = "🚨 **リブート無効前の早期脱落！**\n言い訳無用の「1時間」AIM練習です。"
        color = 0x000000
    else:
        # 2. モード別の重み付け (Solo: 24/12分, Squad: 20/10分)
        if mode == "Solo":
            death_weight = 12 if victory == "した" else 24
        else:
            death_weight = 10 if victory == "した" else 20
        
        death_time = death * death_weight
        effective_kills = (kill // 2) * 2
        kill_reduction = effective_kills * 0.5
        total_time = max(0.0, death_time - kill_reduction)

        description = f"**{mode}** モードの戦績から算出した練習時間です。"
        if mode == "Solo" and early_exit == "はい（早期脱落）":
            description += "\n※Soloのため早期脱落ペナルティは除外されました。"
        color = 0xff4500 if total_time > 30 else 0x00ff00

    embed = discord.Embed(title="🎯 AIM練習指令室", description=description, color=color)
    if not (mode != "Solo" and early_exit == "はい（早期脱落）"):
        v_text = "👑 ビクロイ達成！" if victory == "した" else "💀 敗北..."
        embed.add_field(name="モード / 結果", value=f"{mode} / {v_text}", inline=True)
        embed.add_field(name="戦績", value=f"⚔️ {kill}Kill / 🩸 {death}Death", inline=True)
        embed.add_field(name="計算内訳", value=f"1デスあたり: {death_weight}分\nキル短縮: -{kill_reduction}分", inline=False)
    
    embed.add_field(name="🔥 必要なAIM練習時間", value=f"**{total_time:.1f} 分**", inline=False)
    embed.set_footer(text="全然さぼっていいですよｗ、あなたは今後負けますけどね^^")

    await interaction.followup.send(embed=embed)

MY_USER_ID = 1169659712841711658
INFO_CHANNEL_ID = 1474247948098474084

@client.tree.command(name="update", description="【管理者専用】全機能ガイドを投稿します")
async def update(interaction: discord.Interaction):
    if interaction.user.id != MY_USER_ID:
        await interaction.response.send_message("このコマンドは管理者専用です。", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    info_channel = client.get_channel(INFO_CHANNEL_ID)
    if info_channel is None:
        await interaction.followup.send("案内チャンネルが見つかりませんでした。")
        return
        
    embed = discord.Embed(title="🤖 **Jeysty 完全機能ガイド (最新版)**", description="サーバーの全機能ガイドです！", color=0x00ff7f)
    embed.add_field(name="🎯 **AIM練習計算 (`/reloadaim`)**", value="・Solo:1デス24分 / Squad:1デス20分\n・リブート無効前の脱落は1時間！\n・ビクロイでペナルティ半減。", inline=False)
    embed.add_field(name="🎮 **パーティー募集 (`/lfm`)** / 🔊 **カスタム通話 (`/vc`)**", value="・募集は自動で全員に通知。\n・VCは全員退出で自動削除されます。", inline=False)
    embed.add_field(name="🏆 **ランキング (`/ranking`)** / 🛠️ **ツール集**", value="・勝率ランキングやチーム分け、勝率計算など。", inline=False)
    embed.set_thumbnail(url=client.user.display_avatar.url)
    embed.set_footer(text="アップデートにより機能が随時追加されます！")

    await info_channel.send(embed=embed)
    await interaction.followup.send(f"✅ <#{INFO_CHANNEL_ID}> に案内を投稿しました！")

if __name__ == "__main__":
    keep_alive()
    token = os.getenv('DISCORD_TOKEN')
    client.run(token)












