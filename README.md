# 🌾 Agri Chatbot

Agri Chatbot is an AI-powered assistant designed to help farmers decide **which crops to grow**, based on their **location**, **season**, **rainfall**, and more. It uses **RAG (Retrieval-Augmented Generation)** to provide relevant responses by combining your question with real agricultural data.

> ❗ This chatbot only answers **agriculture-related** questions.

---

## 🧠 Features

- 💬 Ask farming-related questions like:
  - *“What are the top 2 crops to grow in Nagpur during monsoon?”*
  - *“Suggest crops based on 500mm rainfall and loamy soil.”*
- 📍 If a **location** is mentioned, the chatbot gives suggestions specific to that area.
- 🌦️ It considers **season, rainfall, soil**, and **climate** if included in the question.
- 🧠 Uses a **RAG pipeline** to fetch relevant crop data and then passes it to the **LLM (LLaMA 3 via Groq)**.
- 📂 Uses a **simple keyword-based database** built from crop text data.

---

## 🛠️ Tech Stack

| Layer        | Technology                  |
|--------------|------------------------------|
| Frontend     | HTML, CSS, JavaScript        |
| Backend      | Python (Flask/FastAPI ready) |
| AI Model     | LLaMA3 via Groq API          |
| Retrieval    | RAG using simple keyword DB  |
| Storage      | Local JSON-based DB          |

---

## 🖼️ Sample Chatbot UI

### 🔘 Homepage with Quick Questions
![Screenshot (16)](https://github.com/user-attachments/assets/acfc6d0e-f194-441f-bf23-7603209266eb)


### 📩 Response Based on Location and Rainfall
![Screenshot (14)](https://github.com/user-attachments/assets/df748a38-68bb-475a-aa48-1437da51c1bc)


### 📋 Crop Details and Growing Tips
![Screenshot (15)](https://github.com/user-attachments/assets/f6858301-75f0-452d-8d2a-b662064b62de)


---

## ▶️ Getting Started

1. Make sure your crop data is ready in `crop_recommendation_rag_text.txt`
2. Run this to prepare your DB:
   ```bash
   python prepare_data.py
   ```
3. Start your app (Flask/FastAPI):
   ```bash
   python app.py
   ```
4. Open your frontend and chat with the bot!

---

## 📌 Notes

- The chatbot won't reply to non-agriculture questions.
- Location is only used if clearly mentioned in the query.
- The app works **offline** for database search but needs **internet** to call the LLM API.
- Easy to customize and extend with more crop data.

---

## 🙌 Credits

Made for helping farmers avoid losses by growing crops suited for their area and climate.
