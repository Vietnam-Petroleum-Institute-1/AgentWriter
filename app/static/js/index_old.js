let isConversationStarted = false;
let isWaitingForBot = false; // New flag to indicate waiting for bot response
let conversationIdPromise = null;
let feedbackMessageId = null;

window.onload = function () {
  console.log("Window loaded");
  const urlParams = new URLSearchParams(window.location.search);
  const user_id = urlParams.get("user_id");
  const session_id = urlParams.get("session_id");
  console.log("User ID:", user_id, "Session ID:", session_id);

  fetch("/api/user_exist", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ user_id}),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("User existence check:", data);
      if (data.result) {
        conversationIdPromise = checkOrCreateSession(user_id, session_id);
      } else {
        document.getElementById("chatMessages").innerHTML =
          '<div class="message bot"><div class="message-content">Vui lòng đăng nhập để sử dụng trợ lý ảo</div></div>';
        const chatInput = document.querySelector(".chat-input");
        if (chatInput) {
          chatInput.style.display = "none";
        }
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
};

function checkOrCreateSession(user_id, session_id) {
  console.log("Checking or creating session");
  showWaitingBubble();
  return fetch("/api/session_exist", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ user_id, session_id }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Session existence check:", data);
      if (data.result === 1) {
        document.getElementById("chatContainer").style.display = "flex";
        return getConversation(user_id, session_id); // Return the promise from getConversation
      } else if (data.result === 0) {
        const currentDate = new Date();
        const start_time = new Date(currentDate.getTime() + 7 * 60 * 60 * 1000).toISOString();
        const end_time = new Date(currentDate.getTime() + 7 * 60 * 60 * 1000 + 60 * 60 * 1000).toISOString();
        return createSession(user_id, session_id, start_time, end_time);
      } else {
        document.getElementById("chatMessages").innerHTML =
          '<div class="message bot"><div class="message-content">Vui lòng đăng nhập để sử dụng trợ lý ảo</div></div>';
        const chatInput = document.querySelector(".chat-input");
        if (chatInput) {
          chatInput.style.display = "none";
        }
      }
    })
    .catch((error) => {
      console.error("Error in checkOrCreateSession:", error);
      throw error;
    })
    .finally(() => {
      hideWaitingBubble();
    });
}

function createSession(user_id, session_id, start_time, end_time) {
  console.log("Creating session");
  showWaitingBubble();
  return fetch("/api/session", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ user_id, session_id, start_time, end_time }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Session creation result:", data);
      document.getElementById("chatContainer").style.display = "flex";
      return startConversation(user_id, session_id); // Return the promise from startConversation
    })
    .catch((error) => {
      console.error("Error in createSession:", error);
      throw error;
    })
    .finally(() => {
      hideWaitingBubble();
    });
}

function startConversation(user_id, session_id) {
  console.log("Starting conversation");
  showWaitingBubble();
  return fetch("/api/start_conversation", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ user_id, session_id }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Start conversation result:", data);
      const conversation_id = data.conversation_id;
      sessionStorage.setItem("conversation_id", conversation_id);

      const userInput = document.getElementById("userInput");
      const sendButton = document.getElementById("sendButton");
      if (userInput && sendButton) {
        userInput.disabled = false;
        sendButton.disabled = false;
      }

      isConversationStarted = true; // Set flag to true once conversation is started
      console.log("Conversation started, conversation_id:", conversation_id);

      // // Gửi tin nhắn tự động
      addMessageToChat("bot", "Xin chào, rất vui được hỗ trợ bạn");

      return conversation_id;
    })
    .catch((error) => {
      console.error("Error in startConversation:", error);
      document.getElementById("chatMessages").innerHTML +=
        '<div class="message bot"><div class="message-content">Sorry, something went wrong while starting the conversation.</div></div>';
      throw error;
    })
    .finally(() => {
      hideWaitingBubble();
    });
}

function getConversation(user_id, session_id) {
  console.log("Getting conversation");
  showWaitingBubble();
  return fetch("/api/conversation_id", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ user_id, session_id }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Conversation ID:", data.result);
      sessionStorage.setItem("conversation_id", data.result);

      const userInput = document.getElementById("userInput");
      const sendButton = document.getElementById("sendButton");
      if (userInput && sendButton) {
        userInput.disabled = false;
        sendButton.disabled = false;
      }

      isConversationStarted = true; // Set flag to true once conversation ID is obtained
      return data.result;
    })
    .catch((error) => {
      console.error("Error in getConversation:", error);
      throw error;
    })
    .finally(() => {
      hideWaitingBubble();
    });
}

function handleKeyPress(event) {
  if (event.key === "Enter" && !isWaitingForBot && isConversationStarted) {
    sendMessage();
  }
}

function sendMessage(message = null) {
  if (!isConversationStarted || isWaitingForBot) {
    console.log(
      "Conversation has not started yet or still waiting for bot response."
    );
    return;
  }

  const userInput = document.getElementById("userInput");
  const messageText = message || userInput.value.trim();
  if (messageText === "") {
    return;
  }
  const urlParams = new URLSearchParams(window.location.search);
  const user_id = urlParams.get("user_id");
  const session_id = urlParams.get("session_id");
  const conversation_id = sessionStorage.getItem("conversation_id");

  if (!conversation_id) {
    console.error("Error: conversation_id is undefined before sending message");
    return;
  }

  addMessageToChat(message ? "bot" : "user", messageText, null);

  if (!message) {
    userInput.value = "";
  }
  isWaitingForBot = true; // Set flag to true while waiting for bot response
  addWaitingBubble(); // Add waiting bubble

  // Set a timeout to show the "waiting" message if the response takes too long
  const delayMessageTimeout = setTimeout(() => {
    removeWaitingBubble();
    addMessageToChat("bot", "Chờ chút nhé, tôi đang tổng hợp lại câu trả lời cho bạn đây.");
    addWaitingBubble()
  }, 4000);

  fetch(
    `/api/message?text=${encodeURIComponent(
      messageText
    )}&user_id=${encodeURIComponent(user_id)}&session_id=${encodeURIComponent(
      session_id
    )}&conversation_id=${encodeURIComponent(conversation_id)}`
  )
    .then((response) => response.json())
    .then((data) => {
      clearTimeout(delayMessageTimeout); // Clear the timeout as the response has arrived
      console.log("Message sent:", data);
      removeWaitingBubble(); // Remove waiting bubble
      processBotResponse(data.result, data.message_id, messageText, user_id); // Process the bot's response
      isWaitingForBot = false; // Set flag to false after receiving response
    })
    .catch((error) => {
      clearTimeout(delayMessageTimeout); // Clear the timeout in case of error
      console.error("Error:", error);
      removeWaitingBubble(); // Remove waiting bubble
      addMessageToChat("bot", "Sorry, something went wrong.");
      isWaitingForBot = false; // Set flag to false after error
    });
}


function processBotResponse(result, messageId, messageText, user_id) {
  // Check if response ends with "Domain 1", "Domain 2", "Domain 3", or "Domain 4"
  const domainMatch = result.match(/Domain (1|2|3|4)$/);
  console.log("Đây là domainMatch", domainMatch);
  if (domainMatch) {
    const domain = `Domain ${domainMatch[1]}`;

    // Remove the last occurrence of "Domain X" from result
    const resultWithoutDomain = result.replace(/Domain (1|2|3|4)$/, "").trim();

    // Add message to chat without the domain part
    addMessageToChat("bot", resultWithoutDomain, messageId);
    
    // Call uploadPendingFAQ
    uploadPendingFAQ(resultWithoutDomain, messageText, domain, user_id);
  } else {
    // Add message to chat as is
    addMessageToChat("bot", result, messageId);
  }
}

function uploadPendingFAQ(answer, question, domain, user_id) {
  fetch("/api/upload_pending_FAQ", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question: question,
      answer: answer, // Assuming answer is the same as question for simplicity
      domain: domain,
      user_id: user_id, // Adjust as needed
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Success:", data);
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

function addMessageToChat(sender, message, messageId) {
  const chatMessages = document.getElementById("chatMessages");

  const messageElement = document.createElement("div");
  messageElement.classList.add("message", sender);
  if (messageId) {
    messageElement.dataset.messageId = messageId; // Lưu trữ message_id
  }

  const messageContent = document.createElement("div");
  messageContent.classList.add("message-content");
  messageContent.textContent = message;

  messageElement.appendChild(messageContent);

  if (sender === "bot") {
    const feedbackButtons = document.createElement("div");
    feedbackButtons.classList.add("feedback-buttons");

    const likeButton = document.createElement("button");
    likeButton.classList.add("like-button");
    likeButton.innerHTML = '<i class="fas fa-thumbs-up"></i>'; // Add FontAwesome icon
    likeButton.onclick = () => sendFeedback("like", messageId, messageElement);

    const dislikeButton = document.createElement("button");
    dislikeButton.classList.add("dislike-button");
    dislikeButton.innerHTML = '<i class="fas fa-thumbs-down"></i>'; // Add FontAwesome icon
    dislikeButton.onclick = () =>
      sendFeedback("dislike", messageId, messageElement);

    feedbackButtons.appendChild(likeButton);
    feedbackButtons.appendChild(dislikeButton);

    messageElement.appendChild(feedbackButtons);
  }

  chatMessages.appendChild(messageElement);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addWaitingBubble() {
  removeWaitingBubble(); // Remove any existing waiting bubble before adding a new one
  const chatMessages = document.getElementById("chatMessages");

  const waitingBubble = document.createElement("div");
  waitingBubble.classList.add("message", "bot", "waiting-bubble");

  const messageContent = document.createElement("div");
  messageContent.classList.add("message-content");

  // Thêm các dấu chấm với hiệu ứng nhấp nháy
  const dot1 = document.createElement("span");
  dot1.classList.add("dot");
  const dot2 = document.createElement("span");
  dot2.classList.add("dot");
  const dot3 = document.createElement("span");
  dot3.classList.add("dot");

  messageContent.appendChild(dot1);
  messageContent.appendChild(dot2);
  messageContent.appendChild(dot3);

  waitingBubble.appendChild(messageContent);
  chatMessages.appendChild(waitingBubble);

  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeWaitingBubble() {
  const chatMessages = document.getElementById("chatMessages");
  const waitingBubble = chatMessages.querySelector(".waiting-bubble");
  if (waitingBubble) {
    chatMessages.removeChild(waitingBubble);
  }
}

function showWaitingBubble() {
  removeWaitingBubble(); // Ensure any existing waiting bubble is removed before showing a new one
  const chatMessages = document.getElementById("chatMessages");
  const waitingBubble = document.createElement("div");
  waitingBubble.classList.add("message", "bot", "waiting-bubble");

  const messageContent = document.createElement("div");
  messageContent.classList.add("message-content");

  const dot1 = document.createElement("span");
  dot1.classList.add("dot");
  const dot2 = document.createElement("span");
  dot2.classList.add("dot");
  const dot3 = document.createElement("span");
  dot3.classList.add("dot");
  messageContent.appendChild(dot1);
  messageContent.appendChild(dot2);
  messageContent.appendChild(dot3);

  waitingBubble.appendChild(messageContent);
  chatMessages.appendChild(waitingBubble);

  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideWaitingBubble() {
  removeWaitingBubble(); // Ensure the waiting bubble is removed when hiding
}

function submitFeedback(feedbackType, messageId, feedbackText, messageElement) {
  const urlParams = new URLSearchParams(window.location.search);
  const user_id = urlParams.get("user_id");
  const session_id = urlParams.get("session_id");

  fetch("/api/feedback", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      user_id,
      session_id,
      messageId,
      feedbackType,
      feedbackText,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Feedback sent:", data);
      if (feedbackType === "dislike") {
        messageElement
          .querySelector(".dislike-button")
          .classList.add("selected");
      } else {
        messageElement.querySelector(".like-button").classList.add("selected");
      }
    })
    .catch((error) => {
      console.error("Error sending feedback:", error);
    });
}

function sendFeedback(feedbackType, messageId, messageElement) {
  const feedbackButtons = messageElement.querySelector(".feedback-buttons");
  const likeButton = feedbackButtons.querySelector(".like-button");
  const dislikeButton = feedbackButtons.querySelector(".dislike-button");

  // Disable buttons after feedback
  likeButton.disabled = true;
  dislikeButton.disabled = true;

  if (feedbackType === "dislike") {
    feedbackMessageId = messageId;
    showModal();
  } else {
    submitFeedback(feedbackType, messageId, "", messageElement);
  }
}

function showModal() {
  document.getElementById("feedbackModal").style.display = "block";
}

function closeModal() {
  document.getElementById("feedbackModal").style.display = "none";
  feedbackMessageId = null;
}

function submitDislikeFeedback() {
  const feedbackText = document.getElementById("feedbackText").value;
  const messageElement = document.querySelector(
    `.message[data-message-id="${feedbackMessageId}"]`
  );
  submitFeedback("dislike", feedbackMessageId, feedbackText, messageElement);
  closeModal();
}
