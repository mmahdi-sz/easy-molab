# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "huggingface-hub==0.36.2",
#     "mcp==2.2.0",
#     "python-telegram-bot==22.8",
#     "qwen-asr==0.0.6",
#     "transformers==4.57.6",
# ]
# ///

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium", auto_download=["html"])


@app.cell
def _():
    return


@app.cell
def _():
    # ══ 🔑 فقط این خط رو تغییر بده ══
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
    API_ID = 17349
    API_HASH = "344583e45741c457fe1862106095a5eb"
    return API_HASH, API_ID, BOT_TOKEN


@app.cell
def _(API_HASH, API_ID, BOT_TOKEN):
    import marimo as mo
    import os, sys, subprocess, importlib, socket, json, math, time, threading, gc
    import urllib.request, urllib.error, warnings, logging, asyncio, html, shutil, traceback
    from datetime import timedelta

    # ══════════════════════════════════════════════
    #  ۱. دانلود باینری سرور محلی تلگرام
    # ══════════════════════════════════════════════
    if not os.path.exists("./telegram-bot-api"):
        print("📦 دانلود telegram-bot-api...")
        urllib.request.urlretrieve(
            "https://github.com/mmahdi-sz/telegram-bot-api-bin/releases/download/v10.3/telegram-bot-api",
            "telegram-bot-api"
        )
        os.chmod("telegram-bot-api", 0o755)
        print("✅ باینری آماده شد")

    # ══════════════════════════════════════════════
    #  ۲. نصب پکیج‌ها و محیط ایزوله ترجمه
    # ══════════════════════════════════════════════
    print("📦 نصب و بررسی وابستگی‌ها...")
    subprocess.run(["apt-get", "install", "-y", "-qq", "ffmpeg", "fonts-noto-core"], capture_output=True)

    for _pkg, _pip in [
        ("telegram", "python-telegram-bot"),
        ("qwen_asr", "qwen-asr"),
        ("accelerate", "accelerate"),
        ("fireredvad", "fireredvad"),
        ("huggingface_hub", "huggingface_hub[cli]"),
        ("bitsandbytes", "bitsandbytes"),
        ("pysrt", "pysrt"),
        ("tqdm", "tqdm"),
    ]:
        try:
            importlib.import_module(_pkg)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", _pip])

    # محیط اختصاصی transformers 5 برای ورکر ترجمه Qwen3.6
    TF5_DIR = "/content/workspace_tg/tf5_env"
    if not os.path.exists(f"{TF5_DIR}/transformers"):
        print("📦 آماده‌سازی محیط ایزوله Transformers 5 برای مدل Qwen3.6...")
        os.makedirs(TF5_DIR, exist_ok=True)
        _up_cmd = ["uv", "pip", "install", "--target", TF5_DIR, "transformers>=5.18.0"] if shutil.which("uv") else [sys.executable, "-m", "pip", "install", "-q", "--target", TF5_DIR, "transformers>=5.18.0"]
        subprocess.check_call(_up_cmd)
        print("✅ محیط ایزوله ترجمه آماده شد")

    print("✅ تمام پکیج‌ها آماده شدند")

    # ══════════════════════════════════════════════
    #  ۳. بررسی اعتبار توکن
    # ══════════════════════════════════════════════
    _token_valid = False
    _bot_info = None
    _token_error = ""

    if BOT_TOKEN and BOT_TOKEN != "YOUR_BOT_TOKEN_HERE":
        try:
            _url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
            with urllib.request.urlopen(urllib.request.Request(_url, method="GET"), timeout=10) as _r:
                _res = json.loads(_r.read().decode("utf-8"))
                if _res.get("ok"):
                    _token_valid = True
                    _bot_info = _res.get("result", {})
                else:
                    _token_error = _res.get("description", "نامعتبر")
        except urllib.error.HTTPError as _e:
            try:
                _token_error = json.loads(_e.read().decode("utf-8")).get("description", str(_e))
            except:
                _token_error = str(_e)
        except Exception as _e:
            _token_error = str(_e)

    # پاک کردن webhook
    if _token_valid:
        try:
            urllib.request.urlopen(
                urllib.request.Request(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=true",
                    method="GET"
                ), timeout=10
            )
        except:
            pass

    os.environ["BOT_TOKEN"] = BOT_TOKEN
    os.environ["API_ID"] = str(API_ID)
    os.environ["API_HASH"] = API_HASH

    if not _token_valid:
        _msg = "⚠️ توکن را در سلول ۱ قرار دهید" if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" else f"❌ خطا توکن: {_token_error}"
        mo.stop(True, mo.md(_msg))

    _bot_username = _bot_info.get("username", "نامشخص") if _bot_info else "نامشخص"
    _bot_first = _bot_info.get("first_name", "نامشخص") if _bot_info else "نامشخص"
    print(f"✅ توکن معتبر — @{_bot_username}")

    # ══════════════════════════════════════════════
    #  ۴. سرکوب warning ها
    # ══════════════════════════════════════════════
    warnings.filterwarnings("ignore")
    os.environ.update({
        "PYTHONWARNINGS": "ignore", "TF_CPP_MIN_LOG_LEVEL": "3",
        "TRANSFORMERS_VERBOSITY": "error", "HF_HUB_DISABLE_PROGRESS_BARS": "1",
        "TQDM_DISABLE": "1", "TOKENIZERS_PARALLELISM": "false",
    })
    for _lg in ["urllib3", "telegram", "httpx", "httpcore", "huggingface_hub", "transformers", "tokenizers", "absl"]:
        logging.getLogger(_lg).setLevel(logging.ERROR)
    logging.basicConfig(stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.ERROR)
    logging.getLogger("httpcore").setLevel(logging.ERROR)
    logging.getLogger("telegram.ext._updater").setLevel(logging.CRITICAL)

    # ══════════════════════════════════════════════
    #  ۵. تنظیمات GPU و ثابت‌ها
    # ══════════════════════════════════════════════
    import torch
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    torch.backends.cudnn.benchmark = True
    if torch.cuda.is_available():
        torch.cuda.set_per_process_memory_fraction(0.95, device=0)

    dtype = torch.float32
    BATCH_SIZE = 96
    max_inference_batch_size = 128
    max_new_tokens = 512
    CHUNK_DURATION = 60
    FFMPEG_THREADS = os.cpu_count() or 4
    CLEANUP_INTERVAL = 3
    WORK_DIR = "/content/workspace_tg"
    LOCAL_PORT = 8081

    for _d in ["input", "output", "temp", "temp_chunks", "tg_data", "fonts"]:
        os.makedirs(f"{WORK_DIR}/{_d}", exist_ok=True)

    FONT_DIR = f"{WORK_DIR}/fonts"
    FONT_FILE = f"{FONT_DIR}/Vazirmatn-Bold.ttf"
    if not os.path.exists(FONT_FILE) or os.path.getsize(FONT_FILE) < 10000:
        print("📦 دانلود فونت فارسی Vazirmatn...")
        try:
            urllib.request.urlretrieve(
                "https://raw.githubusercontent.com/rastikerdar/vazirmatn/master/fonts/ttf/Vazirmatn-Bold.ttf",
                FONT_FILE
            )
            print("✅ فونت فارسی Vazirmatn آماده شد")
        except Exception as _fe:
            print(f"⚠️ خطا در دانلود فونت Vazirmatn: {_fe}")

    device = "cuda:0" if torch.cuda.is_available() else "cpu"

    # ══════════════════════════════════════════════
    #  ۶. توقف ربات و سرور قبلی + پاکسازی VRAM
    # ══════════════════════════════════════════════
    _bot_state = getattr(sys, "_qwen_bot_state", None)
    if _bot_state:
        _prev_evt = _bot_state.get("stop_event")
        _prev_th = _bot_state.get("bot_thread")
        if _prev_evt:
            _prev_evt.set()
        if _prev_th and hasattr(_prev_th, "is_alive") and _prev_th.is_alive():
            _prev_th.join(timeout=6)
        _bot_state["stop_event"] = None
        _bot_state["bot_thread"] = None
        _bot_state["app"] = None

    subprocess.run(["pkill", "-9", "-f", "telegram-bot-api"], capture_output=True, timeout=5)
    time.sleep(1.5)
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


    # ══════════════════════════════════════════════
    #  ۷. بارگذاری مدل‌ها (ASR + VAD + ForcedAligner)
    # ══════════════════════════════════════════════
    print("\033[1;36m🚀 بارگذاری مدل‌ها...\033[0m")

    # ۷-A. Qwen3-ASR
    from qwen_asr.core.transformers_backend import (
        Qwen3ASRConfig,
        Qwen3ASRForConditionalGeneration,
        Qwen3ASRProcessor,
    )
    from transformers import AutoConfig, AutoModel, AutoProcessor
    AutoConfig.register("qwen3_asr", Qwen3ASRConfig, exist_ok=True)
    AutoModel.register(Qwen3ASRConfig, Qwen3ASRForConditionalGeneration, exist_ok=True)
    AutoProcessor.register(Qwen3ASRConfig, Qwen3ASRProcessor, exist_ok=True)
    from qwen_asr import Qwen3ASRModel
    print("  📥 Qwen3-ASR-1.7B...")
    model = Qwen3ASRModel.from_pretrained(
        "Qwen/Qwen3-ASR-1.7B",
        dtype=dtype,
        device_map=device,
        max_inference_batch_size=max_inference_batch_size,
        max_new_tokens=max_new_tokens,
    )
    print(f"  ✅ ASR روی {device}")

    # ۷-B. FireRedVAD
    print("  📥 FireRedVAD...")
    _vad_dir = f"{WORK_DIR}/pretrained_models/FireRedVAD"
    if not os.path.exists(_vad_dir):
        from huggingface_hub import snapshot_download
        snapshot_download("FireRedTeam/FireRedVAD", local_dir=_vad_dir)

    from fireredvad import FireRedVad as _FRV, FireRedVadConfig as _FRVCfg
    _vad_model = _FRV.from_pretrained(
        f"{_vad_dir}/VAD",
        _FRVCfg(
            use_gpu=torch.cuda.is_available(),
            smooth_window_size=5,
            speech_threshold=0.4,
            min_speech_frame=20,
            max_speech_frame=2000,
            min_silence_frame=20,
            extend_speech_frame=4,
            chunk_max_frame=30000,
        ),
    )
    print("  ✅ VAD آماده")

    # ۷-C. Qwen3-ForcedAligner
    print("  📥 Qwen3-ForcedAligner-0.6B...")
    _attn_impl = "sdpa"
    try:
        import flash_attn  # noqa
        import importlib.metadata as _meta
        _fa_ver = _meta.version("flash_attn")
        _attn_impl = "flash_attention_2"
        print(f"  ✅ flash-attn {_fa_ver} موجود")
    except Exception:
        print("  ℹ️ flash-attn نصب نیست — از sdpa استفاده می‌شود (کاملاً انجام‌شدنی)")
        _attn_impl = "sdpa"

    from qwen_asr import Qwen3ForcedAligner as _Qwen3FA
    _fa_model = _Qwen3FA.from_pretrained(
        "Qwen/Qwen3-ForcedAligner-0.6B",
        dtype=torch.bfloat16,
        device_map=device,
        attn_implementation=_attn_impl,
    )
    print(f"  ✅ ForcedAligner ({_attn_impl})")

    if torch.cuda.is_available():
        _vu = torch.cuda.memory_allocated() / (1024**3)
        _vt = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"\033[1;32m💾 VRAM: {_vu:.1f} / {_vt:.1f} GB\033[0m")

    # ۷-D. مدل ترجمه (lazy load — فقط متغیر تعریف می‌شود)
    _translation_model = None
    _translation_tokenizer = None
    SYSTEM_PROMPT_FA = """تو یک مترجم حرفه‌ای زیرنویس هستی. متن زیرنویس را به فارسی روان، طبیعی و محاوره‌ای ترجمه کن.
    قوانین:
    - فقط ترجمه را برگردان، هیچ توضیح اضافه‌ای ننویس
    - ترتیب جملات و ساختار را حفظ کن
    - هر خط ترجمه را با شماره [1], [2], ... شروع کن
    - اصطلاحات، نام‌ها و اعداد را دقیق نگه دار
    - اگر متن کوتاه است، کوتاه ترجمه کن
    - خروجی فقط متن ترجمه‌شده با شماره خطوط باشد"""

    import pysrt
    import re
    from concurrent.futures import ThreadPoolExecutor, as_completed

    # ══════════════════════════════════════════════
    #  ۸. استارت سرور محلی تلگرام
    # ══════════════════════════════════════════════
    print("\033[1;36m⚙️ استارت سرور محلی...\033[0m")
    tg_cmd = [
        "./telegram-bot-api",
        f"--api-id={os.environ['API_ID']}",
        f"--api-hash={os.environ['API_HASH']}",
        "--local",
        f"--http-port={LOCAL_PORT}",
        f"--dir={WORK_DIR}/tg_data"
    ]
    tg_proc = subprocess.Popen(tg_cmd)
    time.sleep(2)
    if tg_proc.poll() is not None:
        tg_proc = subprocess.Popen(tg_cmd)
        time.sleep(3)

    def _wait_server(port, retries=30):
        for i in range(retries):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(2)
                    s.connect(("127.0.0.1", port))
                return True
            except:
                if i == 0:
                    print("⏳ انتظار سرور...")
                time.sleep(1)
        return False

    if not _wait_server(LOCAL_PORT):
        mo.stop(True, mo.md("❌ سرور محلی آماده نشد!"))
    print("✅ سرور محلی آماده")

    # ══════════════════════════════════════════════
    #  ۹. توابع پایپ‌این تقویت‌شده
    # ══════════════════════════════════════════════
    def seconds_to_srt_time(s):
        h, rem = divmod(int(s), 3600)
        m, sec = divmod(rem, 60)
        ms = int((s % 1) * 1000)
        return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"

    def _group_words_for_srt(words, offset=0.0, max_words=7, max_dur=4.0, min_dur=1.0):
        entries, cur_w, cur_s, cur_e = [], [], None, None
        for w in words:
            wt = w.text.strip() if hasattr(w, "text") else str(w).strip()
            ws = (w.start_time if hasattr(w, "start_time") else 0.0) + offset
            we = (w.end_time if hasattr(w, "end_time") else ws + 0.5) + offset
            if not wt:
                continue
            if cur_s is None:
                cur_s = ws
            cur_w.append(wt)
            cur_e = we
            d = cur_e - cur_s
            if len(cur_w) >= max_words or d >= max_dur or wt.endswith((".", "!", "؟", "?", "。", "！", "？")):
                if d < min_dur:
                    cur_e = cur_s + min_dur
                entries.append((cur_s, cur_e, " ".join(cur_w)))
                cur_w, cur_s, cur_e = [], None, None
        if cur_w and cur_s is not None:
            entries.append((cur_s, cur_e, " ".join(cur_w)))
        return entries

    def process_audio_enhanced(input_path, filename_base, update_callback=None):
        wav_path = f"{WORK_DIR}/temp/{filename_base}_enh.wav"
        logging.info(f"🎬 شروع: {input_path}")
        if update_callback:
            update_callback("🔍 استخراج صوت و حذف سکوت (VAD)...", 10, "در حال استخراج...")
        _ff = subprocess.run([
            "ffmpeg", "-i", input_path, "-ac", "1", "-ar", "16000", "-vn",
            "-threads", str(FFMPEG_THREADS), wav_path, "-y"
        ], capture_output=True, text=True, timeout=600)
        if _ff.returncode != 0:
            raise RuntimeError(f"FFmpeg: {_ff.stderr[-200:]}")

        _dp = subprocess.run([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", wav_path
        ], capture_output=True, text=True, timeout=30)
        try:
            total_duration = float(_dp.stdout.strip())
        except:
            total_duration = 0.0
        logging.info(f"⏱️ مدت: {total_duration:.1f}s")

        logging.info("🔍 FireRedVAD...")
        _vad_res, _ = _vad_model.detect(wav_path)
        _segments = _vad_res.get("timestamps", [])
        _speech = sum(e - s for s, e in _segments) if _segments else 0
        logging.info(f"📢 {len(_segments)} بخش گفتار | {_speech:.1f}s")

        if update_callback:
            update_callback("✂️ قطعه‌بندی گفتار و آماده‌سازی...", 20, "در حال تفکیک...")

        num_chunks = max(1, math.ceil(total_duration / CHUNK_DURATION))
        chunk_files = []
        for i in range(num_chunks):
            start = i * CHUNK_DURATION
            end = start + CHUNK_DURATION
            if not any(ss < end and se > start for ss, se in _segments):
                logging.info(f"🔇 تکه {i+1} سکوت — رد شد")
                continue
            cp = f"{WORK_DIR}/temp_chunks/{filename_base}_e_{i:04d}.wav"
            subprocess.run([
                "ffmpeg", "-i", wav_path, "-ss", str(start), "-t", str(CHUNK_DURATION),
                "-threads", str(FFMPEG_THREADS), cp, "-y"
            ], capture_output=True, timeout=120)
            if os.path.exists(cp):
                chunk_files.append((i, start, cp))
        logging.info(f"📦 {len(chunk_files)} تکه دارای گفتار (از {num_chunks})")

        _asr_results = []
        total_batches = math.ceil(len(chunk_files) / BATCH_SIZE)
        batch_times = []
        _total_inf = 0.0

        for bi in range(total_batches):
            batch = chunk_files[bi * BATCH_SIZE : (bi + 1) * BATCH_SIZE]
            bp = [c[2] for c in batch]
            bi_list = [c[0] for c in batch]
            bs_list = [c[1] for c in batch]

            avg_bt = sum(batch_times) / len(batch_times) if batch_times else 0.0
            est_rem = (total_batches - bi) * avg_bt if batch_times else 0.0
            t_lbl = f"~{est_rem:.0f} ثانیه" if est_rem > 0 else "در حال محاسبه..."
            pct = 20 + int((bi / max(total_batches, 1)) * 40)
            if update_callback:
                update_callback(f"🎙️ رونویسی صوت (بخش {bi+1} از {total_batches})", pct, t_lbl)

            logging.info(f"🧠 ASR Batch {bi+1}/{total_batches}")
            try:
                _t0 = time.time()
                results = model.transcribe(audio=bp, language=None)
                _dt = time.time() - _t0
                _total_inf += _dt
                batch_times.append(_dt)
                if not isinstance(results, list):
                    results = [results]
                for j, res in enumerate(results):
                    text = res.text.strip() if hasattr(res, "text") else str(res).strip()
                    lang = getattr(res, "language", None) if hasattr(res, "language") else None
                    if text:
                        _asr_results.append((bi_list[j], bs_list[j], bp[j], text, lang))
                        logging.info(f"📝 تکه {bi_list[j]+1}: {text[:80]}...")
            except Exception as e:
                logging.error(f"❌ Batch {bi+1}: {e}")
                for j, cp in enumerate(bp):
                    try:
                        _t0 = time.time()
                        r = model.transcribe(audio=cp, language=None)
                        _total_inf += time.time() - _t0
                        t = r[0].text.strip() if r and hasattr(r[0], "text") else str(r).strip()
                        if t:
                            _asr_results.append((bi_list[j], bs_list[j], cp, t, None))
                    except Exception as e2:
                        logging.error(f"❌ تکه {bi_list[j]+1}: {e2}")

            if (bi + 1) % CLEANUP_INTERVAL == 0 and torch.cuda.is_available():
                torch.cuda.empty_cache()

        logging.info(f"🎯 ForcedAligner روی {len(_asr_results)} بخش...")
        _all_entries = []
        total_align = len(_asr_results)
        align_start = time.time()

        for _idx_align, (_ci, _cs, _cp, _txt, _lang) in enumerate(_asr_results):
            if update_callback and total_align > 0:
                elapsed_a = time.time() - align_start
                avg_a = elapsed_a / max(_idx_align, 1)
                rem_a = (total_align - _idx_align) * avg_a
                t_lbl_a = f"~{rem_a:.0f} ثانیه" if _idx_align > 0 and rem_a > 0 else "در حال محاسبه..."
                pct_a = 60 + int((_idx_align / total_align) * 35)
                update_callback(f"🎯 تایمینگ کلمات (جمله {_idx_align+1} از {total_align})", pct_a, t_lbl_a)

            try:
                _t0_fa = time.time()
                _ar = _fa_model.align(audio=_cp, text=_txt, language=_lang)
                _total_inf += (time.time() - _t0_fa)
                if _ar and len(_ar) > 0:
                    _grouped = _group_words_for_srt(_ar[0], offset=_cs)
                    if _grouped:
                        _all_entries.extend(_grouped)
                        logging.info(f"✅ Alignment تکه {_ci+1}: {len(_grouped)} خط")
                    else:
                        _end = min(_cs + CHUNK_DURATION, total_duration)
                        _all_entries.append((_cs, _end, _txt))
                else:
                    _end = min(_cs + CHUNK_DURATION, total_duration)
                    _all_entries.append((_cs, _end, _txt))
            except Exception as _ae:
                logging.warning(f"⚠️ Alignment خطا تکه {_ci+1}: fallback")
                _end = min(_cs + CHUNK_DURATION, total_duration)
                _all_entries.append((_cs, _end, _txt))
            finally:
                if os.path.exists(_cp):
                    os.remove(_cp)
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

        if update_callback:
            update_callback("📝 ذخیره و تولید فایل زیرنویس...", 98, "چند لحظه...")

        _all_entries.sort(key=lambda x: x[0])
        srt_entries = []
        for idx, (_s, _e, _t) in enumerate(_all_entries, 1):
            _clean_t = re.sub(r'[​‎﻿­�]', '', _t).strip()
            if _clean_t:
                srt_entries.append(f"{idx}\n{seconds_to_srt_time(_s)} --> {seconds_to_srt_time(_e)}\n{_clean_t}\n")

        srt_path = f"{WORK_DIR}/output/{filename_base}.srt"
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(srt_entries))

        logging.info(f"🎉 SRT: {srt_path} ({len(srt_entries)} خط)")
        logging.info(f"📊 inference: {_total_inf:.2f}s")

        if os.path.exists(wav_path):
            os.remove(wav_path)
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        return srt_path, _total_inf, total_duration

    WORKER_SCRIPT = f"{WORK_DIR}/translate_worker.py"
    _worker_b64 = "IyB0cmFuc2xhdGVfd29ya2VyLnB5CmltcG9ydCBzeXMsIG9zLCByZSwganNvbiwgdGltZQppbXBvcnQgdG9yY2gKaW1wb3J0IHB5c3J0CmZyb20gdHJhbnNmb3JtZXJzIGltcG9ydCBBdXRvTW9kZWxGb3JJbWFnZVRleHRUb1RleHQsIEF1dG9Ub2tlbml6ZXIsIEJpdHNBbmRCeXRlc0NvbmZpZwoKU1lTVEVNX1BST01QVF9GQSA9ICIiItiq2Ygg24zaqSDZhdiq2LHYrNmFINit2LHZgdmH4oCM2KfbjCDYstuM2LHZhtmI24zYsyDZh9iz2KrbjC4g2YXYqtmGINiy24zYsdmG2YjbjNizINix2Kcg2KjZhyDZgdin2LHYs9uMINix2YjYp9mG2Iwg2LfYqNuM2LnbjCDZiCDZhdit2KfZiNix2YfigIzYp9uMINiq2LHYrNmF2Ycg2qnZhi4K2YLZiNin2YbbjNmGOgotINmB2YLYtyDYqtix2KzZhdmHINix2Kcg2KjYsdqv2LHYr9in2YbYjCDZh9uM2oYg2KrZiNi224zYrSDYp9i22KfZgdmH4oCM2KfbjCDZhtmG2YjbjNizCi0g2KrYsdiq24zYqCDYrNmF2YTYp9iqINmIINiz2KfYrtiq2KfYsSDYsdinINit2YHYuCDaqdmGCi0g2YfYsSDYrti3INiq2LHYrNmF2Ycg2LHYpyDYqNinINi02YXYp9ix2YcgWzFdLCBbMl0sIC4uLiDYtNix2YjYuSDaqdmGCi0g2KfYtdi32YTYp9it2KfYqtiMINmG2KfZheKAjNmH2Kcg2Ygg2KfYudiv2KfYryDYsdinINiv2YLbjNmCINmG2q/ZhyDYr9in2LEKLSDYp9qv2LEg2YXYqtmGINqp2YjYqtin2Ycg2KfYs9iq2Iwg2qnZiNiq2KfZhyDYqtix2KzZhdmHINqp2YYKLSDYrtix2YjYrNuMINmB2YLYtyDZhdiq2YYg2KrYsdis2YXZh+KAjNi02K/ZhyDYqNinINi02YXYp9ix2Ycg2K7Yt9mI2Lcg2KjYp9i02K8iIiIKCmRlZiBtYWluKCk6CiAgICBpZiBsZW4oc3lzLmFyZ3YpIDwgMjoKICAgICAgICBzeXMuZXhpdCgxKQogICAgICAgIAogICAgc3J0X3BhdGggPSBzeXMuYXJndlsxXQogICAgYmF0Y2hfc2l6ZSA9IGludChzeXMuYXJndlsyXSkgaWYgbGVuKHN5cy5hcmd2KSA+IDIgZWxzZSAzMgogICAgcGFyYWxsZWxfc2l6ZSA9IGludChzeXMuYXJndlszXSkgaWYgbGVuKHN5cy5hcmd2KSA+IDMgZWxzZSA4CiAgICBvdXRwdXRfcGF0aCA9IHNydF9wYXRoLnJlcGxhY2UoIi5zcnQiLCAiX2ZhLnNydCIpCiAgICAKICAgIHByaW50KCJTVEFUVVM6bG9hZGluZ19tb2RlbCIsIGZsdXNoPVRydWUpCiAgICBtb2RlbF9pZCA9ICJRd2VuL1F3ZW4zLjYtMzVCLUEzQiIKICAgIGJuYl9jb25maWcgPSBCaXRzQW5kQnl0ZXNDb25maWcoCiAgICAgICAgbG9hZF9pbl80Yml0PVRydWUsCiAgICAgICAgYm5iXzRiaXRfcXVhbnRfdHlwZT0ibmY0IiwKICAgICAgICBibmJfNGJpdF91c2VfZG91YmxlX3F1YW50PVRydWUsCiAgICAgICAgYm5iXzRiaXRfY29tcHV0ZV9kdHlwZT10b3JjaC5iZmxvYXQxNiwKICAgICkKICAgIHRvayA9IEF1dG9Ub2tlbml6ZXIuZnJvbV9wcmV0cmFpbmVkKG1vZGVsX2lkLCB0cnVzdF9yZW1vdGVfY29kZT1UcnVlKQogICAgdG9rLnBhZGRpbmdfc2lkZSA9ICJsZWZ0IgogICAgaWYgdG9rLnBhZF90b2tlbiBpcyBOb25lOgogICAgICAgIHRvay5wYWRfdG9rZW4gPSB0b2suZW9zX3Rva2VuCgogICAgbW9kZWwgPSBBdXRvTW9kZWxGb3JJbWFnZVRleHRUb1RleHQuZnJvbV9wcmV0cmFpbmVkKAogICAgICAgIG1vZGVsX2lkLAogICAgICAgIHF1YW50aXphdGlvbl9jb25maWc9Ym5iX2NvbmZpZywKICAgICAgICBkZXZpY2VfbWFwPSJjdWRhOjAiLAogICAgICAgIHRydXN0X3JlbW90ZV9jb2RlPVRydWUsCiAgICAgICAgdG9yY2hfZHR5cGU9dG9yY2guYmZsb2F0MTYsCiAgICApCiAgICBtb2RlbC5ldmFsKCkKICAgIAogICAgcHJpbnQoIlNUQVRVUzp0cmFuc2xhdGluZyIsIGZsdXNoPVRydWUpCiAgICBzdWJzID0gcHlzcnQub3BlbihzcnRfcGF0aCwgZW5jb2Rpbmc9InV0Zi04IikKICAgIGNodW5rcywgY3VyID0gW10sIFtdCiAgICBmb3IgaSwgc3ViIGluIGVudW1lcmF0ZShzdWJzKToKICAgICAgICBjdXIuYXBwZW5kKHsiaW5kZXgiOiBpLCAic3RhcnQiOiBzdWIuc3RhcnQsICJlbmQiOiBzdWIuZW5kLCAidGV4dCI6IHN1Yi50ZXh0LnN0cmlwKCl9KQogICAgICAgIGlmIGxlbihjdXIpID49IGJhdGNoX3NpemU6CiAgICAgICAgICAgIGNodW5rcy5hcHBlbmQoY3VyKQogICAgICAgICAgICBjdXIgPSBbXQogICAgaWYgY3VyOgogICAgICAgIGNodW5rcy5hcHBlbmQoY3VyKQoKICAgIHRvdGFsX2NodW5rcyA9IGxlbihjaHVua3MpCiAgICB0cmFuc2xhdGVkX2NodW5rcyA9IFtdCiAgICB0b3RhbF90b2tlbnMgPSAwCiAgICAKICAgIGZvciBwX2lkeCBpbiByYW5nZSgwLCB0b3RhbF9jaHVua3MsIHBhcmFsbGVsX3NpemUpOgogICAgICAgIGJhdGNoX2NodW5rcyA9IGNodW5rc1twX2lkeDpwX2lkeCArIHBhcmFsbGVsX3NpemVdCiAgICAgICAgcHJvbXB0cyA9IFtdCiAgICAgICAgZm9yIGNodW5rIGluIGJhdGNoX2NodW5rczoKICAgICAgICAgICAgdGV4dHNfd2l0aF9udW1iZXJzID0gW2YiW3tpdGVtWydpbmRleCddKzF9XSB7aXRlbVsndGV4dCddfSIgZm9yIGl0ZW0gaW4gY2h1bmtdCiAgICAgICAgICAgIGZ1bGxfdGV4dCA9ICJcbiIuam9pbih0ZXh0c193aXRoX251bWJlcnMpCiAgICAgICAgICAgIG1lc3NhZ2VzID0gWwogICAgICAgICAgICAgICAgeyJyb2xlIjogInN5c3RlbSIsICJjb250ZW50IjogU1lTVEVNX1BST01QVF9GQX0sCiAgICAgICAgICAgICAgICB7InJvbGUiOiAidXNlciIsICJjb250ZW50IjogZiLYp9uM2YYg2YXYqtmGINiy24zYsdmG2YjbjNizINix2Kcg2KjZhyDZgdin2LHYs9uMINiq2LHYrNmF2Ycg2qnZhjpcblxue2Z1bGxfdGV4dH0ifQogICAgICAgICAgICBdCiAgICAgICAgICAgIHAgPSB0b2suYXBwbHlfY2hhdF90ZW1wbGF0ZSgKICAgICAgICAgICAgICAgIG1lc3NhZ2VzLAogICAgICAgICAgICAgICAgdG9rZW5pemU9RmFsc2UsCiAgICAgICAgICAgICAgICBhZGRfZ2VuZXJhdGlvbl9wcm9tcHQ9VHJ1ZSwKICAgICAgICAgICAgICAgIGVuYWJsZV90aGlua2luZz1GYWxzZQogICAgICAgICAgICApCiAgICAgICAgICAgIHByb21wdHMuYXBwZW5kKHApCiAgICAgICAgICAgIAogICAgICAgIGlucHV0cyA9IHRvayhwcm9tcHRzLCBwYWRkaW5nPVRydWUsIHJldHVybl90ZW5zb3JzPSJwdCIpLnRvKG1vZGVsLmRldmljZSkKICAgICAgICBpbl9sZW4gPSBpbnB1dHNbImlucHV0X2lkcyJdLnNoYXBlWzFdCiAgICAgICAgCiAgICAgICAgYmF0Y2hfaW5fdG9rZW5zID0gaW5wdXRzWyJpbnB1dF9pZHMiXS5udW1lbCgpCiAgICAgICAgdG9yY2hfZHR5cGU9dG9yY2guYmZsb2F0MTYsCiAgICApCiAgICBtb2RlbC5ldmFsKCkKICAgIAogICAgcHJpbnQoIlNUQVRVUzp0cmFuc2xhdGluZyIsIGZsdXNoPVRydWUpCiAgICBzdWJzID0gcHlzcnQub3BlbihzcnRfcGF0aCwgZW5jb2Rpbmc9InV0Zi04IikKICAgIGNodW5rcywgY3VyID0gW10sIFtdCiAgICBmb3IgaSwgc3ViIGluIGVudW1lcmF0ZShzdWJzKToKICAgICAgICBjdXIuYXBwZW5kKHsiaW5kZXgiOiBpLCAic3RhcnQiOiBzdWIuc3RhcnQsICJlbmQiOiBzdWIuZW5kLCAidGV4dCI6IHN1Yi50ZXh0LnN0cmlwKCl9KQogICAgICAgIGlmIGxlbihjdXIpID49IGJhdGNoX3NpemU6CiAgICAgICAgICAgIGNodW5rcy5hcHBlbmQoY3VyKQogICAgICAgICAgICBjdXIgPSBbXQogICAgaWYgY3VyOgogICAgICAgIGNodW5rcy5hcHBlbmQoY3VyKQoKICAgIHRvdGFsX2NodW5rcyA9IGxlbihjaHVua3MpCiAgICB0cmFuc2xhdGVkX2NodW5rcyA9IFtdCiAgICB0b3RhbF90b2tlbnMgPSAwCiAgICAKICAgIGZvciBwX2lkeCBpbiByYW5nZSgwLCB0b3RhbF9jaHVua3MsIHBhcmFsbGVsX3NpemUpOgogICAgICAgIGJhdGNoX2NodW5rcyA9IGNodW5rc1twX2lkeDpwX2lkeCArIHBhcmFsbGVsX3NpemVdCiAgICAgICAgcHJvbXB0cyA9IFtdCiAgICAgICAgZm9yIGNodW5rIGluIGJhdGNoX2NodW5rczoKICAgICAgICAgICAgdGV4dHNfd2l0aF9udW1iZXJzID0gW2YiW3tpdGVtWydpbmRleCddKzF9XSB7aXRlbVsndGV4dCddfSIgZm9yIGl0ZW0gaW4gY2h1bmtdCiAgICAgICAgICAgIGZ1bGxfdGV4dCA9ICJcbiIuam9pbih0ZXh0c193aXRoX251bWJlcnMpCiAgICAgICAgICAgIG1lc3NhZ2VzID0gWwogICAgICAgICAgICAgICAgeyJyb2xlIjogInN5c3RlbSIsICJjb250ZW50IjogU1lTVEVNX1BST01QVF9GQX0sCiAgICAgICAgICAgICAgICB7InJvbGUiOiAidXNlciIsICJjb250ZW50IjogZiLYp9uM2YYg2YXYqtmGINiy24zYsdmG2YjbjNizINix2Kcg2KjZhyDZgdin2LHYs9uMINiq2LHYrNmF2Ycg2qnZhjpcblxue2Z1bGxfdGV4dH0ifQogICAgICAgICAgICBdCiAgICAgICAgICAgIHAgPSB0b2suYXBwbHlfY2hhdF90ZW1wbGF0ZSgKICAgICAgICAgICAgICAgIG1lc3NhZ2VzLAogICAgICAgICAgICAgICAgdG9rZW5pemU9RmFsc2UsCiAgICAgICAgICAgICAgICBhZGRfZ2VuZXJhdGlvbl9wcm9tcHQ9VHJ1ZSwKICAgICAgICAgICAgICAgIGVuYWJsZV90aGlua2luZz1GYWxzZQogICAgICAgICAgICApCiAgICAgICAgICAgIHByb21wdHMuYXBwZW5kKHApCiAgICAgICAgICAgIAogICAgICAgIGlucHV0cyA9IHRvayhwcm9tcHRzLCBwYWRkaW5nPVRydWUsIHJldHVybl90ZW5zb3JzPSJwdCIpLnRvKG1vZGVsLmRldmljZSkKICAgICAgICBpbl9sZW4gPSBpbnB1dHNbImlucHV0X2lkcyJdLnNoYXBlWzFdCiAgICAgICAgCiAgICAgICAgYmF0Y2hfaW5fdG9rZW5zID0gaW5wdXRzWyJpbnB1dF9pZHMiXS5udW1lbCgpCiAgICAgICAgdG90YWxfdG9rZW5zICs9IGJhdGNoX2luX3Rva2VucwogICAgICAgIAogICAgICAgIHdpdGggdG9yY2gubm9fZ3JhZCgpOgogICAgICAgICAgICBvdXRwdXRzID0gbW9kZWwuZ2VuZXJhdGUoCiAgICAgICAgICAgICAgICAqKmlucHV0cywKICAgICAgICAgICAgICAgIG1heF9uZXdfdG9rZW5zPTIwNDgsCiAgICAgICAgICAgICAgICB0ZW1wZXJhdHVyZT0wLjMsCiAgICAgICAgICAgICAgICB0b3BfcD0wLjksCiAgICAgICAgICAgICAgICBkb19zYW1wbGU9VHJ1ZSwKICAgICAgICAgICAgICAgIHBhZF90b2tlbl9pZD10b2sucGFkX3Rva2VuX2lkLAogICAgICAgICAgICApCiAgICAgICAgICAgIAogICAgICAgIGZvciBpIGluIHJhbmdlKGxlbihwcm9tcHRzKSk6CiAgICAgICAgICAgIG91dF90b2tzID0gKG91dHB1dHNbaV1baW5fbGVuOl0gIT0gdG9rLnBhZF90b2tlbl9pZCkuc3VtKCkuaXRlbSgpCiAgICAgICAgICAgIHRvdGFsX3Rva2VucyArPSBvdXRfdG9rcwogICAgICAgICAgICAKICAgICAgICAgICAgcmVzcCA9IHRvay5kZWNvZGUob3V0cHV0c1tpXVtpbl9sZW46XSwgc2tpcF9zcGVjaWFsX3Rva2Vucz1UcnVlKQogICAgICAgICAgICByZXNwID0gcmUuc3ViKHIiPHRoaW5rPi4qPzwvdGhpbms+IiwgIiIsIHJlc3AsIGZsYWdzPXJlLkRPVEFMTCkuc3RyaXAoKQogICAgICAgICAgICB0cmFuc2xhdGVkX2NodW5rcy5hcHBlbmQocmVzcCkKICAgICAgICAgICAgCiAgICAgICAgZG9uZV9jaHVua3MgPSBtaW4ocF9pZHggKyBwYXJhbGxlbF9zaXplLCB0b3RhbF9jaHVua3MpCiAgICAgICAgdnJhbV91c2VkID0gdG9yY2guY3VkYS5tZW1vcnlfYWxsb2NhdGVkKCkgLyAoMTAyNCoqMykKICAgICAgICB2cmFtX3RvdGFsID0gdG9yY2guY3VkYS5nZXRfZGV2aWNlX3Byb3BlcnRpZXMoMCkudG90YWxfbWVtb3J5IC8gKDEwMjQqKjMpCiAgICAgICAgcHJpbnQoZiJQUk9HUkVTUzp7ZG9uZV9jaHVua3N9L3t0b3RhbF9jaHVua3N9Ont2cmFtX3VzZWQ6LjFmfS97dnJhbV90b3RhbDouMWZ9Ont0b3RhbF90b2tlbnN9IiwgZmx1c2g9VHJ1ZSkKCiAgICBhbGxfdHJhbnNsYXRlZF9saW5lcyA9IFtdCiAgICBmb3IgdHJhbnNsYXRlZCBpbiB0cmFuc2xhdGVkX2NodW5rczoKICAgICAgICBsaW5lcyA9IFtsaW5lLnN0cmlwKCkgZm9yIGxpbmUgaW4gdHJhbnNsYXRlZC5zcGxpdCgiXG4iKSBpZiBsaW5lLnN0cmlwKCldCiAgICAgICAgY2xlYW5fbGluZXMgPSBbcmUuc3ViKHInW+KAi+KAju+7v8Kt77+9XScsICcnLCBsaW5lKS5zdHJpcCgpIGZvciBsaW5lIGluIGxpbmVzXQogICAgICAgIGNsZWFuX2xpbmVzID0gW3JlLnN1YihyIl5cW1xkK1xdXHMqIiwgIiIsIGxpbmUpIGZvciBsaW5lIGluIGNsZWFuX2xpbmVzXQogICAgICAgIGNsZWFuX2xpbmVzID0gW2Yi4oCPe2xpbmV9IiBpZiBub3QgbGluZS5zdGFydHN3aXRoKCLigI8iKSBlbHNlIGxpbmUgZm9yIGxpbmUgaW4gY2xlYW5fbGluZXNdCiAgICAgICAgYWxsX3RyYW5zbGF0ZWRfbGluZXMuZXh0ZW5kKGNsZWFuX2xpbmVzKQoKICAgIGlmIGxlbihhbGxfdHJhbnNsYXRlZF9saW5lcykgIT0gbGVuKHN1YnMpOgogICAgICAgIGFsbF90cmFuc2xhdGVkX2xpbmVzID0gYWxsX3RyYW5zbGF0ZWRfbGluZXNbOmxlbihzdWJzKV0KICAgICAgICB3aGlsZSBsZW4oYWxsX3RyYW5zbGF0ZWRfbGluZXMpIDwgbGVuKHN1YnMpOgogICAgICAgICAgICBhbGxfdHJhbnNsYXRlZF9saW5lcy5hcHBlbmQoc3Vic1tsZW4oYWxsX3RyYW5zbGF0ZWRfbGluZXMpXS50ZXh0KQoKICAgIG5ld19zdWJzID0gcHlzcnQuU3ViUmlwRmlsZSgpCiAgICBmb3IgaSwgc3ViIGluIGVudW1lcmF0ZShzdWJzKToKICAgICAgICBuZXdfc3ViID0gcHlzcnQuU3ViUmlwSXRlbSgKICAgICAgICAgICAgaW5kZXg9aSArIDEsCiAgICAgICAgICAgIHN0YXJ0PXN1Yi5zdGFydCwKICAgICAgICAgICAgZW5kPXN1Yi5lbmQsCiAgICAgICAgICAgIHRleHQ9YWxsX3RyYW5zbGF0ZWRfbGluZXNbaV0KICAgICAgICApCiAgICAgICAgbmV3X3N1YnMuYXBwZW5kKG5ld19zdWIpCgogICAgbmV3X3N1YnMuc2F2ZShvdXRwdXRfcGF0aCwgZW5jb2Rpbmc9InV0Zi04IikKICAgIHByaW50KGYiRE9ORTp7b3V0cHV0X3BhdGh9OntsZW4oc3Vicyl9Ont0b3RhbF90b2tlbnN9IiwgZmx1c2g9VHJ1ZSkKCmlmIF9fbmFtZV9fID09ICJfX21haW5fXyI6CiAgICBtYWluKCkK"
    import base64
    with open(WORKER_SCRIPT, "wb") as _f_worker:
        _f_worker.write(base64.b64decode(_worker_b64))

    # ══════════════════════════════════════════════
    #  ۱۰. Handler های ربات
    # ══════════════════════════════════════════════
    from telegram import (
        Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, MenuButtonCommands
    )
    from telegram.ext import (
        ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters,
        CallbackQueryHandler,
    )

    _last_cache_check = [0.0, "74 GB"]

    def get_system_status_text():
        now = time.time()
        now_str = time.strftime("%H:%M:%S")
        vram_str = "غیرفعال"
        gpu_info = "نامشخص"
        gpu_util = "0%"
        gpu_temp = "نامشخص"
        gpu_pwr = "نامشخص"
        if torch.cuda.is_available():
            try:
                smi = subprocess.run([
                    "nvidia-smi",
                    "--query-gpu=name,memory.used,memory.total,utilization.gpu,temperature.gpu,power.draw",
                    "--format=csv,noheader,nounits"
                ], capture_output=True, text=True, timeout=2)
                if smi.returncode == 0 and smi.stdout.strip():
                    parts = [p.strip() for p in smi.stdout.strip().split(",")]
                    if len(parts) >= 6:
                        gpu_info = parts[0]
                        v_used = float(parts[1]) / 1024.0
                        v_total = float(parts[2]) / 1024.0
                        gpu_util = f"{parts[3]}%"
                        gpu_temp = f"{parts[4]}°C"
                        gpu_pwr = f"{float(parts[5]):.0f}W"
                        vram_str = f"<b>{v_used:.1f} / {v_total:.1f} GB</b>"
            except:
                pass
            if vram_str == "غیرفعال":
                alloc_gb = torch.cuda.memory_allocated() / (1024**3)
                tot_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                vram_str = f"<b>{alloc_gb:.1f} / {tot_gb:.1f} GB</b>"

        du = shutil.disk_usage(WORK_DIR)
        disk_used_gb = du.used / (1024**3)
        disk_total_gb = du.total / (1024**3)
        if disk_total_gb > 2000:
            disk_str = f"• فضای اشغال‌شده سیستم: <b>{disk_used_gb:.1f} GB</b> (فضای ابری ساندباکس)"
        else:
            disk_free_gb = du.free / (1024**3)
            disk_str = f"• فضای اشغال‌شده: <b>{disk_used_gb:.1f} GB</b> (آزاد: <b>{disk_free_gb:.1f} GB</b> از {disk_total_gb:.1f} GB)"

        active_th = len(threading.enumerate())

        if now - _last_cache_check[0] > 60.0:
            _last_cache_check[0] = now
            hub_cache = "/home/marimo/.cache/huggingface/hub"
            if os.path.exists(hub_cache):
                try:
                    cs = subprocess.run(["du", "-sh", hub_cache], capture_output=True, text=True, timeout=2)
                    if cs.returncode == 0 and cs.stdout.strip():
                        _last_cache_check[1] = cs.stdout.strip().split()[0]
                except:
                    pass
        cache_sz = _last_cache_check[1]

        text = (
            f"📊 <b>وضعیت زنده سرور و هوش مصنوعی</b>\n"
            f"🕒 آخرین به‌روزرسانی: <code>{now_str}</code>\n\n"
            f"🎮 <b>کارت گرافیک (GPU):</b>\n"
            f"• مدل: <b>{gpu_info}</b>\n"
            f"• لود پردازشگر: <b>{gpu_util}</b> | دما: <b>{gpu_temp}</b> | توان مصرفی: <b>{gpu_pwr}</b>\n"
            f"• کل حافظه VRAM اشغال‌شده: {vram_str}\n\n"
            f"🧠 <b>مدل‌های هوش مصنوعی فعال:</b>\n"
            f"• صوت: <b>Qwen3-ASR (1.7B)</b>\n"
            f"• تشخیص گفتار: <b>FireRedVAD</b>\n"
            f"• تراز کلمات: <b>Qwen3-ForcedAligner (0.6B)</b>\n"
            f"• ترجمه: <b>Qwen3.6-35B-A3B (MoE 4-bit)</b>\n\n"
            f"💾 <b>دیسک و حافظه محلی:</b>\n"
            f"{disk_str}\n"
            f"• حجم کش مدل‌ها: <b>{cache_sz}</b>\n"
            f"• رشته‌های فعال: <b>{active_th} رشته</b>"
        )
        return text
    async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔄 رفرش وضعیت", callback_data="refresh_status")]])
        await update.message.reply_text(get_system_status_text(), parse_mode="HTML", reply_markup=kb)

    async def status_refresh_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer("✅ وضعیت به‌روزرسانی شد")
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔄 رفرش وضعیت", callback_data="refresh_status")]])
        try:
            await query.edit_message_text(get_system_status_text(), parse_mode="HTML", reply_markup=kb)
        except:
            pass

    async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = (
            "ℹ️ <b>راهنمای جامع ربات زیرنویس و ترجمه هوشمند</b>\n\n"
            "🎬 <b>مراحل کار:</b>\n"
            "۱. یک ویدیو، صوت یا داکیومنت ویدیویی (دانلود تا سقف ۴ گیگابایت و آپلود تا ۲ گیگابایت) ارسال کنید.\n"
            "۲. ربات با استفاده از هوش مصنوعی سه‌مرحله‌ای (VAD + ASR + ForcedAligner) زیرنویس با هماهنگی دقیق کلمه به کلمه تولید می‌کند.\n"
            "۳. پس از دریافت زیرنویس، با کلیک روی <b>«🌐 ترجمه به فارسی»</b>، مدل قدرتمند Qwen3.6-35B زیرنویس را با دقت بالا ترجمه می‌کند.\n"
            "۴. با زدن دکمه <b>«🎬 هاردساب»</b>، زیرنویس مستقیماً روی ویدیو رندر و فایل نهایی برایتان ارسال می‌شود.\n\n"
            "🎞️ <b>کدک‌های تصویر در هاردساب:</b>\n"
            "• <b>H.264 / AVC</b> (بسیار سریع و استاندارد)\n"
            "• <b>HEVC / H.265</b> (فوق فشرده با کیفیت بالا)\n"
            "• <b>VP9</b> (فرمت وب و یوتیوب)\n"
            "• <b>AV1</b> (جدیدترین الگوریتم فشرده‌سازی)\n"
            "<i>(کدک خروجی هاردساب دقیقاً مطابق کدک ویدیوی ارسالی شما تنظیم می‌شود.)</i>\n\n"
            "📌 <b>دستورات دکمه Menu:</b>\n"
            "/start - شروع دوباره ربات\n"
            "/status - مشاهده زنده مصرف گرافیک، دما، رم و دیسک (دارای دکمه رفرش)\n"
            "/clean - پاکسازی کش و فایل‌های موقت برای آزاد شدن دیسک\n"
            "/help - راهنمای امکانات\n"
            "/kill - توقف ربات"
        )
        await update.message.reply_text(help_text, parse_mode="HTML")

    async def clean_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        del_count = 0
        freed_bytes = 0
        for folder in [f"{WORK_DIR}/temp", f"{WORK_DIR}/temp_chunks", f"{WORK_DIR}/input"]:
            if os.path.exists(folder):
                for fname in os.listdir(folder):
                    fp = os.path.join(folder, fname)
                    try:
                        sz = os.path.getsize(fp)
                        if os.path.isfile(fp) or os.path.islink(fp):
                            os.remove(fp)
                            del_count += 1
                            freed_bytes += sz
                    except:
                        pass
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        freed_mb = freed_bytes / (1024 * 1024)
        await update.message.reply_text(
            f"🧹 <b>پاکسازی انجام شد!</b>\n\n"
            f"🗑️ فایل‌های حذف‌شده: <b>{del_count}</b>\n"
            f"💾 فضای آزادشده دیسک: <b>{freed_mb:.1f} MB</b>\n"
            f"✨ حافظه کش GPU نیز آزاد شد.",
            parse_mode="HTML"
        )

    async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        raw_name = user.first_name if user and user.first_name else "کاربر گرامی"
        safe_name = html.escape(raw_name)
        await update.message.reply_text(
            f"‏🎬 <b>سلام {safe_name}!</b>\n\n"
            "‏🚀 ربات تقویت‌شده با <b>VAD + ForcedAligner + Qwen3.6-35B</b> فعال است.\n\n"
            "‏✨ قابلیت‌ها:\n"
            "‏• رونویسی دقیق گفتار با حذف خودکار سکوت\n"
            "‏• تایمینگ کلمه به کلمه زیرنویس\n"
            "‏• ترجمه فارسی روان موازی (۸ دسته‌ای)\n"
            "‏• هاردساب مستقیم به ویدیو با حفظ کدک\n\n"
            "‏📥 یک فایل صوتی یا تصویری بفرستید یا از دکمه <b>Menu</b> برای دستورات دیگر استفاده کنید.",
            parse_mode="HTML"
        )

    async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = update.message
        media = msg.video or msg.audio or msg.voice or msg.document
        if not media:
            return

        status_msg = await msg.reply_text("‏⏳ دریافت فایل...")
        file_id = media.file_id
        is_temp = False

        try:
            total_start = time.time()
            logging.info(f"📥 file_id: {file_id} | type: {type(media).__name__}")

            tg_file = await asyncio.wait_for(context.bot.get_file(file_id), timeout=120)
            file_name = getattr(media, "file_name", None) or f"media_{int(time.time())}.mp4"
            base_name = os.path.splitext(file_name)[0]
            input_path = f"{WORK_DIR}/input/{file_name}"

            local_src = tg_file.file_path
            if local_src and os.path.exists(local_src):
                shutil.copy2(local_src, input_path)
                is_temp = True
                logging.info(f"📁 کپی محلی: {os.path.getsize(input_path)/(1024*1024):.1f} MB")
            else:
                await asyncio.wait_for(tg_file.download_to_drive(custom_path=input_path), timeout=900)
                is_temp = True
                logging.info(f"⬇️ دانلود: {os.path.getsize(input_path)/(1024*1024):.1f} MB")

            thumb_path = f"{WORK_DIR}/output/{base_name}.thumb.jpg"
            orig_thumb = getattr(media, "thumbnail", None)
            if orig_thumb:
                try:
                    tg_thumb = await context.bot.get_file(orig_thumb.file_id)
                    if tg_thumb.file_path and os.path.exists(tg_thumb.file_path):
                        shutil.copy2(tg_thumb.file_path, thumb_path)
                    else:
                        await tg_thumb.download_to_drive(custom_path=thumb_path)
                    logging.info(f"🖼️ تامبنیل اصلی تلگرام ذخیره شد: {thumb_path}")
                except Exception as _te:
                    logging.warning(f"خطا در دریافت تامبنیل تلگرام: {_te}")

            await status_msg.edit_text("‏🔍 در حال پردازش صوت و استخراج زیرنویس...")

            loop = asyncio.get_running_loop()
            last_upd = [0.0]

            def _on_prog(stage_title, pct, t_lbl):
                now = time.time()
                if now - last_upd[0] >= 3.0 or pct >= 98:
                    last_upd[0] = now
                    vram_str = ""
                    if torch.cuda.is_available():
                        vram_str = f"\n💾 حافظه گرافیک (VRAM): <b>{torch.cuda.memory_allocated()/(1024**3):.1f} / {torch.cuda.get_device_properties(0).total_memory/(1024**3):.1f} GB</b>"
                    try:
                        asyncio.run_coroutine_threadsafe(
                            status_msg.edit_text(
                                f"‏⚙️ <b>در حال ساخت زیرنویس هوشمند...</b>\n\n"
                                f"‏📌 وضعیت: <b>{stage_title}</b>\n"
                                f"‏📊 پیشرفت: <b>{pct}%</b>\n"
                                f"‏⏳ زمان تخمینی باقی‌مانده: <b>{t_lbl}</b>"
                                f"{vram_str}",
                                parse_mode="HTML"
                            ), loop
                        )
                    except:
                        pass

            srt_path, transcribe_inf, total_duration = await loop.run_in_executor(
                None, process_audio_enhanced, input_path, base_name, _on_prog
            )

            stage1_total_time = time.time() - total_start
            speed_ratio = total_duration / max(transcribe_inf, 0.1) if total_duration > 0 else 1.0
            dur_min = total_duration / 60.0

            meta_path = f"{WORK_DIR}/output/{base_name}.meta.json"
            try:
                with open(meta_path, "w", encoding="utf-8") as _mf:
                    json.dump({
                        "transcribe_inf": transcribe_inf,
                        "stage1_total_time": stage1_total_time,
                        "duration": total_duration,
                        "input_path": input_path,
                        "thumb_path": thumb_path if os.path.exists(thumb_path) else None,
                    }, _mf)
            except Exception as _me:
                logging.warning(f"Meta save: {_me}")

            kb_buttons = [
                [InlineKeyboardButton("🌐 ترجمه به فارسی", callback_data=f"translate_{base_name}")],
                [InlineKeyboardButton("🎬 هاردساب زیرنویس اصلی به ویدیو", callback_data=f"hardsub_orig_{base_name}")]
            ]
            kb = InlineKeyboardMarkup(kb_buttons)
            with open(srt_path, "rb") as f:
                await asyncio.wait_for(
                    msg.reply_document(
                        document=f,
                        filename=f"{base_name}.srt",
                        caption=(
                            f"🎉 <b>زیرنویس با موفقیت آماده شد!</b>\n\n"
                            f"⏱️ مدت فایل: <b>{total_duration:.1f} ثانیه</b> ({dur_min:.1f} دقیقه)\n"
                            f"⏱️ زمان رونویسی (هوش مصنوعی): <b>{transcribe_inf:.1f} ثانیه</b>\n"
                            f"⚡ سرعت پردازش هوش مصنوعی: <b>{speed_ratio:.1f} برابر زمان واقعی</b>\n"
                            f"⏱️ زمان کل مرحله ۱ (دانلود + FFmpeg + رونویسی): <b>{stage1_total_time:.1f} ثانیه</b>\n\n"
                            f"👇 برای دریافت ترجمه یا هاردساب مستقیم، انتخاب کنید:"
                        ),
                        parse_mode="HTML",
                        reply_markup=kb,
                    ),
                    timeout=120
                )
            await status_msg.delete()
            logging.info("📤 SRT ارسال شد")

        except Exception as e:
            logging.error(f"❌ {traceback.format_exc()}")
            safe_err = html.escape(str(e))
            await status_msg.edit_text(
                f"‏❌ خطا:\n<code>{safe_err}</code>\n{type(e).__name__}",
                parse_mode="HTML"
            )
        finally:
            pass

    async def translate_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        base_name = query.data.replace("translate_", "")
        srt_path = f"{WORK_DIR}/output/{base_name}.srt"
        fa_path = f"{WORK_DIR}/output/{base_name}_fa.srt"
        meta_path = f"{WORK_DIR}/output/{base_name}.meta.json"

        if not os.path.exists(srt_path):
            await query.edit_message_caption(caption="❌ فایل SRT یافت نشد")
            return

        transcribe_inf = 0.0
        stage1_total_time = 0.0
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as _mf:
                    _mdata = json.load(_mf)
                    transcribe_inf = float(_mdata.get("transcribe_inf", _mdata.get("transcribe_time", 0.0)))
                    stage1_total_time = float(_mdata.get("stage1_total_time", transcribe_inf))
            except Exception:
                pass

        await query.edit_message_caption(
            caption="⏳ <b>در حال راه‌اندازی و بارگذاری شتاب‌دهنده هوشمند ترجمه (Qwen3.6-35B)...</b>",
            parse_mode="HTML"
        )

        try:
            loop = asyncio.get_running_loop()
            tr_start_time = time.time()
            final_stats = {"lines": 0, "tokens": 0}

            def _run_worker():
                cmd = [sys.executable, f"{WORK_DIR}/translate_worker.py", srt_path, "32", "8"]
                env = os.environ.copy()
                env["PYTHONPATH"] = f"{WORK_DIR}/tf5_env:" + env.get("PYTHONPATH", "")
                p = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
                last_upd = [0.0]
                start_gen_time = [0.0]
                for line in p.stdout:
                    line = line.strip()
                    if line == "STATUS:translating":
                        start_gen_time[0] = time.time()
                    elif line.startswith("PROGRESS:"):
                        parts = line.split(":")
                        prog = parts[1]
                        cur, tot = map(int, prog.split("/"))
                        vram_info = parts[2] if len(parts) > 2 else ""
                        toks = int(parts[3]) if len(parts) > 3 else 0

                        now = time.time()
                        if now - last_upd[0] >= 3.0 or cur == tot:
                            last_upd[0] = now
                            pct = int((cur / max(tot, 1)) * 100)
            
                            elapsed_gen = now - (start_gen_time[0] or tr_start_time)
                            avg_t = elapsed_gen / max(cur, 1)
                            rem_t = (tot - cur) * avg_t
                            t_str = f"~{rem_t:.0f} ثانیه" if cur > 0 and rem_t > 0 else "در حال تخمین..."
            
                            vram_txt = f"\n💾 حافظه گرافیک (VRAM): <b>{vram_info} گیگابایت</b>" if vram_info else ""
                            tok_txt = f"\n🔤 توکن‌های فعلی: <b>{toks:,}</b>" if toks > 0 else ""

                            try:
                                asyncio.run_coroutine_threadsafe(
                                    query.edit_message_caption(
                                        caption=(
                                            f"🔄 <b>در حال ترجمه فوق‌سریع زیرنویس (۸ دسته‌ای)...</b>\n\n"
                                            f"📊 پیشرفت: <b>{pct}%</b> (بخش {cur} از {tot})\n"
                                            f"⏳ زمان تخمینی باقی‌مانده: <b>{t_str}</b>"
                                            f"{tok_txt}"
                                            f"{vram_txt}"
                                        ),
                                        parse_mode="HTML"
                                    ),
                                    loop
                                )
                            except:
                                pass
                    elif line.startswith("DONE:"):
                        parts = line.split(":")
                        if len(parts) >= 4:
                            final_stats["lines"] = int(parts[2])
                            final_stats["tokens"] = int(parts[3])
            
                p.wait()
                if p.returncode != 0:
                    err = p.stderr.read()
                    raise RuntimeError(err[-300:] if err else "Worker failed")
                return fa_path

            fa_path = await loop.run_in_executor(None, _run_worker)
            translate_time = time.time() - tr_start_time
            grand_total = stage1_total_time + translate_time if stage1_total_time > 0 else translate_time

            if os.path.exists(meta_path):
                try:
                    with open(meta_path, "r", encoding="utf-8") as _mf:
                        _mdata = json.load(_mf)
                    _mdata["translate_time"] = translate_time
                    with open(meta_path, "w", encoding="utf-8") as _mf:
                        json.dump(_mdata, _mf)
                except Exception as _me:
                    logging.warning(f"Meta update translate: {_me}")

            tok_count = final_stats["tokens"]
            line_count = final_stats["lines"]
            tok_m = tok_count / 1_000_000
            speed = tok_count / max(translate_time, 1)

            t_m1_inf = f"⏱️ زمان رونویسی هوش مصنوعی (مرحله ۱): <b>{transcribe_inf:.1f} ثانیه</b>\n" if transcribe_inf > 0 else ""
            t_m1_tot = f"⏱️ زمان کل مرحله ۱ (دانلود + FFmpeg + رونویسی): <b>{stage1_total_time:.1f} ثانیه</b>\n" if stage1_total_time > 0 else ""
            t_tot_txt = f"⏱️ زمان کل فرآیند (مرحله ۱ + ۲): <b>{grand_total:.1f} ثانیه</b>\n" if stage1_total_time > 0 else ""

            kb_fa = InlineKeyboardMarkup([[
                InlineKeyboardButton("🎬 چسباندن زیرنویس فارسی به ویدیو (هاردساب)", callback_data=f"hardsub_fa_{base_name}")
            ]])
            with open(fa_path, "rb") as f:
                await query.message.reply_document(
                    document=f,
                    filename=f"{base_name}_fa.srt",
                    caption=(
                        f"🌐 <b>زیرنویس فارسی با موفقیت آماده شد!</b>\n\n"
                        f"📝 تعداد کل خطوط: <b>{line_count} خط</b>\n"
                        f"🔤 کل توکن‌های پردازش‌شده: <b>{tok_count:,} توکن</b> ({tok_m:.3f}M)\n"
                        f"{t_m1_inf}"
                        f"{t_m1_tot}"
                        f"⏱️ زمان ترجمه (مرحله ۲): <b>{translate_time:.1f} ثانیه</b> (سرعت: <b>{speed:.0f}</b> tok/s)\n"
                        f"{t_tot_txt}"
                        f"⚡ پردازش موازی: <b>۸ دسته‌ای (Tensor Batching)</b>\n\n"
                        f"🎬 برای چسباندن دائمی زیرنویس به ویدیو، روی دکمه زیر کلیک کنید:"
                    ),
                    parse_mode="HTML",
                    reply_markup=kb_fa
                )

            await query.edit_message_caption(caption="✅ ترجمه فارسی با موفقیت انجام و ارسال شد.")

        except Exception as e:
            logging.error(f"❌ ترجمه: {traceback.format_exc()}")
            safe_err = html.escape(str(e))
            await query.edit_message_caption(
                caption=f"❌ خطا در ترجمه:\n<code>{safe_err}</code>",
                parse_mode="HTML"
            )
        finally:
            try:
                await query.edit_message_reply_markup(reply_markup=None)
            except:
                pass

    async def hardsub_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        data = query.data
        is_fa = "hardsub_fa_" in data
        base_name = data.replace("hardsub_fa_", "").replace("hardsub_orig_", "")

        srt_path = f"{WORK_DIR}/output/{base_name}_fa.srt" if is_fa else f"{WORK_DIR}/output/{base_name}.srt"
        meta_path = f"{WORK_DIR}/output/{base_name}.meta.json"

        if not os.path.exists(srt_path):
            await query.message.reply_text("❌ فایل زیرنویس یافت نشد.")
            return

        video_path = None
        total_dur = 0.0
        saved_thumb = None
        stage1_time = 0.0
        stage2_time = 0.0
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as _mf:
                    _mdata = json.load(_mf)
                    video_path = _mdata.get("input_path")
                    total_dur = float(_mdata.get("duration", 0.0))
                    saved_thumb = _mdata.get("thumb_path")
                    stage1_time = float(_mdata.get("stage1_total_time", 0.0))
                    stage2_time = float(_mdata.get("translate_time", 0.0))
            except:
                pass

        if not video_path or not os.path.exists(video_path):
            for f in os.listdir(f"{WORK_DIR}/input"):
                if f.startswith(base_name) and not f.endswith(".wav"):
                    video_path = f"{WORK_DIR}/input/{f}"
                    break

        if not video_path or not os.path.exists(video_path):
            await query.message.reply_text("❌ ویدیوی منبع برای هاردساب یافت نشد.")
            return

        orig_codec = "h264"
        v_width = 1280
        v_height = 720
        probe_cmd = [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height,duration,codec_name,sample_aspect_ratio:stream_tags=rotate:format=duration",
            "-of", "json", video_path
        ]
        try:
            probe_res = json.loads(subprocess.run(probe_cmd, capture_output=True, text=True).stdout)
            streams = probe_res.get("streams", [])
            if not streams:
                await query.message.reply_text("❌ این فایل تصویر ندارد و قابل هاردساب نیست.")
                return
            s = streams[0]
            orig_codec = s.get("codec_name", "h264").lower()
            w = int(s.get("width", 1280))
            h = int(s.get("height", 720))
            rot = s.get("tags", {}).get("rotate", 0)
            try:
                rot = int(float(rot))
            except:
                rot = 0
            if rot in [90, 270]:
                w, h = h, w
            v_width, v_height = w, h

            if "duration" in s and float(s["duration"]) > 0:
                total_dur = float(s["duration"])
            if total_dur <= 0:
                total_dur = float(probe_res.get("format", {}).get("duration", 0.0))
        except Exception as _pe:
            logging.warning(f"Probe error: {_pe}")

        if orig_codec in ["hevc", "h265"]:
            enc_args = ["-c:v", "libx265", "-preset", "veryfast", "-crf", "25"]
            codec_display = "HEVC / H.265"
        elif orig_codec in ["vp9"]:
            enc_args = ["-c:v", "libvpx-vp9", "-crf", "30", "-b:v", "0"]
            codec_display = "VP9"
        elif orig_codec in ["av1"]:
            enc_args = ["-c:v", "libsvtav1", "-preset", "7", "-crf", "30"]
            codec_display = "AV1"
        else:
            enc_args = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "22"]
            codec_display = "H.264 / AVC"

        label = "فارسی" if is_fa else "اصلی"
        status_msg = await query.message.reply_text(
            f"⏳ <b>در حال آماده‌سازی هاردساب زیرنویس {label}...</b>\n"
            f"🎞️ انکودر هماهنگ: <b>{codec_display}</b>\n"
            f"📐 ابعاد ویدیو: <b>{v_width}×{v_height}</b>\n"
            f"⚡ پردازش پرسرعت با {FFMPEG_THREADS} رشته CPU",
            parse_mode="HTML"
        )

        out_video = f"{WORK_DIR}/output/{base_name}_{'fa_' if is_fa else ''}hardsub.mp4"
        t0 = time.time()

        clean_srt_path = f"{WORK_DIR}/temp/{base_name}_{'fa_' if is_fa else ''}clean_render.srt"
        try:
            with open(srt_path, "r", encoding="utf-8") as _in_f:
                _raw_srt = _in_f.read()
            _raw_srt = re.sub(r'[​‎﻿­�]', '', _raw_srt)
            _clean_lines = []
            for line in _raw_srt.splitlines():
                line_str = line.strip()
                if line_str and not line_str.isdigit() and "-->" not in line_str:
                    if not line_str.startswith("‏"):
                        line_str = "‏" + line_str
                _clean_lines.append(line_str)
            with open(clean_srt_path, "w", encoding="utf-8") as _out_f:
                _out_f.write("\n".join(_clean_lines))
            srt_to_render = clean_srt_path
        except Exception as _re:
            logging.warning(f"RTL clean error: {_re}")
            srt_to_render = srt_path

        escaped_srt = srt_to_render.replace("'", "'\\''").replace(":", "\\:")
        escaped_font_dir = FONT_DIR.replace("'", "'\\''").replace(":", "\\:")
        style = "FontName=Vazirmatn,FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2.2,Shadow=1,MarginV=25"
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", f"subtitles='{escaped_srt}':fontsdir='{escaped_font_dir}':force_style='{style}'",
            *enc_args,
            "-threads", str(FFMPEG_THREADS),
            "-c:a", "copy",
            "-progress", "pipe:1",
            "-y", out_video
        ]

        loop = asyncio.get_running_loop()

        def _run_ffmpeg():
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
            last_upd = [0.0]
            for line in p.stdout:
                line = line.strip()
                if line.startswith("out_time_us="):
                    try:
                        us = int(line.split("=")[1])
                        cur_sec = us / 1_000_000.0
                        if total_dur > 0:
                            pct = min(99, int((cur_sec / total_dur) * 100))
                            elapsed = time.time() - t0
                            speed_ratio = cur_sec / max(elapsed, 0.1)
                            rem_sec = (total_dur - cur_sec) / max(speed_ratio, 0.1)
                            t_lbl = f"~{rem_sec:.0f} ثانیه" if rem_sec > 0 else "در حال نهایی‌سازی..."

                            now = time.time()
                            if now - last_upd[0] >= 3.0:
                                last_upd[0] = now
                                try:
                                    asyncio.run_coroutine_threadsafe(
                                        status_msg.edit_text(
                                            f"⏳ <b>در حال هاردساب زیرنویس {label} روی ویدیو...</b>\n\n"
                                            f"🎞️ کدک خروجی: <b>{codec_display}</b>\n"
                                            f"📊 پیشرفت رندر: <b>{pct}%</b>\n"
                                            f"⚡ سرعت: <b>{speed_ratio:.1f}x برابر زمان واقعی</b>\n"
                                            f"⏳ زمان باقی‌مانده: <b>{t_lbl}</b>",
                                            parse_mode="HTML"
                                        ), loop
                                    )
                                except:
                                    pass
                    except:
                        pass
            p.wait()
            return p.returncode, p.stderr.read()

        retcode, stderr_out = await loop.run_in_executor(None, _run_ffmpeg)
        dt = time.time() - t0

        if retcode != 0 or not os.path.exists(out_video):
            logging.error(f"FFmpeg hardsub: {stderr_out[-300:]}")
            safe_err = html.escape(stderr_out[-200:])
            await status_msg.edit_text(f"❌ خطا در هاردساب:\n<code>{safe_err}</code>", parse_mode="HTML")
            return

        thumb_path = saved_thumb if (saved_thumb and os.path.exists(saved_thumb) and os.path.getsize(saved_thumb) > 0) else f"{WORK_DIR}/output/{base_name}.thumb.jpg"
        if not os.path.exists(thumb_path) or os.path.getsize(thumb_path) == 0:
            seek_sec = min(2.0, max(0.5, total_dur * 0.1)) if total_dur > 0 else 1.0
            subprocess.run([
                "ffmpeg", "-ss", str(seek_sec), "-i", video_path,
                "-vframes", "1", "-vf", "scale='min(320,iw)':-2", "-q:v", "2", "-y", thumb_path
            ], capture_output=True)

        size_mb = os.path.getsize(out_video) / (1024 * 1024)
        await status_msg.edit_text("📤 در حال ارسال ویدیوی هاردساب شده به تلگرام...")

        thumb_file = None
        if os.path.exists(thumb_path) and os.path.getsize(thumb_path) > 0:
            try:
                thumb_file = open(thumb_path, "rb")
            except:
                thumb_file = None

        try:
            if is_fa and stage1_time > 0 and stage2_time > 0:
                total_all = stage1_time + stage2_time + dt
                total_line = f"⏱️ زمان کل ۳ مرحله: <b>{total_all:.1f} ثانیه</b>\n"
            elif stage1_time > 0:
                total_all = stage1_time + dt
                total_line = f"⏱️ زمان کل ۲ مرحله: <b>{total_all:.1f} ثانیه</b>\n"
            else:
                total_line = ""

            with open(out_video, "rb") as vf:
                await query.message.reply_video(
                    video=vf,
                    filename=os.path.basename(out_video),
                    duration=int(round(total_dur)) if total_dur > 0 else None,
                    width=v_width,
                    height=v_height,
                    thumbnail=thumb_file,
                    caption=(
                        f"🎬 <b>ویدیوی هاردساب‌شده ({label}) با موفقیت آماده شد!</b>\n\n"
                        f"🎞️ کدک ویدیویی: <b>{codec_display}</b>\n"
                        f"📐 ابعاد: <b>{v_width}×{v_height}</b>\n"
                        f"⏱️ زمان رندر و هاردساب: <b>{dt:.1f} ثانیه</b>\n"
                        f"{total_line}"
                        f"📦 حجم ویدیو: <b>{size_mb:.1f} مگابایت</b>"
                    ),
                    parse_mode="HTML",
                    supports_streaming=True,
                    read_timeout=600,
                    write_timeout=600,
                )
        finally:
            if thumb_file:
                try:
                    thumb_file.close()
                except:
                    pass

        await status_msg.delete()

    async def kill_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🛑 توقف ربات...")
        _state = getattr(sys, "_qwen_bot_state", None)
        if _state and _state.get("stop_event"):
            _state["stop_event"].set()
        elif 'GLOBAL_BOT_STOP_EVENT' in globals():
            GLOBAL_BOT_STOP_EVENT.set()

    # ══════════════════════════════════════════════
    #  ۱۱. راه‌اندازی ربات
    # ══════════════════════════════════════════════
    async def post_init_setup(application):
        commands = [
            BotCommand("start", "🚀 شروع مجدد و راهنما"),
            BotCommand("status", "📊 وضعیت زنده گرافیک و منابع"),
            BotCommand("clean", "🧹 پاکسازی فایل‌های موقت"),
            BotCommand("help", "ℹ️ راهنمای کامل امکانات و کدک‌ها"),
            BotCommand("kill", "🛑 توقف اضطراری"),
        ]
        try:
            await application.bot.set_my_commands(commands)
            await application.bot.set_chat_menu_button(menu_button=MenuButtonCommands())
            logging.info("✅ MenuButtonCommands با موفقیت ثبت شد")
        except Exception as e:
            logging.warning(f"⚠️ MenuButton error: {e}")

    app = (
        ApplicationBuilder()
        .token(os.environ["BOT_TOKEN"])
        .base_url(f"http://127.0.0.1:{LOCAL_PORT}/bot")
        .base_file_url(f"http://127.0.0.1:{LOCAL_PORT}/file/bot")
        .local_mode(True)
        .concurrent_updates(16)
        .read_timeout(300)
        .write_timeout(300)
        .connect_timeout(60)
        .pool_timeout(300)
        .get_updates_read_timeout(300)
        .post_init(post_init_setup)
        .build()
    )

    app.add_handler(CommandHandler("start", start_handler, block=False))
    app.add_handler(CommandHandler("status", status_handler, block=False))
    app.add_handler(CommandHandler("clean", clean_handler, block=False))
    app.add_handler(CommandHandler("help", help_handler, block=False))
    app.add_handler(CommandHandler("kill", kill_handler, block=False))
    app.add_handler(MessageHandler(
        filters.VIDEO | filters.AUDIO | filters.VOICE | filters.Document.ALL,
        handle_media,
        block=False
    ))
    app.add_handler(CallbackQueryHandler(status_refresh_callback, pattern="^refresh_status$", block=False))
    app.add_handler(CallbackQueryHandler(translate_callback, pattern="^translate_", block=False))
    app.add_handler(CallbackQueryHandler(hardsub_callback, pattern="^hardsub_", block=False))

    GLOBAL_BOT_STOP_EVENT = threading.Event()
    if not hasattr(sys, "_qwen_bot_state"):
        sys._qwen_bot_state = {}

    sys._qwen_bot_state["stop_event"] = GLOBAL_BOT_STOP_EVENT
    sys._qwen_bot_state["app"] = app

    async def _bot_main(bot_app, stop_evt):
        import asyncio, logging, time
        from telegram import BotCommand, MenuButtonCommands

        await bot_app.initialize()
        bot_info = None
        for attempt in range(5):
            try:
                bot_info = await bot_app.bot.get_me()
                break
            except Exception as e:
                logging.warning(f"⚠️ تلاش {attempt+1}/5 اتصال به سرور: {e}")
                if attempt < 4:
                    await asyncio.sleep(2)

        if bot_info is None:
            logging.error("❌ اتصال ناموفق به بات تلگرام!")
            try:
                await bot_app.shutdown()
            except Exception:
                pass
            return

        _bu = bot_info.username
        print(" [1;32m" + "="*60 + " [0m")
        print(" [1;32m🎉 ربات تقویت‌شده فعال شد! [0m")
        print(f" [1;36m🤖 @{_bu} [0m")
        print(f" [1;32m   https://t.me/{_bu} [0m")
        print(" [1;36m✨ VAD + ASR + ForcedAligner + Translation [0m")
        print(" [1;32m" + "="*60 + " [0m")

        await bot_app.start()
        await bot_app.updater.start_polling(drop_pending_updates=True)
        try:
            while not stop_evt.is_set():
                await asyncio.sleep(0.5)
        except (KeyboardInterrupt, SystemExit, asyncio.CancelledError, Exception):
            pass
        finally:
            import asyncio
            if bot_app.updater and bot_app.updater.running:
                try:
                    await bot_app.updater.stop()
                except Exception:
                    pass
            if bot_app.running:
                try:
                    await bot_app.stop()
                except Exception:
                    pass
            try:
                await bot_app.shutdown()
            except Exception:
                pass

    def _run_bot(bot_app, stop_evt):
        import asyncio, logging
        try:
            asyncio.run(_bot_main(bot_app, stop_evt))
        except Exception:
            pass

    bot_thread = threading.Thread(target=_run_bot, args=(app, GLOBAL_BOT_STOP_EVENT), daemon=True)
    sys._qwen_bot_state["bot_thread"] = bot_thread
    bot_thread.start()

    # ══════════════════════════════════════════════
    #  نمایش نهایی
    # ══════════════════════════════════════════════
    mo.vstack([
        mo.md(f"## ✅ ربات تقویت‌شده فعال شد!"),
        mo.md(f"""
        **نام ربات:** {_bot_first}  
        **یوزرنیم:** @{_bot_username}

        🚀 **پایپ‌این:**
        - ✅ FireRedVAD — حذف سکوت و موسیقی
        - ✅ Qwen3-ASR-1.7B — رونویسی متن
        - ✅ Qwen3-ForcedAligner-0.6B — تایمینگ سطح کلمه
        - ✅ ترجمه فارسی — با یک کلیک (Qwen3.6-35B-A3B)

        👉 لینک ربات: https://t.me/{_bot_username}

        📤 برای توقف: دستور `/kill` را به ربات بفرستید
        """),
    ])
    return


if __name__ == "__main__":
    app.run()
