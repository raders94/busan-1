# ============================================================
# AI 데이터베이스 강의 실시간 필기 프로그램
# ============================================================

# ------------------------------------------------------------
# OpenMP DLL 중복 충돌 임시 우회
# 반드시 numpy / faster-whisper import 전에 위치해야 함
# ------------------------------------------------------------

import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


# ------------------------------------------------------------
# 기본 라이브러리
# ------------------------------------------------------------

import queue
import threading
import time
from datetime import datetime
from pathlib import Path

import tkinter as tk
from tkinter import scrolledtext, messagebox


# ------------------------------------------------------------
# 외부 라이브러리
# ------------------------------------------------------------

import numpy as np
import requests
import sounddevice as sd

from faster_whisper import WhisperModel


# ============================================================
# 기본 설정
# ============================================================

SAMPLE_RATE = 16000

# Whisper가 한 번에 분석할 음성 길이
CHUNK_SECONDS = 5

# 다음 구간과 겹치는 시간
OVERLAP_SECONDS = 1

# 몇 초마다 AI 자동 정리할지
SUMMARY_INTERVAL = 60


# ============================================================
# Whisper 설정
# ============================================================

# CPU 기준 추천
#
# tiny   : 매우 빠름 / 정확도 낮음
# base   : 빠름
# small  : 추천
# medium : 정확하지만 CPU에서는 느림

WHISPER_MODEL = "small"


# Whisper 모델 객체
model = None

# 모델 준비 여부
model_ready = False


# ============================================================
# Ollama 설정
# ============================================================

# 설치된 Ollama 모델 이름에 맞게 변경

OLLAMA_MODEL = "qwen3:4b"

OLLAMA_URL = "http://localhost:11434/api/generate"


# ============================================================
# 저장 폴더
# ============================================================

BASE_DIR = Path(__file__).parent

NOTE_DIR = BASE_DIR / "lecture_notes"

NOTE_DIR.mkdir(
    exist_ok=True
)


session_name = datetime.now().strftime(
    "%Y-%m-%d_%H-%M-%S"
)


RAW_FILE = NOTE_DIR / (
    f"{session_name}_강의원문.txt"
)

NOTE_FILE = NOTE_DIR / (
    f"{session_name}_DB강의정리.txt"
)


# ============================================================
# Queue
# ============================================================

# 마이크 데이터 Queue
audio_queue = queue.Queue()

# GUI 업데이트 Queue
gui_queue = queue.Queue()


# AI 정리 전 원문 임시 저장
summary_buffer = []

buffer_lock = threading.Lock()


# ============================================================
# 상태 변수
# ============================================================

running = False

stream = None

current_note = ""


# ============================================================
# Whisper 모델 백그라운드 로딩
# ============================================================

def load_whisper_model():

    global model
    global model_ready

    try:

        print()
        print("=" * 60)
        print("Whisper 모델을 불러오는 중...")
        print("=" * 60)
        print()

        gui_queue.put(
            (
                "status",
                "⏳ Whisper 모델 불러오는 중..."
            )
        )

        model = WhisperModel(
            WHISPER_MODEL,
            device="cpu",
            compute_type="int8",
        )

        model_ready = True

        print("Whisper 모델 준비 완료")
        print()

        gui_queue.put(
            (
                "model_ready",
                None
            )
        )

    except Exception as e:

        model_ready = False

        print(
            "Whisper 모델 로딩 오류:",
            e
        )

        gui_queue.put(
            (
                "message",
                f"Whisper 모델 로딩 실패\n\n{e}"
            )
        )


# ============================================================
# Whisper 이상 문장 제거
# ============================================================

def clean_transcript(text):

    """
    Whisper가 실제 강의 내용이 아닌
    프롬프트성 문장을 출력하는 경우 제거
    """

    unwanted_phrases = [

        "한국어 강의 내용이다",

        "한국어 강의입니다",

        "강사가 설명하는 내용을 정확한 한국어 문장으로 기록한다",

        "강사가 설명하는 내용을 기록한다",

        "전문 용어, 프로그래밍 용어, 영어 단어는 가능한 정확하게 기록한다",

        "전문 용어 프로그래밍 용어 영어 단어는 가능한 정확하게 기록한다",

        "전문 용어는 가능한 정확하게 기록한다",

        "프로그래밍 용어는 가능한 정확하게 기록한다",

        "영어 단어는 가능한 정확하게 기록한다",

        "가능한 정확하게 기록한다",

        "정확하게 기록한다",

    ]

    for phrase in unwanted_phrases:

        text = text.replace(
            phrase,
            ""
        )

    # 공백 정리
    text = " ".join(
        text.split()
    )

    return text.strip()


# ============================================================
# 마이크 Callback
# ============================================================

def audio_callback(
    indata,
    frames,
    time_info,
    status
):

    if status:

        print(
            "마이크 상태:",
            status
        )

    if running:

        audio_queue.put(
            indata.copy()
        )


# ============================================================
# 강의 원문 저장
# ============================================================

def save_raw(text):

    now = datetime.now().strftime(
        "%H:%M:%S"
    )

    with open(
        RAW_FILE,
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            f"[{now}] {text}\n"
        )


# ============================================================
# AI 노트 저장
# ============================================================

def save_note(text):

    with open(
        NOTE_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(text)


# ============================================================
# Ollama 연결 확인
# ============================================================

def ollama_available():

    try:

        response = requests.get(
            "http://localhost:11434",
            timeout=2
        )

        return response.status_code == 200

    except Exception:

        return False


# ============================================================
# Ollama 데이터베이스 강의 정리
# ============================================================

def summarize_with_ollama(
    transcript,
    current_note
):

    prompt = f"""
너는 한국어 데이터베이스 강의를 듣는 학생을 위한
전문 강의 필기 도우미다.

현재 수업은 한국어로 진행되는 데이터베이스 강의이다.

아래에는

1. 현재까지 작성된 강의 노트
2. 새롭게 음성 인식된 강의 내용

이 제공된다.

새로운 강의 내용을 기존 노트에 자연스럽게 반영하여
학생이 나중에 복습하기 좋은 데이터베이스 강의 노트를 작성하라.


============================================================
절대 지켜야 하는 규칙
============================================================

1. 음성 인식 텍스트에 없는 강의 내용을 임의로 만들어내지 않는다.

2. 음성 인식 오류라고 문맥상 확실한 경우에만 수정한다.

3. 문맥이 불확실하면 억지로 내용을 추측하지 않는다.

4. 강사의 말투, 추임새, 반복 표현은 제거한다.

예:

- 자
- 어
- 음
- 그렇죠
- 아시겠죠
- 그래서요
- 이제 보면
- 한번 볼게요
- 그러니까요


============================================================
잘못 인식된 시스템 문장 제거
============================================================

다음과 같은 문장이 들어있다면
강사의 실제 발언이 아니므로 반드시 제거한다.

- 한국어 강의 내용이다
- 한국어 강의입니다
- 정확하게 기록한다
- 가능한 정확하게 기록한다
- 전문 용어를 정확하게 기록한다
- 영어 단어를 정확하게 기록한다
- 프로그래밍 용어를 정확하게 기록한다
- 강사가 설명하는 내용을 기록한다
- 강사가 설명하는 내용을 정확하게 기록한다


============================================================
데이터베이스 전문 용어
============================================================

현재 강의는 데이터베이스 수업이다.

다음과 같은 전문 용어가 등장할 수 있다.

Database
DB
DBMS
RDBMS

SQL

DDL
DML
DCL
TCL

CREATE
ALTER
DROP
TRUNCATE

SELECT
INSERT
UPDATE
DELETE

FROM
WHERE

GROUP BY
HAVING
ORDER BY

DISTINCT

JOIN
INNER JOIN
LEFT JOIN
RIGHT JOIN
OUTER JOIN
CROSS JOIN
SELF JOIN

UNION
UNION ALL

SUBQUERY

PRIMARY KEY
FOREIGN KEY

SUPER KEY
CANDIDATE KEY
ALTERNATE KEY

NULL
NOT NULL
UNIQUE
DEFAULT
CHECK

INDEX
VIEW
SEQUENCE

TRANSACTION
COMMIT
ROLLBACK
SAVEPOINT

ACID

ENTITY
ATTRIBUTE
RELATION
TUPLE
SCHEMA

NORMALIZATION

1NF
2NF
3NF
BCNF

FUNCTIONAL DEPENDENCY

무결성

개체 무결성
참조 무결성
도메인 무결성

기본키
외래키
후보키
슈퍼키
대체키

관계형 데이터베이스

테이블

행
열
레코드
튜플
속성
엔터티

카디널리티
디그리


음성 인식 결과에서 위 전문 용어가
문맥상 확실하게 잘못 인식된 경우에는
올바른 데이터베이스 용어로 수정한다.


============================================================
SQL 처리 규칙
============================================================

강사가 실제 SQL 코드 또는 SQL 문법을 설명했다면
일반 설명과 분리해서 작성한다.

예:

SQL / 명령어

SELECT *
FROM student
WHERE score >= 80;

그리고 아래에 SQL이 어떤 동작을 하는지 설명한다.

실제 강의에서 언급되지 않은 SQL 코드는
임의로 만들어내지 않는다.


============================================================
중요한 내용
============================================================

강사가 다음과 비슷한 표현을 사용했다면
중요한 내용으로 처리한다.

- 중요합니다
- 중요한 부분입니다
- 기억하세요
- 외워두세요
- 시험에 나옵니다
- 시험에 나올 수 있습니다
- 자주 나옵니다
- 자주 사용합니다
- 실무에서 많이 사용합니다
- 반드시 알아야 합니다
- 헷갈리면 안 됩니다

이 경우

★ 중요

표시를 사용한다.


============================================================
노트 작성 형식
============================================================

# 데이터베이스 강의 정리


## 핵심 주제

- 현재 강의의 핵심 주제


## 핵심 개념

### 개념명

- 정의:
- 특징:
- 역할:


필요한 경우

- 장점:
- 단점:
- 사용 목적:

등을 작성한다.


## SQL / 명령어

실제 강의에서 SQL이 언급된 경우에만 작성한다.


## 개념 비교

서로 비교되는 개념이 등장하면
표 또는 보기 쉬운 형식으로 정리한다.


## 강사 설명 / 예시

- 강사가 설명한 실제 예시


## ★ 중요 포인트

- 강사가 강조한 내용
- 시험 관련 내용
- 반드시 기억해야 하는 내용


## 헷갈리기 쉬운 부분

- 서로 혼동하기 쉬운 개념
- 강사가 주의하라고 설명한 부분


## 복습 포인트

- 다시 확인하면 좋은 내용


============================================================
기존 노트 처리 규칙
============================================================

이미 기존 노트에 있는 내용을
불필요하게 반복하지 않는다.

새로운 내용이 기존 개념의 보충 설명이면
기존 항목에 내용을 추가한다.

완전히 새로운 주제라면
새로운 항목을 만든다.

기존에 기록되어 있던 중요한 내용은 삭제하지 않는다.

기존 노트를 지나치게 요약하거나 축약하지 않는다.


============================================================
현재까지 작성된 강의 노트
============================================================

{current_note}


============================================================
새롭게 음성 인식된 강의 내용
============================================================

{transcript}


============================================================

위 내용을 바탕으로
전체 데이터베이스 강의 노트를 작성하라.

노트 내용만 출력한다.

다음과 같은 표현은 출력하지 않는다.

- 알겠습니다
- 정리해드리겠습니다
- 다음은 정리 내용입니다
"""

    try:

        response = requests.post(

            OLLAMA_URL,

            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            },

            timeout=180,
        )

        response.raise_for_status()

        result = response.json()

        return result["response"].strip()

    except Exception as e:

        print(
            "Ollama 요약 오류:",
            e
        )

        return None


# ============================================================
# Whisper 음성 인식 Worker
# ============================================================

def transcription_worker():

    audio_buffer = np.array(
        [],
        dtype=np.float32
    )

    required_samples = (
        SAMPLE_RATE
        * CHUNK_SECONDS
    )

    overlap_samples = (
        SAMPLE_RATE
        * OVERLAP_SECONDS
    )

    while True:

        try:

            audio = audio_queue.get(
                timeout=1
            )

        except queue.Empty:

            continue

        audio = audio.flatten()

        audio_buffer = np.concatenate(
            (
                audio_buffer,
                audio
            )
        )

        # 아직 분석할 만큼 음성이 안 쌓였으면 대기
        if len(audio_buffer) < required_samples:

            continue

        chunk = audio_buffer[
            :required_samples
        ]

        # 마지막 1초 정도 남겨서 다음 구간과 연결
        audio_buffer = audio_buffer[
            required_samples
            - overlap_samples:
        ]

        try:

            # 모델 로딩이 끝나지 않았다면 기다림
            if not model_ready:

                continue

            # ------------------------------------------------
            # 중요:
            #
            # initial_prompt 사용 안 함
            #
            # 프롬프트가 실제 강사 발언으로 인식되는 현상 방지
            # ------------------------------------------------

            segments, info = model.transcribe(

                chunk,

                language="ko",

                task="transcribe",

                beam_size=3,

                vad_filter=True,

                condition_on_previous_text=False,
            )

            text_list = []

            for segment in segments:

                text = segment.text.strip()

                if text:

                    text_list.append(
                        text
                    )

            text = " ".join(
                text_list
            )

            text = clean_transcript(
                text
            )

            if not text:

                continue

            if len(text) <= 1:

                continue

            print(
                "인식:",
                text
            )

            # 원문 저장
            save_raw(
                text
            )

            # AI 정리용 Buffer
            with buffer_lock:

                summary_buffer.append(
                    text
                )

            # GUI 표시
            gui_queue.put(
                (
                    "transcript",
                    text
                )
            )

        except Exception as e:

            print(
                "Whisper 오류:",
                e
            )


# ============================================================
# 자동 AI 정리 Worker
# ============================================================

def summary_worker():

    global current_note

    while True:

        time.sleep(
            SUMMARY_INTERVAL
        )

        with buffer_lock:

            if not summary_buffer:

                continue

            text = " ".join(
                summary_buffer
            )

            summary_buffer.clear()

        # ----------------------------------------------------
        # Ollama 실행 중
        # ----------------------------------------------------

        if ollama_available():

            print()
            print("=" * 60)
            print("AI 강의 노트 정리 중...")
            print("=" * 60)

            result = summarize_with_ollama(

                transcript=text,

                current_note=current_note
            )

            if result:

                current_note = result

                save_note(
                    current_note
                )

                gui_queue.put(
                    (
                        "note",
                        current_note
                    )
                )

                print(
                    "AI 강의 노트 정리 완료"
                )

        # ----------------------------------------------------
        # Ollama 실행 안 됨
        # ----------------------------------------------------

        else:

            now = datetime.now().strftime(
                "%H:%M"
            )

            simple_note = (
                f"\n\n"
                f"## {now} 강의 내용\n\n"
                f"{text}"
            )

            current_note += simple_note

            save_note(
                current_note
            )

            gui_queue.put(
                (
                    "note",
                    current_note
                )
            )

            print(
                "Ollama가 실행되지 않아 "
                "원문 형태로 저장했습니다."
            )


# ============================================================
# 녹음 시작
# ============================================================

def start_recording():

    global running
    global stream

    # Whisper 모델 준비 확인
    if not model_ready:

        messagebox.showinfo(

            "Whisper 준비 중",

            "아직 Whisper 모델을 불러오는 중입니다.\n"
            "모델 준비가 완료된 후 다시 눌러주세요."
        )

        return

    if running:

        return

    try:

        running = True

        stream = sd.InputStream(

            samplerate=SAMPLE_RATE,

            channels=1,

            dtype="float32",

            callback=audio_callback,
        )

        stream.start()

        status_label.config(
            text="● 강의 녹음 중"
        )

        start_button.config(
            state="disabled"
        )

        stop_button.config(
            state="normal"
        )

        print()
        print("강의 녹음을 시작했습니다.")
        print()

    except Exception as e:

        running = False

        messagebox.showerror(
            "마이크 오류",
            str(e)
        )


# ============================================================
# 녹음 정지
# ============================================================

def stop_recording():

    global running
    global stream

    running = False

    if stream:

        try:

            stream.stop()
            stream.close()

        except Exception:

            pass

        stream = None

    # 모델이 준비되어 있으면 다시 시작 가능
    if model_ready:

        status_label.config(
            text="■ 녹음 준비 완료"
        )

        start_button.config(
            state="normal"
        )

    else:

        status_label.config(
            text="⏳ Whisper 모델 불러오는 중..."
        )

    stop_button.config(
        state="disabled"
    )

    print()
    print("강의 녹음을 정지했습니다.")
    print()


# ============================================================
# 지금까지 내용 즉시 AI 정리
# ============================================================

def organize_now():

    threading.Thread(

        target=manual_summary,

        daemon=True

    ).start()


# ============================================================
# 수동 AI 정리
# ============================================================

def manual_summary():

    global current_note

    with buffer_lock:

        if not summary_buffer:

            gui_queue.put(
                (
                    "message",
                    "아직 새롭게 정리할 강의 내용이 없습니다."
                )
            )

            return

        text = " ".join(
            summary_buffer
        )

        summary_buffer.clear()

    # Ollama 실행 여부 확인
    if not ollama_available():

        # 내용 손실 방지를 위해 다시 Buffer에 넣음
        with buffer_lock:

            summary_buffer.append(
                text
            )

        gui_queue.put(
            (
                "message",
                "Ollama가 실행되고 있지 않습니다.\n\n"
                "Ollama를 실행한 뒤 다시 시도해주세요."
            )
        )

        return

    gui_queue.put(
        (
            "status",
            "✨ AI가 강의 내용을 정리하는 중..."
        )
    )

    result = summarize_with_ollama(

        transcript=text,

        current_note=current_note
    )

    if result:

        current_note = result

        save_note(
            current_note
        )

        gui_queue.put(
            (
                "note",
                current_note
            )
        )

        if running:

            gui_queue.put(
                (
                    "status",
                    "● 강의 녹음 중"
                )
            )

        else:

            gui_queue.put(
                (
                    "status",
                    "■ 녹음 준비 완료"
                )
            )

    else:

        # AI 실패 시 내용 다시 저장
        with buffer_lock:

            summary_buffer.append(
                text
            )

        gui_queue.put(
            (
                "message",
                "AI 정리에 실패했습니다.\n"
                "Ollama 상태를 확인해주세요."
            )
        )


# ============================================================
# GUI Queue 처리
# ============================================================

def update_gui():

    try:

        while True:

            event, data = gui_queue.get_nowait()

            # ------------------------------------------------
            # 실시간 전사
            # ------------------------------------------------

            if event == "transcript":

                now = datetime.now().strftime(
                    "%H:%M:%S"
                )

                transcript_box.insert(

                    tk.END,

                    f"[{now}] {data}\n\n"
                )

                transcript_box.see(
                    tk.END
                )

            # ------------------------------------------------
            # AI 정리 노트
            # ------------------------------------------------

            elif event == "note":

                note_box.delete(
                    "1.0",
                    tk.END
                )

                note_box.insert(
                    tk.END,
                    data
                )

                note_box.see(
                    tk.END
                )

            # ------------------------------------------------
            # 상태 표시
            # ------------------------------------------------

            elif event == "status":

                status_label.config(
                    text=data
                )

            # ------------------------------------------------
            # Whisper 모델 준비 완료
            # ------------------------------------------------

            elif event == "model_ready":

                status_label.config(
                    text="■ Whisper 준비 완료 / 녹음 가능"
                )

                start_button.config(
                    state="normal"
                )

            # ------------------------------------------------
            # 팝업 메시지
            # ------------------------------------------------

            elif event == "message":

                messagebox.showinfo(
                    "알림",
                    data
                )

    except queue.Empty:

        pass

    # 300ms마다 다시 확인
    root.after(
        300,
        update_gui
    )


# ============================================================
# 프로그램 종료
# ============================================================

def on_close():

    stop_recording()

    root.destroy()


# ============================================================
# GUI 생성
# ============================================================

print("GUI 생성 시작")


root = tk.Tk()


print("GUI 생성 완료")


root.title(
    "AI 데이터베이스 강의 필기 도우미"
)


root.geometry(
    "1500x850"
)


root.minsize(
    1000,
    600
)


# ============================================================
# 제목
# ============================================================

title = tk.Label(

    root,

    text="AI 데이터베이스 강의 필기 도우미",

    font=(
        "맑은 고딕",
        22,
        "bold"
    )

)

title.pack(
    pady=10
)


# ============================================================
# 상태 표시
# ============================================================

status_label = tk.Label(

    root,

    text="⏳ Whisper 모델 불러오는 중...",

    font=(
        "맑은 고딕",
        12
    )

)

status_label.pack(
    pady=5
)


# ============================================================
# 버튼 영역
# ============================================================

button_frame = tk.Frame(
    root
)

button_frame.pack(
    pady=10
)


# ------------------------------------------------------------
# 녹음 시작
# ------------------------------------------------------------

start_button = tk.Button(

    button_frame,

    text="🎙 강의 녹음 시작",

    font=(
        "맑은 고딕",
        12
    ),

    command=start_recording,

    width=18,

    # Whisper 준비 완료 후 활성화
    state="disabled"
)

start_button.pack(

    side=tk.LEFT,

    padx=5
)


# ------------------------------------------------------------
# 녹음 정지
# ------------------------------------------------------------

stop_button = tk.Button(

    button_frame,

    text="⏹ 녹음 정지",

    font=(
        "맑은 고딕",
        12
    ),

    command=stop_recording,

    width=15,

    state="disabled"
)

stop_button.pack(

    side=tk.LEFT,

    padx=5
)


# ------------------------------------------------------------
# 즉시 AI 정리
# ------------------------------------------------------------

summary_button = tk.Button(

    button_frame,

    text="✨ 지금까지 내용 정리",

    font=(
        "맑은 고딕",
        12
    ),

    command=organize_now,

    width=20
)

summary_button.pack(

    side=tk.LEFT,

    padx=5
)


# ============================================================
# 저장 위치 표시
# ============================================================

save_path_label = tk.Label(

    root,

    text=f"저장 위치: {NOTE_DIR}",

    font=(
        "맑은 고딕",
        9
    )
)

save_path_label.pack(
    pady=3
)


# ============================================================
# 본문
# ============================================================

main_frame = tk.Frame(
    root
)

main_frame.pack(

    fill=tk.BOTH,

    expand=True,

    padx=10,

    pady=10
)


# ============================================================
# 왼쪽 - 실시간 강의 원문
# ============================================================

left_frame = tk.Frame(
    main_frame
)

left_frame.pack(

    side=tk.LEFT,

    fill=tk.BOTH,

    expand=True,

    padx=5
)


tk.Label(

    left_frame,

    text="실시간 강의 원문",

    font=(
        "맑은 고딕",
        14,
        "bold"
    )

).pack(
    pady=5
)


transcript_box = scrolledtext.ScrolledText(

    left_frame,

    wrap=tk.WORD,

    font=(
        "맑은 고딕",
        11
    )
)

transcript_box.pack(

    fill=tk.BOTH,

    expand=True
)


# ============================================================
# 오른쪽 - AI 정리
# ============================================================

right_frame = tk.Frame(
    main_frame
)

right_frame.pack(

    side=tk.RIGHT,

    fill=tk.BOTH,

    expand=True,

    padx=5
)


tk.Label(

    right_frame,

    text="AI 데이터베이스 강의 정리",

    font=(
        "맑은 고딕",
        14,
        "bold"
    )

).pack(
    pady=5
)


note_box = scrolledtext.ScrolledText(

    right_frame,

    wrap=tk.WORD,

    font=(
        "맑은 고딕",
        11
    )
)

note_box.pack(

    fill=tk.BOTH,

    expand=True
)


# ============================================================
# GUI Queue 감시 시작
# ============================================================

update_gui()


# ============================================================
# 프로그램 창부터 먼저 화면에 표시
# ============================================================

root.update_idletasks()


# ============================================================
# Worker Thread 시작
# ============================================================

# ------------------------------------------------------------
# Whisper 모델 로딩 Thread
# ------------------------------------------------------------

threading.Thread(

    target=load_whisper_model,

    daemon=True

).start()


# ------------------------------------------------------------
# 음성 인식 Thread
# ------------------------------------------------------------

threading.Thread(

    target=transcription_worker,

    daemon=True

).start()


# ------------------------------------------------------------
# AI 자동 정리 Thread
# ------------------------------------------------------------

threading.Thread(

    target=summary_worker,

    daemon=True

).start()


# ============================================================
# 창 종료 이벤트
# ============================================================

root.protocol(

    "WM_DELETE_WINDOW",

    on_close
)


# ============================================================
# GUI 실행
# ============================================================

print("GUI mainloop 시작")


root.mainloop()


print("프로그램 종료")