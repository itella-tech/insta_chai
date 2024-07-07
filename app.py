import streamlit as st
import requests
import os
from anthropic import Anthropic
import io

# APIキーの設定
elevenlabs_api_key = st.secrets["ELEVENLABS_API_KEY"]
claude_api_key = st.secrets["CLAUDE_API_KEY"]


# Claudeクライアントの初期化
anthropic = Anthropic(api_key=claude_api_key)

def generate_japanese_script(prompt):
    try:
        completion = anthropic.completions.create(
            model="claude-2",
            max_tokens_to_sample=1000,
            prompt=f"\n\nHuman: 日本語で以下のプロンプトに基づいた台本を作成してください：\n\n{prompt}\n\nAssistant: はい、承知しました。以下に日本語の台本を作成いたします：\n\n",
        )
        return completion.completion
    except Exception as e:
        st.error(f"日本語台本の生成中にエラーが発生しました: {str(e)}")
        return None

def translate_to_chinese(japanese_text):
    try:
        completion = anthropic.completions.create(
            model="claude-2",
            max_tokens_to_sample=1000,
            prompt=f"\n\nHuman: 以下の日本語テキストを中国語（簡体字）に翻訳してください：\n\n{japanese_text}\n\nAssistant: はい、承知しました。以下に日本語テキストの中国語（簡体字）翻訳を提供いたします：\n\n",
        )
        return completion.completion
    except Exception as e:
        st.error(f"中国語への翻訳中にエラーが発生しました: {str(e)}")
        return None

def generate_audio(text):
    url = "https://api.elevenlabs.io/v1/text-to-speech/ByhETIclHirOlWnWKhHc"  # ここを変更しました
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": elevenlabs_api_key
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            st.error(f"音声生成中にエラーが発生しました: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"音声生成中にエラーが発生しました: {str(e)}")
        return None

# Streamlitアプリケーション
st.title("日本語台本生成 & 中国語翻訳 & 音声生成アプリ")

# タブの作成
tab1, tab2, tab3 = st.tabs(["日本語台本生成", "中国語翻訳", "音声生成"])

# タブ1: 日本語台本の生成
with tab1:
    st.header("日本語台本生成")
    japanese_prompt = st.text_area("日本語台本のプロンプトを入力してください：")
    if st.button("日本語台本を生成"):
        if japanese_prompt and claude_api_key:
            japanese_script = generate_japanese_script(japanese_prompt)
            if japanese_script:
                st.session_state['japanese_script'] = japanese_script
                st.write("生成された日本語台本:")
                st.write(japanese_script)
        else:
            st.warning("プロンプトとClaude APIキーを入力してください。")

# タブ2: 中国語翻訳
with tab2:
    st.header("中国語翻訳")
    japanese_script = st.text_area("日本語台本を入力してください：", value=st.session_state.get('japanese_script', ''))
    
    if st.button("中国語に翻訳"):
        if japanese_script and claude_api_key:
            chinese_script = translate_to_chinese(japanese_script)
            if chinese_script:
                st.session_state['chinese_script'] = chinese_script
                st.write("翻訳された中国語:")
                st.write(chinese_script)
        else:
            st.warning("日本語台本とClaude APIキーを入力してください。")

# タブ3: 音声生成
with tab3:
    st.header("音声生成")
    chinese_script = st.text_area("中国語テキストを入力してください：", value=st.session_state.get('chinese_script', ''))
    
    if st.button("音声を生成"):
        if chinese_script and elevenlabs_api_key:
            audio_content = generate_audio(chinese_script)
            if audio_content:
                st.audio(audio_content, format='audio/mp3')
                st.session_state['audio_content'] = audio_content
        else:
            st.warning("中国語テキストとElevenLabs APIキーを入力してください。")

    # 音声のダウンロード
    if 'audio_content' in st.session_state:
        audio_file = io.BytesIO(st.session_state['audio_content'])
        st.download_button(
            label="音声をダウンロード",
            data=audio_file,
            file_name="generated_audio.mp3",
            mime="audio/mp3"
        )