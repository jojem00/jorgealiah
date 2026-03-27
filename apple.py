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
            data = json.load(f)
    else:
        data = {}

    # Ensure all top-level keys exist
    data.setdefault("notes", [])
    data.setdefault("dates", [])
    data.setdefault("timeline", [])
    data.setdefault("photos", [])
    data.setdefault("voices", [])
    data.setdefault("letters", [])
    data.setdefault("bucket_list", [])

    # Backfill missing fields on existing items
    for note in data["notes"]:
        note.setdefault("favourited", False)
        note.setdefault("pinned", False)
    for photo in data["photos"]:
        if isinstance(photo, dict):
            photo.setdefault("favourited", False)
    for voice in data["voices"]:
        if isinstance(voice, dict):
            voice.setdefault("favourited", False)
    for letter in data["letters"]:
        letter.setdefault("favourited", False)

    return data

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def main():
    st.title("jorge & aliah💕")

    data = load_data()

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Photos", "Notes", "Voice Messages", "Timeline",
        "💌 Love Letters", "🪣 Bucket List", "Shuffle Memory"
    ])

    # ─── PHOTOS ───────────────────────────────────────────────
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
                    data['photos'].append({"name": uploaded_file.name, "data": encoded, "favourited": False})
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
                if isinstance(photo, str):
                    if os.path.exists(photo):
                        st.image(photo, caption=f"Photo {i+1}")
                else:
                    decoded = base64.b64decode(photo['data'])
                    fav_icon = "❤️" if photo.get("favourited") else "🤍"
                    st.image(decoded, caption=photo['name'])
                    col_fav, col_del = st.columns(2)
                    with col_fav:
                        if st.button(fav_icon, key=f"fav_photo_{i}"):
                            data['photos'][i]['favourited'] = not photo.get("favourited", False)
                            save_data(data)
                            st.rerun()
                    with col_del:
                        if st.button("Delete", key=f"del_photo_{i}"):
                            data['photos'].pop(i)
                            save_data(data)
                            st.rerun()

    # ─── NOTES ────────────────────────────────────────────────
    with tab2:
        st.header("Notes")
        new_note = st.text_area("Add a new note")
        if st.button("Add Note"):
            if new_note:
                data['notes'].append({
                    "text": new_note,
                    "date": str(datetime.now()),
                    "favourited": False,
                    "pinned": False
                })
                save_data(data)
                st.success("Note added!")
                st.rerun()

        st.subheader("Your Notes")

        # Pinned notes first, then the rest in original order
        notes_sorted = sorted(enumerate(data['notes']), key=lambda x: not x[1].get('pinned', False))

        for i, note in notes_sorted:
            pin_icon = "📌" if note.get("pinned") else "📍"
            fav_icon = "❤️" if note.get("favourited") else "🤍"
            pin_label = " 📌 Pinned" if note.get("pinned") else ""

            st.write(f"**{note['date']}**{pin_label}")

            if st.session_state.get("edit_note_index") == i:
                edited_text = st.text_area("Edit note", value=note['text'], key=f"edit_area_note_{i}")
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.button("Save", key=f"save_note_{i}"):
                        data['notes'][i]['text'] = edited_text
                        save_data(data)
                        st.session_state.pop("edit_note_index", None)
                        st.rerun()
                with col_cancel:
                    if st.button("Cancel", key=f"cancel_note_{i}"):
                        st.session_state.pop("edit_note_index", None)
                        st.rerun()
            else:
                st.write(note['text'])
                col_fav, col_pin, col_edit, col_del = st.columns(4)
                with col_fav:
                    if st.button(fav_icon, key=f"fav_note_{i}"):
                        data['notes'][i]['favourited'] = not note.get("favourited", False)
                        save_data(data)
                        st.rerun()
                with col_pin:
                    if st.button(pin_icon, key=f"pin_note_{i}"):
                        data['notes'][i]['pinned'] = not note.get("pinned", False)
                        save_data(data)
                        st.rerun()
                with col_edit:
                    if st.button("✏️", key=f"edit_note_{i}"):
                        st.session_state["edit_note_index"] = i
                        st.rerun()
                with col_del:
                    if st.button("Delete", key=f"del_note_{i}"):
                        data['notes'].pop(i)
                        save_data(data)
                        st.rerun()

            st.divider()

    # ─── VOICE MESSAGES ───────────────────────────────────────
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
                    data['voices'].append({
                        "name": uploaded_voice.name,
                        "data": encoded,
                        "date": str(datetime.now()),
                        "favourited": False
                    })
                    save_data(data)
                    st.success("Voice message uploaded!")
            else:
                st.warning("Choose a voice file first.")

        st.subheader("Voice Messages")
        for i, voice in reversed(list(enumerate(data['voices']))):
            if isinstance(voice, dict) and 'data' in voice:
                decoded = base64.b64decode(voice['data'])
                st.audio(decoded, format='audio/mp3')
                st.write(f"Uploaded on: {voice['date']}")
            elif isinstance(voice, dict) and 'path' in voice:
                if os.path.exists(voice['path']):
                    st.audio(voice['path'], format='audio/mp3')
                    st.write(f"Uploaded on: {voice['date']}")

            fav_icon = "❤️" if voice.get("favourited") else "🤍"
            col_fav, col_del = st.columns(2)
            with col_fav:
                if st.button(fav_icon, key=f"fav_voice_{i}"):
                    data['voices'][i]['favourited'] = not voice.get("favourited", False)
                    save_data(data)
                    st.rerun()
            with col_del:
                if st.button("Delete", key=f"del_voice_{i}"):
                    data['voices'].pop(i)
                    save_data(data)
                    st.rerun()
            st.divider()

    # ─── TIMELINE ─────────────────────────────────────────────
    with tab4:
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
        timeline_sorted = sorted(enumerate(data['timeline']), key=lambda x: x[1]['date'])
        for i, event in timeline_sorted:
            if st.session_state.get("edit_timeline_index") == i:
                new_date = st.date_input(
                    "Edit date",
                    value=datetime.strptime(event['date'], "%Y-%m-%d").date(),
                    key=f"edit_tdate_{i}"
                )
                new_desc = st.text_area("Edit description", value=event['desc'], key=f"edit_tdesc_{i}")
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.button("Save", key=f"save_timeline_{i}"):
                        data['timeline'][i]['date'] = str(new_date)
                        data['timeline'][i]['desc'] = new_desc
                        save_data(data)
                        st.session_state.pop("edit_timeline_index", None)
                        st.rerun()
                with col_cancel:
                    if st.button("Cancel", key=f"cancel_timeline_{i}"):
                        st.session_state.pop("edit_timeline_index", None)
                        st.rerun()
            else:
                st.write(f"**{event['date']}**: {event['desc']}")
                col_edit, col_del = st.columns(2)
                with col_edit:
                    if st.button("✏️", key=f"edit_timeline_{i}"):
                        st.session_state["edit_timeline_index"] = i
                        st.rerun()
                with col_del:
                    if st.button("Delete", key=f"del_timeline_{i}"):
                        for j, orig in enumerate(data['timeline']):
                            if orig == event:
                                data['timeline'].pop(j)
                                save_data(data)
                                st.rerun()
                                break
            st.divider()

    # ─── LOVE LETTERS ─────────────────────────────────────────
    with tab5:
        st.header("💌 Love Letters")
        sender = st.text_input("From", placeholder="Your name")
        letter_body = st.text_area("Write your letter...")
        if st.button("Send Letter 💌"):
            if sender and letter_body:
                data['letters'].append({
                    "from": sender,
                    "text": letter_body,
                    "date": str(datetime.now()),
                    "favourited": False
                })
                save_data(data)
                st.success("Letter sent! 💕")
                st.rerun()
            else:
                st.warning("Fill in both your name and the letter first.")

        st.subheader("Letters")
        for i, letter in reversed(list(enumerate(data['letters']))):
            fav_icon = "❤️" if letter.get("favourited") else "🤍"
            with st.container():
                st.markdown(f"""
<div style="background-color:#fff0f3;border-radius:12px;padding:16px;margin-bottom:8px;border:1px solid #ffb3c1;">
<strong>💌 From {letter['from']}</strong> &nbsp;&nbsp; <small>{letter['date']}</small>
<hr style="border:none;border-top:1px solid #ffb3c1;margin:8px 0;">
{letter['text']}
</div>
""", unsafe_allow_html=True)
                col_fav, col_del = st.columns(2)
                with col_fav:
                    if st.button(fav_icon, key=f"fav_letter_{i}"):
                        data['letters'][i]['favourited'] = not letter.get("favourited", False)
                        save_data(data)
                        st.rerun()
                with col_del:
                    if st.button("Delete", key=f"del_letter_{i}"):
                        data['letters'].pop(i)
                        save_data(data)
                        st.rerun()

    # ─── BUCKET LIST ──────────────────────────────────────────
    with tab6:
        st.header("🪣 Bucket List")
        new_item = st.text_input("Add something to your bucket list")
        if st.button("Add ✨"):
            if new_item:
                data['bucket_list'].append({
                    "text": new_item,
                    "done": False,
                    "date": str(datetime.now())
                })
                save_data(data)
                st.success("Added to your bucket list!")
                st.rerun()
            else:
                st.warning("Type something first!")

        st.subheader("Your List")
        not_done = [(i, item) for i, item in enumerate(data['bucket_list']) if not item.get('done')]
        done_items = [(i, item) for i, item in enumerate(data['bucket_list']) if item.get('done')]

        for i, item in not_done + done_items:
            if item.get('done'):
                st.markdown(f"~~{item['text']}~~")
                check_label = "✅"
            else:
                st.write(item['text'])
                check_label = "⬜"

            col_check, col_del = st.columns(2)
            with col_check:
                if st.button(check_label, key=f"check_bucket_{i}"):
                    data['bucket_list'][i]['done'] = not item.get('done', False)
                    save_data(data)
                    st.rerun()
            with col_del:
                if st.button("Delete", key=f"del_bucket_{i}"):
                    data['bucket_list'].pop(i)
                    save_data(data)
                    st.rerun()
            st.divider()

    # ─── SHUFFLE MEMORY ───────────────────────────────────────
    with tab7:
        st.header("Shuffle Memory")
        if st.button("Shuffle!"):
            all_memories = []
            for photo in data['photos']:
                all_memories.append({"type": "photo", "content": photo})
            for note in data['notes']:
                all_memories.append({"type": "note", "content": note})
            for voice in data['voices']:
                all_memories.append({"type": "voice", "content": voice})
            for event in data['timeline']:
                all_memories.append({"type": "timeline", "content": event})
            for letter in data['letters']:
                all_memories.append({"type": "letter", "content": letter})

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
                elif memory['type'] == 'timeline':
                    st.write(f"Timeline Event: {memory['content']['date']} - {memory['content']['desc']}")
                elif memory['type'] == 'letter':
                    st.write(f"💌 Letter from {memory['content']['from']}: {memory['content']['text']}")
                    st.write(f"Date: {memory['content']['date']}")
            else:
                st.write("No memories yet!")

if __name__ == "__main__":
    main()