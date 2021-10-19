import discord
import requests
import json

TOKEN = 'BOTのトークンを設定'
CHECK_INSIDER_URL = 'インサイダー確認WEBAPIのURLを設定'
CREATE_GAME_URL_DISCORD = 'ゲーム作成WEBAPIのURLを設定'
GET_GAMEINFO_URL = 'ゲーム情報取得WEBAPIのURLを設定'

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)
#client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):

#    print(message.content)

    if message.author.bot:
#        print('botは無視')
        return
    else:
        # メンションがついた場合のみ
        if client.user in message.mentions:
            parameters = message.content.split()
            command = parameters[1]

            print(command)

            # /createGameの場合
            if command == '/createGameDiscord':
                # パラメータの個数チェック
                if len(parameters) != 3:
                    await message.channel.send('/createGame 参加する人のIDをカンマ区切りで指定')
                    return

                # WEBAPIのキック
                apiparams = {"member":parameters[2]}
                r = requests.get(CREATE_GAME_URL_DISCORD, params=apiparams)

                print(r.status_code)

                # JSONの解析
#                print(r.text)
                json_dic = json.loads(r.text)
#                print(json_dic["message"])
#                print(json_dic["members"])

                # コピペ用コマンド
                gameNo = json_dic["message"].split(':')[1]

                commands = ""
                commands += '▼コピペ用コマンド\n'
                commands += '@Insider Bot /seikaiVote\n'
                commands += '@Insider Bot /vote ' + gameNo +'\n'

                # DM送信
                for sendMessage in json_dic["members"]:
 #                   print('id:'+sendMessage["id"])
 #                   print('discord_id:'+sendMessage["discordId"])
                    # print('message:'+sendMessage["body"])

                    commands += '@Insider Bot /checkInsider ' + gameNo + ' ' + sendMessage["id"] + '\n'

                    user = client.get_user(int(sendMessage["discordId"]))
                    dm = await user.create_dm()
                    await dm.send(json_dic["message"]+' '+sendMessage["body"]) 

                # embed = discord.Embed(title = commands, color = discord.Colour.green())

                await message.channel.send(json_dic["message"] + '\n' + commands)

                return

            # /checkInsiderの場合
            if command == '/checkInsider':
                if len(parameters) != 4:
                    await message.channel.send('/checkInsider gameNo チェックする人のID')
                    return
            
                # WEBAPIのキック
                apiparams = {"gameNo":parameters[2],"insider":parameters[3]}
                r = requests.get(CHECK_INSIDER_URL, params=apiparams)

#                print(r.status_code)

                await message.channel.send(r.text)

                return
            
            # cote seikaisya
            if command == '/seikaiVote':
                
                value = "\N{FACE WITH OK GESTURE} -> 吊る\n"
                value += "\N{FACE WITH NO GOOD GESTURE} -> 吊らない\n"
                # 全ての質問項目を1つのembed項目とする
                embed = discord.Embed(title = value, color = discord.Colour.blue())

                msg = await message.channel.send("**正解者をインサイダーとして吊りますか？**", embed = embed)
                await msg.add_reaction("\N{FACE WITH OK GESTURE}")
                await msg.add_reaction("\N{FACE WITH NO GOOD GESTURE}")
                return

            # vote
            if command == '/vote':
                if len(parameters) != 3:
                    await message.channel.send('/vote gameNo')
                    return

                # WEBAPIのキック
                apiparams = {"gameNo":parameters[2]}
                r = requests.get(GET_GAMEINFO_URL, params=apiparams)

#                print(r.status_code)

                # JSONの解析
#                print(r.text)
                json_dic = json.loads(r.text)
#                print(json_dic["message"])
#                print(json_dic["gameInfo"])

                # errorありの場合
                if json_dic["message"] :
                    await message.channel.send(json_dic["message"])
                    return

                gameinfo = json_dic["gameInfo"]
                master = gameinfo["master"]
                members = gameinfo["members"]
                
                members_outMaster = members.replace(master+",","")
#                print(members_outMaster)

                votingMember = members_outMaster.split(',')
#                print(votingMember)

                emoji_list = ["\N{DIGIT ONE}\N{COMBINING ENCLOSING KEYCAP}", "\N{DIGIT TWO}\N{COMBINING ENCLOSING KEYCAP}", "\N{DIGIT THREE}\N{COMBINING ENCLOSING KEYCAP}", "\N{DIGIT FOUR}\N{COMBINING ENCLOSING KEYCAP}", "\N{DIGIT FIVE}\N{COMBINING ENCLOSING KEYCAP}", "\N{DIGIT SIX}\N{COMBINING ENCLOSING KEYCAP}", "\N{DIGIT SEVEN}\N{COMBINING ENCLOSING KEYCAP}"]

                # 縦並びの質問項目を生成
                value = ""
                for num in range(len(votingMember)):
                    value += emoji_list[num] + " -> "  + votingMember[num] + " \nコマンド：@Insider Bot /checkInsider "+parameters[2] +' '+votingMember[num]+"\n"
                    
                msg = await message.channel.send("**インサイダーは誰だ？**\n" + value)
                for i in range(len(votingMember)):
                    await msg.add_reaction(emoji_list[i])

                return

            # それ以外
            await message.channel.send('▼使い方\n/createGameDiscord 参加する人のIDをカンマ区切りで指定\n/checkInsider gameNo チェックする人のID\n/vote gameNo\n/sekaiVote')
            return


client.run(TOKEN)
