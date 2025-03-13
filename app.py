from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/screenshots', methods=['GET'])
def get_screenshots():
    app_id = request.args.get('app_id')
    if not app_id:
        return jsonify({"error": "App ID رو وارد کن"}), 400

    url = f"https://apps.apple.com/us/app/id{app_id}"
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return jsonify({"error": f"خطا در اتصال: {response.status_code}"}), 500

    soup = BeautifulSoup(response.text, "html.parser")
    screenshot_urls = []

    # روش 1: پیدا کردن تگ source و گرفتن بالاترین رزولوشن
    screenshots = soup.find_all("source", {"type": "image/jpeg"})
    for source in screenshots:
        srcset = source.get("srcset", "")
        if srcset:
            # جدا کردن رزولوشن‌ها و انتخاب بالاترین
            urls = srcset.split(",")
            best_url = max(urls, key=lambda x: int(x.split()[-1].replace("w", "")) if "w" in x.split()[-1] else 0)
            img_url = best_url.strip().split(" ")[0]
            if img_url:
                screenshot_urls.append(img_url)

    # روش 2: تگ img با کلاس we-artwork
    if not screenshot_urls:
        screenshots = soup.find_all("img", attrs={"class": lambda x: x and "we-artwork" in x})
        for img in screenshots:
            img_url = img.get("src")
            if img_url and "screenshot" in img_url.lower():
                screenshot_urls.append(img_url)

    if not screenshot_urls:
        return jsonify({"error": "اسکرین‌شاتی پیدا نشد", "html": str(soup)[:1000]}), 404

    return jsonify({"screenshots": screenshot_urls})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
