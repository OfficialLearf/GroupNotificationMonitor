import pyautogui
import time
import os
from PIL import Image, ImageChops, ImageStat
import requests
from dotenv import load_dotenv



SCAN_INTERVAL = 1
ALERT_REGION = (0, 0, 500, 1080)
PREVIOUS_SCREENSHOT = "prev_alert.png"
CURRENT_SCREENSHOT = "current_alert.png"
SOUND_FILE = "notification.wav"

load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DISCORD_USER_ID = os.getenv("DISCORD_USER_ID")

#TESTS FOR THE ENV FILE
#print(f"DISCORD_WEBHOOK_URL: {DISCORD_WEBHOOK_URL}")
#print(f"TELEGRAM_BOT_TOKEN: {TELEGRAM_BOT_TOKEN}")
#print(f"TELEGRAM_CHAT_ID: {TELEGRAM_CHAT_ID}")
#print(f"DISCORD_USER_ID: {DISCORD_USER_ID}")

def send_telegram_notification(message):
    bot_token = TELEGRAM_BOT_TOKEN
    chat_id = TELEGRAM_CHAT_ID
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message
    }

    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("✅ Telegram message sent!")
    else:
        print("❌ Error sending Telegram message")

def send_discord_notification(message):
    webhook_url = DISCORD_WEBHOOK_URL

    user_id = DISCORD_USER_ID

    data = {
        "content": f"<@{user_id}> {message}"
    }

    response = requests.post(webhook_url, json=data)

    if response.status_code == 204:
        print("✅ Discord message sent")
    else:
        print("❌ Discord message failed")

def play_notification_sound():
     import winsound
     winsound.MessageBeep(winsound.MB_ICONASTERISK)
def get_alert_region():
    x, y, width, height = ALERT_REGION
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    return screenshot


def images_are_different(img1, img2, threshold=10):
    if img1.size != img2.size or img1.mode != img2.mode:
        return True

    diff = ImageChops.difference(img1, img2).convert("L")
    stat = ImageStat.Stat(diff)
    rms = stat.rms[0]

    diff.save("diff.png")

    return rms > threshold

def monitor_facebook_alerts():
    print("Starting Facebook alerts monitor with sound notifications...")
    print(f"Monitoring region: {ALERT_REGION}")
    print(f"Scan interval: {SCAN_INTERVAL} seconds")
    print("Press Ctrl+C to stop\n")

    # Capture initial image
    previous_image = get_alert_region()
    previous_image.save(PREVIOUS_SCREENSHOT)

    while True:
        time.sleep(SCAN_INTERVAL)

        try:
            current_image = get_alert_region()
            current_image.save(CURRENT_SCREENSHOT)

            if images_are_different(previous_image, current_image):
                timestamp = time.strftime('%H:%M:%S')
                print(f"[{timestamp}] Alert detected!")
                send_discord_notification("New Facebook alert detected!")
                send_telegram_notification("New Facebook Alert detected!")
                play_notification_sound()

                # Update previous image
                previous_image = current_image.copy()
                previous_image.save(PREVIOUS_SCREENSHOT)

        except pyautogui.ImageNotFoundException:
            print("Alert region not found on screen - is Facebook visible?")
        except Exception as e:
            print(f"Error: {str(e)}")
            continue


if __name__ == "__main__":
    try:
        monitor_facebook_alerts()
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
        # Clean up
        for file in [PREVIOUS_SCREENSHOT, CURRENT_SCREENSHOT, "diff.png"]:
            if os.path.exists(file):
                os.remove(file)
