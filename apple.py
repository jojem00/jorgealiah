import streamlit as st
import json
import os
import random
import base64
from datetime import datetime

DATA_FILE = 'data.json'

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
        uploaded_files = st.file_uploader(
            "Upload photos",
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            key="photo_uploader"
        )
        if st.button("Save Uploaded Photos", key="save_uploaded_photos"):
            if uploaded_files:
                existing_photo_data = {
                    photo['data']
                    for photo in data['photos']
                    if isinstance(photo, dict) and 'data' in photo
                }
                added_count = 0
                for uploaded_file in uploaded_files:
                    image_data = uploaded_file.getvalue()
                    encoded = base64.b64encode(image_data).decode('utf-8')
                    if encoded in existing_photo_data:
                        continue
                    data['photos'].append({"name": uploaded_file.name, "data": encoded})
                    existing_photo_data.add(encoded)
                    added_count += 1

                if added_count > 0:
                    save_data(data)
                    st.success(f"Added {added_count} photo(s)!")
                else:
                    st.info("Those photos are already in your memories.")
            else:
                st.warning("Choose at least one photo first.")

        cols = st.columns(3)
        for i, photo in enumerate(data['photos']):
            with cols[i % 3]:
                if isinstance(photo, str):  # old path
                    if os.path.exists(photo):
                        st.image(photo, caption=f"Photo {i+1}")
                else:  # new dict
                    decoded = base64.b64decode(photo['data'])
                    st.image(decoded, caption=photo['name'])
                if st.button("Delete", key=f"del_photo_{i}"):
                    data['photos'].pop(i)
                    save_data(data)
                    st.experimental_rerun()

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
        notes_with_index = list(enumerate(data['notes']))
        for i, note in reversed(notes_with_index):
            st.write(f"**{note['date']}**: {note['text']}")
            if st.button("Delete", key=f"del_note_{i}"):
                data['notes'].pop(i)
                save_data(data)
                st.experimental_rerun()
            st.divider()

    with tab3:
        st.header("Voice Messages")
        uploaded_voice = st.file_uploader(
            "Upload voice message",
            type=['mp3', 'wav', 'm4a'],
            key="voice_uploader"
        )
        if st.button("Save Voice Message", key="save_uploaded_voice"):
            if uploaded_voice:
                audio_data = uploaded_voice.getvalue()
                encoded = base64.b64encode(audio_data).decode('utf-8')
                existing_voice_data = {
                    voice['data']
                    for voice in data['voices']
                    if isinstance(voice, dict) and 'data' in voice
                }

                if encoded in existing_voice_data:
                    st.info("That voice message is already saved.")
                else:
                    data['voices'].append({"name": uploaded_voice.name, "data": encoded, "date": str(datetime.now())})
                    save_data(data)
                    st.success("Voice message uploaded!")
            else:
                st.warning("Choose a voice file first.")

        st.subheader("Voice Messages")
        voices_with_index = list(enumerate(data['voices']))
        for i, voice in reversed(voices_with_index):
            if isinstance(voice, dict) and 'data' in voice:
                decoded = base64.b64decode(voice['data'])
                st.audio(decoded, format='audio/mp3')
                st.write(f"Uploaded on: {voice['date']}")
            elif isinstance(voice, dict) and 'path' in voice:
                if os.path.exists(voice['path']):
                    st.audio(voice['path'], format='audio/mp3')
                    st.write(f"Uploaded on: {voice['date']}")
            if st.button("Delete", key=f"del_voice_{i}"):
                data['voices'].pop(i)
                save_data(data)
                st.experimental_rerun()
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
        dates_with_index = list(enumerate(sorted(data['dates'], key=lambda x: x['date'])))
        for i, d in dates_with_index:
            st.write(f"**{d['date']}**: {d['desc']}")
            if st.button("Delete", key=f"del_date_{i}"):
                # locate and remove by exact date/desc match to handle sorted index
                for j, orig in enumerate(data['dates']):
                    if orig == d:
                        data['dates'].pop(j)
                        save_data(data)
                        st.experimental_rerun()
                        break
            st.divider()

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
        timeline_with_index = list(enumerate(sorted(data['timeline'], key=lambda x: x['date'])))
        for i, event in timeline_with_index:
            st.write(f"**{event['date']}**: {event['desc']}")
            if st.button("Delete", key=f"del_timeline_{i}"):
                for j, orig in enumerate(data['timeline']):
                    if orig == event:
                        data['timeline'].pop(j)
                        save_data(data)
                        st.experimental_rerun()
                        break
            st.divider()

    with tab6:
        st.header("Shuffle Memory")
        if st.button("Shuffle!"):
            all_memories = []
            for photo in data['photos']:
                all_memories.append({"type": "photo", "content": photo})
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
                    if isinstance(memory['content'], str):
                        if os.path.exists(memory['content']):
                            st.image(memory['content'])
                    else:
                        decoded = base64.b64decode(memory['content']['data'])
                        st.image(decoded, caption=memory['content']['name'])
                elif memory['type'] == 'note':
                    st.write(f"Note: {memory['content']['text']}")
                    st.write(f"Date: {memory['content']['date']}")
                elif memory['type'] == 'voice':
                    if isinstance(memory['content'], dict) and 'data' in memory['content']:
                        decoded = base64.b64decode(memory['content']['data'])
                        st.audio(decoded)
                        st.write(f"Voice from: {memory['content']['date']}")
                    elif isinstance(memory['content'], dict) and 'path' in memory['content']:
                        if os.path.exists(memory['content']['path']):
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