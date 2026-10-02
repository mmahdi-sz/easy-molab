# translate_worker.py
import sys, os, re, json, time
import torch
import pysrt
from transformers import AutoModelForImageTextToText, AutoTokenizer, BitsAndBytesConfig

SYSTEM_PROMPT_FA = """تو یک مترجم حرفه‌ای زیرنویس هستی. متن زیرنویس را به فارسی روان، طبیعی و محاوره‌ای ترجمه کن.
قوانین:
- فقط ترجمه را برگردان، هیچ توضیح اضافه‌ای ننویس
- ترتیب جملات و ساختار را حفظ کن
- هر خط ترجمه را با شماره [1], [2], ... شروع کن
- اصطلاحات، نام‌ها و اعداد را دقیق نگه دار
- اگر متن کوتاه است، کوتاه ترجمه کن
- خروجی فقط متن ترجمه‌شده با شماره خطوط باشد"""

def main():
    if len(sys.argv) < 2:
        sys.exit(1)
        
    srt_path = sys.argv[1]
    batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 32
    parallel_size = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    output_path = srt_path.replace(".srt", "_fa.srt")
    
    print("STATUS:loading_model", flush=True)
    model_id = "Qwen/Qwen3.6-35B-A3B"
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
    tok = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    model = AutoModelForImageTextToText.from_pretrained(
        model_id,
        quantization_config=bnb_config,
        device_map="cuda:0",
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
    )
    model.eval()
    
    print("STATUS:translating", flush=True)
    subs = pysrt.open(srt_path, encoding="utf-8")
    chunks, cur = [], []
    for i, sub in enumerate(subs):
        cur.append({"index": i, "start": sub.start, "end": sub.end, "text": sub.text.strip()})
        if len(cur) >= batch_size:
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)

    total_chunks = len(chunks)
    translated_chunks = []
    total_tokens = 0
    
    for p_idx in range(0, total_chunks, parallel_size):
        batch_chunks = chunks[p_idx:p_idx + parallel_size]
        prompts = []
        for chunk in batch_chunks:
            texts_with_numbers = [f"[{item['index']+1}] {item['text']}" for item in chunk]
            full_text = "\n".join(texts_with_numbers)
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT_FA},
                {"role": "user", "content": f"این متن زیرنویس را به فارسی ترجمه کن:\n\n{full_text}"}
            ]
            p = tok.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False
            )
            prompts.append(p)
            
        inputs = tok(prompts, padding=True, return_tensors="pt").to(model.device)
        in_len = inputs["input_ids"].shape[1]
        
        batch_in_tokens = inputs["input_ids"].numel()
        total_tokens += batch_in_tokens
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=2048,
                temperature=0.3,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tok.pad_token_id,
            )
            
        for i in range(len(prompts)):
            out_toks = (outputs[i][in_len:] != tok.pad_token_id).sum().item()
            total_tokens += out_toks
            
            resp = tok.decode(outputs[i][in_len:], skip_special_tokens=True)
            resp = re.sub(r"<think>.*?</think>", "", resp, flags=re.DOTALL).strip()
            translated_chunks.append(resp)
            
        done_chunks = min(p_idx + parallel_size, total_chunks)
        vram_used = torch.cuda.memory_allocated() / (1024**3)
        vram_total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"PROGRESS:{done_chunks}/{total_chunks}:{vram_used:.1f}/{vram_total:.1f}:{total_tokens}", flush=True)

    all_translated_lines = []
    for translated in translated_chunks:
        lines = [line.strip() for line in translated.split("\n") if line.strip()]
        clean_lines = [re.sub(r'[​‎﻿­�]', '', line).strip() for line in lines]
        clean_lines = [re.sub(r"^\[\d+\]\s*", "", line) for line in clean_lines]
        clean_lines = [f"‏{line}" if not line.startswith("‏") else line for line in clean_lines]
        all_translated_lines.extend(clean_lines)

    if len(all_translated_lines) != len(subs):
        all_translated_lines = all_translated_lines[:len(subs)]
        while len(all_translated_lines) < len(subs):
            all_translated_lines.append(subs[len(all_translated_lines)].text)

    new_subs = pysrt.SubRipFile()
    for i, sub in enumerate(subs):
        new_sub = pysrt.SubRipItem(
            index=i + 1,
            start=sub.start,
            end=sub.end,
            text=all_translated_lines[i]
        )
        new_subs.append(new_sub)

    new_subs.save(output_path, encoding="utf-8")
    print(f"DONE:{output_path}:{len(subs)}:{total_tokens}", flush=True)

if __name__ == "__main__":
    main()
