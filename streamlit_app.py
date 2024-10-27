import streamlit as st
import openai
import re

# 페이지 설정
st.set_page_config(page_title="Travel Planner Chatbot", layout="wide")

# 제목과 설명
st.title("🌍 여행 계획 챗봇")
st.write(
    "이 챗봇은 개인 맞춤형 여행 일정을 제공합니다. "
    "다양한 목적지와 여행 기간을 선택하고 추가 정보를 입력해보세요."
)

# OpenAI API 키 입력
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("OpenAI API 키를 입력해주세요.", icon="🗝️")
else:
    openai.api_key = openai_api_key  # API 키 설정

# 세션 상태 변수 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "destination" not in st.session_state:
    st.session_state.destination = None
if "stay_duration" not in st.session_state:
    st.session_state.stay_duration = None
if "itinerary_generated" not in st.session_state:
    st.session_state.itinerary_generated = False
if "itinerary" not in st.session_state:
    st.session_state.itinerary = ""

# 두 개의 열로 구성된 레이아웃 생성
col1, col2 = st.columns([1, 1])

with col1:

    with st.chat_message("assistant"):
        response = st.markdown(
            "안녕하세요 여행자님! 여행자님의 계획 생성을 도와줄 리포입니다."
        )

    # 도시 선택 체크박스 UI
    with st.chat_message("assistant"):
        st.write("어느 도시를 여행하고 싶으신가요? 아래에서 도시를 선택해주세요.")
        cities = ["오사카", "파리", "방콕", "뉴욕"]

        for city in cities:
            if st.checkbox(city, key=f"city_{city}"):
                st.session_state.destination = city

    # 여행 기간 선택 체크박스 UI
    if st.session_state.destination:
        with st.chat_message("assistant"):
            st.write("언제 여행을 떠날 예정인가요? 여행 일자를 선택해주세요!")

            durations = ["1박 2일", "2박 3일", "3박 4일"]
            for duration in durations:
                if st.checkbox(duration, key=f"duration_{duration}"):
                    st.session_state.stay_duration = duration

            # 여행 계획 생성: 도시와 기간이 선택된 경우
            if st.session_state.destination and st.session_state.stay_duration:
                if not st.session_state.itinerary_generated:
                    try:
                        with st.spinner("여행 일정을 생성하는 중입니다..."):
                            itinerary_request = (
                                f"Create a very detailed {st.session_state.stay_duration} itinerary for a trip to "
                                f"{st.session_state.destination}. Include recommendations for breakfast, lunch, and dinner for each day. "
                                f"Please answer with Korean."
                            )
                            response = openai.chat.completions.create(
                                model="gpt-3.5-turbo",
                                messages=[
                                    {"role": "user", "content": itinerary_request}
                                ],
                            )
                            st.session_state.itinerary = response.choices[
                                0
                            ].message.content
                            # st.session_state.messages.append(
                            #     {
                            #         "role": "assistant",
                            #         "content": st.session_state.itinerary,
                            #     }
                            # )
                            st.session_state.itinerary_generated = True
                    except Exception as e:
                        st.error(f"여행 일정 생성 중 오류가 발생했습니다: {e}")

    # # Display the existing chat messages via `st.chat_message`.
    # for message in st.session_state.messages:
    #     with st.chat_message(message["role"]):
    #         st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message. This will display
    # automatically at the bottom of the page.
    # 채팅 입력 처리

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("여행 기간을 입력하거나 질문해보세요."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 정규 표현식으로 'X박 Y일' 패턴 감지
        match = re.match(r"(\d+)박\s*(\d+)일", prompt)

        if match:
            st.session_state.stay_duration = f"{match.group(1)}박 {match.group(2)}일"
            # st.session_state.messages.append(
            #     {
            #         "role": "user",
            #         "content": f"여행 기간은 {st.session_state.stay_duration}입니다.",
            #     }
            # )

            # 여행 계획 생성 (조건 만족 시에만 생성)
            if st.session_state.destination and st.session_state.stay_duration:
                itinerary_request = (
                    f"Create a detailed {st.session_state.stay_duration} itinerary for a trip to "
                    f"{st.session_state.destination}. Include recommendations for breakfast, lunch, and dinner for each day. "
                    f"Please answer with Korean."
                )

                if not st.session_state.itinerary_generated:
                    try:
                        with st.spinner("여행 일정을 생성하는 중입니다..."):
                            response = openai.chat.completions.create(
                                model="gpt-3.5-turbo",
                                messages=[
                                    {"role": "user", "content": itinerary_request}
                                ],
                            )

                            st.session_state.itinerary = response.choices[
                                0
                            ].message.content
                            st.session_state.messages.append(
                                {
                                    "role": "assistant",
                                    "content": st.session_state.itinerary,
                                }
                            )
                            st.session_state.itinerary_generated = True

                    except Exception as e:
                        st.error(f"여행 일정 생성 중 오류가 발생했습니다: {e}")

        else:
            # 일반 메시지에 대한 응답 처리
            stream = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            with st.chat_message("assistant"):
                response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})

with col2:
    # 일정이 있는 경우에만 표시
    if st.session_state.itinerary:
        st.subheader("🗺️ 여행 일정")

        # 일정 텍스트를 줄 단위로 분리
        itinerary_lines = st.session_state.itinerary.splitlines()
        days = [
            line
            for line in itinerary_lines
            if line.lower().startswith("day") or "일차" in line
        ]

        # 선택된 day에 맞는 내용을 표시하기 위한 변수
        selected_day_content = ""

        if days:
            # 버튼들을 가로로 나열하기 위해 열 생성
            button_columns = st.columns(len(days))  # 일자별로 열 생성

            # 각 버튼을 해당 열에 배치
            for i, day in enumerate(days):
                with button_columns[i]:
                    if st.button(day.strip(), key=f"button_{i}"):
                        # 해당 일자에 맞는 일정만 추출하여 표시
                        start_index = itinerary_lines.index(day)
                        end_index = (
                            itinerary_lines.index(days[i + 1])
                            if i + 1 < len(days)
                            else len(itinerary_lines)
                        )
                        selected_day_content = "\n".join(
                            itinerary_lines[start_index:end_index]
                        )

            # 선택된 일자에 해당하는 내용을 col2에 꽉 차게 표시
            if selected_day_content:
                st.write("### 선택한 일정")
                st.markdown(selected_day_content)

        else:
            st.write("일정에 표시할 날짜가 없습니다. 전체 일정을 확인하세요:")
            st.write(st.session_state.itinerary)
