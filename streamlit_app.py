# 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

import streamlit as st
import openai

# Set up the page configuration
st.set_page_config(page_title="Travel Planner Chatbot", layout="wide")

# Title and description
st.title("🌍 Travel Planner Chatbot")
st.write(
    "This chatbot helps you plan your trips with personalized itineraries. "
    "Feel free to interact and explore different destinations and durations."
)

# User API key input
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    openai.api_key = openai_api_key  # Set the API key

# Initialize session state variables
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

# Create a two-column layout
col1, col2 = st.columns([1, 1])

with col1:
    # Step 1: Select Travel Destination
    st.subheader("Step 1: Select Your Travel Destination")
    destination = st.radio(
        "Choose your destination:",
        options=[None, "Paris", "Tokyo", "New York"],
        format_func=lambda x: "Select a destination" if x is None else x,
    )

    # Update the selected destination in session state
    if destination and destination != st.session_state.destination:
        st.session_state.destination = destination
        st.session_state.messages.append(
            {"role": "user", "content": f"I am planning a trip to {destination}."}
        )
        st.session_state.itinerary_generated = False

    # Step 2: Select Stay Duration (Only if destination is selected)
    if st.session_state.destination:
        st.subheader(
            f"Step 2: Select the Duration of Your Trip to {st.session_state.destination}"
        )
        stay_duration = st.radio(
            "Choose your stay duration:",
            options=[None, "1 night 2 days", "2 nights 3 days", "3 nights 4 days"],
            format_func=lambda x: "Select a duration" if x is None else x,
        )

        if stay_duration and stay_duration != st.session_state.stay_duration:
            st.session_state.stay_duration = stay_duration
            st.session_state.messages.append(
                {"role": "user", "content": f"My trip will last {stay_duration}."}
            )
            st.session_state.itinerary_generated = False

    # Generate itinerary immediately when both destination and duration are provided
    if st.session_state.destination and st.session_state.stay_duration:
        itinerary_request = (
            f"Create a detailed {st.session_state.stay_duration} itinerary for "
            f"a trip to {st.session_state.destination}. Include recommendations for "
            f"breakfast, lunch, and dinner for each day."
        )

        if not st.session_state.itinerary_generated:
            try:
                with st.spinner("Generating itinerary..."):
                    response = openai.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": itinerary_request}],
                    )

                    st.session_state.itinerary = response.choices[0].message.content

                    st.session_state.messages.append(
                        {"role": "assistant", "content": st.session_state.itinerary}
                    )
                    st.session_state.itinerary_generated = True

            except Exception as e:
                st.error(f"An error occurred while generating the itinerary: {e}")

    # Handle additional input to modify the itinerary
    if st.session_state.itinerary:
        if prompt := st.chat_input("Add more details or modify your trip:"):
            if prompt.strip():
                st.session_state.messages.append({"role": "user", "content": prompt})

                custom_request = (
                    f"Create a detailed {st.session_state.stay_duration} itinerary for "
                    f"a trip to {st.session_state.destination}. Include recommendations for "
                    f"breakfast, lunch, and dinner for each day."
                    f"However, if {st.session_state.messages} asks you to change your itinerary or destination to a new one, please modify travel plan accordingly. And the revised travel plan should be made in the format of breakfast, lunch, and dinner for every day."
                )

                try:
                    with st.spinner("Updating itinerary..."):
                        response = openai.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role": "user", "content": custom_request}],
                        )

                        # Update the itinerary with the new response
                        response_text = response.choices[0].message.content
                        st.session_state.itinerary = response_text
                        st.session_state.messages.append(
                            {"role": "assistant", "content": response_text}
                        )

                except Exception as e:
                    st.error(f"An error occurred while updating the itinerary: {e}")

with col2:
    # Display the itinerary with day-wise buttons
    if st.session_state.itinerary:
        st.subheader("🗺️ Your Travel Itinerary")

        # Split the itinerary by day (assuming each day starts with "Day X")
        itinerary_lines = st.session_state.itinerary.splitlines()
        days = [line for line in itinerary_lines if line.lower().startswith("day")]

        if days:
            # Create buttons for each day
            day_buttons = st.columns(len(days))

            for i, day in enumerate(days):
                with day_buttons[i]:
                    if st.button(day.strip()):  # Button for each day
                        start_index = itinerary_lines.index(day)
                        end_index = (
                            itinerary_lines.index(days[i + 1])
                            if i + 1 < len(days)
                            else len(itinerary_lines)
                        )
                        day_content = "\n".join(itinerary_lines[start_index:end_index])
                        st.write(day_content)
        else:
            st.write("No days found in the itinerary. Please try again.")
