# 🎙️ Picnic FM Broadcaster

Broadcast messages from [Picnic API](https://www.picnicapp.link/) live over **FM radio** using a Raspberry Pi 5.  
This project fetches all active groups & messages via the Picnic API, converts them into audio, and transmits them over FM using either:  
- A **USB FM transmitter (recommended)**, or  

si4713_ctl.py → Helper class to control the Si4713 FM transmitter

picnic_fm_broadcaster.py → Main script that:

Polls the Picnic API for new messages

Converts messages to speech (espeak-ng)

Plays them out via ALSA to your USB sound card


Si4713 broadcasts the audio over FM
Broadcast messages from Picnic API
 live over FM radio using a Raspberry Pi 5.
This project fetches all active groups & messages via the Picnic API, converts them into audio, and transmits them over FM using either: A USB FM transmitter (recommended),

---

## 📦 Installation

### 1. Clone this repo
```bash
git clone https://github.com/JoinPiCNiC/FMbroadcast.git
cd FMbroadcast
```

### 2. Create a Python virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

> Dependencies include:
> - `requests` (API requests)  
> - `gTTS` (text-to-speech to generate `.wav` files)  
> - `pydub` (audio conversions)  

### 4. Configure API credentials
Create a `.env` file in the project root:

```ini
PICNIC_API_KEY=your_api_key_here
```

---

## ▶️ Running the Broadcaster

Run the script:

```bash
python picnic_fm_broadcaster.py
```

This will:
1. Fetch all **active groups** from the Picnic API.  
2. Retrieve **new messages** for each group.  
3. Convert text messages to **speech audio (.wav)**.  
4. Play/transmit them live via your FM transmitter.  

---

## 🔧 FM Transmission Setup

### Option A: Using a USB FM transmitter (recommended)
- Plug in a cheap USB FM transmitter (see [suggested devices](#recommended-hardware)).  
- Update the script to call your transmitter’s CLI (e.g., `rtl_fm` or your device driver).  

### Option B: Using legacy GPIO method (not Pi 5)
- The original `fm_transmitter` tool (`markondej/fm_transmitter`) only works on Pi 1–4.  
- Pi 5 users **must use a USB FM adapter** instead.  

---

## ⏱️ Auto-Start on Boot
If you want this to run at reboot:

```bash
crontab -e
```

Add:
```
@reboot /home/admin/FMbroadcast/venv/bin/python /home/admin/FMbroadcast/picnic_fm_broadcaster.py
```

---

## 💻 Recommended Hardware
- **USB FM Transmitter Dongle** (Amazon has several under $20)  
- Raspberry Pi 5 (tested)  
- Small antenna for better range  

---

## ⚠️ Legal Note
FM transmission is regulated in most countries.  
Use low-power FM only for **testing, hobby, or educational purposes**.
