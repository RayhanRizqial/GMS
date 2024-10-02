async function sendMessage() {
  const inputField = document.querySelector('input[type="text"]');
  const sendButton = document.querySelector("button");
  const userMessage = inputField.value;
  const assistantId = "asst_fLNZN6AOHhOjYCk9dXktdboS"; // ID asisten
  let threadId = localStorage.getItem("thread_id"); // Ambil thread_id dari local storage

  // Nonaktifkan input dan tombol kirim saat mengirim pesan
  inputField.disabled = true;
  sendButton.disabled = true;

  // Tambahkan pesan pengguna ke chat
  const chatMessages = document.querySelector(".chat-messages");
  const userMessageDiv = document.createElement("div");
  userMessageDiv.className = "message from-me";
  userMessageDiv.innerHTML = `<div class="message-bubble">${userMessage}</div>`;
  chatMessages.appendChild(userMessageDiv);

  // Tambahkan indikator loading untuk respons GPT
  const gptMessageDiv = document.createElement("div");
  gptMessageDiv.className = "message from-them";
  gptMessageDiv.innerHTML = `<div class="message-bubble">
                                <div class="loading-indicator">
                                  <span class="dot"></span>
                                  <span class="dot"></span>
                                  <span class="dot"></span>
                                </div>
                              </div>`;
  chatMessages.appendChild(gptMessageDiv);

  // Scroll ke bawah untuk menunjukkan pesan terbaru
  chatMessages.scrollTop = chatMessages.scrollHeight;

  try {
    // Kirim pesan ke server untuk mendapatkan respons dan ekspresi
    const response = await fetch("/send-message/exp", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        user_message: userMessage,
        assistant_id: assistantId,
        thread_id: threadId || "", // Pass threadId if available
      }),
    });

    const data = await response.json();
    const gptMessage = data.response;
    const expression = data.expression;

    // Ganti indikator loading dengan respons GPT
    gptMessageDiv.querySelector(".message-bubble").innerHTML = `<div class="from-them">${gptMessage}</div>`;

    // Update gambar ekspresi chatbot
    const chatbotImage = document.querySelector(".agen img");
    chatbotImage.src = `/static/images/${expression}`;
    
    // Simpan thread_id yang baru jika ada
    if (data.thread_id) {
      localStorage.setItem("thread_id", data.thread_id);
    }
  } catch (error) {
    console.error("Error:", error);
  } finally {
    // Aktifkan kembali input dan tombol kirim
    inputField.disabled = false;
    sendButton.disabled = false;

    // Hapus teks di input field
    inputField.value = "";

    // Scroll ke bawah untuk menunjukkan pesan terbaru
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Fokus pada input field
    inputField.focus();
  }
}

// Mencegah pengiriman ganda
let isSending = false;

document.addEventListener("DOMContentLoaded", () => {
  const sendButton = document.querySelector("button");
  const inputField = document.querySelector('input[type="text"]');

  inputField.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !isSending) {
      event.preventDefault();
      isSending = true;
      sendMessage().then(() => (isSending = false));
    }
  });

  sendButton.addEventListener("click", () => {
    if (!isSending) {
      isSending = true;
      sendMessage().then(() => (isSending = false));
    }
  });
});
