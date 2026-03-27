import streamlit as st
import json
import os
import random
import base64
import subprocess
from datetime import datetime

DATA_FILE = 'data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"notes": [], "dates": [], "timeline": [], "photos": [], "voices": []}

def commit_and_push():
    """Commit and push changes to GitHub"""
    try:
        subprocess.run(['git', 'add', DATA_FILE], check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Update data'], check=True, capture_output=True)
        subprocess.run(['git', 'push'], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        # Silently fail if git operations fail (e.g., no changes to commit)
        pass
    except Exception:
        pass

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)
    commit_and_push()

def main():
    st.title("jorge & aliah💕")

    data = load_data()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Photos", "Notes", "Voice Messages", "Important Dates", "Timeline", "Shuffle Memory"])

    with tab1:
        st.header("Photos")
        uploaded_files = st.file_uploader("Upload photos", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
        if uploaded_files:
            for uploaded_file in uploaded_files:
                image_data = uploaded_file.getvalue()
                encoded = base64.b64encode(image_data).decode('utf-8')
                data['photos'].append({"name": uploaded_file.name, "data": encoded})
            save_data(data)
            st.success("Photos uploaded!")

        cols = st.columns(3)
        for i, photo in enumerate(data['photos']):
            with cols[i % 3]:
                if isinstance(photo, str):  # old path
                    if os.path.exists(photo):
                        st.image(photo, caption=f"Photo {i+1}")
                else:  # new dict
                    decoded = base64.b64decode(photo['data'])
                    st.image(decoded, caption=photo['name'])
                
                if st.button("🗑️ Delete", key=f"delete_photo_{i}"):
                    data['photos'].pop(i)
                    save_data(data)
                    st.rerun()

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
        for i, note in enumerate(reversed(data['notes'])):
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.write(f"**{note['date']}**: {note['text']}")
            with col2:
                if st.button("🗑️", key=f"delete_note_{i}"):
                    data['notes'].pop(len(data['notes']) - 1 - i)
                    save_data(data)
                    st.rerun()
            st.divider()

    with tab3:
        st.header("Voice Messages")
        uploaded_voice = st.file_uploader("Upload voice message", type=['mp3', 'wav', 'm4a'])
        if uploaded_voice:
            audio_data = uploaded_voice.getvalue()
            encoded = base64.b64encode(audio_data).decode('utf-8')
            data['voices'].append({"name": uploaded_voice.name, "data": encoded, "date": str(datetime.now())})
            save_data(data)
            st.success("Voice message uploaded!")

        st.subheader("Voice Messages")
        for i, voice in enumerate(reversed(data['voices'])):
            if isinstance(voice, dict) and 'data' in voice:
                decoded = base64.b64decode(voice['data'])
                st.audio(decoded, format='audio/mp3')
                col1, col2 = st.columns([0.9, 0.1])
                with col1:
                    st.write(f"Uploaded on: {voice['date']}")
                with col2:
                    if st.button("🗑️", key=f"delete_voice_{i}"):
                        data['voices'].pop(len(data['voices']) - 1 - i)
                        save_data(data)
                        st.rerun()
            elif isinstance(voice, dict) and 'path' in voice:
                if os.path.exists(voice['path']):
                    st.audio(voice['path'], format='audio/mp3')
                    col1, col2 = st.columns([0.9, 0.1])
                    with col1:
                        st.write(f"Uploaded on: {voice['date']}")
                    with col2:
                        if st.button("🗑️", key=f"delete_voice_path_{i}"):
                            data['voices'].pop(len(data['voices']) - 1 - i)
                            save_data(data)
                            st.rerun()
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
        for i, d in enumerate(sorted(data['dates'], key=lambda x: x['date'])):
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.write(f"**{d['date']}**: {d['desc']}")
            with col2:
                if st.button("🗑️", key=f"delete_date_{i}"):
                    data['dates'].remove(d)
                    save_data(data)
                    st.rerun()

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
        for i, event in enumerate(sorted(data['timeline'], key=lambda x: x['date'])):
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.write(f"**{event['date']}**: {event['desc']}")
            with col2:
                if st.button("🗑️", key=f"delete_timeline_{i}"):
                    data['timeline'].remove(event)
                    save_data(data)
                    st.rerun()
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