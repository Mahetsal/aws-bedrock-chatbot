/**
 * AWS Bedrock Chatbot — Frontend Logic
 * Handles user interaction, API communication, and UI updates.
 */

const API_BASE = window.location.origin;
let sessionId = null;

const messagesContainer = document.getElementById("chat-messages");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const newSessionBtn = document.getElementById("new-session-btn");

// Auto-resize textarea
userInput.addEventListener("input", function () {
    this.style.height = "auto";
    this.style.height = Math.min(this.scrollHeight, 120) + "px";
});

// Send on Enter (Shift+Enter for new line)
userInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

sendBtn.addEventListener("click", sendMessage);
newSessionBtn.addEventListener("click", startNewSession);

function appendMessage(role, content) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${role}`;

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";
    contentDiv.textContent = content;

    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showTypingIndicator() {
    const indicator = document.createElement("div");
    indicator.className = "message assistant";
    indicator.id = "typing-indicator";
    indicator.innerHTML = `
        <div class="message-content">
            <div class="typing-indicator">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;
    messagesContainer.appendChild(indicator);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById("typing-indicator");
    if (indicator) indicator.remove();
}

async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    // Disable input while processing
    userInput.value = "";
    userInput.style.height = "auto";
    sendBtn.disabled = true;

    // Show user message
    appendMessage("user", message);
    showTypingIndicator();

    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: message,
                session_id: sessionId,
            }),
        });

        const data = await response.json();
        removeTypingIndicator();

        if (response.ok) {
            sessionId = data.session_id;
            appendMessage("assistant", data.response);
        } else {
            appendMessage("assistant", `Error: ${data.error || "Something went wrong"}`);
        }
    } catch (error) {
        removeTypingIndicator();
        appendMessage("assistant", "Connection error. Please check if the server is running.");
    }

    sendBtn.disabled = false;
    userInput.focus();
}

function startNewSession() {
    sessionId = null;
    messagesContainer.innerHTML = "";
    appendMessage("assistant", "Hello! I'm an AI assistant powered by Amazon Bedrock. How can I help you today?");
    userInput.focus();
  }
