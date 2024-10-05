import streamlit as st
from calendar_integration import CalendarIntegration
from llm_integration import LLMIntegration  # updated import statement

def main():
    st.title("Google Calendar Integration App")

    calendar_service = CalendarIntegration()
    llm_service = LLMIntegration()  # updated instantiation
    
    if calendar_service.credentials:
        st.success("Google Calendar service created successfully.")
        
        st.subheader("Upcoming Events:")
        events = calendar_service.list_events()
        
        if events:
            for event in events:
                event_time = event['start'].get('dateTime', event['start'].get('date'))
                st.write(f"{event_time} - {event.get('summary', 'No Title')}")
        else:
            st.write("No upcoming events found.")

        # Chat with LLM (OpenAI)
        st.subheader("Ask the LLM")
        user_input = st.text_input("What would you like to ask the LLM?")
        
        if st.button("Get Response"):
            if user_input:
                llm_response = llm_service.generate_response(user_input)  # updated method call
                if llm_response:
                    st.write("LLM Response:")
                    st.write(llm_response)
            else:
                st.warning("Please enter a question for the LLM.")

    else:
        st.error("Failed to create Google Calendar service.")

if __name__ == "__main__":
    main()
