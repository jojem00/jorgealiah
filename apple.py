import streamlit as st
import json
import os
import random
from datetime import datetime

DATA_FILE = 'data.json'
PHOTOS_DIR = 'uploads/photos'
VOICES_DIR = 'uploads/voices'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"notes": [], "dates": [], "timeline": [], "photos": [], "voices": []}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def main():
    st.title("jorge & aliah💕")

    data = load_data()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Photos", "Notes", "Voice Messages", "Important Dates", "Timeline", "Shuffle Memory"])

    with tab1:
        st.header("Photos")
        uploaded_files = st.file_uploader("Upload photos", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
        if uploaded_files:
            for uploaded_file in uploaded_files:
                file_path = os.path.join(PHOTOS_DIR, uploaded_file.name)
                with open(file_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                if file_path not in data['photos']:
                    data['photos'].append(file_path)
            save_data(data)
            st.success("Photos uploaded!")

        cols = st.columns(3)
        for i, photo in enumerate(data['photos']):
            if os.path.exists(photo):
                cols[i % 3].image(photo, caption=f"Photo {i+1}")

    with tab2:
        st.header("Notes")
        new_note = st.text_area("Add a new note")
        if st.button("Add Note"):
            if new_note:
                data['notes'].append({"text": new_note, "date": str(datetime.now())})
                save_data(data)
                st.success("Note added!")
                st.rerun()

        st.subheader("Your Notes")
        for note in reversed(data['notes']):
            st.write(f"**{note['date']}**: {note['text']}")
            st.divider()

    with tab3:
        st.header("Voice Messages")
        uploaded_voice = st.file_uploader("Upload voice message", type=['mp3', 'wav', 'm4a'])
        if uploaded_voice:
            file_path = os.path.join(VOICES_DIR, uploaded_voice.name)
            with open(file_path, 'wb') as f:
                f.write(uploaded_voice.getbuffer())
            data['voices'].append({"path": file_path, "name": uploaded_voice.name, "date": str(datetime.now())})
            save_data(data)
            st.success("Voice message uploaded!")

        st.subheader("Voice Messages")
        for voice in reversed(data['voices']):
            if os.path.exists(voice['path']):
                st.audio(voice['path'], format='audio/mp3')
                st.write(f"Uploaded on: {voice['date']}")
                st.divider()

    with tab4:
        st.header("Important Dates")
        date = st.date_input("Date")
        desc = st.text_input("Description")
        if st.button("Add Date"):
            if desc:
                data['dates'].append({"date": str(date), "desc": desc})
                save_data(data)
                st.success("Date added!")
                st.rerun()

        st.subheader("Important Dates")
        for d in sorted(data['dates'], key=lambda x: x['date']):
            st.write(f"**{d['date']}**: {d['desc']}")

    with tab5:
        st.header("Relationship Timeline")
        event_date = st.date_input("Event Date", key="timeline_date")
        event_desc = st.text_area("Event Description", key="timeline_desc")
        if st.button("Add Event"):
            if event_desc:
                data['timeline'].append({"date": str(event_date), "desc": event_desc})
                save_data(data)
                st.success("Event added!")
                st.rerun()

        st.subheader("Timeline")
        for event in sorted(data['timeline'], key=lambda x: x['date']):
            st.write(f"**{event['date']}**: {event['desc']}")
            st.divider()

    with tab6:
        st.header("Shuffle Memory")
        if st.button("Shuffle!"):
            all_memories = []
            for photo in data['photos']:
                all_memories.append({"type": "photo", "path": photo})
            for note in data['notes']:
                all_memories.append({"type": "note", "content": note})
            for voice in data['voices']:
                all_memories.append({"type": "voice", "content": voice})
            for date in data['dates']:
                all_memories.append({"type": "date", "content": date})
            for event in data['timeline']:
                all_memories.append({"type": "timeline", "content": event})

            if all_memories:
                memory = random.choice(all_memories)
                st.subheader("Random Memory:")
                if memory['type'] == 'photo':
                    st.image(memory['path'])
                elif memory['type'] == 'note':
                    st.write(f"Note: {memory['content']['text']}")
                    st.write(f"Date: {memory['content']['date']}")
                elif memory['type'] == 'voice':
                    st.audio(memory['content']['path'])
                    st.write(f"Voice from: {memory['content']['date']}")
                elif memory['type'] == 'date':
                    st.write(f"Important Date: {memory['content']['date']} - {memory['content']['desc']}")
                elif memory['type'] == 'timeline':
                    st.write(f"Timeline Event: {memory['content']['date']} - {memory['content']['desc']}")
            else:
                st.write("No memories yet!")

if __name__ == "__main__":
    main()