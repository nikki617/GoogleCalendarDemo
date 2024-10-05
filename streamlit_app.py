import streamlit as st
from calendar_integration import CalendarIntegration

def main():
    st.title("Google Calendar Integration App")

    calendar_service = CalendarIntegration()
    
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
    else:
        st.error("Failed to create Google Calendar service.")

if __name__ == "__main__":
    main()
