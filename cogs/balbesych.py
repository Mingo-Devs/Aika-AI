import os
from core.classes import Cog_Extension
import discord
import random
import time
from discord import app_commands

context_store = {}

cooldowns_balb_chat = {}
cooldowns_balb_text = {}
cooldowns_balb_quote = {}

class Balbesych(Cog_Extension):
    @app_commands.command(name="wipe-balb", description="Отчищает контекст диалога с AikaRM")
    async def wipe_balb(self, interaction: discord.Interaction):
        user = interaction.user.name
        message = f'Пользователь {user} использовал команду `/wipe-balb`'
        channel_id = 000000000000000000
        channel = self.bot.get_channel(channel_id)
        await channel.send(message)

        user_id = str(interaction.user.id)
        file_path = f'chats/{user_id}.txt'

        if str(user_id) in open("blocked_users.txt").read():
            error_embed = discord.Embed(title="Ошибка", description="Ваш аккаунт заблокирован.", color=discord.Color.red())
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return

        user_folder = os.path.join("aika_users", str(user_id))
        if not os.path.exists(user_folder):
            error_embed = discord.Embed(title="Ошибка", description="Хм, похоже я с вами еще не знакома. Пожалуйста, воспользуйтесь командой `/register` чтобы создать свой аккаунт", color=discord.Color.red())
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return

        with open(os.path.join(user_folder, "plus", "plan.txt"), "r") as f:
            plan = f.read().strip()

        if os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write("")

            success_embed = discord.Embed(title="Успех", description="Контекст успешно очищен.", color=discord.Color.green())
            await interaction.response.send_message(embed=success_embed, ephemeral=True)
        else:
            error_embed = discord.Embed(title="Ошибка", description="Диалог не найден.", color=discord.Color.red())
            await interaction.response.send_message(embed=error_embed, ephemeral=True)

    @app_commands.command(name="balb-chat", description="Веселое общение с Балбесычем")
    async def balb_chat(self, interaction: discord.Interaction, *, message: str):
        message = str(message)[:100]
        user_id = str(interaction.user.id)
        current_time = time.time()
        last_used_time = cooldowns_balb_chat.get(user_id, 0)

        if str(user_id) in open("blocked_users.txt").read():
            error_embed = discord.Embed(title="Ошибка", description="Ваш аккаунт заблокирован.", color=discord.Color.red())
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return

        user_folder = os.path.join("aika_users", str(user_id))

        if not os.path.exists(user_folder):
            error_embed = discord.Embed(title="Ошибка", description="Хм, похоже я с вами еще не знакома. Пожалуйста, воспользуйтесь командой `/register` чтобы создать свой аккаунт", color=discord.Color.red())
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return

        plan_file_path = os.path.join(user_folder, "plus", "plan.txt")

        if not os.path.exists(plan_file_path):
            cooldown = 30
        else:
            with open(plan_file_path, "r") as plan_file:
                plan_text = plan_file.read().strip()

            if plan_text in ["Basic", "Standart", "Ultimate", "Excelsior"]:
                cooldown = 0
            else:
                cooldown = 30

        if current_time - last_used_time < cooldown:
            error_message = f"Ваш тарифный план не позволяет использовать эту команду чаще 1 раза в {int(cooldown)} секунд. Подробнее по команде `/plus`"
            error_embed = discord.Embed(title="Ошибка", description=error_message, color=discord.Color.red())
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return

        user_file = os.path.join("chats", f"{user_id}.txt")

        with open(user_file, "a") as f:
            words = message.split()
            for word in words:
                f.write(f"{word}\n")

        with open(user_file, "r") as f:
            words = f.read().splitlines()

        num_words = random.randint(1, 20)
        random_words = [random.choice(words) for _ in range(num_words)]
        random_sentence = ' '.join(random_words)

        if len(random_sentence) > 2000:
            random_sentence = random_sentence[:2000]

        log_embed = discord.Embed(title="Balbesych Chat Log", color=0x00ff00)
        log_embed.add_field(name="User", value=interaction.user.display_name, inline=False)
        log_embed.add_field(name="User ID", value=interaction.user.id, inline=False)
        log_embed.add_field(name="Server", value=interaction.guild.name if interaction.guild else "Direct Message", inline=False)
        log_embed.add_field(name="Server ID", value=interaction.guild.id if interaction.guild else "N/A", inline=False)
        log_embed.add_field(name="Channel", value=interaction.channel.name if isinstance(interaction.channel, discord.TextChannel) else "Direct Message", inline=False)
        log_embed.add_field(name="Prompt", value=message, inline=False)
        log_embed.add_field(name="Model Respone", value=random_sentence, inline=False)
        channel_id = 000000000000000000
        channel = self.bot.get_channel(channel_id)
        if channel:
            await channel.send(embed=log_embed)
        await interaction.response.send_message(f"**Балбесыч:** {random_sentence}")
        cooldowns_balb_chat[user_id] = current_time

    @app_commands.command(name="balb-text", description="Балбесыч сгенерирует случайный текст")
    async def balb_text(self, interaction: discord.Interaction, *, words: str = None):
        if words is not None:
            words = str(words)[:100]
        user_id = str(interaction.user.id)
        current_time = time.time()
        last_used_time = cooldowns_balb_text.get(user_id, 0)

        if str(user_id) in open("blocked_users.txt").read():
            error_embed = discord.Embed(title="Ошибка", description="Ваш аккаунт заблокирован.", color=discord.Color.red())
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return

        user_folder = os.path.join("aika_users", str(user_id))
        plan_path = os.path.join(user_folder, "plus", "plan.txt")
        if not os.path.exists(user_folder):
            error_embed = discord.Embed(title="Ошибка", description="Хм, похоже я с вами еще не знакома. Пожалуйста, воспользуйтесь командой `/register` чтобы создать свой аккаунт", color=discord.Color.red())
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return

        with open(plan_path, "r") as f:
            user_plan = f.read().strip()

        premium_plans = ["Standart", "Ultimate", "Excelsior"]
        if user_plan in premium_plans:
            pass
        elif user_plan in ["Free", "Basic"] and current_time - last_used_time < 86400:
            error_message = "Ваш тарифный план не позволяет использовать эту команду больше 1 раза в день. **Это реклама** Подробнее по команде `/plus`"
            error_embed = discord.Embed(title="Ошибка", description=error_message, color=discord.Color.red())
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return
        elif current_time - last_used_time < 86400:
            error_message = "Ваш тарифный план не позволяет использовать эту команду больше 1 раза в день. Подробнее по команде `/plus`"
            error_embed = discord.Embed(title="Ошибка", description=error_message, color=discord.Color.red())
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return

        try:
            cooldowns_balb_text[user_id] = current_time
            if words is None:
                with open('words.txt', 'r') as f:
                    words = f.read().splitlines()
            else:
                words = words.split(',')
            num_words = random.randint(1, 50)
            random_words = [random.choice(words) for _ in range(num_words)]
            random_sentence = ' '.join(random_words)
            if len(random_sentence) > 2000:
                random_sentence = random_sentence[:2000]

            log_embed = discord.Embed(title="Balbesych Text Log", color=0x00ff00)
            log_embed.add_field(name="User", value=interaction.user.display_name, inline=False)
            log_embed.add_field(name="User ID", value=interaction.user.id, inline=False)
            log_embed.add_field(name="Server", value=interaction.guild.name if interaction.guild else "Direct Message", inline=False)
            log_embed.add_field(name="Server ID", value=interaction.guild.id if interaction.guild else "N/A", inline=False)
            log_embed.add_field(name="Channel", value=interaction.channel.name if isinstance(interaction.channel, discord.TextChannel) else "Direct Message", inline=False)
            if words is not None:
                log_embed.add_field(name="Words", value=words, inline=False)
            log_embed.add_field(name="Model Response", value=random_sentence, inline=False)
            channel_id = 000000000000000000
            channel = self.bot.get_channel(channel_id)
            if channel:
                await channel.send(embed=log_embed)

            response_message = f"**Балбесыч:** {random_sentence}"
            await interaction.response.send_message(response_message)
        except Exception as e:
            print(f"{e}")
            error_message = "При обработке сообщения произошла ошибка"
            error_embed = discord.Embed(title="Ошибка", description=error_message, color=discord.Color.red())
            await interaction.response.send_message(embed=error_embed, ephemeral=True)

    @app_commands.command(name="balb-quote", description="Балбесыч сгенерирует случайную цитату случайного человека")
    async def balb_quote(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        current_time = time.time()
        last_used_time = cooldowns_balb_quote.get(user_id, 0)

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
            cooldown = 86400
        else:
            with open(plan_file_path, "r") as plan_file:
                plan_text = plan_file.read().strip()

            if plan_text in ["Basic", "Standart", "Ultimate", "Excelsior"]:
                cooldown = 0
            else:
                cooldown = 86400

        if current_time - last_used_time < cooldown:
            error_embed = discord.Embed(title="Ошибка", description=f"Ваш тарифный план не позволяет использовать эту команду больше 1 раза в {int(cooldown / 3600)} часов. Подробнее по команде `/plus`", color=discord.Color.red())
            await interaction.followup.send(embed=error_embed, ephemeral=True)
            return

        with open('words.txt', 'r') as f:
            words = f.read().splitlines()
        with open('soname.txt', 'r') as f:
            sonames = f.read().splitlines()
        with open('name.txt', 'r') as f:
            names = f.read().splitlines()
        num_words = random.randint(10, 20)
        random_words = [random.choice(words) for _ in range(num_words)]
        random_sentence = ' '.join(random_words)
        random_name = random.choice(names)
        random_soname = random.choice(sonames)
        random_quote = f"> *{random_sentence}*\n***{random_soname} {random_name}***"

        log_embed = discord.Embed(title="Balbesych Quote Log", color=0x00ff00)
        log_embed.add_field(name="User", value=interaction.user.display_name, inline=False)
        log_embed.add_field(name="User ID", value=interaction.user.id, inline=False)
        log_embed.add_field(name="Server", value=interaction.guild.name if interaction.guild else "Direct Message", inline=False)
        log_embed.add_field(name="Server ID", value=interaction.guild.id if interaction.guild else "N/A", inline=False)
        log_embed.add_field(name="Channel", value=interaction.channel.name if isinstance(interaction.channel, discord.TextChannel) else "Direct Message", inline=False)
        log_embed.add_field(name="Model Respone", value=random_quote, inline=False)
        channel_id = 000000000000000000
        channel = self.bot.get_channel(channel_id)
        if channel:
            await channel.send(embed=log_embed)
        await interaction.response.send_message(f"**Балбесыч:** {random_quote}")

        cooldowns_balb_quote[user_id] = current_time

async def setup(bot):
    await bot.add_cog(Balbesych(bot))