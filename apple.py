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

def ensure_replies(data):
    """Ensure all items have replies array for backwards compatibility"""
    for photo in data.get('photos', []):
        if isinstance(photo, dict) and 'replies' not in photo:
            photo['replies'] = []
    for note in data.get('notes', []):
        if 'replies' not in note:
            note['replies'] = []
    for voice in data.get('voices', []):
        if 'replies' not in voice:
            voice['replies'] = []
    for date in data.get('dates', []):
        if 'replies' not in date:
            date['replies'] = []
    for event in data.get('timeline', []):
        if 'replies' not in event:
            event['replies'] = []
    return data

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

def reply_form_open(key):
    return st.session_state.get(f"show_{key}", False)

def toggle_reply_form(key):
    state_key = f"show_{key}"
    st.session_state[state_key] = not st.session_state.get(state_key, False)

def main():
    st.title("jorge & aliah💕")

    data = load_data()
    data = ensure_replies(data)

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Photos", "Notes", "Voice Messages", "Timeline",
        "💌 Love Letters", "🪣 Bucket List", "Shuffle Memory"
    ])

    # ─── PHOTOS ───────────────────────────────────────────────
    with tab1:
        st.header("Photos")
        uploaded_files = st.file_uploader("Upload photos", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
        if uploaded_files:
            for uploaded_file in uploaded_files:
                image_data = uploaded_file.getvalue()
                encoded = base64.b64encode(image_data).decode('utf-8')
                data['photos'].append({"name": uploaded_file.name, "data": encoded, "replies": []})
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
                
                col_del, col_reply = st.columns(2)
                with col_del:
                    if st.button("🗑️", key=f"delete_photo_{i}"):
                        data['photos'].pop(i)
                        save_data(data)
                        st.rerun()
                with col_reply:
                    if st.button("💬", key=f"reply_photo_button_{i}"):
                        toggle_reply_form(f"reply_photo_{i}")
                
                if reply_form_open(f"reply_photo_{i}"):
                    reply_text = st.text_input("Add a reply", key=f"reply_input_photo_{i}")
                    if st.button("Send Reply", key=f"send_reply_photo_{i}"):
                        if reply_text:
                            photo['replies'].append({"text": reply_text, "date": str(datetime.now())})
                            save_data(data)
                            st.rerun()
                
                if photo.get('replies', []):
                    st.caption("Replies:")
                    for j, reply in enumerate(photo['replies']):
                        col1, col2 = st.columns([0.85, 0.15])
                        with col1:
                            st.write(f"💭 {reply['text']}")
                            st.caption(f"_{reply['date']}_")
                        with col2:
                            if st.button("🗑️", key=f"delete_reply_photo_{i}_{j}"):
                                photo['replies'].pop(j)
                                save_data(data)
                                st.rerun()

    # ─── NOTES ────────────────────────────────────────────────
    with tab2:
        st.header("Notes")
        new_note = st.text_area("Add a new note")
        if st.button("Add Note"):
            if new_note:
                data['notes'].append({"text": new_note, "date": str(datetime.now()), "replies": []})
                save_data(data)
                st.success("Note added!")
                st.rerun()

        st.subheader("Notes")
        for i, note in enumerate(reversed(data['notes'])):
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.write(f"**{note['date']}**: {note['text']}")
            with col2:
                if st.button("🗑️", key=f"delete_note_{i}"):
                    data['notes'].pop(len(data['notes']) - 1 - i)
                    save_data(data)
                    st.rerun()
            
            note_idx = len(data['notes']) - 1 - i
            col_reply, col_space = st.columns([0.15, 0.85])
            with col_reply:
                if st.button("💬", key=f"reply_note_button_{i}"):
                    toggle_reply_form(f"reply_note_{i}")
            
            if reply_form_open(f"reply_note_{i}"):
                reply_text = st.text_input("Add a reply", key=f"reply_input_note_{i}")
                if st.button("Send Reply", key=f"send_reply_note_{i}"):
                    if reply_text:
                        data['notes'][note_idx]['replies'].append({"text": reply_text, "date": str(datetime.now())})
                        save_data(data)
                        st.rerun()
            
            if data['notes'][note_idx].get('replies', []):
                st.caption("Replies:")
                for j, reply in enumerate(data['notes'][note_idx]['replies']):
                    col1, col2 = st.columns([0.85, 0.15])
                    with col1:
                        st.write(f"💭 {reply['text']}")
                        st.caption(f"_{reply['date']}_")
                    with col2:
                        if st.button("🗑️", key=f"delete_reply_note_{i}_{j}"):
                            data['notes'][note_idx]['replies'].pop(j)
                            save_data(data)
                            st.rerun()
            st.divider()

    # ─── VOICE MESSAGES ───────────────────────────────────────
    with tab3:
        st.header("Voice Messages")
        uploaded_voice = st.file_uploader("Upload voice message", type=['mp3', 'wav', 'm4a'])
        if uploaded_voice:
            audio_data = uploaded_voice.getvalue()
            encoded = base64.b64encode(audio_data).decode('utf-8')
            data['voices'].append({"name": uploaded_voice.name, "data": encoded, "date": str(datetime.now()), "replies": []})
            save_data(data)
            st.success("Voice message uploaded!")

        st.subheader("Voice Messages")
        for i, voice in enumerate(reversed(data['voices'])):
            voice_idx = len(data['voices']) - 1 - i
            if isinstance(voice, dict) and 'data' in voice:
                decoded = base64.b64decode(voice['data'])
                st.audio(decoded, format='audio/mp3')
                col1, col2, col3 = st.columns([0.8, 0.1, 0.1])
                with col1:
                    st.write(f"Uploaded on: {voice['date']}")
                with col2:
                    if st.button("💬", key=f"reply_voice_button_{i}"):
                        toggle_reply_form(f"reply_voice_{i}")
                with col3:
                    if st.button("🗑️", key=f"delete_voice_{i}"):
                        data['voices'].pop(voice_idx)
                        save_data(data)
                        st.rerun()
                
                if reply_form_open(f"reply_voice_{i}"):
                    reply_text = st.text_input("Add a reply", key=f"reply_input_voice_{i}")
                    if st.button("Send Reply", key=f"send_reply_voice_{i}"):
                        if reply_text:
                            data['voices'][voice_idx]['replies'].append({"text": reply_text, "date": str(datetime.now())})
                            save_data(data)
                            st.rerun()
                
                if data['voices'][voice_idx].get('replies', []):
                    st.caption("Replies:")
                    for j, reply in enumerate(data['voices'][voice_idx]['replies']):
                        col1, col2 = st.columns([0.85, 0.15])
                        with col1:
                            st.write(f"💭 {reply['text']}")
                            st.caption(f"_{reply['date']}_")
                        with col2:
                            if st.button("🗑️", key=f"delete_reply_voice_{i}_{j}"):
                                data['voices'][voice_idx]['replies'].pop(j)
                                save_data(data)
                                st.rerun()
            elif isinstance(voice, dict) and 'path' in voice:
                if os.path.exists(voice['path']):
                    st.audio(voice['path'], format='audio/mp3')
                    col1, col2, col3 = st.columns([0.8, 0.1, 0.1])
                    with col1:
                        st.write(f"Uploaded on: {voice['date']}")
                    with col2:
                        if st.button("💬", key=f"reply_voice_path_button_{i}"):
                            toggle_reply_form(f"reply_voice_path_{i}")
                    with col3:
                        if st.button("🗑️", key=f"delete_voice_path_{i}"):
                            data['voices'].pop(voice_idx)
                            save_data(data)
                            st.rerun()
                    
                    if reply_form_open(f"reply_voice_path_{i}"):
                        reply_text = st.text_input("Add a reply", key=f"reply_input_voice_path_{i}")
                        if st.button("Send Reply", key=f"send_reply_voice_path_{i}"):
                            if reply_text:
                                data['voices'][voice_idx]['replies'].append({"text": reply_text, "date": str(datetime.now())})
                                save_data(data)
                                st.rerun()
                    
                    if data['voices'][voice_idx].get('replies', []):
                        st.caption("Replies:")
                        for j, reply in enumerate(data['voices'][voice_idx]['replies']):
                            col1, col2 = st.columns([0.85, 0.15])
                            with col1:
                                st.write(f"💭 {reply['text']}")
                                st.caption(f"_{reply['date']}_")
                            with col2:
                                if st.button("🗑️", key=f"delete_reply_voice_path_{i}_{j}"):
                                    data['voices'][voice_idx]['replies'].pop(j)
                                    save_data(data)
                                    st.rerun()
            st.divider()

    # ─── TIMELINE ─────────────────────────────────────────────
    with tab4:
        st.header("Important Dates")
        date = st.date_input("Date")
        desc = st.text_input("Description")
        if st.button("Add Date"):
            if desc:
                data['dates'].append({"date": str(date), "desc": desc, "replies": []})
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
            
            col_reply, col_space = st.columns([0.15, 0.85])
            with col_reply:
                if st.button("💬", key=f"reply_date_button_{i}"):
                    toggle_reply_form(f"reply_date_{i}")
            
            if reply_form_open(f"reply_date_{i}"):
                reply_text = st.text_input("Add a reply", key=f"reply_input_date_{i}")
                if st.button("Send Reply", key=f"send_reply_date_{i}"):
                    if reply_text:
                        d['replies'].append({"text": reply_text, "date": str(datetime.now())})
                        save_data(data)
                        st.rerun()
            
            if d.get('replies', []):
                st.caption("Replies:")
                for j, reply in enumerate(d['replies']):
                    col1, col2 = st.columns([0.85, 0.15])
                    with col1:
                        st.write(f"💭 {reply['text']}")
                        st.caption(f"_{reply['date']}_")
                    with col2:
                        if st.button("🗑️", key=f"delete_reply_date_{i}_{j}"):
                            d['replies'].pop(j)
                            save_data(data)
                            st.rerun()
            st.divider()

    with tab5:
        st.header("Relationship Timeline")
        event_date = st.date_input("Event Date", key="timeline_date")
        event_desc = st.text_area("Event Description", key="timeline_desc")
        if st.button("Add Event"):
            if event_desc:
                data['timeline'].append({"date": str(event_date), "desc": event_desc, "replies": []})
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
            
            col_reply, col_space = st.columns([0.15, 0.85])
            with col_reply:
                if st.button("💬", key=f"reply_timeline_button_{i}"):
                    toggle_reply_form(f"reply_timeline_{i}")
            
            if reply_form_open(f"reply_timeline_{i}"):
                reply_text = st.text_input("Add a reply", key=f"reply_input_timeline_{i}")
                if st.button("Send Reply", key=f"send_reply_timeline_{i}"):
                    if reply_text:
                        event['replies'].append({"text": reply_text, "date": str(datetime.now())})
                        save_data(data)
                        st.rerun()
            
            if event.get('replies', []):
                st.caption("Replies:")
                for j, reply in enumerate(event['replies']):
                    col1, col2 = st.columns([0.85, 0.15])
                    with col1:
                        st.write(f"💭 {reply['text']}")
                        st.caption(f"_{reply['date']}_")
                    with col2:
                        if st.button("🗑️", key=f"delete_reply_timeline_{i}_{j}"):
                            event['replies'].pop(j)
                            save_data(data)
                            st.rerun()
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