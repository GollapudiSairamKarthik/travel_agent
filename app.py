# app.py
import streamlit as st
from main_graph import get_supervisor
from langchain_core.messages import AIMessage, HumanMessage

st.set_page_config(page_title="Agentic Travel Planner", layout="wide")

st.title("Agentic Travel Planner")

city = st.text_input("City (e.g. Hyderabad)", "Hyderabad")
start_date = st.text_input("Start date", "2025/10/02")
end_date = st.text_input("End date", "2025/10/04")
daily_limit = st.number_input("POIs per day", min_value=1, max_value=10, value=3)

if st.button("Plan Trip"):
    with st.spinner("Planning trip..."):
        supervisor = get_supervisor()
        state = supervisor.invoke({
            "messages": [
                {"role": "user", "content": f"I want a trip plan to {city} from {start_date} to {end_date}. Provide weather, POIs and itinerary with daily limit {daily_limit}."}
            ]
        })

        msgs = state.get("messages", [])

        # ✅ Extract only the final AI message (not tool calls)
        final_msg = None
        for m in reversed(msgs):  # iterate backwards
            if isinstance(m, AIMessage):
                final_msg = m.content
                break
            elif isinstance(m, dict) and m.get("role") == "assistant":
                final_msg = m.get("content")
                break

        if final_msg:
            st.markdown("## Result")
            st.markdown(final_msg)
        else:
            st.error("No final itinerary generated. Please check logs.")
