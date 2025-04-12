from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from keep_alive import keep_alive
import os
from PIL import Image, ImageDraw, ImageFont
import random
import io

# Start the Replit web server to keep the bot alive
keep_alive()

# Get the bot token from Replit Secrets
TOKEN = os.environ['TOKEN']

# Define the /go command
async def go_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    # Delete the original /go message
    await message.delete()

    # Get the text content after /go
    text = ' '.join(context.args)
    if not text:
        return

    # If it's a reply to someone else's message (not a bot)
    reply_to = message.reply_to_message
    if reply_to and not reply_to.from_user.is_bot:
        await context.bot.send_message(
            chat_id=message.chat_id,
            text=text,
            reply_to_message_id=reply_to.message_id
        )
    else:
        # Send it as a regular message
        await context.bot.send_message(
            chat_id=message.chat_id,
            text=text
        )

# Define the /voice command
async def voice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from gtts import gTTS
    import tempfile
    import os

    message = update.message
    if not message:
        return

    # Get the command text
    text = ' '.join(context.args)
    if not text:
        return

    # Get reply message ID if it's a reply
    reply_to = message.reply_to_message
    reply_msg_id = reply_to.message_id if reply_to else None

    # Delete the command message
    await message.delete()

    # Create temporary file for voice message
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
        # Convert text to speech in Sinhala
        tts = gTTS(text=text, lang='si')
        tts.save(tmp_file.name)
        
        # Send voice message as reply
        with open(tmp_file.name, 'rb') as audio:
            await context.bot.send_voice(
                chat_id=message.chat_id,
                voice=audio,
                reply_to_message_id=reply_msg_id
            )
        
        # Clean up temporary file
        os.unlink(tmp_file.name)

# Define the /stick command
async def stick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    # Get the text content
    text = ' '.join(context.args)
    if not text:
        return

    # Check if it's a reply
    reply_to = message.reply_to_message
    reply_msg_id = reply_to.message_id if reply_to else None

    # Delete the command message
    await message.delete()

    # Create image
    width, height = 512, 512
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD']
    bg_color = random.choice(colors)
    
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Calculate font size based on text length
    font_size = min(80, int(400 / len(text)))
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # Center the text
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) / 2
    y = (height - text_height) / 2
    
    # Add text with outline
    outline_color = '#FFFFFF'
    for offset in range(-2, 3):
        draw.text((x + offset, y), text, font=font, fill=outline_color)
        draw.text((x, y + offset), text, font=font, fill=outline_color)
    
    draw.text((x, y), text, font=font, fill='#000000')

    # Convert to webp
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='WEBP')
    img_byte_arr.seek(0)

    # Send as sticker, replying to original message if it exists
    await context.bot.send_sticker(
        chat_id=message.chat_id,
        sticker=img_byte_arr,
        reply_to_message_id=reply_msg_id  # This will be None for normal messages
    )

# Create the bot app and add the commands
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("go", go_command))
app.add_handler(CommandHandler("voice", voice_command))
app.add_handler(CommandHandler("stick", stick_command))

print("Bot is running...")
app.run_polling()
