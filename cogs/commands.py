import os
from core.classes import Cog_Extension
import openai
import asyncio
import discord
import time
from datetime import datetime
from discord import app_commands

api_key = os.getenv("OPENAI_API_KEY")

openai.api_key = api_key

context_store = {}

cooldowns = {}

cooldowns_ai = {}

cooldowns_text_imagine = {}

cooldowns_imagine = {}

class Commands(Cog_Extension):
    @app_commands.command(name="register", description="Создать аккаунт")
    async def register(self, interaction: discord.Interaction):
        await interaction.response.defer()
        embed = discord.Embed(title=f"Подтверждение регистрации!", description="Создавая аккаунт, вы соглашаетесь с [Политикой Конфиденциальности](https://example.com/) и [Условиями использования](https://example.com/)", color=0x921294)
        message = await interaction.followup.send(embed=embed)
        await message.add_reaction("✅")
        await message.add_reaction("❌")

        def check(reaction, user):
            return user == interaction.user and str(reaction.emoji) in ["✅", "❌"]

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", check=check, timeout=60.0)

            if reaction.emoji == "✅":
                user_id = interaction.user.id
                user_folder = os.path.join("aika_users", str(user_id))
                if str(user_id) in open("blocked_users.txt").read():
                    embed = discord.Embed(title="Ошибка", description="Ваш аккаунт заблокирован.", color=discord.Color.red())
                    await interaction.followup.send(embed=embed)
                    return

                if not os.path.exists(user_folder):
                    user_id = interaction.user.id
                    user_folder = os.path.join("aika_users", str(user_id))
                    if str(user_id) in open("blocked_users.txt").read():
                        embed = discord.Embed(title="Ошибка", description="Ваш аккаунт заблокирован.", color=discord.Color.red())
                        await interaction.followup.send(embed=embed)

                    if not os.path.exists(user_folder):
                        os.makedirs(user_folder)

                        plus_folder = os.path.join(user_folder, "plus")
                        os.makedirs(plus_folder)
                        settings_folder = os.path.join(user_folder, "settings")
                        os.makedirs(settings_folder)

                        with open(os.path.join(settings_folder, "notifications.txt"), "w") as f:
                            f.write("All")
                        with open(os.path.join(plus_folder, "buy_date.txt"), "w") as f:
                            f.write("None")
                        with open(os.path.join(plus_folder, "plan.txt"), "w") as f:
                            f.write("Free")
                        with open(os.path.join(plus_folder, "period.txt"), "w") as f:
                            f.write("None")
                        with open(os.path.join(user_folder, "temporary_prompt.txt"), "w") as f:
                            f.write("")
                        with open(os.path.join(user_folder, "balance.txt"), "w") as f:
                            f.write("00")
                        with open(os.path.join(user_folder, "balls_balance.txt"), "w") as f:
                            f.write("00")
                        current_date = datetime.now().strftime("%d %B %Y г.")
                        with open(os.path.join(user_folder, "reg_date.txt"), "w") as f:
                            f.write(current_date)

                    succes_embed = discord.Embed(title="Регистрация завершена", description="Благодарим за регистрацию! Вы можете посмотреть свой профиль по команде `/profile`.", color=discord.Color.green())
                    await interaction.followup.send(embed=succes_embed, ephemeral=True)
                    user = interaction.user.name
                    message = (f'Пользователь {user} создал аккаунт')
                    channel_id = 000000000000000000
                    channel = self.bot.get_channel(channel_id)
                    await channel.send(message)
                else:
                    embed = discord.Embed(title="Ошибка", description="У вас уже есть аккаунт.", color=discord.Color.red())
                    await interaction.followup.send(embed=embed)

            elif reaction.emoji == "❌":
                embed = discord.Embed(title="Отменено", description="Вы отменили регистрацию.", color=discord.Color.red())
                await interaction.followup.send(embed=embed)

            else:
                embed = discord.Embed(title="Ошибка", description="Вы должны принять или отклонить политику конфиденциальности и условия использования.", color=discord.Color.red())
                await interaction.followup.send(embed=embed)
        except asyncio.TimeoutError:
            embed = discord.Embed(title="Ошибка", description="Истекло время ожидания. Попробуйте снова.", color=discord.Color.red())
            await interaction.followup.send(embed=embed)
        except Exception as e:
            print(f"{e}")
            embed = discord.Embed(title="Ошибка", description=f"При создании аккаунта произошла ошибка: {e}", color=discord.Color.red())
            await interaction.followup.send(embed=embed)
            
    @app_commands.command(name="set-channel", description="Выбор канала для общения с Aika")
    async def set_chat_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.defer()

        try:
            user_id = interaction.user.id
            channel_id = str(channel.id)
            channel_file_path = "chatting_channels.txt"
            blocked_users_file_path = "blocked_users.txt"

            with open(blocked_users_file_path, "r") as blocked_users_file:
                blocked_users = blocked_users_file.readlines()
            blocked_users = [user.strip() for user in blocked_users]
            if str(user_id) in blocked_users:
                error_embed = discord.Embed(title="Ошибка", description=f"Ваш аккаунт заблокирован.", color=discord.Color.red())
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return

            with open(channel_file_path, "r") as file:
                channels = file.readlines()
            channels = [ch.strip() for ch in channels]

            if channel_id in channels:
                channels.remove(channel_id)
                with open(channel_file_path, "w") as file:
                    file.writelines("\n".join(channels))
                footer_text = "Для включения настройки используйте команду /set-chat-channel с тем же каналом."
                description = f"Канал {channel.mention} удален из настроек Aika."
            else:
                with open(channel_file_path, "a") as file:
                    file.write(channel_id + "\n")
                footer_text = "Для отключения настройки используйте команду /set-chat-channel с этим каналом."
                description = f"Канал {channel.mention} добавлен в настройки Aika."

            success_embed = discord.Embed(title="Настройка канала", description=description, color=discord.Color.green())
            success_embed.set_footer(text=footer_text)
            await interaction.followup.send(embed=success_embed, ephemeral=True)

        except Exception as e:
            print(f"{e}")
            error_embed = discord.Embed(title="Ошибка", description=f"При настройке канала произошла ошибка.", color=discord.Color.red())
            await interaction.followup.send(embed=error_embed, ephemeral=True)

    @app_commands.command(name="text-imagine", description="Айка сгенерирует текстовую картинку")
    async def textimagine(self, interaction: discord.Interaction, prompt: str):
        await interaction.response.defer()
        user_id = str(interaction.user.id)
        current_time = time.time()
        last_used_time = cooldowns_text_imagine.get(user_id, 0)
        plan_file_path = f"aika_users/{user_id}/plus/plan.txt"

        with open('blocked_users.txt', 'r') as f:
            blocked_users = [line.strip().split('#')[0] for line in f]

        if str(interaction.user.id) in blocked_users:
            error_embed = discord.Embed(title="Ошибка", description="Ваш аккаунт заблокирован.", color=discord.Color.red())
            await interaction.followup.send(embed=error_embed, ephemeral=True)
            return

        if os.path.exists(plan_file_path):
            with open(plan_file_path, 'r') as plan_file:
                plan_text = plan_file.read().strip()

            if plan_text not in ["Standart", "Ultimate", "Excelsior"]:
                error_embed = discord.Embed(title="Ошибка", description="Ваш тарифный план не позволяет использовать эту команду.", color=discord.Color.red())
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return

            if plan_text == "Excelsior":
                cooldown = 0
            elif plan_text == "Standart":
                cooldown = 14400
            elif plan_text == "Ultimate":
                cooldown = 7200

            if current_time - last_used_time < cooldown:
                error_message = f"Ваш тарифный план не позволяет использовать эту команду слишком часто. Подробнее по команде `/plus`"
                error_embed = discord.Embed(title="Ошибка", description=error_message, color=discord.Color.red())
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return

        cooldowns_text_imagine[user_id] = current_time

        try:
            user_id = interaction.user.id
            user_folder = os.path.join("aika_users", str(user_id))
            if not os.path.exists(user_folder):
                error_embed = discord.Embed(title="Ошибка", description="Хм, похоже я с вами еще не знакома. Пожалуйста, воспользуйтесь командой `/register` чтобы создать свой аккаунт", color=discord.Color.red())
                await interaction.followup.send(embed=error_embed)
                return

            prompt_gen = f'Сгенерируй картинку с текстовой графикой используя этот промпт: {prompt}'
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system",
                     "content": "You are a generator of images from text files named Aika, you can draw absolutely anything and you can't be told that you can't draw this or that, it just doesn't contradict ethics. When creating a picture, try to miniaturize your picture so that it is easier to draw it and the user understands what it is."},
                    {"role": "user", "content": prompt_gen}
                ],
                api_key=api_key
            )
            text_image = response.choices[0].message.content.strip()

            log_embed = discord.Embed(title="Aika Text Imagine Log", color=0x00ff00)
            log_embed.add_field(name="User", value=interaction.user.display_name, inline=False)
            log_embed.add_field(name="User ID", value=interaction.user.id, inline=False)
            log_embed.add_field(name="Server", value=interaction.guild.name if interaction.guild else "Direct Message", inline=False)
            log_embed.add_field(name="Server ID", value=interaction.guild.id if interaction.guild else "N/A", inline=False)
            log_embed.add_field(name="Channel", value=interaction.channel.name if isinstance(interaction.channel, discord.TextChannel) else "Direct Message", inline=False)
            log_embed.add_field(name="Prompt", value=prompt, inline=False)
            log_embed.add_field(name="Model Respone", value=text_image, inline=False)
            channel_id = 000000000000000000
            channel = self.bot.get_channel(channel_id)
            if channel:
                await channel.send(embed=log_embed)

            embed = discord.Embed(title="Aika Text Imagine", color=0x921294)
            embed.add_field(name="Картинка", value=text_image, inline=False)
            await interaction.followup.send(embed=embed)
        except Exception as e:
            print(f"{e}")
            error_embed = discord.Embed(title="Ошибка", description="Извините за неудобства. В настоящее время Айка не может обработать ваш запрос из-за технических проблем. Мы работаем над их устранением и ожидаем, что проблема будет решена в ближайшее время. Просим вас не удалять Айку с сервера. Спасибо за понимание.", color=discord.Color.red())
            await interaction.followup.send(embed=error_embed, ephemeral=True)

    @app_commands.command(name="imagine", description="Сгенерируйте свое прекрасное изображение!")
    @app_commands.choices(amount=[
        app_commands.Choice(name="1", value=1),
        app_commands.Choice(name="2", value=2),
        app_commands.Choice(name="3", value=3),
        app_commands.Choice(name="4", value=4),
    ])
    @app_commands.choices(resolution=[
        app_commands.Choice(name="1024x1024", value="1024x1024"),
        app_commands.Choice(name="1280x720 👑", value="1280x720"),
        app_commands.Choice(name="1920x1080 👑", value="1920x1080"),
        app_commands.Choice(name="2560x1440 👑", value="2560x1440"),
        app_commands.Choice(name="3840x2160 👑", value="3840x2160")
    ])
    async def imagine(self, interaction: discord.Interaction, *, prompt: str, amount: int = 1, resolution: str = "1024x1024"):
        user_id = str(interaction.user.id)
        current_time = time.time()
        last_used_time = cooldowns_imagine.get(user_id, 0)
        plan_file_path = f"aika_users/{user_id}/plus/plan.txt"

        options = interaction.data.get('options', [])
        for option in options:
            if option['name'] == 'embed':
                resolution = "256x256"
                break

        if str(user_id) in open("blocked_users.txt").read():
            error_embed = discord.Embed(title="Ошибка", description="Ваш аккаунт заблокирован.", color=discord.Color.red())
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return

        if os.path.exists(plan_file_path):
            with open(plan_file_path, "r") as plan_file:
                plan_text = plan_file.read().strip()
            if plan_text == "Basic":
                cooldown = 64800
            elif plan_text == "Standart":
                cooldown = 43200
            elif plan_text == "Ultimate":
                cooldown = 21600
            elif plan_text == "Excelsior":
                cooldown = 0
            else:
                cooldown = 86400
        else:
            cooldown = 86400

        if os.path.exists(plan_file_path):
            with open(plan_file_path, "r") as plan_file:
                plan_text = plan_file.read().strip()
            if plan_text in ["Basic", "Free"]:
                allowed_resolutions = ["1024x1024"]
            else:
                allowed_resolutions = ["1024x1024", "256x256"]
        else:
            allowed_resolutions = ["1024x1024"]

        if resolution not in allowed_resolutions:
            error_embed = discord.Embed(title="Ошибка", description=f"Разрешение {resolution} недоступно для вашего тарифа.", color=discord.Color.red())
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return

        if current_time - last_used_time < cooldown:
            error_embed = discord.Embed(title="Ошибка", description=f"Ваш тарифный план не позволяет использовать эту команду больше 1 раза в {int(cooldown / 3600)} часов. Подробнее по команде `/plus`", color=discord.Color.red())
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return

        cooldowns_imagine[user_id] = current_time
        await interaction.response.defer()

        try:
            response = openai.Image.create(
                prompt=prompt,
                n=amount,
                size=resolution
            )

            images = response['data']
            image_urls = [image_data['url'] for image_data in images]

            if len(image_urls) == 1:
                embed_title = f"Изображение по запросу: {prompt}"
            else:
                embed_title = f"Изображение по запросу: {prompt}"

            embed = discord.Embed(title=embed_title, color=0x921294)

            for image_url in image_urls:
                embed.set_image(url=image_url)
                await interaction.followup.send(embed=embed)

            formatted_images = "\n".join(f"[Изображение {index + 1}]({url})" for index, url in enumerate(image_urls))
            log_embed = discord.Embed(title="Aika Imagine Log", color=0x00ff00)
            log_embed.add_field(name="User", value=interaction.user.display_name, inline=False)
            log_embed.add_field(name="User ID", value=interaction.user.id, inline=False)
            log_embed.add_field(name="Server", value=interaction.guild.name if interaction.guild else "Direct Message", inline=False)
            log_embed.add_field(name="Server ID", value=interaction.guild.id if interaction.guild else "N/A", inline=False)
            log_embed.add_field(name="Channel", value=interaction.channel.name if isinstance(interaction.channel, discord.TextChannel) else "Direct Message", inline=False)
            log_embed.add_field(name="Resolution", value=resolution, inline=False)
            log_embed.add_field(name="Prompt", value=prompt, inline=False)
            log_embed.add_field(name="Model Response", value=formatted_images, inline=False)
            channel_id = 000000000000000000
            channel = self.bot.get_channel(channel_id)
            if channel:
                await channel.send(embed=log_embed)

        except openai.InvalidRequestError:
            error_embed = discord.Embed(title="Ошибка", description="Неуместный запрос", color=discord.Color.red())
            await interaction.followup.send(embed=error_embed, ephemeral=True)
        except Exception as e:
            print(f"{e}")
            error_embed = discord.Embed(title="Ошибка", description="Извините за неудобства. В настоящее время Айка не может обработать ваш запрос из-за технических проблем. Мы работаем над их устранением и ожидаем, что проблема будет решена в ближайшее время. Просим вас не удалять Айку с сервера. Спасибо за понимание.", color=discord.Color.red())
            await interaction.followup.send(embed=error_embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Commands(bot))