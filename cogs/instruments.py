import os
from core.classes import Cog_Extension
import openai
import discord
import time
from discord import app_commands

api_key = os.getenv("OPENAI_API_KEY")

context_store = {}
cooldowns_translate = {}
cooldowns_search = {}

cooldowns = {}

cooldowns_ai = {}

class Instruments(Cog_Extension):
    @app_commands.command(name="translate", description="Айка переведет текст на выбранный вами язык")
    @app_commands.choices(target_language=[
        app_commands.Choice(name="Emoji 🆕", value="Emoji"),
        app_commands.Choice(name="Эльфиский 🆕", value="Emoji"),
        app_commands.Choice(name="Дварфовский 🆕", value="Dwarvish"),
        app_commands.Choice(name="Английский", value="ENG"),
        app_commands.Choice(name="Русский", value="RUS"),
        app_commands.Choice(name="Французский", value="FRA"),
        app_commands.Choice(name="Испанский", value="SPA"),
        app_commands.Choice(name="Немецкий", value="GER"),
        app_commands.Choice(name="Итальянский", value="ITA"),
        app_commands.Choice(name="Китайский", value="CHI"),
        app_commands.Choice(name="Японский", value="JAP"),
        app_commands.Choice(name="Корейский", value="KOR"),
    ])
    async def translate_text(self, interaction: discord.Interaction, target_language: str, *, text: str):
        await interaction.response.defer()

        try:
            user_id = interaction.user.id
            current_time = time.time()
            last_used_time = cooldowns_translate.get(user_id, 0)

            if str(user_id) in open("blocked_users.txt").read():
                error_embed = discord.Embed(title="Ошибка", description="Ваш аккаунт заблокирован.", color=discord.Color.red())
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return

            user_folder = os.path.join("aika_users", str(user_id))

            if not os.path.exists(user_folder):
                error_embed = discord.Embed(title="Ошибка", description="Хм, похоже я с вами еще не знакома. Пожалуйста, воспользуйтесь командой `/register` чтобы создать свой аккаунт", color=discord.Color.red())
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return

            plan_file_path = os.path.join(user_folder, "plus", "plan.txt")

            if not os.path.exists(plan_file_path):
                cooldown = 600
            else:
                with open(plan_file_path, "r") as plan_file:
                    plan_text = plan_file.read().strip()

                if plan_text in ["Basic", "Standart", "Ultimate", "Excelsior"]:
                    cooldown = 0
                else:
                    cooldown = 600

            if current_time - last_used_time < cooldown:
                error_message = f"Ваш тарифный план не позволяет использовать эту команду чаще 1 раза в {int(cooldown / 60)} минут. Подробнее по команде `/plus`"
                error_embed = discord.Embed(title="Ошибка", description=error_message, color=discord.Color.red())
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return

            prompt = f'Цель перевода (если цель Emoji то в тексте должны быть только смайлики): {target_language}\nТекст, который надо перевести: {text}'

            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=1024,
                api_key=api_key
            )
            translated_text = response.choices[0].text.strip()

            log_embed = discord.Embed(title="Aika Translator Log", color=0x00ff00)
            log_embed.add_field(name="User", value=interaction.user.display_name, inline=False)
            log_embed.add_field(name="User ID", value=interaction.user.id, inline=False)
            log_embed.add_field(name="Server", value=interaction.guild.name if interaction.guild else "Direct Message", inline=False)
            log_embed.add_field(name="Server ID", value=interaction.guild.id if interaction.guild else "N/A", inline=False)
            log_embed.add_field(name="Channel", value=interaction.channel.name if isinstance(interaction.channel, discord.TextChannel) else "Direct Message", inline=False)
            log_embed.add_field(name="Target Language", value=target_language, inline=False)
            log_embed.add_field(name="Text", value=text, inline=False)
            log_embed.add_field(name="Translated Text", value=translated_text, inline=False)
            channel_id = 000000000000000000
            channel = self.bot.get_channel(channel_id)
            if channel:
                await channel.send(embed=log_embed)

            embed = discord.Embed(title="Aika Переводчик", color=0x921294)
            embed.add_field(name="Цель перевода", value=target_language, inline=False)
            embed.add_field(name="Переведеный текст", value=f"```{translated_text}```", inline=False)
            await interaction.followup.send(embed=embed)

            cooldowns_translate[user_id] = current_time
        except Exception as e:
            print(f"{e}")
            error_embed = discord.Embed(title="Ошибка", description=f"Извините за неудобства. В настоящее время Айка не может обработать ваш запрос из-за технических проблем. Мы работаем над их устранением и ожидаем, что проблема будет решена в ближайшее время. Просим вас не удалять Айку с сервера. Спасибо за понимание.", color=discord.Color.red())
            await interaction.followup.send(embed=error_embed, ephemeral=True)

    @app_commands.command(name="search", description="Поиск в интернете через Aika Aidex (beta)")
    async def search(self, interaction: discord.Interaction, search_query: str):
        await interaction.response.defer()
        user_id = str(interaction.user.id)
        current_time = time.time()
        last_used_time = cooldowns_search.get(user_id, 0)
        plan_file_path = f"aika_users/{user_id}/plus/plan.txt"

        with open('blocked_users.txt', 'r') as f:
            blocked_users = [line.strip().split('#')[0] for line in f]

        if str(interaction.user.id) in blocked_users:
            await interaction.followup.send("Ошибка: Ваш аккаунт заблокирован")
            return

        if not os.path.exists(plan_file_path):
            cooldown = 600
        else:
            with open(plan_file_path, 'r') as plan_file:
                plan_text = plan_file.read().strip()
            if plan_text != "Excelsior" and current_time - last_used_time < 600:
                error_message = f"Ваш тарифный план не позволяет использовать эту команду больше 1 раза в 10 минут. Подробнее по команде `/plus`\nМы также ведем набор в нашу PR и в случае вашего вступления вы получите бесрочный Premium. [Подробнее тут](https://discord.com/channels/1011882995076050987/1112087346549100727)"
                error_embed = discord.Embed(title="Ошибка", description=error_message, color=discord.Color.red())
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return

        cooldowns_search[user_id] = current_time

        try:
            user_id = interaction.user.id
            if str(user_id) in open("blocked_users.txt").read():
                error_embed = discord.Embed(title="Ошибка", description="Ваш аккаунт заблокирован", color=discord.Color.red())
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return
            user_folder = os.path.join("aika_users", str(user_id))
            if not os.path.exists(user_folder):
                error_embed = discord.Embed(title="Ошибка", description="Хм, похоже я с вами еще не знакома. Пожалуйста, воспользуйтесь командой `/register` чтобы создать свой аккаунт", color=discord.Color.red())
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return

            prompt_short_answer = f"Что такое {search_query}?"
            response_short_answer = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system",
                     "content": "You are a search assistant named Aika Search. Your task is to give answers to user requests no longer than 512 characters."},
                    {"role": "user", "content": prompt_short_answer}
                ],
                api_key=api_key
            )
            short_answer = response_short_answer.choices[0].message.content.strip()

            prompt_search_results = f"Chatting in Русский. You are a search engine named Aika Search. Your task is to display a list of sites corresponding to the request for each request and give it a brief description. An example of showing the site **[Site name](link to the site)** is a brief description of the site. You must send only a list of sites without external additions and introductions, only a list of sites and nothing more. My query: {search_query}."

            response_search_results = openai.Completion.create(
                engine="text-davinci-003",
                max_tokens=1024,
                prompt=prompt_search_results,
                api_key=api_key
            )
            search_results = response_search_results.choices[0].text.strip()

            log_embed = discord.Embed(title="Aika Aidex Log", color=0x00ff00)
            log_embed.add_field(name="User", value=interaction.user.display_name, inline=False)
            log_embed.add_field(name="User ID", value=interaction.user.id, inline=False)
            log_embed.add_field(name="Server", value=interaction.guild.name if interaction.guild else "Direct Message", inline=False)
            log_embed.add_field(name="Server ID", value=interaction.guild.id if interaction.guild else "N/A", inline=False)
            log_embed.add_field(name="Channel", value=interaction.channel.name if isinstance(interaction.channel, discord.TextChannel) else "Direct Message", inline=False)
            log_embed.add_field(name="Query", value=search_query, inline=False)
            log_embed.add_field(name="Short answer", value=short_answer, inline=False)
            log_embed.add_field(name="Search result", value=search_results, inline=False)
            channel_id = 000000000000000000
            channel = self.bot.get_channel(channel_id)
            if channel:
                await channel.send(embed=log_embed)

            embed = discord.Embed(title="Aika Aidex (beta)", color=0x921294)
            embed.add_field(name="Запрос:", value=f"{search_query}", inline=False)
            if not os.path.exists(plan_file_path) or plan_text in ["Free", "Basic", "Standart"]:
                embed.add_field(name="Aika AI:", value=f'```{short_answer}```', inline=False)
                embed.add_field(name="Реклама:", value='**Мы ведем набор в нашу PR и в случае вашего вступления вы получите бесрочный Premium. [Подробнее тут](https://discord.com/channels/1011882995076050987/1112087346549100727)**', inline=False)
            else:
                embed.add_field(name="Aika AI:", value=f'```{short_answer}```', inline=False)
            embed.add_field(name="Результат поиска:", value=search_results, inline=False)
            embed.set_footer(text=f"Powered by Aika Aidex", icon_url="https://example.com/")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            print(f"{e}")
            error_message = f"Извините за неудобства. В настоящее время Айка не может обработать ваш запрос из-за технических проблем. Мы работаем над их устранением и ожидаем, что проблема будет решена в ближайшее время. Просим вас не удалять Айку с сервера. Спасибо за понимание."
            error_embed = discord.Embed(title="Ошибка", description=error_message, color=discord.Color.red())
            await interaction.followup.send(embed=error_embed, ephemeral=True)

    @app_commands.command(name="gen-bot", description="Сгенерировать бота")
    @app_commands.choices(platform=[
        app_commands.Choice(name="VK", value="vk"),
        app_commands.Choice(name="Discord", value="discord"),
        app_commands.Choice(name="Telegram", value="telegram")
    ])
    @app_commands.choices(lang=[
        app_commands.Choice(name="Python", value="python"),
        app_commands.Choice(name="JavaScript", value="javascript")
    ])
    async def generate_bot(self, interaction: discord.Interaction, platform: str, lang: str, *, prompt: str):
        await interaction.response.defer()

        try:
            user_id = interaction.user.id
            user_folder = os.path.join("aika_users", str(user_id))
            plan_file_path = os.path.join(user_folder, "plus", "plan.txt")

            if str(user_id) in open("blocked_users.txt").read():
                error_embed = discord.Embed(title="Ошибка", description="Ваш аккаунт заблокирован.", color=discord.Color.red())
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return

            if not os.path.exists(user_folder):
                error_embed = discord.Embed(title="Ошибка", description="Хм, похоже я с вами еще не знакома. Пожалуйста, воспользуйтесь командой `/register` чтобы создать свой аккаунт", color=discord.Color.red())
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return

            if not os.path.exists(plan_file_path):
                error_embed = discord.Embed(title="Ошибка", description="Доступ к этой команде разрешен только для пользователей с тарифами Ultimate и Excelsior.", color=discord.Color.red())
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return

            with open(plan_file_path, "r") as plan_file:
                plan_text = plan_file.read().strip()

            if plan_text not in ["Ultimate", "Excelsior"]:
                error_embed = discord.Embed(title="Ошибка", description="Доступ к этой команде разрешен только для пользователей с тарифами Ultimate и Excelsior.", color=discord.Color.red())
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return

            prompt_gen = f"Сгенерируй код для бота {platform} на языке программирования {lang}. Описание технического задания: {prompt}."

            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt_gen,
                max_tokens=2048,
                api_key=api_key
            )
            generated_code = response.choices[0].text.strip()

            log_embed = discord.Embed(title="Aika Gen Bots Log", color=0x00ff00)
            log_embed.add_field(name="User", value=interaction.user.display_name, inline=False)
            log_embed.add_field(name="User ID", value=interaction.user.id, inline=False)
            log_embed.add_field(name="Server", value=interaction.guild.name if interaction.guild else "Direct Message", inline=False)
            log_embed.add_field(name="Server ID", value=interaction.guild.id if interaction.guild else "N/A", inline=False)
            log_embed.add_field(name="Channel", value=interaction.channel.name if isinstance(interaction.channel, discord.TextChannel) else "Direct Message", inline=False)
            log_embed.add_field(name="Platform", value=platform, inline=False)
            log_embed.add_field(name="Lang", value=lang, inline=False)
            log_embed.add_field(name="Prompt", value=prompt, inline=False)
            log_embed.add_field(name="Code", value=generated_code, inline=False)
            channel_id = 000000000000000000
            channel = self.bot.get_channel(channel_id)
            if channel:
                await channel.send(embed=log_embed)

            file_extension = "py" if lang == "python" else "js"
            file_name = f"{platform}_{lang}_bot_{user_id}.{file_extension}"

            with open(os.path.join("tempbots", file_name), "w") as bot_file:
                bot_file.write(generated_code)

            await interaction.followup.send("Ваш бот был сгенерирован.", file=discord.File(os.path.join("tempbots", file_name)))
        except Exception as e:
            print(f"{e}")
            error_embed = discord.Embed(title="Ошибка", description="Извините за неудобства. В настоящее время Айка не может обработать ваш запрос из-за технических проблем. Мы работаем над их устранением и ожидаем, что проблема будет решена в ближайшее время. Просим вас не удалять Айку с сервера. Спасибо за понимание.", color=discord.Color.red())
            await interaction.followup.send(embed=error_embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Instruments(bot))