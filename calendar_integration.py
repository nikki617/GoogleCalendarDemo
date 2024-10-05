# Create the GoogleCalendar.
calendar = GoogleCalendar(credentials=credentials)

#------- 
### Event listing tool

# Parameters needed to look for an event
class GetEventargs(BaseModel):
    from_datetime: datetime = Field(description="beginning of date range to retrieve events")
    to_datetime: datetime = Field(description="end of date range to retrieve events")

# Define the tool 
def get_events(from_datetime, to_datetime):
    # Ensure that the current year is used by default
    current_year = datetime.now().year
    from_datetime = from_datetime.replace(year=current_year)
    to_datetime = to_datetime.replace(year=current_year)
    
    events = calendar.get_events(calendar_id="nikki617@bu.edu", time_min=from_datetime, time_max=to_datetime)
    return list(events)

# Create a Tool object 
list_event_tool = StructuredTool(
    name="GetEvents",
    func=get_events,
    args_schema=GetEventargs,
    description="Useful for getting the list of events from the user's calendar."
)

#------------

### Event adding tool

# Parameters needed to add an event
class AddEventargs(BaseModel):
    start_date_time: datetime = Field(description="start date and time of event")
    length_hours: int = Field(description="length of event")
    event_name: str = Field(description="name of the event")

# Define the tool 
def add_event(start_date_time, length_hours, event_name):
    # Ensure the current year is used
    current_year = datetime.now().year
    start_date_time = start_date_time.replace(year=current_year)
    start = start_date_time
    end = start + length_hours * hours
    event = Event(event_name,
                  start=start,
                  end=end)
    return calendar.add_event(event, calendar_id="nikki617@bu.edu")

# Create a Tool object 
add_event_tool = StructuredTool(
    name="AddEvent",
    func=add_event,
    args_schema=AddEventargs,
    description="Useful for adding an event with a start date, event name, and length in hours."
)

#------------

## Update this list with the new tools
tools = [list_event_tool, add_event_tool]

#-----------
