import pyautogui
import time
import os
from PIL import Image, ImageChops, ImageStat
import sys
import requests
from pymupdf import message

# Configuration
SCAN_INTERVAL = 1  # seconds between checks
ALERT_REGION = (0, 0, 500, 1080)  # Full height (if 1080p), 500px wide from the left
PREVIOUS_SCREENSHOT = "prev_alert.png"
CURRENT_SCREENSHOT = "current_alert.png"
SOUND_FILE = "notification.wav"  # You can replace this with your own sound file

def send_discord_notification(meesage):
    webhook_url = "https://discord.com/api/webhooks/1362438101271707819/yZNXTT8PSwIXa5yN3aL0LZgqM6KdZjBvNA2FQBlg39z8n_iaqSXPrVEcEqnOVuFeVayf"
    user_id = "@Learf"
    data = {
        "content" : f"{user_id}"
    }
    response = requests.post(webhook_url, data=data)
    if response.status_code == 204:
        print("Discord message sent")
    else:
        print("Discord message failed")


def play_notification_sound():
    """Play a notification sound with fallback options"""
    try:
        # Try Windows built-in sound first
        import winsound
        winsound.MessageBeep(winsound.MB_ICONASTERISK)
    except (ImportError, AttributeError):
        try:
            # Fallback to playsound for cross-platform
            from playsound import playsound
            if os.path.exists(SOUND_FILE):
                playsound(SOUND_FILE)
            else:
                print("Sound file not found. Using system beep instead.")
                winsound.Beep(1000, 500)
        except ImportError:
            print("\a")  # ASCII bell character as last resort
            print("Could not play sound - install playsound for better notifications")


def get_alert_region():
    """Capture the alert region of the screen"""
    x, y, width, height = ALERT_REGION
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    return screenshot


def images_are_different(img1, img2, threshold=10):
    """Compare two images and return True if they're visually different"""
    if img1.size != img2.size or img1.mode != img2.mode:
        return True

    diff = ImageChops.difference(img1, img2).convert("L")
    stat = ImageStat.Stat(diff)
    rms = stat.rms[0]

    # Optional: save diff for debugging
    diff.save("diff.png")

    return rms > threshold


def show_notification(message):
    """Show a notification using plyer"""
    try:
        from plyer import notification
        notification.notify(
            title="Facebook Alert",
            message=message,
            app_name="Facebook Alert Monitor"
        )
    except ImportError:
        print(f"Notification: {message} (Install plyer for popups)")


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
                show_notification("New Facebook alert detected!")
                send_discord_notification("New Facebook alert detected!")
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
