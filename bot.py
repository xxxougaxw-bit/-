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

# クラスの中で設定をすべて完結させます
class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        # ここで allowed_mentions を設定！
        super().__init__(
            intents=intents,
            allowed_mentions=discord.AllowedMentions(everyone=True)
        )
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

client = MyClient()

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
    # 人数表示の切り替え
    display_count = "♾️ 無限（誰でもOK！）" if count <= 0 else f"{count}名"
    
    # 色の切り替え
    embed_color = 0x1e90ff if (count == 0 or mode == "通話") else 0xff4500
    
    embed = discord.Embed(title=f"📢 {mode} 募集中！", description="メンバー募集中", color=embed_color)
    embed.add_field(name="モード", value=f"**{mode}**", inline=True)
    embed.add_field(name="あと", value=f"**{display_count}**", inline=True)
    embed.add_field(name="期限", value=f"**{time}**", inline=False)
    embed.set_footer(text="参加する人はvcかチャットへ！")

    # ここで @everyone を送信！
    await interaction.response.send_message(content="@everyone", embed=embed)

@client.tree.command(name="ranking", description="戦績ランキングを作成します（最大8名）")
@app_commands.describe(
    p1_name="1人目の名前", p1_win="勝数", p1_lose="敗数",
    p2_name="2人目の名前", p2_win="勝数", p2_lose="敗数",
    p3_name="3人目の名前", p3_win="勝数", p3_lose="敗数",
    p4_name="4人目（任意）", p4_win="勝数", p4_lose="敗数",
    p5_name="5人目（任意）", p5_win="勝数", p5_lose="敗数",
    p6_name="6人目（任意）", p6_win="勝数", p6_lose="敗数",
    p7_name="7人目（任意）", p7_win="勝数", p7_lose="敗数",
    p8_name="8人目（任意）", p8_win="勝数", p8_lose="敗数"
)
async def ranking(
    interaction: discord.Interaction, 
    p1_name: str, p1_win: int, p1_lose: int,
    p2_name: str, p2_win: int, p2_lose: int,
    p3_name: str, p3_win: int, p3_lose: int,
    # 4人目以降は None をデフォルト値にすることで「任意」になります
    p4_name: str = None, p4_win: int = 0, p4_lose: int = 0,
    p5_name: str = None, p5_win: int = 0, p5_lose: int = 0,
    p6_name: str = None, p6_win: int = 0, p6_lose: int = 0,
    p7_name: str = None, p7_win: int = 0, p7_lose: int = 0,
    p8_name: str = None, p8_win: int = 0, p8_lose: int = 0
):
    # データをリストにまとめる
    raw_data = [
        (p1_name, p1_win, p1_lose),
        (p2_name, p2_win, p2_lose),
        (p3_name, p3_win, p3_lose),
        (p4_name, p4_win, p4_lose),
        (p5_name, p5_win, p5_lose),
        (p6_name, p6_win, p6_lose),
        (p7_name, p7_win, p7_lose),
        (p8_name, p8_win, p8_lose)
    ]

    players = []
    for n, w, l in raw_data:
        # 名前が入力されている人だけを処理対象にする
        if n is not None:
            total = w + l
            rate = (w / total * 100) if total > 0 else 0
            players.append({"name": n, "win": w, "lose": l, "rate": rate})
    
    # 勝率順に並び替え
    players.sort(key=lambda x: x["rate"], reverse=True)
    
    embed = discord.Embed(title="🏆 戦績ランキング", color=0xffd700)
    for i, p in enumerate(players):
        # 順位に応じた絵文字
        medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "👤"
        embed.add_field(
            name=f"{medal} {i+1}位: {p['name']}", 
            value=f"勝率: **{p['rate']:.1f}%** ({p['win']}勝 {p['lose']}敗)", 
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)
# --- 1. ボットのイベント設定 (最後の方に追加) ---

@client.event
async def on_voice_state_update(member, before, after):
    # 「誰かがボイスチャンネルから出た」とき
    if before.channel is not None:
        # そのチャンネルの名前が「🔊」で始まっているかチェック（ボットが作った目印）
        if before.channel.name.startswith("🔊"):
            # チャンネルが空っぽになったら削除
            if len(before.channel.members) == 0:
                await before.channel.delete()
                print(f"空になったのでチャンネルを削除しました: {before.channel.name}")

# 1. 保存用の辞書をクラスの__init__か、コマンドの外側に用意します
# 作成したチャンネルIDと、消したいメッセージをセットで覚えます
vc_messages = {}

@client.tree.command(name="vc", description="自動消滅する通話チャンネルを作成します")
@app_commands.describe(name="チャンネル名", limit="人数制限（0〜99）")
async def vc(interaction: discord.Interaction, name: str, limit: int = 0):
    # ---（中略：権限チェックなどはそのまま）---

    # チャンネル作成
    channel_name = f"🔊 {name}"
    category = interaction.channel.category
    new_channel = await interaction.guild.create_voice_channel(
        name=channel_name,
        user_limit=limit,
        category=category
    )
    
    # メッセージを送信し、そのメッセージを変数に代入
    response = await interaction.response.send_message(
        f"✅ 通話チャンネル **{new_channel.name}** を作成しました！\n誰もいなくなると自動的に削除されます。"
    )
    
    # 【追加】作成したチャンネルのIDと、返信メッセージを紐づけて保存
    msg = await interaction.original_response()
    vc_messages[new_channel.id] = msg

# --- 削除する時の処理を修正 ---

@client.event
async def on_voice_state_update(member, before, after):
    if before.channel is not None:
        if before.channel.name.startswith("🔊") and len(before.channel.members) == 0:
            # チャンネルを削除
            channel_id = before.channel.id
            await before.channel.delete()
            
            # 【追加】もし保存されたメッセージがあれば削除する
            if channel_id in vc_messages:
                try:
                    await vc_messages[channel_id].delete()
                    del vc_messages[channel_id] # 記憶を消す
                except:
                    pass # すでに消されていたり、エラーが出ても無視

from typing import Literal # 必要に応じてimportを確認してください

@client.tree.command(name="reloadaim", description="【鬼のAIM練習計算】")
@app_commands.describe(
    mode="プレイモード",
    kill="キル数", 
    death="デス数", 
    victory="ビクトリーロイヤルできたか",
    early_exit="リブート無効になる前に全滅（早期脱落）したか"
)
async def reloadaim(
    interaction: discord.Interaction, 
    mode: Literal["Solo", "Duo/Trio/Squad"],
    kill: int, 
    death: int, 
    victory: Literal["した", "してない"],
    early_exit: Literal["はい（早期脱落）", "いいえ"]
):
    # 1. 早期脱落（リブート無効前）なら問答無用で60分
    if early_exit == "はい（早期脱落）":
        total_time = 60.0
        description = "🚨 **リブート無効前の早期脱落！**\n言い訳無用の「1時間」AIM練習です。"
        color = 0x000000  # 黒
    else:
        # 2. モードとビクロイ状況による重み付け
        if mode == "Solo":
            # Solo: 負けたら24分、勝っても12分
            death_weight = 12 if victory == "した" else 24
        else:
            # Squad等: 負けたら10分、勝ったら5分
            death_weight = 5 if victory == "した" else 10
            
        death_time = death * death_weight

        # 3. キル数の計算（奇数なら繰り下げ）
        effective_kills = (kill // 2) * 2
        kill_reduction = effective_kills * 0.5

        total_time = max(0.0, death_time - kill_reduction)
        description = f"**{mode}** モードの戦績から算出した練習時間です。"
        color = 0xff4500 if total_time > 30 else 0x00ff00

    embed = discord.Embed(title="🎯 AIM練習指令室", description=description, color=color)
    
    if early_exit == "いいえ":
        v_text = "👑 ビクロイ達成！" if victory == "した" else "💀 敗北..."
        embed.add_field(name="モード / 結果", value=f"{mode} / {v_text}", inline=True)
        embed.add_field(name="戦績", value=f"⚔️ {kill}Kill / 🩸 {death}Death", inline=True)
        embed.add_field(name="計算内訳", value=f"1デスあたり: {death_weight}分\nキル短縮: -{kill_reduction}分", inline=False)
    
    embed.add_field(name="🔥 必要なAIM練習時間", value=f"**{total_time:.1f} 分**", inline=False)
    # 煽り文句はそのまま残してあります
    embed.set_footer(text="全然さぼっていいですよｗ、あなたは今後負けますけどね^^")

    await interaction.response.send_message(embed=embed)
    
# --- 設定項目（自分のIDに書き換えてください） ---
MY_USER_ID = 1169659712841711658  # あなたのユーザーID
INFO_CHANNEL_ID = 1474247948098474084  # 案内を投稿したいチャンネルのID

@client.tree.command(name="update", description="【管理者専用】ボットの全機能ガイドを最新版に更新して投稿します")
async def update(interaction: discord.Interaction):
    # 1. 管理者チェック
    if interaction.user.id != MY_USER_ID:
        await interaction.response.send_message("このコマンドは管理者専用です。", ephemeral=True)
        return

    # 2. 応答を保留（タイムアウト防止）
    await interaction.response.defer(ephemeral=True)

    # 3. 投稿先のチャンネルを取得
    info_channel = client.get_channel(INFO_CHANNEL_ID)
    if info_channel is None:
        await interaction.followup.send("案内チャンネルが見つかりませんでした。")
        return
        
# --- ここから ---
    # 4. 全機能紹介のEmbed作成
    embed = discord.Embed(
        title="🤖 **Jeysty 完全機能ガイド (最新版)**",
        description="サーバーを盛り上げる全機能の使い方ガイドです！",
        color=0x00ff7f
    )

    # 🎯 AIM計算
    embed.add_field(
        name="🔥 **[NEW]** 🔥🎯 **AIM練習計算 (`/reloadaim`)**",
        value=(
            "・試合結果から必要なAIM練習時間を算出します。\n"
            "・**[重要]** リブート無効前の早期脱落は**1時間確定**！\n"
            "・ビクロイならデス加算が半分に軽減されます。"
        ),
        inline=False
    )

    # 機能1: 募集機能
    embed.add_field(
        name="🎮 **パーティー募集 (`/lfm`)**",
        value=(
            "・対戦メンバーや通話相手を募集！\n"
            "・自動で `@everyone` 通知を飛ばします。"
        ),
        inline=False
    )

    # 機能2: 通話作成
    embed.add_field(
        name="🔥 **[NEW]** 🔥🔊 **カスタム通話作成 (`/vc`)**",
        value=(
            "・使い捨ての通話チャンネルを爆速で作ります。\n"
            "・**[自動削除]** 全員が退出すると部屋も消えてスッキリ！"
        ),
        inline=False
    )

    # 機能3: ランキング
    embed.add_field(
        name="🏆 **戦績ランキング (`/ranking`)**",
        value=(
            "・🔥 **[NEW]** 🔥 最大8名までのランキングに対応しました！\n"
            "・3名までは必須入力、4人目以降は任意で追加可能です。\n"
            "・勝率順に🥇🥈🥉メダル付きで表示します。"
        ),
        inline=False
    )

    # 機能4: 便利ツール
    embed.add_field(
        name="🛠️ **ミニツール集**",
        value=(
            "・`/winrate`: 勝率計算\n"
            "・`/team`: チーム分け\n"
            "・`/coin`: コイン\n"
            "・`/rule`: ルール表示"
        ),
        inline=False
    )

    embed.set_thumbnail(url=client.user.display_avatar.url)
    embed.set_footer(text="アップデートにより機能が随時追加されます！")

    await info_channel.send(embed=embed)
    await interaction.followup.send(f"✅ <#{INFO_CHANNEL_ID}> に案内を投稿しました！")
    # --- ここまで ---

# 実行部分
if __name__ == "__main__":
    keep_alive()
    token = os.getenv('DISCORD_TOKEN')
    client.run(token)













